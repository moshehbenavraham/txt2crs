# SPDX-License-Identifier: MIT-0

"""Durable admission limits for job count, tokens, and paid research."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal

from pydantic import ConfigDict, Field

from txt2crs.domain.models import StrictContract


class AdmissionCapacity(StrictContract):
    """Browser-safe rolling capacity for one authenticated owner.

    The counts are expressed in complete default job reservations. This keeps
    the public result understandable while still respecting every internal
    job, token, and research-cost ceiling used by admission enforcement.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
    )

    schema_version: Literal["1.0"] = "1.0"
    window_seconds: int = Field(gt=0, le=2_592_000)
    owner_job_limit: int = Field(gt=0, le=100_000)
    owner_jobs_used: int = Field(ge=0, le=100_000)
    owner_jobs_remaining: int = Field(ge=0, le=100_000)
    shared_jobs_remaining: int = Field(ge=0, le=100_000)
    available_jobs: int = Field(ge=0, le=100_000)
    next_reservation_expires_at: datetime | None


@dataclass(frozen=True, slots=True)
class AdmissionLimits:
    """Per-user and global reservations allowed in one rolling window."""

    window_seconds: int
    maximum_jobs_per_user: int
    maximum_jobs_global: int
    maximum_reserved_tokens_per_user: int
    maximum_reserved_tokens_global: int
    maximum_research_cost_microusd_per_user: int
    maximum_research_cost_microusd_global: int

    def __post_init__(self) -> None:
        """Reject ambiguous or ineffective admission configuration."""

        positive_values = {
            "window_seconds": self.window_seconds,
            "maximum_jobs_per_user": self.maximum_jobs_per_user,
            "maximum_jobs_global": self.maximum_jobs_global,
            "maximum_reserved_tokens_per_user": (self.maximum_reserved_tokens_per_user),
            "maximum_reserved_tokens_global": self.maximum_reserved_tokens_global,
        }
        for field_name, field_value in positive_values.items():
            if field_value <= 0:
                raise ValueError(f"{field_name} must be positive.")
        nonnegative_values = {
            "maximum_research_cost_microusd_per_user": (
                self.maximum_research_cost_microusd_per_user
            ),
            "maximum_research_cost_microusd_global": (
                self.maximum_research_cost_microusd_global
            ),
        }
        for field_name, field_value in nonnegative_values.items():
            if field_value < 0:
                raise ValueError(f"{field_name} cannot be negative.")


@dataclass(frozen=True, slots=True)
class AdmissionReservation:
    """Worst-case resources reserved before one new job is accepted."""

    maximum_input_tokens: int
    maximum_output_tokens: int
    maximum_research_cost_microusd: int

    def __post_init__(self) -> None:
        """Require a meaningful token cap and a nonnegative paid-cost cap."""

        if self.maximum_input_tokens < 0 or self.maximum_output_tokens < 0:
            raise ValueError("Reserved token limits cannot be negative.")
        if self.reserved_tokens <= 0:
            raise ValueError("At least one token must be reserved.")
        if self.maximum_research_cost_microusd < 0:
            raise ValueError("Reserved research cost cannot be negative.")

    @property
    def reserved_tokens(self) -> int:
        """Return the combined maximum provider-token allowance."""

        return self.maximum_input_tokens + self.maximum_output_tokens


def inspect_admission_capacity(
    *,
    connection: sqlite3.Connection,
    user_id: str,
    reservation: AdmissionReservation,
    limits: AdmissionLimits,
    timestamp: str,
) -> AdmissionCapacity:
    """Project the current owner's remaining complete-job reservations.

    This read uses the same durable admission ledger and rolling cutoff as the
    enforcing write path. Consequently the browser cannot promise work that a
    new submission would immediately reject because of a token, paid-research,
    owner, or shared limit.
    """

    current_time = datetime.fromisoformat(timestamp)
    window_start = current_time - timedelta(seconds=limits.window_seconds)
    window_start_text = window_start.isoformat()
    owner_rows = connection.execute(
        """
        SELECT reserved_tokens, reserved_research_cost_microusd, created_at
        FROM job_admissions
        WHERE user_id = ? AND created_at >= ?
        ORDER BY created_at ASC, job_id ASC
        """,
        (user_id, window_start_text),
    ).fetchall()
    shared_rows = connection.execute(
        """
        SELECT reserved_tokens, reserved_research_cost_microusd, created_at
        FROM job_admissions
        WHERE created_at >= ?
        ORDER BY created_at ASC, job_id ASC
        """,
        (window_start_text,),
    ).fetchall()

    owner_job_limit = _complete_job_limit(
        maximum_jobs=limits.maximum_jobs_per_user,
        maximum_reserved_tokens=limits.maximum_reserved_tokens_per_user,
        maximum_research_cost_microusd=(limits.maximum_research_cost_microusd_per_user),
        reservation=reservation,
    )
    owner_jobs_remaining = _remaining_complete_jobs(
        rows=owner_rows,
        maximum_jobs=limits.maximum_jobs_per_user,
        maximum_reserved_tokens=limits.maximum_reserved_tokens_per_user,
        maximum_research_cost_microusd=(limits.maximum_research_cost_microusd_per_user),
        reservation=reservation,
    )
    shared_jobs_remaining = _remaining_complete_jobs(
        rows=shared_rows,
        maximum_jobs=limits.maximum_jobs_global,
        maximum_reserved_tokens=limits.maximum_reserved_tokens_global,
        maximum_research_cost_microusd=(limits.maximum_research_cost_microusd_global),
        reservation=reservation,
    )

    # Prefer the owner's own oldest reservation. When the owner has none and
    # shared capacity is exhausted, the aggregate expiry remains safe to show:
    # it discloses no other owner identity or course content.
    expiry_rows = owner_rows or (shared_rows if shared_jobs_remaining == 0 else [])
    next_reservation_expires_at = (
        datetime.fromisoformat(str(expiry_rows[0]["created_at"]))
        + timedelta(seconds=limits.window_seconds)
        if expiry_rows
        else None
    )
    return AdmissionCapacity(
        schema_version="1.0",
        window_seconds=limits.window_seconds,
        owner_job_limit=owner_job_limit,
        owner_jobs_used=len(owner_rows),
        owner_jobs_remaining=owner_jobs_remaining,
        shared_jobs_remaining=shared_jobs_remaining,
        available_jobs=min(owner_jobs_remaining, shared_jobs_remaining),
        next_reservation_expires_at=next_reservation_expires_at,
    )


def _complete_job_limit(
    *,
    maximum_jobs: int,
    maximum_reserved_tokens: int,
    maximum_research_cost_microusd: int,
    reservation: AdmissionReservation,
) -> int:
    """Return how many standard jobs fit into an unused allowance."""

    complete_job_limits = [
        maximum_jobs,
        maximum_reserved_tokens // reservation.reserved_tokens,
    ]
    if reservation.maximum_research_cost_microusd > 0:
        complete_job_limits.append(
            maximum_research_cost_microusd // reservation.maximum_research_cost_microusd
        )
    return min(complete_job_limits)


def _remaining_complete_jobs(
    *,
    rows: list[sqlite3.Row],
    maximum_jobs: int,
    maximum_reserved_tokens: int,
    maximum_research_cost_microusd: int,
    reservation: AdmissionReservation,
) -> int:
    """Return the smallest remaining job-equivalent across all resources."""

    remaining_job_limits = [
        max(maximum_jobs - len(rows), 0),
        max(
            (maximum_reserved_tokens - sum(int(row["reserved_tokens"]) for row in rows))
            // reservation.reserved_tokens,
            0,
        ),
    ]
    if reservation.maximum_research_cost_microusd > 0:
        remaining_job_limits.append(
            max(
                (
                    maximum_research_cost_microusd
                    - sum(int(row["reserved_research_cost_microusd"]) for row in rows)
                )
                // reservation.maximum_research_cost_microusd,
                0,
            )
        )
    return min(remaining_job_limits)


def find_admission_limit_violation(
    *,
    connection: sqlite3.Connection,
    user_id: str,
    reservation: AdmissionReservation,
    limits: AdmissionLimits,
    timestamp: str,
) -> tuple[str, int] | None:
    """Return the first exceeded rolling allowance without mutating state.

    The store owns the transaction and the public error type. This helper owns
    only quota arithmetic and read queries, keeping those responsibilities
    testable without making the main job store a multi-purpose module.
    """

    current_time = datetime.fromisoformat(timestamp)
    window_start = current_time - timedelta(seconds=limits.window_seconds)
    window_start_text = window_start.isoformat()
    user_totals = connection.execute(
        """
        SELECT
            COUNT(*) AS job_count,
            COALESCE(SUM(reserved_tokens), 0) AS reserved_tokens,
            COALESCE(SUM(reserved_research_cost_microusd), 0)
                AS reserved_research_cost_microusd
        FROM job_admissions
        WHERE user_id = ? AND created_at >= ?
        """,
        (user_id, window_start_text),
    ).fetchone()
    global_totals = connection.execute(
        """
        SELECT
            COUNT(*) AS job_count,
            COALESCE(SUM(reserved_tokens), 0) AS reserved_tokens,
            COALESCE(SUM(reserved_research_cost_microusd), 0)
                AS reserved_research_cost_microusd
        FROM job_admissions
        WHERE created_at >= ?
        """,
        (window_start_text,),
    ).fetchone()
    if user_totals is None or global_totals is None:
        raise RuntimeError("Admission totals could not be read.")

    quota_checks = (
        (
            "user_jobs",
            int(user_totals["job_count"]) + 1,
            limits.maximum_jobs_per_user,
        ),
        (
            "global_jobs",
            int(global_totals["job_count"]) + 1,
            limits.maximum_jobs_global,
        ),
        (
            "user_tokens",
            int(user_totals["reserved_tokens"]) + reservation.reserved_tokens,
            limits.maximum_reserved_tokens_per_user,
        ),
        (
            "global_tokens",
            int(global_totals["reserved_tokens"]) + reservation.reserved_tokens,
            limits.maximum_reserved_tokens_global,
        ),
        (
            "user_research_cost",
            int(user_totals["reserved_research_cost_microusd"])
            + reservation.maximum_research_cost_microusd,
            limits.maximum_research_cost_microusd_per_user,
        ),
        (
            "global_research_cost",
            int(global_totals["reserved_research_cost_microusd"])
            + reservation.maximum_research_cost_microusd,
            limits.maximum_research_cost_microusd_global,
        ),
    )
    for resource_name, requested_total, configured_limit in quota_checks:
        if requested_total > configured_limit:
            return resource_name, configured_limit
    return None
