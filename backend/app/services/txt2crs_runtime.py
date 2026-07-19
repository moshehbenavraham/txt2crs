"""Single-process ownership arbitration for Codex app-server work."""

from dataclasses import dataclass
from enum import StrEnum
from threading import Condition, RLock
from types import TracebackType

RUNTIME_OWNERSHIP_SCHEMA_VERSION = "1.0"


class RuntimeOwner(StrEnum):
    """Finite owners allowed to launch or interact with provider runtime."""

    readiness = "readiness"
    authentication = "authentication"
    execution = "execution"


class RuntimeOwnershipClosedError(RuntimeError):
    """Runtime ownership was requested after application shutdown."""


@dataclass(frozen=True, slots=True)
class RuntimeOwnershipSnapshot:
    """Content-free state safe for readiness composition."""

    schema_version: str
    owner: RuntimeOwner | None
    is_available: bool
    is_closed: bool


class RuntimeOwnershipLease:
    """One exactly-once release handle returned by the coordinator."""

    def __init__(
        self,
        *,
        coordinator: RuntimeOwnershipCoordinator,
        owner: RuntimeOwner,
    ) -> None:
        self._coordinator = coordinator
        self._owner = owner
        self._is_released = False

    def release(self) -> None:
        """Release once so nested cleanup paths remain harmless."""

        if self._is_released:
            return
        self._is_released = True
        self._coordinator._release(self._owner)

    def __enter__(self) -> RuntimeOwnershipLease:
        """Return this already-acquired lease."""

        return self

    def __exit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """Always release ownership on scope exit."""

        self.release()


class RuntimeOwnershipCoordinator:
    """
    Serialize readiness, authentication, and execution provider ownership.

    The lock contains no job or user identity. It answers only which finite
    operation class currently owns the one allowed Codex app-server graph.
    """

    def __init__(self) -> None:
        self._condition = Condition(RLock())
        self._owner: RuntimeOwner | None = None
        self._is_closed = False

    def acquire(self, owner: RuntimeOwner) -> RuntimeOwnershipLease:
        """Wait until the runtime is free, then return one release handle."""

        with self._condition:
            while self._owner is not None and not self._is_closed:
                self._condition.wait()
            if self._is_closed:
                raise RuntimeOwnershipClosedError("Runtime ownership is closed.")
            self._owner = owner
            return RuntimeOwnershipLease(coordinator=self, owner=owner)

    def try_acquire(
        self,
        owner: RuntimeOwner,
    ) -> RuntimeOwnershipLease | None:
        """Acquire immediately or return ``None`` without blocking."""

        with self._condition:
            if self._is_closed or self._owner is not None:
                return None
            self._owner = owner
            return RuntimeOwnershipLease(coordinator=self, owner=owner)

    def snapshot(self) -> RuntimeOwnershipSnapshot:
        """Return a detached finite projection without runtime identities."""

        with self._condition:
            return RuntimeOwnershipSnapshot(
                schema_version=RUNTIME_OWNERSHIP_SCHEMA_VERSION,
                owner=self._owner,
                is_available=self._owner is None and not self._is_closed,
                is_closed=self._is_closed,
            )

    def close(self) -> None:
        """Reject future acquisitions and wake blocked callers idempotently."""

        with self._condition:
            if self._is_closed:
                return
            self._is_closed = True
            self._condition.notify_all()

    def _release(self, owner: RuntimeOwner) -> None:
        """Release only the exact finite owner that received the lease."""

        with self._condition:
            if self._owner is not owner:
                return
            self._owner = None
            self._condition.notify_all()


__all__ = [
    "RuntimeOwner",
    "RuntimeOwnershipClosedError",
    "RuntimeOwnershipCoordinator",
    "RuntimeOwnershipLease",
    "RuntimeOwnershipSnapshot",
]
