# SPDX-License-Identifier: MIT-0

"""Integration tests for durable idempotent SQLite job state."""

from concurrent.futures import ThreadPoolExecutor
from importlib.resources import files
from pathlib import Path

import pytest

from tests.factories import (
    generous_admission_limits,
    standard_admission_reservation,
)
from txt2crs.jobs.models import JobCheckpoint, JobStatus
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


def test_submission_is_idempotent_but_detects_key_reuse_for_other_input(
    tmp_path: Path,
) -> None:
    """Retries return one job while conflicting payloads fail closed."""

    store = job_store(tmp_path / "jobs.sqlite3")
    first_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=standard_admission_reservation(),
    )
    replayed_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=standard_admission_reservation(),
    )

    assert replayed_job.job_id == first_job.job_id
    assert replayed_job.revision == first_job.revision
    with pytest.raises(IdempotencyConflictError, match="different input"):
        store.create_or_get_job(
            user_id="user-1",
            idempotency_key="submit-1",
            input_hash="sha256:" + ("b" * 64),
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
        input_hash="sha256:" + ("a" * 64),
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
        input_hash="sha256:" + ("a" * 64),
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
        input_hash="sha256:" + ("a" * 64),
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
    assert reopened_store.migration_version == 2


def test_invalid_status_transition_is_rejected(tmp_path: Path) -> None:
    """Completed or early-stage jobs cannot jump across the state machine."""

    store = job_store(tmp_path / "jobs.sqlite3")
    job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="submit-1",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=standard_admission_reservation(),
    )

    with pytest.raises(ValueError, match="transition"):
        store.compare_and_swap_status(
            job_id=job.job_id,
            user_id="user-1",
            expected_revision=0,
            new_status=JobStatus.completed,
        )
