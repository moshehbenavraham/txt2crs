# SPDX-License-Identifier: MIT-0

"""Tests for versioned course-generation domain contracts."""

from typing import Any

import pytest
from pydantic import ValidationError

from tests.factories import (
    copy_data,
    valid_answer_key_data,
    valid_assessment_blueprint_data,
    valid_assessment_data,
    valid_course_data,
    valid_course_module_draft_data,
    valid_review_pack_data,
)
from txt2crs.domain.models import (
    AnswerKey,
    Assessment,
    AssessmentBlueprint,
    Course,
    CourseModuleDraft,
    InputDocument,
    ResearchPlan,
    ReviewPack,
)
from txt2crs.domain.validation import validate_artifact_bundle


@pytest.mark.parametrize(
    ("model_type", "valid_data"),
    [
        (Course, valid_course_data()),
        (CourseModuleDraft, valid_course_module_draft_data()),
        (ReviewPack, valid_review_pack_data()),
        (Assessment, valid_assessment_data()),
        (AssessmentBlueprint, valid_assessment_blueprint_data()),
        (AnswerKey, valid_answer_key_data()),
    ],
)
def test_artifact_models_round_trip_without_losing_data(
    model_type: (
        type[Course]
        | type[CourseModuleDraft]
        | type[ReviewPack]
        | type[Assessment]
        | type[AssessmentBlueprint]
        | type[AnswerKey]
    ),
    valid_data: dict[str, Any],
) -> None:
    """A validated artifact must serialize back to the same public contract."""

    artifact = model_type.model_validate(valid_data)

    assert artifact.model_dump(mode="json") == valid_data


def test_models_reject_unknown_fields() -> None:
    """Provider-added fields cannot silently change a versioned contract."""

    course_data = valid_course_data()
    course_data["provider_debug_trace"] = "must not enter the artifact"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        Course.model_validate(course_data)


def test_models_reject_unknown_schema_versions() -> None:
    """A future schema needs an explicit migration rather than best-effort parsing."""

    course_data = valid_course_data()
    course_data["schema_version"] = "2.0"

    with pytest.raises(ValidationError, match="Input should be '1.0'"):
        Course.model_validate(course_data)


def test_course_rejects_duplicate_and_broken_identifiers() -> None:
    """Stable IDs must be unique and every reference must resolve."""

    course_data = valid_course_data()
    duplicate_module = copy_data(course_data["modules"][0])
    course_data["modules"].append(duplicate_module)
    course_data["modules"][0]["objective_ids"] = ["obj-missing"]

    with pytest.raises(
        ValidationError,
        match="duplicate module_id|unknown objective_id",
    ):
        Course.model_validate(course_data)


def test_input_document_rejects_empty_or_oversized_normalized_text() -> None:
    """Ingestion cannot silently accept an empty result or an unbounded payload."""

    common_fields: dict[str, Any] = {
        "schema_version": "1.0",
        "document_id": "input-1",
        "input_type": "text",
        "media_type": "text/plain",
        "language": "en",
        "metadata": {},
        "content_hash": "sha256:" + ("c" * 64),
        "warnings": [],
        "locations": [],
    }

    with pytest.raises(ValidationError):
        InputDocument.model_validate({**common_fields, "normalized_text": ""})

    with pytest.raises(ValidationError):
        InputDocument.model_validate(
            {**common_fields, "normalized_text": "x" * 2_000_001}
        )


def test_research_plan_requires_unique_questions() -> None:
    """A research plan cannot spend the budget on a repeated question."""

    with pytest.raises(ValidationError, match="duplicate research question"):
        ResearchPlan.model_validate(
            {
                "schema_version": "1.0",
                "plan_id": "plan-1",
                "questions": [
                    {
                        "question_id": "q-1",
                        "question": "What is assignment?",
                        "preferred_source_types": ["official_documentation"],
                        "freshness_days": None,
                    },
                    {
                        "question_id": "q-2",
                        "question": "What is assignment?",
                        "preferred_source_types": ["official_documentation"],
                        "freshness_days": None,
                    },
                ],
                "maximum_sources": 4,
                "stop_criteria": ["Every objective has evidence"],
            }
        )


def test_research_plan_requires_positive_limits() -> None:
    """A zero-source plan cannot meet the package's research promise."""

    with pytest.raises(ValidationError, match="greater than 0"):
        ResearchPlan.model_validate(
            {
                "schema_version": "1.0",
                "plan_id": "plan-1",
                "questions": [
                    {
                        "question_id": "q-1",
                        "question": "What is assignment?",
                        "preferred_source_types": ["official_documentation"],
                        "freshness_days": None,
                    }
                ],
                "maximum_sources": 0,
                "stop_criteria": ["Every objective has evidence"],
            }
        )


def test_bundle_validation_proves_cross_artifact_traceability() -> None:
    """One approved course must anchor review, assessment, and answer artifacts."""

    validated_bundle = validate_artifact_bundle(
        course=Course.model_validate(valid_course_data()),
        review_pack=ReviewPack.model_validate(valid_review_pack_data()),
        assessment=Assessment.model_validate(valid_assessment_data()),
        answer_key=AnswerKey.model_validate(valid_answer_key_data()),
    )

    assert validated_bundle.course.course_id == "course-python-basics"


def test_bundle_validation_rejects_missing_objective_coverage() -> None:
    """Every assessed course objective needs review and assessment coverage."""

    assessment_data = valid_assessment_data()
    assessment_data["blueprint"] = []
    assessment_data["items"] = []

    with pytest.raises(ValueError, match="obj-variables.*assessment"):
        validate_artifact_bundle(
            course=Course.model_validate(valid_course_data()),
            review_pack=ReviewPack.model_validate(valid_review_pack_data()),
            assessment=Assessment.model_validate(assessment_data),
            answer_key=AnswerKey.model_validate(
                {
                    **valid_answer_key_data(),
                    "answers": [],
                }
            ),
        )


def test_bundle_validation_rejects_answer_key_drift() -> None:
    """Instructor answers may not refer to missing or duplicate student items."""

    answer_key_data = valid_answer_key_data()
    answer_key_data["answers"][0]["item_id"] = "item-does-not-exist"

    with pytest.raises(ValueError, match="answer key.*item"):
        validate_artifact_bundle(
            course=Course.model_validate(valid_course_data()),
            review_pack=ReviewPack.model_validate(valid_review_pack_data()),
            assessment=Assessment.model_validate(valid_assessment_data()),
            answer_key=AnswerKey.model_validate(answer_key_data),
        )


def test_bundle_validation_rejects_answer_support_outside_the_course() -> None:
    """Instructor answers may reference only approved sections and evidence."""

    answer_key_data = valid_answer_key_data()
    answer_key_data["answers"][0]["evidence_ids"] = ["ev-not-approved"]

    with pytest.raises(ValueError, match="answer evidence"):
        validate_artifact_bundle(
            course=Course.model_validate(valid_course_data()),
            review_pack=ReviewPack.model_validate(valid_review_pack_data()),
            assessment=Assessment.model_validate(valid_assessment_data()),
            answer_key=AnswerKey.model_validate(answer_key_data),
        )
