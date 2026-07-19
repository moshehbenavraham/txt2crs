"""Tests-first contract for the FastAPI-owned txt2crs composition root."""

import ast
from pathlib import Path
from typing import cast

import pytest
from txt2crs.application import (
    ApplicationFactory,
    RealApplicationConfig,
    Txt2CrsApplication,
)

from app.core.config import Settings
from app.services.txt2crs_application import (
    ApplicationFactoryBuilder,
    Txt2CrsApplicationLifecycle,
    build_execution_profile,
    build_real_application_config,
)


def _settings_payload(tmp_path: Path) -> dict[str, object]:
    """Return isolated required shell settings for composition tests."""

    state_root = tmp_path / "state"
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
        "TXT2CRS_STATE_ROOT": state_root,
        "TXT2CRS_JOB_DB_PATH": state_root / "jobs.sqlite3",
        "TXT2CRS_ARTIFACT_ROOT": state_root / "artifacts",
        "TXT2CRS_CODEX_HOME": state_root / "codex-home",
        "TXT2CRS_WORKER_ROOT": tmp_path / "worker",
        "TAVILY_API_KEY": "private-tavily-key",
    }


def _configured_settings(tmp_path: Path) -> Settings:
    """Build settings without reading the repository dotenv file."""

    return Settings(_env_file=None, **_settings_payload(tmp_path))


class RecordingApplication:
    """Minimal facade double that records lifecycle cleanup."""

    def __init__(self, *, close_error: Exception | None = None) -> None:
        self.close_calls = 0
        self.close_error = close_error

    def close(self) -> None:
        self.close_calls += 1
        if self.close_error is not None:
            raise self.close_error


class RecordingApplicationFactory:
    """Factory double that records construction and can fail deterministically."""

    def __init__(
        self,
        *,
        application: RecordingApplication,
        create_error: Exception | None = None,
    ) -> None:
        self.application = application
        self.create_error = create_error
        self.create_calls = 0

    def create(self) -> Txt2CrsApplication:
        self.create_calls += 1
        if self.create_error is not None:
            raise self.create_error
        return cast(Txt2CrsApplication, self.application)


class RecordingFactoryBuilder:
    """Callable double that retains only public configuration objects."""

    def __init__(self, factory: RecordingApplicationFactory) -> None:
        self.factory = factory
        self.configs: list[RealApplicationConfig] = []

    def __call__(self, config: RealApplicationConfig) -> ApplicationFactory:
        self.configs.append(config)
        return cast(ApplicationFactory, self.factory)


def test_build_execution_profile_translates_every_finite_p0_limit(
    tmp_path: Path,
) -> None:
    settings = _configured_settings(tmp_path)

    execution_profile = build_execution_profile(settings)

    assert execution_profile.schema_version == "1.0"
    assert execution_profile.engine_version.startswith("txt2crs-")
    assert execution_profile.prompt_version == "course-pipeline-v1"
    assert execution_profile.policy_version == "content-policy-v1"
    assert execution_profile.model_id == settings.TXT2CRS_MODEL_ID
    assert execution_profile.reasoning_effort == "high"
    assert execution_profile.retry_policy.model_dump() == {
        "maximum_attempts": 3,
        "base_seconds": 1.0,
        "maximum_seconds": 15.0,
        "jitter_ratio": 0.2,
    }
    assert execution_profile.input_limits.model_dump() == {
        "maximum_input_bytes": 20_971_520,
        "maximum_metadata_bytes": 262_144,
        "maximum_normalized_characters": 200_000,
        "maximum_pdf_pages": 200,
    }
    assert execution_profile.run_limits.model_dump() == {
        "maximum_turns": 20,
        "maximum_research_calls": 12,
        "maximum_search_calls": 6,
        "maximum_extract_calls": 6,
        "maximum_sources": 12,
        "maximum_extracted_bytes": 2_000_000,
        "maximum_input_tokens": 600_000,
        "maximum_output_tokens": 150_000,
        "maximum_retries": 3,
        "maximum_repairs": 3,
        "maximum_elapsed_seconds": 2_700.0,
    }
    assert execution_profile.preference_defaults.duration_minutes == 120
    assert execution_profile.preference_defaults.assessment_item_count == 15
    assert execution_profile.preference_defaults.passing_percentage == 70
    assert execution_profile.curriculum_shape_limits.minimum_objectives == 5
    assert execution_profile.curriculum_shape_limits.maximum_modules == 6


def test_build_real_application_config_translates_public_boundaries(
    tmp_path: Path,
) -> None:
    settings = _configured_settings(tmp_path)

    application_config = build_real_application_config(settings)

    assert application_config is not None
    assert application_config.storage.state_directory == settings.TXT2CRS_STATE_ROOT
    assert application_config.storage.job_database_path == settings.TXT2CRS_JOB_DB_PATH
    assert (
        application_config.storage.artifact_directory == settings.TXT2CRS_ARTIFACT_ROOT
    )
    assert application_config.storage.maximum_artifact_job_bytes == 104_857_600
    # P0 has no operator-configurable time purge. The package maximum keeps
    # expiration effectively disabled until the coordinated P1 policy exists.
    assert application_config.storage.artifact_retention_days == 36_500
    assert application_config.admission.model_dump() == {
        "window_seconds": 86_400,
        "maximum_jobs_per_user": 2,
        "maximum_jobs_global": 5,
        "maximum_reserved_tokens_per_user": 1_500_000,
        "maximum_reserved_tokens_global": 3_750_000,
        "maximum_research_cost_microusd_per_user": 2_000_000,
        "maximum_research_cost_microusd_global": 5_000_000,
    }
    assert application_config.codex_home == settings.TXT2CRS_CODEX_HOME
    assert application_config.worker_directory == settings.TXT2CRS_WORKER_ROOT
    assert application_config.managed_mcp_host == "127.0.0.1"
    assert application_config.managed_mcp_port == 8765
    assert application_config.managed_mcp_startup_timeout_seconds == 10
    assert application_config.managed_mcp_shutdown_timeout_seconds == 10
    assert application_config.http_timeout_seconds == 20
    assert application_config.tavily_api_key.get_secret_value() == "private-tavily-key"
    assert "private-tavily-key" not in application_config.model_dump_json()


def test_shell_composition_imports_only_public_txt2crs_boundaries() -> None:
    """The shell may use public application/job contracts, never internals."""

    composition_path = (
        Path(__file__).parents[2] / "app" / "services" / "txt2crs_application.py"
    )
    parsed_module = ast.parse(composition_path.read_text(encoding="utf-8"))
    imported_txt2crs_modules = {
        imported_module.module
        for imported_module in ast.walk(parsed_module)
        if isinstance(imported_module, ast.ImportFrom)
        and imported_module.module is not None
        and imported_module.module.startswith("txt2crs")
    }

    assert imported_txt2crs_modules <= {
        "txt2crs",
        "txt2crs.application",
        "txt2crs.jobs",
    }


def test_configured_lifecycle_creates_and_closes_one_facade(
    tmp_path: Path,
) -> None:
    application = RecordingApplication()
    factory = RecordingApplicationFactory(application=application)
    factory_builder = RecordingFactoryBuilder(factory)
    lifecycle = Txt2CrsApplicationLifecycle(
        settings=_configured_settings(tmp_path),
        factory_builder=cast(ApplicationFactoryBuilder, factory_builder),
    )

    lifecycle.start()
    lifecycle.start()

    assert lifecycle.is_configured is True
    assert lifecycle.application is application
    assert len(factory_builder.configs) == 1
    assert factory.create_calls == 1

    lifecycle.close()
    lifecycle.close()

    assert application.close_calls == 1
    assert lifecycle.application is None


def test_unconfigured_lifecycle_does_not_construct_a_factory(
    tmp_path: Path,
) -> None:
    payload = _settings_payload(tmp_path)
    payload["TAVILY_API_KEY"] = None
    application = RecordingApplication()
    factory = RecordingApplicationFactory(application=application)
    factory_builder = RecordingFactoryBuilder(factory)
    lifecycle = Txt2CrsApplicationLifecycle(
        settings=Settings(_env_file=None, **payload),
        factory_builder=cast(ApplicationFactoryBuilder, factory_builder),
    )

    lifecycle.start()
    lifecycle.close()

    assert lifecycle.is_configured is False
    assert lifecycle.application is None
    assert factory_builder.configs == []
    assert factory.create_calls == 0
    assert application.close_calls == 0


def test_factory_failure_resets_lifecycle_for_a_safe_retry(
    tmp_path: Path,
) -> None:
    application = RecordingApplication()
    factory = RecordingApplicationFactory(
        application=application,
        create_error=RuntimeError("private provider construction detail"),
    )
    factory_builder = RecordingFactoryBuilder(factory)
    lifecycle = Txt2CrsApplicationLifecycle(
        settings=_configured_settings(tmp_path),
        factory_builder=cast(ApplicationFactoryBuilder, factory_builder),
    )

    with pytest.raises(RuntimeError, match="private provider construction detail"):
        lifecycle.start()

    assert lifecycle.application is None
    assert lifecycle.is_started is False

    factory.create_error = None
    lifecycle.start()
    lifecycle.close()

    assert factory.create_calls == 2
    assert application.close_calls == 1


def test_close_failure_clears_owned_reference_and_is_not_retried(
    tmp_path: Path,
) -> None:
    application = RecordingApplication(
        close_error=RuntimeError("private close detail"),
    )
    factory = RecordingApplicationFactory(application=application)
    lifecycle = Txt2CrsApplicationLifecycle(
        settings=_configured_settings(tmp_path),
        factory_builder=cast(
            ApplicationFactoryBuilder,
            RecordingFactoryBuilder(factory),
        ),
    )
    lifecycle.start()

    with pytest.raises(RuntimeError, match="private close detail"):
        lifecycle.close()

    lifecycle.close()

    assert application.close_calls == 1
    assert lifecycle.application is None
    assert lifecycle.is_started is False


def test_lifecycle_events_do_not_log_secret_path_or_exception_text(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class RecordingLogger:
        """Capture event names and structured fields without root handlers."""

        def __init__(self) -> None:
            self.events: list[tuple[str, dict[str, object] | None]] = []

        def info(
            self,
            event_name: str,
            *,
            extra: dict[str, object] | None = None,
        ) -> None:
            self.events.append((event_name, extra))

        def error(
            self,
            event_name: str,
            *,
            extra: dict[str, object] | None = None,
        ) -> None:
            self.events.append((event_name, extra))

    recording_logger = RecordingLogger()
    monkeypatch.setattr(
        "app.services.txt2crs_application.logger",
        recording_logger,
    )
    application = RecordingApplication()
    factory = RecordingApplicationFactory(
        application=application,
        create_error=RuntimeError("private provider construction detail"),
    )
    lifecycle = Txt2CrsApplicationLifecycle(
        settings=_configured_settings(tmp_path),
        factory_builder=cast(
            ApplicationFactoryBuilder,
            RecordingFactoryBuilder(factory),
        ),
    )

    with pytest.raises(RuntimeError):
        lifecycle.start()

    rendered_logs = repr(recording_logger.events)
    assert "txt2crs.composition_started" in rendered_logs
    assert "txt2crs.composition_failed" in rendered_logs
    assert "private-tavily-key" not in rendered_logs
    assert str(tmp_path) not in rendered_logs
    assert "private provider construction detail" not in rendered_logs
