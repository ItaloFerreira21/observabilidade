from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger
from app.middlewares.request_context import get_request_id

logger = get_logger("app.errors")


def error_payload(
    *,
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "status_code": status_code,
            "request_id": get_request_id(),
        }
    }
    if details:
        payload["error"]["details"] = details
    return payload


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    logger.warning(
        "http_exception",
        method=request.method,
        path=request.url.path,
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(
            status_code=exc.status_code,
            code="HTTP_ERROR",
            message=message,
        ),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = [
        {
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg", "Invalid value."),
            "type": error.get("type", "value_error"),
        }
        for error in exc.errors()
    ]
    logger.warning(
        "request_validation_failed",
        method=request.method,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=422,
        content=error_payload(
            status_code=422,
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=details,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content=error_payload(
            status_code=500,
            code="INTERNAL_SERVER_ERROR",
            message="Internal server error.",
        ),
    )

