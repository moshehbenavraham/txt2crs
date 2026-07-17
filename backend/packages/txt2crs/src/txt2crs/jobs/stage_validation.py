# SPDX-License-Identifier: MIT-0

"""Run deterministic validation with at most one explicit repair."""

from collections.abc import Callable

from txt2crs.ai.runtime import CancellationToken
from txt2crs.jobs.stage_result import StageResult


def run_stage_validation[ArtifactType](
    *,
    produce: Callable[[], ArtifactType],
    validate: Callable[[ArtifactType], list[str]],
    repair: Callable[[ArtifactType, list[str]], ArtifactType],
    cancellation: CancellationToken,
    public_failure_message: str,
) -> StageResult:
    """Accept first-pass output, repair once, or return a terminal result."""

    if cancellation.is_cancelled:
        return StageResult.cancelled(
            public_message="Generation was cancelled before the stage began."
        )
    try:
        artifact = produce()
        cancellation.raise_if_cancelled()
    except RuntimeError:
        if cancellation.is_cancelled:
            return StageResult.cancelled(
                public_message="Generation was cancelled during the stage."
            )
        return StageResult.failed(
            issue_code="stage_execution_failed",
            public_message=public_failure_message,
        )

    validation_issues = validate(artifact)
    if not validation_issues:
        return StageResult.accepted(artifact=artifact)
    if cancellation.is_cancelled:
        return StageResult.cancelled(
            public_message="Generation was cancelled before repair."
        )

    try:
        repaired_artifact = repair(artifact, validation_issues)
        cancellation.raise_if_cancelled()
    except RuntimeError:
        if cancellation.is_cancelled:
            return StageResult.cancelled(
                public_message="Generation was cancelled during repair."
            )
        return StageResult.failed(
            issue_code="stage_repair_failed",
            public_message=public_failure_message,
            repair_count=1,
        )
    repaired_validation_issues = validate(repaired_artifact)
    if repaired_validation_issues:
        return StageResult.failed(
            issue_code="stage_invalid_after_repair",
            public_message=public_failure_message,
            repair_count=1,
        )
    return StageResult.accepted(artifact=repaired_artifact, repair_count=1)
