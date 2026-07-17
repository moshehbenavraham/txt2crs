# SPDX-License-Identifier: MIT-0

"""Tests for deterministic education and cross-artifact quality gates."""

import pytest

from tests.factories import (
    valid_answer_key_data,
    valid_assessment_data,
    valid_course_data,
)
from txt2crs.domain.models import AnswerKey, Assessment, Course
from txt2crs.generation.quality import (
    ArtifactQualityError,
    validate_assessment_quality,
    validate_course_quality,
)
from txt2crs.research.evidence import EvidenceLedger, FrozenEvidenceSet


def frozen_evidence_for_course(course: Course) -> FrozenEvidenceSet:
    """Freeze exactly the source/evidence records embedded in a course."""

    ledger = EvidenceLedger()
    for source in course.sources:
        ledger.add_source(source)
    for excerpt in course.evidence:
        ledger.add_excerpt(excerpt)
    return ledger.freeze()


def test_course_quality_accepts_objective_coverage_and_citations() -> None:
    """A traced course passes deterministic checks without model self-grading."""

    course = Course.model_validate(valid_course_data())

    report = validate_course_quality(
        course,
        evidence_set=frozen_evidence_for_course(course),
        high_risk_course=False,
    )

    assert report.passed is True
    assert report.objective_coverage == {"obj-variables": 1.0}
    assert report.citation_count == 1


def test_course_quality_rejects_uncovered_objectives() -> None:
    """Every declared objective must map to actual lesson content."""

    course_data = valid_course_data()
    course_data["learning_objectives"].append(
        {
            "objective_id": "obj-loops",
            "description": "Use loops.",
            "assessed": True,
        }
    )
    course = Course.model_validate(course_data)

    with pytest.raises(ArtifactQualityError, match="obj-loops"):
        validate_course_quality(
            course,
            evidence_set=frozen_evidence_for_course(course),
            high_risk_course=False,
        )


def test_course_quality_rejects_uncited_factual_blocks() -> None:
    """Externally verifiable teaching claims cannot ship without evidence."""

    course_data = valid_course_data()
    course_data["modules"][0]["sections"][0]["content_blocks"][0]["evidence_ids"] = []
    course = Course.model_validate(course_data)

    with pytest.raises(ArtifactQualityError, match="citation"):
        validate_course_quality(
            course,
            evidence_set=frozen_evidence_for_course(course),
            high_risk_course=False,
        )


def test_assessment_quality_rejects_duplicate_prompts_and_answer_leakage() -> None:
    """Students cannot receive repeated items or answers embedded in prompts."""

    assessment_data = valid_assessment_data()
    duplicated_item = {
        **assessment_data["items"][0],
        "item_id": "item-variable-copy",
    }
    assessment_data["items"].append(duplicated_item)
    assessment_data["blueprint"][0]["item_count"] = 2
    assessment_data["blueprint"][0]["total_points"] = 10
    duplicate_assessment = Assessment.model_validate(assessment_data)

    with pytest.raises(ArtifactQualityError, match="duplicate"):
        validate_assessment_quality(
            course=Course.model_validate(valid_course_data()),
            assessment=duplicate_assessment,
            answer_key=AnswerKey.model_validate(
                {
                    **valid_answer_key_data(),
                    "answers": [
                        *valid_answer_key_data()["answers"],
                        {
                            **valid_answer_key_data()["answers"][0],
                            "item_id": "item-variable-copy",
                        },
                    ],
                }
            ),
        )

    leaked_assessment_data = valid_assessment_data()
    leaked_assessment_data["items"][0]["prompt"] = (
        "The answer is class_size = 24. Explain it."
    )
    with pytest.raises(ArtifactQualityError, match="leaks"):
        validate_assessment_quality(
            course=Course.model_validate(valid_course_data()),
            assessment=Assessment.model_validate(leaked_assessment_data),
            answer_key=AnswerKey.model_validate(valid_answer_key_data()),
        )


def test_assessment_quality_accepts_full_bundle_traceability() -> None:
    """The valid fixture provides separate, aligned student/instructor forms."""

    report = validate_assessment_quality(
        course=Course.model_validate(valid_course_data()),
        assessment=Assessment.model_validate(valid_assessment_data()),
        answer_key=AnswerKey.model_validate(valid_answer_key_data()),
    )

    assert report.passed is True
    assert report.total_points == 5


def test_assessment_quality_rejects_unsupported_answer_explanations() -> None:
    """Answer prose must overlap the exact approved section/evidence support."""

    answer_key_data = valid_answer_key_data()
    answer_key_data["answers"][0]["explanation"] = (
        "Photosynthesis turns light into chemical energy."
    )

    with pytest.raises(ArtifactQualityError, match="support"):
        validate_assessment_quality(
            course=Course.model_validate(valid_course_data()),
            assessment=Assessment.model_validate(valid_assessment_data()),
            answer_key=AnswerKey.model_validate(answer_key_data),
        )


def test_assessment_quality_rejects_choice_answers_missing_from_options() -> None:
    """A choice answer cannot name a value the learner was never offered."""

    assessment_data = valid_assessment_data()
    assessment_data["items"][0].update(
        {
            "item_type": "multiple_choice",
            "prompt": "Which statement assigns 24 to class_size?",
            "options": ["class_size = 24", "print(class_size)"],
        }
    )
    answer_key_data = valid_answer_key_data()
    answer_key_data["answers"][0]["correct_answers"] = ["missing_option = 24"]

    with pytest.raises(ArtifactQualityError, match="option"):
        validate_assessment_quality(
            course=Course.model_validate(valid_course_data()),
            assessment=Assessment.model_validate(assessment_data),
            answer_key=AnswerKey.model_validate(answer_key_data),
        )
