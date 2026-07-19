# SPDX-License-Identifier: MIT-0

"""Durable application runner joining generation, checkpoints, and delivery."""

import json
from collections.abc import Callable
from dataclasses import asdict
from hashlib import sha256
from typing import Protocol

from txt2crs.ai.runtime import CancellationToken
from txt2crs.ai.usage import aggregate_usage
from txt2crs.domain.validation import validate_artifact_bundle
from txt2crs.generation.pipeline import PipelineCheckpoint, PipelineResult
from txt2crs.generation.quality import validate_assessment_quality
from txt2crs.jobs.models import (
    CompletedJobPayload,
    JobCheckpoint,
    JobRecord,
    JobStatus,
)
from txt2crs.jobs.preparation import (
    GenerationPreparation,
    GenerationPreparationService,
    PreparationPolicyError,
)
from txt2crs.jobs.requests import GenerationRequest
from txt2crs.jobs.service import JobService
from txt2crs.jobs.stage_result import StageResult
from txt2crs.rendering.artifacts import ArtifactRenderer


class DurablePipeline(Protocol):
    """The complete generation operation consumed by the job worker."""

    def generate(
        self,
        *,
        preparation: GenerationPreparation,
        cancellation: CancellationToken,
        resume_checkpoint: PipelineCheckpoint | None = None,
        checkpoint_sink: Callable[[PipelineCheckpoint], None] | None = None,
    ) -> PipelineResult:
        """Generate and locally validate all canonical artifacts."""


class DurablePipelineFactory(Protocol):
    """Construct provider-backed generation only after preparation is durable."""

    def create(self, generation_request: GenerationRequest) -> DurablePipeline:
        """Build a pipeline from the exact request accepted by the job store."""


class JobExecutionStateError(RuntimeError):
    """A durable job cannot be executed from its current state."""


class PolicyViolationError(RuntimeError):
    """Provider consent or content policy prevented generation."""


class GenerationJobExecutor:
    """Complete or resume one owner-scoped generation job."""

    def __init__(
        self,
        *,
        job_service: JobService,
        preparation_service: GenerationPreparationService,
        pipeline_factory: DurablePipelineFactory,
        renderer: ArtifactRenderer,
    ) -> None:
        self._job_service = job_service
        self._preparation_service = preparation_service
        self._pipeline_factory = pipeline_factory
        self._renderer = renderer

    def execute(
        self,
        *,
        job_id: str,
        user_id: str,
        cancellation: CancellationToken,
    ) -> JobRecord:
        """Load the accepted request, resume generation, and deliver privately."""

        resume_state = self._job_service.resume(job_id=job_id, user_id=user_id)
        current_job = resume_state.job
        if current_job.status is JobStatus.completed:
            return current_job
        if current_job.status in {JobStatus.failed, JobStatus.cancelled}:
            raise JobExecutionStateError(
                f"Job is already terminal with status {current_job.status.value}."
            )
        generation_request = resume_state.request
        if generation_request.request_hash != current_job.request_hash:
            raise JobExecutionStateError(
                "The durable job and generation request identities do not match."
            )

        if current_job.status is JobStatus.accepted:
            current_job = self._job_service.start(
                job_id=job_id,
                user_id=user_id,
                expected_revision=current_job.revision,
            )

        if current_job.status in {
            JobStatus.researching,
            JobStatus.drafting,
            JobStatus.validating,
        }:
            (
                preparation,
                pipeline_resume_checkpoint,
                current_job,
            ) = self._load_or_prepare_generation(
                job_id=job_id,
                user_id=user_id,
                current_job=current_job,
                generation_request=generation_request,
                checkpoint=resume_state.checkpoint,
                cancellation=cancellation,
            )

            def persist_checkpoint(checkpoint: PipelineCheckpoint) -> None:
                """Atomically advance the durable row after each accepted stage."""

                nonlocal current_job
                next_status_by_stage = {
                    "plan_research": JobStatus.researching,
                    "collect_evidence": JobStatus.drafting,
                    "design_course": JobStatus.drafting,
                    "verify_course": JobStatus.validating,
                    "generate_review_pack": JobStatus.validating,
                    "design_assessment": JobStatus.validating,
                    "cross_validate_artifacts": JobStatus.rendering,
                }
                next_status = next_status_by_stage.get(checkpoint.stage)
                if checkpoint.stage.startswith("write_module:"):
                    next_status = JobStatus.drafting
                if next_status is None:
                    raise JobExecutionStateError(
                        f"Unknown pipeline checkpoint stage {checkpoint.stage!r}."
                    )
                checkpoint_version = _hash_json(checkpoint.model_dump(mode="json"))
                current_job = self._job_service.checkpoint_stage(
                    job_id=job_id,
                    user_id=user_id,
                    expected_revision=current_job.revision,
                    stage=checkpoint.stage,
                    sequence=checkpoint.sequence,
                    result=StageResult.accepted(artifact=checkpoint),
                    artifact_version=checkpoint_version,
                    evidence_version=(
                        checkpoint.evidence_set.evidence_version
                        if checkpoint.evidence_set is not None
                        else None
                    ),
                    budget_snapshot=asdict(checkpoint.budget_snapshot),
                    next_status=next_status,
                    required_stage=True,
                )

            try:
                # The factory is deliberately called after ``prepare_input``
                # has committed. A worker replacement at this exact boundary
                # can reuse normalized input without reading the source again.
                pipeline = self._pipeline_factory.create(generation_request)
                pipeline_result = pipeline.generate(
                    preparation=preparation,
                    cancellation=cancellation,
                    resume_checkpoint=pipeline_resume_checkpoint,
                    checkpoint_sink=persist_checkpoint,
                )
                # ``persist_checkpoint`` reassigns ``current_job`` while the
                # pipeline runs, so this check intentionally reads the live
                # row before accepting the returned artifact set.
                if current_job.status is not JobStatus.rendering:
                    raise JobExecutionStateError(
                        "Pipeline returned without a final accepted checkpoint."
                    )
                rendered_artifacts = pipeline_result.rendered_artifacts
                usage_summary = aggregate_usage(
                    pipeline_result.usage_records
                ).model_dump(mode="json")
            except Exception:
                self._settle_generation_failure(
                    current_job=current_job,
                    cancellation=cancellation,
                )
                raise
        elif current_job.status in {JobStatus.rendering, JobStatus.delivering}:
            if resume_state.checkpoint is None:
                raise JobExecutionStateError(
                    "Rendering or delivery requires a validated bundle checkpoint."
                )
            checkpoint_artifact = self._validated_pipeline_checkpoint(
                checkpoint=resume_state.checkpoint,
                generation_request=generation_request,
            )
            if (
                checkpoint_artifact.stage != "cross_validate_artifacts"
                or checkpoint_artifact.course is None
                or checkpoint_artifact.review_pack is None
                or checkpoint_artifact.assessment is None
                or checkpoint_artifact.answer_key is None
            ):
                raise JobExecutionStateError(
                    "Rendering requires the final cross-validated checkpoint."
                )
            bundle = validate_artifact_bundle(
                course=checkpoint_artifact.course,
                review_pack=checkpoint_artifact.review_pack,
                assessment=checkpoint_artifact.assessment,
                answer_key=checkpoint_artifact.answer_key,
            )
            validate_assessment_quality(
                course=bundle.course,
                assessment=bundle.assessment,
                answer_key=bundle.answer_key,
            )
            cancellation.raise_if_cancelled()
            rendered_artifacts = self._renderer.render_bundle(bundle)
            usage_summary = aggregate_usage(
                checkpoint_artifact.usage_records
            ).model_dump(mode="json")
        else:
            raise JobExecutionStateError(
                f"Job cannot execute from status {current_job.status.value}."
            )

        cancellation.raise_if_cancelled()
        return self._job_service.complete(
            job_id=job_id,
            user_id=user_id,
            expected_revision=current_job.revision,
            payload=CompletedJobPayload(
                artifacts=rendered_artifacts,
                usage_summary=usage_summary,
            ),
        )

    def _load_or_prepare_generation(
        self,
        *,
        job_id: str,
        user_id: str,
        current_job: JobRecord,
        generation_request: GenerationRequest,
        checkpoint: JobCheckpoint | None,
        cancellation: CancellationToken,
    ) -> tuple[GenerationPreparation, PipelineCheckpoint | None, JobRecord]:
        """Reuse accepted preparation or persist it before provider startup."""

        if checkpoint is None:
            try:
                cancellation.raise_if_cancelled()
                preparation = self._preparation_service.prepare(generation_request)
            except PreparationPolicyError as policy_error:
                self._job_service.fail(
                    job_id=job_id,
                    user_id=user_id,
                    expected_revision=current_job.revision,
                    failure_code=policy_error.reason_code,
                )
                raise PolicyViolationError(str(policy_error)) from None
            except Exception:
                self._settle_generation_failure(
                    current_job=current_job,
                    cancellation=cancellation,
                )
                raise

            preparation.require_request_hash(generation_request.request_hash)
            current_job = self._job_service.checkpoint_stage(
                job_id=job_id,
                user_id=user_id,
                expected_revision=current_job.revision,
                stage="prepare_input",
                sequence=1,
                result=StageResult.accepted(artifact=preparation),
                artifact_version=_hash_json(preparation.model_dump(mode="json")),
                evidence_version=None,
                budget_snapshot={},
                next_status=JobStatus.researching,
                required_stage=True,
            )
            return preparation, None, current_job

        if checkpoint.stage == "prepare_input":
            if checkpoint.sequence != 1:
                raise JobExecutionStateError(
                    "The preparation checkpoint has an invalid sequence."
                )
            preparation = GenerationPreparation.model_validate(checkpoint.artifact)
            try:
                preparation.require_request_hash(generation_request.request_hash)
            except ValueError as request_error:
                raise JobExecutionStateError(str(request_error)) from request_error
            return preparation, None, current_job

        pipeline_checkpoint = self._validated_pipeline_checkpoint(
            checkpoint=checkpoint,
            generation_request=generation_request,
        )
        return pipeline_checkpoint.preparation, pipeline_checkpoint, current_job

    def _validated_pipeline_checkpoint(
        self,
        *,
        checkpoint: JobCheckpoint,
        generation_request: GenerationRequest,
    ) -> PipelineCheckpoint:
        """Bind a cumulative artifact to its row and exact accepted request."""

        pipeline_checkpoint = PipelineCheckpoint.model_validate(checkpoint.artifact)
        if (
            checkpoint.stage != pipeline_checkpoint.stage
            or checkpoint.sequence != pipeline_checkpoint.sequence
        ):
            raise JobExecutionStateError(
                "The checkpoint row and pipeline artifact do not agree."
            )
        if pipeline_checkpoint.request_hash != generation_request.request_hash:
            raise JobExecutionStateError(
                "The pipeline checkpoint belongs to a different generation request."
            )
        return pipeline_checkpoint

    def _settle_generation_failure(
        self,
        *,
        current_job: JobRecord,
        cancellation: CancellationToken,
    ) -> None:
        """Expose cancellation separately from all other generation failures."""

        if cancellation.is_cancelled:
            self._job_service.cancel(
                job_id=current_job.job_id,
                user_id=current_job.user_id,
                expected_revision=current_job.revision,
            )
        else:
            self._job_service.fail(
                job_id=current_job.job_id,
                user_id=current_job.user_id,
                expected_revision=current_job.revision,
                failure_code="generation_failed",
            )


def _hash_json(value: object) -> str:
    """Hash one canonical JSON-compatible checkpoint payload."""

    canonical_json = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{sha256(canonical_json.encode('utf-8')).hexdigest()}"
