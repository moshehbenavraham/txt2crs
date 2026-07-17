# SPDX-License-Identifier: MIT-0

"""Learner-controlled generation settings and pipeline result contracts."""

from pydantic import Field

from txt2crs.domain.models import StrictContract


class LearningPreferences(StrictContract):
    """Correctable learning contract established before curriculum design."""

    audience: str = Field(min_length=1, max_length=2_000)
    prior_knowledge: str = Field(min_length=1, max_length=5_000)
    desired_depth: str = Field(min_length=1, max_length=500)
    duration_minutes: int = Field(gt=0, le=100_000)
    language: str = Field(min_length=2, max_length=35)
    tone: str = Field(min_length=1, max_length=200)
    accessibility_requirements: list[str] = Field(max_length=100)
    assessment_item_count: int = Field(gt=0, le=1_000)
    passing_percentage: int = Field(ge=0, le=100)
    high_risk_course: bool
