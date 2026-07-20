"""Reusable credential-free deterministic course support for shell tests.

The acceptance and browser suites intentionally share this module. Keeping one
strict scenario prevents the browser fixture from drifting into a route-only
mock that no longer exercises the real ``txt2crs`` application boundary.
"""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from threading import Event
from time import monotonic
from typing import Any

import pytest
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationStorageConfig,
    DeterministicApplicationConfig,
    DeterministicApplicationFactory,
    DeterministicGenerationScenario,
    DeterministicTurn,
    Txt2CrsApplication,
)
from txt2crs.domain.models import EvidenceExcerpt, SourceRecord
from txt2crs.jobs import (
    CurriculumShapeLimits,
    ExecutionProfile,
    GenerationRequest,
    InputExecutionLimits,
    InputPayload,
    JobStatus,
    LearnerAgeGroup,
    LearningPreferenceDefaults,
    LearningPreferenceIntent,
    RequestRetryPolicy,
    RunExecutionLimits,
)
from txt2crs.research.evidence import EvidenceLedger


@dataclass(frozen=True, slots=True)
class DurableSubmissionHarness:
    """Open production SQLite composition with a deterministic provider graph."""

    state_directory: Path
    execution_profile: ExecutionProfile
    scenario: DeterministicGenerationScenario

    def open(
        self,
        *,
        maximum_jobs_per_user: int = 10,
        maximum_jobs_global: int = 100,
        scenario: DeterministicGenerationScenario | None = None,
    ) -> Txt2CrsApplication:
        """Open or reopen the same exact durable state directory."""

        return DeterministicApplicationFactory(
            DeterministicApplicationConfig(
                storage=ApplicationStorageConfig(
                    state_directory=self.state_directory,
                    maximum_artifact_job_bytes=20_000_000,
                    artifact_retention_days=30,
                ),
                admission=ApplicationAdmissionConfig(
                    window_seconds=3_600,
                    maximum_jobs_per_user=maximum_jobs_per_user,
                    maximum_jobs_global=maximum_jobs_global,
                    maximum_reserved_tokens_per_user=7_500_000,
                    maximum_reserved_tokens_global=75_000_000,
                    maximum_research_cost_microusd_per_user=10_000_000,
                    maximum_research_cost_microusd_global=100_000_000,
                ),
                default_execution_profile=self.execution_profile,
                scenario=scenario or self.scenario,
            )
        ).create()

    def request(
        self,
        *,
        value: str = "Teach relational database indexes.",
        learning_goal: str = "Explain index lookup.",
        provider_consent: bool = True,
        learner_age_group: LearnerAgeGroup = LearnerAgeGroup.adult,
    ) -> GenerationRequest:
        """Build one exact canonical request aligned with the factory profile."""

        return GenerationRequest.create(
            schema_version="1.0",
            request_version="generation-request-v1",
            input_payload=InputPayload(
                input_type="prompt",
                value=value,
                media_type="text/plain",
                file_name=None,
                metadata={"input_mode": "prompt"},
            ),
            preferences=LearningPreferenceIntent(
                audience=None,
                prior_knowledge=None,
                learning_goals=(learning_goal,),
                level="auto",
                language="auto",
            ),
            provider_consent=provider_consent,
            learner_age_group=learner_age_group,
            policy_flags=(),
            execution_profile=self.execution_profile,
        )


def build_deterministic_execution_profile() -> ExecutionProfile:
    """Return the finite P0-like profile frozen into every acceptance request."""

    return ExecutionProfile(
        schema_version="1.0",
        engine_version="txt2crs-0.7.0",
        prompt_version="course-pipeline-v1",
        policy_version="content-policy-v1",
        model_id="gpt-5.6",
        reasoning_effort="high",
        retry_policy=RequestRetryPolicy(
            maximum_attempts=3,
            base_seconds=1.0,
            maximum_seconds=15.0,
            jitter_ratio=0.2,
        ),
        input_limits=InputExecutionLimits(
            maximum_input_bytes=20_971_520,
            maximum_metadata_bytes=262_144,
            maximum_normalized_characters=200_000,
            maximum_pdf_pages=200,
        ),
        run_limits=RunExecutionLimits(
            maximum_turns=20,
            maximum_research_calls=12,
            maximum_search_calls=6,
            maximum_extract_calls=6,
            maximum_sources=12,
            maximum_extracted_bytes=2_000_000,
            maximum_input_tokens=600_000,
            maximum_output_tokens=150_000,
            maximum_retries=3,
            maximum_repairs=3,
            maximum_elapsed_seconds=2_700,
        ),
        preference_defaults=LearningPreferenceDefaults(
            desired_depth="introductory",
            duration_minutes=60,
            tone="clear",
            accessibility_requirements=("semantic headings",),
            assessment_item_count=1,
            passing_percentage=70,
        ),
        curriculum_shape_limits=CurriculumShapeLimits(
            minimum_objectives=1,
            maximum_objectives=2,
            minimum_modules=1,
            maximum_modules=2,
            minimum_sections_per_module=1,
            maximum_sections_per_module=2,
            minimum_content_blocks_per_section=1,
            maximum_content_blocks_per_section=5,
        ),
    )


def _hash_text(value: str) -> str:
    """Return the labeled digest required by strict evidence contracts."""

    return f"sha256:{sha256(value.encode('utf-8')).hexdigest()}"


def _source_data() -> dict[str, Any]:
    """Return one authoritative source shared by the complete scenario."""

    return {
        "schema_version": "1.0",
        "source_id": "src-python-docs",
        "canonical_url": "https://docs.python.org/3/tutorial/",
        "title": "The Python Tutorial",
        "publisher_or_author": "Python Software Foundation",
        "publication_date": None,
        "retrieved_at": "2026-07-17T12:00:00Z",
        "content_hash": _hash_text("A variable binds a name to a value."),
        "source_type": "official_documentation",
        "authority_tier": "primary",
        "language": "en",
    }


def _evidence_data() -> dict[str, Any]:
    """Return one exact excerpt linked to the deterministic source."""

    excerpt = "A variable binds a name to a value."
    return {
        "schema_version": "1.0",
        "evidence_id": "ev-python-readable",
        "source_id": "src-python-docs",
        "excerpt": excerpt,
        "location": {
            "label": "Introduction",
            "page": None,
            "timestamp_seconds": None,
        },
        "content_hash": _hash_text(excerpt),
        "retrieval_method": "web_extract",
        "prompt_injection_warning": False,
    }


def _course_data() -> dict[str, Any]:
    """Return one small, fully referenced course for deterministic acceptance."""

    claim_text = "A variable binds a name to a value."
    return {
        "schema_version": "1.0",
        "course_id": "course-python-basics",
        "title": "Python Basics",
        "language": "en",
        "audience": "First-year computer-science students",
        "level": "beginner",
        "prerequisites": ["Basic computer literacy"],
        "learning_objectives": [
            {
                "objective_id": "obj-variables",
                "description": "Explain and use Python variables.",
                "assessed": True,
            }
        ],
        "sources": [_source_data()],
        "modules": [
            {
                "module_id": "mod-foundations",
                "title": "Foundations",
                "objective_ids": ["obj-variables"],
                "sections": [
                    {
                        "section_id": "sec-variables",
                        "title": "Variables",
                        "objective_ids": ["obj-variables"],
                        "content_blocks": [
                            {
                                "block_id": "block-variable-definition",
                                "kind": "paragraph",
                                "text": claim_text,
                                "evidence_ids": ["ev-python-readable"],
                                "is_model_generated_example": False,
                            }
                        ],
                        "summary": "Variables give useful names to values.",
                    }
                ],
                "summary": "This module introduces Python variables.",
                "misconceptions": ["A variable is not a permanent storage location."],
                "examples": ["student_count = 24"],
            }
        ],
        "glossary": [
            {
                "term": "variable",
                "definition": "A name bound to a value.",
                "section_ids": ["sec-variables"],
            }
        ],
        "unresolved_or_conflicting_claims": [],
        "evidence": [_evidence_data()],
        "citations": [
            {
                "schema_version": "1.0",
                "citation_id": "citation-variable-definition",
                "artifact_location": "block-variable-definition",
                "claim_text": claim_text,
                "claim_hash": _hash_text(claim_text),
                "evidence_ids": ["ev-python-readable"],
                "support_verdict": "supported",
                "verifier_version": "course-citation-v1",
            }
        ],
    }


def _module_draft_data() -> dict[str, Any]:
    """Return the accepted module-sized model output."""

    course = _course_data()
    return {
        "schema_version": "1.0",
        "course_id": course["course_id"],
        "module": course["modules"][0],
        "glossary": course["glossary"],
        "unresolved_or_conflicting_claims": [],
        "citations": course["citations"],
    }


def _review_pack_data() -> dict[str, Any]:
    """Return review materials linked to the course identifiers."""

    glossary = _course_data()["glossary"]
    return {
        "schema_version": "1.0",
        "review_pack_id": "review-python-basics",
        "course_id": "course-python-basics",
        "study_guide": [
            {
                "objective_id": "obj-variables",
                "section_ids": ["sec-variables"],
                "summary": "Practice naming values and changing those values.",
                "key_takeaways": ["Names make programs easier to understand."],
                "misconceptions": [
                    "The equals sign is assignment, not algebraic equality."
                ],
                "source_ids": ["src-python-docs"],
            }
        ],
        "glossary": glossary,
        "flashcards": [
            {
                "flashcard_id": "card-variable",
                "objective_id": "obj-variables",
                "prompt": "What does a Python variable do?",
                "answer": "It binds a name to a value.",
                "section_ids": ["sec-variables"],
            }
        ],
        "worked_examples": [
            {
                "exercise_id": "worked-variable",
                "objective_id": "obj-variables",
                "prompt": "Store the class size.",
                "solution": "class_size = 24",
                "section_ids": ["sec-variables"],
            }
        ],
        "practice_exercises": [
            {
                "exercise_id": "practice-variable",
                "objective_id": "obj-variables",
                "prompt": "Store your name in a variable.",
                "solution": "learner_name = 'Ada'",
                "section_ids": ["sec-variables"],
            }
        ],
        "section_summaries": {"sec-variables": "Variables name values."},
        "cumulative_summary": "Use clear variable names to express intent.",
        "review_sequence": [
            "Read the guide",
            "Try the flashcard",
            "Complete practice",
        ],
    }


def _assessment_data() -> dict[str, Any]:
    """Return one item aligned to the accepted objective and evidence."""

    return {
        "schema_version": "1.0",
        "assessment_id": "assessment-python-basics",
        "course_id": "course-python-basics",
        "title": "Python Basics Assessment",
        "passing_percentage": 70,
        "blueprint": [
            {
                "objective_id": "obj-variables",
                "section_ids": ["sec-variables"],
                "item_count": 1,
                "total_points": 5,
                "difficulty": "beginner",
                "cognitive_skill": "application",
            }
        ],
        "items": [
            {
                "item_id": "item-variable",
                "item_type": "short_answer",
                "prompt": "Write one assignment that stores 24 in class_size.",
                "objective_id": "obj-variables",
                "section_ids": ["sec-variables"],
                "evidence_ids": ["ev-python-readable"],
                "difficulty": "beginner",
                "cognitive_skill": "application",
                "points": 5,
                "options": [],
            }
        ],
        "instructions": "Answer every question.",
    }


def _assessment_blueprint_data() -> dict[str, Any]:
    """Return the accepted item-allocation plan."""

    assessment = _assessment_data()
    return {
        "schema_version": "1.0",
        "blueprint_id": "blueprint-python-basics",
        "course_id": assessment["course_id"],
        "passing_percentage": assessment["passing_percentage"],
        "entries": assessment["blueprint"],
    }


def _answer_key_data() -> dict[str, Any]:
    """Return instructor answers aligned one-to-one with assessment items."""

    return {
        "schema_version": "1.0",
        "answer_key_id": "answers-python-basics",
        "assessment_id": "assessment-python-basics",
        "answers": [
            {
                "item_id": "item-variable",
                "section_ids": ["sec-variables"],
                "evidence_ids": ["ev-python-readable"],
                "correct_answers": ["class_size = 24"],
                "explanation": "Assignment binds the name to the integer value.",
                "grading_criteria": ["Uses class_size", "Assigns the integer 24"],
                "rubric": [
                    {
                        "criterion": "Correct assignment",
                        "points": 5,
                        "description": "The name class_size is assigned 24.",
                    }
                ],
            }
        ],
    }


def build_complete_course_scenario() -> DeterministicGenerationScenario:
    """Return six accepted turns and one integrity-valid evidence set."""

    course = _course_data()
    evidence_ledger = EvidenceLedger()
    evidence_ledger.add_source(SourceRecord.model_validate(_source_data()))
    evidence_ledger.add_excerpt(EvidenceExcerpt.model_validate(_evidence_data()))
    evidence_set = evidence_ledger.freeze()
    research_plan = {
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
    course_plan = {
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
        "learning_objectives": course["learning_objectives"],
        "modules": [
            {
                "module_id": "mod-foundations",
                "title": "Foundations",
                "objective_ids": ["obj-variables"],
                "section_ids": ["sec-variables"],
            }
        ],
    }
    return DeterministicGenerationScenario.create(
        model_id="gpt-5.6",
        turns=(
            DeterministicTurn.create(
                stage="plan_research",
                output=research_plan,
            ),
            DeterministicTurn.create(
                stage="design_course",
                output=course_plan,
            ),
            DeterministicTurn.create(
                stage="write_module:mod-foundations",
                output=_module_draft_data(),
            ),
            DeterministicTurn.create(
                stage="generate_review_pack",
                output=_review_pack_data(),
            ),
            DeterministicTurn.create(
                stage="design_assessment",
                output=_assessment_blueprint_data(),
            ),
            DeterministicTurn.create(
                stage="cross_validate_artifacts",
                output={
                    "schema_version": "1.0",
                    "assessment": _assessment_data(),
                    "answer_key": _answer_key_data(),
                },
            ),
        ),
        evidence_set=evidence_set,
    )


def build_unconsumed_submission_scenario() -> DeterministicGenerationScenario:
    """Return a strict scenario that is never consumed by submission tests."""

    return DeterministicGenerationScenario.create(
        model_id="gpt-5.6",
        turns=(
            DeterministicTurn.create(
                stage="plan_research",
                output={"schema_version": "1.0"},
            ),
        ),
        evidence_set={
            "schema_version": "1.0",
            "evidence_version": "sha256:" + ("0" * 64),
            "sources": [],
            "excerpts": [],
            "selection_scores": [],
        },
    )


@dataclass(frozen=True, slots=True)
class DurableResultsHarness(DurableSubmissionHarness):
    """Complete scenario plus bounded helpers for result/replacement acceptance."""

    def request(
        self,
        *,
        value: str = "Teach Python variables.",
        learning_goal: str = "Explain and use Python variables.",
        provider_consent: bool = True,
        learner_age_group: LearnerAgeGroup = LearnerAgeGroup.adult,
    ) -> GenerationRequest:
        """Build the exact request aligned with the deterministic course plan."""

        return super().request(
            value=value,
            learning_goal=learning_goal,
            provider_consent=provider_consent,
            learner_age_group=learner_age_group,
        )

    def scenario_after(self, accepted_stage: str) -> DeterministicGenerationScenario:
        """Return only turns that follow one already-durable accepted stage."""

        stage_names = [turn.stage for turn in self.scenario.turns]
        try:
            accepted_stage_index = stage_names.index(accepted_stage)
        except ValueError:
            raise ValueError("The accepted deterministic stage is unknown.") from None
        remaining_turns = self.scenario.turns[accepted_stage_index + 1 :]
        if not remaining_turns:
            raise ValueError("The accepted stage has no remaining model turns.")
        return DeterministicGenerationScenario.create(
            model_id=self.scenario.model_id,
            turns=remaining_turns,
            evidence_set=self.scenario.load_evidence_set(),
        )

    def local_replay_scenario(self) -> DeterministicGenerationScenario:
        """Return one fail-loud turn that rendering/delivery must never consume."""

        return DeterministicGenerationScenario.create(
            model_id=self.scenario.model_id,
            turns=(self.scenario.turns[0],),
            evidence_set=self.scenario.load_evidence_set(),
        )

    def wait_for_status(
        self,
        application: Txt2CrsApplication,
        *,
        job_id: str,
        user_id: str,
        expected_status: JobStatus,
        timeout_seconds: float = 5,
    ) -> None:
        """Poll one public projection with a finite deterministic deadline."""

        deadline = monotonic() + timeout_seconds
        brief_wait = Event()
        while monotonic() < deadline:
            snapshot = application.get_public_job(
                job_id=job_id,
                user_id=user_id,
            )
            if snapshot.status is expected_status:
                return
            if snapshot.status in {
                JobStatus.failed,
                JobStatus.cancelled,
            }:
                pytest.fail(
                    "The deterministic job reached an unexpected terminal state."
                )
            brief_wait.wait(timeout=0.01)
        pytest.fail("The deterministic job did not reach the expected status.")


def build_durable_submission_harness(
    state_directory: Path,
) -> DurableSubmissionHarness:
    """Build isolated durable state for a submission-focused shell test."""

    return DurableSubmissionHarness(
        state_directory=state_directory.resolve(),
        execution_profile=build_deterministic_execution_profile(),
        scenario=build_unconsumed_submission_scenario(),
    )


def build_durable_results_harness(state_directory: Path) -> DurableResultsHarness:
    """Build one complete isolated result and recovery harness."""

    return DurableResultsHarness(
        state_directory=state_directory.resolve(),
        execution_profile=build_deterministic_execution_profile(),
        scenario=build_complete_course_scenario(),
    )
