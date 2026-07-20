"""Acceptance fixtures backed by the shared deterministic course scenario."""

from pathlib import Path

import pytest

# These class imports are intentionally re-exported. Existing acceptance tests
# import the harness types from this conftest, while new shell-browser tests use
# the shared support module directly.
from tests.support.deterministic_course import (
    DurableResultsHarness,
    DurableSubmissionHarness,
    build_durable_results_harness,
    build_durable_submission_harness,
)


@pytest.fixture()
def durable_submission_harness(tmp_path: Path) -> DurableSubmissionHarness:
    """Provide isolated durable state for one acceptance test."""

    return build_durable_submission_harness(tmp_path / "state")


@pytest.fixture()
def durable_results_harness(tmp_path: Path) -> DurableResultsHarness:
    """Provide one complete isolated deterministic result/recovery harness."""

    return build_durable_results_harness(tmp_path / "state")
