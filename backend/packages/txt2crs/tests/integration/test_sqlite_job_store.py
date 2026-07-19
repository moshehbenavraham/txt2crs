# SPDX-License-Identifier: MIT-0

"""Integration tests for durable idempotent SQLite job state."""

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from importlib.resources import files
from pathlib import Path

import pytest

from tests.factories import (
    generous_admission_limits,
    standard_admission_reservation,
    valid_generation_request,
)
from txt2crs.jobs.models import JobCheckpoint, JobStatus
from txt2crs.jobs.notifications import DeliveryNotificationPolicy
from txt2crs.jobs.store import (
    ConcurrencyConflictError,
    IdempotencyConflictError,
    JobNotFoundError,
    SqliteJobStore,
)


def job_store(database_path: Path) -> SqliteJobStore:
    """Open and migrate one SQLite database."""

    return SqliteJobStore(
        database_path,
        admission_limits=generous_admission_limits(),
    )


def test_initial_schema_is_a_packaged_reviewable_migration() -> None:
    """Database DDL ships as a versioned resource, not hidden module text."""

    migration_sql = (
        files("txt2crs.jobs")
        .joinpath("migrations", "001_jobs.sql")
        .read_text(encoding="utf-8")
    )

    assert "CREATE TABLE IF NOT EXISTS jobs" in migration_sql
    assert "CREATE TABLE IF NOT EXISTS job_checkpoints" in migration_sql
    assert "CREATE TABLE IF NOT EXISTS job_deliveries" in migration_sql
    admission_migration_sql = (
        files("txt2crs.jobs")
        .joinpath("migrations", "002_job_admissions.sql")
        .read_text(encoding="utf-8")
    )
    assert "CREATE TABLE IF NOT EXISTS job_admissions" in admission_migration_sql
    request_migration_sql = (
        files("txt2crs.jobs")
        .joinpath("migrations", "003_generation_requests.sql")
        .read_text(encoding="utf-8")
    )
    assert "CREATE TABLE IF NOT EXISTS generation_requests" in request_migration_sql
    delivery_notification_migration_sql = (
        files("txt2crs.jobs")
        .joinpath("migrations", "004_delivery_notifications.sql")
        .read_text(encoding="utf-8")
    )
    assert "notification_schema_version" in delivery_notification_migration_sql
    assert "notification_mode" in delivery_notification_migration_sql
    assert "notification_status" in delivery_notification_migration_sql


def test_submission_is_idempotent_but_detects_key_reuse_for_other_input(
    tmp_path: Path,
) -> None:
    """Retries return one job while conflicting payloads fail closed."""

    store = job_store(tmp_path / "jobs.sqlite3")
    first_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        generation_request=valid_generation_request(value="source-a"),
        admission_reservation=standard_admission_reservation(),
    )
    replayed_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        generation_request=valid_generation_request(value="source-a"),
        admission_reservation=standard_admission_reservation(),
    )

    assert replayed_job.job_id == first_job.job_id
    assert replayed_job.revision == first_job.revision
    with pytest.raises(IdempotencyConflictError, match="different request"):
        store.create_or_get_job(
            user_id="user-1",
            idempotency_key="submit-1",
            generation_request=valid_generation_request(value="source-b"),
            admission_reservation=standard_admission_reservation(),
        )


def test_tenant_isolation_returns_not_found_instead_of_leaking_ownership(
    tmp_path: Path,
) -> None:
    """Another user cannot distinguish a foreign job from a missing job."""

    store = job_store(tmp_path / "jobs.sqlite3")
    job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        generation_request=valid_generation_request(),
        admission_reservation=standard_admission_reservation(),
    )

    with pytest.raises(JobNotFoundError):
        store.get_job(job_id=job.job_id, user_id="user-2")
    with pytest.raises(JobNotFoundError):
        store.get_job(job_id="job-does-not-exist", user_id="user-2")


def test_compare_and_swap_allows_only_one_competing_worker(tmp_path: Path) -> None:
    """Two workers cannot both advance one revision."""

    store = job_store(tmp_path / "jobs.sqlite3")
    job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        generation_request=valid_generation_request(),
        admission_reservation=standard_admission_reservation(),
    )

    def try_to_advance() -> bool:
        try:
            store.compare_and_swap_status(
                job_id=job.job_id,
                user_id="user-1",
                expected_revision=0,
                new_status=JobStatus.researching,
            )
        except ConcurrencyConflictError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _index: try_to_advance(), range(2)))

    assert sum(results) == 1
    assert store.get_job(job_id=job.job_id, user_id="user-1").revision == 1


def test_checkpoint_and_job_survive_process_restart(tmp_path: Path) -> None:
    """A restarted worker resumes only from the last accepted checkpoint."""

    database_path = tmp_path / "jobs.sqlite3"
    first_store = job_store(database_path)
    job = first_store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        generation_request=valid_generation_request(),
        admission_reservation=standard_admission_reservation(),
    )
    researching_job = first_store.compare_and_swap_status(
        job_id=job.job_id,
        user_id="user-1",
        expected_revision=job.revision,
        new_status=JobStatus.researching,
    )
    checkpoint = JobCheckpoint(
        schema_version="1.0",
        checkpoint_id="checkpoint-research",
        job_id=job.job_id,
        stage="collect_evidence",
        sequence=1,
        artifact_version="sha256:" + ("c" * 64),
        evidence_version="sha256:" + ("d" * 64),
        artifact={"source_count": 3},
        budget_snapshot={"research_calls": 2},
    )
    first_store.save_checkpoint(
        checkpoint=checkpoint,
        user_id="user-1",
        expected_job_revision=researching_job.revision,
        next_status=JobStatus.drafting,
    )
    first_store.close()

    reopened_store = job_store(database_path)
    resumed_job = reopened_store.get_job(job_id=job.job_id, user_id="user-1")
    resumed_checkpoint = reopened_store.latest_checkpoint(
        job_id=job.job_id,
        user_id="user-1",
    )

    assert resumed_job.status is JobStatus.drafting
    assert resumed_checkpoint == checkpoint
    assert reopened_store.migration_version == 4


def test_version_three_delivery_upgrades_and_reopens_without_nullable_decision(
    tmp_path: Path,
) -> None:
    """Migration 004 backfills old outbox rows and runs only once."""

    database_path = tmp_path / "jobs.sqlite3"
    with sqlite3.connect(database_path) as connection:
        for migration_name in (
            "001_jobs.sql",
            "002_job_admissions.sql",
            "003_generation_requests.sql",
        ):
            migration_sql = (
                files("txt2crs.jobs")
                .joinpath("migrations", migration_name)
                .read_text(encoding="utf-8")
            )
            connection.executescript(migration_sql)
        connection.executemany(
            "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            [
                (1, "2026-07-19T00:00:00+00:00"),
                (2, "2026-07-19T00:00:01+00:00"),
                (3, "2026-07-19T00:00:02+00:00"),
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
                "job-legacy-delivery",
                "user-1",
                "legacy-delivery",
                "sha256:" + ("a" * 64),
                JobStatus.delivering.value,
                1,
                "2026-07-19T00:00:00+00:00",
                "2026-07-19T00:00:00+00:00",
            ),
        )
        connection.execute(
            """
            INSERT INTO job_deliveries(
                job_id, user_id, payload_hash, created_at, notified_at
            ) VALUES (?, ?, ?, ?, NULL)
            """,
            (
                "job-legacy-delivery",
                "user-1",
                "sha256:" + ("b" * 64),
                "2026-07-19T00:00:00+00:00",
            ),
        )

    upgraded_store = job_store(database_path)

    assert upgraded_store.migration_version == 4
    assert (
        upgraded_store.get_delivery_notification(
            job_id="job-legacy-delivery",
            user_id="user-1",
        )
        == DeliveryNotificationPolicy.disabled().state_for_completion()
    )
    upgraded_store.close()

    # Reopening must skip the non-idempotent ALTER statements in migration
    # 004 instead of attempting to add the same columns again.
    reopened_store = job_store(database_path)
    assert reopened_store.migration_version == 4
    assert (
        reopened_store.get_delivery_notification(
            job_id="job-legacy-delivery",
            user_id="user-1",
        )
        == DeliveryNotificationPolicy.disabled().state_for_completion()
    )


def test_failed_version_four_migration_rolls_back_columns_and_version(
    tmp_path: Path,
) -> None:
    """A crash-like migration failure cannot leave unrecorded ALTER results."""

    database_path = tmp_path / "jobs.sqlite3"
    with sqlite3.connect(database_path) as connection:
        for migration_name in (
            "001_jobs.sql",
            "002_job_admissions.sql",
            "003_generation_requests.sql",
        ):
            migration_sql = (
                files("txt2crs.jobs")
                .joinpath("migrations", migration_name)
                .read_text(encoding="utf-8")
            )
            connection.executescript(migration_sql)
        connection.executemany(
            "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
            [
                (1, "2026-07-19T00:00:00+00:00"),
                (2, "2026-07-19T00:00:01+00:00"),
                (3, "2026-07-19T00:00:02+00:00"),
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
                "job-migration-failure",
                "user-1",
                "migration-failure",
                "sha256:" + ("a" * 64),
                JobStatus.delivering.value,
                1,
                "2026-07-19T00:00:00+00:00",
                "2026-07-19T00:00:00+00:00",
            ),
        )
        connection.execute(
            """
            INSERT INTO job_deliveries(
                job_id, user_id, payload_hash, created_at, notified_at
            ) VALUES (?, ?, ?, ?, NULL)
            """,
            (
                "job-migration-failure",
                "user-1",
                "sha256:" + ("b" * 64),
                "2026-07-19T00:00:00+00:00",
            ),
        )
        connection.execute(
            """
            CREATE TRIGGER reject_notification_backfill
            BEFORE UPDATE ON job_deliveries
            BEGIN
                SELECT RAISE(ABORT, 'simulated migration interruption');
            END
            """
        )

    with pytest.raises(sqlite3.IntegrityError, match="migration interruption"):
        job_store(database_path)

    with sqlite3.connect(database_path) as connection:
        delivery_columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(job_deliveries)")
        }
        migration_version = int(
            connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[
                0
            ]
        )
        connection.execute("DROP TRIGGER reject_notification_backfill")

    assert migration_version == 3
    assert "notification_schema_version" not in delivery_columns
    assert "notification_mode" not in delivery_columns
    assert "notification_status" not in delivery_columns

    repaired_store = job_store(database_path)
    assert repaired_store.migration_version == 4


def test_invalid_status_transition_is_rejected(tmp_path: Path) -> None:
    """Completed or early-stage jobs cannot jump across the state machine."""

    store = job_store(tmp_path / "jobs.sqlite3")
    job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        generation_request=valid_generation_request(),
        admission_reservation=standard_admission_reservation(),
    )

    with pytest.raises(ValueError, match="transition"):
        store.compare_and_swap_status(
            job_id=job.job_id,
            user_id="user-1",
            expected_revision=0,
            new_status=JobStatus.completed,
        )
