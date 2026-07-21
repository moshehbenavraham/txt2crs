"""
Application configuration using Pydantic Settings.

This module provides centralized configuration management for the application,
loading settings from environment variables with sensible defaults for local
development. All settings are validated at startup.

Configuration Sources (in order of precedence):
    1. Environment variables
    2. .env file in the backend directory
    3. Default values defined in the Settings class

Environment Variables:
    Required (no defaults):
        - PROJECT_NAME: Display name for the application
        - ENVIRONMENT: "local", "staging", or "production"
        - POSTGRES_SERVER: PostgreSQL host address
        - POSTGRES_USER: PostgreSQL username
        - FIRST_SUPERUSER: Email for the initial admin user
        - FIRST_SUPERUSER_PASSWORD: Password for the initial admin user

    Optional (with defaults):
        - SECRET_KEY: JWT signing key (auto-generated only for local)
        - ACCESS_TOKEN_EXPIRE_MINUTES: JWT expiry (default: 1440 = 24 hours)
        - POSTGRES_PORT: Database port (default: 5450 for host development)
        - POSTGRES_PASSWORD: Database password (default: "")
        - POSTGRES_DB: Database name (default: "")
        - SMTP_*: Email configuration (all optional)
        - SENTRY_DSN: Sentry error tracking URL (optional)
        - BACKEND_CORS_ORIGINS: Comma-separated CORS origins (default: [])
        - FRONTEND_HOST: Frontend URL for CORS (default: http://localhost:5196)

Example:
    Access settings anywhere in the application:

    >>> from app.core.config import settings
    >>> print(settings.PROJECT_NAME)
    "My Application"
    >>> print(settings.ENVIRONMENT)
    "local"

Note:
    In non-local environments, SECRET_KEY, POSTGRES_PASSWORD, and
    FIRST_SUPERUSER_PASSWORD must not be "changethis" or a ValueError
    will be raised at startup.
"""

import secrets
from ipaddress import ip_address
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    Field,
    HttpUrl,
    PostgresDsn,
    SecretStr,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """
    Parse CORS origins from environment variable.

    Handles multiple input formats for flexibility in configuration:
    - Comma-separated string: "http://localhost:5195,http://localhost:5196"
    - JSON array string: '["http://localhost:5196"]'
    - Python list (when set programmatically)

    Args:
        v: Raw value from environment variable or direct assignment.
            Can be a comma-separated string, JSON array string, or list.

    Returns:
        List of origin strings or the original value if already valid.

    Raises:
        ValueError: If the value cannot be parsed as a valid CORS origin list.

    Example:
        >>> parse_cors("http://localhost:5196,http://example.com")
        ['http://localhost:5196', 'http://example.com']
        >>> parse_cors('["http://localhost:5196"]')
        '["http://localhost:5196"]'  # Passed through for Pydantic to parse
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def parse_optional_secret(value: Any) -> SecretStr | None:
    """
    Normalize an optional provider secret without retaining whitespace.

    Operator setup and OpenAPI must load before Tavily is configured. Treating
    an empty dotenv placeholder as ``None`` gives the composition service one
    explicit unconfigured state instead of constructing a fake credential.
    """
    if value is None:
        return None
    secret_value = (
        value.get_secret_value() if isinstance(value, SecretStr) else str(value)
    ).strip()
    return SecretStr(secret_value) if secret_value else None


def _path_uses_existing_symlink(path: Path) -> bool:
    """
    Return whether an absolute path traverses an existing symbolic link.

    `Path.resolve()` follows symlinks, which is useful for normalization but
    would erase the evidence needed for this startup safety check. Walking the
    original path first lets configuration fail closed when either the final
    path or an existing parent redirects storage somewhere unexpected.
    """
    current_path = Path(path.anchor)
    for path_part in path.parts[1:]:
        current_path /= path_part
        if current_path.is_symlink():
            return True
    return False


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    This class uses Pydantic Settings to load and validate configuration
    from environment variables and .env files. All settings are validated
    at application startup.

    Attributes:
        API_V1_STR: Base path prefix for API v1 endpoints.
        SECRET_KEY: Secret key for JWT token signing. Auto-generated if not set.
            MUST be changed in production environments.
        ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time in minutes.
            Default is 8 days (11520 minutes).
        FRONTEND_HOST: URL of the frontend application for CORS configuration.
        ENVIRONMENT: Deployment environment. Affects security validations
            and feature flags.

    Security:
        In staging/production environments, the following must not be "changethis":
        - SECRET_KEY
        - POSTGRES_PASSWORD
        - FIRST_SUPERUSER_PASSWORD

    Example:
        Access settings in application code:

        >>> from app.core.config import settings
        >>> if settings.ENVIRONMENT == "production":
        ...     # Production-specific logic
        ...     pass
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # === API Configuration ===
    API_V1_STR: str = "/api/v1"
    """Base path prefix for all API v1 endpoints (e.g., "/api/v1")."""

    SECRET_KEY: str = secrets.token_urlsafe(32)
    """JWT signing secret. Auto-generated for local dev; MUST be set in production."""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    """JWT access token expiration in minutes. Default: 1440 (24 hours)."""

    FRONTEND_HOST: str = "http://localhost:5196"
    """Frontend application URL. Added to CORS allowed origins automatically."""

    ENVIRONMENT: Literal["local", "staging", "production"]
    """Deployment environment. Controls security validations and feature flags."""

    ENABLE_PRIVATE_DEV_ROUTES: bool = False
    """
    Enable local-only `/private` routes.

    This must only be enabled in local development, and stays disabled in
    staging/production regardless of accidental enablement attempts.
    """

    @computed_field  # type: ignore[prop-decorator]
    @property
    def private_dev_routes_enabled(self) -> bool:
        """True only when private development routes are explicitly enabled locally."""
        return self.ENVIRONMENT == "local" and self.ENABLE_PRIVATE_DEV_ROUTES

    ENABLE_PUBLIC_SIGNUP: bool = False
    """
    Enable unauthenticated account registration only for local development.

    The default remains false for the judge/demo profile, where an operator
    provisions a bounded account instead of exposing the shared subscription.
    """

    @computed_field  # type: ignore[prop-decorator]
    @property
    def public_signup_enabled(self) -> bool:
        """True only for an explicit local developer-mode selection."""

        return self.ENVIRONMENT == "local" and self.ENABLE_PUBLIC_SIGNUP

    # === CORS Configuration ===
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    """
    Additional CORS allowed origins (comma-separated or JSON array).
    FRONTEND_HOST is always included automatically via all_cors_origins.
    Example: "http://localhost:5195,http://localhost:5196"
    """

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """
        Combined list of all CORS allowed origins.

        Includes both explicitly configured BACKEND_CORS_ORIGINS and
        FRONTEND_HOST. Trailing slashes are stripped for consistency.

        Returns:
            List of origin URLs without trailing slashes.
        """
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # === Project & Monitoring ===
    PROJECT_NAME: str
    """Display name for the application. Required, no default."""

    SENTRY_DSN: HttpUrl | None = None
    """Sentry DSN URL for error tracking. Optional; disabled if not set."""

    # === OpenTelemetry Configuration ===
    OTEL_ENABLED: bool = False
    """Enable OpenTelemetry distributed tracing. Default: False (opt-in)."""

    OTLP_ENDPOINT: str | None = None
    """
    OTLP exporter endpoint URL for sending traces.
    Example: "http://localhost:4324" (gRPC) or "http://localhost:4325/v1/traces" (HTTP).
    If not set, tracing is disabled even if OTEL_ENABLED is True.
    """

    OTEL_SERVICE_NAME: str | None = None
    """
    Service name for traces. Defaults to PROJECT_NAME if not set.
    Used as service.name resource attribute in OpenTelemetry.
    """

    OTEL_TRACES_SAMPLER_ARG: float = 1.0
    """
    Trace sampling rate (0.0 to 1.0). Default: 1.0 (sample all traces).
    Set to 0.1 to sample 10% of traces in high-traffic production environments.
    """

    # === MCP (Model Context Protocol) Configuration ===
    MCP_ENABLED: bool = True
    """
    Enable MCP server for AI agent tool access. Default: True.
    When enabled, AI agents can access database introspection and validation tools.
    """

    MCP_DB_READ_ONLY: bool = True
    """
    Restrict MCP database access to read-only operations. Default: True.
    NEVER disable this in production environments.
    """

    # === txt2crs Private Filesystem Configuration ===
    TXT2CRS_STATE_ROOT: Path = Path("/var/lib/txt2crs")
    """
    Application-owned persistent root for engine state.

    SQLite state, rendered artifacts, and Codex-managed credentials must stay
    below this boundary so one private volume can preserve them together.
    """

    TXT2CRS_JOB_DB_PATH: Path = Path("/var/lib/txt2crs/jobs.sqlite3")
    """Tenant-scoped SQLite job and checkpoint database file."""

    TXT2CRS_ARTIFACT_ROOT: Path = Path("/var/lib/txt2crs/artifacts")
    """Private root for integrity-checked rendered artifacts."""

    TXT2CRS_CODEX_HOME: Path = Path("/var/lib/txt2crs/codex-home")
    """Isolated persistent CODEX_HOME for the dedicated application identity."""

    TXT2CRS_WORKER_ROOT: Path = Path("/tmp/txt2crs-worker")
    """Empty ephemeral working directory used by the read-only Codex sandbox."""

    # === txt2crs Application Composition ===
    #
    # These finite defaults are copied into the immutable execution profile
    # stored with each accepted job. Changing an environment default later
    # therefore cannot reinterpret already-durable work after a restart.
    TXT2CRS_MODEL_ID: Literal[
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "gpt-5.6-luna",
    ] = "gpt-5.6-sol"
    """Exact reviewed GPT-5.6 family model; no older-model fallback exists."""

    TXT2CRS_RESEARCH_ENABLED: bool = True
    """Disable-only operator switch for package-owned Tavily research."""

    TXT2CRS_RESEARCH_MCP_HOST: str = "127.0.0.1"
    """Numeric loopback host for the private package-owned research MCP."""

    TXT2CRS_RESEARCH_MCP_PORT: int = Field(default=8765, ge=0, le=65_535)
    """Private MCP port; zero is retained for isolated dynamic-port tests."""

    TXT2CRS_RESEARCH_MCP_STARTUP_TIMEOUT_SECONDS: float = Field(
        default=10,
        gt=0,
        le=60,
    )
    """Maximum bounded wait for the two-tool research MCP to become ready."""

    TXT2CRS_RESEARCH_MCP_SHUTDOWN_TIMEOUT_SECONDS: float = Field(
        default=10,
        gt=0,
        le=60,
    )
    """Maximum bounded wait for managed research MCP shutdown."""

    TXT2CRS_WORKER_POLL_SECONDS: float = Field(default=2, gt=0, le=60)
    """Durable queue scan interval; in-process nudges only reduce latency."""

    TXT2CRS_WORKER_HEARTBEAT_SECONDS: float = Field(default=5, gt=0, le=60)
    """Content-free activity pulse while one course executor is running."""

    TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS: float = Field(
        default=30,
        gt=0,
        le=300,
    )
    """Maximum graceful drain before restart-safe worker interruption."""

    TXT2CRS_READINESS_REFRESH_SECONDS: float = Field(
        default=60,
        gt=0,
        le=3_600,
    )
    """Bounded interval between provider and destructive storage probes."""

    TXT2CRS_READINESS_STALE_AFTER_SECONDS: float = Field(
        default=120,
        gt=0,
        le=7_200,
    )
    """Maximum age accepted for the last complete readiness projection."""

    TXT2CRS_READINESS_SHUTDOWN_TIMEOUT_SECONDS: float = Field(
        default=30,
        gt=0,
        le=300,
    )
    """Maximum finite join for the readiness maintenance thread."""

    TXT2CRS_AUTH_MONITOR_POLL_SECONDS: float = Field(
        default=0.5,
        gt=0,
        le=10,
    )
    """Finite interval for reading an active package ceremony's memory state."""

    TXT2CRS_AUTH_SHUTDOWN_TIMEOUT_SECONDS: float = Field(
        default=10,
        gt=0,
        le=60,
    )
    """Maximum finite join for the shell authentication monitor."""

    TXT2CRS_MAX_INPUT_BYTES: int = Field(
        default=20_971_520,
        gt=0,
        le=1_000_000_000,
    )
    """Maximum raw payload size stored with one generation request."""

    TXT2CRS_MAX_METADATA_BYTES: int = Field(
        default=262_144,
        gt=0,
        le=10_000_000,
    )
    """Maximum canonical input metadata size stored with one request."""

    TXT2CRS_MAX_NORMALIZED_CHARACTERS: int = Field(
        default=200_000,
        gt=0,
        le=2_000_000,
    )
    """Maximum normalized text length after bounded ingestion."""

    TXT2CRS_MAX_PDF_PAGES: int = Field(default=200, gt=0, le=10_000)
    """Maximum pages accepted from one PDF."""

    TXT2CRS_ARTIFACT_MAX_JOB_BYTES: int = Field(
        default=104_857_600,
        gt=0,
        le=1_000_000_000,
    )
    """Maximum complete private publication bundle for one job."""

    TXT2CRS_HTML_PREVIEW_MAX_BYTES: int = Field(
        default=5_242_880,
        gt=0,
        le=100_000_000,
    )
    """Maximum HTML artifact bytes a later browser preview may read."""

    TXT2CRS_RETRY_MAXIMUM_ATTEMPTS: int = Field(default=3, ge=2, le=10)
    """Total attempts allowed by the shared provider retry policy."""

    TXT2CRS_RETRY_BASE_SECONDS: float = Field(default=1, gt=0, le=60)
    """Initial retry backoff in seconds."""

    TXT2CRS_RETRY_MAXIMUM_SECONDS: float = Field(default=15, gt=0, le=300)
    """Maximum retry backoff in seconds."""

    TXT2CRS_RETRY_JITTER_RATIO: float = Field(default=0.2, ge=0, le=1)
    """Bounded jitter ratio used by deterministic retry calculations."""

    TXT2CRS_RUN_MAXIMUM_TURNS: int = Field(default=20, gt=0, le=10_000)
    TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS: int = Field(default=12, gt=0, le=10_000)
    TXT2CRS_RUN_MAXIMUM_SEARCH_CALLS: int = Field(default=6, gt=0, le=10_000)
    TXT2CRS_RUN_MAXIMUM_EXTRACT_CALLS: int = Field(default=6, gt=0, le=10_000)
    TXT2CRS_RUN_MAXIMUM_SOURCES: int = Field(default=12, gt=0, le=1_000)
    TXT2CRS_RUN_MAXIMUM_EXTRACTED_BYTES: int = Field(
        default=2_000_000,
        gt=0,
        le=100_000_000,
    )
    TXT2CRS_RUN_MAXIMUM_INPUT_TOKENS: int = Field(
        default=600_000,
        gt=0,
        le=10_000_000,
    )
    TXT2CRS_RUN_MAXIMUM_OUTPUT_TOKENS: int = Field(
        default=150_000,
        gt=0,
        le=10_000_000,
    )
    TXT2CRS_RUN_MAXIMUM_RETRIES: int = Field(default=3, ge=0, le=1_000)
    TXT2CRS_RUN_MAXIMUM_REPAIRS: int = Field(default=3, ge=0, le=1_000)
    TXT2CRS_RUN_MAXIMUM_ELAPSED_SECONDS: float = Field(
        default=2_700,
        gt=0,
        le=86_400,
    )

    TXT2CRS_ADMISSION_WINDOW_SECONDS: int = Field(
        default=86_400,
        gt=0,
        le=2_592_000,
    )
    TXT2CRS_ADMISSION_MAXIMUM_JOBS_PER_USER: int = Field(
        default=2,
        gt=0,
        le=10_000,
    )
    TXT2CRS_ADMISSION_MAXIMUM_JOBS_GLOBAL: int = Field(
        default=5,
        gt=0,
        le=100_000,
    )
    TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER: int = Field(
        default=1_500_000,
        gt=0,
        le=1_000_000_000,
    )
    TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_GLOBAL: int = Field(
        default=3_750_000,
        gt=0,
        le=10_000_000_000,
    )
    TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_PER_USER: int = Field(
        default=2_000_000,
        ge=0,
        le=1_000_000_000_000,
    )
    TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_GLOBAL: int = Field(
        default=5_000_000,
        ge=0,
        le=10_000_000_000_000,
    )

    TAVILY_API_KEY: Annotated[
        SecretStr | None,
        BeforeValidator(parse_optional_secret),
    ] = None
    """Optional research secret; absence keeps the shell safely unconfigured."""

    TAVILY_TIMEOUT_SECONDS: float = Field(default=20, gt=0, le=60)
    """Timeout for each package-owned Tavily HTTP request."""

    @field_validator("TXT2CRS_RESEARCH_MCP_HOST")
    @classmethod
    def _require_numeric_loopback_research_host(cls, configured_host: str) -> str:
        """
        Keep the research MCP off wildcard, DNS, and external interfaces.

        A numeric address makes the security decision independent of mutable
        host resolution. Both IPv4 and IPv6 loopback addresses remain valid.
        """
        try:
            parsed_address = ip_address(configured_host)
        except ValueError:
            raise ValueError(
                "TXT2CRS_RESEARCH_MCP_HOST must be a numeric loopback address."
            ) from None
        if not parsed_address.is_loopback:
            raise ValueError(
                "TXT2CRS_RESEARCH_MCP_HOST must be a numeric loopback address."
            )
        return str(parsed_address)

    @model_validator(mode="after")
    def _validate_txt2crs_composition_budgets(self) -> Self:
        """
        Reject finite settings that cannot produce one internally valid job.

        Pydantic validates each individual bound above. These relationships
        ensure the complete profile can pay for its own retry and provider
        actions and that per-user reservations fit inside global capacity.
        """
        if (
            self.TXT2CRS_READINESS_STALE_AFTER_SECONDS
            < self.TXT2CRS_READINESS_REFRESH_SECONDS
        ):
            raise ValueError(
                "TXT2CRS readiness stale bound must not be shorter than refresh."
            )

        if self.TXT2CRS_RETRY_BASE_SECONDS > self.TXT2CRS_RETRY_MAXIMUM_SECONDS:
            raise ValueError(
                "TXT2CRS_RETRY_BASE_SECONDS must not exceed "
                "TXT2CRS_RETRY_MAXIMUM_SECONDS."
            )

        maximum_retry_count = self.TXT2CRS_RETRY_MAXIMUM_ATTEMPTS - 1
        if self.TXT2CRS_RUN_MAXIMUM_RETRIES < maximum_retry_count:
            raise ValueError(
                "TXT2CRS_RUN_MAXIMUM_RETRIES must cover the configured retry policy."
            )

        planned_research_calls = (
            self.TXT2CRS_RUN_MAXIMUM_SEARCH_CALLS
            + self.TXT2CRS_RUN_MAXIMUM_EXTRACT_CALLS
        )
        if planned_research_calls > self.TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS:
            raise ValueError(
                "TXT2CRS search and extract call limits must fit within "
                "TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS."
            )

        if self.TXT2CRS_HTML_PREVIEW_MAX_BYTES > (self.TXT2CRS_ARTIFACT_MAX_JOB_BYTES):
            raise ValueError(
                "TXT2CRS_HTML_PREVIEW_MAX_BYTES must not exceed "
                "TXT2CRS_ARTIFACT_MAX_JOB_BYTES."
            )

        admission_pairs = (
            (
                "jobs",
                self.TXT2CRS_ADMISSION_MAXIMUM_JOBS_PER_USER,
                self.TXT2CRS_ADMISSION_MAXIMUM_JOBS_GLOBAL,
            ),
            (
                "reserved tokens",
                self.TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER,
                self.TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_GLOBAL,
            ),
            (
                "research allowance",
                self.TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_PER_USER,
                self.TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_GLOBAL,
            ),
        )
        for capacity_name, per_user_capacity, global_capacity in admission_pairs:
            if per_user_capacity > global_capacity:
                raise ValueError(
                    f"TXT2CRS admission {capacity_name} per user must not "
                    "exceed global capacity."
                )

        reserved_job_tokens = (
            self.TXT2CRS_RUN_MAXIMUM_INPUT_TOKENS
            + self.TXT2CRS_RUN_MAXIMUM_OUTPUT_TOKENS
        )
        if reserved_job_tokens > (
            self.TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER
        ):
            raise ValueError(
                "TXT2CRS per-user reserved tokens must admit one complete job."
            )

        reserved_job_research_microusd = 1_000_000
        if reserved_job_research_microusd > (
            self.TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_PER_USER
        ):
            raise ValueError(
                "TXT2CRS per-user research allowance must admit one complete job."
            )

        return self

    @model_validator(mode="after")
    def _derive_txt2crs_persistent_path_defaults(self) -> Self:
        """
        Keep omitted persistent children attached to a custom state root.

        Pydantic field defaults are independent values. Without this small
        derivation step, changing only TXT2CRS_STATE_ROOT would silently leave
        the database, artifacts, and credentials under `/var/lib/txt2crs`.
        Explicit child overrides are preserved for deployments that need a
        deeper directory layout inside the same private root.
        """
        persistent_child_defaults = {
            "TXT2CRS_JOB_DB_PATH": self.TXT2CRS_STATE_ROOT / "jobs.sqlite3",
            "TXT2CRS_ARTIFACT_ROOT": self.TXT2CRS_STATE_ROOT / "artifacts",
            "TXT2CRS_CODEX_HOME": self.TXT2CRS_STATE_ROOT / "codex-home",
        }
        for field_name, derived_path in persistent_child_defaults.items():
            if field_name not in self.model_fields_set:
                setattr(self, field_name, derived_path)

        return self

    @model_validator(mode="after")
    def _validate_txt2crs_path_boundaries(self) -> Self:
        """
        Normalize engine paths and reject layouts that escape private storage.

        Persistent children must be strict descendants of the state root.
        Artifacts, credentials, and the SQLite file also receive distinct
        boundaries so one subsystem cannot overwrite another. The worker
        directory is deliberately outside persistent storage because Codex
        uses it only as an empty, isolated working directory.
        """
        configured_paths = {
            "TXT2CRS_STATE_ROOT": self.TXT2CRS_STATE_ROOT,
            "TXT2CRS_JOB_DB_PATH": self.TXT2CRS_JOB_DB_PATH,
            "TXT2CRS_ARTIFACT_ROOT": self.TXT2CRS_ARTIFACT_ROOT,
            "TXT2CRS_CODEX_HOME": self.TXT2CRS_CODEX_HOME,
            "TXT2CRS_WORKER_ROOT": self.TXT2CRS_WORKER_ROOT,
        }

        normalized_paths: dict[str, Path] = {}
        for field_name, configured_path in configured_paths.items():
            if not configured_path.is_absolute():
                raise ValueError(f"{field_name} must be an absolute path.")
            if _path_uses_existing_symlink(configured_path):
                raise ValueError(
                    f"{field_name} must not use an existing symlink endpoint or parent."
                )

            normalized_paths[field_name] = configured_path.resolve(strict=False)

        state_root = normalized_paths["TXT2CRS_STATE_ROOT"]
        persistent_child_names = (
            "TXT2CRS_JOB_DB_PATH",
            "TXT2CRS_ARTIFACT_ROOT",
            "TXT2CRS_CODEX_HOME",
        )
        for field_name in persistent_child_names:
            child_path = normalized_paths[field_name]
            if child_path == state_root or not child_path.is_relative_to(state_root):
                raise ValueError(
                    f"{field_name} must be a strict child of TXT2CRS_STATE_ROOT."
                )

        job_database_path = normalized_paths["TXT2CRS_JOB_DB_PATH"]
        artifact_root = normalized_paths["TXT2CRS_ARTIFACT_ROOT"]
        codex_home = normalized_paths["TXT2CRS_CODEX_HOME"]
        worker_root = normalized_paths["TXT2CRS_WORKER_ROOT"]

        directory_boundaries_overlap = (
            artifact_root == codex_home
            or artifact_root.is_relative_to(codex_home)
            or codex_home.is_relative_to(artifact_root)
        )
        if directory_boundaries_overlap:
            raise ValueError(
                "TXT2CRS_ARTIFACT_ROOT and TXT2CRS_CODEX_HOME must not overlap."
            )

        database_overlaps_directory = (
            job_database_path == artifact_root
            or job_database_path == codex_home
            or job_database_path.is_relative_to(artifact_root)
            or job_database_path.is_relative_to(codex_home)
            or artifact_root.is_relative_to(job_database_path)
            or codex_home.is_relative_to(job_database_path)
        )
        if database_overlaps_directory:
            raise ValueError(
                "TXT2CRS_JOB_DB_PATH must not overlap an engine directory."
            )

        if worker_root == state_root or worker_root.is_relative_to(state_root):
            raise ValueError(
                "TXT2CRS_WORKER_ROOT must remain outside TXT2CRS_STATE_ROOT."
            )

        # Expose the normalized values everywhere else in the shell. Package
        # factories can now consume one canonical representation instead of
        # repeating path cleanup at each call site.
        for field_name, normalized_path in normalized_paths.items():
            setattr(self, field_name, normalized_path)

        return self

    # === Database Configuration ===
    POSTGRES_SERVER: str
    """PostgreSQL server hostname or IP address. Required, no default."""

    POSTGRES_PORT: int = 5450
    """Registered host PostgreSQL port; Compose overrides internal clients to 5432."""

    POSTGRES_USER: str
    """PostgreSQL username for database connection. Required, no default."""

    POSTGRES_PASSWORD: str = ""
    """PostgreSQL password. MUST not be 'changethis' in production."""

    POSTGRES_DB: str = ""
    """PostgreSQL database name. Defaults to empty string."""

    DB_POOL_PRE_PING: bool = True
    """Enable connection liveness checks before pool checkout."""

    DB_POOL_SIZE: int | None = Field(default=None, ge=1)
    """Optional override for SQLAlchemy QueuePool size."""

    DB_POOL_MAX_OVERFLOW: int | None = Field(default=None, ge=0)
    """Optional override for SQLAlchemy max overflow connections."""

    DB_POOL_TIMEOUT_SECONDS: int | None = Field(default=None, ge=1)
    """Optional override for pool checkout timeout in seconds."""

    DB_POOL_RECYCLE_SECONDS: int | None = Field(default=None, ge=30)
    """Optional override for connection recycle interval in seconds."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_db_pool_size(self) -> int:
        """
        Effective SQLAlchemy pool size by environment.

        Local defaults stay conservative to avoid over-allocating local DB
        connections; non-local defaults provide additional concurrency headroom.
        """
        if self.DB_POOL_SIZE is not None:
            return self.DB_POOL_SIZE
        return 5 if self.ENVIRONMENT == "local" else 10

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_db_pool_max_overflow(self) -> int:
        """Effective SQLAlchemy max overflow by environment."""
        if self.DB_POOL_MAX_OVERFLOW is not None:
            return self.DB_POOL_MAX_OVERFLOW
        return 10 if self.ENVIRONMENT == "local" else 20

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_db_pool_timeout_seconds(self) -> int:
        """Effective pool checkout timeout in seconds."""
        if self.DB_POOL_TIMEOUT_SECONDS is not None:
            return self.DB_POOL_TIMEOUT_SECONDS
        return 30

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_db_pool_recycle_seconds(self) -> int:
        """Effective connection recycle interval in seconds."""
        if self.DB_POOL_RECYCLE_SECONDS is not None:
            return self.DB_POOL_RECYCLE_SECONDS
        return 1800

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        """
        Construct the PostgreSQL database connection URI.

        Builds a SQLAlchemy-compatible connection string from individual
        database configuration parameters using the psycopg driver.

        Returns:
            PostgresDsn: Validated PostgreSQL connection URI.

        Example:
            postgresql+psycopg://user:pass@localhost:5450/mydb
        """
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # === Email Configuration ===
    SMTP_TLS: bool = True
    """Enable STARTTLS for SMTP connection. Default: True."""

    SMTP_SSL: bool = False
    """Enable SSL/TLS for SMTP connection. Default: False (use STARTTLS instead)."""

    SMTP_PORT: int = 587
    """SMTP server port. Default: 587 (standard STARTTLS port)."""

    SMTP_HOST: str | None = None
    """SMTP server hostname. Required for email functionality."""

    SMTP_TIMEOUT_SECONDS: int = Field(default=10, ge=1)
    """Timeout in seconds for each SMTP delivery attempt."""

    SMTP_MAX_ATTEMPTS: int = Field(default=3, ge=1, le=5)
    """Maximum number of SMTP attempts per outbound email."""

    SMTP_RETRY_BACKOFF_SECONDS: float = Field(default=0.5, ge=0)
    """Base exponential backoff delay (seconds) between retry attempts."""

    SMTP_USER: str | None = None
    """SMTP authentication username. Optional depending on server config."""

    SMTP_PASSWORD: str | None = None
    """SMTP authentication password. Optional depending on server config."""

    EMAILS_FROM_EMAIL: EmailStr | None = None
    """'From' email address for outgoing emails. Required for email functionality."""

    EMAILS_FROM_NAME: str | None = None
    """'From' display name for outgoing emails. Defaults to PROJECT_NAME if not set."""

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        """Set EMAILS_FROM_NAME to PROJECT_NAME if not explicitly configured."""
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    """Hours until password reset tokens expire. Default: 48 hours."""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        """
        Check if email functionality is configured.

        Email requires both SMTP_HOST and EMAILS_FROM_EMAIL to be set.

        Returns:
            True if email is configured and can be used, False otherwise.
        """
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    # === Initial Superuser Configuration ===
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    """Email used for test user in development. Default: test@example.com."""

    FIRST_SUPERUSER: EmailStr
    """Email address for the initial superuser account. Required, no default."""

    FIRST_SUPERUSER_PASSWORD: str
    """Password for the initial superuser. MUST not be 'changethis' in production."""

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        """
        Validate that sensitive settings are not using default placeholder values.

        In non-local environments, raises ValueError if a secret is set to
        "changethis". In local environment, this check is skipped to allow
        easy development setup.

        Args:
            var_name: Name of the environment variable being checked.
            value: Current value of the setting.

        Raises:
            ValueError: If value is "changethis" in non-local environments.
        """
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                # Suppress warnings in local development to reduce log noise
                pass
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_runtime_security_defaults(self) -> Self:
        """
        Fail closed for non-local runtime security settings.

        Non-local environments must always provide an explicit SECRET_KEY
        and cannot enable local-only private development routes.
        """
        if self.ENVIRONMENT != "local" and (
            "SECRET_KEY" not in self.model_fields_set or not self.SECRET_KEY.strip()
        ):
            raise ValueError(
                "SECRET_KEY must be explicitly set when ENVIRONMENT is staging "
                "or production."
            )

        if self.ENVIRONMENT != "local" and self.ENABLE_PRIVATE_DEV_ROUTES:
            raise ValueError(
                "ENABLE_PRIVATE_DEV_ROUTES can only be enabled when "
                'ENVIRONMENT="local".'
            )

        if self.ENVIRONMENT != "local" and self.ENABLE_PUBLIC_SIGNUP:
            raise ValueError(
                'ENABLE_PUBLIC_SIGNUP can only be enabled when ENVIRONMENT="local".'
            )

        return self

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        """
        Validate that all sensitive secrets have been properly configured.

        Checks SECRET_KEY, POSTGRES_PASSWORD, and FIRST_SUPERUSER_PASSWORD
        to ensure they are not using the placeholder value "changethis".
        This validation runs after all other validators.

        Returns:
            Self: The validated settings instance.

        Raises:
            ValueError: If any secret is using a default value in non-local env.
        """
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        return self


settings = Settings(**{})
"""
Global settings instance.

This singleton is created at module import time and provides access
to all application configuration. Import this in application code:

>>> from app.core.config import settings
>>> print(settings.PROJECT_NAME)
"""
