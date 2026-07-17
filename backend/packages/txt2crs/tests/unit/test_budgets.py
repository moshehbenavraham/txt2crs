# SPDX-License-Identifier: MIT-0

"""Tests for hard, concurrency-safe course-generation budgets."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

import pytest

from txt2crs.ai.budgets import (
    BudgetExceededError,
    RunBudget,
    RunBudgetLimits,
    RunBudgetSnapshot,
)


def test_budget_reserves_and_reports_every_resource() -> None:
    """Each reservation updates a typed snapshot instead of hidden counters."""

    budget = RunBudget(
        RunBudgetLimits(
            maximum_turns=2,
            maximum_research_calls=3,
            maximum_search_calls=2,
            maximum_extract_calls=2,
            maximum_sources=4,
            maximum_extracted_bytes=1_000,
            maximum_input_tokens=2_000,
            maximum_output_tokens=1_000,
            maximum_retries=2,
            maximum_repairs=1,
            maximum_elapsed_seconds=60,
        )
    )

    budget.reserve_turn()
    budget.reserve_research_call(tool_name="research_search")
    budget.reserve_sources(2)
    budget.reserve_extracted_bytes(250)
    budget.record_tokens(input_tokens=120, output_tokens=80)
    budget.reserve_retry()
    budget.reserve_repair()
    snapshot = budget.snapshot()

    assert snapshot.turns == 1
    assert snapshot.research_calls == 1
    assert snapshot.search_calls == 1
    assert snapshot.extract_calls == 0
    assert snapshot.sources == 2
    assert snapshot.extracted_bytes == 250
    assert snapshot.input_tokens == 120
    assert snapshot.output_tokens == 80
    assert snapshot.retries == 1
    assert snapshot.repairs == 1


@pytest.mark.parametrize(
    "exhaust_budget",
    [
        lambda budget: (budget.reserve_turn(), budget.reserve_turn()),
        lambda budget: (
            budget.reserve_research_call(tool_name="research_search"),
            budget.reserve_research_call(tool_name="research_search"),
        ),
        lambda budget: budget.reserve_sources(2),
        lambda budget: budget.reserve_extracted_bytes(11),
        lambda budget: budget.record_tokens(input_tokens=11, output_tokens=0),
        lambda budget: budget.record_tokens(input_tokens=0, output_tokens=11),
        lambda budget: (budget.reserve_retry(), budget.reserve_retry()),
        lambda budget: (budget.reserve_repair(), budget.reserve_repair()),
    ],
)
def test_budget_rejects_reservations_that_cross_a_limit(
    exhaust_budget: Callable[[RunBudget], object],
) -> None:
    """Every resource limit fails closed before over-budget work begins."""

    budget = RunBudget(
        RunBudgetLimits(
            maximum_turns=1,
            maximum_research_calls=1,
            maximum_search_calls=1,
            maximum_extract_calls=1,
            maximum_sources=1,
            maximum_extracted_bytes=10,
            maximum_input_tokens=10,
            maximum_output_tokens=10,
            maximum_retries=1,
            maximum_repairs=1,
            maximum_elapsed_seconds=60,
        )
    )

    with pytest.raises(BudgetExceededError):
        exhaust_budget(budget)


def test_concurrent_budget_reservations_never_exceed_the_limit() -> None:
    """Parallel workers must not win a race and over-consume model turns."""

    budget = RunBudget(
        RunBudgetLimits(
            maximum_turns=25,
            maximum_research_calls=1,
            maximum_search_calls=1,
            maximum_extract_calls=1,
            maximum_sources=1,
            maximum_extracted_bytes=1,
            maximum_input_tokens=1,
            maximum_output_tokens=1,
            maximum_retries=1,
            maximum_repairs=1,
            maximum_elapsed_seconds=60,
        )
    )

    def try_to_reserve_turn() -> bool:
        try:
            budget.reserve_turn()
        except BudgetExceededError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=20) as executor:
        reservation_results = list(
            executor.map(lambda _: try_to_reserve_turn(), range(100))
        )

    assert sum(reservation_results) == 25
    assert budget.snapshot().turns == 25


def test_budget_restores_checkpoint_counters_before_new_reservations() -> None:
    """A replacement worker cannot reset hard limits by starting a new process."""

    budget = RunBudget(
        RunBudgetLimits(
            maximum_turns=3,
            maximum_research_calls=2,
            maximum_search_calls=1,
            maximum_extract_calls=1,
            maximum_sources=3,
            maximum_extracted_bytes=100,
            maximum_input_tokens=100,
            maximum_output_tokens=100,
            maximum_retries=1,
            maximum_repairs=1,
            maximum_elapsed_seconds=60,
        )
    )
    budget.restore(
        RunBudgetSnapshot(
            turns=2,
            research_calls=1,
            search_calls=1,
            sources=2,
            extracted_bytes=40,
            input_tokens=50,
            output_tokens=25,
            elapsed_seconds=5,
        )
    )

    budget.reserve_turn()
    assert budget.snapshot().turns == 3
    with pytest.raises(BudgetExceededError, match="turns"):
        budget.reserve_turn()
    with pytest.raises(RuntimeError, match="already"):
        budget.restore(RunBudgetSnapshot())


def test_token_preflight_rejects_without_consuming_reported_usage() -> None:
    """An oversized prompt is stopped before a provider turn is reserved."""

    budget = RunBudget(
        RunBudgetLimits(
            maximum_turns=1,
            maximum_research_calls=1,
            maximum_search_calls=1,
            maximum_extract_calls=1,
            maximum_sources=1,
            maximum_extracted_bytes=1,
            maximum_input_tokens=100,
            maximum_output_tokens=100,
            maximum_retries=1,
            maximum_repairs=1,
            maximum_elapsed_seconds=60,
        )
    )

    budget.ensure_token_capacity(estimated_input_tokens=100)
    assert budget.snapshot().input_tokens == 0
    with pytest.raises(BudgetExceededError, match="input_tokens"):
        budget.ensure_token_capacity(estimated_input_tokens=101)
    assert budget.snapshot().input_tokens == 0
