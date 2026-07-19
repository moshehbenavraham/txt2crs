# SPDX-License-Identifier: MIT-0

"""Tests-first public configuration and application-factory contracts."""

from pathlib import Path
from typing import Any

import pytest
from pydantic import SecretStr, ValidationError

from tests.factories import (
    deterministic_generation_request,
    deterministic_generation_scenario,
    standard_admission_reservation,
    valid_execution_profile,
    valid_generation_request,
)
from txt2crs.ai.job_runtime import JobRuntimeResources, JobRuntimeResourcesFactory
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationFactory,
    ApplicationStorageConfig,
    DeterministicApplicationConfig,
    DeterministicApplicationFactory,
    DeterministicGenerationScenario,
    DeterministicTurn,
    RealApplicationConfig,
    RealApplicationFactory,
    Txt2CrsApplication,
)


def _storage(tmp_path: Path) -> ApplicationStorageConfig:
    """Return an absolute private-state configuration."""

    return ApplicationStorageConfig(
        state_directory=(tmp_path / "state").resolve(),
        maximum_artifact_job_bytes=20_000_000,
        artifact_retention_days=30,
    )


def _admission() -> ApplicationAdmissionConfig:
    """Return finite admission settings for both factories."""

    return ApplicationAdmissionConfig(
        window_seconds=3_600,
        maximum_jobs_per_user=10,
        maximum_jobs_global=100,
        maximum_reserved_tokens_per_user=10_000_000,
        maximum_reserved_tokens_global=100_000_000,
        maximum_research_cost_microusd_per_user=1_000_000,
        maximum_research_cost_microusd_global=10_000_000,
    )


def _scenario() -> DeterministicGenerationScenario:
    """Return a minimal strict scenario for factory-shape checks."""

    return DeterministicGenerationScenario.create(
        model_id="gpt-5.6",
        turns=(
            DeterministicTurn.create(
                stage="plan_research",
                output={"schema_version": "1.0"},
            ),
        ),
        evidence_set={
            "schema_version": "1.0",
            "evidence_version": (
                "sha256:0000000000000000000000000000000000000000000000000000000000000000"
            ),
            "sources": [],
            "excerpts": [],
            "selection_scores": [],
        },
    )


def test_application_config_is_strict_immutable_and_hides_secret(
    tmp_path: Path,
) -> None:
    """Shell translation cannot add unknown fields or serialize provider keys."""

    config = RealApplicationConfig(
        storage=_storage(tmp_path),
        admission=_admission(),
        default_execution_profile=valid_execution_profile(),
        codex_home=(tmp_path / "codex-home").resolve(),
        tavily_api_key=SecretStr("private-tavily-key"),
    )

    with pytest.raises(ValidationError):
        RealApplicationConfig.model_validate(
            {
                **config.model_dump(mode="python"),
                "unreviewed_setting": True,
            }
        )
    with pytest.raises(ValidationError):
        config.codex_home = tmp_path / "other"
    assert "private-tavily-key" not in config.model_dump_json()


def test_deterministic_json_contracts_reject_invalid_direct_construction() -> None:
    """Callers cannot bypass scenario validation by skipping create helpers."""

    with pytest.raises(ValidationError):
        DeterministicTurn(
            stage="plan_research",
            output_json="[]",
        )
    with pytest.raises(ValidationError):
        DeterministicGenerationScenario(
            model_id="gpt-5.6",
            turns=(
                DeterministicTurn.create(
                    stage="plan_research",
                    output={"schema_version": "1.0"},
                ),
            ),
            evidence_set_json="{}",
        )


@pytest.mark.parametrize(
    ("storage_directory", "codex_directory"),
    [
        (Path("relative-state"), Path("/tmp/codex-home")),
        (Path("/tmp/state"), Path("relative-codex")),
        (Path("/tmp/shared"), Path("/tmp/shared")),
    ],
)
def test_real_config_rejects_ambiguous_private_paths(
    storage_directory: Path,
    codex_directory: Path,
) -> None:
    """Real composition requires separate absolute state and credential roots."""

    with pytest.raises(ValidationError):
        RealApplicationConfig(
            storage=ApplicationStorageConfig(
                state_directory=storage_directory,
                maximum_artifact_job_bytes=1_000,
                artifact_retention_days=1,
            ),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=codex_directory,
            tavily_api_key=SecretStr("test-only"),
        )


def test_real_config_accepts_distinct_paths_in_one_private_state_root(
    tmp_path: Path,
) -> None:
    """Shell paths may share one backup root without overlapping each other."""

    state_directory = (tmp_path / "state").resolve()
    config = RealApplicationConfig(
        storage=ApplicationStorageConfig(
            state_directory=state_directory,
            job_database_path=state_directory / "jobs.sqlite3",
            artifact_directory=state_directory / "artifacts",
            maximum_artifact_job_bytes=1_000,
            artifact_retention_days=1,
        ),
        admission=_admission(),
        default_execution_profile=valid_execution_profile(),
        codex_home=state_directory / "codex-home",
        worker_directory=(tmp_path / "worker").resolve(),
        tavily_api_key=SecretStr("test-only"),
    )

    assert config.storage.job_database_path == state_directory / "jobs.sqlite3"
    assert config.storage.artifact_directory == state_directory / "artifacts"
    assert config.codex_home == state_directory / "codex-home"
    assert config.worker_directory == (tmp_path / "worker").resolve()


@pytest.mark.parametrize(
    "codex_relative_path",
    [".", "artifacts", "artifacts/codex-home", "jobs.sqlite3"],
)
def test_real_config_rejects_overlapping_same_root_paths(
    tmp_path: Path,
    codex_relative_path: str,
) -> None:
    state_directory = (tmp_path / "state").resolve()

    with pytest.raises(ValidationError):
        RealApplicationConfig(
            storage=ApplicationStorageConfig(
                state_directory=state_directory,
                job_database_path=state_directory / "jobs.sqlite3",
                artifact_directory=state_directory / "artifacts",
                maximum_artifact_job_bytes=1_000,
                artifact_retention_days=1,
            ),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=state_directory / codex_relative_path,
            tavily_api_key=SecretStr("test-only"),
        )


def test_storage_config_rejects_symlinked_or_escaping_explicit_paths(
    tmp_path: Path,
) -> None:
    """Every explicit durable child stays under the canonical private root."""

    state_directory = (tmp_path / "state").resolve()
    real_parent = tmp_path / "real-parent"
    real_parent.mkdir()
    linked_parent = tmp_path / "linked-parent"
    linked_parent.symlink_to(real_parent, target_is_directory=True)
    with pytest.raises(ValidationError):
        ApplicationStorageConfig(
            state_directory=linked_parent / "state",
            maximum_artifact_job_bytes=1_000,
            artifact_retention_days=1,
        )

    with pytest.raises(ValidationError):
        ApplicationStorageConfig(
            state_directory=state_directory,
            job_database_path=tmp_path / "outside.sqlite3",
            artifact_directory=state_directory / "artifacts",
            maximum_artifact_job_bytes=1_000,
            artifact_retention_days=1,
        )

    state_directory.mkdir()
    real_artifacts = state_directory / "real-artifacts"
    real_artifacts.mkdir()
    linked_artifacts = state_directory / "artifacts"
    linked_artifacts.symlink_to(real_artifacts, target_is_directory=True)
    with pytest.raises(ValidationError):
        ApplicationStorageConfig(
            state_directory=state_directory,
            job_database_path=state_directory / "jobs.sqlite3",
            artifact_directory=linked_artifacts,
            maximum_artifact_job_bytes=1_000,
            artifact_retention_days=1,
        )


@pytest.mark.parametrize(
    "worker_relative_path",
    ["relative-worker", "state/worker", "state/codex-home/worker"],
)
def test_real_config_rejects_unsafe_worker_directory(
    tmp_path: Path,
    worker_relative_path: str,
) -> None:
    state_directory = (tmp_path / "state").resolve()
    worker_directory = (
        Path(worker_relative_path)
        if worker_relative_path == "relative-worker"
        else tmp_path / worker_relative_path
    )

    with pytest.raises(ValidationError):
        RealApplicationConfig(
            storage=ApplicationStorageConfig(
                state_directory=state_directory,
                maximum_artifact_job_bytes=1_000,
                artifact_retention_days=1,
            ),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=state_directory / "codex-home",
            worker_directory=worker_directory,
            tavily_api_key=SecretStr("test-only"),
        )


def test_real_factory_uses_explicit_database_and_artifact_paths(
    tmp_path: Path,
) -> None:
    """Package composition honors shell paths instead of deriving duplicates."""

    state_directory = (tmp_path / "state").resolve()
    job_database_path = state_directory / "database" / "jobs.sqlite3"
    artifact_directory = state_directory / "published-artifacts"
    application = RealApplicationFactory(
        RealApplicationConfig(
            storage=ApplicationStorageConfig(
                state_directory=state_directory,
                job_database_path=job_database_path,
                artifact_directory=artifact_directory,
                maximum_artifact_job_bytes=1_000,
                artifact_retention_days=1,
            ),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=state_directory / "codex-home",
            worker_directory=(tmp_path / "worker").resolve(),
            tavily_api_key=SecretStr("test-only"),
        )
    ).create()

    try:
        assert job_database_path.is_file()
        assert artifact_directory.is_dir()
        assert not (state_directory / "jobs.sqlite3").exists()
        assert not (state_directory / "artifacts").exists()
    finally:
        application.close()


@pytest.mark.parametrize("unsafe_host", ["0.0.0.0", "localhost", "192.0.2.10"])
def test_real_config_rejects_non_numeric_or_non_loopback_mcp_hosts(
    tmp_path: Path,
    unsafe_host: str,
) -> None:
    """Unsafe listener configuration fails before any application is built."""

    with pytest.raises(ValidationError):
        RealApplicationConfig(
            storage=_storage(tmp_path),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=(tmp_path / "codex-home").resolve(),
            tavily_api_key=SecretStr("test-only"),
            managed_mcp_host=unsafe_host,
        )


def test_real_and_deterministic_factories_share_public_protocol(
    tmp_path: Path,
) -> None:
    """The shell can select a factory without reconstructing either graph."""

    real_factory = RealApplicationFactory(
        RealApplicationConfig(
            storage=_storage(tmp_path),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=(tmp_path / "codex-home").resolve(),
            tavily_api_key=SecretStr("test-only"),
        )
    )
    deterministic_factory = DeterministicApplicationFactory(
        DeterministicApplicationConfig(
            storage=_storage(tmp_path / "deterministic"),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            scenario=_scenario(),
        )
    )

    assert isinstance(real_factory, ApplicationFactory)
    assert isinstance(deterministic_factory, ApplicationFactory)
    assert isinstance(deterministic_factory.create(), Txt2CrsApplication)


def test_factory_create_does_not_start_job_scoped_provider_resources(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Application startup may open storage/auth state but not Tavily/MCP/Codex."""

    provider_events: list[str] = []

    def reject_provider_start(*_args: Any, **_kwargs: Any) -> None:
        provider_events.append("provider-start")
        raise AssertionError("provider resource started during application creation")

    monkeypatch.setattr(
        "txt2crs.application.factories.ManagedResearchMcpServer.start",
        reject_provider_start,
    )
    monkeypatch.setattr(
        "txt2crs.application.factories.OfficialCodexSdkAdapter.create",
        reject_provider_start,
    )
    factory = RealApplicationFactory(
        RealApplicationConfig(
            storage=_storage(tmp_path),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=(tmp_path / "codex-home").resolve(),
            tavily_api_key=SecretStr("test-only"),
        )
    )

    application = factory.create()

    assert provider_events == []
    generation_request = valid_generation_request()
    submitted = application.submit(
        user_id="owner-123",
        idempotency_key="lazy-provider-123",
        generation_request=generation_request,
        admission_reservation=standard_admission_reservation(),
    )
    application.get_public_job(
        job_id=submitted.job_id,
        user_id="owner-123",
    )
    application.create_executor(
        job_id=submitted.job_id,
        user_id="owner-123",
    )
    application.purge_owner(user_id="owner-123")
    assert provider_events == []
    application.close()


def test_deterministic_factory_builds_fresh_job_scoped_graphs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No budget, cancellation, runtime turn queue, or provider fake is shared."""

    created_resources: list[JobRuntimeResources] = []
    original_resources_factory = JobRuntimeResourcesFactory

    class RecordingResourcesFactory:
        """Observe public composition while delegating resource construction."""

        def create(self, execution_profile: Any) -> JobRuntimeResources:
            resources = original_resources_factory().create(execution_profile)
            created_resources.append(resources)
            return resources

    monkeypatch.setattr(
        "txt2crs.application.factories.JobRuntimeResourcesFactory",
        RecordingResourcesFactory,
    )
    generation_request = deterministic_generation_request()
    application = DeterministicApplicationFactory(
        DeterministicApplicationConfig(
            storage=_storage(tmp_path),
            admission=_admission(),
            default_execution_profile=generation_request.execution_profile,
            scenario=deterministic_generation_scenario(),
        )
    ).create()
    first_job = application.submit(
        user_id="owner-123",
        idempotency_key="fresh-graph-1",
        generation_request=generation_request,
        admission_reservation=standard_admission_reservation(),
    )
    second_job = application.submit(
        user_id="owner-123",
        idempotency_key="fresh-graph-2",
        generation_request=generation_request,
        admission_reservation=standard_admission_reservation(),
    )

    first_executor = application.create_executor(
        job_id=first_job.job_id,
        user_id="owner-123",
    )
    second_executor = application.create_executor(
        job_id=second_job.job_id,
        user_id="owner-123",
    )

    assert first_executor is not second_executor
    assert len(created_resources) == 2
    assert created_resources[0].budget is not created_resources[1].budget
    assert first_executor.cancellation is not second_executor.cancellation
    first_executor.close()
    assert first_executor.cancellation.is_cancelled is True
    assert second_executor.cancellation.is_cancelled is False
    application.close()


def test_persistent_store_closes_when_artifact_store_construction_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A partially built deterministic graph must not leak its SQLite handle."""

    close_events: list[str] = []

    class RecordingStore:
        """Minimal constructor/cleanup double for the failed-build boundary."""

        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def close(self) -> None:
            close_events.append("store-closed")

    def fail_artifact_store(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("synthetic artifact-store failure")

    monkeypatch.setattr(
        "txt2crs.application.factories.SqliteJobStore",
        RecordingStore,
    )
    monkeypatch.setattr(
        "txt2crs.application.factories.FilesystemPrivateArtifactStore",
        fail_artifact_store,
    )
    factory = DeterministicApplicationFactory(
        DeterministicApplicationConfig(
            storage=_storage(tmp_path),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            scenario=_scenario(),
        )
    )

    with pytest.raises(RuntimeError, match="synthetic artifact-store failure"):
        factory.create()

    assert close_events == ["store-closed"]


def test_real_factory_closes_partial_resources_when_authentication_build_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Later failures close acquired resources and keep Codex cwd ephemeral.

    Authentication is part of the real Codex graph, so its working directory
    must use the configured worker root rather than durable engine state.
    """

    close_events: list[str] = []
    authentication_worker_directories: list[Path] = []

    class RecordingStore:
        """Minimal store double whose cleanup is observable."""

        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def close(self) -> None:
            close_events.append("store-closed")

    class RecordingHttpClient:
        """HTTP client double sufficient for lazy ingestion construction."""

        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def close(self) -> None:
            close_events.append("http-closed")

    def fail_authentication(*_args: Any, **kwargs: Any) -> None:
        authentication_worker_directories.append(kwargs["worker_directory"])
        raise RuntimeError("synthetic authentication failure")

    monkeypatch.setattr(
        "txt2crs.application.factories.SqliteJobStore",
        RecordingStore,
    )
    monkeypatch.setattr(
        "txt2crs.application.factories.httpx.Client",
        RecordingHttpClient,
    )
    monkeypatch.setattr(
        "txt2crs.application.factories.DedicatedSystemAuthenticator.create",
        fail_authentication,
    )
    worker_directory = (tmp_path / "worker").resolve()
    factory = RealApplicationFactory(
        RealApplicationConfig(
            storage=_storage(tmp_path),
            admission=_admission(),
            default_execution_profile=valid_execution_profile(),
            codex_home=(tmp_path / "codex-home").resolve(),
            worker_directory=worker_directory,
            tavily_api_key=SecretStr("test-only"),
        )
    )

    with pytest.raises(RuntimeError, match="synthetic authentication failure"):
        factory.create()

    assert close_events == ["http-closed", "store-closed"]
    assert authentication_worker_directories == [worker_directory / "authentication"]
