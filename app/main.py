from collections.abc import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from app.core.config import Settings, get_settings
from app.core.errors import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.logging import configure_logging
from app.core.metrics import metrics_response, set_service_info
from app.core.telemetry import setup_telemetry
from app.middlewares.logging import AccessLogMiddleware
from app.middlewares.metrics import MetricsMiddleware
from app.middlewares.request_context import (
    CORRELATION_ID_HEADER,
    REQUEST_ID_HEADER,
    RequestContextMiddleware,
)
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.routers import health, system

ExceptionHandler = Callable[[Request, Exception], StarletteResponse | Awaitable[StarletteResponse]]


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    set_service_info(settings)

    docs_url = "/docs" if settings.should_enable_docs else None
    openapi_url = "/openapi.json" if settings.should_enable_docs else None

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url=docs_url,
        redoc_url=None,
        openapi_url=openapi_url,
    )
    app.state.settings = settings

    configure_middlewares(app, settings)
    register_exception_handlers(app)
    register_routes(app, settings)
    setup_telemetry(app, settings)
    return app


def configure_middlewares(app: FastAPI, settings: Settings) -> None:
    if settings.trusted_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=False,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=[
            "Authorization",
            "Content-Type",
            REQUEST_ID_HEADER,
            CORRELATION_ID_HEADER,
        ],
        expose_headers=[REQUEST_ID_HEADER, CORRELATION_ID_HEADER],
        max_age=600,
    )
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(MetricsMiddleware, enabled=settings.metrics_enabled)
    app.add_middleware(
        SecurityHeadersMiddleware,
        hsts_enabled=settings.hsts_enabled or settings.is_production,
    )
    app.add_middleware(RequestContextMiddleware)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        StarletteHTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(Exception, unhandled_exception_handler)


def register_routes(app: FastAPI, settings: Settings) -> None:
    app.include_router(system.router)
    app.include_router(health.router)

    if settings.metrics_enabled:
        app.add_api_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)


async def metrics_endpoint() -> Response:
    return metrics_response()


app = create_app()
