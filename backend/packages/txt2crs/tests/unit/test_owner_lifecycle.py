# SPDX-License-Identifier: MIT-0

"""Tests-first owner-wide erasure across artifacts and durable job state."""

from dataclasses import dataclass

import pytest
from pydantic import ValidationError

from txt2crs.application import (
    OwnerPurgeCoordinator,
    OwnerPurgeError,
    OwnerPurgeResult,
)


@dataclass(slots=True)
class RecordingOwnerStore:
    """Record the SQLite-side purge without exposing any SQL detail."""

    events: list[str]
    deleted_jobs: int = 2
    failure: Exception | None = None

    def purge_owner(self, *, user_id: str) -> int:
        """Return the configured deletion count or fail deterministically."""

        assert user_id == "owner-123"
        self.events.append("database")
        if self.failure is not None:
            raise self.failure
        return self.deleted_jobs


@dataclass(slots=True)
class RecordingOwnerArtifactStore:
    """Record artifact purge ordering and deterministic failures."""

    events: list[str]
    deleted_artifact_jobs: int = 1
    failure: Exception | None = None

    def purge_owner(self, *, user_id: str) -> int:
        """Return the configured deletion count or fail deterministically."""

        assert user_id == "owner-123"
        self.events.append("artifacts")
        if self.failure is not None:
            raise self.failure
        return self.deleted_artifact_jobs


def test_owner_purge_removes_artifacts_before_database_and_returns_counts() -> None:
    """Database identity remains available until artifact deletion succeeds."""

    events: list[str] = []
    coordinator = OwnerPurgeCoordinator(
        artifact_store=RecordingOwnerArtifactStore(events),
        owner_store=RecordingOwnerStore(events),
    )

    result = coordinator.purge_owner(user_id="owner-123")

    assert result == OwnerPurgeResult(
        schema_version="1.0",
        deleted_job_count=2,
        deleted_artifact_job_count=1,
    )
    assert events == ["artifacts", "database"]


def test_artifact_failure_prevents_database_deletion_and_is_context_free() -> None:
    """A partial filesystem failure cannot erase the durable retry identity."""

    events: list[str] = []
    coordinator = OwnerPurgeCoordinator(
        artifact_store=RecordingOwnerArtifactStore(
            events,
            failure=OSError("/private/owners/hash leaked"),
        ),
        owner_store=RecordingOwnerStore(events),
    )

    with pytest.raises(OwnerPurgeError, match="could not be completed") as error_info:
        coordinator.purge_owner(user_id="owner-123")

    assert events == ["artifacts"]
    assert "/private" not in str(error_info.value)
    assert error_info.value.__cause__ is None
    assert error_info.value.__context__ is None


def test_database_failure_after_artifact_success_is_reported_and_retryable() -> None:
    """A retry may safely observe an already-empty artifact owner tree."""

    events: list[str] = []
    owner_store = RecordingOwnerStore(
        events,
        failure=RuntimeError("SELECT private_state"),
    )
    artifact_store = RecordingOwnerArtifactStore(events)
    coordinator = OwnerPurgeCoordinator(
        artifact_store=artifact_store,
        owner_store=owner_store,
    )

    with pytest.raises(OwnerPurgeError, match="could not be completed"):
        coordinator.purge_owner(user_id="owner-123")

    owner_store.failure = None
    artifact_store.deleted_artifact_jobs = 0
    result = coordinator.purge_owner(user_id="owner-123")

    assert events == ["artifacts", "database", "artifacts", "database"]
    assert result.deleted_job_count == 2
    assert result.deleted_artifact_job_count == 0


def test_already_purged_owner_is_an_idempotent_success() -> None:
    """Repeated account-deletion coordination receives one explicit success."""

    events: list[str] = []
    coordinator = OwnerPurgeCoordinator(
        artifact_store=RecordingOwnerArtifactStore(
            events,
            deleted_artifact_jobs=0,
        ),
        owner_store=RecordingOwnerStore(events, deleted_jobs=0),
    )

    result = coordinator.purge_owner(user_id="owner-123")

    assert result.deleted_job_count == 0
    assert result.deleted_artifact_job_count == 0
    assert events == ["artifacts", "database"]


def test_owner_purge_result_rejects_impossible_negative_counts() -> None:
    """A faulty store cannot publish a nonsensical successful purge result."""

    with pytest.raises(ValidationError):
        OwnerPurgeResult(
            schema_version="1.0",
            deleted_job_count=-1,
            deleted_artifact_job_count=0,
        )


def test_owner_purge_translates_impossible_store_counts() -> None:
    """A faulty storage implementation still produces the stable purge error."""

    coordinator = OwnerPurgeCoordinator(
        artifact_store=RecordingOwnerArtifactStore(
            [],
            deleted_artifact_jobs=-1,
        ),
        owner_store=RecordingOwnerStore([]),
    )

    with pytest.raises(OwnerPurgeError, match="could not be completed"):
        coordinator.purge_owner(user_id="owner-123")


@pytest.mark.parametrize("invalid_owner_id", ["", " ", "a" * 256, "../owner"])
def test_owner_purge_rejects_invalid_identifiers_before_either_store(
    invalid_owner_id: str,
) -> None:
    """Unsafe owner identity never reaches a filesystem or SQL operation."""

    events: list[str] = []
    coordinator = OwnerPurgeCoordinator(
        artifact_store=RecordingOwnerArtifactStore(events),
        owner_store=RecordingOwnerStore(events),
    )

    with pytest.raises(OwnerPurgeError, match="identity is invalid"):
        coordinator.purge_owner(user_id=invalid_owner_id)

    assert events == []
