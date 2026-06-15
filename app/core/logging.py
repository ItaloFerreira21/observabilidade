import logging
import sys
from collections.abc import Callable, MutableMapping
from typing import Any, cast

import structlog

from app.core.config import Settings
from app.core.security import sanitize_mapping

Processor = Callable[[Any, str, MutableMapping[str, Any]], MutableMapping[str, Any]]


def add_service_context(settings: Settings) -> Processor:
    def processor(
        _: Any,
        __: str,
        event_dict: MutableMapping[str, Any],
    ) -> MutableMapping[str, Any]:
        event_dict.setdefault("service", settings.service_name)
        event_dict.setdefault("environment", settings.environment)
        event_dict.setdefault("version", settings.app_version)
        return event_dict

    return processor


def redact_sensitive_data(
    _: Any,
    __: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    return sanitize_mapping(event_dict)


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level,
        force=True,
    )

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        add_service_context(settings),
        redact_sensitive_data,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[*shared_processors, structlog.processors.JSONRenderer()],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.getLogger("uvicorn.access").disabled = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
