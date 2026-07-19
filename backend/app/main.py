from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import Settings, settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.rate_limit import limiter
from app.core.telemetry import instrument_app, setup_telemetry
from app.services import Txt2CrsApplicationLifecycle

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

Txt2CrsLifecycleFactory = Callable[[Settings], Txt2CrsApplicationLifecycle]


def build_txt2crs_lifecycle(
    application_settings: Settings,
) -> Txt2CrsApplicationLifecycle:
    """Build one shell lifecycle owner for one FastAPI lifespan."""

    return Txt2CrsApplicationLifecycle(settings=application_settings)


def create_app(
    *,
    application_settings: Settings = settings,
    txt2crs_lifecycle_factory: Txt2CrsLifecycleFactory = (build_txt2crs_lifecycle),
) -> FastAPI:
    """
    Construct a FastAPI application with an injectable engine lifecycle.

    Tests inject a recording lifecycle and never need Tavily or Codex. The
    exported production app uses the same function, which keeps middleware,
    routes, observability, and exception handlers identical in both paths.
    """

    @asynccontextmanager
    async def application_lifespan(
        fastapi_app: FastAPI,
    ) -> AsyncIterator[None]:
        # Create a fresh owner for every lifespan re-entry. Storing only the
        # shell service (not config, paths, or secrets) gives later worker and
        # readiness dependencies one stable access point.
        txt2crs_lifecycle = txt2crs_lifecycle_factory(application_settings)
        fastapi_app.state.txt2crs_lifecycle = txt2crs_lifecycle
        try:
            txt2crs_lifecycle.start()
            yield
        finally:
            # The finally block also runs when start raises after partially
            # acquiring a facade, so FastAPI never leaks package resources.
            txt2crs_lifecycle.close()

    fastapi_app = FastAPI(
        title=application_settings.PROJECT_NAME,
        openapi_url=f"{application_settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
        lifespan=application_lifespan,
    )

    # Instrumentation is application-specific and must run after this instance
    # exists. Global exporter setup remains above so it happens only once.
    instrument_app(fastapi_app)
    register_exception_handlers(fastapi_app)
    fastapi_app.state.limiter = limiter

    if application_settings.all_cors_origins:
        fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=application_settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    fastapi_app.add_middleware(RequestLoggingMiddleware)
    fastapi_app.include_router(
        api_router,
        prefix=application_settings.API_V1_STR,
    )
    return fastapi_app


app = create_app()
