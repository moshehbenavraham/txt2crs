# SPDX-License-Identifier: MIT-0

"""End-to-end durable execution from one submission through private delivery."""

from collections.abc import Callable
from pathlib import Path

import pytest

from tests.factories import (
    generous_admission_limits,
    standard_admission_reservation,
    valid_assessment_blueprint_data,
    valid_course_module_draft_data,
    valid_review_pack_data,
)
from tests.integration.test_generation_pipeline import (
    assessment_package_data,
    course_plan_data,
    frozen_evidence,
    pipeline_with_evidence,
    research_plan_data,
    scripted_turn,
)
from txt2crs.ai.fake_runtime import ScriptedTurn
from txt2crs.ai.runtime import CancellationToken
from txt2crs.generation.models import LearningPreferences
from txt2crs.generation.pipeline import (
    CourseGenerationPipeline,
    PipelineCheckpoint,
    PipelineResult,
)
from txt2crs.ingestion.models import InputPayload
from txt2crs.jobs.executor import GenerationJobExecutor, PolicyViolationError
from txt2crs.jobs.models import JobStatus
from txt2crs.jobs.service import InMemoryPrivateArtifactStore, JobService
from txt2crs.jobs.store import SqliteJobStore
from txt2crs.rendering.artifacts import ArtifactRenderer, RenderedArtifact
from txt2crs.security.policy import ContentPolicy


class RecordingNotificationSink:
    """Record the stable notification keys emitted after private storage."""

    def __init__(self) -> None:
        self.keys: list[str] = []

    def send_completion(
        self,
        *,
        user_id: str,
        job_id: str,
        idempotency_key: str,
    ) -> None:
        """Record one provider-idempotent completion request."""

        assert user_id
        assert job_id
        self.keys.append(idempotency_key)


class CountingPipeline:
    """Wrap the real offline pipeline so resume behavior is observable."""

    def __init__(self, pipeline: CourseGenerationPipeline) -> None:
        self._pipeline = pipeline
        self.call_count = 0

    def generate(
        self,
        *,
        payload: InputPayload,
        preferences: LearningPreferences,
        cancellation: CancellationToken,
        resume_checkpoint: PipelineCheckpoint | None = None,
        checkpoint_sink: Callable[[PipelineCheckpoint], None] | None = None,
    ) -> PipelineResult:
        """Generate once and count any accidental replay after checkpointing."""

        self.call_count += 1
        return self._pipeline.generate(
            payload=payload,
            preferences=preferences,
            cancellation=cancellation,
            resume_checkpoint=resume_checkpoint,
            checkpoint_sink=checkpoint_sink,
        )


class FailOncePrivateArtifactStore(InMemoryPrivateArtifactStore):
    """Fail the first delivery write to simulate process replacement."""

    def __init__(self) -> None:
        super().__init__()
        self._fail_next_save = True

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Raise once, then accept the exact replay."""

        if self._fail_next_save:
            self._fail_next_save = False
            raise OSError("simulated artifact storage outage")
        super().save(user_id=user_id, job_id=job_id, artifacts=artifacts)


def learning_preferences() -> LearningPreferences:
    """Return the preferences used by the credential-free pipeline fixture."""

    return LearningPreferences(
        audience="First-year computer-science students",
        prior_knowledge="Basic computer literacy",
        desired_depth="introductory",
        duration_minutes=60,
        language="en",
        tone="clear",
        accessibility_requirements=["semantic headings"],
        assessment_item_count=1,
        passing_percentage=70,
        high_risk_course=False,
    )


def input_payload() -> InputPayload:
    """Return one complete topic request."""

    return InputPayload(
        input_type="prompt",
        value="Teach Python variables.",
        media_type="text/plain",
        file_name=None,
        metadata={},
    )


def test_executor_completes_and_privately_delivers_all_formats(
    tmp_path: Path,
) -> None:
    """One submitted job reaches a durable checkpoint and private artifacts."""

    private_store = InMemoryPrivateArtifactStore()
    notification_sink = RecordingNotificationSink()
    service = JobService(
        store=SqliteJobStore(
            tmp_path / "jobs.sqlite3",
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=private_store,
        notification_sink=notification_sink,
    )
    job = service.submit(
        user_id="user-1",
        idempotency_key="generate-python",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=standard_admission_reservation(),
    )
    pipeline = CountingPipeline(pipeline_with_evidence(frozen_evidence()))
    executor = GenerationJobExecutor(
        job_service=service,
        pipeline=pipeline,
        renderer=ArtifactRenderer(),
        content_policy=ContentPolicy(),
    )

    completed_job = executor.execute(
        job_id=job.job_id,
        user_id="user-1",
        payload=input_payload(),
        preferences=learning_preferences(),
        cancellation=CancellationToken(),
        provider_consent=True,
        learner_age=18,
    )

    resume_state = service.resume(job_id=job.job_id, user_id="user-1")
    stored_artifacts = private_store.get(user_id="user-1", job_id=job.job_id)
    assert completed_job.status is JobStatus.completed
    assert resume_state.checkpoint is not None
    assert resume_state.checkpoint.stage == "cross_validate_artifacts"
    assert resume_state.checkpoint.sequence == 9
    assert len(stored_artifacts) == 16
    assert pipeline.call_count == 1
    assert notification_sink.keys == [f"delivery:{job.job_id}"]


def test_executor_resumes_delivery_without_regenerating_from_model(
    tmp_path: Path,
) -> None:
    """A replacement worker revalidates the durable bundle and skips model work."""

    private_store = FailOncePrivateArtifactStore()
    notification_sink = RecordingNotificationSink()
    service = JobService(
        store=SqliteJobStore(
            tmp_path / "jobs.sqlite3",
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=private_store,
        notification_sink=notification_sink,
    )
    job = service.submit(
        user_id="user-1",
        idempotency_key="generate-python",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=standard_admission_reservation(),
    )
    pipeline = CountingPipeline(pipeline_with_evidence(frozen_evidence()))
    executor = GenerationJobExecutor(
        job_service=service,
        pipeline=pipeline,
        renderer=ArtifactRenderer(),
        content_policy=ContentPolicy(),
    )

    with pytest.raises(OSError, match="storage outage"):
        executor.execute(
            job_id=job.job_id,
            user_id="user-1",
            payload=input_payload(),
            preferences=learning_preferences(),
            cancellation=CancellationToken(),
            provider_consent=True,
            learner_age=18,
        )
    interrupted_state = service.resume(job_id=job.job_id, user_id="user-1")
    completed_job = executor.execute(
        job_id=job.job_id,
        user_id="user-1",
        payload=input_payload(),
        preferences=learning_preferences(),
        cancellation=CancellationToken(),
        provider_consent=True,
        learner_age=18,
    )

    assert interrupted_state.job.status is JobStatus.delivering
    assert completed_job.status is JobStatus.completed
    assert pipeline.call_count == 1
    assert private_store.save_count == 1


def test_executor_rejects_missing_consent_before_model_or_research_work(
    tmp_path: Path,
) -> None:
    """Provider consent is a hard application boundary, not a UI convention."""

    private_store = InMemoryPrivateArtifactStore()
    service = JobService(
        store=SqliteJobStore(
            tmp_path / "jobs.sqlite3",
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=private_store,
        notification_sink=RecordingNotificationSink(),
    )
    job = service.submit(
        user_id="user-1",
        idempotency_key="no-consent",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=standard_admission_reservation(),
    )
    pipeline = CountingPipeline(pipeline_with_evidence(frozen_evidence()))
    executor = GenerationJobExecutor(
        job_service=service,
        pipeline=pipeline,
        renderer=ArtifactRenderer(),
        content_policy=ContentPolicy(),
    )

    with pytest.raises(PolicyViolationError, match="Consent"):
        executor.execute(
            job_id=job.job_id,
            user_id="user-1",
            payload=input_payload(),
            preferences=learning_preferences(),
            cancellation=CancellationToken(),
            provider_consent=False,
            learner_age=18,
        )

    rejected_job = service.resume(job_id=job.job_id, user_id="user-1").job
    assert rejected_job.status is JobStatus.failed
    assert rejected_job.failure_code == "provider_consent_required"
    assert pipeline.call_count == 0
    assert private_store.save_count == 0


def test_executor_resumes_from_last_stage_after_worker_process_exit(
    tmp_path: Path,
) -> None:
    """A replacement worker does not replay accepted research or model turns."""

    database_path = tmp_path / "jobs.sqlite3"
    private_store = InMemoryPrivateArtifactStore()
    notification_sink = RecordingNotificationSink()
    first_service = JobService(
        store=SqliteJobStore(
            database_path,
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=private_store,
        notification_sink=notification_sink,
    )
    job = first_service.submit(
        user_id="user-1",
        idempotency_key="resume-stage",
        input_hash="sha256:" + ("a" * 64),
        admission_reservation=standard_admission_reservation(),
    )
    first_pipeline = pipeline_with_evidence(
        frozen_evidence(),
        scripted_turns=(
            # The research plan is accepted and checkpointed. Process loss
            # occurs when the next model turn begins.
            scripted_turn(research_plan_data(), 1),
            ScriptedTurn(error=SystemExit("simulated worker replacement")),
        ),
    )
    first_executor = GenerationJobExecutor(
        job_service=first_service,
        pipeline=first_pipeline,
        renderer=ArtifactRenderer(),
        content_policy=ContentPolicy(),
    )

    with pytest.raises(SystemExit, match="worker replacement"):
        first_executor.execute(
            job_id=job.job_id,
            user_id="user-1",
            payload=input_payload(),
            preferences=learning_preferences(),
            cancellation=CancellationToken(),
            provider_consent=True,
            learner_age=18,
        )

    interrupted_state = first_service.resume(
        job_id=job.job_id,
        user_id="user-1",
    )
    assert interrupted_state.job.status is JobStatus.drafting
    assert interrupted_state.checkpoint is not None
    assert interrupted_state.checkpoint.stage == "collect_evidence"
    assert interrupted_state.checkpoint.sequence == 3

    replacement_service = JobService(
        store=SqliteJobStore(
            database_path,
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=private_store,
        notification_sink=notification_sink,
    )
    replacement_pipeline = pipeline_with_evidence(
        frozen_evidence(),
        scripted_turns=(
            scripted_turn(course_plan_data(), 2),
            scripted_turn(valid_course_module_draft_data(), 3),
            scripted_turn(valid_review_pack_data(), 4),
            scripted_turn(valid_assessment_blueprint_data(), 5),
            scripted_turn(assessment_package_data(), 6),
        ),
    )
    replacement_executor = GenerationJobExecutor(
        job_service=replacement_service,
        pipeline=replacement_pipeline,
        renderer=ArtifactRenderer(),
        content_policy=ContentPolicy(),
    )
    completed_job = replacement_executor.execute(
        job_id=job.job_id,
        user_id="user-1",
        payload=input_payload(),
        preferences=learning_preferences(),
        cancellation=CancellationToken(),
        provider_consent=True,
        learner_age=18,
    )

    assert completed_job.status is JobStatus.completed
    final_checkpoint = replacement_service.resume(
        job_id=job.job_id,
        user_id="user-1",
    ).checkpoint
    assert final_checkpoint is not None
    assert final_checkpoint.stage == "cross_validate_artifacts"
    assert final_checkpoint.sequence == 9
