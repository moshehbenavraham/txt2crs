# SPDX-License-Identifier: MIT-0

"""Tests for accepted-only checkpoints and exactly-once private delivery."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from tests.factories import (
    generous_admission_limits,
    standard_admission_reservation,
    valid_generation_request,
)
from txt2crs.jobs.models import CompletedJobPayload, JobRecord, JobStatus, ResumeState
from txt2crs.jobs.service import (
    InMemoryPrivateArtifactStore,
    JobService,
)
from txt2crs.jobs.stage_result import StageResult
from txt2crs.jobs.store import JobNotFoundError, SqliteJobStore
from txt2crs.rendering.artifacts import RenderedArtifact


class IdempotentNotificationSink:
    """Record one notification per stable delivery key."""

    def __init__(self) -> None:
        self.sent_keys: set[str] = set()
        self.send_attempts = 0

    def send_completion(
        self,
        *,
        user_id: str,
        job_id: str,
        idempotency_key: str,
    ) -> None:
        """Simulate a provider that deduplicates its idempotency key."""

        assert user_id
        assert job_id
        self.send_attempts += 1
        self.sent_keys.add(idempotency_key)


class FailOnceArtifactStore(InMemoryPrivateArtifactStore):
    """Simulate a worker crash immediately after entering delivery."""

    def __init__(self) -> None:
        super().__init__()
        self._should_fail = True

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Fail the first write and behave idempotently on the retry."""

        if self._should_fail:
            self._should_fail = False
            raise OSError("simulated storage outage")
        super().save(user_id=user_id, job_id=job_id, artifacts=artifacts)


def job_service(
    tmp_path: Path,
) -> tuple[
    JobService,
    InMemoryPrivateArtifactStore,
    IdempotentNotificationSink,
]:
    """Build a service with durable state and observable local side effects."""

    artifact_store = InMemoryPrivateArtifactStore()
    notification_sink = IdempotentNotificationSink()
    service = JobService(
        store=SqliteJobStore(
            tmp_path / "jobs.sqlite3",
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=artifact_store,
        notification_sink=notification_sink,
    )
    return service, artifact_store, notification_sink


def accepted_job(service: JobService) -> JobRecord:
    """Submit and start one job for stage tests."""

    generation_request = valid_generation_request()
    job = service.submit(
        user_id="user-1",
        idempotency_key="submit-1",
        generation_request=generation_request,
        admission_reservation=standard_admission_reservation(),
    )
    assert (
        service.resume(
            job_id=job.job_id,
            user_id="user-1",
        ).request
        == generation_request
    )
    return service.start(
        job_id=job.job_id,
        user_id="user-1",
        expected_revision=job.revision,
    )


def test_resume_delegates_one_atomic_store_snapshot(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The service cannot assemble job, request, and checkpoint across writes."""

    service, _artifact_store, _notification_sink = job_service(tmp_path)
    generation_request = valid_generation_request()
    job = service.submit(
        user_id="user-1",
        idempotency_key="atomic-resume",
        generation_request=generation_request,
        admission_reservation=standard_admission_reservation(),
    )
    expected_state = ResumeState(
        job=job,
        request=generation_request,
        checkpoint=None,
    )
    captured_calls: list[tuple[str, str]] = []

    def return_atomic_state(
        _store: SqliteJobStore,
        *,
        job_id: str,
        user_id: str,
    ) -> ResumeState:
        captured_calls.append((job_id, user_id))
        return expected_state

    monkeypatch.setattr(
        SqliteJobStore,
        "get_resume_state",
        return_atomic_state,
        raising=False,
    )

    assert service.resume(job_id=job.job_id, user_id="user-1") is expected_state
    assert captured_calls == [(job.job_id, "user-1")]


def test_only_accepted_required_stage_is_checkpointed(tmp_path: Path) -> None:
    """Required degradation becomes visible failure and stores no artifact."""

    service, _artifact_store, _notification_sink = job_service(tmp_path)
    started_job = accepted_job(service)

    failed_job = service.checkpoint_stage(
        job_id=started_job.job_id,
        user_id="user-1",
        expected_revision=started_job.revision,
        stage="collect_evidence",
        sequence=1,
        result=StageResult.degraded(
            artifact={"sources": []},
            issue_code="research_unavailable",
            public_message="Research is unavailable.",
        ),
        artifact_version="sha256:" + ("b" * 64),
        evidence_version=None,
        budget_snapshot={},
        next_status=JobStatus.drafting,
        required_stage=True,
    )

    assert failed_job.status is JobStatus.failed
    assert (
        service.resume(job_id=started_job.job_id, user_id="user-1").checkpoint is None
    )


def test_resume_returns_only_last_accepted_checkpoint(tmp_path: Path) -> None:
    """Crash recovery receives validated state and its exact job revision."""

    service, _artifact_store, _notification_sink = job_service(tmp_path)
    started_job = accepted_job(service)
    drafting_job = service.checkpoint_stage(
        job_id=started_job.job_id,
        user_id="user-1",
        expected_revision=started_job.revision,
        stage="collect_evidence",
        sequence=1,
        result=StageResult.accepted(artifact={"source_count": 3}),
        artifact_version="sha256:" + ("b" * 64),
        evidence_version="sha256:" + ("c" * 64),
        budget_snapshot={"research_calls": 2},
        next_status=JobStatus.drafting,
        required_stage=True,
    )

    resume_state = service.resume(job_id=started_job.job_id, user_id="user-1")

    assert resume_state.job == drafting_job
    assert resume_state.checkpoint is not None
    assert resume_state.checkpoint.artifact == {"source_count": 3}


def test_completion_stores_private_artifacts_and_notifies_once(tmp_path: Path) -> None:
    """Replaying completion cannot duplicate files or completion notification."""

    service, artifact_store, notification_sink = job_service(tmp_path)
    started_job = accepted_job(service)
    rendering_job = service.checkpoint_stage(
        job_id=started_job.job_id,
        user_id="user-1",
        expected_revision=started_job.revision,
        stage="cross_validate_artifacts",
        sequence=1,
        result=StageResult.accepted(artifact={"bundle": "validated"}),
        artifact_version="sha256:" + ("b" * 64),
        evidence_version="sha256:" + ("c" * 64),
        budget_snapshot={},
        next_status=JobStatus.rendering,
        required_stage=True,
    )
    payload = CompletedJobPayload(
        artifacts={
            "course_html": RenderedArtifact(
                file_name="course.html",
                media_type="text/html",
                content=b"<main>Course</main>",
            ),
            "answer_key_html": RenderedArtifact(
                file_name="answer-key.html",
                media_type="text/html",
                content=b"<main>Answers</main>",
            ),
        },
        usage_summary={"token_usage_state": "reported"},
    )

    completed_job = service.complete(
        job_id=rendering_job.job_id,
        user_id="user-1",
        expected_revision=rendering_job.revision,
        payload=payload,
    )
    replayed_completion = service.complete(
        job_id=rendering_job.job_id,
        user_id="user-1",
        expected_revision=rendering_job.revision,
        payload=payload,
    )

    assert completed_job.status is JobStatus.completed
    assert replayed_completion == completed_job
    assert artifact_store.save_count == 1
    assert notification_sink.sent_keys == {f"delivery:{rendering_job.job_id}"}
    assert notification_sink.send_attempts == 1
    assert (
        artifact_store.get(
            user_id="user-1",
            job_id=rendering_job.job_id,
        )["course_html"].content
        == b"<main>Course</main>"
    )
    with pytest.raises(JobNotFoundError):
        artifact_store.get(user_id="user-2", job_id=rendering_job.job_id)


def test_in_memory_artifact_queries_are_owner_scoped_and_context_managed() -> None:
    """The deterministic store matches real manifest and stream semantics."""

    artifact_store = InMemoryPrivateArtifactStore()
    artifact_store.save(
        user_id="user-1",
        job_id="job-in-memory",
        artifacts={
            "course_markdown": RenderedArtifact(
                file_name="course.md",
                media_type="text/markdown",
                content=b"# In-memory course",
            ),
            "assessment_pdf": RenderedArtifact(
                file_name="assessment.pdf",
                media_type="application/pdf",
                content=b"%PDF-assessment",
            ),
        },
    )

    manifest = artifact_store.get_manifest(
        user_id="user-1",
        job_id="job-in-memory",
    )
    with artifact_store.open_artifact(
        user_id="user-1",
        job_id="job-in-memory",
        artifact_id="course_markdown",
    ) as artifact_chunks:
        streamed_content = b"".join(artifact_chunks)

    assert [artifact.artifact_id for artifact in manifest.artifacts] == [
        "assessment_pdf",
        "course_markdown",
    ]
    assert streamed_content == b"# In-memory course"
    messages: list[str] = []
    for user_id, artifact_id in (
        ("user-2", "course_markdown"),
        ("user-1", "artifact-missing"),
    ):
        with pytest.raises(JobNotFoundError) as error_info:
            with artifact_store.open_artifact(
                user_id=user_id,
                job_id="job-in-memory",
                artifact_id=artifact_id,
            ):
                pytest.fail("Unauthorized or missing artifacts must not stream.")
        messages.append(str(error_info.value))
    assert messages[0] == messages[1]


def test_in_memory_artifact_save_is_atomic_when_manifest_clock_fails() -> None:
    """A timestamp failure cannot leave an unreadable half-created entry."""

    clock_values = iter(
        (
            datetime(2026, 7, 19, 12, 0),
            datetime(2026, 7, 19, 12, 1, tzinfo=UTC),
        )
    )
    artifact_store = InMemoryPrivateArtifactStore(clock=lambda: next(clock_values))
    artifacts = {
        "course_markdown": RenderedArtifact(
            file_name="course.md",
            media_type="text/markdown",
            content=b"# Course",
        )
    }

    with pytest.raises(ValueError, match="timezone-aware"):
        artifact_store.save(
            user_id="user-1",
            job_id="job-clock-retry",
            artifacts=artifacts,
        )
    artifact_store.save(
        user_id="user-1",
        job_id="job-clock-retry",
        artifacts=artifacts,
    )

    manifest = artifact_store.get_manifest(
        user_id="user-1",
        job_id="job-clock-retry",
    )
    assert [artifact.artifact_id for artifact in manifest.artifacts] == [
        "course_markdown"
    ]
    assert artifact_store.save_count == 1


def test_in_memory_artifact_save_rejects_empty_sets() -> None:
    """The deterministic store matches the production store's nonempty rule."""

    artifact_store = InMemoryPrivateArtifactStore()

    with pytest.raises(ValueError, match="At least one"):
        artifact_store.save(
            user_id="user-1",
            job_id="job-empty",
            artifacts={},
        )


def test_in_memory_artifact_save_rejects_unsafe_metadata() -> None:
    """Deterministic tests cannot accept data the production writer rejects."""

    artifact_store = InMemoryPrivateArtifactStore()

    with pytest.raises(ValueError, match="file name"):
        artifact_store.save(
            user_id="user-1",
            job_id="job-unsafe-metadata",
            artifacts={
                "course_markdown": RenderedArtifact(
                    file_name="course.md\r\nX-Injected: yes",
                    media_type="text/markdown",
                    content=b"# Course",
                )
            },
        )


def test_public_snapshot_reports_unpublished_artifacts_after_owner_check(
    tmp_path: Path,
) -> None:
    """An authorized accepted job may safely have no artifact manifest yet."""

    service, _artifact_store, _notification_sink = job_service(tmp_path)
    submitted_job = service.submit(
        user_id="user-1",
        idempotency_key="snapshot-before-artifacts",
        generation_request=valid_generation_request(),
        admission_reservation=standard_admission_reservation(),
    )

    snapshot = service.get_public_snapshot(
        job_id=submitted_job.job_id,
        user_id="user-1",
    )

    assert snapshot.status is JobStatus.accepted
    assert snapshot.artifacts.available is False
    assert snapshot.artifacts.count == 0
    with pytest.raises(JobNotFoundError):
        service.get_public_snapshot(
            job_id=submitted_job.job_id,
            user_id="user-2",
        )


def test_delivery_resumes_after_worker_failure_in_delivering_state(
    tmp_path: Path,
) -> None:
    """A delivery-side crash can retry from the durable validated checkpoint."""

    artifact_store = FailOnceArtifactStore()
    notification_sink = IdempotentNotificationSink()
    service = JobService(
        store=SqliteJobStore(
            tmp_path / "jobs.sqlite3",
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=artifact_store,
        notification_sink=notification_sink,
    )
    started_job = accepted_job(service)
    rendering_job = service.checkpoint_stage(
        job_id=started_job.job_id,
        user_id="user-1",
        expected_revision=started_job.revision,
        stage="cross_validate_artifacts",
        sequence=1,
        result=StageResult.accepted(artifact={"bundle": "validated"}),
        artifact_version="sha256:" + ("b" * 64),
        evidence_version="sha256:" + ("c" * 64),
        budget_snapshot={},
        next_status=JobStatus.rendering,
        required_stage=True,
    )
    payload = CompletedJobPayload(
        artifacts={
            "course_html": RenderedArtifact(
                file_name="course.html",
                media_type="text/html",
                content=b"<main>Course</main>",
            )
        },
        usage_summary={"token_usage_state": "reported"},
    )

    with pytest.raises(OSError, match="storage outage"):
        service.complete(
            job_id=rendering_job.job_id,
            user_id="user-1",
            expected_revision=rendering_job.revision,
            payload=payload,
        )
    interrupted_job = service.resume(
        job_id=rendering_job.job_id,
        user_id="user-1",
    ).job
    completed_job = service.complete(
        job_id=rendering_job.job_id,
        user_id="user-1",
        expected_revision=interrupted_job.revision,
        payload=payload,
    )

    assert interrupted_job.status is JobStatus.delivering
    assert completed_job.status is JobStatus.completed
    assert artifact_store.save_count == 1
    assert notification_sink.send_attempts == 1


def test_partial_failure_never_stores_or_delivers_artifacts(tmp_path: Path) -> None:
    """Failed validation cannot masquerade as success or trigger side effects."""

    service, artifact_store, notification_sink = job_service(tmp_path)
    started_job = accepted_job(service)

    failed_job = service.checkpoint_stage(
        job_id=started_job.job_id,
        user_id="user-1",
        expected_revision=started_job.revision,
        stage="verify_course",
        sequence=1,
        result=StageResult.failed(
            issue_code="citation_failure",
            public_message="Course citations could not be verified.",
        ),
        artifact_version="sha256:" + ("b" * 64),
        evidence_version=None,
        budget_snapshot={},
        next_status=JobStatus.validating,
        required_stage=True,
    )

    assert failed_job.status is JobStatus.failed
    assert artifact_store.save_count == 0
    assert notification_sink.send_attempts == 0


def test_all_service_reads_enforce_owner_identity(tmp_path: Path) -> None:
    """Application callers cannot read or resume another tenant's job."""

    service, _artifact_store, _notification_sink = job_service(tmp_path)
    started_job = accepted_job(service)

    with pytest.raises(JobNotFoundError):
        service.resume(job_id=started_job.job_id, user_id="user-2")
