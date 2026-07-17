# SPDX-License-Identifier: MIT-0

"""Tests for the public metadata exposed by the txt2crs package.

These small tests intentionally come before the package implementation. They
define the first public contract: installed callers can discover the library
version without knowing anything about the repository layout.
"""

from importlib.metadata import version
from pathlib import Path

import pytest

import txt2crs


def _find_repository_version_file() -> Path | None:
    """Find the repository VERSION file without breaking exported test suites.

    A source distribution can be tested after it has been extracted away from
    the monorepo. In that case there is intentionally no repository-level
    VERSION file, so callers receive ``None`` instead of a guessed path.
    """

    for parent_directory in Path(__file__).resolve().parents:
        candidate_version_file = parent_directory / "VERSION"
        if candidate_version_file.is_file():
            return candidate_version_file
    return None


def _normalize_semantic_version_for_python(semantic_version: str) -> str:
    """Translate the project's documented prereleases to PEP 440 spellings."""

    prerelease_replacements = {
        "-dev.": ".dev",
        "-alpha.": "a",
        "-beta.": "b",
        "-rc.": "rc",
    }
    normalized_version = semantic_version
    for semantic_marker, python_marker in prerelease_replacements.items():
        normalized_version = normalized_version.replace(
            semantic_marker,
            python_marker,
        )
    return normalized_version


def test_public_version_matches_installed_distribution() -> None:
    """Keep ``txt2crs.__version__`` aligned with built package metadata."""

    assert txt2crs.__version__ == version("txt2crs")


def test_package_version_matches_repository_version_when_available() -> None:
    """Prevent release drift between root SemVer and Python package metadata."""

    repository_version_file = _find_repository_version_file()
    if repository_version_file is None:
        pytest.skip("The exported package does not include repository metadata.")

    repository_version = repository_version_file.read_text(encoding="utf-8").strip()
    expected_package_version = _normalize_semantic_version_for_python(
        repository_version,
    )

    assert txt2crs.__version__ == expected_package_version
