"""
One-process serial worker over the public txt2crs application facade.

The durable engine database is the queue. This shell service owns only thread
supervision, polling, shutdown ordering, and a small readiness-safe snapshot.
It must never import a private store, request envelope, checkpoint, provider,
pipeline, or renderer.
"""

from dataclasses import dataclass
from enum import StrEnum
from threading import Event, RLock, Thread
from typing import Protocol

from app.core.logging import get_logger

logger = get_logger(__name__)

WORKER_SNAPSHOT_SCHEMA_VERSION = "1.0"
WORKER_THREAD_NAME = "txt2crs-serial-worker"


class WorkerStatus(StrEnum):
    """Finite lifecycle states safe for later readiness composition."""

    stopped = "stopped"
    starting = "starting"
    idle = "idle"
    active = "active"
    shutting_down = "shutting_down"
    failed = "failed"


class WorkerFailureCode(StrEnum):
    """Bounded reasons that never retain a private exception or identity."""

    discovery_failed = "discovery_failed"
    executor_creation_failed = "executor_creation_failed"
    execution_failed = "execution_failed"
    cleanup_failed = "cleanup_failed"
    shutdown_timed_out = "shutdown_timed_out"
    worker_crashed = "worker_crashed"


class WorkerClosedError(RuntimeError):
    """A caller tried to restart a supervisor after terminal close."""


class WorkerShutdownError(RuntimeError):
    """The active executor did not drain within the configured bound."""


@dataclass(frozen=True, slots=True)
class WorkerSnapshot:
    """Immutable, content-free worker state consumed by readiness code."""

    schema_version: str
    status: WorkerStatus
    is_alive: bool
    has_active_job: bool
    has_capacity: bool
    is_shutting_down: bool
    last_failure_code: WorkerFailureCode | None


class RunnableJob(Protocol):
    """Two durable identity fields exposed by one public resume state."""

    @property
    def job_id(self) -> str:
        """Return the package-owned job identity."""

    @property
    def user_id(self) -> str:
        """Return the package-owned pseudonymous owner identity."""


class RunnableState(Protocol):
    """Narrow structural view of ``txt2crs.jobs.models.ResumeState``."""

    @property
    def job(self) -> RunnableJob:
        """Return the durable row selected by package ordering."""


class WorkerExecutor(Protocol):
    """Public one-shot executor operations needed by the supervisor."""

    def execute(self) -> object:
        """Execute or resume the already-bound owner/job."""

    def request_shutdown(self) -> None:
        """Request restart-safe interruption without waiting."""

    def close(self) -> None:
        """Settle and release all executor-owned resources."""


class WorkerApplication(Protocol):
    """Public facade operations used by the worker and nothing more."""

    def next_runnable(self) -> RunnableState | None:
        """Return the next package-ordered durable recovery item."""

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> WorkerExecutor:
        """Create one fresh public executor graph."""


def _log_worker_event_safely(
    event_name: str,
    *,
    extra: dict[str, object] | None = None,
    level: str = "info",
) -> None:
    """
    Emit one bounded event without letting an observer kill the worker.

    Session 03 will compose the complete sanitized observability layer. The
    supervisor already treats logging as best-effort because a custom handler
    must not leak a provider graph or stop durable recovery.
    """
    try:
        log_method = logger.error if level == "error" else logger.info
        log_method(event_name, extra=extra)
    except BaseException:
        return


class SerialTxt2CrsWorker:
    """
    Discover and execute at most one durable job at a time.

    The event is deliberately only a wake-up hint. Clearing it before a timed
    wait prevents stale hints from spinning, while the finite timeout ensures
    startup recovery and missed notifications still scan the durable queue.
    """

    def __init__(
        self,
        *,
        application: WorkerApplication,
        poll_interval_seconds: float,
        shutdown_timeout_seconds: float,
    ) -> None:
        if poll_interval_seconds <= 0 or poll_interval_seconds > 60:
            raise ValueError("Worker polling must be between 0 and 60 seconds.")
        if shutdown_timeout_seconds <= 0 or shutdown_timeout_seconds > 300:
            raise ValueError("Worker shutdown must be between 0 and 300 seconds.")

        self._application = application
        self._poll_interval_seconds = poll_interval_seconds
        self._shutdown_timeout_seconds = shutdown_timeout_seconds
        self._lock = RLock()
        self._stop_requested = Event()
        self._wake_requested = Event()
        self._thread: Thread | None = None
        self._active_executor: WorkerExecutor | None = None
        self._status = WorkerStatus.stopped
        self._last_failure_code: WorkerFailureCode | None = None
        self._close_requested = False
        self._is_closed = False

    def start(self) -> None:
        """Start exactly one daemon thread and scan before the first wait."""

        with self._lock:
            if self._close_requested or self._is_closed:
                raise WorkerClosedError("The txt2crs worker is closed.")
            if self._thread is not None:
                return

            self._status = WorkerStatus.starting
            worker_thread = Thread(
                target=self._run,
                name=WORKER_THREAD_NAME,
                daemon=True,
            )
            self._thread = worker_thread
            worker_thread.start()
        _log_worker_event_safely("txt2crs.worker_started")

    def notify_runnable(self) -> None:
        """Wake an idle poll after a durable commit; never act as the queue."""

        with self._lock:
            if self._close_requested or self._is_closed:
                return
            self._wake_requested.set()

    def snapshot(self) -> WorkerSnapshot:
        """Return one detached safe lifecycle projection."""

        with self._lock:
            worker_thread = self._thread
            is_alive = worker_thread is not None and worker_thread.is_alive()
            has_active_job = self._active_executor is not None
            is_shutting_down = self._close_requested and not self._is_closed
            return WorkerSnapshot(
                schema_version=WORKER_SNAPSHOT_SCHEMA_VERSION,
                status=self._status,
                is_alive=is_alive,
                has_active_job=has_active_job,
                has_capacity=(
                    is_alive
                    and self._status is WorkerStatus.idle
                    and not has_active_job
                    and not is_shutting_down
                ),
                is_shutting_down=is_shutting_down,
                last_failure_code=self._last_failure_code,
            )

    def close(self) -> None:
        """
        Stop claims, drain once, then signal restart-safe interruption.

        A timed-out call leaves the thread and executor reference intact so a
        later FastAPI facade close can join resource cleanup. Calling ``close``
        again after the executor settles finalizes the supervisor idempotently.
        """
        with self._lock:
            if self._is_closed:
                return
            self._close_requested = True
            self._stop_requested.set()
            self._wake_requested.set()
            worker_thread = self._thread
            if worker_thread is None:
                self._status = WorkerStatus.stopped
                self._is_closed = True
                return
            self._status = WorkerStatus.shutting_down

        _log_worker_event_safely("txt2crs.worker_shutdown_started")
        worker_thread.join(timeout=self._shutdown_timeout_seconds)
        if worker_thread.is_alive():
            with self._lock:
                active_executor = self._active_executor
            if active_executor is not None:
                try:
                    active_executor.request_shutdown()
                except Exception:
                    # The bounded shutdown result is already a failure. Record
                    # only a safe code and let facade cleanup attempt the join.
                    self._record_failure(WorkerFailureCode.cleanup_failed)
            self._record_failure(
                WorkerFailureCode.shutdown_timed_out,
                status=WorkerStatus.shutting_down,
            )
            raise WorkerShutdownError(
                "The txt2crs worker did not stop within the configured bound."
            ) from None

        with self._lock:
            self._status = WorkerStatus.stopped
            self._is_closed = True
        _log_worker_event_safely("txt2crs.worker_shutdown_completed")

    def _run(self) -> None:
        """Own the complete serial discovery and executor loop."""

        try:
            with self._lock:
                if self._stop_requested.is_set():
                    self._status = WorkerStatus.stopped
                    return
                self._status = WorkerStatus.idle

            while not self._stop_requested.is_set():
                runnable_state = self._discover_next_runnable()
                if runnable_state is None:
                    self._wait_for_retry()
                    continue
                if self._stop_requested.is_set():
                    break

                executor = self._create_executor(runnable_state)
                if executor is None:
                    self._wait_for_retry()
                    continue
                if self._stop_requested.is_set():
                    self._close_unstarted_executor(executor)
                    break

                did_attempt_fail = self._execute_one(executor)
                if did_attempt_fail and not self._stop_requested.is_set():
                    self._wait_for_retry()
        except BaseException:
            # Exception-shaped failures are isolated in helper methods. This
            # final guard covers programming errors and interpreter-level
            # exits without retaining the private exception on worker state.
            self._record_failure(
                WorkerFailureCode.worker_crashed,
                status=WorkerStatus.failed,
            )
        finally:
            with self._lock:
                if self._status is not WorkerStatus.failed:
                    self._status = (
                        WorkerStatus.shutting_down
                        if self._close_requested and not self._is_closed
                        else WorkerStatus.stopped
                    )

    def _discover_next_runnable(self) -> RunnableState | None:
        """Read one package-ordered item and convert failures into safe retry."""

        try:
            return self._application.next_runnable()
        except Exception:
            self._record_failure(WorkerFailureCode.discovery_failed)
            return None

    def _create_executor(
        self,
        runnable_state: RunnableState,
    ) -> WorkerExecutor | None:
        """Create one public graph without exposing its durable identity."""

        try:
            return self._application.create_executor(
                job_id=runnable_state.job.job_id,
                user_id=runnable_state.job.user_id,
            )
        except Exception:
            self._record_failure(WorkerFailureCode.executor_creation_failed)
            return None

    def _execute_one(self, executor: WorkerExecutor) -> bool:
        """Run and close one graph, returning whether a retry delay is needed."""

        with self._lock:
            if self._stop_requested.is_set():
                self._close_unstarted_executor(executor)
                return False
            self._active_executor = executor
            self._status = WorkerStatus.active

        execution_failed = False
        cleanup_failed = False
        try:
            executor.execute()
        except Exception:
            # Process interruption intentionally reaches this branch. Once
            # shutdown has started it is an expected recovery path, not an
            # operational execution failure.
            if not self._stop_requested.is_set():
                execution_failed = True
                self._record_failure(WorkerFailureCode.execution_failed)
        finally:
            try:
                executor.close()
            except Exception:
                cleanup_failed = True
                self._record_failure(WorkerFailureCode.cleanup_failed)
            with self._lock:
                if self._active_executor is executor:
                    self._active_executor = None
                self._status = (
                    WorkerStatus.shutting_down
                    if self._stop_requested.is_set()
                    else WorkerStatus.idle
                )
        return execution_failed or cleanup_failed

    def _close_unstarted_executor(self, executor: WorkerExecutor) -> None:
        """Release a graph acquired just as shutdown stopped new claims."""

        try:
            executor.close()
        except Exception:
            self._record_failure(WorkerFailureCode.cleanup_failed)

    def _wait_for_retry(self) -> None:
        """Wait for either a latency nudge, shutdown, or the durable poll bound."""

        self._wake_requested.clear()
        if self._stop_requested.is_set():
            return
        self._wake_requested.wait(timeout=self._poll_interval_seconds)

    def _record_failure(
        self,
        failure_code: WorkerFailureCode,
        *,
        status: WorkerStatus | None = None,
    ) -> None:
        """Store and log one safe code without retaining an exception object."""

        with self._lock:
            self._last_failure_code = failure_code
            if status is not None:
                self._status = status
        _log_worker_event_safely(
            "txt2crs.worker_failed",
            extra={"reason_code": failure_code.value},
            level="error",
        )
