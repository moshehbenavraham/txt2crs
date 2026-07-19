# SPDX-License-Identifier: MIT-0

"""Small, reusable dictionaries for contract and pipeline tests.

The production models deliberately reject unknown fields and broken references.
Keeping one valid example in this module makes individual tests easier to read:
each test can change only the field whose behavior it is proving.
"""

from copy import deepcopy
from hashlib import sha256
from typing import Any

from txt2crs.ai.budgets import RunBudgetSnapshot
from txt2crs.domain.models import InputDocument
from txt2crs.generation.models import LearningPreferences
from txt2crs.generation.pipeline import PipelineCheckpoint
from txt2crs.generation.preferences import PreparedLearningPreferences
from txt2crs.ingestion.models import InputPayload, InputType
from txt2crs.jobs.preparation import GenerationPreparation
from txt2crs.jobs.quota import AdmissionLimits, AdmissionReservation
from txt2crs.jobs.requests import (
    CurriculumShapeLimits,
    ExecutionProfile,
    GenerationRequest,
    InputExecutionLimits,
    LearnerAgeGroup,
    LearningPreferenceDefaults,
    LearningPreferenceIntent,
    RequestRetryPolicy,
    RunExecutionLimits,
)
from txt2crs.security.policy import PolicyDecision, PolicyOutcome, PolicyStage


def _hash_text(value: str) -> str:
    """Return the same labeled SHA-256 form used by production contracts."""

    return f"sha256:{sha256(value.encode('utf-8')).hexdigest()}"


def valid_source_data() -> dict[str, Any]:
    """Return one authoritative source with stable metadata."""

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


def valid_evidence_data() -> dict[str, Any]:
    """Return evidence that belongs to :func:`valid_source_data`."""

    excerpt = "A variable binds a name to a value."
    return {
        "schema_version": "1.0",
        "evidence_id": "ev-python-readable",
        "source_id": "src-python-docs",
        "excerpt": excerpt,
        "location": {"label": "Introduction", "page": None, "timestamp_seconds": None},
        "content_hash": _hash_text(excerpt),
        "retrieval_method": "web_extract",
        "prompt_injection_warning": False,
    }


def valid_course_data() -> dict[str, Any]:
    """Return the smallest useful course with one fully traced objective."""

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
        "sources": [valid_source_data()],
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
                                "text": "A variable binds a name to a value.",
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
        "evidence": [valid_evidence_data()],
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


def valid_course_module_draft_data() -> dict[str, Any]:
    """Return one module-sized model output for deterministic course assembly."""

    course_data = valid_course_data()
    return {
        "schema_version": "1.0",
        "course_id": course_data["course_id"],
        "module": course_data["modules"][0],
        "glossary": course_data["glossary"],
        "unresolved_or_conflicting_claims": course_data[
            "unresolved_or_conflicting_claims"
        ],
        "citations": course_data["citations"],
    }


def valid_review_pack_data() -> dict[str, Any]:
    """Return review material linked to the course's canonical identifiers."""

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
        "glossary": [
            {
                "term": "variable",
                "definition": "A name bound to a value.",
                "section_ids": ["sec-variables"],
            }
        ],
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
        "review_sequence": ["Read the guide", "Try the flashcard", "Complete practice"],
    }


def valid_assessment_data() -> dict[str, Any]:
    """Return a student assessment with an explicit objective blueprint."""

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


def valid_assessment_blueprint_data() -> dict[str, Any]:
    """Return the assessment plan that must be approved before item writing."""

    assessment_data = valid_assessment_data()
    return {
        "schema_version": "1.0",
        "blueprint_id": "blueprint-python-basics",
        "course_id": assessment_data["course_id"],
        "passing_percentage": assessment_data["passing_percentage"],
        "entries": assessment_data["blueprint"],
    }


def valid_answer_key_data() -> dict[str, Any]:
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


def copy_data(data: dict[str, Any]) -> dict[str, Any]:
    """Deep-copy nested test data before a test mutates it."""

    return deepcopy(data)


def generous_admission_limits() -> AdmissionLimits:
    """Return high but finite rolling limits for unrelated job tests."""

    return AdmissionLimits(
        window_seconds=3_600,
        maximum_jobs_per_user=100,
        maximum_jobs_global=1_000,
        maximum_reserved_tokens_per_user=10_000_000,
        maximum_reserved_tokens_global=100_000_000,
        maximum_research_cost_microusd_per_user=10_000_000,
        maximum_research_cost_microusd_global=100_000_000,
    )


def standard_admission_reservation() -> AdmissionReservation:
    """Return the finite worst-case reservation used by job fixtures."""

    return AdmissionReservation(
        maximum_input_tokens=600_000,
        maximum_output_tokens=150_000,
        maximum_research_cost_microusd=100_000,
    )


def valid_execution_profile(
    *,
    maximum_input_bytes: int = 20_971_520,
    maximum_metadata_bytes: int = 262_144,
    maximum_input_tokens: int = 600_000,
    maximum_output_tokens: int = 150_000,
) -> ExecutionProfile:
    """Return the finite P0-like profile shared by request tests."""

    return ExecutionProfile(
        schema_version="1.0",
        engine_version="engine-0.4",
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
            maximum_input_bytes=maximum_input_bytes,
            maximum_metadata_bytes=maximum_metadata_bytes,
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
            maximum_input_tokens=maximum_input_tokens,
            maximum_output_tokens=maximum_output_tokens,
            maximum_retries=3,
            maximum_repairs=3,
            maximum_elapsed_seconds=2_700.0,
        ),
        preference_defaults=LearningPreferenceDefaults(),
        curriculum_shape_limits=CurriculumShapeLimits(),
    )


def valid_generation_request(
    *,
    value: str | bytes = "Teach Python variables with worked examples.",
    input_payload: InputPayload | None = None,
    metadata: dict[str, object] | None = None,
    preferences: LearningPreferenceIntent | None = None,
    learning_goal: str = "Explain variables.",
    provider_consent: bool = True,
    learner_age_group: LearnerAgeGroup = LearnerAgeGroup.adult,
    policy_flags: tuple[str, ...] = ("allow_external_research",),
    execution_profile: ExecutionProfile | None = None,
) -> GenerationRequest:
    """Create one complete request whose hash production code computes."""

    request_metadata = {"source": "learner"} if metadata is None else metadata
    request_input_payload = input_payload or InputPayload(
        input_type="text",
        value=value,
        media_type="text/plain",
        file_name=None,
        metadata=request_metadata,
    )
    return GenerationRequest.create(
        schema_version="1.0",
        request_version="generation-request-v1",
        input_payload=request_input_payload,
        preferences=preferences
        or LearningPreferenceIntent(
            audience=None,
            prior_knowledge=None,
            learning_goals=(learning_goal,),
            level="auto",
            language="auto",
        ),
        provider_consent=provider_consent,
        learner_age_group=learner_age_group,
        policy_flags=policy_flags,
        execution_profile=execution_profile or valid_execution_profile(),
    )


def valid_input_document(
    *,
    normalized_text: str = "Teach Python variables with worked examples.",
    input_type: InputType = "text",
    media_type: str = "text/plain",
    language: str = "en",
    metadata: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
) -> InputDocument:
    """Return one canonical normalized input document for checkpoint tests."""

    content_hash = _hash_text(normalized_text)
    return InputDocument(
        schema_version="1.0",
        document_id=f"input-{content_hash.removeprefix('sha256:')[:24]}",
        input_type=input_type,
        media_type=media_type,
        normalized_text=normalized_text,
        language=language,
        metadata=deepcopy(metadata or {}),
        content_hash=content_hash,
        warnings=list(warnings or []),
        locations=[],
    )


def valid_generation_preparation(
    *,
    generation_request: GenerationRequest | None = None,
    input_document: InputDocument | None = None,
) -> GenerationPreparation:
    """Return allowed provider-free state bound to one exact request hash."""

    request = generation_request or valid_generation_request()
    prepared_document = input_document or valid_input_document(
        input_type=request.input_payload.input_type,
        media_type=request.input_payload.media_type,
    )
    return GenerationPreparation(
        schema_version="1.0",
        request_hash=request.request_hash,
        input_document=prepared_document,
        policy_decision=PolicyDecision(
            policy_version=request.execution_profile.policy_version,
            stage=PolicyStage.post_ingestion,
            outcome=PolicyOutcome.allowed,
            reason_code="allowed",
            high_risk=False,
            public_message="The request may proceed.",
        ),
        planning_preferences=PreparedLearningPreferences.from_request(
            generation_request=request,
            detected_input_language=prepared_document.language,
            high_risk_course=False,
        ),
        curriculum_shape_limits=(request.execution_profile.curriculum_shape_limits),
    )


def valid_resolved_preferences(
    *,
    audience: str = "First-year computer-science students",
    prior_knowledge: str = "Basic computer literacy",
    learning_goals: tuple[str, ...] = ("Explain and use Python variables.",),
    level: str = "beginner",
    language: str = "en",
    defaults: LearningPreferenceDefaults | None = None,
) -> LearningPreferences:
    """Return one concrete post-plan learning contract."""

    preference_defaults = defaults or LearningPreferenceDefaults()
    return LearningPreferences.model_validate(
        {
            "audience": audience,
            "prior_knowledge": prior_knowledge,
            "learning_goals": learning_goals,
            "level": level,
            "desired_depth": preference_defaults.desired_depth,
            "duration_minutes": preference_defaults.duration_minutes,
            "language": language,
            "tone": preference_defaults.tone,
            "accessibility_requirements": (
                preference_defaults.accessibility_requirements
            ),
            "assessment_item_count": preference_defaults.assessment_item_count,
            "passing_percentage": preference_defaults.passing_percentage,
            "high_risk_course": False,
        }
    )


def valid_pipeline_checkpoint(
    *,
    normalized_text: str = "Private normalized course input.",
    input_type: InputType = "text",
    media_type: str = "text/plain",
    input_metadata: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    source_data: dict[str, Any] | None = None,
    evidence_data: dict[str, Any] | None = None,
    unresolved_conflicts: list[str] | None = None,
    usage_records: list[dict[str, Any]] | None = None,
) -> PipelineCheckpoint:
    """Return one final cumulative checkpoint for public-query tests.

    The helper deliberately permits tests to inject private sentinels into
    nested state. Production projection tests can then prove those values stay
    absent without rebuilding the pipeline's many referenced contracts.
    """

    retained_source = deepcopy(source_data or valid_source_data())
    retained_evidence = deepcopy(evidence_data or valid_evidence_data())
    course_data = valid_course_data()
    course_data["sources"] = [retained_source]
    course_data["evidence"] = [retained_evidence]
    course_data["unresolved_or_conflicting_claims"] = list(unresolved_conflicts or [])
    request_payload = InputPayload(
        input_type=input_type,
        value=(
            normalized_text
            if input_type in {"prompt", "text", "url"}
            else b"bounded-private-input"
        ),
        media_type=media_type,
        file_name="course-source.pdf" if input_type == "pdf" else None,
        metadata={},
    )
    generation_request = valid_generation_request(input_payload=request_payload)
    prepared_document = valid_input_document(
        normalized_text=normalized_text,
        input_type=input_type,
        media_type=media_type,
        metadata=input_metadata,
        warnings=warnings,
    )
    preparation = valid_generation_preparation(
        generation_request=generation_request,
        input_document=prepared_document,
    )

    # Replacing an evidence fixture requires every course-local reference to
    # point at the replacement ID so the checkpoint stays structurally valid.
    replacement_evidence_id = retained_evidence["evidence_id"]
    for module in course_data["modules"]:
        for section in module["sections"]:
            for content_block in section["content_blocks"]:
                content_block["evidence_ids"] = [replacement_evidence_id]
    for citation in course_data["citations"]:
        citation["evidence_ids"] = [replacement_evidence_id]

    module_draft_data = valid_course_module_draft_data()
    module_draft_data["module"] = deepcopy(course_data["modules"][0])
    module_draft_data["unresolved_or_conflicting_claims"] = list(
        course_data["unresolved_or_conflicting_claims"]
    )
    module_draft_data["citations"] = deepcopy(course_data["citations"])

    checkpoint_hash = preparation.request_hash
    return PipelineCheckpoint.model_validate(
        {
            "schema_version": "1.0",
            "stage": "cross_validate_artifacts",
            "sequence": 9,
            "request_hash": checkpoint_hash,
            "preparation": preparation.model_dump(mode="json"),
            "research_plan": {
                "schema_version": "1.0",
                "plan_id": "research-plan-public-query",
                "questions": [
                    {
                        "question_id": "question-public-query",
                        "question": "What reviewed evidence supports this course?",
                        "preferred_source_types": ["official documentation"],
                        "freshness_days": None,
                    }
                ],
                "maximum_sources": 10,
                "stop_criteria": ["Enough evidence supports the learning goals."],
            },
            "evidence_set": {
                "schema_version": "1.0",
                "evidence_version": checkpoint_hash,
                "sources": [retained_source],
                "excerpts": [retained_evidence],
                "selection_scores": [],
            },
            "course_plan": {
                "schema_version": "1.0",
                "plan_id": "course-plan-public-query",
                "course_id": course_data["course_id"],
                "title": course_data["title"],
                "language": course_data["language"],
                "audience": course_data["audience"],
                "level": course_data["level"],
                "prerequisites": course_data["prerequisites"],
                "duration_minutes": 120,
                "accessibility_requirements": ["Semantic headings"],
                "learning_objectives": course_data["learning_objectives"],
                "modules": [
                    {
                        "module_id": course_data["modules"][0]["module_id"],
                        "title": course_data["modules"][0]["title"],
                        "objective_ids": course_data["modules"][0]["objective_ids"],
                        "section_ids": [
                            section["section_id"]
                            for section in course_data["modules"][0]["sections"]
                        ],
                    }
                ],
            },
            "resolved_preferences": valid_resolved_preferences().model_dump(
                mode="json"
            ),
            "course_module_drafts": [module_draft_data],
            "course": course_data,
            "review_pack": valid_review_pack_data(),
            "assessment_blueprint": valid_assessment_blueprint_data(),
            "assessment": valid_assessment_data(),
            "answer_key": valid_answer_key_data(),
            "usage_records": usage_records or [],
            "budget_snapshot": RunBudgetSnapshot(),
        }
    )
