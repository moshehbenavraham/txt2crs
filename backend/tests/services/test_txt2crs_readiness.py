"""Tests-first cached readiness behavior with no browser-side effects."""

from datetime import UTC, datetime, timedelta
from threading import Event

from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import SubscriptionQuotaState
from txt2crs.application import ApplicationReadiness

from app.services.txt2crs_readiness import (
    CachedReadinessCoordinator,
    ReadinessCheckState,
    ReadinessStatus,
)
from app.services.txt2crs_runtime import RuntimeOwner, RuntimeOwnershipCoordinator
from app.services.txt2crs_worker import WorkerSnapshot, WorkerStatus


class RecordingApplication:
    """Return one package projection and count real refresh work."""

    def __init__(self) -> None:
        self.inspect_calls = 0
        self.second_inspection = Event()

    def inspect_application_readiness(self) -> ApplicationReadiness:
        """Count the provider/storage probe boundary."""

        self.inspect_calls += 1
        if self.inspect_calls >= 2:
            self.second_inspection.set()
        return ApplicationReadiness.create(
            configured_model_id="gpt-5.6-sol",
            enabled_input_modes=(
                "prompt",
                "text",
                "url",
                "youtube",
                "pdf",
                "document",
                "slides",
            ),
            runtime=RuntimeReadiness.create(
                status=RuntimeReadinessStatus.ready,
                credential_status=CredentialStatus.valid,
                model_entitled=True,
                subscription_quota_state=SubscriptionQuotaState.unknown,
                warnings=[],
                recovery_actions=[],
            ),
            research_ready=True,
            sqlite_ready=True,
            artifacts_ready=True,
            inputs_ready=True,
            admission_ready=True,
            warnings=[],
            recovery_actions=[],
        )


class RecordingWorker:
    """Expose only safe worker state and count snapshot reads."""

    def __init__(self) -> None:
        self.snapshot_calls = 0

    def snapshot(self) -> WorkerSnapshot:
        """Return one idle healthy worker."""

        self.snapshot_calls += 1
        return WorkerSnapshot(
            schema_version="1.0",
            status=WorkerStatus.idle,
            is_alive=True,
            has_active_job=False,
            has_capacity=True,
            is_shutting_down=False,
            last_failure_code=None,
        )


def test_cache_start_refreshes_once_and_reads_never_probe_application() -> None:
    """Repeated browser reads use only immutable cached and worker state."""

    application = RecordingApplication()
    worker = RecordingWorker()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = CachedReadinessCoordinator(
        application=application,
        worker=worker,
        runtime_ownership=ownership,
        refresh_interval_seconds=60,
        stale_after_seconds=120,
        shutdown_timeout_seconds=1,
    )

    coordinator.start()
    assert application.inspect_calls == 1
    first = coordinator.snapshot()
    second = coordinator.snapshot()

    assert first.status is ReadinessStatus.ready
    assert first.accepting_jobs is True
    assert second == first
    assert application.inspect_calls == 1
    assert worker.snapshot_calls >= 2
    coordinator.close()


def test_maintenance_refresh_runs_on_finite_interval() -> None:
    """One daemon refreshes after waiting; startup is not duplicated."""

    application = RecordingApplication()
    coordinator = CachedReadinessCoordinator(
        application=application,
        worker=RecordingWorker(),
        runtime_ownership=RuntimeOwnershipCoordinator(),
        refresh_interval_seconds=0.01,
        stale_after_seconds=0.02,
        shutdown_timeout_seconds=1,
    )

    coordinator.start()

    assert application.second_inspection.wait(timeout=1)
    assert application.inspect_calls >= 2
    coordinator.close()


def test_active_runtime_owner_blocks_acceptance_without_refresh_work() -> None:
    """A running job keeps the cache readable and prevents a second runtime."""

    application = RecordingApplication()
    worker = RecordingWorker()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = CachedReadinessCoordinator(
        application=application,
        worker=worker,
        runtime_ownership=ownership,
        refresh_interval_seconds=60,
        stale_after_seconds=120,
        shutdown_timeout_seconds=1,
    )
    coordinator.start()

    with ownership.acquire(RuntimeOwner.execution):
        snapshot = coordinator.snapshot()
        assert snapshot.accepting_jobs is False
        assert snapshot.status is ReadinessStatus.degraded
        assert snapshot.checks.runtime_ownership is ReadinessCheckState.unavailable
        assert application.inspect_calls == 1

    coordinator.close()


def test_unconfigured_readiness_is_safe_and_starts_no_thread() -> None:
    """Missing operator setup remains a truthful browser-loadable state."""

    ownership = RuntimeOwnershipCoordinator()
    coordinator = CachedReadinessCoordinator(
        application=None,
        worker=None,
        runtime_ownership=ownership,
        refresh_interval_seconds=60,
        stale_after_seconds=120,
        shutdown_timeout_seconds=1,
    )

    coordinator.start()
    snapshot = coordinator.snapshot()

    assert snapshot.status is ReadinessStatus.unavailable
    assert snapshot.accepting_jobs is False
    assert snapshot.configured_model_id == "gpt-5.6-sol"
    rendered = snapshot.model_dump_json()
    assert "TAVILY_API_KEY" not in rendered
    assert "/var/lib" not in rendered
    coordinator.close()
    coordinator.close()


def test_stale_snapshot_fails_closed_without_synchronous_refresh() -> None:
    """Age changes acceptance but never turns a read into provider work."""

    now = datetime(2026, 7, 19, tzinfo=UTC)
    clock_value = [now]
    application = RecordingApplication()
    coordinator = CachedReadinessCoordinator(
        application=application,
        worker=RecordingWorker(),
        runtime_ownership=RuntimeOwnershipCoordinator(),
        refresh_interval_seconds=60,
        stale_after_seconds=120,
        shutdown_timeout_seconds=1,
        clock=lambda: clock_value[0],
    )
    coordinator.start()
    assert coordinator.snapshot().accepting_jobs is True

    clock_value[0] = now + timedelta(seconds=121)
    stale_snapshot = coordinator.snapshot()

    assert stale_snapshot.accepting_jobs is False
    assert stale_snapshot.is_fresh is False
    assert application.inspect_calls == 1
    coordinator.close()


def test_contended_manual_refresh_keeps_last_snapshot() -> None:
    """Refresh contention does not launch work or erase the safe cache."""

    application = RecordingApplication()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = CachedReadinessCoordinator(
        application=application,
        worker=RecordingWorker(),
        runtime_ownership=ownership,
        refresh_interval_seconds=60,
        stale_after_seconds=120,
        shutdown_timeout_seconds=1,
    )
    coordinator.start()
    first = coordinator.snapshot()

    with ownership.acquire(RuntimeOwner.execution):
        assert coordinator.refresh_now() is False
        assert application.inspect_calls == 1
        assert coordinator.snapshot().checked_at == first.checked_at

    coordinator.close()


def test_refresh_after_close_never_restarts_package_work() -> None:
    """A stale coordinator reference cannot launch provider work on shutdown."""

    application = RecordingApplication()
    coordinator = CachedReadinessCoordinator(
        application=application,
        worker=RecordingWorker(),
        runtime_ownership=RuntimeOwnershipCoordinator(),
        refresh_interval_seconds=60,
        stale_after_seconds=120,
        shutdown_timeout_seconds=1,
    )
    coordinator.start()
    coordinator.close()

    assert coordinator.refresh_now() is False
    assert application.inspect_calls == 1
