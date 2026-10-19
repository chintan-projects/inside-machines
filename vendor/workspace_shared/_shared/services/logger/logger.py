"""Structured JSON logger that wraps the standard library ``logging`` module.

Every record is one JSON object per line with ``timestamp``, ``level``, ``logger`` and
``message``, plus any context fields set on the logger and any keyword fields passed to the
call. Output goes to stderr unless a stream is given: a process that speaks a protocol on
stdout (an MCP server, for one) must never have log lines mixed into it.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any, TextIO

# Field values are whatever the caller passes; json.dumps stringifies the rest.
Fields = dict[str, Any]


class StructuredLogger:
    """JSON logger with context fields that persist across calls."""

    def __init__(self, name: str, level: str = "INFO", stream: TextIO | None = None) -> None:
        """Create a logger.

        Args:
            name: Logger name, usually ``__name__``.
            level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL (case-insensitive).
            stream: Where records are written. ``None`` means stderr.
        """
        self.name = name
        self.level = level.upper()
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self.level)
        self._logger.propagate = False
        self._context_fields: Fields = {}

        if not self._logger.handlers:
            handler = logging.StreamHandler(stream)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)

    def set_context(self, **fields: Any) -> None:
        """Set fields that are included in every subsequent record."""
        self._context_fields.update(fields)

    def clear_context(self) -> None:
        """Drop all context fields."""
        self._context_fields.clear()

    def _build_log_entry(self, level: str, message: str, fields: Fields) -> str:
        entry: Fields = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
        }
        entry.update(self._context_fields)
        entry.update(fields)
        return json.dumps(entry, default=str)

    def debug(self, message: str, **fields: Any) -> None:
        """Log at DEBUG."""
        self._logger.debug(self._build_log_entry("DEBUG", message, fields))

    def info(self, message: str, **fields: Any) -> None:
        """Log at INFO."""
        self._logger.info(self._build_log_entry("INFO", message, fields))

    def warning(self, message: str, **fields: Any) -> None:
        """Log at WARNING."""
        self._logger.warning(self._build_log_entry("WARNING", message, fields))

    warn = warning

    def error(self, message: str, **fields: Any) -> None:
        """Log at ERROR."""
        self._logger.error(self._build_log_entry("ERROR", message, fields))

    def critical(self, message: str, **fields: Any) -> None:
        """Log at CRITICAL."""
        self._logger.critical(self._build_log_entry("CRITICAL", message, fields))

    def log_latency(self, operation: str, duration_ms: float) -> None:
        """Log a latency measurement at INFO."""
        self.info("Operation completed", operation=operation, duration_ms=duration_ms)


Logger = StructuredLogger

_loggers: dict[str, StructuredLogger] = {}


def get_logger(name: str, level: str = "INFO", stream: TextIO | None = None) -> StructuredLogger:
    """Return the logger registered under ``name``, creating it on first use.

    ``level`` and ``stream`` only apply when the logger is created; later calls with the same
    name return the existing instance unchanged.
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name, level, stream)
    return _loggers[name]
