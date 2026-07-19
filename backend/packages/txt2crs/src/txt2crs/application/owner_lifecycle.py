# SPDX-License-Identifier: MIT-0

"""Retry-safe coordination for one owner's complete engine erasure."""

from threading import RLock
from typing import Protocol

from pydantic import ConfigDict, Field

from txt2crs.domain.models import Identifier, SchemaVersion, StrictContract


class OwnerPurgeError(RuntimeError):
    """Owner erasure failed without exposing private storage details."""


class OwnerPurgeResult(StrictContract):
    """Counts returned only after artifacts and durable rows both succeed."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    schema_version: SchemaVersion
    deleted_job_count: int = Field(ge=0)
    deleted_artifact_job_count: int = Field(ge=0)


class OwnerRecordStore(Protocol):
    """Durable parent-row deletion needed by the purge coordinator."""

    def purge_owner(self, *, user_id: str) -> int:
        """Delete all owner jobs and return the number of parent rows."""


class OwnerArtifactStore(Protocol):
    """Private artifact-tree deletion needed by the purge coordinator."""

    def purge_owner(self, *, user_id: str) -> int:
        """Delete all owner artifact jobs and return their count."""


class _OwnerIdentity(StrictContract):
    """Validate an owner without inventing a second identifier grammar."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    user_id: Identifier


class OwnerPurgeCoordinator:
    """Delete artifacts first, then atomically delete durable parent rows.

    A filesystem failure leaves the SQLite job list intact so a caller still
    has durable retry identity. If SQLite fails after artifact deletion, the
    artifact operation is idempotent and a retry can finish the database side.
    Cross-store atomicity is impossible, so success is returned only after both
    operations have completed in the documented order.
    """

    def __init__(
        self,
        *,
        artifact_store: OwnerArtifactStore,
        owner_store: OwnerRecordStore,
    ) -> None:
        self._artifact_store = artifact_store
        self._owner_store = owner_store
        # Cross-store work cannot be one transaction. Serializing this small
        # application-scoped coordinator prevents two deletion requests from
        # interleaving their artifact and database phases.
        self._lock = RLock()

    def purge_owner(self, *, user_id: str) -> OwnerPurgeResult:
        """Erase one valid owner or raise one stable context-free error."""

        with self._lock:
            return self._purge_owner_serially(user_id=user_id)

    def _purge_owner_serially(self, *, user_id: str) -> OwnerPurgeResult:
        """Perform both store phases while the coordinator lock is held."""

        normalized_identity: _OwnerIdentity | None = None
        try:
            normalized_identity = _OwnerIdentity(user_id=user_id)
        except ValueError:
            # Raise after leaving the handler so invalid caller text cannot be
            # retained in validation context.
            pass
        if normalized_identity is None:
            raise OwnerPurgeError("The owner identity is invalid.")

        artifact_job_count: int | None = None
        try:
            artifact_job_count = self._artifact_store.purge_owner(
                user_id=normalized_identity.user_id
            )
        except Exception:
            # Translate outside the handler to discard paths or provider
            # details retained by the underlying exception.
            pass
        if not _is_valid_deletion_count(artifact_job_count):
            raise OwnerPurgeError("The owner purge could not be completed.")

        deleted_job_count: int | None = None
        try:
            deleted_job_count = self._owner_store.purge_owner(
                user_id=normalized_identity.user_id
            )
        except Exception:
            pass
        if not _is_valid_deletion_count(deleted_job_count):
            raise OwnerPurgeError("The owner purge could not be completed.")

        # The explicit guards above narrow runtime values supplied by
        # structurally typed stores, including third-party implementations.
        assert artifact_job_count is not None
        assert deleted_job_count is not None
        return OwnerPurgeResult(
            schema_version="1.0",
            deleted_job_count=deleted_job_count,
            deleted_artifact_job_count=artifact_job_count,
        )


def _is_valid_deletion_count(deleted_count: object) -> bool:
    """Accept only real non-negative integers, never booleans or sentinels."""

    return (
        isinstance(deleted_count, int)
        and not isinstance(deleted_count, bool)
        and deleted_count >= 0
    )
