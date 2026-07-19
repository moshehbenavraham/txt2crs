# SPDX-License-Identifier: MIT-0

"""Tests-first public facade delegation, ownership, and close semantics."""

import gc
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import Event, Thread
from typing import Any, get_type_hints
from weakref import ref

import pytest

from tests.factories import (
    standard_admission_reservation,
    valid_generation_request,
)
from txt2crs.ai.runtime import CancellationReason, CancellationToken
from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.system_authentication import (
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
)
from txt2crs.ai.usage import SubscriptionQuotaState
from txt2crs.application import (
    ApplicationClosedError,
    ApplicationCloseError,
    ApplicationExecutor,
    ExecutorAlreadyUsedError,
    OwnerPurgeResult,
    Txt2CrsApplication,
)
from txt2crs.jobs import GenerationRequest
from txt2crs.jobs.models import JobRecord
from txt2crs.jobs.notifications import DeliveryNotificationPolicy
from txt2crs.jobs.quota import AdmissionLimits, AdmissionReservation
from txt2crs.jobs.service import InMemoryPrivateArtifactStore, JobService
from txt2crs.jobs.store import SqliteJobStore


@dataclass(slots=True)
class RecordingReadinessInspector:
    """Return one safe readiness value and count facade delegation."""

    calls: int = 0

    def inspect_readiness(self) -> RuntimeReadiness:
        """Return a browser-safe deterministic readiness projection."""

        self.calls += 1
        return RuntimeReadiness.create(
            status=RuntimeReadinessStatus.ready,
            credential_status=CredentialStatus.valid,
            model_entitled=True,
            subscription_quota_state=SubscriptionQuotaState.unknown,
            warnings=[],
            recovery_actions=[],
        )


@dataclass(slots=True)
class RecordingAuthenticator:
    """Small authentication double with only public-safe state."""

    events: list[str] = field(default_factory=list)

    @staticmethod
    def _snapshot(state: SystemAuthenticationState) -> SystemAuthenticationSnapshot:
        """Return one strict safe authentication fixture."""

        return SystemAuthenticationSnapshot(
            state=state,
            verification_url=None,
            user_code=None,
            message=f"Authentication is {state.value}.",
        )

    def start_device_code_login(self) -> SystemAuthenticationSnapshot:
        """Record start delegation."""

        self.events.append("auth-start")
        return self._snapshot(SystemAuthenticationState.waiting_for_user)

    def current_status(
        self,
        *,
        refresh: bool = False,
    ) -> SystemAuthenticationSnapshot:
        """Return a stable test snapshot."""

        self.events.append("auth-status")
        return self._snapshot(
            SystemAuthenticationState.authenticated
            if refresh
            else SystemAuthenticationState.signed_out
        )

    def logout(self) -> SystemAuthenticationSnapshot:
        """Record logout delegation."""

        self.events.append("auth-logout")
        return self._snapshot(SystemAuthenticationState.signed_out)

    def close(self) -> None:
        """Record application cleanup."""

        self.events.append("auth-close")


class RecordingGenerationExecutor:
    """Return the submitted job and count exact owner/job executions."""

    def __init__(self, result: JobRecord) -> None:
        self.result = result
        self.calls: list[tuple[str, str, CancellationToken]] = []

    def execute(
        self,
        *,
        job_id: str,
        user_id: str,
        cancellation: CancellationToken,
    ) -> JobRecord:
        """Record the exact bound execution."""

        self.calls.append((job_id, user_id, cancellation))
        return self.result


@dataclass(slots=True)
class RecordingExecutorFactory:
    """Build a fresh public executor handle for each facade request."""

    result: JobRecord
    created: list[ApplicationExecutor] = field(default_factory=list)

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
        generation_request: GenerationRequest,
    ) -> ApplicationExecutor:
        """Create one fresh cancellation and one bound executor."""

        assert generation_request.request_hash == self.result.request_hash
        handle = ApplicationExecutor(
            executor=RecordingGenerationExecutor(self.result),
            job_id=job_id,
            user_id=user_id,
            cancellation=CancellationToken(),
        )
        self.created.append(handle)
        return handle


@dataclass(slots=True)
class RecordingOwnerLifecycle:
    """Return a sentinel owner-purge result."""

    calls: list[str] = field(default_factory=list)

    def purge_owner(self, *, user_id: str) -> OwnerPurgeResult:
        """Record exact owner delegation."""

        self.calls.append(user_id)
        return OwnerPurgeResult(
            schema_version="1.0",
            deleted_job_count=1,
            deleted_artifact_job_count=1,
        )


class BlockingSubmitJobService(JobService):
    """Hold one facade call open so close synchronization is observable."""

    def __init__(
        self,
        *,
        result: JobRecord,
        submit_entered: Event,
        release_submit: Event,
    ) -> None:
        # This focused synchronization double overrides the only method the
        # test calls, so it deliberately does not construct JobService stores.
        self._result = result
        self._submit_entered = submit_entered
        self._release_submit = release_submit

    def submit(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        generation_request: GenerationRequest,
        admission_reservation: AdmissionReservation,
    ) -> JobRecord:
        """Block after the facade has admitted this operation."""

        del user_id, idempotency_key, generation_request, admission_reservation
        self._submit_entered.set()
        assert self._release_submit.wait(timeout=2)
        return self._result


class ObservableCancellationToken(CancellationToken):
    """Expose the instant an owner purge requests worker cancellation."""

    def __init__(self, cancellation_observed: Event) -> None:
        super().__init__()
        self._cancellation_observed = cancellation_observed

    def cancel(self) -> None:
        """Set both the production token and the test synchronization event."""

        super().cancel()
        self._cancellation_observed.set()

    def interrupt_for_shutdown(self) -> None:
        """Observe facade cleanup's restart-safe interruption path."""

        super().interrupt_for_shutdown()
        self._cancellation_observed.set()


class BlockingGenerationExecutor:
    """Represent an active job that cooperatively finishes after cancellation."""

    def __init__(
        self,
        *,
        result: JobRecord,
        execution_entered: Event,
        release_execution: Event,
    ) -> None:
        self._result = result
        self._execution_entered = execution_entered
        self._release_execution = release_execution

    def execute(
        self,
        *,
        job_id: str,
        user_id: str,
        cancellation: CancellationToken,
    ) -> JobRecord:
        """Remain active until the test permits cancellation cleanup to finish."""

        del job_id, user_id, cancellation
        self._execution_entered.set()
        assert self._release_execution.wait(timeout=2)
        return self._result


@dataclass(slots=True)
class BlockingExecutorFactory:
    """Create one observable active handle for owner-purge coordination."""

    result: JobRecord
    execution_entered: Event
    release_execution: Event
    cancellation_observed: Event

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
        generation_request: GenerationRequest,
    ) -> ApplicationExecutor:
        """Bind a blocking executor and observable cancellation to the job."""

        assert generation_request.request_hash == self.result.request_hash
        return ApplicationExecutor(
            executor=BlockingGenerationExecutor(
                result=self.result,
                execution_entered=self.execution_entered,
                release_execution=self.release_execution,
            ),
            job_id=job_id,
            user_id=user_id,
            cancellation=ObservableCancellationToken(self.cancellation_observed),
        )


@dataclass(slots=True)
class ObservableOwnerLifecycle:
    """Record when deletion begins after active execution has settled."""

    purge_called: Event

    def purge_owner(self, *, user_id: str) -> OwnerPurgeResult:
        """Publish one success sentinel after recording the owner."""

        assert user_id == "owner-123"
        self.purge_called.set()
        return OwnerPurgeResult(
            schema_version="1.0",
            deleted_job_count=1,
            deleted_artifact_job_count=1,
        )


def _admission_limits() -> AdmissionLimits:
    """Return generous local limits for facade unit tests."""

    return AdmissionLimits(
        window_seconds=3_600,
        maximum_jobs_per_user=10,
        maximum_jobs_global=100,
        maximum_reserved_tokens_per_user=1_000_000,
        maximum_reserved_tokens_global=10_000_000,
        maximum_research_cost_microusd_per_user=1_000_000,
        maximum_research_cost_microusd_global=10_000_000,
    )


def test_facade_exposes_strict_authentication_and_purge_return_types() -> None:
    """Public shell methods must not erase safe package contracts to Any."""

    assert (
        get_type_hints(Txt2CrsApplication.get_system_authentication_status)["return"]
        is SystemAuthenticationSnapshot
    )
    assert get_type_hints(Txt2CrsApplication.purge_owner)["return"] is OwnerPurgeResult


def _application(
    tmp_path: Any,
) -> tuple[
    Txt2CrsApplication,
    JobService,
    SqliteJobStore,
    RecordingReadinessInspector,
    RecordingAuthenticator,
    RecordingExecutorFactory,
    RecordingOwnerLifecycle,
]:
    """Compose the facade over real durable services and recording boundaries."""

    store = SqliteJobStore(
        tmp_path / "jobs.sqlite3",
        admission_limits=_admission_limits(),
    )
    job_service = JobService(
        store=store,
        artifact_store=InMemoryPrivateArtifactStore(),
        notification_policy=DeliveryNotificationPolicy.disabled(),
    )
    request = valid_generation_request()
    submitted_job = job_service.submit(
        user_id="owner-123",
        idempotency_key="request-123",
        generation_request=request,
        admission_reservation=standard_admission_reservation(),
    )
    readiness = RecordingReadinessInspector()
    authenticator = RecordingAuthenticator()
    executor_factory = RecordingExecutorFactory(submitted_job)
    owner_lifecycle = RecordingOwnerLifecycle()
    application = Txt2CrsApplication(
        job_service=job_service,
        readiness_inspector=readiness,
        authenticator=authenticator,
        executor_factory=executor_factory,
        owner_lifecycle=owner_lifecycle,
        close_callbacks=(store.close,),
    )
    return (
        application,
        job_service,
        store,
        readiness,
        authenticator,
        executor_factory,
        owner_lifecycle,
    )


def test_facade_delegates_complete_public_job_lifecycle(tmp_path: Any) -> None:
    """Shell consumers need no private persistence or projection import."""

    (
        application,
        _job_service,
        _store,
        readiness,
        authenticator,
        executor_factory,
        owner_lifecycle,
    ) = _application(tmp_path)
    request = valid_generation_request()

    submitted = application.submit(
        user_id="owner-123",
        idempotency_key="request-123",
        generation_request=request,
        admission_reservation=standard_admission_reservation(),
    )
    recovered = application.recover(
        job_id=submitted.job_id,
        user_id="owner-123",
    )
    runnable = application.next_runnable()
    snapshot = application.get_public_job(
        job_id=submitted.job_id,
        user_id="owner-123",
    )
    runtime_readiness = application.inspect_readiness()
    auth_started = application.start_system_authentication()
    auth_status = application.get_system_authentication_status(refresh=True)
    auth_logout = application.logout_system_authentication()
    executor = application.create_executor(
        job_id=submitted.job_id,
        user_id="owner-123",
    )
    executed = executor.execute()
    purged = application.purge_owner(user_id="owner-123")

    assert recovered.job == submitted
    assert runnable is not None and runnable.job.job_id == submitted.job_id
    assert snapshot.job_id == submitted.job_id
    assert runtime_readiness.status is RuntimeReadinessStatus.ready
    assert auth_started.state is SystemAuthenticationState.waiting_for_user
    assert auth_status.state is SystemAuthenticationState.authenticated
    assert auth_logout.state is SystemAuthenticationState.signed_out
    assert executed == submitted
    assert len(executor_factory.created) == 1
    assert readiness.calls == 1
    assert authenticator.events[:3] == [
        "auth-start",
        "auth-status",
        "auth-logout",
    ]
    assert purged.deleted_job_count == 1
    assert purged.deleted_artifact_job_count == 1
    assert owner_lifecycle.calls == ["owner-123"]


def test_executor_is_bound_one_shot_and_close_requests_cancellation(
    tmp_path: Any,
) -> None:
    """One handle cannot be retargeted, replayed, or run after close."""

    application, *_rest = _application(tmp_path)
    runnable = application.next_runnable()
    assert runnable is not None
    executor = application.create_executor(
        job_id=runnable.job.job_id,
        user_id="owner-123",
    )

    executor.execute()

    with pytest.raises(ExecutorAlreadyUsedError, match="already been used"):
        executor.execute()
    executor.close()
    executor.close()
    assert executor.cancellation.is_cancelled is True
    assert executor.cancellation.reason is CancellationReason.application_shutdown


def test_executor_shutdown_request_is_non_blocking_and_close_still_joins(
    tmp_path: Any,
) -> None:
    """The supervisor can signal restart-safe interruption before a bounded join."""

    application, job_service, *_rest = _application(tmp_path)
    runnable = job_service.next_runnable()
    assert runnable is not None
    execution_entered = Event()
    release_execution = Event()
    executor = ApplicationExecutor(
        executor=BlockingGenerationExecutor(
            result=runnable.job,
            execution_entered=execution_entered,
            release_execution=release_execution,
        ),
        job_id=runnable.job.job_id,
        user_id=runnable.job.user_id,
        cancellation=CancellationToken(),
    )
    execution_thread = Thread(target=executor.execute)
    execution_thread.start()
    assert execution_entered.wait(timeout=2)

    executor.request_shutdown()

    assert executor.cancellation.is_cancelled is True
    assert executor.cancellation.reason is CancellationReason.application_shutdown
    assert execution_thread.is_alive() is True

    release_execution.set()
    executor.close()
    execution_thread.join(timeout=2)
    assert execution_thread.is_alive() is False
    application.close()


def test_closed_executor_is_not_retained_for_application_lifetime(
    tmp_path: Any,
) -> None:
    """Completed jobs must not accumulate whole executor graphs in the facade."""

    application, _service, _store, _readiness, _auth, factory, _owner = _application(
        tmp_path
    )
    runnable = application.next_runnable()
    assert runnable is not None
    executor = application.create_executor(
        job_id=runnable.job.job_id,
        user_id="owner-123",
    )
    executor.close()
    executor_reference = ref(executor)
    factory.created.clear()
    del executor
    gc.collect()

    assert executor_reference() is None
    application.close()


def test_owner_purge_cancels_and_waits_for_active_owner_executor(
    tmp_path: Any,
) -> None:
    """An active worker cannot recreate artifacts after purge reports success."""

    (
        original_application,
        job_service,
        _store,
        readiness,
        authenticator,
        _factory,
        _owner_lifecycle,
    ) = _application(tmp_path)
    runnable = job_service.next_runnable()
    assert runnable is not None
    execution_entered = Event()
    release_execution = Event()
    cancellation_observed = Event()
    purge_called = Event()
    application = Txt2CrsApplication(
        job_service=job_service,
        readiness_inspector=readiness,
        authenticator=authenticator,
        executor_factory=BlockingExecutorFactory(
            result=runnable.job,
            execution_entered=execution_entered,
            release_execution=release_execution,
            cancellation_observed=cancellation_observed,
        ),
        owner_lifecycle=ObservableOwnerLifecycle(purge_called),
        close_callbacks=(),
    )
    executor = application.create_executor(
        job_id=runnable.job.job_id,
        user_id="owner-123",
    )
    execution_thread = Thread(target=executor.execute)
    purge_thread = Thread(target=lambda: application.purge_owner(user_id="owner-123"))
    execution_thread.start()
    assert execution_entered.wait(timeout=2)
    purge_thread.start()

    cancellation_was_observed = cancellation_observed.wait(timeout=0.1)
    deletion_started_too_early = purge_called.is_set()
    release_execution.set()
    execution_thread.join(timeout=2)
    purge_thread.join(timeout=2)

    assert cancellation_was_observed is True
    assert deletion_started_too_early is False
    assert execution_thread.is_alive() is False
    assert purge_thread.is_alive() is False
    assert purge_called.is_set()
    application.close()
    original_application.close()


def test_application_close_is_reverse_order_idempotent_and_blocks_later_use(
    tmp_path: Any,
) -> None:
    """Facade close owns process services and rejects stale shell references."""

    (
        application,
        _job_service,
        _store,
        _readiness,
        authenticator,
        _executor_factory,
        _owner_lifecycle,
    ) = _application(tmp_path)

    runnable = application.next_runnable()
    assert runnable is not None
    executor = application.create_executor(
        job_id=runnable.job.job_id,
        user_id="owner-123",
    )

    application.close()
    application.close()

    assert authenticator.events == ["auth-close"]
    assert executor.cancellation.is_cancelled is True
    assert executor.cancellation.reason is CancellationReason.application_shutdown
    with pytest.raises(ApplicationClosedError, match="application is closed"):
        application.next_runnable()
    with pytest.raises(ApplicationClosedError, match="application is closed"):
        application.purge_owner(user_id="owner-123")


def test_application_close_attempts_every_resource_and_returns_safe_error(
    tmp_path: Any,
) -> None:
    """One cleanup failure cannot skip later process-owned resources."""

    (
        _application_value,
        job_service,
        store,
        _readiness,
        authenticator,
        executor_factory,
        owner_lifecycle,
    ) = _application(tmp_path)
    close_events: list[str] = []

    def fail_first_close() -> None:
        close_events.append("first")
        raise OSError("/private/cleanup/path")

    def close_second() -> None:
        close_events.append("second")
        store.close()

    application = Txt2CrsApplication(
        job_service=job_service,
        readiness_inspector=RecordingReadinessInspector(),
        authenticator=authenticator,
        executor_factory=executor_factory,
        owner_lifecycle=owner_lifecycle,
        close_callbacks=(fail_first_close, close_second),
    )

    with pytest.raises(ApplicationCloseError, match="failed to close") as error_info:
        application.close()

    assert close_events == ["first", "second"]
    assert "/private" not in str(error_info.value)
    assert error_info.value.__cause__ is None
    assert error_info.value.__context__ is None
    application.close()


def test_application_close_waits_for_an_admitted_facade_call(
    tmp_path: Any,
) -> None:
    """Store cleanup cannot race a call that passed the open-state check."""

    (
        original_application,
        job_service,
        _store,
        readiness,
        authenticator,
        executor_factory,
        owner_lifecycle,
    ) = _application(tmp_path)
    runnable = job_service.next_runnable()
    assert runnable is not None
    submit_entered = Event()
    release_submit = Event()
    close_completed = Event()
    application = Txt2CrsApplication(
        job_service=BlockingSubmitJobService(
            result=runnable.job,
            submit_entered=submit_entered,
            release_submit=release_submit,
        ),
        readiness_inspector=readiness,
        authenticator=authenticator,
        executor_factory=executor_factory,
        owner_lifecycle=owner_lifecycle,
        close_callbacks=(close_completed.set,),
    )

    submit_thread = Thread(
        target=lambda: application.submit(
            user_id="owner-123",
            idempotency_key="request-123",
            generation_request=valid_generation_request(),
            admission_reservation=standard_admission_reservation(),
        )
    )
    close_thread = Thread(target=application.close)
    submit_thread.start()
    assert submit_entered.wait(timeout=2)
    close_thread.start()

    assert close_completed.wait(timeout=0.1) is False

    release_submit.set()
    submit_thread.join(timeout=2)
    close_thread.join(timeout=2)
    assert submit_thread.is_alive() is False
    assert close_thread.is_alive() is False
    assert close_completed.is_set()
    original_application.close()


def test_artifact_stream_context_is_delegated_without_eager_read(
    tmp_path: Any,
) -> None:
    """The facade returns the package-owned context and never buffers bytes."""

    application, job_service, *_rest = _application(tmp_path)
    opened = False

    @contextmanager
    def recording_stream() -> Iterator[Iterator[bytes]]:
        nonlocal opened
        opened = True
        yield iter((b"one", b"two"))

    job_service.open_artifact = lambda **_kwargs: recording_stream()  # type: ignore[method-assign]
    artifact_context = application.open_artifact(
        job_id="job-123",
        user_id="owner-123",
        artifact_id="course_html",
    )

    assert opened is False
    with artifact_context as chunks:
        assert b"".join(chunks) == b"onetwo"
    assert opened is True
