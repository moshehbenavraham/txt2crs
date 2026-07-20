import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.rate_limit import is_rate_limiting_enabled


def _base_settings_payload() -> dict[str, object]:
    return {
        "PROJECT_NAME": "Test Project",
        "ENVIRONMENT": "local",
        "SECRET_KEY": "local-dev-secret-key",
        "POSTGRES_SERVER": "localhost",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "test-password",
        "POSTGRES_DB": "app",
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "test-superuser-password",
        "ENABLE_PRIVATE_DEV_ROUTES": False,
    }


def test_settings_require_explicit_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    payload = _base_settings_payload()
    payload.pop("ENVIRONMENT")

    with pytest.raises(ValidationError):
        Settings(_env_file=None, **payload)


def test_non_local_settings_require_explicit_secret_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SECRET_KEY", raising=False)
    payload = _base_settings_payload()
    payload["ENVIRONMENT"] = "staging"
    payload.pop("SECRET_KEY")

    with pytest.raises(ValidationError, match="SECRET_KEY must be explicitly set"):
        Settings(_env_file=None, **payload)


def test_non_local_settings_reject_blank_secret_key() -> None:
    payload = _base_settings_payload()
    payload["ENVIRONMENT"] = "staging"
    payload["SECRET_KEY"] = "   "

    with pytest.raises(ValidationError, match="SECRET_KEY must be explicitly set"):
        Settings(_env_file=None, **payload)


def test_local_environment_can_auto_generate_secret_key() -> None:
    payload = _base_settings_payload()
    payload.pop("SECRET_KEY")

    settings = Settings(_env_file=None, **payload)

    assert settings.ENVIRONMENT == "local"
    assert settings.SECRET_KEY


def test_host_development_defaults_use_registered_ports() -> None:
    """Direct backend defaults must match the workstation port allocation."""

    settings = Settings(_env_file=None, **_base_settings_payload())

    assert settings.FRONTEND_HOST == "http://localhost:5196"
    assert settings.POSTGRES_PORT == 5450


def test_private_dev_routes_flag_is_rejected_outside_local() -> None:
    payload = _base_settings_payload()
    payload["ENVIRONMENT"] = "production"
    payload["ENABLE_PRIVATE_DEV_ROUTES"] = True

    with pytest.raises(ValidationError, match="ENABLE_PRIVATE_DEV_ROUTES"):
        Settings(_env_file=None, **payload)


@pytest.mark.parametrize(
    ("environment", "enable_private_dev_routes", "expected"),
    [
        ("local", False, False),
        ("local", True, True),
        ("staging", False, False),
        ("production", False, False),
    ],
)
def test_private_dev_routes_enabled_only_with_local_explicit_flag(
    environment: str, enable_private_dev_routes: bool, expected: bool
) -> None:
    payload = _base_settings_payload()
    payload["ENVIRONMENT"] = environment
    payload["ENABLE_PRIVATE_DEV_ROUTES"] = enable_private_dev_routes

    settings = Settings(_env_file=None, **payload)

    assert settings.private_dev_routes_enabled is expected


@pytest.mark.parametrize(
    ("environment", "expected"),
    [
        ("local", False),
        ("staging", True),
        ("production", True),
    ],
)
def test_rate_limiter_enabled_for_non_local_environments(
    environment: str, expected: bool
) -> None:
    assert is_rate_limiting_enabled(environment) is expected


def test_db_pool_defaults_local_environment() -> None:
    settings = Settings(_env_file=None, **_base_settings_payload())

    assert settings.DB_POOL_PRE_PING is True
    assert settings.effective_db_pool_size == 5
    assert settings.effective_db_pool_max_overflow == 10
    assert settings.effective_db_pool_timeout_seconds == 30
    assert settings.effective_db_pool_recycle_seconds == 1800


def test_db_pool_defaults_non_local_environment() -> None:
    payload = _base_settings_payload()
    payload["ENVIRONMENT"] = "production"
    settings = Settings(_env_file=None, **payload)

    assert settings.effective_db_pool_size == 10
    assert settings.effective_db_pool_max_overflow == 20
    assert settings.effective_db_pool_timeout_seconds == 30
    assert settings.effective_db_pool_recycle_seconds == 1800


def test_db_pool_overrides_are_respected() -> None:
    payload = _base_settings_payload()
    payload.update(
        {
            "DB_POOL_PRE_PING": False,
            "DB_POOL_SIZE": 12,
            "DB_POOL_MAX_OVERFLOW": 24,
            "DB_POOL_TIMEOUT_SECONDS": 45,
            "DB_POOL_RECYCLE_SECONDS": 900,
        }
    )
    settings = Settings(_env_file=None, **payload)

    assert settings.DB_POOL_PRE_PING is False
    assert settings.effective_db_pool_size == 12
    assert settings.effective_db_pool_max_overflow == 24
    assert settings.effective_db_pool_timeout_seconds == 45
    assert settings.effective_db_pool_recycle_seconds == 900


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("DB_POOL_SIZE", 0),
        ("DB_POOL_MAX_OVERFLOW", -1),
        ("DB_POOL_TIMEOUT_SECONDS", 0),
        ("DB_POOL_RECYCLE_SECONDS", 0),
    ],
)
def test_db_pool_overrides_reject_invalid_values(field_name: str, value: int) -> None:
    payload = _base_settings_payload()
    payload[field_name] = value

    with pytest.raises(ValidationError):
        Settings(_env_file=None, **payload)
