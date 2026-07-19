"""Authenticated HTTP contracts for durable course-job submission."""

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import cast

import fitz  # type: ignore[import-untyped]
import pytest
from fastapi.testclient import TestClient
from txt2crs.jobs import JobRecord, JobStatus

from app.api.deps import get_txt2crs_submission
from app.core.config import settings
from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.core.rate_limit import limiter
from app.main import app
from app.schemas.jobs import JobSubmissionRequest, JobUploadMetadata
from app.services.txt2crs_submission import Txt2CrsSubmissionService
from app.services.txt2crs_uploads import ValidatedCourseUpload

_PRIVATE_KEY = "private-browser-retry-key"


def _json_payload() -> dict[str, object]:
    """Return one valid prompt submission body."""

    return {
        "input": {"type": "prompt", "value": "Teach relational indexes."},
        "preferences": {
            "level": "auto",
            "audience": None,
            "prior_knowledge": None,
            "learning_goals": [],
            "language": "auto",
        },
        "consent_to_ai_processing": True,
        "learner_age_group": "adult",
    }


def _metadata_json() -> str:
    """Return valid strict metadata for a multipart upload."""

    payload = _json_payload()
    del payload["input"]
    return json.dumps(payload)


def _pdf_bytes() -> bytes:
    """Return one tiny real PDF accepted by transport validation."""

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Course source")
    content = cast(bytes, document.tobytes())
    document.close()
    return content


def _job(
    *,
    status: JobStatus = JobStatus.accepted,
    revision: int = 0,
) -> JobRecord:
    """Return the public fields needed to build a 202 response."""

    timestamp = datetime(2026, 7, 19, 20, 0, tzinfo=UTC)
    return JobRecord(
        schema_version="1.0",
        job_id="job-route",
        user_id="owner-route",
        idempotency_key=_PRIVATE_KEY,
        request_hash="sha256:" + ("a" * 64),
        status=status,
        revision=revision,
        created_at=timestamp,
        updated_at=timestamp,
    )


class RecordingSubmissionService:
    """Capture route calls and return or raise a deterministic result."""

    def __init__(self) -> None:
        self.json_calls: list[dict[str, object]] = []
        self.upload_calls: list[dict[str, object]] = []
        self.result = _job()
        self.error: AppException | None = None

    def submit_json(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        request: JobSubmissionRequest,
    ) -> JobRecord:
        self.json_calls.append(
            {
                "user_id": user_id,
                "idempotency_key": idempotency_key,
                "request": request,
            }
        )
        if self.error is not None:
            raise self.error
        return self.result

    def submit_upload(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        metadata: JobUploadMetadata,
        upload: ValidatedCourseUpload,
    ) -> JobRecord:
        self.upload_calls.append(
            {
                "user_id": user_id,
                "idempotency_key": idempotency_key,
                "metadata": metadata,
                "upload": upload,
            }
        )
        if self.error is not None:
            raise self.error
        return self.result


@pytest.fixture()
def submission_service() -> Iterator[RecordingSubmissionService]:
    """Override only the lifespan-owned submission composition service."""

    service = RecordingSubmissionService()
    app.dependency_overrides[get_txt2crs_submission] = lambda: cast(
        Txt2CrsSubmissionService,
        service,
    )
    yield service
    app.dependency_overrides.pop(get_txt2crs_submission, None)
    limiter.reset()


def test_submission_authenticates_before_private_body_validation(
    client: TestClient,
    submission_service: RecordingSubmissionService,
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        headers={"Idempotency-Key": _PRIVATE_KEY},
        json={"source_text": "private malformed learner body"},
    )

    assert response.status_code == 401
    assert response.json()["code"] == ErrorCode.AUTH_TOKEN_INVALID.value
    assert submission_service.json_calls == []


def test_json_submission_returns_allowlisted_202_and_privacy_headers(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        headers={**normal_user_token_headers, "Idempotency-Key": _PRIVATE_KEY},
        json=_json_payload(),
    )

    assert response.status_code == 202
    assert response.json() == {
        "schema_version": "1.0",
        "job_id": "job-route",
        "status": "accepted",
        "revision": 0,
        "status_url": f"{settings.API_V1_STR}/jobs/job-route",
    }
    assert response.headers["location"] == f"{settings.API_V1_STR}/jobs/job-route"
    assert response.headers["cache-control"] == "private, no-store"
    assert response.headers["pragma"] == "no-cache"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert _PRIVATE_KEY not in response.text
    assert len(submission_service.json_calls) == 1
    assert submission_service.json_calls[0]["idempotency_key"] == _PRIVATE_KEY


def test_terminal_replay_still_returns_stable_initial_acceptance_revision(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
) -> None:
    """POST acknowledges the original admission; GET owns current job state."""

    submission_service.result = _job(status=JobStatus.completed, revision=6)

    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        headers={**normal_user_token_headers, "Idempotency-Key": _PRIVATE_KEY},
        json=_json_payload(),
    )

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
    assert response.json()["revision"] == 0


@pytest.mark.parametrize(
    ("header_value", "body_change"),
    [
        (None, {}),
        ("contains space", {}),
        (_PRIVATE_KEY, {"private_model": "gpt-private"}),
        (_PRIVATE_KEY, {"consent_to_ai_processing": False}),
    ],
)
def test_json_submission_rejects_invalid_header_or_unknown_body_before_service(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
    header_value: str | None,
    body_change: dict[str, object],
) -> None:
    headers = dict(normal_user_token_headers)
    if header_value is not None:
        headers["Idempotency-Key"] = header_value

    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        headers=headers,
        json={**_json_payload(), **body_change},
    )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == ErrorCode.VALIDATION_ERROR.value
    assert submission_service.json_calls == []


def test_json_submission_preserves_context_free_problem_details(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
) -> None:
    submission_service.error = AppException(
        code=ErrorCode.JOB_POLICY_REJECTED,
        detail="This request cannot be processed automatically.",
    )

    response = client.post(
        f"{settings.API_V1_STR}/jobs",
        headers={**normal_user_token_headers, "Idempotency-Key": _PRIVATE_KEY},
        json=_json_payload(),
    )

    assert response.status_code == 422
    assert response.json()["code"] == ErrorCode.JOB_POLICY_REJECTED.value
    assert response.headers["content-type"].startswith("application/problem+json")
    assert "trace_id" in response.json()


def test_upload_submission_validates_and_returns_same_202_contract(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/jobs/upload",
        headers={**normal_user_token_headers, "Idempotency-Key": _PRIVATE_KEY},
        data={"metadata": _metadata_json()},
        files={"file": ("course.pdf", _pdf_bytes(), "application/pdf")},
    )

    assert response.status_code == 202
    assert response.headers["location"] == f"{settings.API_V1_STR}/jobs/job-route"
    assert response.headers["cache-control"] == "private, no-store"
    assert len(submission_service.upload_calls) == 1
    validated_upload = submission_service.upload_calls[0]["upload"]
    assert validated_upload.input_type == "pdf"
    assert validated_upload.file_name == "course.pdf"
    assert validated_upload.content.startswith(b"%PDF")


@pytest.mark.parametrize(
    ("data", "files"),
    [
        (
            {"metadata": _metadata_json(), "extra": "private"},
            [("file", ("course.pdf", _pdf_bytes(), "application/pdf"))],
        ),
        (
            {"metadata": _metadata_json()},
            [
                ("file", ("one.pdf", _pdf_bytes(), "application/pdf")),
                ("file", ("two.pdf", _pdf_bytes(), "application/pdf")),
            ],
        ),
        (
            [
                ("metadata", _metadata_json()),
                ("metadata", _metadata_json()),
            ],
            [("file", ("course.pdf", _pdf_bytes(), "application/pdf"))],
        ),
    ],
)
def test_upload_rejects_extra_or_duplicate_multipart_fields(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
    data: object,
    files: object,
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/jobs/upload",
        headers={**normal_user_token_headers, "Idempotency-Key": _PRIVATE_KEY},
        data=cast(object, data),
        files=cast(object, files),
    )

    assert response.status_code == 422
    assert response.json()["code"] == ErrorCode.VALIDATION_ERROR.value
    assert submission_service.upload_calls == []


@pytest.mark.parametrize(
    ("filename", "media_type", "content", "expected_status", "expected_code"),
    [
        (
            "course.txt",
            "text/plain",
            b"private",
            415,
            ErrorCode.JOB_UNSUPPORTED_MEDIA,
        ),
        (
            "course.pdf",
            "application/pdf",
            b"x" * 1_100_000,
            413,
            ErrorCode.JOB_PAYLOAD_TOO_LARGE,
        ),
    ],
)
def test_upload_transport_errors_are_problem_details_and_skip_service(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
    monkeypatch: pytest.MonkeyPatch,
    filename: str,
    media_type: str,
    content: bytes,
    expected_status: int,
    expected_code: ErrorCode,
) -> None:
    # Keep this test small while exercising the route's configured bound.
    monkeypatch.setattr(settings, "TXT2CRS_MAX_INPUT_BYTES", 1_000_000)

    response = client.post(
        f"{settings.API_V1_STR}/jobs/upload",
        headers={**normal_user_token_headers, "Idempotency-Key": _PRIVATE_KEY},
        data={"metadata": _metadata_json()},
        files={"file": (filename, content, media_type)},
    )

    assert response.status_code == expected_status
    assert response.json()["code"] == expected_code.value
    assert response.headers["content-type"].startswith("application/problem+json")
    assert submission_service.upload_calls == []


def test_json_submission_has_finite_rate_limit(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    submission_service: RecordingSubmissionService,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del submission_service
    monkeypatch.setattr(limiter, "enabled", True)
    limiter.reset()

    responses = [
        client.post(
            f"{settings.API_V1_STR}/jobs",
            headers={
                **normal_user_token_headers,
                "Idempotency-Key": f"rate-limit-{request_index}",
            },
            json=_json_payload(),
        )
        for request_index in range(11)
    ]

    assert responses[-1].status_code == 429
    assert responses[-1].json()["code"] == ErrorCode.RATE_LIMIT_EXCEEDED.value
