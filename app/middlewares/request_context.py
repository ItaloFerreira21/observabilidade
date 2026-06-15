import re
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from structlog.contextvars import bind_contextvars, clear_contextvars

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
HEADER_VALUE_RE = re.compile(r"^[A-Za-z0-9._\-:/]{1,128}$")

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
CallNext = Callable[[Request], Awaitable[Response]]


def valid_context_header(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip()
    if HEADER_VALUE_RE.fullmatch(normalized):
        return normalized
    return None


def get_request_id() -> str | None:
    return request_id_ctx.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        request_id = valid_context_header(request.headers.get(REQUEST_ID_HEADER))
        if request_id is None:
            request_id = str(uuid.uuid4())
        correlation_id = (
            valid_context_header(request.headers.get(CORRELATION_ID_HEADER)) or request_id
        )

        clear_contextvars()
        bind_contextvars(request_id=request_id, correlation_id=correlation_id)
        request_id_token = request_id_ctx.set(request_id)
        correlation_id_token = correlation_id_ctx.set(correlation_id)

        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(request_id_token)
            correlation_id_ctx.reset(correlation_id_token)
            clear_contextvars()

        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response
