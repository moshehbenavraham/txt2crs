"""
OpenTelemetry distributed tracing configuration.

This module provides distributed tracing via OpenTelemetry with:
- Automatic instrumentation of FastAPI, SQLAlchemy, and HTTPX
- OTLP exporter for sending traces to collectors (Jaeger, Tempo, etc.)
- Integration with existing trace ID correlation system
- Configurable sampling rate for high-traffic environments

Usage:
    In main.py (before creating FastAPI app):
        from app.core.telemetry import setup_telemetry, instrument_app
        setup_telemetry()  # Initialize tracer provider
        app = FastAPI(...)
        instrument_app(app)  # Instrument the app

Configuration:
    Set these environment variables to enable tracing:
    - OTEL_ENABLED=true
    - OTLP_ENDPOINT=http://localhost:4317  (gRPC) or http://localhost:4318/v1/traces (HTTP)
    - OTEL_SERVICE_NAME=my-service  (optional, defaults to PROJECT_NAME)
    - OTEL_TRACES_SAMPLER_ARG=1.0  (optional, 1.0 = sample all, 0.1 = sample 10%)

Example Docker Compose with Jaeger:
    services:
      jaeger:
        image: jaegertracing/jaeger:2.19.0
        ports:
          - "16686:16686"  # Jaeger UI
          - "4317:4317"    # OTLP gRPC
          - "4318:4318"    # OTLP HTTP
        environment:
          - COLLECTOR_OTLP_GRPC_HOST_PORT=0.0.0.0:4317
          - COLLECTOR_OTLP_HTTP_HOST_PORT=0.0.0.0:4318

Note:
    OpenTelemetry instrumentation must be set up BEFORE the FastAPI app
    is created to properly instrument the underlying ASGI framework.
"""

from functools import lru_cache
from importlib import metadata as importlib_metadata
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = get_logger(__name__)

# Module-level flag to track initialization state
_telemetry_initialized: bool = False


@lru_cache(maxsize=1)
def get_service_version() -> str:
    """
    Resolve application version for telemetry `service.version`.

    Prefers installed package metadata to keep telemetry versioning aligned
    with the backend project version automatically. The resolved value is
    cached to avoid repeated metadata lookups on hot paths (for example,
    readiness probes that include service version metadata).
    """
    package_name = "app"
    fallback_version = "unknown"

    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        logger.warning(
            "telemetry.service_version_resolution_failed",
            extra={
                "package_name": package_name,
                "reason": "package_not_found",
                "fallback_version": fallback_version,
            },
        )
        return fallback_version
    except Exception:
        logger.warning(
            "telemetry.service_version_resolution_failed",
            extra={
                "package_name": package_name,
                "reason": "unexpected_error",
                "fallback_version": fallback_version,
            },
        )
        return fallback_version


def is_telemetry_enabled() -> bool:
    """
    Check if OpenTelemetry is configured and enabled.

    Returns:
        True if OTEL_ENABLED is True AND OTLP_ENDPOINT is set, False otherwise.

    Example:
        >>> if is_telemetry_enabled():
        ...     # Add custom spans
        ...     pass
    """
    return bool(settings.OTEL_ENABLED and settings.OTLP_ENDPOINT)


def setup_telemetry() -> bool:
    """
    Initialize OpenTelemetry tracer provider and exporter.

    Sets up:
    - Resource attributes (service name, version, environment)
    - OTLP exporter (gRPC or HTTP based on endpoint)
    - Trace sampling based on OTEL_TRACES_SAMPLER_ARG
    - SQLAlchemy and HTTPX auto-instrumentation

    Must be called BEFORE creating the FastAPI application.

    Returns:
        True if telemetry was successfully initialized, False if disabled/failed.

    Raises:
        No exceptions raised; failures are logged and function returns False.

    Example:
        >>> from app.core.telemetry import setup_telemetry
        >>> if setup_telemetry():
        ...     print("Tracing enabled")
        ... else:
        ...     print("Tracing disabled")
    """
    global _telemetry_initialized

    if _telemetry_initialized:
        logger.debug("telemetry.setup_skipped", extra={"reason": "already_initialized"})
        return True

    if not is_telemetry_enabled():
        logger.info(
            "telemetry.setup_skipped",
            extra={
                "reason": "disabled",
                "otel_enabled": settings.OTEL_ENABLED,
                "otlp_endpoint_set": settings.OTLP_ENDPOINT is not None,
            },
        )
        return False

    try:
        # Import OpenTelemetry packages (optional dependencies)
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

        # Determine service metadata
        service_name = settings.OTEL_SERVICE_NAME or settings.PROJECT_NAME
        service_version = get_service_version()

        # Create resource with service metadata
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": service_version,
                "deployment.environment": settings.ENVIRONMENT,
            }
        )

        # Configure sampler
        sampler = TraceIdRatioBased(settings.OTEL_TRACES_SAMPLER_ARG)

        # Create tracer provider
        provider = TracerProvider(resource=resource, sampler=sampler)

        # Configure OTLP exporter
        # The endpoint format determines protocol:
        # - Ends with port (e.g., :4317) = gRPC
        # - Ends with path (e.g., /v1/traces) = HTTP
        exporter = OTLPSpanExporter(
            endpoint=settings.OTLP_ENDPOINT,
            insecure=True,  # Use True for local development
        )

        # Add batch processor for efficient export
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Instrument SQLAlchemy (database queries)
        SQLAlchemyInstrumentor().instrument()

        # Instrument HTTPX (outbound HTTP calls)
        HTTPXClientInstrumentor().instrument()

        _telemetry_initialized = True

        logger.info(
            "telemetry.setup_completed",
            extra={
                "service_name": service_name,
                "service_version": service_version,
                "exporter_configured": True,
                "sampling_rate": settings.OTEL_TRACES_SAMPLER_ARG,
                "environment": settings.ENVIRONMENT,
            },
        )

        return True

    except ImportError:
        logger.warning(
            "telemetry.setup_failed",
            extra={
                "reason": "missing_dependencies",
                "hint": "Install opentelemetry packages: pip install opentelemetry-sdk opentelemetry-exporter-otlp",
            },
        )
        return False
    except Exception:
        logger.error(
            "telemetry.setup_failed",
            extra={"reason": "unexpected_error"},
        )
        return False


def instrument_app(app: FastAPI) -> None:
    """
    Instrument a FastAPI application with OpenTelemetry.

    Must be called AFTER setup_telemetry() and AFTER creating the FastAPI app.
    If telemetry is not enabled, this function does nothing.

    Args:
        app: The FastAPI application instance to instrument.

    Example:
        >>> from fastapi import FastAPI
        >>> from app.core.telemetry import setup_telemetry, instrument_app
        >>> setup_telemetry()
        >>> app = FastAPI()
        >>> instrument_app(app)
    """
    if not _telemetry_initialized:
        return

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)

        logger.info(
            "telemetry.fastapi_instrumented",
            extra={"app_title": app.title},
        )

    except ImportError:
        logger.warning(
            "telemetry.fastapi_instrumentation_failed",
            extra={"reason": "missing_fastapi_instrumentation"},
        )
    except Exception:
        logger.error(
            "telemetry.fastapi_instrumentation_failed",
            extra={"reason": "unexpected_error"},
        )


def get_current_trace_id() -> str | None:
    """
    Get the current OpenTelemetry trace ID if tracing is active.

    Returns:
        Trace ID as hex string, or None if no active span.

    Example:
        >>> trace_id = get_current_trace_id()
        >>> if trace_id:
        ...     print(f"Current trace: {trace_id}")
    """
    if not _telemetry_initialized:
        return None

    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span and span.is_recording():
            ctx = span.get_span_context()
            if ctx.is_valid:
                return format(ctx.trace_id, "032x")
        return None
    except Exception:
        return None


def get_tracer(name: str) -> object | None:
    """
    Get an OpenTelemetry tracer for creating custom spans.

    Args:
        name: Tracer name (typically module __name__).

    Returns:
        Tracer instance if telemetry is enabled, None otherwise.
        The return type is 'object' to avoid import dependency; cast to
        opentelemetry.trace.Tracer when using.

    Example:
        >>> tracer = get_tracer(__name__)
        >>> if tracer:
        ...     with tracer.start_as_current_span("my-operation") as span:
        ...         span.set_attribute("key", "value")
        ...         # do work
    """
    if not _telemetry_initialized:
        return None

    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except Exception:
        return None
