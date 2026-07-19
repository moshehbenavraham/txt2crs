"""Tests-first contract for one shared provider-runtime owner."""

from app.services.txt2crs_runtime import (
    RuntimeOwner,
    RuntimeOwnershipCoordinator,
)


def test_runtime_ownership_is_exclusive_and_released_by_context() -> None:
    """Readiness, authentication, and execution cannot overlap."""

    coordinator = RuntimeOwnershipCoordinator()

    with coordinator.acquire(RuntimeOwner.execution):
        snapshot = coordinator.snapshot()
        assert snapshot.owner is RuntimeOwner.execution
        assert snapshot.is_available is False
        assert coordinator.try_acquire(RuntimeOwner.readiness) is None
        assert coordinator.try_acquire(RuntimeOwner.authentication) is None

    released_snapshot = coordinator.snapshot()
    assert released_snapshot.owner is None
    assert released_snapshot.is_available is True


def test_runtime_owner_snapshot_is_content_free_and_close_is_idempotent() -> None:
    """The coordinator never retains a job, user, thread, or provider identity."""

    coordinator = RuntimeOwnershipCoordinator()

    snapshot_fields = coordinator.snapshot().__dataclass_fields__
    assert set(snapshot_fields) == {
        "schema_version",
        "owner",
        "is_available",
        "is_closed",
    }

    coordinator.close()
    coordinator.close()
    assert coordinator.try_acquire(RuntimeOwner.readiness) is None
    assert coordinator.snapshot().is_closed is True
