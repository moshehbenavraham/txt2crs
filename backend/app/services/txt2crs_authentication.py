"""Lifecycle-owned cache and runtime lease for system device authentication."""

from enum import StrEnum
from threading import Event, RLock, Thread
from typing import Protocol

from txt2crs.application import (
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
)

from app.core.logging import get_logger
from app.services.txt2crs_runtime import (
    RuntimeOwner,
    RuntimeOwnershipCoordinator,
    RuntimeOwnershipLease,
)

AUTHENTICATION_MONITOR_THREAD_NAME = "txt2crs-authentication-monitor"

logger = get_logger(__name__)


class SystemAuthenticationFailureCode(StrEnum):
    """Finite internal reasons safe for structured operational events."""

    unavailable = "unavailable"
    runtime_busy = "runtime_busy"
    package_failed = "package_failed"
    monitor_failed = "monitor_failed"
    shutdown_timeout = "shutdown_timeout"


class SystemAuthenticationBusyError(RuntimeError):
    """A job or readiness refresh currently owns the provider runtime."""


class SystemAuthenticationUnavailableError(RuntimeError):
    """The configured application/authentication service is unavailable."""


class SystemAuthenticationClosedError(RuntimeError):
    """A stale caller attempted to use a terminal coordinator."""


class SystemAuthenticationShutdownError(RuntimeError):
    """The finite in-memory monitor did not stop before its deadline."""


class SystemAuthenticationApplication(Protocol):
    """Narrow public facade surface used by the shell coordinator."""

    def start_system_authentication(self) -> SystemAuthenticationSnapshot:
        """Start or replay one package-owned device-code attempt."""

    def get_system_authentication_status(
        self,
        *,
        refresh: bool = False,
    ) -> SystemAuthenticationSnapshot:
        """Return the package's browser-safe authentication projection."""


def _safe_snapshot(
    *,
    state: SystemAuthenticationState,
    message: str,
) -> SystemAuthenticationSnapshot:
    """Build a challenge-free bounded state without provider detail."""

    return SystemAuthenticationSnapshot(
        state=state,
        verification_url=None,
        user_code=None,
        message=message,
    )


def _log_authentication_event(
    event_name: str,
    *,
    state: SystemAuthenticationState | None = None,
    reason_code: SystemAuthenticationFailureCode | None = None,
    level: str = "info",
) -> None:
    """Emit only finite state/reason dimensions and never mask real work."""

    extra: dict[str, object] = {}
    if state is not None:
        extra["state"] = state.value
    if reason_code is not None:
        extra["reason_code"] = reason_code.value
    try:
        log_method = logger.error if level == "error" else logger.info
        log_method(event_name, extra=extra)
    except BaseException:
        # Logging is an observer. It cannot leak a lease or replace the
        # package/start/shutdown operation that owns the real outcome.
        return


class SystemAuthenticationCoordinator:
    """
    Cache safe auth state and retain runtime ownership across background login.

    HTTP status handlers call only :meth:`snapshot`. The monitor is the sole
    shell caller that observes an already-active package ceremony, and it uses
    ``refresh=False`` so it never constructs another Codex app-server.
    """

    def __init__(
        self,
        *,
        application: SystemAuthenticationApplication | None,
        runtime_ownership: RuntimeOwnershipCoordinator,
        monitor_poll_seconds: float,
        shutdown_timeout_seconds: float,
    ) -> None:
        if monitor_poll_seconds <= 0 or monitor_poll_seconds > 10:
            raise ValueError("Authentication monitor poll must be 0-10 seconds.")
        if shutdown_timeout_seconds <= 0 or shutdown_timeout_seconds > 60:
            raise ValueError("Authentication shutdown must be 0-60 seconds.")

        self._application = application
        self._runtime_ownership = runtime_ownership
        self._monitor_poll_seconds = monitor_poll_seconds
        self._shutdown_timeout_seconds = shutdown_timeout_seconds
        self._lock = RLock()
        self._stop_requested = Event()
        self._wake_requested = Event()
        self._thread: Thread | None = None
        self._active_lease: RuntimeOwnershipLease | None = None
        self._is_started = False
        self._is_closed = False
        self._snapshot = _safe_snapshot(
            state=SystemAuthenticationState.signed_out,
            message="Dedicated ChatGPT subscription is not connected.",
        )

    def start(self) -> None:
        """Refresh persisted account state once, then start one finite monitor."""

        with self._lock:
            if self._is_closed:
                raise SystemAuthenticationClosedError(
                    "System authentication coordination is closed."
                )
            if self._is_started:
                return
            self._is_started = True
            application = self._application

        if application is None:
            with self._lock:
                self._snapshot = _safe_snapshot(
                    state=SystemAuthenticationState.signed_out,
                    message="Complete system setup before connecting ChatGPT.",
                )
            _log_authentication_event(
                "system.authentication_validated",
                state=SystemAuthenticationState.signed_out,
            )
            return

        initial_lease = self._runtime_ownership.try_acquire(RuntimeOwner.authentication)
        if initial_lease is not None:
            try:
                initial_snapshot = application.get_system_authentication_status(
                    refresh=True
                )
            except Exception:
                initial_snapshot = _safe_snapshot(
                    state=SystemAuthenticationState.failed,
                    message="System authentication status is unavailable.",
                )
            with self._lock:
                self._snapshot = initial_snapshot
                if initial_snapshot.state is SystemAuthenticationState.waiting_for_user:
                    self._active_lease = initial_lease
                    self._wake_requested.set()
                else:
                    initial_lease.release()
        else:
            with self._lock:
                self._snapshot = _safe_snapshot(
                    state=SystemAuthenticationState.failed,
                    message="System authentication status is temporarily unavailable.",
                )

        monitor_thread = Thread(
            target=self._run,
            name=AUTHENTICATION_MONITOR_THREAD_NAME,
            daemon=True,
        )
        with self._lock:
            self._thread = monitor_thread
        try:
            monitor_thread.start()
        except BaseException:
            with self._lock:
                self._thread = None
                self._is_started = False
                active_lease = self._active_lease
                self._active_lease = None
            if active_lease is not None:
                active_lease.release()
            raise
        _log_authentication_event(
            "system.authentication_validated",
            state=self.snapshot().state,
        )

    def snapshot(self) -> SystemAuthenticationSnapshot:
        """Return the immutable cached package projection without side effects."""

        with self._lock:
            return self._snapshot.model_copy(deep=True)

    def start_authentication(self) -> SystemAuthenticationSnapshot:
        """Start exactly one ceremony or replay the cached active/final state."""

        with self._lock:
            if self._is_closed:
                raise SystemAuthenticationClosedError(
                    "System authentication coordination is closed."
                )
            if not self._is_started:
                raise SystemAuthenticationUnavailableError(
                    "System authentication has not started."
                )
            application = self._application
            if application is None:
                raise SystemAuthenticationUnavailableError(
                    "System authentication is unavailable."
                )
            if self._active_lease is not None:
                return self._snapshot.model_copy(deep=True)
            if self._snapshot.state is SystemAuthenticationState.authenticated:
                return self._snapshot.model_copy(deep=True)

        authentication_lease = self._runtime_ownership.try_acquire(
            RuntimeOwner.authentication
        )
        if authentication_lease is None:
            raise SystemAuthenticationBusyError

        try:
            started_snapshot = application.start_system_authentication()
        except Exception:
            authentication_lease.release()
            with self._lock:
                self._snapshot = _safe_snapshot(
                    state=SystemAuthenticationState.failed,
                    message="System authentication could not be started.",
                )
            _log_authentication_event(
                "system.authentication_failed",
                reason_code=SystemAuthenticationFailureCode.package_failed,
                level="error",
            )
            raise

        with self._lock:
            if self._is_closed:
                authentication_lease.release()
                raise SystemAuthenticationClosedError(
                    "System authentication coordination is closed."
                )
            self._snapshot = started_snapshot
            if started_snapshot.state is SystemAuthenticationState.waiting_for_user:
                self._active_lease = authentication_lease
                self._wake_requested.set()
            else:
                authentication_lease.release()

        _log_authentication_event(
            "system.authentication_started",
            state=started_snapshot.state,
        )
        return started_snapshot.model_copy(deep=True)

    def close(self) -> None:
        """Stop monitoring and release any retained authentication lease."""

        with self._lock:
            if self._is_closed:
                return
            self._is_closed = True
            self._stop_requested.set()
            self._wake_requested.set()
            monitor_thread = self._thread
            self._thread = None
            active_lease = self._active_lease
            self._active_lease = None

        if active_lease is not None:
            active_lease.release()
        if monitor_thread is not None:
            monitor_thread.join(timeout=self._shutdown_timeout_seconds)
            if monitor_thread.is_alive():
                _log_authentication_event(
                    "system.authentication_shutdown_failed",
                    reason_code=SystemAuthenticationFailureCode.shutdown_timeout,
                    level="error",
                )
                raise SystemAuthenticationShutdownError(
                    "System authentication monitor did not stop in time."
                )
        _log_authentication_event("system.authentication_shutdown_completed")

    def _run(self) -> None:
        """Observe only an active package attempt until it becomes terminal."""

        while not self._stop_requested.is_set():
            self._wake_requested.wait(timeout=self._monitor_poll_seconds)
            self._wake_requested.clear()
            if self._stop_requested.is_set():
                return

            with self._lock:
                has_active_attempt = self._active_lease is not None
                application = self._application
            if not has_active_attempt or application is None:
                continue

            try:
                observed_snapshot = application.get_system_authentication_status(
                    refresh=False
                )
            except Exception:
                observed_snapshot = _safe_snapshot(
                    state=SystemAuthenticationState.failed,
                    message="System authentication failed. Start a new attempt.",
                )

            terminal_lease: RuntimeOwnershipLease | None = None
            with self._lock:
                if self._is_closed:
                    return
                self._snapshot = observed_snapshot
                if (
                    observed_snapshot.state
                    is not SystemAuthenticationState.waiting_for_user
                ):
                    terminal_lease = self._active_lease
                    self._active_lease = None
            if terminal_lease is not None:
                terminal_lease.release()
                event_name = (
                    "system.authentication_completed"
                    if observed_snapshot.state
                    is SystemAuthenticationState.authenticated
                    else "system.authentication_failed"
                )
                _log_authentication_event(
                    event_name,
                    state=observed_snapshot.state,
                )


__all__ = [
    "SystemAuthenticationBusyError",
    "SystemAuthenticationClosedError",
    "SystemAuthenticationCoordinator",
    "SystemAuthenticationFailureCode",
    "SystemAuthenticationShutdownError",
    "SystemAuthenticationUnavailableError",
]
