"""
Structured JSON logging for AI agent-optimized log parsing.

This module provides JSON-formatted logs with trace ID correlation,
enabling AI agents and monitoring tools to parse logs programmatically.

Usage:
    from app.core.logging import get_logger, setup_logging, trace_id_var

    logger = get_logger(__name__)
    logger.info("user.registration_completed", extra={"user_id": str(user.id)})

Log Event Naming Convention:
    Pattern: {domain}.{action}_{state}

    Domains: user, item, auth, database, request, health, external, agent
    Actions: create, update, delete, get, list, validate, login, etc.
    States: _started, _completed, _failed, _validated, _rejected, _retrying

    Examples:
        - user.registration_started
        - item.create_completed
        - auth.login_failed
        - database.query_executed
        - request.http_received
"""

import contextvars
import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

# Context variable for request-scoped trace ID
trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "trace_id", default=""
)


def generate_trace_id() -> str:
    """Generate a new trace ID for request correlation."""
    return str(uuid4())


class StructuredLogFormatter(logging.Formatter):
    """JSON formatter for structured, machine-parseable logs.

    Outputs single-line JSON objects with standardized fields:
    - timestamp: ISO 8601 format with UTC timezone
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - logger: Logger name
    - message: Human-readable message (event name)
    - trace_id: Request correlation ID
    - location: File, line, function
    - extra: Additional context fields

    Example output:
        {"timestamp": "2024-01-15T10:30:00Z", "level": "INFO",
         "logger": "app.api.routes.users", "message": "user.create_completed",
         "trace_id": "abc-123", "extra": {"user_id": "uuid-here"}}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": trace_id_var.get() or None,
        }

        # Add location info for debugging
        log_data["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add exception info if present
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
            }

        # Add extra fields from record
        # Filter out standard LogRecord attributes
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "exc_info",
            "exc_text",
            "thread",
            "threadName",
            "taskName",
            "message",
        }

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_attrs
        }

        if extra_fields:
            log_data["extra"] = extra_fields

        return json.dumps(log_data, default=str)


class HumanReadableFormatter(logging.Formatter):
    """Human-readable formatter for local development.

    Format: TIMESTAMP | LEVEL | LOGGER | MESSAGE | EXTRA
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record for human readability."""
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        trace_id = trace_id_var.get()
        trace_part = f" [{trace_id[:8]}]" if trace_id else ""

        # Get extra fields
        standard_attrs = {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "exc_info",
            "exc_text",
            "thread",
            "threadName",
            "taskName",
            "message",
        }

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_attrs
        }

        extra_str = ""
        if extra_fields:
            extra_str = " | " + " ".join(f"{k}={v}" for k, v in extra_fields.items())

        base_msg = (
            f"{timestamp} | {record.levelname:8}{trace_part} | "
            f"{record.name} | {record.getMessage()}{extra_str}"
        )

        if record.exc_info:
            base_msg += "\n" + self.formatException(record.exc_info)

        return base_msg


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
) -> None:
    """Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ("json" for production, "text" for development)

    Example:
        >>> from app.core.logging import setup_logging
        >>> setup_logging(level="DEBUG", format_type="text")  # Development
        >>> setup_logging(level="INFO", format_type="json")   # Production
    """
    handler = logging.StreamHandler(sys.stdout)

    if format_type == "json":
        handler.setFormatter(StructuredLogFormatter())
    else:
        handler.setFormatter(HumanReadableFormatter())

    # Clear existing handlers and set new one
    logging.root.handlers = []
    logging.root.addHandler(handler)
    logging.root.setLevel(getattr(logging, level.upper()))

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with structured output.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Configured logger instance

    Example:
        >>> from app.core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("user.create_completed", extra={"user_id": "123"})
    """
    return logging.getLogger(name)


# Initialize logging on module import
# Can be reconfigured by calling setup_logging() explicitly
setup_logging(level="INFO", format_type="json")
