# SPDX-License-Identifier: MIT-0

"""Integration tests for exact request persistence and worker discovery."""

import json
import sqlite3
import traceback
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from importlib.resources import files
from pathlib import Path
from threading import Barrier

import pytest

from tests.factories import (
    generous_admission_limits,
    standard_admission_reservation,
    valid_generation_request,
)
from txt2crs.jobs.models import JobRecord, JobStatus
from txt2crs.jobs.quota import AdmissionReservation
from txt2crs.jobs.requests import GenerationRequest, serialize_generation_request
from txt2crs.jobs.store import (
    IdempotencyConflictError,
    JobNotFoundError,
    JobRequestCompatibilityError,
    JobStoreError,
    SqliteJobStore,
)


def job_store(
    database_path: Path,
    *,
    clock: Callable[[], datetime] | None = None,
) -> SqliteJobStore:
    """Open one migrated store with generous deterministic admission limits."""

    return SqliteJobStore(
        database_path,
        admission_limits=generous_admission_limits(),
        clock=clock,
    )


def submit_request(
    store: SqliteJobStore,
    *,
    user_id: str = "user-1",
    idempotency_key: str = "submit-1",
    request: GenerationRequest | None = None,
    reservation: AdmissionReservation | None = None,
) -> JobRecord:
    """Submit a complete request through the target store API."""

    return store.create_or_get_job(
        user_id=user_id,
        idempotency_key=idempotency_key,
        generation_request=request or valid_generation_request(),
        admission_reservation=reservation or standard_admission_reservation(),
    )


def durable_row_counts(database_path: Path) -> tuple[int, int, int]:
    """Read job, request, and admission row counts through a fresh connection."""

    with sqlite3.connect(database_path) as connection:
        return (
            int(connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]),
            int(
                connection.execute(
                    "SELECT COUNT(*) FROM generation_requests"
                ).fetchone()[0]
            ),
            int(
                connection.execute("SELECT COUNT(*) FROM job_admissions").fetchone()[0]
            ),
        )


def test_request_job_and_admission_commit_atomically(tmp_path: Path) -> None:
    """Accepted means all three durable records exist after one transaction."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)
    request = valid_generation_request(value=b"\x00\x80\xffPK\x03\x04")

    job = submit_request(store, request=request)

    assert job.request_hash == request.request_hash
    assert (
        store.get_generation_request(
            job_id=job.job_id,
            user_id="user-1",
        )
        == request
    )
    assert durable_row_counts(database_path) == (1, 1, 1)
    assert store.migration_version == 4


@pytest.mark.parametrize(
    ("user_id", "idempotency_key"),
    [
        ("", "submit-1"),
        ("user-1", "../unsafe-key"),
    ],
)
def test_submission_rejects_invalid_identity_before_any_write(
    tmp_path: Path,
    user_id: str,
    idempotency_key: str,
) -> None:
    """Invalid owner or key values cannot leave an unreadable accepted row."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)

    with pytest.raises(JobStoreError, match="identity is invalid"):
        submit_request(
            store,
            user_id=user_id,
            idempotency_key=idempotency_key,
        )

    assert durable_row_counts(database_path) == (0, 0, 0)


def test_submission_uses_normalized_identity_for_write_and_followup_reads(
    tmp_path: Path,
) -> None:
    """Whitespace normalization cannot make the returned owner unreadable."""

    store = job_store(tmp_path / "jobs.sqlite3")

    job = submit_request(
        store,
        user_id=" user-1 ",
        idempotency_key=" submit-1 ",
    )

    assert job.user_id == "user-1"
    assert job.idempotency_key == "submit-1"
    assert store.get_job(job_id=job.job_id, user_id="user-1") == job


def test_exact_replay_is_free_but_any_request_or_reservation_change_conflicts(
    tmp_path: Path,
) -> None:
    """Idempotency covers full intent, profile, and reserved resources."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)
    request = valid_generation_request()
    first_job = submit_request(store, request=request)

    replayed_job = submit_request(store, request=request)

    assert replayed_job == first_job
    assert durable_row_counts(database_path) == (1, 1, 1)
    with pytest.raises(IdempotencyConflictError, match="different request"):
        submit_request(
            store,
            request=valid_generation_request(learning_goal="Apply variables."),
        )
    with pytest.raises(IdempotencyConflictError, match="resource limits"):
        submit_request(
            store,
            request=request,
            reservation=AdmissionReservation(
                maximum_input_tokens=20_000,
                maximum_output_tokens=10_000,
                maximum_research_cost_microusd=100_000,
            ),
        )
    assert durable_row_counts(database_path) == (1, 1, 1)


def test_same_idempotency_key_is_scoped_to_owner(tmp_path: Path) -> None:
    """Two owners may independently use the same client-generated key."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)

    first_job = submit_request(store, user_id="user-1")
    second_job = submit_request(store, user_id="user-2")

    assert first_job.job_id != second_job.job_id
    assert durable_row_counts(database_path) == (2, 2, 2)


def test_concurrent_exact_replay_commits_one_durable_request(tmp_path: Path) -> None:
    """Two process-like connections cannot duplicate one owner/key request."""

    database_path = tmp_path / "jobs.sqlite3"
    first_store = job_store(database_path)
    second_store = job_store(database_path)
    request = valid_generation_request()
    start_barrier = Barrier(2)

    def submit_after_barrier(store: SqliteJobStore) -> JobRecord:
        start_barrier.wait()
        return submit_request(store, request=request)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(submit_after_barrier, first_store)
        second_future = executor.submit(submit_after_barrier, second_store)
        first_job = first_future.result()
        second_job = second_future.result()

    assert first_job == second_job
    assert durable_row_counts(database_path) == (1, 1, 1)


def test_request_insert_failure_rolls_back_job_and_admission(tmp_path: Path) -> None:
    """A mid-transaction request failure cannot leave accepted partial state."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TRIGGER reject_generation_request
            BEFORE INSERT ON generation_requests
            BEGIN
                SELECT RAISE(ABORT, 'test request rejection');
            END
            """
        )

    with pytest.raises(sqlite3.IntegrityError, match="test request rejection"):
        submit_request(store)

    assert durable_row_counts(database_path) == (0, 0, 0)


def test_new_submission_rejects_token_under_reservation(tmp_path: Path) -> None:
    """Admission cannot reserve fewer tokens than the executable run profile."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)

    with pytest.raises(JobStoreError, match="does not cover"):
        submit_request(
            store,
            reservation=AdmissionReservation(
                maximum_input_tokens=10,
                maximum_output_tokens=10,
                maximum_research_cost_microusd=100_000,
            ),
        )

    assert durable_row_counts(database_path) == (0, 0, 0)


def test_request_round_trips_exactly_after_store_restart(tmp_path: Path) -> None:
    """Recovery reopens arbitrary bytes and the exact immutable profile."""

    database_path = tmp_path / "jobs.sqlite3"
    first_store = job_store(database_path)
    request = valid_generation_request(value=b"\x00\x80\xffPK\x03\x04")
    job = submit_request(first_store, request=request)
    first_store.close()

    reopened_store = job_store(database_path)
    restored_request = reopened_store.get_generation_request(
        job_id=job.job_id,
        user_id="user-1",
    )

    assert restored_request == request
    assert restored_request.input_payload.value == b"\x00\x80\xffPK\x03\x04"
    assert restored_request.execution_profile == request.execution_profile


def test_request_reads_enforce_owner_without_leaking_existence(
    tmp_path: Path,
) -> None:
    """Foreign and missing jobs share the same owner-safe not-found behavior."""

    store = job_store(tmp_path / "jobs.sqlite3")
    job = submit_request(store)

    with pytest.raises(JobNotFoundError) as foreign_error:
        store.get_generation_request(job_id=job.job_id, user_id="user-2")
    with pytest.raises(JobNotFoundError) as missing_error:
        store.get_generation_request(job_id="job-missing", user_id="user-2")

    assert str(foreign_error.value) == str(missing_error.value)


def test_version_two_database_upgrades_without_rewriting_existing_rows(
    tmp_path: Path,
) -> None:
    """Migration 003 adds envelopes while preserving released job history."""

    database_path = tmp_path / "jobs.sqlite3"
    with sqlite3.connect(database_path) as connection:
        for migration_name in ("001_jobs.sql", "002_job_admissions.sql"):
            migration_sql = (
                files("txt2crs.jobs")
                .joinpath("migrations", migration_name)
                .read_text(encoding="utf-8")
            )
            connection.executescript(migration_sql)
        connection.executemany(
            "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            [
                (1, "2026-07-18T00:00:00+00:00"),
                (2, "2026-07-18T00:00:01+00:00"),
            ],
        )
        connection.execute(
            """
            INSERT INTO jobs(
                job_id, user_id, idempotency_key, input_hash, status,
                revision, failure_code, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)
            """,
            (
                "job-legacy",
                "user-1",
                "legacy-key",
                "sha256:" + ("a" * 64),
                "accepted",
                0,
                "2026-07-18T00:00:00+00:00",
                "2026-07-18T00:00:00+00:00",
            ),
        )

    store = job_store(database_path)

    assert store.migration_version == 4
    assert store.get_job(job_id="job-legacy", user_id="user-1").job_id == "job-legacy"
    with pytest.raises(JobRequestCompatibilityError, match="cannot be recovered"):
        store.get_generation_request(job_id="job-legacy", user_id="user-1")


def test_corrupt_persisted_request_fails_with_safe_compatibility_error(
    tmp_path: Path,
) -> None:
    """Recovery rejects altered state without echoing learner content."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)
    private_input = "private learner source"
    job = submit_request(
        store,
        request=valid_generation_request(value=private_input),
    )
    serialized_request = json.loads(
        serialize_generation_request(
            store.get_generation_request(
                job_id=job.job_id,
                user_id="user-1",
            )
        )
    )
    # Keep the learner input intact and alter only the hash. The underlying
    # validation error therefore contains sensitive request context unless the
    # store deliberately suppresses that cause.
    serialized_request["request_hash"] = "sha256:" + ("0" * 64)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            UPDATE generation_requests
            SET request_json = ?
            WHERE job_id = ?
            """,
            (
                json.dumps(serialized_request, sort_keys=True, separators=(",", ":")),
                job.job_id,
            ),
        )

    with pytest.raises(JobRequestCompatibilityError) as captured_error:
        store.get_generation_request(job_id=job.job_id, user_id="user-1")

    assert "cannot be recovered" in str(captured_error.value)
    assert private_input not in str(captured_error.value)
    assert captured_error.value.__cause__ is None
    assert captured_error.value.__context__ is None
    formatted_error = "".join(
        traceback.format_exception(captured_error.type, captured_error.value, None)
    )
    assert private_input not in formatted_error


class MutableClock:
    """Supply controlled aware timestamps for deterministic queue tests."""

    def __init__(self) -> None:
        self.current_time = datetime(2026, 7, 19, 9, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        """Return the current controlled time."""

        return self.current_time

    def advance(self) -> None:
        """Move later submissions forward by one stable interval."""

        self.current_time += timedelta(minutes=1)


def advance_job_to_status(
    store: SqliteJobStore,
    job: JobRecord,
    target_status: JobStatus,
) -> JobRecord:
    """Advance one accepted job through each valid state up to the target."""

    status_path = (
        JobStatus.researching,
        JobStatus.drafting,
        JobStatus.validating,
        JobStatus.rendering,
        JobStatus.delivering,
    )
    current_job = job
    if target_status is JobStatus.accepted:
        return current_job
    for next_status in status_path:
        current_job = store.compare_and_swap_status(
            job_id=current_job.job_id,
            user_id=current_job.user_id,
            expected_revision=current_job.revision,
            new_status=next_status,
        )
        if next_status is target_status:
            return current_job
    raise AssertionError(f"Unsupported target status for test: {target_status}")


def test_runnable_discovery_prefers_late_recovery_then_other_active_work(
    tmp_path: Path,
) -> None:
    """Nearly complete work wins even when accepted work is much older."""

    clock = MutableClock()
    store = job_store(tmp_path / "jobs.sqlite3", clock=clock)
    jobs_by_status: dict[JobStatus, JobRecord] = {}
    for status in (
        JobStatus.accepted,
        JobStatus.researching,
        JobStatus.drafting,
        JobStatus.validating,
        JobStatus.rendering,
        JobStatus.delivering,
    ):
        job = submit_request(
            store,
            idempotency_key=f"submit-{status.value}",
            request=valid_generation_request(value=f"source-{status.value}"),
        )
        jobs_by_status[status] = advance_job_to_status(store, job, status)
        clock.advance()

    expected_priority = (
        JobStatus.delivering,
        JobStatus.rendering,
        JobStatus.validating,
        JobStatus.drafting,
        JobStatus.researching,
        JobStatus.accepted,
    )
    for expected_status in expected_priority:
        runnable_state = store.next_runnable_job()
        assert runnable_state is not None
        expected_job = jobs_by_status[expected_status]
        assert runnable_state.job.job_id == expected_job.job_id
        assert runnable_state.request.request_hash == expected_job.request_hash
        store.compare_and_swap_status(
            job_id=expected_job.job_id,
            user_id=expected_job.user_id,
            expected_revision=expected_job.revision,
            new_status=JobStatus.failed,
            failure_code="settled-by-test",
        )

    assert store.next_runnable_job() is None


def test_runnable_discovery_breaks_equal_timestamps_by_job_id(
    tmp_path: Path,
) -> None:
    """A queue replay has one stable result when timestamps are identical."""

    clock = MutableClock()
    store = job_store(tmp_path / "jobs.sqlite3", clock=clock)
    first_job = submit_request(
        store,
        idempotency_key="submit-1",
        request=valid_generation_request(value="first source"),
    )
    second_job = submit_request(
        store,
        idempotency_key="submit-2",
        request=valid_generation_request(value="second source"),
    )

    runnable_state = store.next_runnable_job()

    assert runnable_state is not None
    assert runnable_state.job.job_id == min(first_job.job_id, second_job.job_id)


def test_runnable_discovery_survives_restart_and_excludes_terminal_jobs(
    tmp_path: Path,
) -> None:
    """A replacement process finds active work but never settled history."""

    database_path = tmp_path / "jobs.sqlite3"
    first_store = job_store(database_path)
    active_job = advance_job_to_status(
        first_store,
        submit_request(
            first_store,
            idempotency_key="active",
            request=valid_generation_request(value="active source"),
        ),
        JobStatus.drafting,
    )
    failed_job = submit_request(
        first_store,
        idempotency_key="failed",
        request=valid_generation_request(value="failed source"),
    )
    first_store.compare_and_swap_status(
        job_id=failed_job.job_id,
        user_id=failed_job.user_id,
        expected_revision=failed_job.revision,
        new_status=JobStatus.failed,
        failure_code="settled-by-test",
    )
    cancelled_job = submit_request(
        first_store,
        idempotency_key="cancelled",
        request=valid_generation_request(value="cancelled source"),
    )
    first_store.compare_and_swap_status(
        job_id=cancelled_job.job_id,
        user_id=cancelled_job.user_id,
        expected_revision=cancelled_job.revision,
        new_status=JobStatus.cancelled,
        failure_code="cancelled-by-test",
    )
    first_store.close()

    reopened_store = job_store(database_path)
    runnable_state = reopened_store.next_runnable_job()

    assert runnable_state is not None
    assert runnable_state.job.job_id == active_job.job_id
    assert runnable_state.request == valid_generation_request(value="active source")
    reopened_store.compare_and_swap_status(
        job_id=active_job.job_id,
        user_id=active_job.user_id,
        expected_revision=active_job.revision,
        new_status=JobStatus.failed,
        failure_code="settled-by-test",
    )
    assert reopened_store.next_runnable_job() is None


def test_runnable_discovery_fails_closed_for_missing_request_envelope(
    tmp_path: Path,
) -> None:
    """A legacy non-terminal job is surfaced as incompatible, not skipped."""

    database_path = tmp_path / "jobs.sqlite3"
    store = job_store(database_path)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO jobs(
                job_id, user_id, idempotency_key, input_hash, status,
                revision, failure_code, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 0, NULL, ?, ?)
            """,
            (
                "job-without-request",
                "user-1",
                "legacy-key",
                "sha256:" + ("a" * 64),
                JobStatus.accepted.value,
                "2026-07-18T00:00:00+00:00",
                "2026-07-18T00:00:00+00:00",
            ),
        )

    with pytest.raises(JobRequestCompatibilityError, match="cannot be recovered"):
        store.next_runnable_job()
