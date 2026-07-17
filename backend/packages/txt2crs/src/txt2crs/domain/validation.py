# SPDX-License-Identifier: MIT-0

"""Deterministic validation across course, review, and assessment artifacts."""

from dataclasses import dataclass

from txt2crs.domain.models import AnswerKey, Assessment, Course, ReviewPack


@dataclass(frozen=True, slots=True)
class ArtifactBundle:
    """A fully cross-validated set of required learner deliverables."""

    course: Course
    review_pack: ReviewPack
    assessment: Assessment
    answer_key: AnswerKey


def validate_artifact_bundle(
    *,
    course: Course,
    review_pack: ReviewPack,
    assessment: Assessment,
    answer_key: AnswerKey,
) -> ArtifactBundle:
    """Prove shared IDs and required objective coverage before rendering."""

    if review_pack.course_id != course.course_id:
        raise ValueError("review pack course_id does not match the approved course")
    if assessment.course_id != course.course_id:
        raise ValueError("assessment course_id does not match the approved course")
    if answer_key.assessment_id != assessment.assessment_id:
        raise ValueError("answer key assessment_id does not match the assessment")

    objective_ids = {objective.objective_id for objective in course.learning_objectives}
    assessed_objective_ids = {
        objective.objective_id
        for objective in course.learning_objectives
        if objective.assessed
    }
    section_ids = {
        section.section_id
        for course_module in course.modules
        for section in course_module.sections
    }
    source_ids = {source.source_id for source in course.sources}
    evidence_ids = {evidence.evidence_id for evidence in course.evidence}

    review_objective_ids = {item.objective_id for item in review_pack.study_guide} | {
        flashcard.objective_id for flashcard in review_pack.flashcards
    }
    missing_review_objectives = assessed_objective_ids - review_objective_ids
    if missing_review_objectives:
        missing_id = sorted(missing_review_objectives)[0]
        raise ValueError(f"{missing_id} is missing from review material")

    assessment_objective_ids = {item.objective_id for item in assessment.items} | {
        entry.objective_id for entry in assessment.blueprint
    }
    missing_assessment_objectives = assessed_objective_ids - assessment_objective_ids
    if missing_assessment_objectives:
        missing_id = sorted(missing_assessment_objectives)[0]
        raise ValueError(f"{missing_id} is missing from the assessment")

    _require_subset(
        "review objective",
        review_objective_ids,
        objective_ids,
    )
    _require_subset(
        "assessment objective",
        assessment_objective_ids,
        objective_ids,
    )

    for study_guide_item in review_pack.study_guide:
        _require_subset(
            "review section",
            set(study_guide_item.section_ids),
            section_ids,
        )
        _require_subset(
            "review source",
            set(study_guide_item.source_ids),
            source_ids,
        )
    for flashcard in review_pack.flashcards:
        _require_subset("flashcard section", set(flashcard.section_ids), section_ids)
    for exercise in [
        *review_pack.worked_examples,
        *review_pack.practice_exercises,
    ]:
        _require_subset("exercise section", set(exercise.section_ids), section_ids)
    _require_subset(
        "section summary",
        set(review_pack.section_summaries),
        section_ids,
    )

    for item in assessment.items:
        _require_subset("assessment section", set(item.section_ids), section_ids)
        _require_subset("assessment evidence", set(item.evidence_ids), evidence_ids)

    assessment_item_ids = {item.item_id for item in assessment.items}
    answer_item_ids = {answer.item_id for answer in answer_key.answers}
    if answer_item_ids != assessment_item_ids:
        raise ValueError("answer key item references do not match assessment items")

    item_by_id = {item.item_id: item for item in assessment.items}
    item_points = {item.item_id: item.points for item in assessment.items}
    for answer in answer_key.answers:
        assessment_item = item_by_id[answer.item_id]
        _require_subset(
            "answer section",
            set(answer.section_ids),
            set(assessment_item.section_ids),
        )
        _require_subset(
            "answer evidence",
            set(answer.evidence_ids),
            set(assessment_item.evidence_ids),
        )
        if (
            sum(criterion.points for criterion in answer.rubric)
            != item_points[answer.item_id]
        ):
            raise ValueError(
                f"answer key rubric points do not match item {answer.item_id}"
            )

    return ArtifactBundle(
        course=course,
        review_pack=review_pack,
        assessment=assessment,
        answer_key=answer_key,
    )


def _require_subset(
    reference_name: str,
    referenced_ids: set[str],
    known_ids: set[str],
) -> None:
    """Reject the first stable ID that has no canonical target."""

    unknown_ids = referenced_ids - known_ids
    if unknown_ids:
        unknown_id = sorted(unknown_ids)[0]
        raise ValueError(f"unknown {reference_name} reference: {unknown_id}")
