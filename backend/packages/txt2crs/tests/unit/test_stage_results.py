# SPDX-License-Identifier: MIT-0

"""Tests for explicit stage terminal states and checkpoint policy."""

import pytest

from txt2crs.jobs.stage_result import StageResult, StageStatus


def test_only_accepted_required_artifacts_can_checkpoint() -> None:
    """Required deliverables cannot silently advance in degraded form."""

    accepted = StageResult.accepted(artifact={"course_id": "course-1"})
    degraded = StageResult.degraded(
        artifact={"course_id": "course-1"},
        issue_code="research_unavailable",
        public_message="Research is unavailable; this is not a researched course.",
    )
    failed = StageResult.failed(
        issue_code="invalid_schema",
        public_message="The course could not be validated.",
    )

    assert accepted.status is StageStatus.accepted
    assert accepted.can_checkpoint(required_stage=True) is True
    assert degraded.can_checkpoint(required_stage=True) is False
    assert degraded.can_checkpoint(required_stage=False) is True
    assert failed.can_checkpoint(required_stage=False) is False


def test_stage_result_repair_count_is_bounded_to_one() -> None:
    """The workflow cannot conceal an unbounded repair loop in result state."""

    with pytest.raises(ValueError, match="repair_count"):
        StageResult.failed(
            issue_code="still_invalid",
            public_message="Validation failed after repair.",
            repair_count=2,
        )


def test_cancelled_stage_has_no_usable_artifact() -> None:
    """Cancellation preserves earlier checkpoints but never the partial stage."""

    cancelled = StageResult.cancelled(public_message="Generation was cancelled.")

    assert cancelled.status is StageStatus.cancelled
    assert cancelled.artifact is None
    assert cancelled.can_checkpoint(required_stage=False) is False
