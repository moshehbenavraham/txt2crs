"""
FastAPI-shell composition boundary for the public txt2crs application.

This module is intentionally the only shell location that translates mutable
environment settings into immutable engine contracts. It may use documented
``txt2crs.application`` and ``txt2crs.jobs`` exports, but it must never import
or reconstruct stores, adapters, provider clients, pipelines, or renderers.
"""

from threading import RLock
from typing import Literal, Protocol

from txt2crs import __version__ as txt2crs_version
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationFactory,
    ApplicationStorageConfig,
    RealApplicationConfig,
    RealApplicationFactory,
    Txt2CrsApplication,
)
from txt2crs.jobs import (
    ExecutionProfile,
    InputExecutionLimits,
    RequestRetryPolicy,
    RunExecutionLimits,
)

from app.core.config import Settings
from app.core.logging import get_logger

EXECUTION_PROFILE_SCHEMA_VERSION: Literal["1.0"] = "1.0"
PROMPT_VERSION = "course-pipeline-v1"
CONTENT_POLICY_VERSION = "content-policy-v1"
# P0 performs no time-based purge. The package contract requires a finite
# positive retention value, so its maximum keeps expiry effectively disabled
# until Phase 04 introduces coordinated request/artifact retention semantics.
P0_ARTIFACT_RETENTION_DAYS = 36_500

logger = get_logger(__name__)


class ApplicationFactoryBuilder(Protocol):
    """Injectable shell boundary that accepts only one public package config."""

    def __call__(self, config: RealApplicationConfig) -> ApplicationFactory:
        """Return a package-owned facade factory."""


def build_real_application_factory(
    config: RealApplicationConfig,
) -> ApplicationFactory:
    """Return the package-owned real factory without assembling its graph."""

    return RealApplicationFactory(config)


def build_execution_profile(settings: Settings) -> ExecutionProfile:
    """
    Detach one exact finite job profile from validated shell settings.

    The returned Pydantic contract is frozen by the engine package. A durable
    request can therefore retain this exact identity even if an operator later
    changes environment defaults before a process restart.
    """
    # A source-tree fallback version can contain ``+`` while the engine's
    # identifier contract permits dots. Normal installed releases are already
    # plain SemVer, and this replacement keeps both forms deterministic.
    safe_engine_version = txt2crs_version.replace("+", ".")
    return ExecutionProfile(
        schema_version=EXECUTION_PROFILE_SCHEMA_VERSION,
        engine_version=f"txt2crs-{safe_engine_version}",
        prompt_version=PROMPT_VERSION,
        policy_version=CONTENT_POLICY_VERSION,
        model_id=settings.TXT2CRS_MODEL_ID,
        reasoning_effort="high",
        retry_policy=RequestRetryPolicy(
            maximum_attempts=settings.TXT2CRS_RETRY_MAXIMUM_ATTEMPTS,
            base_seconds=settings.TXT2CRS_RETRY_BASE_SECONDS,
            maximum_seconds=settings.TXT2CRS_RETRY_MAXIMUM_SECONDS,
            jitter_ratio=settings.TXT2CRS_RETRY_JITTER_RATIO,
        ),
        input_limits=InputExecutionLimits(
            maximum_input_bytes=settings.TXT2CRS_MAX_INPUT_BYTES,
            maximum_metadata_bytes=settings.TXT2CRS_MAX_METADATA_BYTES,
            maximum_normalized_characters=(settings.TXT2CRS_MAX_NORMALIZED_CHARACTERS),
            maximum_pdf_pages=settings.TXT2CRS_MAX_PDF_PAGES,
        ),
        run_limits=RunExecutionLimits(
            maximum_turns=settings.TXT2CRS_RUN_MAXIMUM_TURNS,
            maximum_research_calls=(settings.TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS),
            maximum_search_calls=settings.TXT2CRS_RUN_MAXIMUM_SEARCH_CALLS,
            maximum_extract_calls=settings.TXT2CRS_RUN_MAXIMUM_EXTRACT_CALLS,
            maximum_sources=settings.TXT2CRS_RUN_MAXIMUM_SOURCES,
            maximum_extracted_bytes=(settings.TXT2CRS_RUN_MAXIMUM_EXTRACTED_BYTES),
            maximum_input_tokens=settings.TXT2CRS_RUN_MAXIMUM_INPUT_TOKENS,
            maximum_output_tokens=settings.TXT2CRS_RUN_MAXIMUM_OUTPUT_TOKENS,
            maximum_retries=settings.TXT2CRS_RUN_MAXIMUM_RETRIES,
            maximum_repairs=settings.TXT2CRS_RUN_MAXIMUM_REPAIRS,
            maximum_elapsed_seconds=(settings.TXT2CRS_RUN_MAXIMUM_ELAPSED_SECONDS),
        ),
    )


def build_real_application_config(
    settings: Settings,
) -> RealApplicationConfig | None:
    """
    Translate configured shell values into one strict public engine config.

    Missing or explicitly disabled research is a supported operator-setup
    state. Returning ``None`` prevents a partial graph or fake Tavily secret;
    invalid finite/path configuration still fails earlier in ``Settings``.
    """
    if not settings.TXT2CRS_RESEARCH_ENABLED or settings.TAVILY_API_KEY is None:
        return None

    return RealApplicationConfig(
        storage=ApplicationStorageConfig(
            state_directory=settings.TXT2CRS_STATE_ROOT,
            job_database_path=settings.TXT2CRS_JOB_DB_PATH,
            artifact_directory=settings.TXT2CRS_ARTIFACT_ROOT,
            maximum_artifact_job_bytes=(settings.TXT2CRS_ARTIFACT_MAX_JOB_BYTES),
            artifact_retention_days=P0_ARTIFACT_RETENTION_DAYS,
        ),
        admission=ApplicationAdmissionConfig(
            window_seconds=settings.TXT2CRS_ADMISSION_WINDOW_SECONDS,
            maximum_jobs_per_user=(settings.TXT2CRS_ADMISSION_MAXIMUM_JOBS_PER_USER),
            maximum_jobs_global=(settings.TXT2CRS_ADMISSION_MAXIMUM_JOBS_GLOBAL),
            maximum_reserved_tokens_per_user=(
                settings.TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER
            ),
            maximum_reserved_tokens_global=(
                settings.TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_GLOBAL
            ),
            maximum_research_cost_microusd_per_user=(
                settings.TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_PER_USER
            ),
            maximum_research_cost_microusd_global=(
                settings.TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_GLOBAL
            ),
        ),
        default_execution_profile=build_execution_profile(settings),
        codex_home=settings.TXT2CRS_CODEX_HOME,
        worker_directory=settings.TXT2CRS_WORKER_ROOT,
        tavily_api_key=settings.TAVILY_API_KEY,
        managed_mcp_host=settings.TXT2CRS_RESEARCH_MCP_HOST,
        managed_mcp_port=settings.TXT2CRS_RESEARCH_MCP_PORT,
        managed_mcp_startup_timeout_seconds=(
            settings.TXT2CRS_RESEARCH_MCP_STARTUP_TIMEOUT_SECONDS
        ),
        managed_mcp_shutdown_timeout_seconds=(
            settings.TXT2CRS_RESEARCH_MCP_SHUTDOWN_TIMEOUT_SECONDS
        ),
        http_timeout_seconds=settings.TAVILY_TIMEOUT_SECONDS,
    )


class Txt2CrsApplicationLifecycle:
    """
    Own at most one public engine facade for one FastAPI lifespan.

    The lock protects future worker/readiness access from observing a
    half-started or half-closed reference. Provider resources remain owned by
    the package facade and are not exposed through this shell service.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        factory_builder: ApplicationFactoryBuilder = build_real_application_factory,
    ) -> None:
        self._settings = settings
        self._factory_builder = factory_builder
        self._lock = RLock()
        self._application: Txt2CrsApplication | None = None
        self._is_started = False
        self._is_configured = False

    @property
    def application(self) -> Txt2CrsApplication | None:
        """Return the configured facade, or ``None`` during setup state."""

        with self._lock:
            return self._application

    @property
    def is_started(self) -> bool:
        """Return whether this lifecycle completed its start transition."""

        with self._lock:
            return self._is_started

    @property
    def is_configured(self) -> bool:
        """Return whether the current lifespan owns a real engine facade."""

        with self._lock:
            return self._is_configured

    def start(self) -> None:
        """
        Create the configured facade once or enter safe setup state.

        Construction remains inside the lifecycle lock so concurrent startup
        triggers cannot create two SQLite owners or provider-authentication
        clients. State changes only after the package factory returns a fully
        owned facade, which leaves a failed attempt cleanly retryable.
        """
        with self._lock:
            if self._is_started:
                return

            logger.info("txt2crs.composition_started")
            try:
                application_config = build_real_application_config(self._settings)
                if application_config is None:
                    self._is_configured = False
                    self._is_started = True
                    logger.info(
                        "txt2crs.configuration_validated",
                        extra={
                            "configured": False,
                            "reason_code": "research_not_configured",
                        },
                    )
                    logger.info(
                        "txt2crs.composition_completed",
                        extra={"configured": False},
                    )
                    return

                application_factory = self._factory_builder(application_config)
                application = application_factory.create()
                self._application = application
                self._is_configured = True
                self._is_started = True
                logger.info(
                    "txt2crs.composition_completed",
                    extra={"configured": True},
                )
            except BaseException:
                # Never include the exception, config, secret, or private paths
                # in this event. Later shell error translation owns the
                # caller-safe failure code.
                self._application = None
                self._is_configured = False
                self._is_started = False
                logger.error("txt2crs.composition_failed")
                raise

    def close(self) -> None:
        """
        Clear shell ownership and close the package facade at most once.

        The reference and state flags are reset before calling package cleanup.
        If cleanup raises after partially releasing resources, a second shell
        close cannot invoke the same facade again or mask the original error.
        """
        with self._lock:
            application = self._application
            was_started = self._is_started
            self._application = None
            self._is_configured = False
            self._is_started = False
            if not was_started and application is None:
                return

            logger.info(
                "txt2crs.shutdown_started",
                extra={"configured": application is not None},
            )
            try:
                if application is not None:
                    application.close()
            except BaseException:
                logger.error("txt2crs.shutdown_failed")
                raise
            logger.info("txt2crs.shutdown_completed")
