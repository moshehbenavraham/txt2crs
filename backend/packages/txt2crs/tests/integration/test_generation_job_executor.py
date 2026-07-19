# SPDX-License-Identifier: MIT-0

"""Durable preparation-first execution through private artifact delivery."""

from collections import deque
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import cast

import pytest

from tests.factories import (
    generous_admission_limits,
    standard_admission_reservation,
    valid_assessment_blueprint_data,
    valid_course_module_draft_data,
    valid_generation_request,
    valid_pipeline_checkpoint,
    valid_review_pack_data,
)
from tests.integration.test_generation_pipeline import (
    assessment_package_data,
    course_plan_data,
    frozen_evidence,
    generation_request_for_pipeline,
    pipeline_with_evidence,
    research_plan_data,
    scripted_turn,
)
from txt2crs.ai.fake_runtime import ScriptedTurn
from txt2crs.ai.runtime import CancellationToken
from txt2crs.domain.models import InputDocument
from txt2crs.generation.pipeline import (
    CourseGenerationPipeline,
    PipelineCheckpoint,
    PipelineResult,
)
from txt2crs.ingestion.models import InputPayload
from txt2crs.ingestion.service import IngestionService
from txt2crs.jobs.executor import (
    DurablePipeline,
    DurablePipelineFactory,
    GenerationJobExecutor,
    JobExecutionStateError,
    PolicyViolationError,
)
from txt2crs.jobs.models import JobStatus
from txt2crs.jobs.notifications import DeliveryNotificationPolicy
from txt2crs.jobs.preparation import GenerationPreparation, GenerationPreparationService
from txt2crs.jobs.requests import GenerationRequest
from txt2crs.jobs.service import InMemoryPrivateArtifactStore, JobService
from txt2crs.jobs.stage_result import StageResult
from txt2crs.jobs.store import SqliteJobStore
from txt2crs.rendering.artifacts import ArtifactRenderer, RenderedArtifact
from txt2crs.security.policy import ContentPolicy


class CountingPipeline:
    """Wrap the real offline pipeline so resume behavior is observable."""

    def __init__(self, pipeline: CourseGenerationPipeline) -> None:
        self._pipeline = pipeline
        self.call_count = 0

    def generate(
        self,
        *,
        preparation: GenerationPreparation,
        cancellation: CancellationToken,
        resume_checkpoint: PipelineCheckpoint | None = None,
        checkpoint_sink: Callable[[PipelineCheckpoint], None] | None = None,
    ) -> PipelineResult:
        """Generate once and count accidental provider-backed replay."""

        self.call_count += 1
        return self._pipeline.generate(
            preparation=preparation,
            cancellation=cancellation,
            resume_checkpoint=resume_checkpoint,
            checkpoint_sink=checkpoint_sink,
        )


class RecordingPipelineFactory:
    """Open scripted pipelines lazily and record their complete lifetime."""

    def __init__(
        self,
        pipelines: tuple[DurablePipeline, ...],
        *,
        before_open: Callable[[], None] | None = None,
        lifecycle_events: list[str] | None = None,
    ) -> None:
        self._pipelines = deque(pipelines)
        self._before_open = before_open
        self.requests: list[GenerationRequest] = []
        self.lifecycle_events = lifecycle_events if lifecycle_events is not None else []

    @contextmanager
    def open(
        self,
        generation_request: GenerationRequest,
    ) -> Iterator[DurablePipeline]:
        """Own one pipeline from post-preparation construction through its turn."""

        if self._before_open is not None:
            self._before_open()
        self.requests.append(generation_request)
        self.lifecycle_events.append("pipeline.open")
        try:
            if not self._pipelines:
                raise AssertionError(
                    "No pipeline was configured for this factory call."
                )
            yield self._pipelines.popleft()
        finally:
            self.lifecycle_events.append("pipeline.close")


class RaisingPipelineFactory:
    """Simulate abrupt replacement at the provider-graph construction boundary."""

    def __init__(self, *, before_create: Callable[[], None]) -> None:
        self._before_create = before_create
        self.call_count = 0

    @contextmanager
    def open(
        self,
        _generation_request: GenerationRequest,
    ) -> Iterator[CountingPipeline]:
        """Prove preparation durability, then interrupt managed construction."""

        self._before_create()
        self.call_count += 1
        try:
            raise SystemExit("simulated worker replacement after preparation")
            yield  # pragma: no cover - makes this a typed generator context.
        finally:
            self.call_count += 0


class FailingPipelineFactory:
    """Raise an ordinary provider-graph construction failure."""

    def __init__(self) -> None:
        self.call_count = 0
        self.lifecycle_events: list[str] = []

    @contextmanager
    def open(
        self,
        _generation_request: GenerationRequest,
    ) -> Iterator[CountingPipeline]:
        """Represent a managed provider startup failure, not process loss."""

        self.call_count += 1
        self.lifecycle_events.append("pipeline.open")
        try:
            raise RuntimeError("simulated provider startup failure")
            yield  # pragma: no cover - makes this a typed generator context.
        finally:
            self.lifecycle_events.append("pipeline.close")


class FailingGenerationPipeline:
    """Raise after managed provider construction has yielded successfully."""

    def __init__(self, *, cancel_before_failure: bool = False) -> None:
        self._cancel_before_failure = cancel_before_failure

    def generate(
        self,
        *,
        preparation: GenerationPreparation,
        cancellation: CancellationToken,
        resume_checkpoint: PipelineCheckpoint | None = None,
        checkpoint_sink: Callable[[PipelineCheckpoint], None] | None = None,
    ) -> PipelineResult:
        """Fail inside the pipeline, optionally through the cancellation path."""

        assert preparation
        assert resume_checkpoint is None
        assert checkpoint_sink is not None
        if self._cancel_before_failure:
            cancellation.cancel()
            cancellation.raise_if_cancelled()
        raise RuntimeError("simulated generation failure")


class ShutdownInterruptedPipeline:
    """Represent cooperative process shutdown during provider-backed work."""

    def generate(
        self,
        *,
        preparation: GenerationPreparation,
        cancellation: CancellationToken,
        resume_checkpoint: PipelineCheckpoint | None = None,
        checkpoint_sink: Callable[[PipelineCheckpoint], None] | None = None,
    ) -> PipelineResult:
        """Interrupt after preparation without claiming the learner cancelled."""

        assert preparation
        assert resume_checkpoint is None
        assert checkpoint_sink is not None
        cancellation.interrupt_for_shutdown()
        cancellation.raise_if_cancelled()
        raise AssertionError("The interruption must stop before output is accepted.")


class FailingResultExtractionPipeline:
    """Return a result whose artifact read requires the provider context."""

    def __init__(self, *, provider_is_open: Callable[[], bool]) -> None:
        self._provider_is_open = provider_is_open

    def generate(
        self,
        *,
        preparation: GenerationPreparation,
        cancellation: CancellationToken,
        resume_checkpoint: PipelineCheckpoint | None = None,
        checkpoint_sink: Callable[[PipelineCheckpoint], None] | None = None,
    ) -> PipelineResult:
        """Checkpoint a valid final bundle, then defer one failing result read."""

        assert preparation
        assert resume_checkpoint is None
        assert checkpoint_sink is not None
        final_checkpoint = valid_pipeline_checkpoint()
        checkpoint_sink(final_checkpoint)

        class DeferredResult:
            """Small result-shaped value that observes provider ownership."""

            usage_records: tuple[()] = ()

            @property
            def rendered_artifacts(self) -> dict[str, RenderedArtifact]:
                assert self_provider_is_open(), (
                    "The provider context closed before result extraction."
                )
                raise RuntimeError("simulated result extraction failure")

        self_provider_is_open = self._provider_is_open
        return cast(PipelineResult, DeferredResult())


class RecordingIngestionService:
    """Return configured normalized input while counting source reads."""

    def __init__(self, *, normalized_text: str, language: str = "en") -> None:
        self._normalized_text = normalized_text
        self._language = language
        self.payloads: list[InputPayload] = []

    def ingest(self, payload: InputPayload) -> InputDocument:
        """Record one source read and return its canonical document."""

        self.payloads.append(payload)
        return InputDocument(
            schema_version="1.0",
            document_id="input-executor",
            input_type=payload.input_type,
            media_type=payload.media_type,
            normalized_text=self._normalized_text,
            language=self._language,
            metadata={},
            content_hash=(
                "sha256:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
            ),
            warnings=[],
            locations=[],
        )


class FailIfIngestionRepeats:
    """Fail loudly if recovery attempts to read an accepted source again."""

    def ingest(self, _payload: InputPayload) -> InputDocument:
        """Recovery must use the checkpoint instead of entering this method."""

        raise AssertionError("accepted source preparation was repeated")


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


def _job_service(
    database_path: Path,
    *,
    artifact_store: InMemoryPrivateArtifactStore | None = None,
) -> JobService:
    """Build one real SQLite application boundary for executor tests."""

    return JobService(
        store=SqliteJobStore(
            database_path,
            admission_limits=generous_admission_limits(),
        ),
        artifact_store=artifact_store or InMemoryPrivateArtifactStore(),
        notification_policy=DeliveryNotificationPolicy.disabled(),
    )


def _preparation_service(
    ingestion_service: IngestionService
    | RecordingIngestionService
    | FailIfIngestionRepeats,
) -> GenerationPreparationService:
    """Build preparation with the stored policy version used by fixtures."""

    return GenerationPreparationService(
        ingestion_service=ingestion_service,
        content_policy=ContentPolicy(policy_version="content-policy-v1"),
    )


def _submit_pipeline_request(
    service: JobService,
    *,
    idempotency_key: str,
    generation_request: GenerationRequest | None = None,
) -> tuple[str, GenerationRequest]:
    """Persist one complete request and return its durable job identifier."""

    request = generation_request or generation_request_for_pipeline()
    job = service.submit(
        user_id="user-1",
        idempotency_key=idempotency_key,
        generation_request=request,
        admission_reservation=standard_admission_reservation(),
    )
    return job.job_id, request


def _executor(
    *,
    service: JobService,
    preparation_service: GenerationPreparationService,
    pipeline_factory: DurablePipelineFactory,
) -> GenerationJobExecutor:
    """Build the executor without constructing provider-backed work eagerly."""

    return GenerationJobExecutor(
        job_service=service,
        preparation_service=preparation_service,
        pipeline_factory=pipeline_factory,
        renderer=ArtifactRenderer(),
    )


def test_executor_persists_preparation_before_lazy_pipeline_and_delivers(
    tmp_path: Path,
) -> None:
    """One request reaches all artifacts only after sequence-1 preparation."""

    private_store = InMemoryPrivateArtifactStore()
    service = _job_service(
        tmp_path / "jobs.sqlite3",
        artifact_store=private_store,
    )
    job_id, request = _submit_pipeline_request(
        service,
        idempotency_key="generate-python",
    )
    ingestion_service = RecordingIngestionService(
        normalized_text="Teach Python variables."
    )
    pipeline = CountingPipeline(pipeline_with_evidence(frozen_evidence()))

    def assert_preparation_is_durable() -> None:
        checkpoint = service.resume(job_id=job_id, user_id="user-1").checkpoint
        assert checkpoint is not None
        assert checkpoint.stage == "prepare_input"
        assert checkpoint.sequence == 1

    pipeline_factory = RecordingPipelineFactory(
        (pipeline,),
        before_open=assert_preparation_is_durable,
    )
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(ingestion_service),
        pipeline_factory=pipeline_factory,
    )

    completed_job = executor.execute(
        job_id=job_id,
        user_id="user-1",
        cancellation=CancellationToken(),
    )

    resume_state = service.resume(job_id=job_id, user_id="user-1")
    assert completed_job.status is JobStatus.completed
    assert resume_state.checkpoint is not None
    assert resume_state.checkpoint.stage == "cross_validate_artifacts"
    assert resume_state.checkpoint.sequence == 9
    assert len(private_store.get(user_id="user-1", job_id=job_id)) == 16
    assert ingestion_service.payloads == [request.input_payload]
    assert pipeline_factory.requests == [request]
    assert pipeline.call_count == 1
    assert pipeline_factory.lifecycle_events == ["pipeline.open", "pipeline.close"]


def test_executor_rejects_preflight_without_ingestion_or_pipeline_construction(
    tmp_path: Path,
) -> None:
    """Missing consent is terminal before any source or provider work."""

    service = _job_service(tmp_path / "jobs.sqlite3")
    base_request = generation_request_for_pipeline()
    denied_request = valid_generation_request(
        input_payload=base_request.input_payload,
        preferences=base_request.preferences,
        provider_consent=False,
        execution_profile=base_request.execution_profile,
    )
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key="no-consent",
        generation_request=denied_request,
    )
    ingestion_service = RecordingIngestionService(normalized_text="unused")
    pipeline_factory = RecordingPipelineFactory(())
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(ingestion_service),
        pipeline_factory=pipeline_factory,
    )

    with pytest.raises(PolicyViolationError, match="Permission"):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    rejected_job = service.resume(job_id=job_id, user_id="user-1").job
    assert rejected_job.status is JobStatus.failed
    assert rejected_job.failure_code == "provider_consent_required"
    assert ingestion_service.payloads == []
    assert pipeline_factory.requests == []


def test_executor_rejects_post_ingestion_review_without_pipeline_construction(
    tmp_path: Path,
) -> None:
    """Normalized binary content is terminally gated before provider creation."""

    service = _job_service(tmp_path / "jobs.sqlite3")
    base_request = generation_request_for_pipeline()
    binary_request = valid_generation_request(
        input_payload=InputPayload(
            input_type="pdf",
            value=b"%PDF-safe",
            media_type="application/pdf",
            file_name="course.pdf",
            metadata={},
        ),
        preferences=base_request.preferences,
        execution_profile=base_request.execution_profile,
    )
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key="post-policy",
        generation_request=binary_request,
    )
    ingestion_service = RecordingIngestionService(
        normalized_text="A guide to adjusting insulin dosage."
    )
    pipeline_factory = RecordingPipelineFactory(())
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(ingestion_service),
        pipeline_factory=pipeline_factory,
    )

    with pytest.raises(PolicyViolationError, match="qualified review"):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    rejected_job = service.resume(job_id=job_id, user_id="user-1").job
    assert rejected_job.status is JobStatus.failed
    assert rejected_job.failure_code == "high_risk_review_required"
    assert ingestion_service.payloads == [binary_request.input_payload]
    assert pipeline_factory.requests == []


def test_pipeline_factory_failure_settles_generation_after_preparation(
    tmp_path: Path,
) -> None:
    """An ordinary provider startup failure cannot leave a hot-loop job."""

    service = _job_service(tmp_path / "jobs.sqlite3")
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key="provider-startup-failure",
    )
    pipeline_factory = FailingPipelineFactory()
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(
            RecordingIngestionService(normalized_text="Teach Python variables.")
        ),
        pipeline_factory=pipeline_factory,
    )

    with pytest.raises(RuntimeError, match="provider startup"):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    resume_state = service.resume(job_id=job_id, user_id="user-1")
    assert resume_state.job.status is JobStatus.failed
    assert resume_state.job.failure_code == "generation_failed"
    assert resume_state.checkpoint is not None
    assert resume_state.checkpoint.stage == "prepare_input"
    assert pipeline_factory.call_count == 1
    assert pipeline_factory.lifecycle_events == ["pipeline.open", "pipeline.close"]


@pytest.mark.parametrize(
    ("cancel_before_failure", "expected_status", "expected_failure_code"),
    [
        (False, JobStatus.failed, "generation_failed"),
        (True, JobStatus.cancelled, "cancelled"),
    ],
)
def test_pipeline_context_closes_after_generation_failure_or_cancellation(
    tmp_path: Path,
    cancel_before_failure: bool,
    expected_status: JobStatus,
    expected_failure_code: str,
) -> None:
    """Every yielded provider graph closes before terminal settlement returns."""

    service = _job_service(tmp_path / "jobs.sqlite3")
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key=f"managed-exit-{expected_status.value}",
    )
    pipeline_factory = RecordingPipelineFactory(
        # The factory is structurally typed, so the failure double can focus
        # on the same generation method without inheriting production code.
        (FailingGenerationPipeline(cancel_before_failure=cancel_before_failure),),
    )
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(
            RecordingIngestionService(normalized_text="Teach Python variables.")
        ),
        pipeline_factory=pipeline_factory,
    )

    with pytest.raises(RuntimeError):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    settled_job = service.resume(job_id=job_id, user_id="user-1").job
    assert settled_job.status is expected_status
    assert settled_job.failure_code == expected_failure_code
    assert pipeline_factory.lifecycle_events == ["pipeline.open", "pipeline.close"]


def test_application_shutdown_keeps_interrupted_job_runnable(
    tmp_path: Path,
) -> None:
    """Deployment interruption preserves the exact durable recovery checkpoint."""

    service = _job_service(tmp_path / "jobs.sqlite3")
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key="application-shutdown",
    )
    pipeline_factory = RecordingPipelineFactory((ShutdownInterruptedPipeline(),))
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(
            RecordingIngestionService(normalized_text="Teach Python variables.")
        ),
        pipeline_factory=pipeline_factory,
    )

    with pytest.raises(RuntimeError, match="cancelled"):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    resume_state = service.resume(job_id=job_id, user_id="user-1")
    next_runnable = service.next_runnable()
    assert resume_state.job.status is JobStatus.researching
    assert resume_state.job.failure_code is None
    assert resume_state.checkpoint is not None
    assert resume_state.checkpoint.stage == "prepare_input"
    assert next_runnable is not None
    assert next_runnable.job.job_id == job_id
    assert pipeline_factory.lifecycle_events == ["pipeline.open", "pipeline.close"]


def test_pipeline_context_remains_open_through_result_extraction(
    tmp_path: Path,
) -> None:
    """Provider ownership includes final-checkpoint and result acceptance."""

    service = _job_service(tmp_path / "jobs.sqlite3")
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key="managed-result-extraction",
    )
    lifecycle_events: list[str] = []
    pipeline = FailingResultExtractionPipeline(
        provider_is_open=lambda: lifecycle_events == ["pipeline.open"]
    )
    pipeline_factory = RecordingPipelineFactory(
        (pipeline,),
        lifecycle_events=lifecycle_events,
    )
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(
            RecordingIngestionService(normalized_text="Teach Python variables.")
        ),
        pipeline_factory=pipeline_factory,
    )

    with pytest.raises(RuntimeError, match="result extraction failure"):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    settled_job = service.resume(job_id=job_id, user_id="user-1").job
    assert settled_job.status is JobStatus.failed
    assert pipeline_factory.lifecycle_events == ["pipeline.open", "pipeline.close"]


def test_restart_reuses_durable_preparation_without_refetching(
    tmp_path: Path,
) -> None:
    """Replacement after provider construction begins uses sequence 1 exactly."""

    database_path = tmp_path / "jobs.sqlite3"
    private_store = InMemoryPrivateArtifactStore()
    first_service = _job_service(
        database_path,
        artifact_store=private_store,
    )
    job_id, _request = _submit_pipeline_request(
        first_service,
        idempotency_key="resume-preparation",
    )
    first_ingestion = RecordingIngestionService(
        normalized_text="Teach Python variables."
    )

    def assert_preparation_is_durable() -> None:
        checkpoint = first_service.resume(
            job_id=job_id,
            user_id="user-1",
        ).checkpoint
        assert checkpoint is not None
        assert checkpoint.stage == "prepare_input"
        assert checkpoint.sequence == 1

    first_executor = _executor(
        service=first_service,
        preparation_service=_preparation_service(first_ingestion),
        pipeline_factory=RaisingPipelineFactory(
            before_create=assert_preparation_is_durable
        ),
    )

    with pytest.raises(SystemExit, match="after preparation"):
        first_executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    replacement_service = _job_service(
        database_path,
        artifact_store=private_store,
    )
    replacement_pipeline = CountingPipeline(pipeline_with_evidence(frozen_evidence()))
    replacement_factory = RecordingPipelineFactory((replacement_pipeline,))
    replacement_executor = _executor(
        service=replacement_service,
        preparation_service=_preparation_service(FailIfIngestionRepeats()),
        pipeline_factory=replacement_factory,
    )

    completed_job = replacement_executor.execute(
        job_id=job_id,
        user_id="user-1",
        cancellation=CancellationToken(),
    )

    assert completed_job.status is JobStatus.completed
    assert len(first_ingestion.payloads) == 1
    assert replacement_pipeline.call_count == 1


def test_restart_reuses_resolved_preferences_after_design_course(
    tmp_path: Path,
) -> None:
    """A replacement worker does not reinterpret auto or replay accepted stages."""

    database_path = tmp_path / "jobs.sqlite3"
    private_store = InMemoryPrivateArtifactStore()
    first_service = _job_service(
        database_path,
        artifact_store=private_store,
    )
    job_id, _request = _submit_pipeline_request(
        first_service,
        idempotency_key="resume-resolved-preferences",
    )
    first_pipeline = CountingPipeline(
        pipeline_with_evidence(
            frozen_evidence(),
            scripted_turns=(
                scripted_turn(research_plan_data(), 1),
                scripted_turn(course_plan_data(), 2),
                ScriptedTurn(error=SystemExit("simulated module replacement")),
            ),
        )
    )
    first_executor = _executor(
        service=first_service,
        preparation_service=_preparation_service(
            RecordingIngestionService(normalized_text="Teach Python variables.")
        ),
        pipeline_factory=RecordingPipelineFactory((first_pipeline,)),
    )

    with pytest.raises(SystemExit, match="module replacement"):
        first_executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    interrupted_checkpoint = first_service.resume(
        job_id=job_id,
        user_id="user-1",
    ).checkpoint
    assert interrupted_checkpoint is not None
    assert interrupted_checkpoint.stage == "design_course"
    assert interrupted_checkpoint.sequence == 4
    parsed_checkpoint = PipelineCheckpoint.model_validate(
        interrupted_checkpoint.artifact
    )
    assert parsed_checkpoint.resolved_preferences is not None
    assert parsed_checkpoint.resolved_preferences.level == "beginner"

    replacement_service = _job_service(
        database_path,
        artifact_store=private_store,
    )
    replacement_pipeline = CountingPipeline(
        pipeline_with_evidence(
            frozen_evidence(),
            scripted_turns=(
                scripted_turn(valid_course_module_draft_data(), 3),
                scripted_turn(valid_review_pack_data(), 4),
                scripted_turn(valid_assessment_blueprint_data(), 5),
                scripted_turn(assessment_package_data(), 6),
            ),
        )
    )
    replacement_executor = _executor(
        service=replacement_service,
        preparation_service=_preparation_service(FailIfIngestionRepeats()),
        pipeline_factory=RecordingPipelineFactory((replacement_pipeline,)),
    )

    completed_job = replacement_executor.execute(
        job_id=job_id,
        user_id="user-1",
        cancellation=CancellationToken(),
    )

    assert completed_job.status is JobStatus.completed
    assert replacement_pipeline.call_count == 1


def test_delivery_restart_does_not_construct_pipeline_or_repeat_preparation(
    tmp_path: Path,
) -> None:
    """Local delivery recovery stays independent from provider availability."""

    database_path = tmp_path / "jobs.sqlite3"
    private_store = FailOncePrivateArtifactStore()
    service = _job_service(database_path, artifact_store=private_store)
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key="resume-delivery",
    )
    pipeline = CountingPipeline(pipeline_with_evidence(frozen_evidence()))
    first_factory = RecordingPipelineFactory((pipeline,))
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(
            RecordingIngestionService(normalized_text="Teach Python variables.")
        ),
        pipeline_factory=first_factory,
    )

    with pytest.raises(OSError, match="storage outage"):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    replacement_service = _job_service(
        database_path,
        artifact_store=private_store,
    )
    replacement_factory = RecordingPipelineFactory(())
    replacement_executor = _executor(
        service=replacement_service,
        preparation_service=_preparation_service(FailIfIngestionRepeats()),
        pipeline_factory=replacement_factory,
    )
    completed_job = replacement_executor.execute(
        job_id=job_id,
        user_id="user-1",
        cancellation=CancellationToken(),
    )

    assert completed_job.status is JobStatus.completed
    assert pipeline.call_count == 1
    assert replacement_factory.requests == []
    assert replacement_factory.lifecycle_events == []
    assert private_store.save_count == 1


def test_delivery_rejects_checkpoint_from_a_different_request(
    tmp_path: Path,
) -> None:
    """Rendering cannot deliver a valid bundle transplanted from another job."""

    private_store = InMemoryPrivateArtifactStore()
    service = _job_service(
        tmp_path / "jobs.sqlite3",
        artifact_store=private_store,
    )
    job_id, _request = _submit_pipeline_request(
        service,
        idempotency_key="foreign-render-checkpoint",
    )
    submitted_state = service.resume(job_id=job_id, user_id="user-1")
    started_job = service.start(
        job_id=job_id,
        user_id="user-1",
        expected_revision=submitted_state.job.revision,
    )
    foreign_checkpoint = valid_pipeline_checkpoint()
    service.checkpoint_stage(
        job_id=job_id,
        user_id="user-1",
        expected_revision=started_job.revision,
        stage=foreign_checkpoint.stage,
        sequence=foreign_checkpoint.sequence,
        result=StageResult.accepted(artifact=foreign_checkpoint),
        artifact_version=foreign_checkpoint.request_hash,
        evidence_version=(
            foreign_checkpoint.evidence_set.evidence_version
            if foreign_checkpoint.evidence_set is not None
            else None
        ),
        budget_snapshot={},
        next_status=JobStatus.rendering,
        required_stage=True,
    )
    executor = _executor(
        service=service,
        preparation_service=_preparation_service(FailIfIngestionRepeats()),
        pipeline_factory=RecordingPipelineFactory(()),
    )

    with pytest.raises(JobExecutionStateError, match="different generation request"):
        executor.execute(
            job_id=job_id,
            user_id="user-1",
            cancellation=CancellationToken(),
        )

    assert private_store.save_count == 0
