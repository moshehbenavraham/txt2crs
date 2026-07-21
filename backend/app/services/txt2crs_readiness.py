"""Side-effect-free shell cache over complete package readiness."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from threading import Event, RLock, Thread
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import SubscriptionQuotaState
from txt2crs.application import (
    ApplicationReadiness,
    ApplicationReadinessCheckState,
    ApplicationReadinessStatus,
)

from app.core.logging import get_logger
from app.services.txt2crs_runtime import (
    RuntimeOwner,
    RuntimeOwnershipCoordinator,
)
from app.services.txt2crs_worker import WorkerSnapshot, WorkerStatus

READINESS_SCHEMA_VERSION = "1.0"
READINESS_THREAD_NAME = "txt2crs-readiness-maintenance"

logger = get_logger(__name__)


class ReadinessStatus(StrEnum):
    """Overall cached state presented to later API schemas."""

    ready = "ready"
    degraded = "degraded"
    unavailable = "unavailable"


class ReadinessCheckState(StrEnum):
    """Coarse state for one safe shell readiness dimension."""

    ready = "ready"
    unavailable = "unavailable"


class ReadinessChecks(BaseModel):
    """Allowlisted checks with no provider or infrastructure detail."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    authentication: ReadinessCheckState
    model: ReadinessCheckState
    research: ReadinessCheckState
    storage: ReadinessCheckState
    worker: ReadinessCheckState
    inputs: ReadinessCheckState
    admission: ReadinessCheckState
    runtime_ownership: ReadinessCheckState


class ReadinessSnapshot(BaseModel):
    """Immutable last-known state returned without synchronous probe work."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = READINESS_SCHEMA_VERSION
    status: ReadinessStatus
    accepting_jobs: bool
    configured_model_id: str
    enabled_input_modes: tuple[str, ...] = Field(max_length=20)
    checks: ReadinessChecks
    warnings: tuple[str, ...] = Field(max_length=20)
    recovery_actions: tuple[str, ...] = Field(max_length=20)
    checked_at: datetime
    is_fresh: bool


class ReadinessApplication(Protocol):
    """One public package facade operation used by maintenance refresh."""

    def inspect_application_readiness(self) -> ApplicationReadiness:
        """Run and return the package-owned aggregate probe."""


class ReadinessWorker(Protocol):
    """Safe worker state used by side-effect-free cache reads."""

    def snapshot(self) -> WorkerSnapshot:
        """Return one detached content-free worker projection."""


class ReadinessClosedError(RuntimeError):
    """A caller tried to restart a terminal readiness coordinator."""


class ReadinessShutdownError(RuntimeError):
    """The finite maintenance thread did not stop within its bound."""


class CachedReadinessCoordinator:
    """
    Refresh package readiness on a bounded schedule and serve only snapshots.

    Browser-facing callers use ``snapshot``. Only ``start``, ``refresh_now``,
    and the maintenance thread can invoke the package's provider or storage
    probes.
    """

    def __init__(
        self,
        *,
        application: ReadinessApplication | None,
        worker: ReadinessWorker | None,
        runtime_ownership: RuntimeOwnershipCoordinator,
        refresh_interval_seconds: float,
        stale_after_seconds: float,
        shutdown_timeout_seconds: float,
        configured_model_id: str = "gpt-5.6-sol",
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if refresh_interval_seconds <= 0 or refresh_interval_seconds > 3_600:
            raise ValueError("Readiness refresh must be between 0 and 3600 seconds.")
        if stale_after_seconds < refresh_interval_seconds:
            raise ValueError("Readiness stale bound cannot be shorter than refresh.")
        if stale_after_seconds > 7_200:
            raise ValueError("Readiness stale bound cannot exceed 7200 seconds.")
        if shutdown_timeout_seconds <= 0 or shutdown_timeout_seconds > 300:
            raise ValueError("Readiness shutdown must be between 0 and 300 seconds.")

        self._application = application
        self._worker = worker
        self._runtime_ownership = runtime_ownership
        self._refresh_interval_seconds = refresh_interval_seconds
        self._stale_after_seconds = stale_after_seconds
        self._shutdown_timeout_seconds = shutdown_timeout_seconds
        self._configured_model_id = configured_model_id
        self._clock = clock or (lambda: datetime.now(UTC))
        self._lock = RLock()
        self._stop_requested = Event()
        self._thread: Thread | None = None
        self._is_started = False
        self._is_closed = False
        initial_time = self._now()
        self._cached_package_readiness = _unavailable_package_readiness(
            configured_model_id=configured_model_id,
            warning="System setup is incomplete.",
            recovery_action="Complete system setup and retry readiness.",
        )
        self._checked_at = initial_time

    def start(self) -> None:
        """Refresh once before serving, then start finite maintenance."""

        with self._lock:
            if self._is_closed:
                raise ReadinessClosedError("Readiness coordination is closed.")
            if self._is_started:
                return
            self._is_started = True

        if self._application is None:
            _log_readiness_event(
                "system.readiness_validated",
                extra={"status": ReadinessStatus.unavailable.value},
            )
            return

        # Startup performs one bounded probe before the worker can claim the
        # provider runtime. FastAPI ordering is responsible for calling this
        # before worker.start().
        self.refresh_now()
        maintenance_thread = Thread(
            target=self._run,
            name=READINESS_THREAD_NAME,
            daemon=True,
        )
        with self._lock:
            self._thread = maintenance_thread
        try:
            maintenance_thread.start()
        except BaseException:
            with self._lock:
                self._thread = None
                self._is_started = False
            raise

    def refresh_now(self) -> bool:
        """
        Refresh immediately when runtime ownership is available.

        Returning ``False`` is normal while execution or authentication owns
        the runtime. The last safe cache remains authoritative.
        """

        with self._lock:
            if self._is_closed or self._application is None:
                return False
        runtime_lease = self._runtime_ownership.try_acquire(RuntimeOwner.readiness)
        if runtime_lease is None:
            _log_readiness_event(
                "system.readiness_deferred",
                extra={"reason_code": "runtime_busy"},
            )
            return False

        with runtime_lease:
            try:
                package_readiness = self._application.inspect_application_readiness()
            except Exception:
                package_readiness = _unavailable_package_readiness(
                    configured_model_id=self._configured_model_id,
                    warning="System readiness could not be refreshed.",
                    recovery_action="Retry system readiness.",
                )

        with self._lock:
            if self._is_closed:
                return False
            self._cached_package_readiness = package_readiness
            self._checked_at = self._now()
        _log_readiness_event(
            "system.readiness_validated",
            extra={"status": package_readiness.status.value},
        )
        return True

    def snapshot(self) -> ReadinessSnapshot:
        """Combine cached package and live safe worker/owner state only."""

        with self._lock:
            package_readiness = self._cached_package_readiness
            checked_at = self._checked_at
        current_time = self._now()
        is_fresh = current_time <= checked_at + timedelta(
            seconds=self._stale_after_seconds
        )
        # Read ownership before worker state so the two snapshots have a useful
        # ordering. If execution ownership is observed first and discovery then
        # claims a durable job, the worker's later ``active`` state wins. This
        # avoids misclassifying the executor-construction window as an idle scan.
        ownership_snapshot = self._runtime_ownership.snapshot()
        worker_snapshot = self._worker.snapshot() if self._worker is not None else None

        package_checks = package_readiness.checks
        storage_ready = (
            package_checks.sqlite is ApplicationReadinessCheckState.ready
            and package_checks.artifacts is ApplicationReadinessCheckState.ready
        )
        worker_ready = (
            worker_snapshot is not None
            and worker_snapshot.is_alive
            and worker_snapshot.has_capacity
            and not worker_snapshot.is_shutting_down
        )
        # The serial worker holds execution ownership while it checks the
        # durable queue, even when there is no job. That very short idle scan is
        # internal synchronization, not user-visible provider work. Once a job
        # is found, the worker publishes ``active`` before constructing its
        # executor, so only the exact idle/capable state is safe to treat as
        # available here.
        execution_owner_is_only_scanning_idle_queue = (
            ownership_snapshot.owner is RuntimeOwner.execution
            and worker_snapshot is not None
            and worker_snapshot.status is WorkerStatus.idle
            and worker_snapshot.has_capacity
            and not worker_snapshot.has_active_job
            and not worker_snapshot.is_shutting_down
        )
        owner_ready = (
            ownership_snapshot.is_available
            or execution_owner_is_only_scanning_idle_queue
        )
        checks = ReadinessChecks(
            authentication=_shell_check(package_checks.authentication),
            model=_shell_check(package_checks.model),
            research=_shell_check(package_checks.research),
            storage=_boolean_check(storage_ready),
            worker=_boolean_check(worker_ready),
            inputs=_shell_check(package_checks.inputs),
            admission=_shell_check(package_checks.admission),
            runtime_ownership=_boolean_check(owner_ready),
        )
        accepting_jobs = (
            is_fresh
            and package_readiness.status is ApplicationReadinessStatus.ready
            and worker_ready
            and owner_ready
        )
        worker_operational = (
            worker_snapshot is not None
            and worker_snapshot.is_alive
            and not worker_snapshot.is_shutting_down
        )
        worker_is_processing = worker_snapshot is not None and (
            worker_snapshot.status is WorkerStatus.active
            or worker_snapshot.has_active_job
        )
        is_temporarily_busy = (
            ownership_snapshot.owner is not None
            and not execution_owner_is_only_scanning_idle_queue
        ) or worker_is_processing
        is_degraded = (
            is_fresh
            and package_readiness.status is ApplicationReadinessStatus.ready
            and worker_operational
            and is_temporarily_busy
        )
        warnings = list(package_readiness.warnings)
        recovery_actions = list(package_readiness.recovery_actions)
        if not is_fresh:
            warnings.append("System readiness is stale.")
            recovery_actions.append("Wait for readiness to refresh.")
        if not worker_ready and worker_snapshot is not None:
            if worker_is_processing:
                warnings.append("The course worker is processing a job.")
                recovery_actions.append("Wait for the active job to finish.")
            else:
                warnings.append("The course worker is unavailable.")
                recovery_actions.append("Wait for the course worker to become ready.")
        if not owner_ready:
            warnings.append("The provider runtime is currently busy.")
            recovery_actions.append("Wait for the active operation to finish.")

        return ReadinessSnapshot(
            status=(
                ReadinessStatus.ready
                if accepting_jobs
                else (
                    ReadinessStatus.degraded
                    if is_degraded
                    else ReadinessStatus.unavailable
                )
            ),
            accepting_jobs=accepting_jobs,
            configured_model_id=package_readiness.configured_model_id,
            enabled_input_modes=package_readiness.enabled_input_modes,
            checks=checks,
            warnings=tuple(warnings[:20]),
            recovery_actions=tuple(recovery_actions[:20]),
            checked_at=checked_at,
            is_fresh=is_fresh,
        )

    def close(self) -> None:
        """Stop and join finite maintenance without touching package state."""

        with self._lock:
            if self._is_closed:
                return
            self._is_closed = True
            self._stop_requested.set()
            maintenance_thread = self._thread
        if maintenance_thread is None:
            return
        maintenance_thread.join(timeout=self._shutdown_timeout_seconds)
        if maintenance_thread.is_alive():
            raise ReadinessShutdownError(
                "Readiness maintenance did not stop within its bound."
            ) from None

    def _run(self) -> None:
        """Wait before each maintenance refresh so startup is not duplicated."""

        while not self._stop_requested.wait(self._refresh_interval_seconds):
            self.refresh_now()

    def _now(self) -> datetime:
        """Return one normalized aware UTC time for freshness comparisons."""

        current_time = self._clock()
        if current_time.tzinfo is None:
            raise ValueError("Readiness clock must return an aware datetime.")
        return current_time.astimezone(UTC)


def _unavailable_package_readiness(
    *,
    configured_model_id: str,
    warning: str,
    recovery_action: str,
) -> ApplicationReadiness:
    """Return a complete generic failure with no private diagnostic."""

    return ApplicationReadiness.create(
        configured_model_id=configured_model_id,
        enabled_input_modes=(),
        runtime=RuntimeReadiness.create(
            status=RuntimeReadinessStatus.unavailable,
            credential_status=CredentialStatus.unknown,
            model_entitled=False,
            subscription_quota_state=SubscriptionQuotaState.unknown,
            warnings=[],
            recovery_actions=[],
        ),
        research_ready=False,
        sqlite_ready=False,
        artifacts_ready=False,
        inputs_ready=False,
        admission_ready=False,
        warnings=[warning],
        recovery_actions=[recovery_action],
    )


def _shell_check(
    package_state: ApplicationReadinessCheckState,
) -> ReadinessCheckState:
    """Translate the public package enum without exposing internals."""

    return (
        ReadinessCheckState.ready
        if package_state is ApplicationReadinessCheckState.ready
        else ReadinessCheckState.unavailable
    )


def _boolean_check(is_ready: bool) -> ReadinessCheckState:
    """Translate one safe shell boolean to a finite state."""

    return ReadinessCheckState.ready if is_ready else ReadinessCheckState.unavailable


def _log_readiness_event(
    event_name: str,
    *,
    extra: dict[str, object] | None = None,
) -> None:
    """Keep observer failures from replacing readiness or cleanup behavior."""

    try:
        logger.info(event_name, extra=extra)
    except BaseException:
        return


__all__ = [
    "CachedReadinessCoordinator",
    "ReadinessCheckState",
    "ReadinessChecks",
    "ReadinessClosedError",
    "ReadinessShutdownError",
    "ReadinessSnapshot",
    "ReadinessStatus",
]
