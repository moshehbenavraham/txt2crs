# SPDX-License-Identifier: MIT-0

"""Durable application runner joining generation, checkpoints, and delivery."""

import json
from collections.abc import Callable
from dataclasses import asdict
from hashlib import sha256
from typing import Protocol, cast

from txt2crs.ai.runtime import CancellationToken
from txt2crs.ai.usage import aggregate_usage
from txt2crs.domain.validation import validate_artifact_bundle
from txt2crs.generation.models import LearningPreferences
from txt2crs.generation.pipeline import PipelineCheckpoint, PipelineResult
from txt2crs.generation.quality import validate_assessment_quality
from txt2crs.ingestion.models import InputPayload
from txt2crs.jobs.models import CompletedJobPayload, JobRecord, JobStatus
from txt2crs.jobs.service import JobService
from txt2crs.jobs.stage_result import StageResult
from txt2crs.rendering.artifacts import ArtifactRenderer
from txt2crs.security.policy import ContentPolicy, PolicyOutcome


class DurablePipeline(Protocol):
    """The complete generation operation consumed by the job worker."""

    def generate(
        self,
        *,
        payload: InputPayload,
        preferences: LearningPreferences,
        cancellation: CancellationToken,
        resume_checkpoint: PipelineCheckpoint | None = None,
        checkpoint_sink: Callable[[PipelineCheckpoint], None] | None = None,
    ) -> PipelineResult:
        """Generate and locally validate all canonical artifacts."""


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
        pipeline: DurablePipeline,
        renderer: ArtifactRenderer,
        content_policy: ContentPolicy,
    ) -> None:
        self._job_service = job_service
        self._pipeline = pipeline
        self._renderer = renderer
        self._content_policy = content_policy

    def execute(
        self,
        *,
        job_id: str,
        user_id: str,
        payload: InputPayload,
        preferences: LearningPreferences,
        cancellation: CancellationToken,
        provider_consent: bool,
        learner_age: int | None,
        high_risk_review_approved: bool = False,
    ) -> JobRecord:
        """Generate or resume accepted stages and deliver idempotently."""

        resume_state = self._job_service.resume(job_id=job_id, user_id=user_id)
        current_job = resume_state.job
        if current_job.status is JobStatus.completed:
            return current_job
        if current_job.status in {JobStatus.failed, JobStatus.cancelled}:
            raise JobExecutionStateError(
                f"Job is already terminal with status {current_job.status.value}."
            )

        policy_decision = self._content_policy.evaluate(
            request_text=_policy_text(payload),
            learner_age=learner_age,
            provider_consent=provider_consent,
        )
        high_risk_review_required = (
            policy_decision.outcome is PolicyOutcome.human_review
            or preferences.high_risk_course
        )
        if policy_decision.outcome is PolicyOutcome.rejected:
            self._job_service.fail(
                job_id=job_id,
                user_id=user_id,
                expected_revision=current_job.revision,
                failure_code=policy_decision.reason_code,
            )
            raise PolicyViolationError(policy_decision.public_message)
        if high_risk_review_required and not high_risk_review_approved:
            self._job_service.fail(
                job_id=job_id,
                user_id=user_id,
                expected_revision=current_job.revision,
                failure_code="high_risk_review_required",
            )
            raise PolicyViolationError(
                "High-stakes educational material requires qualified review."
            )
        if high_risk_review_required and not preferences.high_risk_course:
            # A deterministic topic match cannot be weakened by a client that
            # incorrectly labels the course as ordinary.
            preferences = preferences.model_copy(update={"high_risk_course": True})

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
            pipeline_resume_checkpoint = (
                PipelineCheckpoint.model_validate(resume_state.checkpoint.artifact)
                if resume_state.checkpoint is not None
                else None
            )

            def persist_checkpoint(checkpoint: PipelineCheckpoint) -> None:
                """Atomically advance the durable row after each accepted stage."""

                nonlocal current_job
                next_status_by_stage = {
                    "ingest_input": JobStatus.researching,
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
                checkpoint_version = _hash_json(
                    checkpoint.model_dump(mode="json")
                )
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
                pipeline_result = self._pipeline.generate(
                    payload=payload,
                    preferences=preferences,
                    cancellation=cancellation,
                    resume_checkpoint=pipeline_resume_checkpoint,
                    checkpoint_sink=persist_checkpoint,
                )
            except Exception:
                self._settle_generation_failure(
                    current_job=current_job,
                    cancellation=cancellation,
                )
                raise
            # ``persist_checkpoint`` reassigns ``current_job`` (nonlocal)
            # while ``generate`` runs, so the status narrowing from the
            # branch guard above no longer holds; cast back to the full
            # enum so this re-check compares against the live value.
            status_after_generation = cast(JobStatus, current_job.status)
            if status_after_generation is not JobStatus.rendering:
                raise JobExecutionStateError(
                    "Pipeline returned without a final accepted checkpoint."
                )
            rendered_artifacts = pipeline_result.rendered_artifacts
            usage_summary = aggregate_usage(
                pipeline_result.usage_records
            ).model_dump(mode="json")
        elif current_job.status in {JobStatus.rendering, JobStatus.delivering}:
            if resume_state.checkpoint is None:
                raise JobExecutionStateError(
                    "Rendering or delivery requires a validated bundle checkpoint."
                )
            checkpoint_artifact = PipelineCheckpoint.model_validate(
                resume_state.checkpoint.artifact
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


def _policy_text(payload: InputPayload) -> str:
    """Extract bounded pre-provider text without attempting remote ingestion."""

    if isinstance(payload.value, str):
        return payload.value[:100_000]
    return payload.file_name or "Uploaded binary educational material"
