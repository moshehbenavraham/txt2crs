"""Authenticated HTTP contracts for owner-scoped job results and artifacts."""

from collections.abc import Iterator
from contextlib import AbstractContextManager
from datetime import UTC, datetime
from hashlib import sha256
from types import TracebackType
from typing import cast

import pytest
from fastapi.testclient import TestClient
from txt2crs.application import Txt2CrsApplication
from txt2crs.jobs import (
    ArtifactDeliverable,
    ArtifactFormat,
    ArtifactIntegrityError,
    ArtifactManifest,
    ArtifactMetadata,
    JobNotFoundError,
    JobStatus,
    PublicArtifactAvailability,
    PublicInputSummary,
    PublicJobPage,
    PublicJobProgress,
    PublicJobSnapshot,
    PublicJobSummary,
    PublicSourceSummary,
)

from app.api.deps import get_txt2crs_application
from app.core.config import settings
from app.core.constants import ErrorCode
from app.main import app

_ARTIFACT_BYTES = b"%PDF-owner-scoped-course"


def _snapshot() -> PublicJobSnapshot:
    """Return one completed path-free package projection."""

    return PublicJobSnapshot(
        schema_version="1.0",
        job_id="job-results-route",
        revision=11,
        status=JobStatus.completed,
        created_at=datetime(2026, 7, 20, 9, 0, tzinfo=UTC),
        updated_at=datetime(2026, 7, 20, 9, 15, tzinfo=UTC),
        last_accepted_stage="cross_validate_artifacts",
        progress=PublicJobProgress(completed_units=9, total_units=9),
        input=PublicInputSummary(
            input_type="pdf",
            display_name="source.pdf",
            size_bytes=4_096,
            extraction_warnings=("One page used OCR.",),
            extraction_warnings_truncated=False,
        ),
        failure=None,
        course_title="Database Indexes",
        resolved_audience="First-year students",
        resolved_level="beginner",
        resolved_language="en",
        objective_count=2,
        module_count=1,
        sources=(
            PublicSourceSummary(
                title="PostgreSQL documentation",
                canonical_url="https://www.postgresql.org/docs/current/",
                publisher="PostgreSQL Global Development Group",
                retrieved_at=datetime(2026, 7, 20, 8, 0, tzinfo=UTC),
            ),
        ),
        sources_truncated=False,
        conflicts=(),
        conflicts_truncated=False,
        artifacts=PublicArtifactAvailability(available=True, count=4),
    )


def _manifest() -> ArtifactManifest:
    """Return one verified metadata row for every educational deliverable."""

    rows = (
        (
            "answer_key_html",
            ArtifactDeliverable.answer_key,
            ArtifactFormat.html,
            "answer-key.html",
            b"<html>answer key</html>",
        ),
        (
            "assessment_pdf",
            ArtifactDeliverable.assessment,
            ArtifactFormat.pdf,
            "assessment.pdf",
            b"%PDF-assessment",
        ),
        (
            "course_pdf",
            ArtifactDeliverable.course,
            ArtifactFormat.pdf,
            'course "final";.pdf',
            _ARTIFACT_BYTES,
        ),
        (
            "review_pack_markdown",
            ArtifactDeliverable.review_pack,
            ArtifactFormat.markdown,
            "review-pack.md",
            b"# Review pack",
        ),
    )
    return ArtifactManifest(
        schema_version="1.0",
        job_id="job-results-route",
        created_at=datetime(2026, 7, 20, 9, 15, tzinfo=UTC),
        artifacts=tuple(
            ArtifactMetadata(
                artifact_id=artifact_id,
                deliverable=deliverable,
                format=artifact_format,
                safe_file_name=file_name,
                media_type=(
                    "application/pdf"
                    if artifact_format is ArtifactFormat.pdf
                    else "text/plain"
                ),
                size_bytes=len(content),
                content_hash=f"sha256:{sha256(content).hexdigest()}",
            )
            for artifact_id, deliverable, artifact_format, file_name, content in rows
        ),
    )


class _CountingStreamContext(AbstractContextManager[Iterator[bytes]]):
    """Count entry/exit so route tests can prove response-owned cleanup."""

    def __init__(
        self,
        content: bytes,
        *,
        entry_error: Exception | None = None,
    ) -> None:
        self._content = content
        self._entry_error = entry_error
        self.enter_count = 0
        self.exit_count = 0

    def __enter__(self) -> Iterator[bytes]:
        self.enter_count += 1
        if self._entry_error is not None:
            raise self._entry_error
        midpoint = len(self._content) // 2
        return iter((self._content[:midpoint], self._content[midpoint:]))

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exception_type, exception_value, traceback
        self.exit_count += 1


class RecordingResultsApplication:
    """Implement only the public facade reads exercised by these routes."""

    def __init__(self) -> None:
        self.snapshot = _snapshot()
        self.manifest = _manifest()
        self.error: Exception | None = None
        self.stream_context = _CountingStreamContext(_ARTIFACT_BYTES)
        self.calls: list[tuple[str, str, str, str | None]] = []

    def list_public_jobs(
        self,
        *,
        user_id: str,
        page_size: int,
        cursor: str | None = None,
    ) -> PublicJobPage:
        """Return one bounded collection while recording exact pagination."""

        self.calls.append(("library", user_id, str(page_size), cursor))
        self._raise_configured_error()
        snapshot = self.snapshot
        return PublicJobPage(
            schema_version="1.0",
            items=(
                PublicJobSummary(
                    schema_version="1.0",
                    job_id=snapshot.job_id,
                    revision=snapshot.revision,
                    status=snapshot.status,
                    title=snapshot.course_title or snapshot.input.display_name,
                    input_type=snapshot.input.input_type,
                    created_at=snapshot.created_at,
                    updated_at=snapshot.updated_at,
                    progress=snapshot.progress,
                    failure=snapshot.failure,
                    artifacts=snapshot.artifacts,
                ),
            ),
            next_cursor="next-private-page",
        )

    def get_public_job(self, *, job_id: str, user_id: str) -> PublicJobSnapshot:
        self.calls.append(("status", user_id, job_id, None))
        self._raise_configured_error()
        return self.snapshot

    def get_artifact_manifest(
        self,
        *,
        job_id: str,
        user_id: str,
    ) -> ArtifactManifest:
        self.calls.append(("manifest", user_id, job_id, None))
        self._raise_configured_error()
        return self.manifest

    def open_artifact(
        self,
        *,
        job_id: str,
        user_id: str,
        artifact_id: str,
    ) -> AbstractContextManager[Iterator[bytes]]:
        self.calls.append(("artifact", user_id, job_id, artifact_id))
        self._raise_configured_error()
        return self.stream_context

    def _raise_configured_error(self) -> None:
        if self.error is not None:
            raise self.error


@pytest.fixture()
def results_application() -> Iterator[RecordingResultsApplication]:
    """Override only the lifespan-owned public application facade."""

    recording_application = RecordingResultsApplication()
    app.dependency_overrides[get_txt2crs_application] = lambda: cast(
        Txt2CrsApplication,
        recording_application,
    )
    yield recording_application
    app.dependency_overrides.pop(get_txt2crs_application, None)


def _assert_private_response_headers(response_headers: object) -> None:
    """Assert the fixed cache and browser hardening shared by every GET."""

    headers = cast(dict[str, str], response_headers)
    assert headers["cache-control"] == "private, no-store"
    assert headers["pragma"] == "no-cache"
    assert headers["x-content-type-options"] == "nosniff"
    assert headers["referrer-policy"] == "no-referrer"
    assert "etag" not in headers


def test_status_route_authenticates_before_facade_read(
    client: TestClient,
    results_application: RecordingResultsApplication,
) -> None:
    response = client.get(f"{settings.API_V1_STR}/jobs/job-results-route")

    assert response.status_code == 401
    assert response.json()["code"] == ErrorCode.AUTH_TOKEN_INVALID.value
    assert results_application.calls == []


def test_status_route_returns_current_revisioned_result_with_private_headers(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/jobs/job-results-route",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-results-route"
    assert response.json()["revision"] == 11
    assert response.json()["status"] == "completed"
    assert response.json()["progress"] == {
        "stage": "ready",
        "message": "Your course materials are ready.",
        "completed_units": 9,
        "total_units": 9,
    }
    assert response.json()["result"]["title"] == "Database Indexes"
    assert response.json()["artifacts"]["manifest_url"] == (
        f"{settings.API_V1_STR}/jobs/job-results-route/artifacts"
    )
    _assert_private_response_headers(response.headers)
    assert len(results_application.calls) == 1
    assert results_application.calls[0][0] == "status"


def test_library_route_returns_owner_page_with_private_headers(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
) -> None:
    """GET /jobs delegates pagination and exposes only the reviewed summary."""

    response = client.get(
        f"{settings.API_V1_STR}/jobs",
        params={"limit": 1, "cursor": "current-private-page"},
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "1.0",
        "data": [
            {
                "schema_version": "1.0",
                "job_id": "job-results-route",
                "revision": 11,
                "status": "completed",
                "title": "Database Indexes",
                "input_type": "pdf",
                "created_at": "2026-07-20T09:00:00Z",
                "updated_at": "2026-07-20T09:15:00Z",
                "progress": {
                    "stage": "ready",
                    "message": "Your course materials are ready.",
                    "completed_units": 9,
                    "total_units": 9,
                },
                "failure": None,
                "artifacts": {
                    "available": True,
                    "count": 4,
                    "manifest_url": "/api/v1/jobs/job-results-route/artifacts",
                },
            }
        ],
        "next_cursor": "next-private-page",
    }
    _assert_private_response_headers(response.headers)
    assert results_application.calls[0][0] == "library"
    assert results_application.calls[0][1]
    assert results_application.calls[0][2:] == (
        "1",
        "current-private-page",
    )


def test_library_route_authenticates_and_validates_before_facade_read(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
) -> None:
    """Unauthenticated and malformed requests never reach the engine facade."""

    unauthenticated_response = client.get(f"{settings.API_V1_STR}/jobs")
    invalid_limit_response = client.get(
        f"{settings.API_V1_STR}/jobs",
        params={"limit": 51},
        headers=normal_user_token_headers,
    )

    assert unauthenticated_response.status_code == 401
    assert invalid_limit_response.status_code == 422
    assert results_application.calls == []


@pytest.mark.parametrize("resource_kind", ["status", "manifest", "artifact"])
@pytest.mark.parametrize("absence_kind", ["missing", "wrong-owner"])
def test_missing_and_foreign_resources_share_one_context_free_404(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
    resource_kind: str,
    absence_kind: str,
) -> None:
    private_detail = {
        "missing": "private missing-resource existence detail",
        "wrong-owner": "private foreign-owner identity detail",
    }[absence_kind]
    results_application.error = JobNotFoundError(private_detail)
    resource_path = {
        "status": "/jobs/job-hidden",
        "manifest": "/jobs/job-hidden/artifacts",
        "artifact": "/jobs/job-hidden/artifacts/course_pdf",
    }[resource_kind]

    response = client.get(
        f"{settings.API_V1_STR}{resource_path}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 404
    assert response.json()["code"] == ErrorCode.JOB_NOT_FOUND.value
    assert response.json()["detail"] == "The requested course job was not found."
    assert private_detail not in response.text


def test_manifest_route_returns_canonical_groups_without_paths_or_bodies(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
) -> None:
    del results_application
    response = client.get(
        f"{settings.API_V1_STR}/jobs/job-results-route/artifacts",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert [group["deliverable"] for group in response.json()["deliverables"]] == [
        "course",
        "review_pack",
        "assessment",
        "answer_key",
    ]
    course_artifact = response.json()["deliverables"][0]["artifacts"][0]
    assert course_artifact["artifact_id"] == "course_pdf"
    assert course_artifact["download_url"].endswith(
        "/jobs/job-results-route/artifacts/course_pdf"
    )
    assert "path" not in response.text
    assert "content" not in course_artifact
    _assert_private_response_headers(response.headers)


def test_artifact_route_streams_verified_bytes_and_rfc_safe_headers(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/jobs/job-results-route/artifacts/course_pdf",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.content == _ARTIFACT_BYTES
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-length"] == str(len(_ARTIFACT_BYTES))
    assert response.headers["content-disposition"] == (
        "attachment; filename*=utf-8''course%20%22final%22%3B.pdf"
    )
    _assert_private_response_headers(response.headers)
    assert results_application.stream_context.enter_count == 1
    assert results_application.stream_context.exit_count == 1


def test_integrity_failure_before_stream_entry_is_a_safe_problem_detail(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
) -> None:
    results_application.stream_context = _CountingStreamContext(
        _ARTIFACT_BYTES,
        entry_error=ArtifactIntegrityError(
            "private /filesystem/path failed sha256:secret"
        ),
    )

    response = client.get(
        f"{settings.API_V1_STR}/jobs/job-results-route/artifacts/course_pdf",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 500
    assert response.json()["code"] == ErrorCode.ENGINE_OPERATION_FAILED.value
    assert "filesystem" not in response.text
    assert "sha256" not in response.text
    assert results_application.stream_context.enter_count == 1
    assert results_application.stream_context.exit_count == 0


@pytest.mark.parametrize(
    "path",
    [
        "/jobs/contains space",
        "/jobs/job-results-route/artifacts/contains@symbol",
        f"/jobs/{'a' * 129}",
    ],
)
def test_result_routes_reject_invalid_identifiers_before_facade_reads(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
    path: str,
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}{path}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 422
    assert response.json()["code"] == ErrorCode.VALIDATION_ERROR.value
    assert results_application.calls == []


def test_response_construction_failure_closes_the_entered_context_once(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    results_application: RecordingResultsApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A route failure after entry cannot leak the verified descriptor."""

    class _ResponseConstructionError(Exception):
        pass

    def fail_response_construction(*_args: object, **_kwargs: object) -> None:
        raise _ResponseConstructionError("private response construction failure")

    monkeypatch.setattr(
        "app.api.routes.jobs.ArtifactStreamingResponse",
        fail_response_construction,
    )

    with pytest.raises(_ResponseConstructionError):
        client.get(
            f"{settings.API_V1_STR}/jobs/job-results-route/artifacts/course_pdf",
            headers=normal_user_token_headers,
        )

    assert results_application.stream_context.enter_count == 1
    assert results_application.stream_context.exit_count == 1
