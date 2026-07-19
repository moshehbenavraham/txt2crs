# SPDX-License-Identifier: MIT-0

"""Deterministic learning-intent resolution and local curriculum gates."""

from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest

from tests.factories import valid_generation_request
from txt2crs.domain.models import CoursePlan
from txt2crs.generation.preferences import (
    NO_PREREQUISITE_KNOWLEDGE,
    PreferenceResolutionError,
    PreparedLearningPreferences,
    resolve_learning_preferences,
)
from txt2crs.jobs.requests import CurriculumShapeLimits, LearningPreferenceIntent


def _valid_course_plan_data() -> dict[str, Any]:
    """Return the smallest plan inside every documented P0 shape bound."""

    objectives = [
        {
            "objective_id": f"objective-{objective_number}",
            "description": f"Apply skill {objective_number}.",
            "assessed": True,
        }
        for objective_number in range(1, 6)
    ]
    return {
        "schema_version": "1.0",
        "plan_id": "plan-preferences",
        "course_id": "course-preferences",
        "title": "Applied Skills",
        "language": "he",
        "audience": "Independent adult learners",
        "level": "intermediate",
        "prerequisites": [],
        "duration_minutes": 120,
        "accessibility_requirements": [
            "Semantic headings",
            "Plain-language definitions",
            "Textual explanations of visual concepts",
        ],
        "learning_objectives": objectives,
        "modules": [
            {
                "module_id": f"module-{module_number}",
                "title": f"Module {module_number}",
                "objective_ids": (
                    ["objective-1", "objective-2"]
                    if module_number == 1
                    else (
                        ["objective-3", "objective-4"]
                        if module_number == 2
                        else ["objective-5"]
                    )
                ),
                "section_ids": [
                    f"module-{module_number}-section-1",
                    f"module-{module_number}-section-2",
                ],
            }
            for module_number in range(1, 4)
        ],
    }


def _limit_objectives_to_four(course_plan_data: dict[str, Any]) -> None:
    """Keep references valid while moving objective count below the P0 minimum."""

    course_plan_data["learning_objectives"] = course_plan_data["learning_objectives"][
        :4
    ]
    course_plan_data["modules"][2]["objective_ids"] = ["objective-4"]


def _limit_modules_to_two(course_plan_data: dict[str, Any]) -> None:
    """Keep every objective covered while moving module count below minimum."""

    course_plan_data["modules"] = course_plan_data["modules"][:2]
    course_plan_data["modules"][1]["objective_ids"].append("objective-5")


def _limit_first_module_to_one_section(
    course_plan_data: dict[str, Any],
) -> None:
    """Move one module below the stored section minimum."""

    course_plan_data["modules"][0]["section_ids"] = ["module-1-section-1"]


def test_auto_intent_resolves_from_input_and_accepted_course_plan() -> None:
    """Auto values become concrete once and retain every stored P0 default."""

    request = valid_generation_request(
        preferences=LearningPreferenceIntent(
            audience=None,
            prior_knowledge=None,
            learning_goals=(),
            level="auto",
            language="auto",
        )
    )
    planning_preferences = PreparedLearningPreferences.from_request(
        generation_request=request,
        detected_input_language="he",
        high_risk_course=False,
    )
    course_plan = CoursePlan.model_validate(_valid_course_plan_data())

    resolved = resolve_learning_preferences(
        planning_preferences=planning_preferences,
        course_plan=course_plan,
        shape_limits=request.execution_profile.curriculum_shape_limits,
    )

    assert planning_preferences.language == "he"
    assert resolved.audience == "Independent adult learners"
    assert resolved.prior_knowledge == NO_PREREQUISITE_KNOWLEDGE
    assert resolved.learning_goals == tuple(
        objective.description for objective in course_plan.learning_objectives
    )
    assert resolved.level == "intermediate"
    assert resolved.language == "he"
    assert resolved.duration_minutes == 120
    assert resolved.assessment_item_count == 15
    assert resolved.passing_percentage == 70
    assert resolved.high_risk_course is False


def test_explicit_preferences_are_preserved_after_normalized_alignment() -> None:
    """Whitespace/case normalization is deterministic, not semantic guessing."""

    explicit_goal = "Apply skill 1."
    request = valid_generation_request(
        preferences=LearningPreferenceIntent(
            audience="Independent adult learners",
            prior_knowledge="No prerequisite knowledge",
            learning_goals=(explicit_goal,),
            level="intermediate",
            language="he",
        )
    )
    planning_preferences = PreparedLearningPreferences.from_request(
        generation_request=request,
        detected_input_language="en",
        high_risk_course=False,
    )
    course_plan_data = _valid_course_plan_data()
    first_objective = course_plan_data["learning_objectives"]
    assert isinstance(first_objective, list)
    first_objective[0]["description"] = "  APPLY   SKILL 1.  "

    resolved = resolve_learning_preferences(
        planning_preferences=planning_preferences,
        course_plan=CoursePlan.model_validate(course_plan_data),
        shape_limits=request.execution_profile.curriculum_shape_limits,
    )

    assert resolved.audience == "Independent adult learners"
    assert resolved.prior_knowledge == "No prerequisite knowledge"
    assert resolved.learning_goals == (explicit_goal,)
    assert resolved.level == "intermediate"
    assert resolved.language == "he"


@pytest.mark.parametrize(
    ("field_name", "replacement", "error_code"),
    [
        ("language", "en", "language_mismatch"),
        ("audience", "A different audience", "audience_mismatch"),
        ("level", "advanced", "level_mismatch"),
        ("duration_minutes", 90, "duration_mismatch"),
        (
            "accessibility_requirements",
            ["Semantic headings"],
            "accessibility_mismatch",
        ),
    ],
)
def test_explicit_and_default_plan_drift_is_rejected_locally(
    field_name: str,
    replacement: object,
    error_code: str,
) -> None:
    """A schema-valid plan cannot silently ignore the learning contract."""

    request = valid_generation_request(
        preferences=LearningPreferenceIntent(
            audience="Independent adult learners",
            prior_knowledge=None,
            learning_goals=("Apply skill 1.",),
            level="intermediate",
            language="he",
        )
    )
    planning_preferences = PreparedLearningPreferences.from_request(
        generation_request=request,
        detected_input_language="he",
        high_risk_course=False,
    )
    course_plan_data = _valid_course_plan_data()
    course_plan_data[field_name] = replacement

    with pytest.raises(PreferenceResolutionError) as captured_error:
        resolve_learning_preferences(
            planning_preferences=planning_preferences,
            course_plan=CoursePlan.model_validate(course_plan_data),
            shape_limits=request.execution_profile.curriculum_shape_limits,
        )

    assert captured_error.value.code == error_code
    assert captured_error.value.__cause__ is None


def test_explicit_learning_goal_without_matching_objective_is_rejected() -> None:
    """P0 never substitutes semantic similarity for an enforceable mapping."""

    request = valid_generation_request(learning_goal="Build a complete program.")
    planning_preferences = PreparedLearningPreferences.from_request(
        generation_request=request,
        detected_input_language="he",
        high_risk_course=False,
    )

    with pytest.raises(PreferenceResolutionError) as captured_error:
        resolve_learning_preferences(
            planning_preferences=planning_preferences,
            course_plan=CoursePlan.model_validate(_valid_course_plan_data()),
            shape_limits=request.execution_profile.curriculum_shape_limits,
        )

    assert captured_error.value.code == "learning_goal_unmapped"


@pytest.mark.parametrize(
    ("mutate_plan", "error_code"),
    [
        (
            _limit_objectives_to_four,
            "objective_count_out_of_bounds",
        ),
        (
            _limit_modules_to_two,
            "module_count_out_of_bounds",
        ),
        (
            _limit_first_module_to_one_section,
            "section_count_out_of_bounds",
        ),
    ],
)
def test_curriculum_shape_drift_is_rejected_before_module_drafting(
    mutate_plan: Callable[[dict[str, Any]], None],
    error_code: str,
) -> None:
    """Objective, module, and section limits are local acceptance rules."""

    request = valid_generation_request(learning_goal="Apply skill 1.")
    planning_preferences = PreparedLearningPreferences.from_request(
        generation_request=request,
        detected_input_language="he",
        high_risk_course=False,
    )
    course_plan_data = deepcopy(_valid_course_plan_data())
    mutate_plan(course_plan_data)

    with pytest.raises(PreferenceResolutionError) as captured_error:
        resolve_learning_preferences(
            planning_preferences=planning_preferences,
            course_plan=CoursePlan.model_validate(course_plan_data),
            shape_limits=request.execution_profile.curriculum_shape_limits,
        )

    assert captured_error.value.code == error_code


def test_derived_goals_support_the_stored_objective_limit() -> None:
    """A valid custom profile cannot outgrow the concrete preference contract."""

    request = valid_generation_request(
        preferences=LearningPreferenceIntent(
            audience=None,
            prior_knowledge=None,
            learning_goals=(),
            level="auto",
            language="auto",
        )
    )
    planning_preferences = PreparedLearningPreferences.from_request(
        generation_request=request,
        detected_input_language="he",
        high_risk_course=False,
    )
    course_plan_data = _valid_course_plan_data()
    additional_objectives = [
        {
            "objective_id": f"objective-{objective_number}",
            "description": f"Apply skill {objective_number}.",
            "assessed": True,
        }
        for objective_number in range(6, 14)
    ]
    course_plan_data["learning_objectives"].extend(additional_objectives)
    course_plan_data["modules"][2]["objective_ids"].extend(
        objective["objective_id"] for objective in additional_objectives
    )
    shape_limits = CurriculumShapeLimits.model_validate(
        {
            **request.execution_profile.curriculum_shape_limits.model_dump(
                mode="python"
            ),
            "maximum_objectives": 13,
        }
    )

    resolved_preferences = resolve_learning_preferences(
        planning_preferences=planning_preferences,
        course_plan=CoursePlan.model_validate(course_plan_data),
        shape_limits=shape_limits,
    )

    assert len(resolved_preferences.learning_goals) == 13
