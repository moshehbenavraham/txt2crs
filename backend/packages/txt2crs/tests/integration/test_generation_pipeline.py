# SPDX-License-Identifier: MIT-0

"""Credential-free end-to-end tests for the staged education pipeline."""

from typing import Any

import pytest

from tests.factories import (
    copy_data,
    valid_answer_key_data,
    valid_assessment_blueprint_data,
    valid_assessment_data,
    valid_course_data,
    valid_course_module_draft_data,
    valid_execution_profile,
    valid_generation_request,
    valid_review_pack_data,
)
from txt2crs.ai.budgets import BudgetExceededError, RunBudget, RunBudgetLimits
from txt2crs.ai.fake_runtime import FakeRuntime, ScriptedTurn
from txt2crs.ai.retry import RetrySettings
from txt2crs.ai.runtime import CancellationToken
from txt2crs.ai.runtime_status import CredentialStatus, RuntimeReadinessStatus
from txt2crs.ai.usage import RuntimeUsage
from txt2crs.domain.models import EvidenceExcerpt, SourceRecord
from txt2crs.generation.pipeline import (
    CourseGenerationPipeline,
    PipelineCheckpoint,
    PipelineGenerationError,
)
from txt2crs.ingestion.models import IngestionLimits
from txt2crs.ingestion.service import IngestionService
from txt2crs.jobs.preparation import GenerationPreparation, GenerationPreparationService
from txt2crs.jobs.requests import (
    CurriculumShapeLimits,
    GenerationRequest,
    LearningPreferenceDefaults,
    LearningPreferenceIntent,
)
from txt2crs.rendering.artifacts import ArtifactRenderer
from txt2crs.research.evidence import EvidenceLedger, FrozenEvidenceSet
from txt2crs.security.policy import ContentPolicy


def fake_usage() -> RuntimeUsage:
    """Return truthful subscription-shaped usage for one fake stage."""

    return RuntimeUsage.for_chatgpt_subscription(
        model_id="fake-model",
        input_tokens=100,
        output_tokens=50,
        latency_ms=5,
    )


def scripted_turn(output: dict[str, Any], turn_number: int) -> ScriptedTurn:
    """Wrap a stage output in deterministic runtime metadata."""

    return ScriptedTurn(
        output=output,
        usage=fake_usage(),
        thread_id=f"thread-{turn_number}",
        turn_id=f"turn-{turn_number}",
    )


def research_plan_data() -> dict[str, Any]:
    """Return the pipeline's finite research plan fixture."""

    return {
        "schema_version": "1.0",
        "plan_id": "plan-python",
        "questions": [
            {
                "question_id": "q-assignment",
                "question": "How does Python assignment bind names?",
                "preferred_source_types": ["official_documentation"],
                "freshness_days": None,
            }
        ],
        "maximum_sources": 3,
        "stop_criteria": ["The objective has primary evidence"],
    }


def course_plan_data() -> dict[str, Any]:
    """Return a course design aligned to the final course fixture."""

    return {
        "schema_version": "1.0",
        "plan_id": "course-plan-python",
        "course_id": "course-python-basics",
        "title": "Python Basics",
        "language": "en",
        "audience": "First-year computer-science students",
        "level": "beginner",
        "prerequisites": ["Basic computer literacy"],
        "duration_minutes": 60,
        "accessibility_requirements": ["semantic headings"],
        "learning_objectives": valid_course_data()["learning_objectives"],
        "modules": [
            {
                "module_id": "mod-foundations",
                "title": "Foundations",
                "objective_ids": ["obj-variables"],
                "section_ids": ["sec-variables"],
            }
        ],
    }


def assessment_package_data() -> dict[str, Any]:
    """Return separate student and instructor artifacts in one stage result."""

    return {
        "schema_version": "1.0",
        "assessment": valid_assessment_data(),
        "answer_key": valid_answer_key_data(),
    }


def frozen_evidence() -> FrozenEvidenceSet:
    """Freeze the same source and excerpt used by the final course."""

    course_data = valid_course_data()
    ledger = EvidenceLedger()
    ledger.add_source(SourceRecord.model_validate(course_data["sources"][0]))
    ledger.add_excerpt(EvidenceExcerpt.model_validate(course_data["evidence"][0]))
    return ledger.freeze()


def pipeline_budget(
    *,
    maximum_turns: int = 6,
    maximum_input_tokens: int = 10_000,
) -> RunBudget:
    """Return complete finite job limits shared by model and research stages."""

    return RunBudget(
        RunBudgetLimits(
            maximum_turns=maximum_turns,
            maximum_research_calls=10,
            maximum_search_calls=5,
            maximum_extract_calls=5,
            maximum_sources=10,
            maximum_extracted_bytes=1_000_000,
            maximum_input_tokens=maximum_input_tokens,
            maximum_output_tokens=10_000,
            maximum_retries=2,
            maximum_repairs=1,
            maximum_elapsed_seconds=600,
        )
    )


class FakeResearchCoordinator:
    """Return one approved evidence set and record stage ordering."""

    def __init__(self, evidence_set: FrozenEvidenceSet) -> None:
        self.evidence_set = evidence_set
        self.called = False

    def collect(
        self,
        _research_plan: object,
        cancellation: CancellationToken,
        *,
        high_risk_course: bool,
    ) -> FrozenEvidenceSet:
        """Set the ordering marker before returning evidence."""

        cancellation.raise_if_cancelled()
        assert high_risk_course is False
        self.called = True
        return self.evidence_set


def pipeline_with_evidence(
    evidence_set: FrozenEvidenceSet,
    *,
    budget: RunBudget | None = None,
    scripted_turns: tuple[ScriptedTurn, ...] | None = None,
) -> CourseGenerationPipeline:
    """Build the complete offline pipeline with six scripted AI stages."""

    runtime = FakeRuntime(
        readiness_status=RuntimeReadinessStatus.ready,
        credential_status=CredentialStatus.valid,
        models=("fake-model",),
        scripted_turns=scripted_turns
        or (
            scripted_turn(research_plan_data(), 1),
            scripted_turn(course_plan_data(), 2),
            scripted_turn(valid_course_module_draft_data(), 3),
            scripted_turn(valid_review_pack_data(), 4),
            scripted_turn(valid_assessment_blueprint_data(), 5),
            scripted_turn(assessment_package_data(), 6),
        ),
    )
    return CourseGenerationPipeline(
        runtime=runtime,
        research_coordinator=FakeResearchCoordinator(evidence_set),
        renderer=ArtifactRenderer(),
        model_id="fake-model",
        budget=budget or pipeline_budget(),
        retry_settings=RetrySettings(
            maximum_attempts=2,
            base_seconds=0.001,
            maximum_seconds=0.001,
            jitter_ratio=0,
        ),
    )


def generation_request_for_pipeline(
    *,
    minimum_content_blocks_per_section: int = 1,
    input_value: str = "Teach Python variables.",
) -> GenerationRequest:
    """Build the compact fixture request with explicit test-only stored limits."""

    base_profile = valid_execution_profile()
    execution_profile = base_profile.model_copy(
        update={
            "preference_defaults": LearningPreferenceDefaults(
                desired_depth="introductory",
                duration_minutes=60,
                tone="clear",
                accessibility_requirements=("semantic headings",),
                assessment_item_count=1,
                passing_percentage=70,
            ),
            "curriculum_shape_limits": CurriculumShapeLimits(
                minimum_objectives=1,
                maximum_objectives=2,
                minimum_modules=1,
                maximum_modules=2,
                minimum_sections_per_module=1,
                maximum_sections_per_module=2,
                minimum_content_blocks_per_section=(minimum_content_blocks_per_section),
                maximum_content_blocks_per_section=3,
            ),
        }
    )
    return valid_generation_request(
        value=input_value,
        preferences=LearningPreferenceIntent(
            audience="First-year computer-science students",
            prior_knowledge="Basic computer literacy",
            learning_goals=("Explain and use Python variables.",),
            level="beginner",
            language="en",
        ),
        execution_profile=execution_profile,
    )


def prepared_generation_for_pipeline(
    *,
    minimum_content_blocks_per_section: int = 1,
    input_value: str = "Teach Python variables.",
) -> GenerationPreparation:
    """Prepare the compact legacy fixture with explicit test-only stored limits."""

    request = generation_request_for_pipeline(
        minimum_content_blocks_per_section=minimum_content_blocks_per_section,
        input_value=input_value,
    )
    return GenerationPreparationService(
        ingestion_service=IngestionService(
            limits=IngestionLimits(
                maximum_input_bytes=10_000,
                maximum_normalized_characters=20_000,
            ),
            adapters={},
        ),
        content_policy=ContentPolicy(policy_version="content-policy-v1"),
    ).prepare(request)


def test_pipeline_generates_all_required_artifacts_from_one_evidence_set() -> None:
    """One input reaches course, review, test, answer sheet, and render output."""

    budget = pipeline_budget()
    pipeline = pipeline_with_evidence(frozen_evidence(), budget=budget)

    result = pipeline.generate(
        preparation=prepared_generation_for_pipeline(),
        cancellation=CancellationToken(),
    )

    assert result.input_document.document_id.startswith("input-")
    assert result.course.title == "Python Basics"
    assert result.review_pack.course_id == result.course.course_id
    assert result.assessment.course_id == result.course.course_id
    assert result.answer_key.assessment_id == result.assessment.assessment_id
    assert result.evidence_set.evidence_version == frozen_evidence().evidence_version
    assert set(result.rendered_artifacts) >= {
        "course_html",
        "course_pdf",
        "review_pack_html",
        "assessment_html",
        "answer_key_html",
    }
    assert result.assessment_blueprint.entries == result.assessment.blueprint
    assert len(result.usage_records) == 6
    assert budget.snapshot().turns == 6
    assert budget.snapshot().input_tokens == 600
    assert budget.snapshot().output_tokens == 300


def test_pipeline_reserves_each_turn_before_calling_the_runtime() -> None:
    """A hard turn limit stops assessment writing before provider side effects."""

    pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=pipeline_budget(maximum_turns=5),
    )

    with pytest.raises(BudgetExceededError, match="turns"):
        pipeline.generate(
            preparation=prepared_generation_for_pipeline(),
            cancellation=CancellationToken(),
        )


def test_pipeline_rejects_oversized_prompt_before_reserving_a_turn() -> None:
    """Approximate input-token preflight protects spend before provider work."""

    budget = pipeline_budget(maximum_input_tokens=10)
    pipeline = pipeline_with_evidence(frozen_evidence(), budget=budget)

    with pytest.raises(BudgetExceededError, match="input_tokens"):
        pipeline.generate(
            preparation=prepared_generation_for_pipeline(
                input_value="Python variables " * 100
            ),
            cancellation=CancellationToken(),
        )

    assert budget.snapshot().turns == 0
    assert budget.snapshot().input_tokens == 0


def test_pipeline_repairs_invalid_schema_output_exactly_once() -> None:
    """A malformed model artifact gets one bounded schema repair turn."""

    budget = pipeline_budget(maximum_turns=7)
    pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=budget,
        scripted_turns=(
            scripted_turn({"unexpected": "field"}, 1),
            scripted_turn(research_plan_data(), 2),
            scripted_turn(course_plan_data(), 3),
            scripted_turn(valid_course_module_draft_data(), 4),
            scripted_turn(valid_review_pack_data(), 5),
            scripted_turn(valid_assessment_blueprint_data(), 6),
            scripted_turn(assessment_package_data(), 7),
        ),
    )

    result = pipeline.generate(
        preparation=prepared_generation_for_pipeline(),
        cancellation=CancellationToken(),
    )

    assert result.course.course_id == "course-python-basics"
    assert len(result.usage_records) == 7
    assert budget.snapshot().turns == 7
    assert budget.snapshot().repairs == 1


def test_pipeline_retries_one_transient_model_transport_failure() -> None:
    """Retryable transport errors use finite attempts and the shared budget."""

    budget = pipeline_budget(maximum_turns=7)
    pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=budget,
        scripted_turns=(
            ScriptedTurn(error=ConnectionError("transport closed")),
            scripted_turn(research_plan_data(), 2),
            scripted_turn(course_plan_data(), 3),
            scripted_turn(valid_course_module_draft_data(), 4),
            scripted_turn(valid_review_pack_data(), 5),
            scripted_turn(valid_assessment_blueprint_data(), 6),
            scripted_turn(assessment_package_data(), 7),
        ),
    )

    result = pipeline.generate(
        preparation=prepared_generation_for_pipeline(),
        cancellation=CancellationToken(),
    )

    assert result.course.course_id == "course-python-basics"
    assert budget.snapshot().turns == 7
    assert budget.snapshot().retries == 1
    assert result.usage_records[0].retries == 1
    assert all(usage.retries == 0 for usage in result.usage_records[1:])


def test_pipeline_refuses_to_call_an_empty_result_deep_researched() -> None:
    """The product promise fails explicitly when no research evidence exists."""

    empty_ledger = EvidenceLedger()
    pipeline = pipeline_with_evidence(empty_ledger.freeze())

    with pytest.raises(PipelineGenerationError, match="research"):
        pipeline.generate(
            preparation=prepared_generation_for_pipeline(),
            cancellation=CancellationToken(),
        )


def test_pipeline_cancellation_stops_before_checkpointable_output() -> None:
    """A pre-cancelled run does not emit partial artifacts."""

    cancellation = CancellationToken()
    cancellation.cancel()
    pipeline = pipeline_with_evidence(frozen_evidence())

    with pytest.raises(RuntimeError, match="cancelled"):
        pipeline.generate(
            preparation=prepared_generation_for_pipeline(input_value="Teach Python."),
            cancellation=cancellation,
        )


def test_pipeline_emits_cumulative_accepted_checkpoints_and_resumes() -> None:
    """A replacement worker skips every model/research stage already accepted."""

    class SimulatedWorkerExit(BaseException):
        """Represent process loss without application-level failure settlement."""

    first_run_checkpoints: list[PipelineCheckpoint] = []
    first_pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=pipeline_budget(),
    )

    def stop_after_course_design(checkpoint: PipelineCheckpoint) -> None:
        """Retain each checkpoint and stop after the second model stage."""

        first_run_checkpoints.append(checkpoint)
        if checkpoint.stage == "design_course":
            raise SimulatedWorkerExit

    with pytest.raises(SimulatedWorkerExit):
        first_pipeline.generate(
            preparation=prepared_generation_for_pipeline(),
            cancellation=CancellationToken(),
            checkpoint_sink=stop_after_course_design,
        )

    durable_checkpoint = first_run_checkpoints[-1]
    assert [checkpoint.stage for checkpoint in first_run_checkpoints] == [
        "plan_research",
        "collect_evidence",
        "design_course",
    ]
    assert durable_checkpoint.course_plan is not None
    assert durable_checkpoint.budget_snapshot.turns == 2

    resumed_checkpoints: list[PipelineCheckpoint] = []
    resumed_pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=pipeline_budget(),
        scripted_turns=(
            scripted_turn(valid_course_module_draft_data(), 3),
            scripted_turn(valid_review_pack_data(), 4),
            scripted_turn(valid_assessment_blueprint_data(), 5),
            scripted_turn(assessment_package_data(), 6),
        ),
    )
    result = resumed_pipeline.generate(
        preparation=prepared_generation_for_pipeline(),
        cancellation=CancellationToken(),
        resume_checkpoint=durable_checkpoint,
        checkpoint_sink=resumed_checkpoints.append,
    )

    assert [checkpoint.stage for checkpoint in resumed_checkpoints] == [
        "write_module:mod-foundations",
        "verify_course",
        "generate_review_pack",
        "design_assessment",
        "cross_validate_artifacts",
    ]
    assert len(result.usage_records) == 6
    assert resumed_checkpoints[-1].budget_snapshot.turns == 6


def test_pipeline_writes_and_checkpoints_each_planned_module_separately() -> None:
    """Two planned modules require two bounded turns and two durable stages."""

    second_module_draft = copy_data(valid_course_module_draft_data())
    second_module_draft["module"].update(
        {
            "module_id": "mod-practice",
            "title": "Practice",
            "summary": "This module practices Python variable assignment.",
        }
    )
    second_section = second_module_draft["module"]["sections"][0]
    second_section.update(
        {
            "section_id": "sec-practice",
            "title": "Assignment practice",
            "summary": "Practice binding names to values.",
        }
    )
    second_block = second_section["content_blocks"][0]
    second_block["block_id"] = "block-practice-definition"
    second_module_draft["glossary"][0]["section_ids"] = ["sec-practice"]
    second_module_draft["citations"][0].update(
        {
            "citation_id": "citation-practice-definition",
            "artifact_location": "block-practice-definition",
        }
    )
    two_module_plan = course_plan_data()
    two_module_plan["modules"].append(
        {
            "module_id": "mod-practice",
            "title": "Practice",
            "objective_ids": ["obj-variables"],
            "section_ids": ["sec-practice"],
        }
    )
    checkpoints: list[PipelineCheckpoint] = []
    pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=pipeline_budget(maximum_turns=7),
        scripted_turns=(
            scripted_turn(research_plan_data(), 1),
            scripted_turn(two_module_plan, 2),
            scripted_turn(valid_course_module_draft_data(), 3),
            scripted_turn(second_module_draft, 4),
            scripted_turn(valid_review_pack_data(), 5),
            scripted_turn(valid_assessment_blueprint_data(), 6),
            scripted_turn(assessment_package_data(), 7),
        ),
    )

    result = pipeline.generate(
        preparation=prepared_generation_for_pipeline(),
        cancellation=CancellationToken(),
        checkpoint_sink=checkpoints.append,
    )

    assert [module.module_id for module in result.course.modules] == [
        "mod-foundations",
        "mod-practice",
    ]
    assert [
        checkpoint.stage
        for checkpoint in checkpoints
        if checkpoint.stage.startswith("write_module:")
    ] == [
        "write_module:mod-foundations",
        "write_module:mod-practice",
    ]
    assert checkpoints[-1].sequence == 10
    assert len(result.usage_records) == 7


def test_prepared_pipeline_checkpoints_resolved_preferences_before_drafting() -> None:
    """The first model stage sees accepted preparation, never raw re-ingestion."""

    checkpoints: list[PipelineCheckpoint] = []
    preparation = prepared_generation_for_pipeline()

    result = pipeline_with_evidence(frozen_evidence()).generate(
        preparation=preparation,
        cancellation=CancellationToken(),
        checkpoint_sink=checkpoints.append,
    )

    assert result.input_document == preparation.input_document
    assert checkpoints[0].stage == "plan_research"
    assert checkpoints[0].sequence == 2
    assert all(checkpoint.stage != "ingest_input" for checkpoint in checkpoints)
    design_checkpoint = next(
        checkpoint for checkpoint in checkpoints if checkpoint.stage == "design_course"
    )
    first_module_checkpoint = next(
        checkpoint
        for checkpoint in checkpoints
        if checkpoint.stage.startswith("write_module:")
    )
    assert design_checkpoint.resolved_preferences is not None
    assert design_checkpoint.resolved_preferences.level == "beginner"
    assert design_checkpoint.resolved_preferences.learning_goals == (
        "Explain and use Python variables.",
    )
    assert design_checkpoint.preparation == preparation
    assert design_checkpoint.sequence < first_module_checkpoint.sequence


def test_checkpoint_rejects_artifacts_beyond_its_labeled_stage() -> None:
    """A tampered early checkpoint cannot skip required generation stages."""

    checkpoints: list[PipelineCheckpoint] = []
    result = pipeline_with_evidence(frozen_evidence()).generate(
        preparation=prepared_generation_for_pipeline(),
        cancellation=CancellationToken(),
        checkpoint_sink=checkpoints.append,
    )
    design_checkpoint = next(
        checkpoint for checkpoint in checkpoints if checkpoint.stage == "design_course"
    )
    tampered_checkpoint_data = design_checkpoint.model_dump(mode="python")
    tampered_checkpoint_data["course"] = result.course.model_dump(mode="python")

    with pytest.raises(ValueError, match="unaccepted artifacts"):
        PipelineCheckpoint.model_validate(tampered_checkpoint_data)


def test_schema_valid_course_plan_gets_one_local_alignment_repair() -> None:
    """Local contract drift spends the same single bounded repair allowance."""

    drifting_plan = course_plan_data()
    drifting_plan["language"] = "he"
    budget = pipeline_budget(maximum_turns=7)
    checkpoints: list[PipelineCheckpoint] = []
    pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=budget,
        scripted_turns=(
            scripted_turn(research_plan_data(), 1),
            scripted_turn(drifting_plan, 2),
            scripted_turn(course_plan_data(), 3),
            scripted_turn(valid_course_module_draft_data(), 4),
            scripted_turn(valid_review_pack_data(), 5),
            scripted_turn(valid_assessment_blueprint_data(), 6),
            scripted_turn(assessment_package_data(), 7),
        ),
    )

    pipeline.generate(
        preparation=prepared_generation_for_pipeline(),
        cancellation=CancellationToken(),
        checkpoint_sink=checkpoints.append,
    )

    assert budget.snapshot().repairs == 1
    assert [checkpoint.stage for checkpoint in checkpoints].count("design_course") == 1


def test_course_plan_that_fails_local_gate_twice_never_reaches_module_drafting() -> (
    None
):
    """Prompt compliance cannot override deterministic local acceptance."""

    drifting_plan = course_plan_data()
    drifting_plan["level"] = "advanced"
    budget = pipeline_budget(maximum_turns=3)
    checkpoints: list[PipelineCheckpoint] = []
    pipeline = pipeline_with_evidence(
        frozen_evidence(),
        budget=budget,
        scripted_turns=(
            scripted_turn(research_plan_data(), 1),
            scripted_turn(drifting_plan, 2),
            scripted_turn(drifting_plan, 3),
        ),
    )

    with pytest.raises(PipelineGenerationError, match="course plan"):
        pipeline.generate(
            preparation=prepared_generation_for_pipeline(),
            cancellation=CancellationToken(),
            checkpoint_sink=checkpoints.append,
        )

    assert budget.snapshot().turns == 3
    assert budget.snapshot().repairs == 1
    assert all(
        not checkpoint.stage.startswith("write_module:") for checkpoint in checkpoints
    )


def test_module_content_block_shape_is_enforced_before_checkpoint() -> None:
    """A schema-valid module can still violate the accepted curriculum range."""

    checkpoints: list[PipelineCheckpoint] = []
    pipeline = pipeline_with_evidence(frozen_evidence())

    with pytest.raises(PipelineGenerationError, match="content block"):
        pipeline.generate(
            preparation=prepared_generation_for_pipeline(
                minimum_content_blocks_per_section=2
            ),
            cancellation=CancellationToken(),
            checkpoint_sink=checkpoints.append,
        )

    assert all(
        not checkpoint.stage.startswith("write_module:") for checkpoint in checkpoints
    )


def test_resume_checkpoint_is_bound_to_preparation_request_hash() -> None:
    """A checkpoint cannot be replayed with a different durable request."""

    checkpoints: list[PipelineCheckpoint] = []
    first_preparation = prepared_generation_for_pipeline()
    pipeline_with_evidence(frozen_evidence()).generate(
        preparation=first_preparation,
        cancellation=CancellationToken(),
        checkpoint_sink=checkpoints.append,
    )
    different_preparation = first_preparation.model_copy(
        update={
            "request_hash": (
                "sha256:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
            )
        }
    )

    with pytest.raises(PipelineGenerationError, match="different generation request"):
        pipeline_with_evidence(frozen_evidence()).generate(
            preparation=different_preparation,
            cancellation=CancellationToken(),
            resume_checkpoint=checkpoints[-1],
        )
