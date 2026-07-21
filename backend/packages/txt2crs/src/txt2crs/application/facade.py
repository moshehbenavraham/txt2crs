# SPDX-License-Identifier: MIT-0

"""Framework-independent public facade over authoritative engine services."""

from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from threading import Condition, RLock
from typing import Protocol
from weakref import WeakSet

from txt2crs.ai.runtime import CancellationToken
from txt2crs.ai.runtime_status import RuntimeReadiness
from txt2crs.ai.system_authentication import SystemAuthenticationSnapshot
from txt2crs.application.owner_lifecycle import OwnerPurgeResult
from txt2crs.application.readiness import ApplicationReadiness
from txt2crs.jobs.artifact_queries import ArtifactManifest
from txt2crs.jobs.models import JobRecord, ResumeState
from txt2crs.jobs.preparation import PreparationPolicyError
from txt2crs.jobs.public_queries import PublicJobPage, PublicJobSnapshot
from txt2crs.jobs.quota import AdmissionCapacity, AdmissionReservation
from txt2crs.jobs.requests import GenerationRequest
from txt2crs.jobs.service import JobService
from txt2crs.security.policy import PolicyDecision, PolicyOutcome


class ApplicationClosedError(RuntimeError):
    """A caller retained an application or executor after explicit close."""


class ApplicationCloseError(RuntimeError):
    """One or more owned application resources failed to close safely."""


class ExecutorAlreadyUsedError(RuntimeError):
    """A one-shot job executor handle was invoked more than once."""


class RuntimeReadinessInspector(Protocol):
    """Safe readiness operation exposed through the facade."""

    def inspect_readiness(self) -> RuntimeReadiness:
        """Return one browser-safe runtime projection."""


class ApplicationReadinessInspector(Protocol):
    """Complete safe readiness operation exposed through the facade."""

    def inspect_readiness(self) -> ApplicationReadiness:
        """Return one package-owned aggregate projection."""


class SubmissionPreflightEvaluator(Protocol):
    """Evaluate the package's synchronous policy before a durable write."""

    def evaluate_preflight(
        self,
        generation_request: GenerationRequest,
    ) -> PolicyDecision:
        """Return one safe package-owned submission decision."""


class SystemAuthenticator(Protocol):
    """Framework-neutral authentication operations used by future routes."""

    def start_device_code_login(self) -> SystemAuthenticationSnapshot:
        """Start or replay the current device-code ceremony."""

    def current_status(
        self,
        *,
        refresh: bool = False,
    ) -> SystemAuthenticationSnapshot:
        """Return one browser-safe authentication snapshot."""

    def logout(self) -> SystemAuthenticationSnapshot:
        """Clear the dedicated system authentication state."""

    def close(self) -> None:
        """Release any active authentication client/thread."""


class PublicExecutorFactory(Protocol):
    """Create a fresh owner/job-bound executor from exact stored request data."""

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
        generation_request: GenerationRequest,
    ) -> "ApplicationExecutor":
        """Return one fresh one-shot handle."""


class BoundGenerationExecutor(Protocol):
    """Narrow executor behavior retained by one public handle."""

    def execute(
        self,
        *,
        job_id: str,
        user_id: str,
        cancellation: CancellationToken,
    ) -> JobRecord:
        """Execute or resume exactly one owner-scoped job."""


class OwnerLifecycle(Protocol):
    """Owner-wide engine erasure exposed by the facade."""

    def purge_owner(self, *, user_id: str) -> OwnerPurgeResult:
        """Return success only after every engine store succeeds."""


class ApplicationExecutor:
    """Bind one engine executor to one owner/job and cancellation token."""

    def __init__(
        self,
        *,
        executor: BoundGenerationExecutor,
        job_id: str,
        user_id: str,
        cancellation: CancellationToken,
    ) -> None:
        self._executor = executor
        self._job_id = job_id
        self._user_id = user_id
        self._cancellation = cancellation
        self._lock = RLock()
        self._condition = Condition(self._lock)
        self._used = False
        self._executing = False
        self._closed = False

    @property
    def cancellation(self) -> CancellationToken:
        """Expose only the handle-owned token for worker cancellation wiring."""

        return self._cancellation

    def execute(self) -> JobRecord:
        """Execute the bound job exactly once."""

        with self._condition:
            if self._closed:
                raise ApplicationClosedError("The application executor is closed.")
            if self._used:
                raise ExecutorAlreadyUsedError(
                    "The application executor has already been used."
                )
            # Reserve the one attempt before releasing the lock. Concurrent
            # worker calls cannot both enter the underlying executor.
            self._used = True
            self._executing = True
        try:
            return self._executor.execute(
                job_id=self._job_id,
                user_id=self._user_id,
                cancellation=self._cancellation,
            )
        finally:
            with self._condition:
                self._executing = False
                self._condition.notify_all()

    def close(self) -> None:
        """Request restart-safe interruption, wait, and close idempotently."""

        with self._condition:
            if not self._closed:
                self._closed = True
                self._cancellation.interrupt_for_shutdown()
            # Cancellation is cooperative, so the configured provider's finite
            # timeouts bound this wait if it is currently inside external work.
            while self._executing:
                self._condition.wait()

    def request_shutdown(self) -> None:
        """
        Signal process interruption without waiting for provider cooperation.

        The shell supervisor first gives active work a finite drain interval.
        If it expires, this non-blocking method lets the worker leave its last
        accepted checkpoint runnable while FastAPI continues reverse cleanup.
        A later ``close`` still joins the execution before resources disappear.
        """
        with self._condition:
            if self._closed:
                return
            self._closed = True
            self._cancellation.interrupt_for_shutdown()

    def _is_bound_to_owner(self, *, user_id: str) -> bool:
        """Return whether this immutable handle belongs to one owner."""

        return self._user_id == user_id

    def __enter__(self) -> "ApplicationExecutor":
        """Return the open one-shot handle."""

        with self._lock:
            if self._closed:
                raise ApplicationClosedError("The application executor is closed.")
        return self

    def __exit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception_value: BaseException | None,
        _traceback: object | None,
    ) -> None:
        """Always request cancellation when leaving the worker-owned context."""

        self.close()


class Txt2CrsApplication:
    """One documented shell-facing boundary for the complete engine lifecycle."""

    def __init__(
        self,
        *,
        job_service: JobService,
        readiness_inspector: RuntimeReadinessInspector,
        authenticator: SystemAuthenticator,
        executor_factory: PublicExecutorFactory,
        owner_lifecycle: OwnerLifecycle,
        preflight_evaluator: SubmissionPreflightEvaluator,
        admission_reservation: AdmissionReservation,
        close_callbacks: tuple[Callable[[], None], ...],
        application_readiness_inspector: ApplicationReadinessInspector | None = None,
    ) -> None:
        self._job_service = job_service
        self._readiness_inspector = readiness_inspector
        self._authenticator = authenticator
        self._executor_factory = executor_factory
        self._owner_lifecycle = owner_lifecycle
        self._preflight_evaluator = preflight_evaluator
        self._admission_reservation = admission_reservation
        self._close_callbacks = close_callbacks
        self._application_readiness_inspector = application_readiness_inspector
        self._lock = RLock()
        self._closed = False
        # A running worker or shell reference keeps its handle alive. Weak
        # tracking lets completed handles and their potentially large provider
        # graphs be collected instead of accumulating until process shutdown.
        self._executor_handles: WeakSet[ApplicationExecutor] = WeakSet()

    def _require_open(self) -> None:
        """Reject calls made through a stale application reference."""

        with self._lock:
            if self._closed:
                raise ApplicationClosedError("The txt2crs application is closed.")

    def submit(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        generation_request: GenerationRequest,
        admission_reservation: AdmissionReservation,
    ) -> JobRecord:
        """Apply package policy, then durably submit or replay one exact request.

        Preflight and persistence stay inside the same facade lock. This makes
        the ordering an invariant for every shell consumer and prevents
        application cleanup from racing between the policy decision and write.
        """

        with self._lock:
            self._require_open()
            policy_decision = self._preflight_evaluator.evaluate_preflight(
                generation_request
            )
            if policy_decision.outcome is not PolicyOutcome.allowed:
                raise PreparationPolicyError(decision=policy_decision)
            return self._job_service.submit(
                user_id=user_id,
                idempotency_key=idempotency_key,
                generation_request=generation_request,
                admission_reservation=admission_reservation,
            )

    def default_admission_reservation(self) -> AdmissionReservation:
        """Return the factory-reviewed finite reservation for new work."""

        with self._lock:
            self._require_open()
            return self._admission_reservation

    def get_admission_capacity(self, *, user_id: str) -> AdmissionCapacity:
        """Return one owner-scoped view of remaining generation capacity."""

        with self._lock:
            self._require_open()
            return self._job_service.inspect_admission_capacity(
                user_id=user_id,
                reservation=self._admission_reservation,
            )

    def recover(self, *, job_id: str, user_id: str) -> ResumeState:
        """Return one owner-authorized exact recovery snapshot."""

        with self._lock:
            self._require_open()
            return self._job_service.resume(job_id=job_id, user_id=user_id)

    def next_runnable(self) -> ResumeState | None:
        """Return the next deterministic recovery-first worker item."""

        with self._lock:
            self._require_open()
            return self._job_service.next_runnable()

    def record_runtime_activity(self, *, job_id: str, user_id: str) -> None:
        """Persist content-free worker liveness through the package boundary."""

        with self._lock:
            self._require_open()
            self._job_service.record_runtime_activity(
                job_id=job_id,
                user_id=user_id,
            )

    def get_public_job(self, *, job_id: str, user_id: str) -> PublicJobSnapshot:
        """Return one path-free public job projection."""

        with self._lock:
            self._require_open()
            return self._job_service.get_public_snapshot(
                job_id=job_id,
                user_id=user_id,
            )

    def list_public_jobs(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None = None,
    ) -> PublicJobPage:
        """Return one bounded owner-scoped course-library page."""

        with self._lock:
            self._require_open()
            return self._job_service.list_public_jobs(
                user_id=user_id,
                page_size=page_size,
                cursor=cursor,
            )

    def get_artifact_manifest(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> ArtifactManifest:
        """Return owner-scoped verified artifact metadata."""

        with self._lock:
            self._require_open()
            return self._job_service.get_artifact_manifest(
                job_id=job_id,
                user_id=user_id,
            )

    def open_artifact(
        self,
        *,
        job_id: str,
        user_id: str,
        artifact_id: str,
    ) -> AbstractContextManager[Iterator[bytes]]:
        """Return the existing verified one-descriptor stream context."""

        with self._lock:
            self._require_open()
            return self._job_service.open_artifact(
                job_id=job_id,
                user_id=user_id,
                artifact_id=artifact_id,
            )

    def inspect_readiness(self) -> RuntimeReadiness:
        """Probe and return only the package's safe readiness projection."""

        with self._lock:
            self._require_open()
            return self._readiness_inspector.inspect_readiness()

    def inspect_application_readiness(self) -> ApplicationReadiness:
        """Probe every package-owned dependency through one safe contract."""

        with self._lock:
            self._require_open()
            if self._application_readiness_inspector is not None:
                return self._application_readiness_inspector.inspect_readiness()

            # Compatibility callers that manually compose the facade retain a
            # truthful fail-closed aggregate until they supply the complete
            # inspector. Production factories always supply it.
            runtime = self._readiness_inspector.inspect_readiness()
            return ApplicationReadiness.create(
                configured_model_id="gpt-5.6-sol",
                enabled_input_modes=("prompt", "text"),
                runtime=runtime,
                research_ready=False,
                sqlite_ready=False,
                artifacts_ready=False,
                inputs_ready=False,
                admission_ready=False,
                warnings=["Complete application readiness is unavailable."],
                recovery_actions=["Use a package application factory."],
            )

    def start_system_authentication(self) -> SystemAuthenticationSnapshot:
        """Start or replay dedicated system device-code authentication."""

        with self._lock:
            self._require_open()
            return self._authenticator.start_device_code_login()

    def get_system_authentication_status(
        self,
        *,
        refresh: bool = False,
    ) -> SystemAuthenticationSnapshot:
        """Return the browser-safe authentication snapshot."""

        with self._lock:
            self._require_open()
            return self._authenticator.current_status(refresh=refresh)

    def logout_system_authentication(self) -> SystemAuthenticationSnapshot:
        """Clear the dedicated system account through the package boundary."""

        with self._lock:
            self._require_open()
            return self._authenticator.logout()

    def create_executor(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> ApplicationExecutor:
        """Build fresh job-scoped state from the exact stored request."""

        with self._lock:
            self._require_open()
            resume_state = self._job_service.resume(job_id=job_id, user_id=user_id)
            executor_handle = self._executor_factory.create_executor(
                job_id=job_id,
                user_id=user_id,
                generation_request=resume_state.request,
            )
            self._executor_handles.add(executor_handle)
            return executor_handle

    def purge_owner(self, *, user_id: str) -> OwnerPurgeResult:
        """Erase all engine-owned state for one owner."""

        with self._lock:
            self._require_open()
            owner_executor_handles = tuple(
                executor_handle
                for executor_handle in self._executor_handles
                if executor_handle._is_bound_to_owner(user_id=user_id)
            )
            # Stop and join owner work before artifacts are removed. Without
            # this barrier, an executor already in delivery could recreate its
            # artifact directory after a successful owner purge.
            for executor_handle in owner_executor_handles:
                executor_handle.close()
            return self._owner_lifecycle.purge_owner(user_id=user_id)

    def close(self) -> None:
        """Close authentication and process services exactly once."""

        # Keep this lock through cleanup. A facade call that already acquired
        # the lock completes before close begins, while concurrent calls and
        # duplicate close attempts wait until every resource is settled.
        with self._lock:
            if self._closed:
                return
            self._closed = True
            executor_handles = tuple(self._executor_handles)
            self._executor_handles.clear()

            cleanup_failed = False
            for executor_handle in executor_handles:
                try:
                    executor_handle.close()
                except Exception:
                    cleanup_failed = True
            # Authentication owns a possible background thread/app-server and
            # must stop before the durable store closes underneath methods.
            try:
                self._authenticator.close()
            except Exception:
                cleanup_failed = True
            for close_callback in self._close_callbacks:
                try:
                    close_callback()
                except Exception:
                    cleanup_failed = True
            if cleanup_failed:
                raise ApplicationCloseError(
                    "One or more txt2crs resources failed to close."
                )

    def __enter__(self) -> "Txt2CrsApplication":
        """Return the open application."""

        self._require_open()
        return self

    def __exit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception_value: BaseException | None,
        _traceback: object | None,
    ) -> None:
        """Release the application composition root."""

        self.close()
