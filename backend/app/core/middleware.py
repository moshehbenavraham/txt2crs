"""
Request middleware for logging and trace ID correlation.

This module provides middleware for:
- Generating and propagating trace IDs across requests
- Structured request/response logging
- Request timing metrics
- Integration with OpenTelemetry distributed tracing

When OpenTelemetry is enabled, uses OTEL trace IDs for consistency.
Otherwise, generates UUIDs for standalone trace correlation.

Usage:
    In main.py:
        from app.core.middleware import RequestLoggingMiddleware
        app.add_middleware(RequestLoggingMiddleware)
"""

import re
import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import generate_trace_id, get_logger, trace_id_var
from app.core.telemetry import get_current_trace_id, is_telemetry_enabled

logger = get_logger(__name__)
_TRACE_ID_PATTERN = re.compile(r"[A-Za-z0-9-]{16,64}")

# Type alias for the call_next function
RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging with trace ID correlation.

    Features:
    - Generates unique trace ID for each request (or uses X-Trace-ID header)
    - Logs request received and completed events
    - Tracks request duration
    - Adds X-Trace-ID to response headers for correlation

    Log Events:
    - request.http_received: When request is received
    - request.http_completed: When response is sent

    Raw paths, query strings, client addresses, headers, and bodies are never
    logged. A completed request may include only its reviewed route name.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request with logging and trace ID.

        Trace ID priority:
        1. A bounded safe X-Trace-ID header from an incoming request
        2. OpenTelemetry trace ID (if OTEL is enabled)
        3. Newly generated UUID (fallback)
        """
        # Determine trace ID from various sources
        incoming_trace_id = request.headers.get("X-Trace-ID")

        if incoming_trace_id and _TRACE_ID_PATTERN.fullmatch(incoming_trace_id):
            # Use propagated trace ID from upstream service
            trace_id = incoming_trace_id
        elif is_telemetry_enabled():
            # Use OpenTelemetry trace ID if available
            otel_trace_id = get_current_trace_id()
            trace_id = otel_trace_id if otel_trace_id else generate_trace_id()
        else:
            # Generate our own trace ID
            trace_id = generate_trace_id()

        trace_id_var.set(trace_id)

        start_time = time.perf_counter()

        # Log request received
        logger.info(
            "request.http_received",
            extra={"method": request.method},
        )

        try:
            response: Response = await call_next(request)
        except BaseException:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request.http_failed",
                extra={
                    "method": request.method,
                    "route_name": get_safe_route_name(request),
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log request completed
        log_level = "warning" if response.status_code >= 400 else "info"
        getattr(logger, log_level)(
            "request.http_completed",
            extra={
                "method": request.method,
                "route_name": get_safe_route_name(request),
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id

        return response


def get_safe_route_name(request: Request) -> str | None:
    """Return only the static reviewed route name assigned by FastAPI."""

    route = request.scope.get("route")
    route_name = getattr(route, "name", None)
    if not isinstance(route_name, str):
        return None
    # Route names are developer-authored, but clamping and a conservative
    # alphabet prevent a custom route from turning logs into arbitrary text.
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", route_name):
        return None
    return route_name
