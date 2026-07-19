# SPDX-License-Identifier: MIT-0

"""Durable admission limits for job count, tokens, and paid research."""

from dataclasses import dataclass


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
