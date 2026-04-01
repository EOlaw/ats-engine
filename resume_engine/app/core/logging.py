"""Structured logging configuration using structlog.

Provides a LoggerFactory that configures structlog with environment-appropriate
renderers: JSON in production for log aggregation, colorized console in development.
"""

import logging
import sys
from typing import Any

import structlog
from structlog.types import FilteringBoundLogger

from app.core.config import get_settings


class LoggerFactory:
    """Factory for creating configured structlog loggers.

    Configures structlog once on first access and provides a static method
    to retrieve named loggers throughout the application. Renders as JSON
    in production environments and as colorized console output in development.
    """

    _configured: bool = False

    @classmethod
    def _configure(cls) -> None:
        """Configure structlog processors and renderer based on environment."""
        if cls._configured:
            return

        settings = get_settings()

        # Configure standard library logging
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=log_level,
        )

        shared_processors: list[Any] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]

        if settings.is_production:
            # Production: JSON output suitable for log aggregation systems
            processors: list[Any] = shared_processors + [
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer(),
            ]
        else:
            # Development: human-readable colorized console output
            processors = shared_processors + [
                structlog.dev.ConsoleRenderer(colors=True),
            ]

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(log_level),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        cls._configured = True

    @staticmethod
    def get_logger(name: str) -> FilteringBoundLogger:
        """Return a named structlog bound logger.

        Ensures structlog is configured before returning a logger.
        The returned logger supports all standard log levels as methods.

        Args:
            name: Logical name for the logger, typically the module or class name.

        Returns:
            A structlog BoundLogger pre-bound with the given name.
        """
        LoggerFactory._configure()
        return structlog.get_logger(name)
