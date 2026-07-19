"""Regression tests for the shell-owned txt2crs filesystem boundary."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings

TXT2CRS_PATH_ENVIRONMENT_NAMES = (
    "TXT2CRS_STATE_ROOT",
    "TXT2CRS_JOB_DB_PATH",
    "TXT2CRS_ARTIFACT_ROOT",
    "TXT2CRS_CODEX_HOME",
    "TXT2CRS_WORKER_ROOT",
)

TXT2CRS_COMPOSITION_ENVIRONMENT_NAMES = (
    "TXT2CRS_MODEL_ID",
    "TXT2CRS_RESEARCH_ENABLED",
    "TXT2CRS_RESEARCH_MCP_HOST",
    "TXT2CRS_RESEARCH_MCP_PORT",
    "TXT2CRS_RESEARCH_MCP_STARTUP_TIMEOUT_SECONDS",
    "TXT2CRS_RESEARCH_MCP_SHUTDOWN_TIMEOUT_SECONDS",
    "TXT2CRS_WORKER_POLL_SECONDS",
    "TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS",
    "TXT2CRS_READINESS_REFRESH_SECONDS",
    "TXT2CRS_READINESS_STALE_AFTER_SECONDS",
    "TXT2CRS_READINESS_SHUTDOWN_TIMEOUT_SECONDS",
    "TXT2CRS_AUTH_MONITOR_POLL_SECONDS",
    "TXT2CRS_AUTH_SHUTDOWN_TIMEOUT_SECONDS",
    "TXT2CRS_MAX_INPUT_BYTES",
    "TXT2CRS_MAX_METADATA_BYTES",
    "TXT2CRS_MAX_NORMALIZED_CHARACTERS",
    "TXT2CRS_MAX_PDF_PAGES",
    "TXT2CRS_ARTIFACT_MAX_JOB_BYTES",
    "TXT2CRS_HTML_PREVIEW_MAX_BYTES",
    "TXT2CRS_RETRY_MAXIMUM_ATTEMPTS",
    "TXT2CRS_RETRY_BASE_SECONDS",
    "TXT2CRS_RETRY_MAXIMUM_SECONDS",
    "TXT2CRS_RETRY_JITTER_RATIO",
    "TXT2CRS_RUN_MAXIMUM_TURNS",
    "TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS",
    "TXT2CRS_RUN_MAXIMUM_SEARCH_CALLS",
    "TXT2CRS_RUN_MAXIMUM_EXTRACT_CALLS",
    "TXT2CRS_RUN_MAXIMUM_SOURCES",
    "TXT2CRS_RUN_MAXIMUM_EXTRACTED_BYTES",
    "TXT2CRS_RUN_MAXIMUM_INPUT_TOKENS",
    "TXT2CRS_RUN_MAXIMUM_OUTPUT_TOKENS",
    "TXT2CRS_RUN_MAXIMUM_RETRIES",
    "TXT2CRS_RUN_MAXIMUM_REPAIRS",
    "TXT2CRS_RUN_MAXIMUM_ELAPSED_SECONDS",
    "TXT2CRS_ADMISSION_WINDOW_SECONDS",
    "TXT2CRS_ADMISSION_MAXIMUM_JOBS_PER_USER",
    "TXT2CRS_ADMISSION_MAXIMUM_JOBS_GLOBAL",
    "TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER",
    "TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_GLOBAL",
    "TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_PER_USER",
    "TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_GLOBAL",
    "TAVILY_API_KEY",
    "TAVILY_TIMEOUT_SECONDS",
)


@pytest.fixture(autouse=True)
def _clear_inherited_txt2crs_path_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Keep focused Settings cases independent from the caller's environment.

    Passing `_env_file=None` disables dotenv files, but Pydantic Settings still
    reads exported process variables. Clearing only the five fields under test
    prevents a developer's local or CI path configuration from changing the
    expected defaults and custom-root scenarios.
    """
    for environment_name in (
        *TXT2CRS_PATH_ENVIRONMENT_NAMES,
        *TXT2CRS_COMPOSITION_ENVIRONMENT_NAMES,
    ):
        monkeypatch.delenv(environment_name, raising=False)


def _base_settings_payload() -> dict[str, object]:
    """Return the unrelated required settings needed by every focused test."""
    return {
        "PROJECT_NAME": "txt2crs Test",
        "ENVIRONMENT": "local",
        "SECRET_KEY": "local-dev-secret-key",
        "POSTGRES_SERVER": "localhost",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "test-password",
        "POSTGRES_DB": "app",
        "FIRST_SUPERUSER": "admin@example.com",
        "FIRST_SUPERUSER_PASSWORD": "test-superuser-password",
    }


def test_txt2crs_paths_use_private_container_defaults() -> None:
    settings = Settings(_env_file=None, **_base_settings_payload())

    assert settings.TXT2CRS_STATE_ROOT == Path("/var/lib/txt2crs")
    assert settings.TXT2CRS_JOB_DB_PATH == Path("/var/lib/txt2crs/jobs.sqlite3")
    assert settings.TXT2CRS_ARTIFACT_ROOT == Path("/var/lib/txt2crs/artifacts")
    assert settings.TXT2CRS_CODEX_HOME == Path("/var/lib/txt2crs/codex-home")
    assert settings.TXT2CRS_WORKER_ROOT == Path("/tmp/txt2crs-worker")


def test_txt2crs_composition_uses_conservative_p0_defaults() -> None:
    """Finite settings match the reviewed implementation-plan profile."""

    settings = Settings(_env_file=None, **_base_settings_payload())

    assert settings.TXT2CRS_MODEL_ID == "gpt-5.6"
    assert settings.TXT2CRS_RESEARCH_ENABLED is True
    assert settings.TXT2CRS_RESEARCH_MCP_HOST == "127.0.0.1"
    assert settings.TXT2CRS_RESEARCH_MCP_PORT == 8765
    assert settings.TXT2CRS_RESEARCH_MCP_STARTUP_TIMEOUT_SECONDS == 10
    assert settings.TXT2CRS_RESEARCH_MCP_SHUTDOWN_TIMEOUT_SECONDS == 10
    assert settings.TXT2CRS_WORKER_POLL_SECONDS == 2
    assert settings.TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS == 30
    assert settings.TXT2CRS_READINESS_REFRESH_SECONDS == 60
    assert settings.TXT2CRS_READINESS_STALE_AFTER_SECONDS == 120
    assert settings.TXT2CRS_READINESS_SHUTDOWN_TIMEOUT_SECONDS == 30
    assert settings.TXT2CRS_AUTH_MONITOR_POLL_SECONDS == 0.5
    assert settings.TXT2CRS_AUTH_SHUTDOWN_TIMEOUT_SECONDS == 10
    assert settings.TXT2CRS_MAX_INPUT_BYTES == 20_971_520
    assert settings.TXT2CRS_MAX_METADATA_BYTES == 262_144
    assert settings.TXT2CRS_MAX_NORMALIZED_CHARACTERS == 200_000
    assert settings.TXT2CRS_MAX_PDF_PAGES == 200
    assert settings.TXT2CRS_ARTIFACT_MAX_JOB_BYTES == 104_857_600
    assert settings.TXT2CRS_HTML_PREVIEW_MAX_BYTES == 5_242_880
    assert settings.TXT2CRS_RETRY_MAXIMUM_ATTEMPTS == 3
    assert settings.TXT2CRS_RETRY_BASE_SECONDS == 1
    assert settings.TXT2CRS_RETRY_MAXIMUM_SECONDS == 15
    assert settings.TXT2CRS_RETRY_JITTER_RATIO == 0.2
    assert settings.TXT2CRS_RUN_MAXIMUM_TURNS == 20
    assert settings.TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS == 12
    assert settings.TXT2CRS_RUN_MAXIMUM_SEARCH_CALLS == 6
    assert settings.TXT2CRS_RUN_MAXIMUM_EXTRACT_CALLS == 6
    assert settings.TXT2CRS_RUN_MAXIMUM_SOURCES == 12
    assert settings.TXT2CRS_RUN_MAXIMUM_EXTRACTED_BYTES == 2_000_000
    assert settings.TXT2CRS_RUN_MAXIMUM_INPUT_TOKENS == 600_000
    assert settings.TXT2CRS_RUN_MAXIMUM_OUTPUT_TOKENS == 150_000
    assert settings.TXT2CRS_RUN_MAXIMUM_RETRIES == 3
    assert settings.TXT2CRS_RUN_MAXIMUM_REPAIRS == 3
    assert settings.TXT2CRS_RUN_MAXIMUM_ELAPSED_SECONDS == 2_700
    assert settings.TXT2CRS_ADMISSION_WINDOW_SECONDS == 86_400
    assert settings.TXT2CRS_ADMISSION_MAXIMUM_JOBS_PER_USER == 2
    assert settings.TXT2CRS_ADMISSION_MAXIMUM_JOBS_GLOBAL == 5
    assert settings.TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER == 1_500_000
    assert settings.TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_GLOBAL == 3_750_000
    assert settings.TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_PER_USER == 2_000_000
    assert settings.TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_GLOBAL == 5_000_000
    assert settings.TAVILY_TIMEOUT_SECONDS == 20
    assert settings.TAVILY_API_KEY is None


@pytest.mark.parametrize(
    "model_id",
    ["gpt-5.6", "gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna"],
)
def test_txt2crs_model_accepts_only_reviewed_gpt56_family(model_id: str) -> None:
    settings = Settings(
        _env_file=None,
        **_base_settings_payload(),
        TXT2CRS_MODEL_ID=model_id,
    )

    assert settings.TXT2CRS_MODEL_ID == model_id


def test_txt2crs_model_rejects_non_gpt56_identifier() -> None:
    with pytest.raises(ValidationError, match="TXT2CRS_MODEL_ID"):
        Settings(
            _env_file=None,
            **_base_settings_payload(),
            TXT2CRS_MODEL_ID="gpt-5.4",
        )


@pytest.mark.parametrize(
    ("field_name", "unsafe_value"),
    [
        ("TXT2CRS_RESEARCH_MCP_PORT", 65_536),
        ("TXT2CRS_RESEARCH_MCP_STARTUP_TIMEOUT_SECONDS", 0),
        ("TXT2CRS_WORKER_POLL_SECONDS", 0),
        ("TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS", 301),
        ("TXT2CRS_READINESS_REFRESH_SECONDS", 3_601),
        ("TXT2CRS_READINESS_STALE_AFTER_SECONDS", 7_201),
        ("TXT2CRS_READINESS_SHUTDOWN_TIMEOUT_SECONDS", 0),
        ("TXT2CRS_AUTH_MONITOR_POLL_SECONDS", 11),
        ("TXT2CRS_AUTH_SHUTDOWN_TIMEOUT_SECONDS", 0),
        ("TXT2CRS_MAX_INPUT_BYTES", 0),
        ("TXT2CRS_MAX_PDF_PAGES", 0),
        ("TXT2CRS_ARTIFACT_MAX_JOB_BYTES", 1_000_000_001),
        ("TXT2CRS_RETRY_MAXIMUM_ATTEMPTS", 1),
        ("TXT2CRS_RETRY_JITTER_RATIO", 1.1),
        ("TXT2CRS_RUN_MAXIMUM_TURNS", 0),
        ("TXT2CRS_RUN_MAXIMUM_ELAPSED_SECONDS", 0),
        ("TXT2CRS_ADMISSION_WINDOW_SECONDS", 0),
        ("TAVILY_TIMEOUT_SECONDS", 61),
    ],
)
def test_txt2crs_composition_rejects_unsafe_finite_bounds(
    field_name: str,
    unsafe_value: int | float,
) -> None:
    with pytest.raises(ValidationError, match=field_name):
        Settings(
            _env_file=None,
            **_base_settings_payload(),
            **{field_name: unsafe_value},
        )


@pytest.mark.parametrize(
    "unsafe_host",
    ["0.0.0.0", "localhost", "192.0.2.10"],
)
def test_txt2crs_research_mcp_requires_numeric_loopback(
    unsafe_host: str,
) -> None:
    with pytest.raises(ValidationError, match="TXT2CRS_RESEARCH_MCP_HOST"):
        Settings(
            _env_file=None,
            **_base_settings_payload(),
            TXT2CRS_RESEARCH_MCP_HOST=unsafe_host,
        )


def test_txt2crs_cross_field_budgets_reject_impossible_profiles() -> None:
    with pytest.raises(ValidationError, match="stale"):
        Settings(
            _env_file=None,
            **_base_settings_payload(),
            TXT2CRS_READINESS_REFRESH_SECONDS=120,
            TXT2CRS_READINESS_STALE_AFTER_SECONDS=60,
        )

    with pytest.raises(ValidationError, match="search and extract"):
        Settings(
            _env_file=None,
            **_base_settings_payload(),
            TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS=4,
            TXT2CRS_RUN_MAXIMUM_SEARCH_CALLS=3,
            TXT2CRS_RUN_MAXIMUM_EXTRACT_CALLS=2,
        )

    with pytest.raises(ValidationError, match="reserved tokens"):
        Settings(
            _env_file=None,
            **_base_settings_payload(),
            TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER=4_000_000,
            TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_GLOBAL=3_750_000,
        )


def test_tavily_secret_is_optional_trimmed_and_hidden() -> None:
    whitespace_settings = Settings(
        _env_file=None,
        **_base_settings_payload(),
        TAVILY_API_KEY="   ",
    )
    configured_settings = Settings(
        _env_file=None,
        **_base_settings_payload(),
        TAVILY_API_KEY="private-tavily-key",
    )

    assert whitespace_settings.TAVILY_API_KEY is None
    assert configured_settings.TAVILY_API_KEY is not None
    assert configured_settings.TAVILY_API_KEY.get_secret_value() == "private-tavily-key"
    assert "private-tavily-key" not in repr(configured_settings)


def test_custom_state_root_derives_omitted_persistent_children(
    tmp_path: Path,
) -> None:
    configured_state_root = tmp_path / "private-state"
    payload = {
        **_base_settings_payload(),
        "TXT2CRS_STATE_ROOT": configured_state_root,
    }

    settings = Settings(_env_file=None, **payload)

    assert settings.TXT2CRS_STATE_ROOT == configured_state_root.resolve()
    assert settings.TXT2CRS_JOB_DB_PATH == configured_state_root / "jobs.sqlite3"
    assert settings.TXT2CRS_ARTIFACT_ROOT == configured_state_root / "artifacts"
    assert settings.TXT2CRS_CODEX_HOME == configured_state_root / "codex-home"


def test_safe_explicit_txt2crs_paths_are_normalized(tmp_path: Path) -> None:
    configured_state_root = tmp_path / "parent" / ".." / "private-state"
    payload = {
        **_base_settings_payload(),
        "TXT2CRS_STATE_ROOT": configured_state_root,
        "TXT2CRS_JOB_DB_PATH": configured_state_root / "database" / "jobs.sqlite3",
        "TXT2CRS_ARTIFACT_ROOT": configured_state_root / "published-artifacts",
        "TXT2CRS_CODEX_HOME": configured_state_root / "credentials",
        "TXT2CRS_WORKER_ROOT": tmp_path / "worker",
    }

    settings = Settings(_env_file=None, **payload)

    assert settings.TXT2CRS_STATE_ROOT == configured_state_root.resolve()
    assert (
        settings.TXT2CRS_JOB_DB_PATH
        == (configured_state_root / "database" / "jobs.sqlite3").resolve()
    )
    assert (
        settings.TXT2CRS_ARTIFACT_ROOT
        == (configured_state_root / "published-artifacts").resolve()
    )
    assert (
        settings.TXT2CRS_CODEX_HOME == (configured_state_root / "credentials").resolve()
    )
    assert settings.TXT2CRS_WORKER_ROOT == (tmp_path / "worker").resolve()


@pytest.mark.parametrize(
    ("field_name", "relative_value"),
    [
        ("TXT2CRS_STATE_ROOT", "relative-state"),
        ("TXT2CRS_JOB_DB_PATH", "relative-state/jobs.sqlite3"),
        ("TXT2CRS_ARTIFACT_ROOT", "relative-state/artifacts"),
        ("TXT2CRS_CODEX_HOME", "relative-state/codex-home"),
        ("TXT2CRS_WORKER_ROOT", "relative-worker"),
    ],
)
def test_txt2crs_paths_reject_relative_values(
    field_name: str,
    relative_value: str,
) -> None:
    payload = {
        **_base_settings_payload(),
        field_name: relative_value,
    }

    with pytest.raises(ValidationError, match=field_name):
        Settings(_env_file=None, **payload)


@pytest.mark.parametrize(
    "field_name",
    [
        "TXT2CRS_JOB_DB_PATH",
        "TXT2CRS_ARTIFACT_ROOT",
        "TXT2CRS_CODEX_HOME",
    ],
)
def test_persistent_children_cannot_escape_state_root(
    tmp_path: Path,
    field_name: str,
) -> None:
    configured_state_root = tmp_path / "private-state"
    payload = {
        **_base_settings_payload(),
        "TXT2CRS_STATE_ROOT": configured_state_root,
        field_name: tmp_path / "outside-state",
    }

    with pytest.raises(ValidationError, match=field_name):
        Settings(_env_file=None, **payload)


def test_persistent_directory_boundaries_cannot_overlap(tmp_path: Path) -> None:
    configured_state_root = tmp_path / "private-state"
    artifact_root = configured_state_root / "artifacts"
    payload = {
        **_base_settings_payload(),
        "TXT2CRS_STATE_ROOT": configured_state_root,
        "TXT2CRS_ARTIFACT_ROOT": artifact_root,
        "TXT2CRS_CODEX_HOME": artifact_root / "codex-home",
    }

    with pytest.raises(ValidationError, match="must not overlap"):
        Settings(_env_file=None, **payload)


def test_job_database_path_cannot_name_a_directory_boundary(tmp_path: Path) -> None:
    configured_state_root = tmp_path / "private-state"
    payload = {
        **_base_settings_payload(),
        "TXT2CRS_STATE_ROOT": configured_state_root,
        "TXT2CRS_JOB_DB_PATH": configured_state_root / "artifacts",
        "TXT2CRS_ARTIFACT_ROOT": configured_state_root / "artifacts",
    }

    with pytest.raises(ValidationError, match="TXT2CRS_JOB_DB_PATH"):
        Settings(_env_file=None, **payload)


def test_worker_root_must_stay_outside_persistent_state(tmp_path: Path) -> None:
    configured_state_root = tmp_path / "private-state"
    payload = {
        **_base_settings_payload(),
        "TXT2CRS_STATE_ROOT": configured_state_root,
        "TXT2CRS_WORKER_ROOT": configured_state_root / "worker",
    }

    with pytest.raises(ValidationError, match="TXT2CRS_WORKER_ROOT"):
        Settings(_env_file=None, **payload)


@pytest.mark.parametrize(
    "symlink_field",
    ["state", "job_database", "artifact", "codex", "worker"],
)
def test_txt2crs_paths_reject_existing_symlink_endpoints(
    tmp_path: Path,
    symlink_field: str,
) -> None:
    real_state_root = tmp_path / "real-state"
    real_state_root.mkdir()
    real_artifact_root = real_state_root / "real-artifacts"
    real_artifact_root.mkdir()
    real_codex_home = real_state_root / "real-codex-home"
    real_codex_home.mkdir()
    real_job_database = real_state_root / "real-jobs.sqlite3"
    real_job_database.touch()
    real_worker_root = tmp_path / "real-worker"
    real_worker_root.mkdir()

    state_symlink = tmp_path / "state-symlink"
    state_symlink.symlink_to(real_state_root, target_is_directory=True)
    artifact_symlink = real_state_root / "artifact-symlink"
    artifact_symlink.symlink_to(real_artifact_root, target_is_directory=True)
    codex_symlink = real_state_root / "codex-symlink"
    codex_symlink.symlink_to(real_codex_home, target_is_directory=True)
    job_database_symlink = real_state_root / "jobs-symlink.sqlite3"
    job_database_symlink.symlink_to(real_job_database)
    worker_symlink = tmp_path / "worker-symlink"
    worker_symlink.symlink_to(real_worker_root, target_is_directory=True)

    payload: dict[str, object] = {
        **_base_settings_payload(),
        "TXT2CRS_STATE_ROOT": real_state_root,
        "TXT2CRS_JOB_DB_PATH": real_job_database,
        "TXT2CRS_ARTIFACT_ROOT": real_artifact_root,
        "TXT2CRS_CODEX_HOME": real_codex_home,
        "TXT2CRS_WORKER_ROOT": real_worker_root,
    }
    selected_path = {
        "state": ("TXT2CRS_STATE_ROOT", state_symlink),
        "job_database": ("TXT2CRS_JOB_DB_PATH", job_database_symlink),
        "artifact": ("TXT2CRS_ARTIFACT_ROOT", artifact_symlink),
        "codex": ("TXT2CRS_CODEX_HOME", codex_symlink),
        "worker": ("TXT2CRS_WORKER_ROOT", worker_symlink),
    }[symlink_field]
    payload[selected_path[0]] = selected_path[1]

    with pytest.raises(ValidationError, match="symlink"):
        Settings(_env_file=None, **payload)
