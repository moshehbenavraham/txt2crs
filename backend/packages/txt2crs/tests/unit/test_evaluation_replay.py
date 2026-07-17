# SPDX-License-Identifier: MIT-0

"""Tests for private, versioned, dry-runnable evaluation snapshots."""

from pathlib import Path

import pytest

from txt2crs.evals.models import EvaluationCase, EvaluationResult
from txt2crs.evals.runner import (
    EvaluationRunner,
    EvaluationSnapshotStore,
    SnapshotPathError,
)


def evaluation_case(case_id: str = "case-short-prompt") -> EvaluationCase:
    """Return one privacy-safe evaluation case definition."""

    return EvaluationCase(
        schema_version="1.0",
        case_id=case_id,
        case_version="1",
        category="short_prompt",
        input_hash="sha256:" + ("a" * 64),
        expected_invariants=["course", "review_pack", "assessment", "answer_key"],
        private_input_reference=f"private://{case_id}",
    )


def test_dry_run_plans_cases_without_live_execution() -> None:
    """Operators can inspect case/model/budget scope before spending quota."""

    live_call_count = 0

    def execute_case(_case: EvaluationCase) -> EvaluationResult:
        nonlocal live_call_count
        live_call_count += 1
        raise AssertionError("dry-run must not execute cases")

    plan = EvaluationRunner(execute_case=execute_case).plan(
        cases=[evaluation_case()],
        model_id="gpt-5.4",
        maximum_turns=10,
        live=False,
    )

    assert plan.case_ids == ["case-short-prompt"]
    assert plan.live is False
    assert live_call_count == 0


def test_snapshot_store_is_path_confined_and_round_trips_private_results(
    tmp_path: Path,
) -> None:
    """Case output stays beneath its private root with immutable hashes."""

    store = EvaluationSnapshotStore(tmp_path / "private-evals")
    result = EvaluationResult(
        schema_version="1.0",
        case_id="case-short-prompt",
        case_version="1",
        passed=True,
        artifact_hashes={"course": "sha256:" + ("b" * 64)},
        invariant_results={"course": True},
        rubric_scores={"pedagogy": 0.9},
        prompt_version="pipeline-v1",
        schema_versions={"course": "1.0"},
        model_id="fake-model",
        runtime_version="fake-runtime-v1",
        template_version="render-v1",
        evidence_version="sha256:" + ("c" * 64),
        learner_rating=4,
        correction_reason_codes=["terminology"],
        human_review_status="completed",
        private_feedback_reference="private://feedback-1",
        private_output_reference="private://output-1",
    )

    snapshot_path = store.write(result)
    loaded_result = store.read("case-short-prompt", "1")

    assert snapshot_path.is_relative_to(tmp_path / "private-evals")
    assert loaded_result == result
    with pytest.raises(SnapshotPathError):
        store.read("../escape", "1")


def test_published_aggregate_contains_no_case_content_or_private_references() -> None:
    """Publishing is explicit and returns bounded aggregate metrics only."""

    results = [
        EvaluationResult(
            schema_version="1.0",
            case_id="case-1",
            case_version="1",
            passed=True,
            artifact_hashes={},
            invariant_results={"course": True},
            rubric_scores={"pedagogy": 0.9},
            prompt_version="pipeline-v1",
            schema_versions={"course": "1.0"},
            model_id="fake-model",
            runtime_version="fake-runtime-v1",
            template_version="render-v1",
            evidence_version=None,
            learner_rating=2,
            correction_reason_codes=["factual_correction"],
            human_review_status="completed",
            private_feedback_reference="private://feedback-secret",
            private_output_reference="private://secret-output",
        )
    ]

    aggregate = EvaluationRunner.publish_aggregate(results)
    rendered = aggregate.model_dump_json()

    assert aggregate.case_count == 1
    assert aggregate.pass_rate == 1.0
    assert "case-1" not in rendered
    assert "private://secret-output" not in rendered
    assert "factual_correction" not in rendered
    assert "private://feedback-secret" not in rendered
