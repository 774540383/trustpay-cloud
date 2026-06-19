"""Structured logging configuration."""
import logging
import sys
import structlog
from app.core.config import settings


def setup_logging():
    log_level = logging.DEBUG if settings.APP_DEBUG else logging.INFO
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.is_development
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    logging.basicConfig(stream=sys.stdout, level=log_level)


logger = structlog.get_logger("trustpay")
