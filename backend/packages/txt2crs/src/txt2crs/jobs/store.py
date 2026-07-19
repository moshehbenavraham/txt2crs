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
        self._apply_migrations()

    @property
    def migration_version(self) -> int:
        """Return the highest applied local schema version."""

        row = self._connection.execute(
            "SELECT COALESCE(MAX(version), 0) AS version FROM schema_migrations"
        ).fetchone()
        return int(row["version"])

    def _apply_migrations(self) -> None:
        """Apply each idempotent schema migration and record its version."""

        with self._lock:
            for migration_version in sorted(_MIGRATION_RESOURCES):
                migration_sql = (
                    files("txt2crs.jobs")
                    .joinpath("migrations", _MIGRATION_RESOURCES[migration_version])
                    .read_text(encoding="utf-8")
                )
                self._connection.executescript(migration_sql)
                self._connection.execute(
                    """
                    INSERT OR IGNORE INTO schema_migrations(version, applied_at)
                    VALUES (?, ?)
                    """,
                    (migration_version, self._now_text()),
                )

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
    ) -> bool:
        """Claim one stable delivery row after private artifact storage."""

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
                return False
            self._connection.execute(
                """
                INSERT INTO job_deliveries(
                    job_id, user_id, payload_hash, created_at, notified_at
                ) VALUES (?, ?, ?, ?, NULL)
                """,
                (job_id, user_id, payload_hash, self._now_text()),
            )
            return True

    def delivery_needs_notification(self, *, job_id: str, user_id: str) -> bool:
        """Return whether the durable delivery outbox remains pending."""

        self.get_job(job_id=job_id, user_id=user_id)
        row = self._connection.execute(
            """
            SELECT notified_at FROM job_deliveries
            WHERE job_id = ? AND user_id = ?
            """,
            (job_id, user_id),
        ).fetchone()
        return row is not None and row["notified_at"] is None

    def mark_delivery_notified(self, *, job_id: str, user_id: str) -> None:
        """Mark the outbox sent after an idempotent notification succeeds."""

        with self._lock:
            cursor = self._connection.execute(
                """
                UPDATE job_deliveries
                SET notified_at = COALESCE(notified_at, ?)
                WHERE job_id = ? AND user_id = ?
                """,
                (self._now_text(), job_id, user_id),
            )
            if cursor.rowcount != 1:
                raise JobNotFoundError("The requested delivery was not found.")


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


def _canonical_json(value: object) -> str:
    """Serialize checkpoint and delivery data deterministically."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
