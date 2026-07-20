"""Credential-free acceptance for coordinated shell and engine owner erasure."""

from collections.abc import Iterator
from contextlib import contextmanager
from threading import Event, Thread
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from txt2crs.ai.fake_runtime import FakeRuntime
from txt2crs.ai.runtime import CancellationToken, TurnRequest
from txt2crs.application import Txt2CrsApplication
from txt2crs.jobs import JobNotFoundError, JobStatus
from txt2crs.jobs.artifact_store import FilesystemPrivateArtifactStore

from app import crud
from app.api.deps import get_txt2crs_application
from app.core.config import settings
from app.main import app
from app.models import User, UserCreate
from tests.acceptance.conftest import DurableResultsHarness
from tests.utils.utils import random_email, random_lower_string


@contextmanager
def _override_txt2crs_application(
    application: Txt2CrsApplication,
) -> Iterator[None]:
    """Expose one real deterministic facade to the account route under test."""

    app.dependency_overrides[get_txt2crs_application] = lambda: application
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_txt2crs_application, None)


def _create_authenticated_user(
    client: TestClient,
    db: Session,
) -> tuple[User, dict[str, str]]:
    """Create one PostgreSQL identity and return its bearer authorization."""

    password = random_lower_string()
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email=random_email(), password=password),
    )
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": str(user.email), "password": password},
    )
    assert response.status_code == 200
    return user, {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }


def _submit(
    application: Txt2CrsApplication,
    harness: DurableResultsHarness,
    *,
    user_id: str,
    idempotency_key: str,
    value: str,
) -> str:
    """Submit one durable owner request and return its stable job ID."""

    job = application.submit(
        user_id=user_id,
        idempotency_key=idempotency_key,
        generation_request=harness.request(value=value),
        admission_reservation=application.default_admission_reservation(),
    )
    return job.job_id


def _complete_job(
    application: Txt2CrsApplication,
    *,
    job_id: str,
    user_id: str,
) -> None:
    """Create and settle one executor so real private artifacts exist."""

    with application.create_executor(job_id=job_id, user_id=user_id) as executor:
        completed = executor.execute()
    assert completed.status is JobStatus.completed


def test_self_delete_waits_for_active_facade_work_then_purges_both_stores(
    client: TestClient,
    db: Session,
    durable_results_harness: DurableResultsHarness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HTTP success means active work settled and both owner stores are empty."""

    user, headers = _create_authenticated_user(client, db)
    user_id = user.id
    owner_id = str(user_id)
    application = durable_results_harness.open()
    completed_job_id = _submit(
        application,
        durable_results_harness,
        user_id=owner_id,
        idempotency_key="purge-completed",
        value="Teach Python variables for the completed purge fixture.",
    )
    _complete_job(
        application,
        job_id=completed_job_id,
        user_id=owner_id,
    )
    assert application.get_artifact_manifest(
        job_id=completed_job_id,
        user_id=owner_id,
    ).artifacts

    active_job_id = _submit(
        application,
        durable_results_harness,
        user_id=owner_id,
        idempotency_key="purge-active",
        value="Teach Python variables for the active purge fixture.",
    )
    active_executor = application.create_executor(
        job_id=active_job_id,
        user_id=owner_id,
    )
    runtime_entered = Event()
    cancellation_observed = Event()
    release_runtime = Event()
    original_run_validated_turn = FakeRuntime.run_validated_turn

    def block_until_owner_cancellation(
        runtime: FakeRuntime,
        *,
        request: TurnRequest,
        artifact_model: type[Any],
        cancellation: CancellationToken,
    ) -> Any:
        runtime_entered.set()
        while not cancellation.is_cancelled:
            release_runtime.wait(timeout=0.01)
        cancellation_observed.set()
        assert release_runtime.wait(timeout=2)
        return original_run_validated_turn(
            runtime,
            request=request,
            artifact_model=artifact_model,
            cancellation=cancellation,
        )

    monkeypatch.setattr(
        FakeRuntime,
        "run_validated_turn",
        block_until_owner_cancellation,
    )
    execution_errors: list[BaseException] = []
    delete_responses: list[Any] = []

    def execute_active_job() -> None:
        try:
            active_executor.execute()
        except BaseException as exc:
            # Cancellation may surface as the package's restart-safe
            # interruption. The acceptance invariant is that the thread
            # settles before HTTP deletion commits.
            execution_errors.append(exc)

    def delete_account() -> None:
        delete_responses.append(
            client.delete(
                f"{settings.API_V1_STR}/users/me",
                headers=headers,
            )
        )

    execution_thread = Thread(target=execute_active_job)
    delete_thread = Thread(target=delete_account)
    execution_thread_started = False
    delete_thread_started = False
    try:
        execution_thread.start()
        execution_thread_started = True
        assert runtime_entered.wait(timeout=2)
        with _override_txt2crs_application(application):
            delete_thread.start()
            delete_thread_started = True
            observed_cancellation = cancellation_observed.wait(timeout=2)
            deletion_waited_for_executor = delete_thread.is_alive()
            db.expire_all()
            identity_present_during_barrier = db.get(User, user_id) is not None
            release_runtime.set()
            execution_thread.join(timeout=3)
            delete_thread.join(timeout=3)

        assert observed_cancellation is True
        assert deletion_waited_for_executor is True
        assert identity_present_during_barrier is True
        assert execution_thread.is_alive() is False
        assert delete_thread.is_alive() is False
        assert len(delete_responses) == 1
        assert delete_responses[0].status_code == 200
        assert len(execution_errors) <= 1
        db.expire_all()
        assert db.get(User, user_id) is None
        with pytest.raises(JobNotFoundError):
            application.get_public_job(
                job_id=completed_job_id,
                user_id=owner_id,
            )
        assert not any(
            path.is_file()
            for path in durable_results_harness.state_directory.rglob("*")
            if "artifacts" in path.parts
        )
    finally:
        release_runtime.set()
        # An assertion can fail before the deletion thread starts. Cancel any
        # active executor first, and never call ``join`` on an unstarted
        # thread, so cleanup cannot mask the original test failure.
        if execution_thread_started and execution_thread.is_alive():
            active_executor.close()
        if execution_thread_started:
            execution_thread.join(timeout=3)
        if delete_thread_started:
            delete_thread.join(timeout=3)
        application.close()


def test_real_facade_purge_failure_retains_identity_and_retry_completes(
    client: TestClient,
    db: Session,
    durable_results_harness: DurableResultsHarness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Artifact-store failure must become safe 503 before PostgreSQL deletion."""

    user, headers = _create_authenticated_user(client, db)
    user_id = user.id
    owner_id = str(user_id)
    application = durable_results_harness.open()
    job_id = _submit(
        application,
        durable_results_harness,
        user_id=owner_id,
        idempotency_key="purge-retry",
        value="Teach Python variables for a purge retry.",
    )
    original_purge_owner = FilesystemPrivateArtifactStore.purge_owner

    def fail_artifact_purge(
        _store: FilesystemPrivateArtifactStore,
        *,
        user_id: str,
    ) -> int:
        raise OSError(f"/private/artifacts/{user_id}/must-never-reach-http-or-logs")

    try:
        with _override_txt2crs_application(application):
            monkeypatch.setattr(
                FilesystemPrivateArtifactStore,
                "purge_owner",
                fail_artifact_purge,
            )
            failed_response = client.delete(
                f"{settings.API_V1_STR}/users/me",
                headers=headers,
            )
            monkeypatch.setattr(
                FilesystemPrivateArtifactStore,
                "purge_owner",
                original_purge_owner,
            )

            db.expire_all()
            assert db.get(User, user_id) is not None
            assert (
                application.get_public_job(
                    job_id=job_id,
                    user_id=owner_id,
                ).job_id
                == job_id
            )

            retry_response = client.delete(
                f"{settings.API_V1_STR}/users/me",
                headers=headers,
            )

        assert failed_response.status_code == 503
        assert failed_response.json()["code"] == "USER_2007"
        assert "private" not in failed_response.text.lower()
        assert "must-never" not in failed_response.text
        assert retry_response.status_code == 200
        db.expire_all()
        assert db.get(User, user_id) is None
        with pytest.raises(JobNotFoundError):
            application.get_public_job(job_id=job_id, user_id=owner_id)
    finally:
        application.close()
