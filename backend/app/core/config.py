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
        - POSTGRES_PORT: Database port (default: 5441)
        - POSTGRES_PASSWORD: Database password (default: "")
        - POSTGRES_DB: Database name (default: "")
        - SMTP_*: Email configuration (all optional)
        - SENTRY_DSN: Sentry error tracking URL (optional)
        - BACKEND_CORS_ORIGINS: Comma-separated CORS origins (default: [])
        - FRONTEND_HOST: Frontend URL for CORS (default: http://localhost:5181)

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
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    Field,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    """
    Parse CORS origins from environment variable.

    Handles multiple input formats for flexibility in configuration:
    - Comma-separated string: "http://localhost:3000,http://localhost:5173"
    - JSON array string: '["http://localhost:3000"]'
    - Python list (when set programmatically)

    Args:
        v: Raw value from environment variable or direct assignment.
            Can be a comma-separated string, JSON array string, or list.

    Returns:
        List of origin strings or the original value if already valid.

    Raises:
        ValueError: If the value cannot be parsed as a valid CORS origin list.

    Example:
        >>> parse_cors("http://localhost:3000,http://example.com")
        ['http://localhost:3000', 'http://example.com']
        >>> parse_cors('["http://localhost:3000"]')
        '["http://localhost:3000"]'  # Passed through for Pydantic to parse
    """
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


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

    FRONTEND_HOST: str = "http://localhost:5181"
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

    # === CORS Configuration ===
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []
    """
    Additional CORS allowed origins (comma-separated or JSON array).
    FRONTEND_HOST is always included automatically via all_cors_origins.
    Example: "http://localhost:3000,http://localhost:5173"
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
    Example: "http://localhost:4317" (gRPC) or "http://localhost:4318/v1/traces" (HTTP).
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

    # === Database Configuration ===
    POSTGRES_SERVER: str
    """PostgreSQL server hostname or IP address. Required, no default."""

    POSTGRES_PORT: int = 5441
    """PostgreSQL server port. Default: 5441 (non-standard to avoid conflicts)."""

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
            postgresql+psycopg://user:pass@localhost:5441/mydb
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
