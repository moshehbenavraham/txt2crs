# SPDX-License-Identifier: MIT-0

"""Tests for bounded retry, error taxonomy, and stable runtime events."""

import pytest

from txt2crs.ai.budgets import RunBudget, RunBudgetLimits
from txt2crs.ai.errors import (
    RuntimeErrorCode,
    classify_runtime_error,
)
from txt2crs.ai.events import RuntimeEvent, RuntimeEventType, stable_tool_call_id
from txt2crs.ai.retry import RetryController, RetrySettings, jittered_backoff
from txt2crs.ai.runtime import CancellationToken


def retry_budget() -> RunBudget:
    """Return limits whose retry counter is easy to inspect."""

    return RunBudget(
        RunBudgetLimits(
            maximum_turns=2,
            maximum_research_calls=2,
            maximum_search_calls=1,
            maximum_extract_calls=1,
            maximum_sources=2,
            maximum_extracted_bytes=100,
            maximum_input_tokens=100,
            maximum_output_tokens=100,
            maximum_retries=2,
            maximum_repairs=1,
            maximum_elapsed_seconds=60,
        )
    )


def test_jittered_backoff_is_bounded_and_injectable() -> None:
    """Tests and production share one deterministic capped delay formula."""

    assert jittered_backoff(
        attempt=0,
        base_seconds=2,
        maximum_seconds=30,
        jitter_ratio=0.25,
        random_unit=lambda: 0.5,
    ) == pytest.approx(2.0)
    assert jittered_backoff(
        attempt=10,
        base_seconds=2,
        maximum_seconds=30,
        jitter_ratio=0.25,
        random_unit=lambda: 1.0,
    ) == pytest.approx(30.0)


def test_retry_controller_retries_only_classified_failures_with_hard_budget() -> None:
    """Two transient failures reserve retries and use deterministic delays."""

    attempts = 0
    recorded_delays: list[float] = []
    budget = retry_budget()

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("temporary transport")
        return "completed"

    controller = RetryController(
        settings=RetrySettings(
            maximum_attempts=3,
            base_seconds=1,
            maximum_seconds=5,
            jitter_ratio=0,
        ),
        budget=budget,
        cancellation=CancellationToken(),
        sleeper=recorded_delays.append,
        random_unit=lambda: 0.5,
    )

    result = controller.run(
        operation,
        is_retryable=lambda error: isinstance(error, ConnectionError),
        retry_after_seconds=lambda _error: None,
    )

    assert result == "completed"
    assert attempts == 3
    assert recorded_delays == [1.0, 2.0]
    assert budget.snapshot().retries == 2


@pytest.mark.parametrize(
    ("error", "expected_code", "retryable"),
    [
        (TimeoutError("turn timed out"), RuntimeErrorCode.timeout, True),
        (
            RuntimeError("429 rate limit quota exhausted"),
            RuntimeErrorCode.subscription_quota,
            False,
        ),
        (
            RuntimeError("401 authentication expired"),
            RuntimeErrorCode.reauthentication_required,
            False,
        ),
        (
            ConnectionError("transport closed"),
            RuntimeErrorCode.retryable_transport,
            True,
        ),
        (
            ValueError("schema invalid"),
            RuntimeErrorCode.schema_or_quality_rejection,
            False,
        ),
    ],
)
def test_small_error_taxonomy_controls_retry_policy(
    error: Exception,
    expected_code: RuntimeErrorCode,
    retryable: bool,
) -> None:
    """Provider text maps to seven local categories without body exposure."""

    classified_error = classify_runtime_error(error)

    assert classified_error.code is expected_code
    assert classified_error.retryable is retryable
    assert str(error) not in classified_error.public_message


def test_stable_tool_call_identity_survives_event_replay() -> None:
    """A retried stream projects the same tool call ID from stable inputs."""

    first_id = stable_tool_call_id(
        thread_id="thread-1",
        turn_id="turn-1",
        provider_call_id="provider-call-1",
        tool_name="research_search",
    )
    second_id = stable_tool_call_id(
        thread_id="thread-1",
        turn_id="turn-1",
        provider_call_id="provider-call-1",
        tool_name="research_search",
    )

    assert first_id == second_id
    assert first_id.startswith("call-")


def test_runtime_event_vocabulary_excludes_reasoning_and_raw_bodies() -> None:
    """Only the documented bounded event vocabulary can be constructed."""

    event = RuntimeEvent(
        event_id="event-1",
        event_type=RuntimeEventType.tool_completed,
        stage="collect_evidence",
        safe_message="Research search completed.",
        tool_call_id="call-1",
        input_tokens=None,
        output_tokens=None,
    )

    assert event.event_type is RuntimeEventType.tool_completed
    assert "reasoning" not in event.model_dump()
    assert "provider_body" not in event.model_dump()
