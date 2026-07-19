# SPDX-License-Identifier: MIT-0

"""Learner-controlled generation settings and pipeline result contracts."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from txt2crs.domain.models import StrictContract


class LearningPreferences(StrictContract):
    """Concrete accepted learning contract established from the course plan."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    audience: str = Field(min_length=1, max_length=2_000)
    prior_knowledge: str = Field(min_length=1, max_length=5_000)
    # A custom stored curriculum profile may permit every objective supported
    # by ``CoursePlan``. Derived goals therefore use the same 100-item ceiling
    # instead of the learner-intent transport limit of ten explicit goals.
    learning_goals: tuple[str, ...] = Field(min_length=1, max_length=100)
    level: Literal["beginner", "intermediate", "advanced", "mixed"]
    desired_depth: str = Field(min_length=1, max_length=500)
    duration_minutes: int = Field(gt=0, le=100_000)
    language: str = Field(min_length=2, max_length=35)
    tone: str = Field(min_length=1, max_length=200)
    accessibility_requirements: tuple[str, ...] = Field(min_length=1, max_length=100)
    assessment_item_count: int = Field(gt=0, le=1_000)
    passing_percentage: int = Field(ge=0, le=100)
    high_risk_course: bool

    @model_validator(mode="after")
    def require_unique_goals_and_accessibility_requirements(self) -> Self:
        """Keep set-like contract fields deterministic after acceptance."""

        normalized_goals = tuple(
            " ".join(learning_goal.casefold().split())
            for learning_goal in self.learning_goals
        )
        normalized_accessibility = tuple(
            " ".join(requirement.casefold().split())
            for requirement in self.accessibility_requirements
        )
        if len(normalized_goals) != len(set(normalized_goals)):
            raise ValueError("learning goals must be unique")
        if len(normalized_accessibility) != len(set(normalized_accessibility)):
            raise ValueError("accessibility requirements must be unique")
        return self
