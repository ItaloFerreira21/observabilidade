from typing import cast

from fastapi import APIRouter, Request

from app.core.config import Settings
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=HealthResponse)
async def liveness(request: Request) -> HealthResponse:
    settings = cast(Settings, request.app.state.settings)
    return HealthResponse(
        status="ok",
        service=settings.service_name,
        environment=settings.environment,
        version=settings.app_version,
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness(request: Request) -> ReadinessResponse:
    settings = cast(Settings, request.app.state.settings)
    return ReadinessResponse(
        status="ready",
        service=settings.service_name,
        environment=settings.environment,
        version=settings.app_version,
        checks={"api": "ok"},
    )
