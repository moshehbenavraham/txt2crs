"""Tests-first lifecycle and exclusivity for system device authentication."""

from threading import Event

import pytest
from txt2crs.application import (
    SystemAuthenticationError,
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
)

from app.services.txt2crs_authentication import (
    SystemAuthenticationBusyError,
    SystemAuthenticationClosedError,
    SystemAuthenticationCoordinator,
    SystemAuthenticationUnavailableError,
)
from app.services.txt2crs_runtime import RuntimeOwner, RuntimeOwnershipCoordinator


def _authentication_snapshot(
    state: SystemAuthenticationState,
) -> SystemAuthenticationSnapshot:
    """Return one package-shaped browser-safe authentication fixture."""

    is_waiting = state is SystemAuthenticationState.waiting_for_user
    return SystemAuthenticationSnapshot(
        state=state,
        verification_url=(
            "https://auth.openai.com/codex/device" if is_waiting else None
        ),
        user_code="ABCD-1234" if is_waiting else None,
        message=f"Authentication is {state.value}.",
    )


class RecordingAuthenticationApplication:
    """Small public-facade double with controllable terminal state."""

    def __init__(self) -> None:
        self.state = SystemAuthenticationState.signed_out
        self.start_calls = 0
        self.status_refreshes: list[bool] = []
        self.terminal_polled = Event()
        self.start_error: Exception | None = None

    def start_system_authentication(self) -> SystemAuthenticationSnapshot:
        """Start one challenge or raise one safe package error."""

        self.start_calls += 1
        if self.start_error is not None:
            raise self.start_error
        self.state = SystemAuthenticationState.waiting_for_user
        return _authentication_snapshot(self.state)

    def get_system_authentication_status(
        self,
        *,
        refresh: bool = False,
    ) -> SystemAuthenticationSnapshot:
        """Record whether a caller attempted a provider-backed refresh."""

        self.status_refreshes.append(refresh)
        if not refresh and self.state in {
            SystemAuthenticationState.authenticated,
            SystemAuthenticationState.failed,
        }:
            self.terminal_polled.set()
        return _authentication_snapshot(self.state)


def _coordinator(
    application: RecordingAuthenticationApplication | None,
    ownership: RuntimeOwnershipCoordinator | None = None,
) -> SystemAuthenticationCoordinator:
    """Build one fast finite coordinator for deterministic thread tests."""

    return SystemAuthenticationCoordinator(
        application=application,
        runtime_ownership=ownership or RuntimeOwnershipCoordinator(),
        monitor_poll_seconds=0.01,
        shutdown_timeout_seconds=1,
    )


def test_startup_refreshes_once_and_snapshot_never_calls_package() -> None:
    """The lifespan owns persisted-account refresh; HTTP reads copy cache."""

    application = RecordingAuthenticationApplication()
    coordinator = _coordinator(application)

    coordinator.start()
    first = coordinator.snapshot()
    second = coordinator.snapshot()

    assert first == second
    assert application.status_refreshes == [True]
    coordinator.close()


def test_start_before_lifecycle_is_rejected_without_acquiring_runtime() -> None:
    """A partial-startup service cannot strand a lease without its monitor."""

    application = RecordingAuthenticationApplication()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(application, ownership)

    with pytest.raises(SystemAuthenticationUnavailableError):
        coordinator.start_authentication()

    assert application.start_calls == 0
    assert ownership.snapshot().is_available is True
    coordinator.close()


def test_busy_initial_refresh_publishes_safe_failed_state() -> None:
    """Contention cannot masquerade as a confirmed signed-out account."""

    application = RecordingAuthenticationApplication()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(application, ownership)

    with ownership.acquire(RuntimeOwner.execution):
        coordinator.start()
        assert coordinator.snapshot().state is SystemAuthenticationState.failed
        assert application.status_refreshes == []

    coordinator.close()


def test_startup_retains_lease_for_an_existing_waiting_attempt() -> None:
    """A coordinator replacement cannot overlap a package ceremony in memory."""

    application = RecordingAuthenticationApplication()
    application.state = SystemAuthenticationState.waiting_for_user
    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(application, ownership)

    coordinator.start()

    assert ownership.snapshot().owner is RuntimeOwner.authentication
    application.state = SystemAuthenticationState.failed
    assert application.terminal_polled.wait(timeout=1)
    assert ownership.snapshot().is_available is True
    coordinator.close()


def test_waiting_attempt_replays_and_holds_runtime_until_terminal() -> None:
    """The POST lifetime cannot release the app-server's shared lease."""

    application = RecordingAuthenticationApplication()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(application, ownership)
    coordinator.start()

    first = coordinator.start_authentication()
    replay = coordinator.start_authentication()

    assert first.state is SystemAuthenticationState.waiting_for_user
    assert replay == first
    assert application.start_calls == 1
    assert ownership.snapshot().owner is RuntimeOwner.authentication
    assert ownership.try_acquire(RuntimeOwner.execution) is None

    application.state = SystemAuthenticationState.authenticated
    assert application.terminal_polled.wait(timeout=1)
    assert ownership.snapshot().is_available is True
    assert coordinator.snapshot().state is SystemAuthenticationState.authenticated
    coordinator.close()


def test_busy_start_fails_without_package_call_or_blocking() -> None:
    """Execution ownership rejects device start through a finite safe error."""

    application = RecordingAuthenticationApplication()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(application, ownership)
    coordinator.start()

    with ownership.acquire(RuntimeOwner.execution):
        with pytest.raises(SystemAuthenticationBusyError):
            coordinator.start_authentication()

    assert application.start_calls == 0
    coordinator.close()


def test_start_failure_releases_lease_and_caches_safe_failed_state() -> None:
    """Package details cannot leave authentication ownership stuck."""

    application = RecordingAuthenticationApplication()
    application.start_error = SystemAuthenticationError(
        "Bearer private-provider-response"
    )
    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(application, ownership)
    coordinator.start()

    with pytest.raises(SystemAuthenticationError):
        coordinator.start_authentication()

    assert ownership.snapshot().is_available is True
    assert coordinator.snapshot().state is SystemAuthenticationState.failed
    assert "private-provider-response" not in coordinator.snapshot().model_dump_json()
    coordinator.close()


def test_active_close_releases_runtime_and_is_idempotent() -> None:
    """Shutdown stops monitoring and releases the retained lease exactly once."""

    application = RecordingAuthenticationApplication()
    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(application, ownership)
    coordinator.start()
    coordinator.start_authentication()

    coordinator.close()
    coordinator.close()

    assert ownership.snapshot().is_available is True
    with pytest.raises(SystemAuthenticationClosedError):
        coordinator.start_authentication()


def test_unconfigured_start_is_safe_and_never_acquires_runtime() -> None:
    """OpenAPI/setup state remains loadable without a composed facade."""

    ownership = RuntimeOwnershipCoordinator()
    coordinator = _coordinator(None, ownership)
    coordinator.start()

    with pytest.raises(SystemAuthenticationUnavailableError):
        coordinator.start_authentication()

    assert ownership.snapshot().is_available is True
    assert "Complete system setup" in coordinator.snapshot().message
    coordinator.close()
