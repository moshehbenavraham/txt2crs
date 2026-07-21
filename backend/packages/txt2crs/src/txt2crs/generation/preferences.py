# SPDX-License-Identifier: MIT-0

"""Immutable pre-plan preferences and deterministic course-plan resolution."""

import re
from typing import Literal, NoReturn, Self

from pydantic import ConfigDict, Field, model_validator

from txt2crs.domain.models import (
    CourseModuleDraft,
    CoursePlan,
    HashValue,
    StrictContract,
)
from txt2crs.generation.models import LearningPreferences
from txt2crs.jobs.requests import (
    CurriculumShapeLimits,
    GenerationRequest,
)

NO_PREREQUISITE_KNOWLEDGE = "No prerequisite knowledge."

# These noun phrases describe a broad aspiration but do not identify an
# observable learner performance. They are accepted when the same objective
# also contains a concrete action such as "build" or "compare".
_VAGUE_OBJECTIVE_TERMS = frozenset(
    {"familiarity", "knowledge", "mastery", "proficiency", "understanding"}
)
_MEASURABLE_OBJECTIVE_VERBS = frozenset(
    {
        "analyze",
        "apply",
        "build",
        "calculate",
        "classify",
        "compare",
        "construct",
        "create",
        "debug",
        "define",
        "demonstrate",
        "describe",
        "design",
        "differentiate",
        "evaluate",
        "explain",
        "identify",
        "implement",
        "interpret",
        "predict",
        "solve",
        "trace",
        "use",
        "validate",
        "write",
    }
)
_GOAL_ALIGNMENT_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "be",
        "coding",
        "complete",
        "in",
        "intermediate",
        "of",
        "proficiency",
        "the",
        "to",
        "with",
    }
)


class PreferenceResolutionError(ValueError):
    """A safe local course-plan rejection without learner or model content."""

    def __init__(self, *, code: str) -> None:
        self.code = code
        super().__init__("The course plan did not satisfy the learning contract.")


class PreparedLearningPreferences(StrictContract):
    """Pre-plan intent and server defaults frozen after input ingestion."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    request_hash: HashValue
    audience: str | None = Field(default=None, max_length=500)
    prior_knowledge: str | None = Field(default=None, max_length=2_000)
    learning_goals: tuple[str, ...] = Field(max_length=10)
    level: Literal["auto", "beginner", "intermediate", "advanced", "mixed"]
    language: str = Field(min_length=2, max_length=35)
    desired_depth: str = Field(min_length=1, max_length=2_000)
    duration_minutes: int = Field(gt=0, le=100_000)
    tone: str = Field(min_length=1, max_length=200)
    accessibility_requirements: tuple[str, ...] = Field(
        min_length=1,
        max_length=20,
    )
    assessment_item_count: int = Field(gt=0, le=1_000)
    passing_percentage: int = Field(ge=0, le=100)
    high_risk_course: bool

    @classmethod
    def from_request(
        cls,
        *,
        generation_request: GenerationRequest,
        detected_input_language: str,
        high_risk_course: bool,
    ) -> Self:
        """Freeze input-dependent and server-selected values exactly once."""

        resolved_language = (
            detected_input_language
            if generation_request.preferences.language == "auto"
            else generation_request.preferences.language
        )
        preference_defaults = generation_request.execution_profile.preference_defaults
        return cls(
            request_hash=generation_request.request_hash,
            audience=generation_request.preferences.audience,
            prior_knowledge=generation_request.preferences.prior_knowledge,
            learning_goals=generation_request.preferences.learning_goals,
            level=generation_request.preferences.level,
            language=resolved_language,
            desired_depth=preference_defaults.desired_depth,
            duration_minutes=preference_defaults.duration_minutes,
            tone=preference_defaults.tone,
            accessibility_requirements=(preference_defaults.accessibility_requirements),
            assessment_item_count=preference_defaults.assessment_item_count,
            passing_percentage=preference_defaults.passing_percentage,
            high_risk_course=high_risk_course,
        )

    @model_validator(mode="after")
    def require_unique_set_like_values(self) -> Self:
        """Reject ambiguous goal or accessibility duplicates before persistence."""

        _require_normalized_unique(self.learning_goals, field_name="learning goals")
        _require_normalized_unique(
            self.accessibility_requirements,
            field_name="accessibility requirements",
        )
        return self


def resolve_learning_preferences(
    *,
    planning_preferences: PreparedLearningPreferences,
    course_plan: CoursePlan,
    shape_limits: CurriculumShapeLimits,
) -> LearningPreferences:
    """Resolve one locally accepted course plan into a concrete contract."""

    _validate_course_plan_shape(course_plan=course_plan, shape_limits=shape_limits)
    _require_aligned_text(
        expected=planning_preferences.language,
        actual=course_plan.language,
        error_code="language_mismatch",
    )
    if planning_preferences.audience is not None:
        _require_aligned_text(
            expected=planning_preferences.audience,
            actual=course_plan.audience,
            error_code="audience_mismatch",
        )
        resolved_audience = planning_preferences.audience
    else:
        resolved_audience = course_plan.audience

    resolved_prior_knowledge = _resolve_prior_knowledge(
        explicit_prior_knowledge=planning_preferences.prior_knowledge,
        course_plan=course_plan,
    )
    if planning_preferences.level != "auto":
        _require_aligned_text(
            expected=planning_preferences.level,
            actual=course_plan.level,
            error_code="level_mismatch",
        )
    resolved_level = course_plan.level

    if course_plan.duration_minutes != planning_preferences.duration_minutes:
        _reject("duration_mismatch")
    if {
        _normalize_alignment_text(requirement)
        for requirement in course_plan.accessibility_requirements
    } != {
        _normalize_alignment_text(requirement)
        for requirement in planning_preferences.accessibility_requirements
    }:
        _reject("accessibility_mismatch")

    resolved_learning_goals = _resolve_learning_goals(
        explicit_learning_goals=planning_preferences.learning_goals,
        course_plan=course_plan,
    )
    return LearningPreferences(
        audience=resolved_audience,
        prior_knowledge=resolved_prior_knowledge,
        learning_goals=resolved_learning_goals,
        level=resolved_level,
        desired_depth=planning_preferences.desired_depth,
        duration_minutes=planning_preferences.duration_minutes,
        language=planning_preferences.language,
        tone=planning_preferences.tone,
        accessibility_requirements=(planning_preferences.accessibility_requirements),
        assessment_item_count=planning_preferences.assessment_item_count,
        passing_percentage=planning_preferences.passing_percentage,
        high_risk_course=planning_preferences.high_risk_course,
    )


def validate_module_content_block_shape(
    *,
    module_draft: CourseModuleDraft,
    shape_limits: CurriculumShapeLimits,
) -> None:
    """Reject a module whose section prose exceeds the stored P0 shape."""

    for section in module_draft.module.sections:
        content_block_count = len(section.content_blocks)
        if not (
            shape_limits.minimum_content_blocks_per_section
            <= content_block_count
            <= shape_limits.maximum_content_blocks_per_section
        ):
            _reject("content_block_count_out_of_bounds")


def _validate_course_plan_shape(
    *,
    course_plan: CoursePlan,
    shape_limits: CurriculumShapeLimits,
) -> None:
    """Enforce finite objective, module, and section ranges before drafting."""

    objective_count = len(course_plan.learning_objectives)
    if not (
        shape_limits.minimum_objectives
        <= objective_count
        <= shape_limits.maximum_objectives
    ):
        _reject("objective_count_out_of_bounds")

    normalized_objective_descriptions = [
        _normalize_alignment_text(objective.description)
        for objective in course_plan.learning_objectives
    ]
    if len(normalized_objective_descriptions) != len(
        set(normalized_objective_descriptions)
    ):
        _reject("objective_description_duplicate")
    for normalized_description in normalized_objective_descriptions:
        description_terms = set(re.findall(r"[a-z]+", normalized_description))
        if (
            description_terms & _VAGUE_OBJECTIVE_TERMS
            and not description_terms & _MEASURABLE_OBJECTIVE_VERBS
        ):
            _reject("objective_description_not_measurable")

    module_count = len(course_plan.modules)
    if not (
        shape_limits.minimum_modules <= module_count <= shape_limits.maximum_modules
    ):
        _reject("module_count_out_of_bounds")

    for module in course_plan.modules:
        section_count = len(module.section_ids)
        if not (
            shape_limits.minimum_sections_per_module
            <= section_count
            <= shape_limits.maximum_sections_per_module
        ):
            _reject("section_count_out_of_bounds")


def _resolve_prior_knowledge(
    *,
    explicit_prior_knowledge: str | None,
    course_plan: CoursePlan,
) -> str:
    """Preserve explicit prerequisites or derive one stable plan summary."""

    if explicit_prior_knowledge is None:
        if not course_plan.prerequisites:
            return NO_PREREQUISITE_KNOWLEDGE
        return "; ".join(course_plan.prerequisites)

    normalized_explicit = _normalize_alignment_text(explicit_prior_knowledge)
    no_prerequisite_phrases = {
        _normalize_alignment_text(NO_PREREQUISITE_KNOWLEDGE),
        "no prerequisite knowledge",
        "none",
    }
    normalized_plan_prerequisites = {
        _normalize_alignment_text(prerequisite)
        for prerequisite in course_plan.prerequisites
    }
    if normalized_explicit in no_prerequisite_phrases:
        if normalized_plan_prerequisites:
            _reject("prior_knowledge_mismatch")
    elif normalized_explicit not in normalized_plan_prerequisites:
        _reject("prior_knowledge_mismatch")
    return explicit_prior_knowledge


def _resolve_learning_goals(
    *,
    explicit_learning_goals: tuple[str, ...],
    course_plan: CoursePlan,
) -> tuple[str, ...]:
    """Map explicit goals exactly or derive plan objectives for auto intent."""

    objective_descriptions = tuple(
        objective.description for objective in course_plan.learning_objectives
    )
    if not explicit_learning_goals:
        return objective_descriptions
    objective_term_sets = [
        _alignment_terms(description) for description in objective_descriptions
    ]
    if any(
        not any(
            _alignment_terms(learning_goal) & objective_terms
            for objective_terms in objective_term_sets
        )
        for learning_goal in explicit_learning_goals
    ):
        _reject("learning_goal_unmapped")
    return explicit_learning_goals


def _alignment_terms(value: str) -> set[str]:
    """Return stable topic words for a conservative goal-to-plan check."""

    return {
        term
        for term in re.findall(r"[a-z0-9]+", value.casefold())
        if len(term) >= 3 and term not in _GOAL_ALIGNMENT_STOP_WORDS
    }


def _require_aligned_text(
    *,
    expected: str,
    actual: str,
    error_code: str,
) -> None:
    """Compare contract text using only deterministic whitespace and case."""

    if _normalize_alignment_text(expected) != _normalize_alignment_text(actual):
        _reject(error_code)


def _reject(error_code: str) -> NoReturn:
    """Raise one context-free local acceptance error."""

    raise PreferenceResolutionError(code=error_code)


def _require_normalized_unique(values: tuple[str, ...], *, field_name: str) -> None:
    """Require one deterministic representation for set-like text values."""

    normalized_values = tuple(_normalize_alignment_text(value) for value in values)
    if len(normalized_values) != len(set(normalized_values)):
        raise ValueError(f"{field_name} must be unique")


def _normalize_alignment_text(value: str) -> str:
    """Normalize only whitespace and case; never guess semantic similarity."""

    return " ".join(value.casefold().split())


__all__ = [
    "NO_PREREQUISITE_KNOWLEDGE",
    "PreferenceResolutionError",
    "PreparedLearningPreferences",
    "resolve_learning_preferences",
    "validate_module_content_block_shape",
]
