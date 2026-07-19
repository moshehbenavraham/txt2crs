# SPDX-License-Identifier: MIT-0

"""Regression tests for the supported package-level composition contracts."""

import subprocess
import sys

import txt2crs.generation as generation_package
import txt2crs.jobs as jobs_package


def test_supported_generation_and_preparation_exports_load_cleanly() -> None:
    """A fresh process can import both sides without initialization order bugs."""

    import_script = """
from txt2crs.generation import (
    CourseGenerationPipeline,
    LearningPreferences,
    PreparedLearningPreferences,
)
from txt2crs.jobs import (
    CurriculumShapeLimits,
    GenerationPreparation,
    GenerationPreparationService,
    InputIngestionService,
    LearningPreferenceDefaults,
    PreparationPolicyError,
)
assert all(
    imported_contract is not None
    for imported_contract in (
        CourseGenerationPipeline,
        LearningPreferences,
        PreparedLearningPreferences,
        CurriculumShapeLimits,
        GenerationPreparation,
        GenerationPreparationService,
        InputIngestionService,
        LearningPreferenceDefaults,
        PreparationPolicyError,
    )
)
"""
    completed_process = subprocess.run(
        [sys.executable, "-c", import_script],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed_process.returncode == 0, completed_process.stderr


def test_internal_resolution_and_projection_helpers_are_not_exported() -> None:
    """Application composition cannot import private acceptance helpers."""

    assert "resolve_learning_preferences" not in generation_package.__all__
    assert "validate_module_content_block_shape" not in generation_package.__all__
    assert not hasattr(generation_package, "resolve_learning_preferences")
    assert not hasattr(generation_package, "validate_module_content_block_shape")
    assert "project_public_job_snapshot" not in jobs_package.__all__
