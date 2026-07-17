# SPDX-License-Identifier: MIT-0

"""Tests for atomic per-user/global job, token, and research-cost admission."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from txt2crs.jobs.quota import AdmissionLimits, AdmissionReservation
from txt2crs.jobs.store import AdmissionQuotaExceededError, SqliteJobStore


def reservation(
    *,
    tokens: int = 100,
    research_cost_microusd: int = 10,
) -> AdmissionReservation:
    """Split a convenient total token reservation across input and output."""

    return AdmissionReservation(
        maximum_input_tokens=tokens // 2,
        maximum_output_tokens=tokens - (tokens // 2),
        maximum_research_cost_microusd=research_cost_microusd,
    )


def test_submission_reserves_user_and_global_allowance_exactly_once(
    tmp_path: Path,
) -> None:
    """Idempotent replay is free; new jobs consume both rolling counters."""

    store = SqliteJobStore(
        tmp_path / "jobs.sqlite3",
        admission_limits=AdmissionLimits(
            window_seconds=3_600,
            maximum_jobs_per_user=1,
            maximum_jobs_global=2,
            maximum_reserved_tokens_per_user=1_000,
            maximum_reserved_tokens_global=2_000,
            maximum_research_cost_microusd_per_user=1_000,
            maximum_research_cost_microusd_global=2_000,
        ),
    )
    first_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="job-1",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=reservation(),
    )
    replayed_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="job-1",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=reservation(),
    )

    assert replayed_job == first_job
    with pytest.raises(AdmissionQuotaExceededError, match="user_jobs"):
        store.create_or_get_job(
            user_id="user-1",
            idempotency_key="job-2",
            input_hash="sha256:" + ("b" * 64),
            admission_reservation=reservation(),
        )
    store.create_or_get_job(
        user_id="user-2",
        idempotency_key="job-1",
        input_hash="sha256:" + ("c" * 64),
        admission_reservation=reservation(),
    )
    with pytest.raises(AdmissionQuotaExceededError, match="global_jobs"):
        store.create_or_get_job(
            user_id="user-3",
            idempotency_key="job-1",
            input_hash="sha256:" + ("d" * 64),
            admission_reservation=reservation(),
        )


@pytest.mark.parametrize(
    ("limits", "requested_reservation", "resource_name"),
    [
        (
            AdmissionLimits(
                window_seconds=3_600,
                maximum_jobs_per_user=10,
                maximum_jobs_global=10,
                maximum_reserved_tokens_per_user=99,
                maximum_reserved_tokens_global=1_000,
                maximum_research_cost_microusd_per_user=1_000,
                maximum_research_cost_microusd_global=1_000,
            ),
            reservation(tokens=100),
            "user_tokens",
        ),
        (
            AdmissionLimits(
                window_seconds=3_600,
                maximum_jobs_per_user=10,
                maximum_jobs_global=10,
                maximum_reserved_tokens_per_user=1_000,
                maximum_reserved_tokens_global=99,
                maximum_research_cost_microusd_per_user=1_000,
                maximum_research_cost_microusd_global=1_000,
            ),
            reservation(tokens=100),
            "global_tokens",
        ),
        (
            AdmissionLimits(
                window_seconds=3_600,
                maximum_jobs_per_user=10,
                maximum_jobs_global=10,
                maximum_reserved_tokens_per_user=1_000,
                maximum_reserved_tokens_global=1_000,
                maximum_research_cost_microusd_per_user=9,
                maximum_research_cost_microusd_global=1_000,
            ),
            reservation(research_cost_microusd=10),
            "user_research_cost",
        ),
        (
            AdmissionLimits(
                window_seconds=3_600,
                maximum_jobs_per_user=10,
                maximum_jobs_global=10,
                maximum_reserved_tokens_per_user=1_000,
                maximum_reserved_tokens_global=1_000,
                maximum_research_cost_microusd_per_user=1_000,
                maximum_research_cost_microusd_global=9,
            ),
            reservation(research_cost_microusd=10),
            "global_research_cost",
        ),
    ],
)
def test_submission_rejects_each_token_and_cost_limit(
    tmp_path: Path,
    limits: AdmissionLimits,
    requested_reservation: AdmissionReservation,
    resource_name: str,
) -> None:
    """Every configured spend dimension fails before a job row is created."""

    store = SqliteJobStore(
        tmp_path / f"{resource_name}.sqlite3",
        admission_limits=limits,
    )

    with pytest.raises(AdmissionQuotaExceededError, match=resource_name):
        store.create_or_get_job(
            user_id="user-1",
            idempotency_key="job-1",
            input_hash="sha256:" + ("a" * 64),
            admission_reservation=requested_reservation,
        )


def test_admission_window_expires_without_deleting_job_history(
    tmp_path: Path,
) -> None:
    """Old reservations stop counting while durable completed history remains."""

    current_time = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    store = SqliteJobStore(
        tmp_path / "jobs.sqlite3",
        admission_limits=AdmissionLimits(
            window_seconds=60,
            maximum_jobs_per_user=1,
            maximum_jobs_global=1,
            maximum_reserved_tokens_per_user=100,
            maximum_reserved_tokens_global=100,
            maximum_research_cost_microusd_per_user=10,
            maximum_research_cost_microusd_global=10,
        ),
        clock=lambda: current_time,
    )
    first_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="job-1",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=reservation(),
    )
    current_time += timedelta(seconds=61)
    second_job = store.create_or_get_job(
        user_id="user-1",
        idempotency_key="job-2",
        input_hash="sha256:" + ("b" * 64),
        admission_reservation=reservation(),
    )

    assert first_job.job_id != second_job.job_id
    assert store.get_job(job_id=first_job.job_id, user_id="user-1") == first_job
