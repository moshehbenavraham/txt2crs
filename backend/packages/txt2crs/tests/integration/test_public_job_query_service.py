# SPDX-License-Identifier: MIT-0

"""Integration tests for owner-safe job and artifact read operations."""

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.factories import (
    disabled_delivery_notification_policy,
    generous_admission_limits,
    standard_admission_reservation,
    valid_generation_preparation,
    valid_generation_request,
    valid_input_document,
)
from txt2crs.jobs.artifact_store import (
    ArtifactIntegrityError,
    FilesystemPrivateArtifactStore,
)
from txt2crs.jobs.models import JobStatus
from txt2crs.jobs.requests import GenerationRequest
from txt2crs.jobs.service import JobService
from txt2crs.jobs.stage_result import StageResult
from txt2crs.jobs.store import JobNotFoundError, SqliteJobStore
from txt2crs.rendering.artifacts import RenderedArtifact

_HASH = "sha256:" + ("c" * 64)
_PRIVATE_INPUT = "PRIVATE QUERY SERVICE INPUT"


def _job_service(
    *,
    database_path: Path,
    artifact_root: Path,
) -> tuple[JobService, SqliteJobStore, FilesystemPrivateArtifactStore]:
    """Build the real SQLite/filesystem query graph used by these tests."""

    job_store = SqliteJobStore(
        database_path,
        admission_limits=generous_admission_limits(),
    )
    artifact_store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=100_000,
        retention_days=30,
    )
    return (
        JobService(
            store=job_store,
            artifact_store=artifact_store,
            notification_policy=disabled_delivery_notification_policy(),
        ),
        job_store,
        artifact_store,
    )


def _checkpoint_prepared_input(
    *,
    service: JobService,
    job_id: str,
    expected_revision: int,
    generation_request: GenerationRequest,
) -> None:
    """Persist one accepted provider-free preparation through the job service."""

    preparation = valid_generation_preparation(
        generation_request=generation_request,
        input_document=valid_input_document(
            normalized_text=_PRIVATE_INPUT,
            metadata={"private_path": "/home/ada/private/input.txt"},
            warnings=["Minor extraction warning"],
        ),
    )
    service.checkpoint_stage(
        job_id=job_id,
        user_id="owner-1",
        expected_revision=expected_revision,
        stage="prepare_input",
        sequence=1,
        result=StageResult.accepted(artifact=preparation),
        artifact_version=_HASH,
        evidence_version=None,
        budget_snapshot={},
        next_status=JobStatus.researching,
        required_stage=True,
    )


def test_service_queries_survive_sqlite_and_filesystem_restart(
    tmp_path: Path,
) -> None:
    """One authorized query graph reopens exact state and private bytes."""

    database_path = tmp_path / "state" / "jobs.sqlite3"
    artifact_root = tmp_path / "state" / "artifacts"
    service, first_job_store, artifact_store = _job_service(
        database_path=database_path,
        artifact_root=artifact_root,
    )
    request = valid_generation_request(value=_PRIVATE_INPUT)
    submitted_job = service.submit(
        user_id="owner-1",
        idempotency_key="query-service-key",
        generation_request=request,
        admission_reservation=standard_admission_reservation(),
    )
    started_job = service.start(
        job_id=submitted_job.job_id,
        user_id="owner-1",
        expected_revision=submitted_job.revision,
    )
    _checkpoint_prepared_input(
        service=service,
        job_id=started_job.job_id,
        expected_revision=started_job.revision,
        generation_request=request,
    )
    artifact_store.save(
        user_id="owner-1",
        job_id=started_job.job_id,
        artifacts={
            "course_markdown": RenderedArtifact(
                file_name="course.md",
                media_type="text/markdown; charset=utf-8",
                content=b"# Restart-safe course",
            )
        },
    )
    first_job_store.close()

    reopened_service, reopened_job_store, _reopened_artifact_store = _job_service(
        database_path=database_path,
        artifact_root=artifact_root,
    )
    try:
        reopened_resume_state = reopened_service.resume(
            job_id=started_job.job_id,
            user_id="owner-1",
        )
        snapshot = reopened_service.get_public_snapshot(
            job_id=started_job.job_id,
            user_id="owner-1",
        )
        manifest = reopened_service.get_artifact_manifest(
            job_id=started_job.job_id,
            user_id="owner-1",
        )
        with reopened_service.open_artifact(
            job_id=started_job.job_id,
            user_id="owner-1",
            artifact_id="course_markdown",
        ) as artifact_chunks:
            restored_bytes = b"".join(artifact_chunks)
    finally:
        reopened_job_store.close()

    assert snapshot.status is JobStatus.researching
    assert snapshot.revision == reopened_resume_state.job.revision
    assert snapshot.last_accepted_stage == "prepare_input"
    assert snapshot.progress.completed_units == 1
    assert snapshot.progress.total_units is None
    assert snapshot.input.size_bytes == len(_PRIVATE_INPUT.encode("utf-8"))
    assert snapshot.input.extraction_warnings == ("Minor extraction warning",)
    assert snapshot.input.extraction_warnings_truncated is False
    assert snapshot.course_title is None
    assert snapshot.resolved_audience is None
    assert snapshot.objective_count is None
    assert snapshot.sources_truncated is False
    assert snapshot.conflicts_truncated is False
    assert snapshot.artifacts.available is True
    assert snapshot.artifacts.count == 1
    assert _PRIVATE_INPUT not in snapshot.model_dump_json()
    assert [artifact.artifact_id for artifact in manifest.artifacts] == [
        "course_markdown"
    ]
    assert restored_bytes == b"# Restart-safe course"


def test_service_queries_make_missing_and_wrong_owner_indistinguishable(
    tmp_path: Path,
) -> None:
    """Durable and byte queries do not reveal resource ownership or existence."""

    service, job_store, artifact_store = _job_service(
        database_path=tmp_path / "jobs.sqlite3",
        artifact_root=tmp_path / "artifacts",
    )
    submitted_job = service.submit(
        user_id="owner-1",
        idempotency_key="query-privacy-key",
        generation_request=valid_generation_request(),
        admission_reservation=standard_admission_reservation(),
    )
    artifact_store.save(
        user_id="owner-1",
        job_id=submitted_job.job_id,
        artifacts={
            "course_markdown": RenderedArtifact(
                file_name="course.md",
                media_type="text/markdown",
                content=b"private course",
            )
        },
    )
    try:
        job_errors: list[str] = []
        for job_id, user_id in (
            (submitted_job.job_id, "owner-2"),
            ("job-missing", "owner-1"),
        ):
            with pytest.raises(JobNotFoundError) as error_info:
                service.get_public_snapshot(job_id=job_id, user_id=user_id)
            job_errors.append(str(error_info.value))

        artifact_errors: list[str] = []
        artifact_operations: tuple[Callable[[], object], ...] = (
            lambda: service.get_artifact_manifest(
                job_id=submitted_job.job_id,
                user_id="owner-2",
            ),
            lambda: service.get_artifact_manifest(
                job_id="job-missing",
                user_id="owner-1",
            ),
        )
        for operation in artifact_operations:
            with pytest.raises(JobNotFoundError) as error_info:
                operation()
            artifact_errors.append(str(error_info.value))
        with pytest.raises(JobNotFoundError) as missing_id_error:
            with service.open_artifact(
                job_id=submitted_job.job_id,
                user_id="owner-1",
                artifact_id="artifact-missing",
            ):
                pytest.fail("A missing artifact ID must not yield a stream.")
        artifact_errors.append(str(missing_id_error.value))
    finally:
        job_store.close()

    assert job_errors == [job_errors[0], job_errors[0]]
    assert artifact_errors == [artifact_errors[0]] * len(artifact_errors)


def test_service_preserves_artifact_integrity_failures(tmp_path: Path) -> None:
    """Corrupt owner-authorized bytes do not collapse into false unavailability."""

    artifact_root = tmp_path / "artifacts"
    service, job_store, artifact_store = _job_service(
        database_path=tmp_path / "jobs.sqlite3",
        artifact_root=artifact_root,
    )
    submitted_job = service.submit(
        user_id="owner-1",
        idempotency_key="query-integrity-key",
        generation_request=valid_generation_request(),
        admission_reservation=standard_admission_reservation(),
    )
    artifact_store.save(
        user_id="owner-1",
        job_id=submitted_job.job_id,
        artifacts={
            "course_markdown": RenderedArtifact(
                file_name="course.md",
                media_type="text/markdown",
                content=b"verified course",
            )
        },
    )
    stored_course_path = next(artifact_root.rglob("course.md"))
    stored_course_path.write_bytes(b"corrupt course!")
    try:
        with pytest.raises(ArtifactIntegrityError, match="integrity"):
            with service.open_artifact(
                job_id=submitted_job.job_id,
                user_id="owner-1",
                artifact_id="course_markdown",
            ):
                pytest.fail("Corrupt bytes must fail before a stream is returned.")
    finally:
        job_store.close()
