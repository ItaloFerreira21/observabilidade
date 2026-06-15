from typing import cast

from fastapi import APIRouter, Request

from app.core.config import Settings

router = APIRouter(tags=["system"])


def public_service_info(settings: Settings) -> dict[str, str]:
    return {
        "service": settings.service_name,
        "environment": settings.environment,
        "version": settings.app_version,
    }


@router.get("/", include_in_schema=False)
async def root(request: Request) -> dict[str, str]:
    settings = cast(Settings, request.app.state.settings)
    return {"status": "ok", **public_service_info(settings)}


@router.get("/v1/info")
async def info(request: Request) -> dict[str, str]:
    settings = cast(Settings, request.app.state.settings)
    return public_service_info(settings)
