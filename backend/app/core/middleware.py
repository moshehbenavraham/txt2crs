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
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.constants import ContentTypes, ErrorCode
from app.core.exceptions import AppException
from app.core.logging import generate_trace_id, get_logger, trace_id_var
from app.core.telemetry import get_current_trace_id, is_telemetry_enabled

logger = get_logger(__name__)
_TRACE_ID_PATTERN = re.compile(r"[A-Za-z0-9-]{16,64}")

# Type alias for the call_next function
RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


class _UploadBodyTooLarge(Exception):
    """Private control flow raised while the downstream parser reads chunks."""


class UploadBodyLimitMiddleware:
    """Enforce one finite multipart route body before framework spooling.

    This is pure ASGI middleware because ``BaseHTTPMiddleware`` may buffer or
    transform request streams. The wrapper counts the exact bytes delivered to
    FastAPI's multipart parser and therefore still protects requests with a
    missing or dishonest ``Content-Length`` header.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        maximum_body_bytes: int,
        upload_path: str,
    ) -> None:
        if maximum_body_bytes <= 0:
            raise ValueError("Upload body limit must be positive.")
        if not upload_path.startswith("/"):
            raise ValueError("Upload path must be absolute.")
        self._app = app
        self._maximum_body_bytes = maximum_body_bytes
        self._upload_path = upload_path

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Reject malformed/oversize framing and count every request chunk."""

        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") != self._upload_path
        ):
            await self._app(scope, receive, send)
            return

        content_lengths = [
            header_value
            for header_name, header_value in scope.get("headers", [])
            if header_name.lower() == b"content-length"
        ]
        if len(content_lengths) > 1:
            await self._send_invalid_framing(scope, receive, send)
            return
        if content_lengths:
            raw_content_length = content_lengths[0]
            # HTTP Content-Length uses only ASCII decimal digits. Python's
            # ``int`` also accepts signs, whitespace, and underscores, which
            # would make our framing decision disagree with stricter proxies.
            if not raw_content_length or not raw_content_length.isdigit():
                await self._send_invalid_framing(scope, receive, send)
                return
            declared_length = int(raw_content_length)
            if declared_length > self._maximum_body_bytes:
                await self._send_too_large(scope, receive, send)
                return

        received_body_bytes = 0

        async def bounded_receive() -> Message:
            """Forward one ASGI frame after applying the cumulative byte cap."""

            nonlocal received_body_bytes
            message = await receive()
            if message["type"] == "http.request":
                received_body_bytes += len(message.get("body", b""))
                if received_body_bytes > self._maximum_body_bytes:
                    raise _UploadBodyTooLarge
            return message

        try:
            await self._app(scope, bounded_receive, send)
        except _UploadBodyTooLarge:
            # FastAPI consumes multipart input before a route can start a
            # response, so it is safe to replace this framing failure with one
            # complete Problem Details response.
            await self._send_too_large(scope, receive, send)

    @staticmethod
    async def _send_problem(
        *,
        scope: Scope,
        receive: Receive,
        send: Send,
        error: AppException,
    ) -> None:
        """Write one bounded RFC 9457 response without invoking route code."""

        problem = error.to_problem_detail()
        response = JSONResponse(
            status_code=error.status,
            content=problem.model_dump(exclude_none=True),
            media_type=ContentTypes.PROBLEM_JSON,
        )
        await response(scope, receive, send)

    async def _send_invalid_framing(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Reject ambiguous content lengths with a content-free 400."""

        await self._send_problem(
            scope=scope,
            receive=receive,
            send=send,
            error=AppException(
                code=ErrorCode.INVALID_FORMAT,
                detail="Upload request framing is invalid.",
            ),
        )

    async def _send_too_large(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Reject declared or observed overflow with the same stable 413."""

        await self._send_problem(
            scope=scope,
            receive=receive,
            send=send,
            error=AppException(
                code=ErrorCode.JOB_PAYLOAD_TOO_LARGE,
                detail="Upload request body exceeds the configured limit.",
            ),
        )


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
