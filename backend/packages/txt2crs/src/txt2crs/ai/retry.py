# SPDX-License-Identifier: MIT

"""Bounded exponential backoff with injectable jitter.

The pure delay behavior was adapted from Hermes' MIT-licensed
``agent/retry_utils.py`` at commit
``0f102fa4dc04b7dfdab048169aaaa640d09d7523``.
"""

from collections.abc import Callable
from dataclasses import dataclass
from random import random
from time import sleep

from txt2crs.ai.budgets import RunBudget
from txt2crs.ai.runtime import CancellationToken


@dataclass(frozen=True, slots=True)
class RetrySettings:
    """Finite retry attempts and capped exponential-delay configuration."""

    maximum_attempts: int
    base_seconds: float
    maximum_seconds: float
    jitter_ratio: float

    def __post_init__(self) -> None:
        """Reject policies that could loop forever or sleep unreasonably."""

        if self.maximum_attempts < 1:
            raise ValueError("maximum_attempts must be positive")
        if self.base_seconds <= 0 or self.maximum_seconds <= 0:
            raise ValueError("retry delays must be positive")
        if self.maximum_seconds > 60:
            raise ValueError("maximum retry delay cannot exceed 60 seconds")
        if not 0 <= self.jitter_ratio <= 1:
            raise ValueError("jitter_ratio must be between zero and one")


class RetryController:
    """Retry only caller-classified failures under the shared job budget."""

    def __init__(
        self,
        *,
        settings: RetrySettings,
        budget: RunBudget,
        cancellation: CancellationToken,
        sleeper: Callable[[float], None] = sleep,
        random_unit: Callable[[], float] = random,
    ) -> None:
        self._settings = settings
        self._budget = budget
        self._cancellation = cancellation
        self._sleeper = sleeper
        self._random_unit = random_unit

    def run[ResultType](
        self,
        operation: Callable[[], ResultType],
        *,
        is_retryable: Callable[[Exception], bool],
        retry_after_seconds: Callable[[Exception], float | None],
    ) -> ResultType:
        """Return the operation result or re-raise its final safe exception."""

        for attempt_index in range(self._settings.maximum_attempts):
            self._cancellation.raise_if_cancelled()
            try:
                return operation()
            except Exception as operation_error:
                is_final_attempt = attempt_index + 1 >= self._settings.maximum_attempts
                if is_final_attempt or not is_retryable(operation_error):
                    raise

                self._budget.reserve_retry()
                calculated_delay = jittered_backoff(
                    attempt=attempt_index,
                    base_seconds=self._settings.base_seconds,
                    maximum_seconds=self._settings.maximum_seconds,
                    jitter_ratio=self._settings.jitter_ratio,
                    random_unit=self._random_unit,
                )
                provider_delay = retry_after_seconds(operation_error)
                if provider_delay is not None and provider_delay < 0:
                    raise ValueError(
                        "Provider retry-after delay cannot be negative."
                    ) from operation_error
                bounded_delay = min(
                    self._settings.maximum_seconds,
                    max(calculated_delay, provider_delay or 0),
                )
                self._cancellation.raise_if_cancelled()
                self._sleeper(bounded_delay)
                self._cancellation.raise_if_cancelled()

        # The finite range always returns or raises. This statement protects the
        # generic return type if that invariant is changed later.
        raise RuntimeError("Retry controller exhausted without a result.")


def jittered_backoff(
    *,
    attempt: int,
    base_seconds: float,
    maximum_seconds: float,
    jitter_ratio: float,
    random_unit: Callable[[], float],
) -> float:
    """Return a non-negative capped exponential delay."""

    if attempt < 0:
        raise ValueError("attempt cannot be negative")
    if base_seconds <= 0 or maximum_seconds <= 0:
        raise ValueError("backoff durations must be positive")
    if not 0 <= jitter_ratio <= 1:
        raise ValueError("jitter_ratio must be between zero and one")
    random_value = random_unit()
    if not 0 <= random_value <= 1:
        raise ValueError("random_unit must return a value from zero to one")

    exponential_delay = min(maximum_seconds, base_seconds * (2**attempt))
    jitter_multiplier = 1 + ((2 * random_value - 1) * jitter_ratio)
    return float(min(maximum_seconds, max(0.0, exponential_delay * jitter_multiplier)))
