# SPDX-License-Identifier: MIT-0

"""Staged, evidence-grounded course and assessment generation."""

from typing import Any

from txt2crs.generation.models import LearningPreferences
from txt2crs.generation.preferences import PreparedLearningPreferences

_PIPELINE_EXPORTS = frozenset({"CourseGenerationPipeline"})


def __getattr__(name: str) -> Any:
    """Load the preparation-dependent pipeline without an import cycle.

    ``jobs.preparation`` stores ``PreparedLearningPreferences`` and the
    pipeline consumes ``GenerationPreparation``. Importing both eagerly from
    their package initializers would leave one module only partially defined.
    """

    if name not in _PIPELINE_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from txt2crs.generation import pipeline

    return getattr(pipeline, name)


__all__ = [
    "CourseGenerationPipeline",
    "LearningPreferences",
    "PreparedLearningPreferences",
]
