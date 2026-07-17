# SPDX-License-Identifier: MIT-0

"""Tests for exactly one repair and explicit stage terminal outcomes."""

from txt2crs.ai.runtime import CancellationToken
from txt2crs.jobs.stage_result import StageStatus
from txt2crs.jobs.stage_validation import run_stage_validation


def test_first_pass_success_uses_no_repair() -> None:
    """Valid output becomes accepted immediately."""

    repair_calls = 0

    def repair(_artifact: dict[str, int], _issues: list[str]) -> dict[str, int]:
        nonlocal repair_calls
        repair_calls += 1
        return {"value": 2}

    result = run_stage_validation(
        produce=lambda: {"value": 1},
        validate=lambda artifact: [] if artifact["value"] == 1 else ["invalid"],
        repair=repair,
        cancellation=CancellationToken(),
        public_failure_message="Stage failed validation.",
    )

    assert result.status is StageStatus.accepted
    assert result.repair_count == 0
    assert repair_calls == 0


def test_invalid_output_receives_exactly_one_successful_repair() -> None:
    """Validation feedback can fix one artifact without an unbounded loop."""

    repair_calls = 0

    def repair(_artifact: dict[str, int], issues: list[str]) -> dict[str, int]:
        nonlocal repair_calls
        repair_calls += 1
        assert issues == ["value must equal 2"]
        return {"value": 2}

    result = run_stage_validation(
        produce=lambda: {"value": 1},
        validate=lambda artifact: (
            [] if artifact["value"] == 2 else ["value must equal 2"]
        ),
        repair=repair,
        cancellation=CancellationToken(),
        public_failure_message="Stage failed validation.",
    )

    assert result.status is StageStatus.accepted
    assert result.artifact == {"value": 2}
    assert result.repair_count == 1
    assert repair_calls == 1


def test_invalid_repair_is_terminal_failure() -> None:
    """A second repair is never attempted or hidden as degraded success."""

    repair_calls = 0

    def repair(_artifact: dict[str, int], _issues: list[str]) -> dict[str, int]:
        nonlocal repair_calls
        repair_calls += 1
        return {"value": 1}

    result = run_stage_validation(
        produce=lambda: {"value": 1},
        validate=lambda _artifact: ["still invalid"],
        repair=repair,
        cancellation=CancellationToken(),
        public_failure_message="Stage failed validation.",
    )

    assert result.status is StageStatus.failed
    assert result.artifact is None
    assert result.repair_count == 1
    assert repair_calls == 1


def test_pre_cancelled_stage_does_not_call_producer() -> None:
    """Cancellation settles before model/provider work begins."""

    cancellation = CancellationToken()
    cancellation.cancel()
    producer_calls = 0

    def produce() -> dict[str, int]:
        nonlocal producer_calls
        producer_calls += 1
        return {"value": 1}

    result = run_stage_validation(
        produce=produce,
        validate=lambda _artifact: [],
        repair=lambda artifact, _issues: artifact,
        cancellation=cancellation,
        public_failure_message="Stage failed validation.",
    )

    assert result.status is StageStatus.cancelled
    assert producer_calls == 0
