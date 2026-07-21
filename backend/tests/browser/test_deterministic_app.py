"""Browser-server contracts for the credential-free learner journey.

The browser test server must exercise the same FastAPI routes, authentication,
SQLite job store, serial worker, and public package facade as production. It
is deliberately defined under ``tests/`` so production imports cannot expose
its scenario controls by accident.
"""

from collections.abc import Iterator
from pathlib import Path
from stat import S_IMODE
from time import monotonic, sleep

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_db
from app.core.config import settings
from app.main import app as production_app
from tests.browser.deterministic_app import create_deterministic_browser_app
from tests.utils.user import authentication_token_from_email


def _submission_payload() -> dict[str, object]:
    """Return one complete learner request accepted by the real route."""

    return {
        "input": {
            "type": "prompt",
            "value": "Teach Python variables.",
        },
        "preferences": {
            "level": "auto",
            "audience": None,
            "prior_knowledge": None,
            "learning_goals": ["Explain and use Python variables."],
            "language": "auto",
        },
        "consent_to_ai_processing": True,
        "learner_age_group": "adult",
    }


@pytest.fixture()
def deterministic_browser_app(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> FastAPI:
    """Create one explicitly enabled, isolated browser application."""

    monkeypatch.setenv("TXT2CRS_ENABLE_BROWSER_TEST_APP", "1")
    return create_deterministic_browser_app(
        state_directory=tmp_path / "browser-state",
        scenario_name="complete",
    )


@pytest.fixture()
def deterministic_browser_client(
    deterministic_browser_app: FastAPI,
) -> Iterator[TestClient]:
    """Own the full ASGI lifespan and prove cleanup after the test."""

    with TestClient(deterministic_browser_app) as client:
        yield client

    assert deterministic_browser_app.state.txt2crs_worker is None
    assert deterministic_browser_app.state.txt2crs_readiness is None
    assert deterministic_browser_app.state.txt2crs_submission is None
    assert deterministic_browser_app.state.txt2crs_runtime_ownership is None
    assert deterministic_browser_app.state.txt2crs_lifecycle.application is None


def _normal_user_headers(
    client: TestClient,
    browser_app: FastAPI,
) -> dict[str, str]:
    """Create a normal user inside the browser app's private account store."""

    # Browser composition deliberately overrides ``get_db`` with run-owned
    # SQLite. Seed through that same provider so this test cannot touch the
    # application-suite PostgreSQL fixture or a developer's live database.
    browser_database_provider = browser_app.dependency_overrides[get_db]
    browser_database_generator = browser_database_provider()
    browser_database_session = next(browser_database_generator)
    try:
        return authentication_token_from_email(
            client=client,
            email=settings.EMAIL_TEST_USER,
            db=browser_database_session,
        )
    finally:
        browser_database_generator.close()


def test_browser_app_requires_explicit_test_only_enablement(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A normal process cannot construct the deterministic browser server."""

    monkeypatch.delenv("TXT2CRS_ENABLE_BROWSER_TEST_APP", raising=False)

    with pytest.raises(RuntimeError, match="browser test application is disabled"):
        create_deterministic_browser_app(
            state_directory=tmp_path / "disabled-state",
            scenario_name="complete",
        )


def test_browser_app_rejects_a_preexisting_state_directory_without_mutating_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Environment input cannot repurpose or chmod an existing directory."""

    monkeypatch.setenv("TXT2CRS_ENABLE_BROWSER_TEST_APP", "1")
    existing_directory = tmp_path / "existing-state"
    existing_directory.mkdir(mode=0o750)
    existing_mode = S_IMODE(existing_directory.stat().st_mode)

    with pytest.raises(ValueError, match="fresh state directory"):
        create_deterministic_browser_app(
            state_directory=existing_directory,
            scenario_name="complete",
        )

    assert S_IMODE(existing_directory.stat().st_mode) == existing_mode


def test_production_route_graph_has_no_browser_fixture_controls() -> None:
    """Test-only controls can never appear in production OpenAPI."""

    production_paths = production_app.openapi()["paths"]

    assert all(not path.startswith("/__test__") for path in production_paths)


def test_browser_app_uses_a_state_scoped_sqlite_account_database(
    deterministic_browser_app: FastAPI,
) -> None:
    """The deterministic journey must never inherit a developer PostgreSQL URL."""

    database_override = deterministic_browser_app.dependency_overrides[get_db]
    session_generator = database_override()
    isolated_session = next(session_generator)
    try:
        database_url = str(isolated_session.get_bind().url)
    finally:
        session_generator.close()

    assert database_url.startswith("sqlite:///")
    assert database_url.endswith("/browser-state/accounts.sqlite3")


def test_real_http_submission_executes_and_reopens_from_durable_state(
    deterministic_browser_client: TestClient,
    deterministic_browser_app: FastAPI,
) -> None:
    """The browser fixture proves real durable execution, not route stubs."""

    headers = _normal_user_headers(
        deterministic_browser_client,
        deterministic_browser_app,
    )
    accepted = deterministic_browser_client.post(
        f"{settings.API_V1_STR}/jobs",
        headers={**headers, "Idempotency-Key": "browser-course-request"},
        json=_submission_payload(),
    )

    assert accepted.status_code == 202
    accepted_body = accepted.json()
    assert accepted_body["status"] == "accepted"
    assert accepted_body["revision"] == 0
    status_url = accepted_body["status_url"]

    deadline = monotonic() + 10
    latest = deterministic_browser_client.get(status_url, headers=headers)
    while (
        latest.json()["status"]
        not in {
            "completed",
            "failed",
            "cancelled",
        }
        and monotonic() < deadline
    ):
        sleep(0.02)
        latest = deterministic_browser_client.get(status_url, headers=headers)

    assert latest.status_code == 200
    completed = latest.json()
    assert completed["status"] == "completed"
    assert completed["revision"] > 0
    assert completed["result"]["title"] == "Python Basics"
    assert completed["artifacts"]["available"] is True
    assert completed["artifacts"]["count"] == 16

    # A second route read uses the durable package projection and returns the
    # same identity after all worker work has settled.
    reopened = deterministic_browser_client.get(status_url, headers=headers)
    assert reopened.status_code == 200
    assert reopened.json()["job_id"] == accepted_body["job_id"]
    assert reopened.json()["revision"] == completed["revision"]


def test_browser_app_keeps_wrong_owner_indistinguishable_from_missing(
    deterministic_browser_client: TestClient,
    deterministic_browser_app: FastAPI,
) -> None:
    """The fixture must retain the package's owner-hidden read boundary."""

    headers = _normal_user_headers(
        deterministic_browser_client,
        deterministic_browser_app,
    )

    response = deterministic_browser_client.get(
        f"{settings.API_V1_STR}/jobs/job-that-does-not-exist",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == "JOB_7001"
