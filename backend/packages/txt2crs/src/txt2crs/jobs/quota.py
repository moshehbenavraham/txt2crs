# SPDX-License-Identifier: MIT-0

"""Durable admission limits for job count, tokens, and paid research."""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta


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
