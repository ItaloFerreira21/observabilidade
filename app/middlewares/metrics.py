from collections.abc import Awaitable, Callable
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
    route_template,
)

CallNext = Callable[[Request], Awaitable[Response]]


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, enabled: bool = True) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        if not self.enabled or request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        status_code = 500
        started_at = perf_counter()

        HTTP_REQUESTS_IN_PROGRESS.labels(method=method).inc()
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = perf_counter() - started_at
            path = route_template(request)
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method).dec()
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status_code=str(status_code),
            ).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration)
