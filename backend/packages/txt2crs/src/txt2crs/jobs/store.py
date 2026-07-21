# SPDX-License-Identifier: MIT-0

"""SQLite job store with idempotency, tenant isolation, and CAS updates."""

import json
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from threading import RLock
from uuid import uuid4

from txt2crs.jobs.models import (
    JobCheckpoint,
    JobRecord,
    JobStatus,
    JobSubmissionIdentity,
    ResumeState,
    validate_status_transition,
)
from txt2crs.jobs.notifications import DeliveryNotificationState
from txt2crs.jobs.quota import (
    AdmissionLimits,
    AdmissionReservation,
    find_admission_limit_violation,
)
from txt2crs.jobs.request_store import (
    PersistedRequestError,
    insert_request_envelope,
    load_request_envelope,
    request_envelope_matches,
)
from txt2crs.jobs.requests import (
    GenerationRequest,
    serialize_generation_request,
)

_MIGRATION_RESOURCES = {
    1: "001_jobs.sql",
    2: "002_job_admissions.sql",
    3: "003_generation_requests.sql",
    4: "004_delivery_notifications.sql",
    5: "005_runtime_activity.sql",
}
_MIGRATION_VERSION = max(_MIGRATION_RESOURCES)


class JobStoreError(RuntimeError):
    """Base class for durable state failures."""


class JobNotFoundError(JobStoreError):
    """The job is missing or belongs to another tenant."""


class IdempotencyConflictError(JobStoreError):
    """An idempotency key was reused with a different complete request."""


class ConcurrencyConflictError(JobStoreError):
    """Another worker already advanced the expected job revision."""


class AdmissionQuotaExceededError(JobStoreError):
    """A new job would exceed a configured rolling resource allowance."""

    def __init__(self, resource_name: str, limit: int) -> None:
        self.resource_name = resource_name
        self.limit = limit
        super().__init__(f"The {resource_name} admission quota ({limit}) is exhausted.")


class AdmissionReservationMismatchError(JobStoreError):
    """A reservation is smaller than the immutable request run ceiling."""


class InvalidJobSubmissionError(JobStoreError):
    """An owner or idempotency identifier is invalid for durable storage."""


class JobRequestCompatibilityError(JobStoreError):
    """An accepted job lacks an exact request this engine can safely restore."""


class InvalidJobListRequestError(JobStoreError):
    """An owner library request has an invalid bound or continuation cursor."""


class SqliteJobStore:
    """Own the SQLite connection and apply every packaged schema migration."""

    def __init__(
        self,
        database_path: Path,
        *,
        admission_limits: AdmissionLimits,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(
            database_path,
            check_same_thread=False,
            isolation_level=None,
        )
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._lock = RLock()
        self._admission_limits = admission_limits
        self._clock = clock or (lambda: datetime.now(UTC))
        try:
            self._apply_migrations()
        except BaseException:
            # Construction has not yielded a usable store, so no caller can
            # close this connection. Release it here on migration errors,
            # cancellation, or process-shutdown exceptions.
            self._connection.close()
            raise

    @property
    def migration_version(self) -> int:
        """Return the highest applied local schema version."""

        with self._lock:
            row = self._connection.execute(
                "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
            ).fetchone()
        return int(row["version"])

    def probe_readiness(self) -> bool:
        """
        Verify current migrations and rollback-only SQLite writability.

        The probe takes SQLite's writer lock and exercises a temporary table,
        but always rolls the transaction back. Browser requests never call
        this method; the application readiness coordinator invokes it only on
        its bounded maintenance schedule.
        """

        with self._lock:
            if self.migration_version != _MIGRATION_VERSION:
                return False
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                self._connection.execute(
                    "CREATE TEMP TABLE txt2crs_readiness_probe(value INTEGER)"
                )
                self._connection.execute(
                    "INSERT INTO txt2crs_readiness_probe(value) VALUES (1)"
                )
                row = self._connection.execute(
                    "SELECT value FROM txt2crs_readiness_probe"
                ).fetchone()
            except Exception:
                self._connection.execute("ROLLBACK")
                return False
            self._connection.execute("ROLLBACK")
            return row is not None and int(row["value"]) == 1

    def has_admission_capacity(
        self,
        *,
        reservation: AdmissionReservation,
    ) -> bool:
        """Read whether one conservative reservation fits without writing."""

        with self._lock:
            violation = find_admission_limit_violation(
                connection=self._connection,
                # This fixed opaque value creates no row and represents a new
                # owner whose per-user rolling counters are empty.
                user_id="readiness-capacity-probe",
                reservation=reservation,
                limits=self._admission_limits,
                timestamp=self._now_text(),
            )
        return violation is None

    def _apply_migrations(self) -> None:
        """Apply each not-yet-recorded migration exactly once."""

        with self._lock:
            # Acquire SQLite's writer lock before reading applied versions.
            # Concurrent workers then serialize migration discovery instead of
            # both deciding that the same one-time ALTER is missing.
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                migration_table_exists = self._connection.execute(
                    """
                    SELECT 1
                    FROM sqlite_master
                    WHERE type = 'table' AND name = 'schema_migrations'
                    """
                ).fetchone()
                applied_versions = (
                    {
                        int(row["version"])
                        for row in self._connection.execute(
                            "SELECT version FROM schema_migrations"
                        ).fetchall()
                    }
                    if migration_table_exists is not None
                    else set()
                )
                for migration_version in sorted(_MIGRATION_RESOURCES):
                    if migration_version in applied_versions:
                        continue
                    migration_sql = (
                        files("txt2crs.jobs")
                        .joinpath(
                            "migrations",
                            _MIGRATION_RESOURCES[migration_version],
                        )
                        .read_text(encoding="utf-8")
                    )
                    # ``sqlite3.executescript`` implicitly commits before
                    # execution, which would separate ALTER statements from
                    # their version record. Execute complete statements inside
                    # this explicit transaction instead.
                    for migration_statement in _iter_sqlite_statements(migration_sql):
                        self._connection.execute(migration_statement)
                    self._connection.execute(
                        """
                        INSERT INTO schema_migrations(version, applied_at)
                        VALUES (?, ?)
                        """,
                        (migration_version, self._now_text()),
                    )
            except BaseException:
                self._connection.execute("ROLLBACK")
                raise
            self._connection.execute("COMMIT")

    def close(self) -> None:
        """Close the process-local SQLite connection."""

        with self._lock:
            self._connection.close()

    def _now_text(self) -> str:
        """Return an aware UTC timestamp from the injectable store clock."""

        current_time = self._clock()
        if current_time.tzinfo is None:
            raise ValueError("Job-store clock must return a timezone-aware time.")
        return current_time.astimezone(UTC).isoformat()

    def create_or_get_job(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        generation_request: GenerationRequest,
        admission_reservation: AdmissionReservation,
    ) -> JobRecord:
        """Atomically reserve resources and create or replay one exact job."""

        submission_identity = _normalize_submission_identity(
            user_id=user_id,
            idempotency_key=idempotency_key,
        )
        user_id = submission_identity.user_id
        idempotency_key = submission_identity.idempotency_key

        # Serialize before taking the write lock so invalid request metadata
        # cannot hold an SQLite transaction open. The request model recomputes
        # its hash here, catching mutation after construction.
        serialized_request = serialize_generation_request(generation_request)
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                existing_row = self._connection.execute(
                    """
                    SELECT * FROM jobs
                    WHERE user_id = ? AND idempotency_key = ?
                    """,
                    (user_id, idempotency_key),
                ).fetchone()
                if existing_row is not None:
                    existing_job = _job_from_row(existing_row)
                    if existing_job.request_hash != generation_request.request_hash:
                        raise IdempotencyConflictError(
                            "The idempotency key was reused for a different request."
                        )
                    if not request_envelope_matches(
                        self._connection,
                        job_id=existing_job.job_id,
                        user_id=user_id,
                        request_hash=generation_request.request_hash,
                        serialized_request=serialized_request,
                    ):
                        raise IdempotencyConflictError(
                            "The idempotency key has incompatible durable request "
                            "state."
                        )
                    admission_row = self._connection.execute(
                        """
                        SELECT reserved_tokens, reserved_research_cost_microusd
                        FROM job_admissions
                        WHERE job_id = ? AND user_id = ?
                        """,
                        (existing_job.job_id, user_id),
                    ).fetchone()
                    if (
                        admission_row is None
                        or int(admission_row["reserved_tokens"])
                        != admission_reservation.reserved_tokens
                        or int(admission_row["reserved_research_cost_microusd"])
                        != admission_reservation.maximum_research_cost_microusd
                    ):
                        raise IdempotencyConflictError(
                            "The idempotency key was reused with different "
                            "resource limits."
                        )
                    self._connection.execute("COMMIT")
                    return existing_job

                run_limits = generation_request.execution_profile.run_limits
                if (
                    admission_reservation.maximum_input_tokens
                    < run_limits.maximum_input_tokens
                    or admission_reservation.maximum_output_tokens
                    < run_limits.maximum_output_tokens
                ):
                    raise AdmissionReservationMismatchError(
                        "The admission reservation does not cover the request "
                        "execution profile."
                    )

                timestamp = self._now_text()
                self._enforce_admission_limits(
                    user_id=user_id,
                    reservation=admission_reservation,
                    timestamp=timestamp,
                )
                job_id = f"job-{uuid4().hex}"
                self._connection.execute(
                    """
                    INSERT INTO jobs(
                        job_id, user_id, idempotency_key, input_hash, status,
                        revision, failure_code, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 0, NULL, ?, ?)
                    """,
                    (
                        job_id,
                        user_id,
                        idempotency_key,
                        generation_request.request_hash,
                        JobStatus.accepted.value,
                        timestamp,
                        timestamp,
                    ),
                )
                insert_request_envelope(
                    self._connection,
                    job_id=job_id,
                    user_id=user_id,
                    generation_request=generation_request,
                    serialized_request=serialized_request,
                    timestamp=timestamp,
                )
                self._connection.execute(
                    """
                    INSERT INTO job_admissions(
                        job_id, user_id, reserved_tokens,
                        reserved_research_cost_microusd, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        job_id,
                        user_id,
                        admission_reservation.reserved_tokens,
                        admission_reservation.maximum_research_cost_microusd,
                        timestamp,
                    ),
                )
            except Exception:
                self._connection.execute("ROLLBACK")
                raise
            self._connection.execute("COMMIT")
            return self.get_job(job_id=job_id, user_id=user_id)

    def _enforce_admission_limits(
        self,
        *,
        user_id: str,
        reservation: AdmissionReservation,
        timestamp: str,
    ) -> None:
        """Fail before insertion when any rolling reservation would exceed."""

        violation = find_admission_limit_violation(
            connection=self._connection,
            user_id=user_id,
            reservation=reservation,
            limits=self._admission_limits,
            timestamp=timestamp,
        )
        if violation is not None:
            resource_name, configured_limit = violation
            raise AdmissionQuotaExceededError(resource_name, configured_limit)

    def get_job(self, *, job_id: str, user_id: str) -> JobRecord:
        """Read a job through a tenant-scoped query."""

        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM jobs WHERE job_id = ? AND user_id = ?",
                (job_id, user_id),
            ).fetchone()
            if row is None:
                raise JobNotFoundError("The requested job was not found.")
            return _job_from_row(row)

    def get_generation_request(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> GenerationRequest:
        """Restore one owner's exact request or fail closed on incompatible state."""

        job = self.get_job(job_id=job_id, user_id=user_id)
        generation_request: GenerationRequest | None = None
        try:
            with self._lock:
                generation_request = load_request_envelope(
                    self._connection,
                    job=job,
                )
        except PersistedRequestError:
            # Raise only after leaving this handler. That keeps the private
            # serialized request out of both ``__cause__`` and ``__context__``
            # on the package-facing compatibility error.
            pass
        if generation_request is None:
            raise JobRequestCompatibilityError(
                "The accepted job cannot be recovered with this engine."
            )
        return generation_request

    def get_resume_state(self, *, job_id: str, user_id: str) -> ResumeState:
        """Read one process-local job/request/checkpoint snapshot for an owner."""

        # FastAPI reads and the serial worker share this store instance. Keep
        # the reentrant lock across all three reads so a status/checkpoint write
        # cannot interleave and produce a state assembled from different
        # revisions.
        with self._lock:
            return ResumeState(
                job=self.get_job(job_id=job_id, user_id=user_id),
                request=self.get_generation_request(job_id=job_id, user_id=user_id),
                checkpoint=self.latest_checkpoint(job_id=job_id, user_id=user_id),
            )

    def list_resume_states(
        self,
        *,
        user_id: str,
        limit: int,
        before_created_at: datetime | None = None,
        before_job_id: str | None = None,
    ) -> tuple[ResumeState, ...]:
        """Read one stable newest-first owner page as coherent resume states.

        The service asks for one row beyond its public page size so it can
        determine whether another opaque continuation cursor is necessary.
        Both cursor leaves are required together; accepting half a cursor
        would make ordering ambiguous and could accidentally restart at page
        one.
        """

        normalized_user_id = _normalize_owner_id(user_id)
        if limit < 1 or limit > 51:
            raise InvalidJobListRequestError("The job-list bound is invalid.")
        has_timestamp = before_created_at is not None
        has_job_id = before_job_id is not None
        if has_timestamp != has_job_id:
            raise InvalidJobListRequestError("The job-list cursor is incomplete.")

        with self._lock:
            if before_created_at is None:
                rows = self._connection.execute(
                    """
                    SELECT *
                    FROM jobs
                    WHERE user_id = ?
                    ORDER BY created_at DESC, job_id DESC
                    LIMIT ?
                    """,
                    (normalized_user_id, limit),
                ).fetchall()
            else:
                if before_created_at.tzinfo is None:
                    raise InvalidJobListRequestError(
                        "The job-list cursor timestamp is invalid."
                    )
                cursor_timestamp = before_created_at.astimezone(UTC).isoformat()
                rows = self._connection.execute(
                    """
                    SELECT *
                    FROM jobs
                    WHERE user_id = ?
                      AND (
                        created_at < ?
                        OR (created_at = ? AND job_id < ?)
                      )
                    ORDER BY created_at DESC, job_id DESC
                    LIMIT ?
                    """,
                    (
                        normalized_user_id,
                        cursor_timestamp,
                        cursor_timestamp,
                        before_job_id,
                        limit,
                    ),
                ).fetchall()

            # The process-local reentrant lock stays held while each request
            # and checkpoint is loaded, preserving the same snapshot guarantee
            # as the single-job read boundary.
            return tuple(
                self.get_resume_state(
                    job_id=str(row["job_id"]),
                    user_id=normalized_user_id,
                )
                for row in rows
            )

    def next_runnable_job(self) -> ResumeState | None:
        """Return one complete recovery-first work item in stable order.

        This is an internal worker query, so it deliberately selects the owner
        from the durable job rather than accepting an owner from an HTTP
        caller. Public owner queries continue to require an explicit
        ``user_id`` at the closest storage boundary.
        """

        with self._lock:
            row = self._connection.execute(
                """
                SELECT *
                FROM jobs
                WHERE status IN (?, ?, ?, ?, ?, ?)
                ORDER BY
                    CASE status
                        WHEN ? THEN 0
                        WHEN ? THEN 1
                        WHEN ? THEN 2
                        WHEN ? THEN 3
                        WHEN ? THEN 4
                        WHEN ? THEN 5
                        ELSE 6
                    END,
                    created_at ASC,
                    job_id ASC
                LIMIT 1
                """,
                (
                    JobStatus.accepted.value,
                    JobStatus.researching.value,
                    JobStatus.drafting.value,
                    JobStatus.validating.value,
                    JobStatus.rendering.value,
                    JobStatus.delivering.value,
                    JobStatus.delivering.value,
                    JobStatus.rendering.value,
                    JobStatus.validating.value,
                    JobStatus.drafting.value,
                    JobStatus.researching.value,
                    JobStatus.accepted.value,
                ),
            ).fetchone()
            if row is None:
                return None

            job = _job_from_row(row)
            return self.get_resume_state(job_id=job.job_id, user_id=job.user_id)

    def compare_and_swap_status(
        self,
        *,
        job_id: str,
        user_id: str,
        expected_revision: int,
        new_status: JobStatus,
        failure_code: str | None = None,
    ) -> JobRecord:
        """Advance one revision only when the expected revision still owns it."""

        with self._lock:
            current_job = self.get_job(job_id=job_id, user_id=user_id)
            if current_job.revision != expected_revision:
                raise ConcurrencyConflictError(
                    "The job revision changed before this update."
                )
            validate_status_transition(current_job.status, new_status)
            cursor = self._connection.execute(
                """
                UPDATE jobs
                SET status = ?, revision = revision + 1,
                    failure_code = ?, updated_at = ?
                WHERE job_id = ? AND user_id = ? AND revision = ?
                """,
                (
                    new_status.value,
                    failure_code,
                    self._now_text(),
                    job_id,
                    user_id,
                    expected_revision,
                ),
            )
            if cursor.rowcount != 1:
                raise ConcurrencyConflictError(
                    "The job revision changed before this update."
                )
            return self.get_job(job_id=job_id, user_id=user_id)

    def record_runtime_activity(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> JobRecord:
        """Persist worker liveness without claiming a checkpoint revision.

        A final heartbeat can race the terminal status write. The status
        predicate makes that race harmless, while the owner-scoped read first
        preserves the same missing/foreign behavior as every other job write.
        """

        terminal_statuses = (
            JobStatus.completed.value,
            JobStatus.failed.value,
            JobStatus.cancelled.value,
        )
        with self._lock:
            self.get_job(job_id=job_id, user_id=user_id)
            self._connection.execute(
                """
                UPDATE jobs
                SET runtime_activity_at = ?
                WHERE job_id = ? AND user_id = ?
                  AND status NOT IN (?, ?, ?)
                """,
                (
                    self._now_text(),
                    job_id,
                    user_id,
                    *terminal_statuses,
                ),
            )
            return self.get_job(job_id=job_id, user_id=user_id)

    def save_checkpoint(
        self,
        *,
        checkpoint: JobCheckpoint,
        user_id: str,
        expected_job_revision: int,
        next_status: JobStatus,
    ) -> JobRecord:
        """Atomically persist an accepted checkpoint and advance the job."""

        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                current_job = self.get_job(
                    job_id=checkpoint.job_id,
                    user_id=user_id,
                )
                if current_job.revision != expected_job_revision:
                    raise ConcurrencyConflictError(
                        "The job revision changed before checkpointing."
                    )
                validate_status_transition(
                    current_job.status,
                    next_status,
                    allow_same=True,
                )
                self._connection.execute(
                    """
                    INSERT INTO job_checkpoints(
                        checkpoint_id, job_id, user_id, stage, sequence,
                        artifact_version, evidence_version, artifact_json,
                        budget_snapshot_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        checkpoint.checkpoint_id,
                        checkpoint.job_id,
                        user_id,
                        checkpoint.stage,
                        checkpoint.sequence,
                        checkpoint.artifact_version,
                        checkpoint.evidence_version,
                        _canonical_json(checkpoint.artifact),
                        _canonical_json(checkpoint.budget_snapshot),
                        self._now_text(),
                    ),
                )
                cursor = self._connection.execute(
                    """
                    UPDATE jobs
                    SET status = ?, revision = revision + 1, updated_at = ?
                    WHERE job_id = ? AND user_id = ? AND revision = ?
                    """,
                    (
                        next_status.value,
                        self._now_text(),
                        checkpoint.job_id,
                        user_id,
                        expected_job_revision,
                    ),
                )
                if cursor.rowcount != 1:
                    raise ConcurrencyConflictError(
                        "The job revision changed before checkpointing."
                    )
            except Exception:
                self._connection.execute("ROLLBACK")
                raise
            self._connection.execute("COMMIT")
            return self.get_job(job_id=checkpoint.job_id, user_id=user_id)

    def latest_checkpoint(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> JobCheckpoint | None:
        """Return only the highest accepted checkpoint for the owner."""

        self.get_job(job_id=job_id, user_id=user_id)
        with self._lock:
            row = self._connection.execute(
                """
                SELECT * FROM job_checkpoints
                WHERE job_id = ? AND user_id = ?
                ORDER BY sequence DESC
                LIMIT 1
                """,
                (job_id, user_id),
            ).fetchone()
            if row is None:
                return None
            return JobCheckpoint(
                schema_version="1.0",
                checkpoint_id=str(row["checkpoint_id"]),
                job_id=str(row["job_id"]),
                stage=str(row["stage"]),
                sequence=int(row["sequence"]),
                artifact_version=str(row["artifact_version"]),
                evidence_version=(
                    str(row["evidence_version"])
                    if row["evidence_version"] is not None
                    else None
                ),
                artifact=json.loads(str(row["artifact_json"])),
                budget_snapshot=json.loads(str(row["budget_snapshot_json"])),
            )

    def record_delivery_if_absent(
        self,
        *,
        job_id: str,
        user_id: str,
        payload_hash: str,
        notification_state: DeliveryNotificationState,
    ) -> bool:
        """Claim one stable delivery row with exact notification state."""

        self.get_job(job_id=job_id, user_id=user_id)
        with self._lock:
            existing_row = self._connection.execute(
                "SELECT * FROM job_deliveries WHERE job_id = ? AND user_id = ?",
                (job_id, user_id),
            ).fetchone()
            if existing_row is not None:
                if str(existing_row["payload_hash"]) != payload_hash:
                    raise IdempotencyConflictError(
                        "A different payload already owns this delivery."
                    )
                if (
                    str(existing_row["notification_schema_version"])
                    != notification_state.schema_version
                    or str(existing_row["notification_mode"])
                    != notification_state.mode.value
                    or str(existing_row["notification_status"])
                    != notification_state.status.value
                ):
                    raise IdempotencyConflictError(
                        "Different notification state already owns this delivery."
                    )
                return False
            self._connection.execute(
                """
                INSERT INTO job_deliveries(
                    job_id, user_id, payload_hash, created_at, notified_at,
                    notification_schema_version, notification_mode,
                    notification_status
                ) VALUES (?, ?, ?, ?, NULL, ?, ?, ?)
                """,
                (
                    job_id,
                    user_id,
                    payload_hash,
                    self._now_text(),
                    notification_state.schema_version,
                    notification_state.mode.value,
                    notification_state.status.value,
                ),
            )
            return True

    def get_delivery_notification(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> DeliveryNotificationState:
        """Read one owner's explicit versioned delivery-notification state."""

        self.get_job(job_id=job_id, user_id=user_id)
        with self._lock:
            row = self._connection.execute(
                """
                SELECT notification_schema_version, notification_mode,
                       notification_status
                FROM job_deliveries
                WHERE job_id = ? AND user_id = ?
                """,
                (job_id, user_id),
            ).fetchone()
            if row is None:
                raise JobNotFoundError("The requested delivery was not found.")
            return DeliveryNotificationState.model_validate(
                {
                    "schema_version": str(row["notification_schema_version"]),
                    "mode": str(row["notification_mode"]),
                    "status": str(row["notification_status"]),
                }
            )

    def purge_owner(self, *, user_id: str) -> int:
        """Atomically delete every job and cascaded row for one valid owner."""

        normalized_user_id = _normalize_owner_id(user_id)
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                count_row = self._connection.execute(
                    "SELECT COUNT(*) AS job_count FROM jobs WHERE user_id = ?",
                    (normalized_user_id,),
                ).fetchone()
                if count_row is None:
                    raise JobStoreError("Owner job count could not be read.")
                deleted_job_count = int(count_row["job_count"])
                delete_cursor = self._connection.execute(
                    "DELETE FROM jobs WHERE user_id = ?",
                    (normalized_user_id,),
                )
                if delete_cursor.rowcount != deleted_job_count:
                    raise JobStoreError("Owner job deletion could not be verified.")
                # COMMIT is part of the transaction's success boundary. A
                # filesystem-full, authorizer, or I/O failure here must still
                # enter the rollback path so a later purge can retry cleanly.
                self._connection.execute("COMMIT")
            except BaseException:
                self._connection.execute("ROLLBACK")
                raise
            return deleted_job_count


def _job_from_row(row: sqlite3.Row) -> JobRecord:
    """Convert one SQLite row to the strict public job contract."""

    return JobRecord(
        schema_version="1.0",
        job_id=str(row["job_id"]),
        user_id=str(row["user_id"]),
        idempotency_key=str(row["idempotency_key"]),
        request_hash=str(row["input_hash"]),
        status=JobStatus(str(row["status"])),
        revision=int(row["revision"]),
        failure_code=(
            str(row["failure_code"]) if row["failure_code"] is not None else None
        ),
        created_at=datetime.fromisoformat(str(row["created_at"])),
        updated_at=datetime.fromisoformat(str(row["updated_at"])),
        runtime_activity_at=(
            datetime.fromisoformat(str(row["runtime_activity_at"]))
            if row["runtime_activity_at"] is not None
            else None
        ),
    )


def _normalize_submission_identity(
    *,
    user_id: str,
    idempotency_key: str,
) -> JobSubmissionIdentity:
    """Return storage-safe identifiers without retaining validation context."""

    normalized_identity: JobSubmissionIdentity | None = None
    try:
        normalized_identity = JobSubmissionIdentity(
            user_id=user_id,
            idempotency_key=idempotency_key,
        )
    except ValueError:
        # The idempotency key is private request metadata. Leave the handler
        # before translating so it is not retained in exception context.
        pass
    if normalized_identity is None:
        raise InvalidJobSubmissionError("The job submission identity is invalid.")
    return normalized_identity


def _normalize_owner_id(user_id: str) -> str:
    """Validate an owner with the existing durable identifier grammar."""

    normalized_identity: JobSubmissionIdentity | None = None
    try:
        normalized_identity = JobSubmissionIdentity(
            user_id=user_id,
            # This fixed internal value is validated but never stored.
            idempotency_key="owner-purge",
        )
    except ValueError:
        pass
    if normalized_identity is None:
        raise InvalidJobSubmissionError("The owner identity is invalid.")
    return normalized_identity.user_id


def _canonical_json(value: object) -> str:
    """Serialize checkpoint and delivery data deterministically."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _iter_sqlite_statements(migration_sql: str) -> list[str]:
    """Split a reviewed migration without breaking triggers or SQL comments."""

    complete_statements: list[str] = []
    statement_lines: list[str] = []
    for migration_line in migration_sql.splitlines(keepends=True):
        statement_lines.append(migration_line)
        statement_candidate = "".join(statement_lines)
        if sqlite3.complete_statement(statement_candidate):
            if statement_candidate.strip():
                complete_statements.append(statement_candidate)
            statement_lines = []
    if "".join(statement_lines).strip():
        raise JobStoreError("A packaged SQLite migration is incomplete.")
    return complete_statements
