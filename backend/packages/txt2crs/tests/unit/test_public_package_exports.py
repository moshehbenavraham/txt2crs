# SPDX-License-Identifier: MIT-0

"""Regression tests for the supported package-level composition contracts."""

import subprocess
import sys

import txt2crs
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


def test_public_application_facade_and_factories_import_cleanly() -> None:
    """A shell needs only the documented application package boundary."""

    import_script = """
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationExecutor,
    ApplicationFactory,
    ApplicationStorageConfig,
    DeterministicApplicationConfig,
    DeterministicApplicationFactory,
    OwnerPurgeResult,
    RealApplicationConfig,
    RealApplicationFactory,
    SystemAuthenticationError,
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
    Txt2CrsApplication,
)
assert all(
    imported_contract is not None
    for imported_contract in (
        ApplicationAdmissionConfig,
        ApplicationExecutor,
        ApplicationFactory,
        ApplicationStorageConfig,
        DeterministicApplicationConfig,
        DeterministicApplicationFactory,
        OwnerPurgeResult,
        RealApplicationConfig,
        RealApplicationFactory,
        SystemAuthenticationError,
        SystemAuthenticationSnapshot,
        SystemAuthenticationState,
        Txt2CrsApplication,
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


def test_top_level_package_lazily_exports_application_entrypoints() -> None:
    """Shell startup can discover the facade without eager provider imports."""

    import_script = """
import sys
import txt2crs
assert "txt2crs.application" not in sys.modules
assert txt2crs.Txt2CrsApplication is not None
assert "txt2crs.application" in sys.modules
"""
    completed_process = subprocess.run(
        [sys.executable, "-c", import_script],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed_process.returncode == 0, completed_process.stderr
    assert txt2crs.Txt2CrsApplication is not None
    assert txt2crs.RealApplicationFactory is not None
    assert txt2crs.DeterministicApplicationFactory is not None
    assert "Txt2CrsApplication" in txt2crs.__all__
