from collections.abc import Awaitable, Callable
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger
from app.core.metrics import route_template

logger = get_logger("app.access")
CallNext = Callable[[Request], Awaitable[Response]]


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        if request.url.path == "/metrics":
            return await call_next(request)

        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            logger.exception(
                "http_request_failed",
                method=request.method,
                path=route_template(request),
                duration_ms=duration_ms,
            )
            raise

        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        logger.info(
            "http_request_completed",
            method=request.method,
            path=route_template(request),
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response
