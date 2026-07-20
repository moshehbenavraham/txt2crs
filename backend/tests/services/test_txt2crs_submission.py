"""Tests for the thin shell-to-engine job submission adapter."""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
from txt2crs.application import Txt2CrsApplication
from txt2crs.jobs import (
    AdmissionQuotaExceededError,
    IdempotencyConflictError,
    JobRecord,
    JobStatus,
    PreparationPolicyError,
)
from txt2crs.security.policy import PolicyDecision, PolicyOutcome, PolicyStage

from app.core.config import Settings
from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.schemas.jobs import JobSubmissionRequest, JobUploadMetadata
from app.services.txt2crs_application import build_execution_profile
from app.services.txt2crs_submission import Txt2CrsSubmissionService
from app.services.txt2crs_uploads import ValidatedCourseUpload

_PRIVATE_TOPIC = "PRIVATE learner topic sentinel"
_PRIVATE_KEY = "private-idempotency-key"
_PRIVATE_URL = "https://example.com/private?token=secret"
_PRIVATE_HASH = "sha256:" + ("a" * 64)


def _settings(tmp_path: Path) -> Settings:
    """Create an isolated shell configuration without reading dotenv."""

    state_root = tmp_path / "state"
    return Settings(
        _env_file=None,
        PROJECT_NAME="txt2crs Test",
        ENVIRONMENT="local",
        SECRET_KEY="local-dev-secret-key",
        POSTGRES_SERVER="localhost",
        POSTGRES_USER="postgres",
        POSTGRES_PASSWORD="test-password",
        POSTGRES_DB="app",
        FIRST_SUPERUSER="admin@example.com",
        FIRST_SUPERUSER_PASSWORD="test-superuser-password",
        TXT2CRS_STATE_ROOT=state_root,
        TXT2CRS_JOB_DB_PATH=state_root / "jobs.sqlite3",
        TXT2CRS_ARTIFACT_ROOT=state_root / "artifacts",
        TXT2CRS_CODEX_HOME=state_root / "codex-home",
        TXT2CRS_WORKER_ROOT=tmp_path / "worker",
    )


def _json_request(
    *,
    input_type: str = "prompt",
    value: str = _PRIVATE_TOPIC,
) -> JobSubmissionRequest:
    """Build one public request through its strict transport schema."""

    return JobSubmissionRequest.model_validate(
        {
            "input": {"type": input_type, "value": value},
            "preferences": {
                "level": "beginner",
                "audience": "first-year students",
                "prior_knowledge": "basic SQL",
                "learning_goals": ["Explain index lookup", "Compare table scans"],
                "language": "en",
            },
            "consent_to_ai_processing": True,
            "learner_age_group": "adult",
        }
    )


def _job() -> JobRecord:
    """Return one durable accepted record from a facade double."""

    timestamp = datetime(2026, 7, 19, 20, 0, tzinfo=UTC)
    return JobRecord(
        schema_version="1.0",
        job_id="job-accepted",
        user_id="owner-1",
        idempotency_key=_PRIVATE_KEY,
        request_hash=_PRIVATE_HASH,
        status=JobStatus.accepted,
        revision=0,
        created_at=timestamp,
        updated_at=timestamp,
    )


class RecordingApplication:
    """Record only public facade calls and return or raise deterministically."""

    def __init__(
        self,
        *,
        result: JobRecord | None = None,
        submit_error: BaseException | None = None,
    ) -> None:
        self.result = result or _job()
        self.submit_error = submit_error
        self.submit_calls: list[dict[str, object]] = []
        self.reservation_calls = 0
        self.reservation = SimpleNamespace(
            maximum_input_tokens=600_000,
            maximum_output_tokens=150_000,
            maximum_research_cost_microusd=1_000_000,
        )

    def default_admission_reservation(self) -> object:
        self.reservation_calls += 1
        return self.reservation

    def submit(self, **arguments: object) -> JobRecord:
        self.submit_calls.append(arguments)
        if self.submit_error is not None:
            raise self.submit_error
        return self.result


class RecordingReadiness:
    """Expose a cached boolean and prove no refresh/probe method is needed."""

    def __init__(self, *, accepting_jobs: bool) -> None:
        self.accepting_jobs = accepting_jobs
        self.snapshot_calls = 0

    def snapshot(self) -> object:
        self.snapshot_calls += 1
        return SimpleNamespace(accepting_jobs=self.accepting_jobs)


class RecordingWorker:
    """Count latency-only wake hints and optionally simulate a broken hint."""

    def __init__(self, *, notify_error: BaseException | None = None) -> None:
        self.notify_error = notify_error
        self.notify_calls = 0

    def notify_runnable(self) -> None:
        self.notify_calls += 1
        if self.notify_error is not None:
            raise self.notify_error


def _service(
    tmp_path: Path,
    *,
    application: RecordingApplication | None = None,
    readiness: RecordingReadiness | None = None,
    worker: RecordingWorker | None = None,
) -> tuple[
    Txt2CrsSubmissionService,
    RecordingApplication,
    RecordingReadiness,
    RecordingWorker,
]:
    """Compose the service from side-effect-free recording collaborators."""

    recording_application = application or RecordingApplication()
    recording_readiness = readiness or RecordingReadiness(accepting_jobs=True)
    recording_worker = worker or RecordingWorker()
    service = Txt2CrsSubmissionService(
        application=cast(Txt2CrsApplication, recording_application),
        readiness=recording_readiness,
        worker=recording_worker,
        execution_profile=build_execution_profile(_settings(tmp_path)),
    )
    return service, recording_application, recording_readiness, recording_worker


def test_json_submission_maps_every_reviewed_value_then_notifies(
    tmp_path: Path,
) -> None:
    service, application, readiness, worker = _service(tmp_path)
    request = _json_request()

    job = service.submit_json(
        user_id="owner-1",
        idempotency_key=_PRIVATE_KEY,
        request=request,
    )

    assert job.job_id == "job-accepted"
    assert readiness.snapshot_calls == 1
    assert application.reservation_calls == 1
    assert worker.notify_calls == 1
    assert len(application.submit_calls) == 1
    submitted = application.submit_calls[0]
    assert submitted["user_id"] == "owner-1"
    assert submitted["idempotency_key"] == _PRIVATE_KEY
    assert submitted["admission_reservation"] is application.reservation
    generation_request = submitted["generation_request"]
    assert generation_request.input_payload.model_dump() == {
        "input_type": "prompt",
        "value": _PRIVATE_TOPIC,
        "media_type": "text/plain",
        "file_name": None,
        "metadata": {"input_mode": "prompt"},
    }
    assert generation_request.preferences.model_dump() == {
        "audience": "first-year students",
        "prior_knowledge": "basic SQL",
        "learning_goals": ("Explain index lookup", "Compare table scans"),
        "level": "beginner",
        "language": "en",
    }
    assert generation_request.provider_consent is True
    assert generation_request.learner_age_group.value == "adult"
    assert generation_request.policy_flags == ()
    assert generation_request.execution_profile.model_id == "gpt-5.6-sol"


def test_youtube_intent_maps_to_package_url_without_shell_host_policy(
    tmp_path: Path,
) -> None:
    service, application, _, _ = _service(tmp_path)

    service.submit_json(
        user_id="owner-1",
        idempotency_key=_PRIVATE_KEY,
        request=_json_request(input_type="youtube", value=_PRIVATE_URL),
    )

    input_payload = application.submit_calls[0]["generation_request"].input_payload
    assert input_payload.input_type == "url"
    assert input_payload.value == _PRIVATE_URL
    assert input_payload.media_type == "text/uri-list"
    assert input_payload.metadata == {"input_mode": "youtube"}


def test_upload_submission_preserves_validated_bytes_and_metadata(
    tmp_path: Path,
) -> None:
    service, application, _, worker = _service(tmp_path)
    upload_metadata = JobUploadMetadata.model_validate(
        {
            "preferences": {
                "level": "auto",
                "audience": None,
                "prior_knowledge": None,
                "learning_goals": [],
                "language": "auto",
            },
            "consent_to_ai_processing": True,
            "learner_age_group": "not_provided",
        }
    )
    validated_upload = ValidatedCourseUpload(
        input_type="document",
        content=b"PK\x03\x04reviewed",
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        file_name="course.docx",
        size_bytes=12,
    )

    service.submit_upload(
        user_id="owner-1",
        idempotency_key=_PRIVATE_KEY,
        metadata=upload_metadata,
        upload=validated_upload,
    )

    input_payload = application.submit_calls[0]["generation_request"].input_payload
    assert input_payload.input_type == "document"
    assert input_payload.value == b"PK\x03\x04reviewed"
    assert input_payload.file_name == "course.docx"
    assert input_payload.metadata == {"size_bytes": 12}
    assert worker.notify_calls == 1


def test_cached_unready_state_rejects_before_request_or_facade_work(
    tmp_path: Path,
) -> None:
    service, application, readiness, worker = _service(
        tmp_path,
        readiness=RecordingReadiness(accepting_jobs=False),
    )

    with pytest.raises(AppException) as captured_error:
        service.submit_json(
            user_id="owner-1",
            idempotency_key=_PRIVATE_KEY,
            request=_json_request(),
        )

    assert captured_error.value.code is ErrorCode.SYSTEM_NOT_READY
    assert readiness.snapshot_calls == 1
    assert application.reservation_calls == 0
    assert application.submit_calls == []
    assert worker.notify_calls == 0


@pytest.mark.parametrize(
    ("package_error", "expected_code"),
    [
        (
            AdmissionQuotaExceededError("private-quota-resource", 7),
            ErrorCode.JOB_ADMISSION_REJECTED,
        ),
        (
            IdempotencyConflictError("private request hash"),
            ErrorCode.JOB_IDEMPOTENCY_CONFLICT,
        ),
        (
            PreparationPolicyError(
                decision=PolicyDecision(
                    policy_version="content-policy-v1",
                    stage=PolicyStage.preflight,
                    outcome=PolicyOutcome.rejected,
                    reason_code="provider_consent_required",
                    high_risk=False,
                    public_message="Private policy detail.",
                )
            ),
            ErrorCode.JOB_POLICY_REJECTED,
        ),
        (RuntimeError("private provider failure"), ErrorCode.INTERNAL_ERROR),
    ],
)
def test_package_failures_translate_without_notifying_worker(
    tmp_path: Path,
    package_error: Exception,
    expected_code: ErrorCode,
) -> None:
    service, application, _, worker = _service(
        tmp_path,
        application=RecordingApplication(submit_error=package_error),
    )

    with pytest.raises(AppException) as captured_error:
        service.submit_json(
            user_id="owner-1",
            idempotency_key=_PRIVATE_KEY,
            request=_json_request(),
        )

    assert captured_error.value.code is expected_code
    assert len(application.submit_calls) == 1
    assert worker.notify_calls == 0
    assert captured_error.value.__cause__ is None


def test_post_commit_worker_hint_failure_does_not_replace_durable_success(
    tmp_path: Path,
) -> None:
    service, application, _, worker = _service(
        tmp_path,
        worker=RecordingWorker(notify_error=RuntimeError("private worker state")),
    )

    job = service.submit_json(
        user_id="owner-1",
        idempotency_key=_PRIVATE_KEY,
        request=_json_request(),
    )

    assert job.job_id == "job-accepted"
    assert len(application.submit_calls) == 1
    assert worker.notify_calls == 1


def test_terminal_replay_does_not_wake_worker(tmp_path: Path) -> None:
    """An exact replay of terminal durable work has nothing runnable to wake."""

    completed_job = _job().model_copy(
        update={"status": JobStatus.completed, "revision": 6}
    )
    service, application, _, worker = _service(
        tmp_path,
        application=RecordingApplication(result=completed_job),
    )

    replayed_job = service.submit_json(
        user_id="owner-1",
        idempotency_key=_PRIVATE_KEY,
        request=_json_request(),
    )

    assert replayed_job.status is JobStatus.completed
    assert application.submit_calls
    assert worker.notify_calls == 0


def test_cancellation_propagates_without_notification(tmp_path: Path) -> None:
    service, _, _, worker = _service(
        tmp_path,
        application=RecordingApplication(submit_error=asyncio.CancelledError()),
    )

    with pytest.raises(asyncio.CancelledError):
        service.submit_json(
            user_id="owner-1",
            idempotency_key=_PRIVATE_KEY,
            request=_json_request(),
        )

    assert worker.notify_calls == 0


def test_submission_logs_only_allowlisted_opaque_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Inspect service events without depending on process-global log handlers."""

    class RecordingLogger:
        """Capture structured values at the service's own logger boundary."""

        def __init__(self) -> None:
            self.records: list[tuple[str, dict[str, object] | None]] = []

        def info(
            self,
            event_name: str,
            *,
            extra: dict[str, object] | None = None,
        ) -> None:
            self.records.append((event_name, extra))

        def error(
            self,
            event_name: str,
            *,
            extra: dict[str, object] | None = None,
        ) -> None:
            self.records.append((event_name, extra))

    recording_logger = RecordingLogger()
    monkeypatch.setattr(
        "app.services.txt2crs_submission.logger",
        recording_logger,
    )
    service, _, _, _ = _service(tmp_path)

    service.submit_json(
        user_id="owner-1",
        idempotency_key=_PRIVATE_KEY,
        request=_json_request(input_type="youtube", value=_PRIVATE_URL),
    )

    rendered_records = repr(recording_logger.records)
    assert "job.submission_started" in rendered_records
    assert "job.submission_completed" in rendered_records
    assert "owner-1" in rendered_records
    assert "job-accepted" in rendered_records
    for private_value in (_PRIVATE_TOPIC, _PRIVATE_KEY, _PRIVATE_URL, _PRIVATE_HASH):
        assert private_value not in rendered_records
