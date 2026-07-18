import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.rate_limit import limiter
from app.core.telemetry import instrument_app, setup_telemetry

# Configure structured logging based on environment
log_format = "text" if settings.ENVIRONMENT == "local" else "json"
setup_logging(level="INFO", format_type=log_format)

# Initialize OpenTelemetry tracing (must be before creating FastAPI app)
# This enables distributed tracing when OTEL_ENABLED=true and OTLP_ENDPOINT is set
setup_telemetry()


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Instrument FastAPI with OpenTelemetry (must be after app creation)
instrument_app(app)

# Register exception handlers for RFC 9457 Problem Details format
register_exception_handlers(app)

# Add rate limiter to app state
app.state.limiter = limiter

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add request logging middleware with trace ID correlation
app.add_middleware(RequestLoggingMiddleware)


app.include_router(api_router, prefix=settings.API_V1_STR)
