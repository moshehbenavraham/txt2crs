# SPDX-License-Identifier: MIT-0

"""Small, reusable dictionaries for contract and pipeline tests.

The production models deliberately reject unknown fields and broken references.
Keeping one valid example in this module makes individual tests easier to read:
each test can change only the field whose behavior it is proving.
"""

from copy import deepcopy
from hashlib import sha256
from typing import Any

from txt2crs.ingestion.models import InputPayload
from txt2crs.jobs.quota import AdmissionLimits, AdmissionReservation
from txt2crs.jobs.requests import (
    ExecutionProfile,
    GenerationRequest,
    InputExecutionLimits,
    LearnerAgeGroup,
    LearningPreferenceIntent,
    RequestRetryPolicy,
    RunExecutionLimits,
)


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
