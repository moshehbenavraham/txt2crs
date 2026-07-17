# SPDX-License-Identifier: MIT-0

"""Tests for the fixed, versioned evaluation corpus shipped in the wheel."""

from hashlib import sha256
from importlib.resources import files
from typing import get_args

from txt2crs.evals.cases import built_in_evaluation_cases
from txt2crs.evals.models import EvaluationCase


def test_built_in_cases_cover_every_required_failure_and_content_category() -> None:
    """The documented replay matrix must be concrete rather than aspirational."""

    cases = built_in_evaluation_cases()
    declared_categories = set(
        get_args(EvaluationCase.model_fields["category"].annotation)
    )

    assert {evaluation_case.category for evaluation_case in cases} == (
        declared_categories
    )
    assert "noisy_extraction" in declared_categories
    assert len({evaluation_case.case_id for evaluation_case in cases}) == len(cases)
    assert all(evaluation_case.case_version == "eval-v1" for evaluation_case in cases)


def test_every_built_in_case_points_to_a_packaged_hash_matching_fixture() -> None:
    """A replay case cannot silently drift away from its immutable input hash."""

    fixture_root = files("txt2crs.evals").joinpath("fixtures")

    for evaluation_case in built_in_evaluation_cases():
        fixture_name = evaluation_case.private_input_reference.removeprefix(
            "package://txt2crs.evals/fixtures/"
        )
        fixture_bytes = fixture_root.joinpath(fixture_name).read_bytes()

        assert evaluation_case.private_input_reference.startswith(
            "package://txt2crs.evals/fixtures/"
        )
        assert evaluation_case.input_hash == (
            f"sha256:{sha256(fixture_bytes).hexdigest()}"
        )
        assert fixture_bytes
