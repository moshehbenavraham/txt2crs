from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from txt2crs.application import Txt2CrsApplication
from txt2crs.jobs import ExecutionProfile

from app.api.main import api_router
from app.core.config import Settings, settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware, UploadBodyLimitMiddleware
from app.core.rate_limit import limiter
from app.core.telemetry import instrument_app, setup_telemetry
from app.services import (
    CachedReadinessCoordinator,
    RuntimeOwnershipCoordinator,
    SerialTxt2CrsWorker,
    SystemAuthenticationCoordinator,
    Txt2CrsApplicationLifecycle,
    Txt2CrsSubmissionService,
    build_execution_profile,
)

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
Txt2CrsWorkerFactory = Callable[
    [Txt2CrsApplication, Settings, RuntimeOwnershipCoordinator],
    SerialTxt2CrsWorker,
]
Txt2CrsReadinessFactory = Callable[
    [
        Txt2CrsApplication | None,
        SerialTxt2CrsWorker | None,
        RuntimeOwnershipCoordinator,
        Settings,
    ],
    CachedReadinessCoordinator,
]
Txt2CrsAuthenticationFactory = Callable[
    [
        Txt2CrsApplication | None,
        RuntimeOwnershipCoordinator,
        Settings,
    ],
    SystemAuthenticationCoordinator,
]
Txt2CrsExecutionProfileFactory = Callable[[Settings], ExecutionProfile]

# Multipart boundaries and headers are counted in the HTTP request body but
# are not part of the learner file. This finite allowance lets one exact-limit
# file plus bounded metadata pass while keeping parser overhead constrained.
UPLOAD_MULTIPART_FRAMING_ALLOWANCE_BYTES = 65_536


def build_txt2crs_lifecycle(
    application_settings: Settings,
) -> Txt2CrsApplicationLifecycle:
    """Build one shell lifecycle owner for one FastAPI lifespan."""

    return Txt2CrsApplicationLifecycle(settings=application_settings)


def build_txt2crs_worker(
    application: Txt2CrsApplication,
    application_settings: Settings,
    runtime_ownership: RuntimeOwnershipCoordinator,
) -> SerialTxt2CrsWorker:
    """Build the one-process serial worker from finite shell settings."""

    return SerialTxt2CrsWorker(
        application=application,
        poll_interval_seconds=application_settings.TXT2CRS_WORKER_POLL_SECONDS,
        shutdown_timeout_seconds=(
            application_settings.TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS
        ),
        runtime_ownership=runtime_ownership,
    )


def build_txt2crs_readiness(
    application: Txt2CrsApplication | None,
    worker: SerialTxt2CrsWorker | None,
    runtime_ownership: RuntimeOwnershipCoordinator,
    application_settings: Settings,
) -> CachedReadinessCoordinator:
    """Build one cache over package and safe worker state."""

    return CachedReadinessCoordinator(
        application=application,
        worker=worker,
        runtime_ownership=runtime_ownership,
        refresh_interval_seconds=(
            application_settings.TXT2CRS_READINESS_REFRESH_SECONDS
        ),
        stale_after_seconds=(
            application_settings.TXT2CRS_READINESS_STALE_AFTER_SECONDS
        ),
        shutdown_timeout_seconds=(
            application_settings.TXT2CRS_READINESS_SHUTDOWN_TIMEOUT_SECONDS
        ),
        configured_model_id=application_settings.TXT2CRS_MODEL_ID,
    )


def build_txt2crs_authentication(
    application: Txt2CrsApplication | None,
    runtime_ownership: RuntimeOwnershipCoordinator,
    application_settings: Settings,
) -> SystemAuthenticationCoordinator:
    """Build one cached system-auth owner over the public facade."""

    return SystemAuthenticationCoordinator(
        application=application,
        runtime_ownership=runtime_ownership,
        monitor_poll_seconds=(application_settings.TXT2CRS_AUTH_MONITOR_POLL_SECONDS),
        shutdown_timeout_seconds=(
            application_settings.TXT2CRS_AUTH_SHUTDOWN_TIMEOUT_SECONDS
        ),
    )


def create_app(
    *,
    application_settings: Settings = settings,
    txt2crs_lifecycle_factory: Txt2CrsLifecycleFactory = (build_txt2crs_lifecycle),
    txt2crs_worker_factory: Txt2CrsWorkerFactory = build_txt2crs_worker,
    txt2crs_readiness_factory: Txt2CrsReadinessFactory = (build_txt2crs_readiness),
    txt2crs_authentication_factory: Txt2CrsAuthenticationFactory = (
        build_txt2crs_authentication
    ),
    txt2crs_execution_profile_factory: Txt2CrsExecutionProfileFactory = (
        build_execution_profile
    ),
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
        fastapi_app.state.txt2crs_worker = None
        fastapi_app.state.txt2crs_readiness = None
        fastapi_app.state.txt2crs_authentication = None
        fastapi_app.state.txt2crs_submission = None
        runtime_ownership = RuntimeOwnershipCoordinator()
        fastapi_app.state.txt2crs_runtime_ownership = runtime_ownership
        txt2crs_worker: SerialTxt2CrsWorker | None = None
        txt2crs_readiness: CachedReadinessCoordinator | None = None
        txt2crs_authentication: SystemAuthenticationCoordinator | None = None
        primary_error: BaseException | None = None
        try:
            txt2crs_lifecycle.start()
            txt2crs_application = txt2crs_lifecycle.application
            if txt2crs_application is not None:
                txt2crs_worker = txt2crs_worker_factory(
                    txt2crs_application,
                    application_settings,
                    runtime_ownership,
                )
                fastapi_app.state.txt2crs_worker = txt2crs_worker

            # Refresh cached account state first. Readiness and worker startup
            # then use the same gate, so no two app-servers can overlap.
            txt2crs_authentication = txt2crs_authentication_factory(
                txt2crs_application,
                runtime_ownership,
                application_settings,
            )
            fastapi_app.state.txt2crs_authentication = txt2crs_authentication
            txt2crs_authentication.start()

            # Browser reads see only this cache plus safe worker state and can
            # never launch provider or storage work.
            txt2crs_readiness = txt2crs_readiness_factory(
                txt2crs_application,
                txt2crs_worker,
                runtime_ownership,
                application_settings,
            )
            fastapi_app.state.txt2crs_readiness = txt2crs_readiness
            txt2crs_readiness.start()
            if txt2crs_application is not None and txt2crs_worker is not None:
                # Compose this stateless adapter once from the exact facade,
                # cache, worker, and startup-reviewed profile. Requests then
                # retrieve it without rebuilding or probing provider state.
                fastapi_app.state.txt2crs_submission = Txt2CrsSubmissionService(
                    application=txt2crs_application,
                    readiness=txt2crs_readiness,
                    worker=txt2crs_worker,
                    execution_profile=txt2crs_execution_profile_factory(
                        application_settings
                    ),
                )
            if txt2crs_worker is not None:
                txt2crs_worker.start()
            yield
        except BaseException as error:
            # Cleanup errors must never replace a startup or request failure.
            # The original exception remains authoritative after every
            # acquired worker/facade resource has received one close attempt.
            primary_error = error
            raise
        finally:
            cleanup_error: BaseException | None = None
            if txt2crs_worker is not None:
                try:
                    txt2crs_worker.close()
                except BaseException as error:
                    cleanup_error = error
            if txt2crs_readiness is not None:
                try:
                    txt2crs_readiness.close()
                except BaseException as error:
                    if cleanup_error is None:
                        cleanup_error = error
            if txt2crs_authentication is not None:
                try:
                    txt2crs_authentication.close()
                except BaseException as error:
                    if cleanup_error is None:
                        cleanup_error = error
            runtime_ownership.close()
            # Worker and maintenance must stop before the package facade
            # closes its executor and persistence graph.
            try:
                txt2crs_lifecycle.close()
            except BaseException as error:
                if cleanup_error is None:
                    cleanup_error = error
            fastapi_app.state.txt2crs_worker = None
            fastapi_app.state.txt2crs_readiness = None
            fastapi_app.state.txt2crs_authentication = None
            fastapi_app.state.txt2crs_submission = None
            fastapi_app.state.txt2crs_runtime_ownership = None
            if primary_error is None and cleanup_error is not None:
                raise cleanup_error

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

    fastapi_app.add_middleware(
        UploadBodyLimitMiddleware,
        maximum_body_bytes=(
            application_settings.TXT2CRS_MAX_INPUT_BYTES
            + application_settings.TXT2CRS_MAX_METADATA_BYTES
            + UPLOAD_MULTIPART_FRAMING_ALLOWANCE_BYTES
        ),
        upload_path=f"{application_settings.API_V1_STR}/jobs/upload",
    )
    # Add logging last so it is the outer middleware and assigns a trace ID
    # even when the upload cap rejects a request before FastAPI routing.
    fastapi_app.add_middleware(RequestLoggingMiddleware)
    fastapi_app.include_router(
        api_router,
        prefix=application_settings.API_V1_STR,
    )
    return fastapi_app


app = create_app()
