# SPDX-License-Identifier: MIT-0

"""Deterministic checks run before any educational artifact is accepted."""

from dataclasses import dataclass

from txt2crs.domain.models import AnswerKey, Assessment, Course
from txt2crs.research.evidence import (
    CitationValidationError,
    FrozenEvidenceSet,
    has_minimum_text_support,
    validate_claim_citations,
)


class ArtifactQualityError(ValueError):
    """Raised when a schema-valid artifact still fails product invariants."""


@dataclass(frozen=True, slots=True)
class CourseQualityReport:
    """Deterministic course metrics safe to persist with a checkpoint."""

    passed: bool
    objective_coverage: dict[str, float]
    citation_count: int
    section_count: int


@dataclass(frozen=True, slots=True)
class AssessmentQualityReport:
    """Deterministic assessment metrics safe to persist."""

    passed: bool
    total_points: int
    item_count: int


def validate_course_quality(
    course: Course,
    *,
    evidence_set: FrozenEvidenceSet,
    high_risk_course: bool,
) -> CourseQualityReport:
    """Check frozen evidence, objective coverage, claims, and duplication."""

    expected_sources = [
        source.model_dump(mode="json")
        for source in sorted(evidence_set.sources, key=lambda item: item.source_id)
    ]
    course_sources = [
        source.model_dump(mode="json")
        for source in sorted(course.sources, key=lambda item: item.source_id)
    ]
    expected_excerpts = [
        excerpt.model_dump(mode="json")
        for excerpt in sorted(
            evidence_set.excerpts,
            key=lambda item: item.evidence_id,
        )
    ]
    course_excerpts = [
        excerpt.model_dump(mode="json")
        for excerpt in sorted(course.evidence, key=lambda item: item.evidence_id)
    ]
    if course_sources != expected_sources or course_excerpts != expected_excerpts:
        raise ArtifactQualityError(
            "Course sources/evidence do not match the frozen research set."
        )

    objective_section_counts = {
        objective.objective_id: 0 for objective in course.learning_objectives
    }
    normalized_section_summaries: set[str] = set()
    factual_block_ids: set[str] = set()
    for course_module in course.modules:
        for section in course_module.sections:
            normalized_summary = " ".join(section.summary.casefold().split())
            if normalized_summary in normalized_section_summaries:
                raise ArtifactQualityError("Course contains duplicate section content.")
            normalized_section_summaries.add(normalized_summary)
            for objective_id in section.objective_ids:
                objective_section_counts[objective_id] += 1
            for content_block in section.content_blocks:
                if not content_block.is_model_generated_example:
                    factual_block_ids.add(content_block.block_id)
                    if not content_block.evidence_ids:
                        raise ArtifactQualityError(
                            f"Course block {content_block.block_id} lacks a citation."
                        )

    for objective_id, section_count in objective_section_counts.items():
        if section_count == 0:
            raise ArtifactQualityError(
                f"Learning objective {objective_id} has no course content."
            )

    cited_block_ids = {citation.artifact_location for citation in course.citations}
    missing_citation_blocks = factual_block_ids - cited_block_ids
    if missing_citation_blocks:
        missing_block_id = sorted(missing_citation_blocks)[0]
        raise ArtifactQualityError(
            f"Course block {missing_block_id} has no verified citation."
        )
    try:
        validate_claim_citations(
            citations=course.citations,
            evidence_set=evidence_set,
            unresolved_claims=course.unresolved_or_conflicting_claims,
            high_risk_course=high_risk_course,
        )
    except CitationValidationError as citation_error:
        raise ArtifactQualityError(str(citation_error)) from citation_error

    objective_coverage = {
        objective_id: 1.0 if section_count > 0 else 0.0
        for objective_id, section_count in objective_section_counts.items()
    }
    return CourseQualityReport(
        passed=True,
        objective_coverage=objective_coverage,
        citation_count=len(course.citations),
        section_count=sum(len(module.sections) for module in course.modules),
    )


def validate_assessment_quality(
    *,
    course: Course,
    assessment: Assessment,
    answer_key: AnswerKey,
) -> AssessmentQualityReport:
    """Check duplicates, leakage, choices, support, and aligned point totals."""

    if answer_key.assessment_id != assessment.assessment_id:
        raise ArtifactQualityError("Answer key does not match the assessment.")
    normalized_prompts = [
        " ".join(item.prompt.casefold().split()) for item in assessment.items
    ]
    if len(normalized_prompts) != len(set(normalized_prompts)):
        raise ArtifactQualityError("Assessment contains a duplicate item prompt.")

    answer_by_item_id = {answer.item_id: answer for answer in answer_key.answers}
    if set(answer_by_item_id) != {item.item_id for item in assessment.items}:
        raise ArtifactQualityError("Assessment and answer key items do not align.")
    evidence_by_id = {evidence.evidence_id: evidence for evidence in course.evidence}
    sections_by_id = {
        section.section_id: section
        for course_module in course.modules
        for section in course_module.sections
    }
    for assessment_item in assessment.items:
        normalized_prompt = " ".join(assessment_item.prompt.casefold().split())
        answer_entry = answer_by_item_id[assessment_item.item_id]
        normalized_options = {
            " ".join(option.casefold().split()) for option in assessment_item.options
        }
        normalized_correct_answers = {
            " ".join(answer.casefold().split())
            for answer in answer_entry.correct_answers
        }
        if assessment_item.item_type == "multiple_choice":
            if len(normalized_correct_answers) != 1:
                raise ArtifactQualityError(
                    f"Assessment item {assessment_item.item_id} must have one "
                    "correct option."
                )
            if not normalized_correct_answers <= normalized_options:
                raise ArtifactQualityError(
                    f"Assessment item {assessment_item.item_id} answer is not "
                    "one of its options."
                )
        elif assessment_item.item_type == "multiple_select":
            if not normalized_correct_answers <= normalized_options:
                raise ArtifactQualityError(
                    f"Assessment item {assessment_item.item_id} answers include "
                    "a value outside its options."
                )
        for correct_answer in answer_entry.correct_answers:
            normalized_answer = " ".join(correct_answer.casefold().split())
            if (
                assessment_item.item_type not in {"multiple_choice", "multiple_select"}
                and len(normalized_answer) >= 4
                and normalized_answer in normalized_prompt
            ):
                raise ArtifactQualityError(
                    f"Assessment item {assessment_item.item_id} leaks its answer."
                )

        # The model must name the exact canonical sections and evidence used
        # for the answer. Cross-artifact validation has already proven these
        # references exist and belong to the assessment item. This independent
        # text check then rejects an unrelated explanation even when all IDs
        # are syntactically valid.
        supporting_text_parts = [
            evidence_by_id[evidence_id].excerpt
            for evidence_id in answer_entry.evidence_ids
        ]
        for section_id in answer_entry.section_ids:
            section = sections_by_id[section_id]
            supporting_text_parts.extend(
                content_block.text for content_block in section.content_blocks
            )
            supporting_text_parts.append(section.summary)
        if not has_minimum_text_support(
            claim_text=answer_entry.explanation,
            evidence_text="\n".join(supporting_text_parts),
            high_risk_course=False,
        ):
            raise ArtifactQualityError(
                f"Answer explanation for {assessment_item.item_id} lacks "
                "independent course/evidence support."
            )

    return AssessmentQualityReport(
        passed=True,
        total_points=sum(item.points for item in assessment.items),
        item_count=len(assessment.items),
    )
