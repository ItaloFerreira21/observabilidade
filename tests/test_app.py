from collections.abc import AsyncIterator

import httpx2
import pytest
from fastapi import FastAPI
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.core.security import sanitize_mapping
from app.main import create_app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("TRUSTED_HOSTS", "testserver,localhost,127.0.0.1")
    monkeypatch.setenv("METRICS_AUTH_TOKEN", "")
    get_settings.cache_clear()
    return create_app()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[httpx2.AsyncClient]:
    transport = httpx2.ASGITransport(app=app)
    async with httpx2.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
    get_settings.cache_clear()


@pytest.mark.anyio
async def test_liveness_returns_service_status(client: httpx2.AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-request-id"]
    assert response.headers["x-correlation-id"]


@pytest.mark.anyio
async def test_security_headers_are_applied(client: httpx2.AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "geolocation=()" in response.headers["permissions-policy"]


@pytest.mark.anyio
async def test_metrics_endpoint_exposes_request_metrics(client: httpx2.AsyncClient) -> None:
    await client.get("/health/live")
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert 'path="/health/live"' in response.text


@pytest.mark.anyio
async def test_metrics_endpoint_requires_bearer_token_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("TRUSTED_HOSTS", "testserver,localhost,127.0.0.1")
    monkeypatch.setenv("METRICS_AUTH_TOKEN", "test-metrics-token")
    get_settings.cache_clear()
    protected_app = create_app()
    transport = httpx2.ASGITransport(protected_app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://testserver") as protected_client:
        denied_response = await protected_client.get("/metrics")
        allowed_response = await protected_client.get(
            "/metrics", headers={"Authorization": "Bearer test-metrics-token"}
        )

    assert denied_response.status_code == 403
    assert allowed_response.status_code == 200
    get_settings.cache_clear()


def test_production_requires_metrics_token() -> None:
    with pytest.raises(ValidationError, match="METRICS_AUTH_TOKEN"):
        Settings(environment="production", metrics_enabled=True, metrics_auth_token=None)


def test_production_rejects_insecure_otlp() -> None:
    with pytest.raises(ValidationError, match="Insecure OTLP"):
        Settings(
            environment="production",
            metrics_enabled=False,
            otel_enabled=True,
            otel_exporter_otlp_endpoint="collector.example.internal:4317",
            otel_exporter_otlp_insecure=True,
        )


def test_production_allows_secure_otlp() -> None:
    settings = Settings(
        environment="production",
        metrics_enabled=False,
        otel_enabled=True,
        otel_exporter_otlp_endpoint="collector.example.internal:4317",
        otel_exporter_otlp_insecure=False,
    )

    assert settings.otel_exporter_otlp_insecure is False


@pytest.mark.anyio
async def test_not_found_uses_structured_error_payload(client: httpx2.AsyncClient) -> None:
    response = await client.get("/missing")
    body = response.json()

    assert response.status_code == 404
    assert body["error"]["code"] == "HTTP_ERROR"
    assert body["error"]["request_id"]


def test_sensitive_data_is_redacted() -> None:
    sanitized = sanitize_mapping(
        {
            "Authorization": "Bearer secret",
            "email": "person@example.com",
            "nested": {"token": "abc123"},
            "cpf_text": "CPF 123.456.789-09",
        }
    )

    assert sanitized["Authorization"] == "[REDACTED]"
    assert sanitized["email"] == "p***@e***"
    assert sanitized["nested"]["token"] == "[REDACTED]"  # noqa: S105
    assert sanitized["cpf_text"] == "[REDACTED]"
