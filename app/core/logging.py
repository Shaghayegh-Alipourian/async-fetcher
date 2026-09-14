from typing import cast
import structlog
from structlog.stdlib import BoundLogger

import logging
import sys
from typing import Any

import structlog


def configure_logging() -> None:
    """Configure application-wide structured logging."""

    timestamper = structlog.processors.TimeStamper(
        fmt="iso",
        utc=True,
    )

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def get_logger(name: str) -> BoundLogger:
    """Return a structured logger for the given module name."""

    return cast(BoundLogger, structlog.get_logger(name))