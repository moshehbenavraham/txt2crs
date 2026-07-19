"""Tests-first contract for the one-process serial txt2crs worker."""

import ast
import logging
from collections import deque
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Event, Lock, Thread
from time import monotonic
from typing import cast

import pytest

from app.services.txt2crs_worker import (
    SerialTxt2CrsWorker,
    WorkerApplication,
    WorkerClosedError,
    WorkerFailureCode,
    WorkerShutdownError,
    WorkerStatus,
)


@dataclass(frozen=True, slots=True)
class RecordingJob:
    """Expose only the two durable identity fields the public worker consumes."""

    job_id: str
    user_id: str


@dataclass(frozen=True, slots=True)
class RecordingRunnable:
    """Structurally match the public resume state used by the supervisor."""

    job: RecordingJob


@dataclass(slots=True)
class ConcurrencyCounter:
    """Track active fake executors without relying on thread timing guesses."""

    active_count: int = 0
    maximum_active_count: int = 0


class RecordingExecutor:
    """Event-coordinated public executor handle used by worker tests."""

    def __init__(
        self,
        *,
        name: str,
        concurrency_counter: ConcurrencyCounter,
        concurrency_lock: Lock,
        release_execution: Event | None = None,
        execute_error: Exception | None = None,
        close_error: Exception | None = None,
    ) -> None:
        self.name = name
        self._concurrency_counter = concurrency_counter
        self._concurrency_lock = concurrency_lock
        self._release_execution = release_execution
        self._execute_error = execute_error
        self._close_error = close_error
        self.execution_entered = Event()
        self.execution_finished = Event()
        self.shutdown_requested = Event()
        self.close_calls = 0

    def execute(self) -> object:
        """Run once, optionally block, and publish exact overlap evidence."""

        with self._concurrency_lock:
            self._concurrency_counter.active_count += 1
            self._concurrency_counter.maximum_active_count = max(
                self._concurrency_counter.maximum_active_count,
                self._concurrency_counter.active_count,
            )
        self.execution_entered.set()
        try:
            if self._release_execution is not None:
                assert self._release_execution.wait(timeout=2)
            if self._execute_error is not None:
                raise self._execute_error
            return object()
        finally:
            with self._concurrency_lock:
                self._concurrency_counter.active_count -= 1
            self.execution_finished.set()

    def request_shutdown(self) -> None:
        """Record the supervisor's non-blocking process interruption."""

        self.shutdown_requested.set()

    def close(self) -> None:
        """Record resource cleanup and optionally expose one private failure."""

        self.close_calls += 1
        if self._close_error is not None:
            raise self._close_error


class RecordingApplication:
    """Thread-safe facade double with durable-discovery shaped behavior."""

    def __init__(
        self,
        runnables: tuple[RecordingRunnable, ...] = (),
        *,
        discovery_failures: int = 0,
    ) -> None:
        self._lock = Lock()
        self._runnables = deque(runnables)
        self._executors_by_job_id: dict[str, RecordingExecutor] = {}
        self._creation_failures_by_job_id: dict[str, Exception] = {}
        self._discovery_failures = discovery_failures
        self.discovery_calls = 0
        self.discovery_called = Event()
        self.last_discovery_call = Event()

    def add_runnable(
        self,
        runnable: RecordingRunnable,
        executor: RecordingExecutor,
    ) -> None:
        """Add durable-looking work independently from an in-memory nudge."""

        with self._lock:
            self._runnables.append(runnable)
            self._executors_by_job_id[runnable.job.job_id] = executor

    def fail_creation(self, *, job_id: str, error: Exception) -> None:
        """Configure one public executor factory failure."""

        with self._lock:
            self._creation_failures_by_job_id[job_id] = error

    def next_runnable(self) -> RecordingRunnable | None:
        """Return one queued public resume state or a configured safe retry."""

        with self._lock:
            self.discovery_calls += 1
            self.discovery_called.set()
            if self._discovery_failures > 0:
                self._discovery_failures -= 1
                raise RuntimeError(
                    "private discovery failure for /var/lib/txt2crs/jobs.sqlite3"
                )
            if not self._runnables:
                self.last_discovery_call.set()
                return None
            return self._runnables.popleft()

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> RecordingExecutor:
        """Return the exact owner/job-bound handle selected by the facade."""

        with self._lock:
            creation_error = self._creation_failures_by_job_id.pop(job_id, None)
            if creation_error is not None:
                raise creation_error
            executor = self._executors_by_job_id[job_id]
        assert user_id == f"owner-{job_id}"
        return executor


def _runnable(job_number: int) -> RecordingRunnable:
    """Return one stable owner/job identity without learner content."""

    job_id = f"job-{job_number}"
    return RecordingRunnable(job=RecordingJob(job_id, f"owner-{job_id}"))


def _wait_until(predicate: Callable[[], bool], *, timeout: float = 2) -> None:
    """Wait for a zero-argument predicate without an unbounded test sleep."""

    deadline = monotonic() + timeout
    brief_wait = Event()
    while monotonic() < deadline:
        if predicate():
            return
        brief_wait.wait(timeout=0.001)
    pytest.fail("The expected concurrent state was not reached within the bound.")


def _worker(
    application: RecordingApplication,
    *,
    poll_interval_seconds: float = 0.01,
    shutdown_timeout_seconds: float = 0.2,
) -> SerialTxt2CrsWorker:
    """Build one focused supervisor without provider or database access."""

    return SerialTxt2CrsWorker(
        application=cast(WorkerApplication, application),
        poll_interval_seconds=poll_interval_seconds,
        shutdown_timeout_seconds=shutdown_timeout_seconds,
    )


def test_worker_imports_only_public_txt2crs_boundaries() -> None:
    """The shell worker cannot bypass facade recovery or executor ownership."""

    worker_path = Path(__file__).parents[2] / "app" / "services" / "txt2crs_worker.py"
    parsed_module = ast.parse(worker_path.read_text(encoding="utf-8"))
    imported_txt2crs_modules = {
        imported_module.module
        for imported_module in ast.walk(parsed_module)
        if isinstance(imported_module, ast.ImportFrom)
        and imported_module.module is not None
        and imported_module.module.startswith("txt2crs")
    }

    assert imported_txt2crs_modules <= {
        "txt2crs.application",
        "txt2crs.jobs",
    }


def test_startup_scans_immediately_and_nudge_wakes_idle_poll() -> None:
    """Startup and missed-event recovery do not depend on an HTTP submission."""

    concurrency_counter = ConcurrencyCounter()
    concurrency_lock = Lock()
    first_runnable = _runnable(1)
    first_executor = RecordingExecutor(
        name="first",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
    )
    application = RecordingApplication()
    application.add_runnable(first_runnable, first_executor)
    worker = _worker(application, poll_interval_seconds=60)

    worker.start()
    assert first_executor.execution_finished.wait(timeout=2)

    second_runnable = _runnable(2)
    second_executor = RecordingExecutor(
        name="second",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
    )
    application.add_runnable(second_runnable, second_executor)
    worker.notify_runnable()

    assert second_executor.execution_finished.wait(timeout=2)
    worker.close()
    assert first_executor.close_calls == 1
    assert second_executor.close_calls == 1


def test_worker_never_overlaps_two_executor_graphs() -> None:
    """The P0 process owns exactly one active provider graph."""

    concurrency_counter = ConcurrencyCounter()
    concurrency_lock = Lock()
    release_first = Event()
    first_executor = RecordingExecutor(
        name="first",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
        release_execution=release_first,
    )
    second_executor = RecordingExecutor(
        name="second",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
    )
    application = RecordingApplication()
    application.add_runnable(_runnable(1), first_executor)
    application.add_runnable(_runnable(2), second_executor)
    worker = _worker(application)

    worker.start()
    assert first_executor.execution_entered.wait(timeout=2)
    assert second_executor.execution_entered.wait(timeout=0.05) is False

    release_first.set()
    assert second_executor.execution_finished.wait(timeout=2)
    worker.close()
    assert concurrency_counter.maximum_active_count == 1


def test_discovery_failure_retries_without_logging_private_detail(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A transient facade read cannot kill the worker or leak its exception."""

    caplog.set_level(logging.INFO)
    concurrency_counter = ConcurrencyCounter()
    concurrency_lock = Lock()
    executor = RecordingExecutor(
        name="recovered",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
    )
    application = RecordingApplication(discovery_failures=1)
    application.add_runnable(_runnable(1), executor)
    worker = _worker(application)

    worker.start()
    assert executor.execution_finished.wait(timeout=2)
    snapshot = worker.snapshot()
    worker.close()

    assert application.discovery_calls >= 2
    assert snapshot.last_failure_code is WorkerFailureCode.discovery_failed
    assert "/var/lib/txt2crs" not in caplog.text
    assert "private discovery failure" not in caplog.text


def test_creation_and_cleanup_failures_do_not_stop_later_work() -> None:
    """Every failed attempt is isolated and the periodic queue scan continues."""

    concurrency_counter = ConcurrencyCounter()
    concurrency_lock = Lock()
    first_runnable = _runnable(1)
    second_runnable = _runnable(2)
    third_runnable = _runnable(3)
    cleanup_failure_executor = RecordingExecutor(
        name="cleanup-failure",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
        close_error=OSError("/private/provider/session"),
    )
    final_executor = RecordingExecutor(
        name="final",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
    )
    application = RecordingApplication()
    application.add_runnable(
        first_runnable,
        RecordingExecutor(
            name="unused",
            concurrency_counter=concurrency_counter,
            concurrency_lock=concurrency_lock,
        ),
    )
    application.fail_creation(
        job_id=first_runnable.job.job_id,
        error=RuntimeError("private factory error"),
    )
    application.add_runnable(second_runnable, cleanup_failure_executor)
    application.add_runnable(third_runnable, final_executor)
    worker = _worker(application)

    worker.start()
    assert final_executor.execution_finished.wait(timeout=2)
    snapshot = worker.snapshot()
    worker.close()

    assert cleanup_failure_executor.close_calls == 1
    assert final_executor.close_calls == 1
    assert snapshot.last_failure_code is WorkerFailureCode.cleanup_failed


def test_worker_snapshot_is_bounded_and_contains_no_runnable_identity() -> None:
    """Later readiness consumes booleans and enums, never private job state."""

    concurrency_counter = ConcurrencyCounter()
    concurrency_lock = Lock()
    release_execution = Event()
    executor = RecordingExecutor(
        name="active",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
        release_execution=release_execution,
    )
    application = RecordingApplication()
    application.add_runnable(_runnable(8675309), executor)
    worker = _worker(application)

    stopped_snapshot = worker.snapshot()
    worker.start()
    assert executor.execution_entered.wait(timeout=2)
    active_snapshot = worker.snapshot()

    assert stopped_snapshot.status is WorkerStatus.stopped
    assert stopped_snapshot.is_alive is False
    assert active_snapshot.status is WorkerStatus.active
    assert active_snapshot.is_alive is True
    assert active_snapshot.has_active_job is True
    assert active_snapshot.has_capacity is False
    serialized_snapshot = str(asdict(active_snapshot))
    assert "8675309" not in serialized_snapshot
    assert "owner-" not in serialized_snapshot

    release_execution.set()
    worker.close()


def test_shutdown_stops_claims_before_current_executor_drains() -> None:
    """A second durable item cannot start after the stop transition begins."""

    concurrency_counter = ConcurrencyCounter()
    concurrency_lock = Lock()
    release_first = Event()
    first_executor = RecordingExecutor(
        name="first",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
        release_execution=release_first,
    )
    second_executor = RecordingExecutor(
        name="second",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
    )
    application = RecordingApplication()
    application.add_runnable(_runnable(1), first_executor)
    application.add_runnable(_runnable(2), second_executor)
    worker = _worker(application, shutdown_timeout_seconds=1)
    close_errors: list[BaseException] = []

    worker.start()
    assert first_executor.execution_entered.wait(timeout=2)

    def close_worker() -> None:
        try:
            worker.close()
        except BaseException as error:
            close_errors.append(error)

    close_thread = Thread(target=close_worker)
    close_thread.start()
    _wait_until(lambda: worker.snapshot().is_shutting_down)
    release_first.set()
    close_thread.join(timeout=2)

    assert close_thread.is_alive() is False
    assert close_errors == []
    assert second_executor.execution_entered.is_set() is False
    assert first_executor.shutdown_requested.is_set() is False
    assert worker.snapshot().status is WorkerStatus.stopped


def test_shutdown_timeout_requests_restart_safe_interruption_and_can_finish() -> None:
    """The bounded close reports safely while leaving active cleanup retryable."""

    concurrency_counter = ConcurrencyCounter()
    concurrency_lock = Lock()
    release_execution = Event()
    executor = RecordingExecutor(
        name="blocked",
        concurrency_counter=concurrency_counter,
        concurrency_lock=concurrency_lock,
        release_execution=release_execution,
    )
    application = RecordingApplication()
    application.add_runnable(_runnable(1), executor)
    worker = _worker(application, shutdown_timeout_seconds=0.01)

    worker.start()
    assert executor.execution_entered.wait(timeout=2)

    with pytest.raises(WorkerShutdownError, match="within the configured bound") as exc:
        worker.close()

    timed_out_snapshot = worker.snapshot()
    assert executor.shutdown_requested.is_set() is True
    assert timed_out_snapshot.is_shutting_down is True
    assert timed_out_snapshot.last_failure_code is WorkerFailureCode.shutdown_timed_out
    assert "blocked" not in str(exc.value)

    release_execution.set()
    assert executor.execution_finished.wait(timeout=2)
    worker.close()
    assert worker.snapshot().status is WorkerStatus.stopped


def test_close_before_start_is_terminal_and_repeated_close_is_safe() -> None:
    """A closed supervisor cannot create a late duplicate worker thread."""

    worker = _worker(RecordingApplication())

    worker.close()
    worker.close()
    worker.notify_runnable()

    with pytest.raises(WorkerClosedError, match="closed"):
        worker.start()
