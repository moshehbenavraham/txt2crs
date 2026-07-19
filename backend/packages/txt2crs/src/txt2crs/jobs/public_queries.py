# SPDX-License-Identifier: MIT-0

"""Allowlisted, bounded job state for authorized application callers.

The durable request and checkpoint contain raw learner input, model accounting,
evidence excerpts, and provider-private values. Those objects must never be
serialized and filtered after the fact. This module instead defines small
public contracts that projection code fills one reviewed field at a time.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Annotated
from urllib.parse import unquote, urlsplit, urlunsplit

from pydantic import ConfigDict, Field, ValidationError, model_validator

from txt2crs.domain.models import (
    Identifier,
    InputDocument,
    SchemaVersion,
    StrictContract,
)
from txt2crs.generation.pipeline import PipelineCheckpoint
from txt2crs.ingestion.models import InputType
from txt2crs.jobs.artifact_queries import ArtifactManifest
from txt2crs.jobs.models import JobStatus, ResumeState
from txt2crs.jobs.preparation import GenerationPreparation
from txt2crs.security.redaction import sanitize_public_text

PublicDisplayText = Annotated[str, Field(min_length=1, max_length=500)]
_PUBLIC_PROGRESS_UNIT_LIMIT = 108
_PUBLIC_DEFAULT_TOTAL_UNITS = 12
_PATH_SEPARATOR_PATTERN = re.compile(r"[/\\]+")


class _PublicQueryContract(StrictContract):
    """Make every application-facing query result strict and immutable."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )


class PublicJobProjectionError(RuntimeError):
    """Private durable state cannot be represented by the public contract."""


class PublicFailureCode(StrEnum):
    """Reviewed stable failure categories the application may translate."""

    provider_consent_required = "provider_consent_required"
    age_inappropriate = "age_inappropriate"
    copyright_reproduction = "copyright_reproduction"
    high_risk_review_required = "high_risk_review_required"
    stage_not_accepted = "stage_not_accepted"
    generation_failed = "generation_failed"
    cancelled = "cancelled"


_PUBLIC_FAILURES = {
    PublicFailureCode.provider_consent_required: (
        "Permission to use the configured providers is required."
    ),
    PublicFailureCode.age_inappropriate: (
        "This course request is not available for the selected age group."
    ),
    PublicFailureCode.copyright_reproduction: (
        "The request cannot reproduce protected material."
    ),
    PublicFailureCode.high_risk_review_required: (
        "This course requires qualified review before generation."
    ),
    PublicFailureCode.stage_not_accepted: (
        "A required course stage could not be accepted."
    ),
    PublicFailureCode.generation_failed: ("Course generation could not be completed."),
    PublicFailureCode.cancelled: "Course generation was cancelled.",
}


class PublicJobProgress(_PublicQueryContract):
    """Bounded accepted work units for a durable generation job."""

    completed_units: int = Field(ge=0, le=108)
    total_units: int = Field(ge=0, le=108)

    @model_validator(mode="after")
    def completed_work_cannot_exceed_total(self) -> "PublicJobProgress":
        """Reject internally contradictory progress before it reaches a UI."""

        if self.completed_units > self.total_units:
            raise ValueError("Completed progress cannot exceed total progress.")
        return self


class PublicInputSummary(_PublicQueryContract):
    """Safe display metadata without the request value or normalized text."""

    input_type: InputType
    display_name: Annotated[str, Field(min_length=1, max_length=255)]
    extraction_warnings: tuple[PublicDisplayText, ...] = Field(max_length=20)


class PublicSourceSummary(_PublicQueryContract):
    """Display-safe bibliographic metadata without source or evidence bodies."""

    title: PublicDisplayText
    canonical_url: Annotated[str, Field(min_length=8, max_length=2_048)] | None
    publisher: PublicDisplayText
    retrieved_at: datetime


class PublicJobFailure(_PublicQueryContract):
    """Stable public failure code and reviewed learner-facing message."""

    code: PublicFailureCode
    message: PublicDisplayText


class PublicArtifactAvailability(_PublicQueryContract):
    """Whether a verified private manifest is published for this job."""

    available: bool
    count: int = Field(ge=0, le=16)

    @model_validator(mode="after")
    def availability_must_match_count(self) -> "PublicArtifactAvailability":
        """Keep the boolean and count from contradicting each other."""

        if self.available != (self.count > 0):
            raise ValueError("Artifact availability must match its count.")
        return self


class PublicJobSnapshot(_PublicQueryContract):
    """Complete allowlisted state for one owner-authorized generation job."""

    schema_version: SchemaVersion
    job_id: Identifier
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    last_accepted_stage: Identifier | None
    progress: PublicJobProgress
    input: PublicInputSummary
    failure: PublicJobFailure | None
    course_title: PublicDisplayText | None
    sources: tuple[PublicSourceSummary, ...] = Field(max_length=100)
    conflicts: tuple[PublicDisplayText, ...] = Field(max_length=20)
    artifacts: PublicArtifactAvailability

    @model_validator(mode="after")
    def validate_public_state_coherence(self) -> "PublicJobSnapshot":
        """Reject impossible timestamps and terminal failure combinations."""

        if self.updated_at < self.created_at:
            raise ValueError("Job update time cannot precede creation time.")
        has_public_failure = self.failure is not None
        needs_public_failure = self.status in {
            JobStatus.failed,
            JobStatus.cancelled,
        }
        if has_public_failure != needs_public_failure:
            raise ValueError("Terminal failure state must match a public failure.")
        return self


@dataclass(frozen=True, slots=True)
class _ValidatedCheckpointProjection:
    """Private checkpoint leaves needed to build the public allowlist.

    Preparation and pipeline artifacts contain substantially more private
    state. Keeping that full object behind this tiny internal projection makes
    it difficult for a future response field to expose the artifact by
    accident.
    """

    stage: str
    sequence: int
    input_document: InputDocument
    pipeline_checkpoint: PipelineCheckpoint | None


def project_public_job_snapshot(
    *,
    resume_state: ResumeState,
    artifact_manifest: ArtifactManifest | None,
) -> PublicJobSnapshot:
    """Copy one coherent private resume state into a bounded public allowlist.

    The helper catches validation failures only long enough to leave the
    exception handler. Raising the package error afterward keeps raw nested
    checkpoint values out of both ``__cause__`` and ``__context__``.
    """

    public_snapshot: PublicJobSnapshot | None = None
    try:
        public_snapshot = _build_public_job_snapshot(
            resume_state=resume_state,
            artifact_manifest=artifact_manifest,
        )
    except (TypeError, ValueError, ValidationError):
        pass
    if public_snapshot is None:
        raise PublicJobProjectionError(
            "The durable state cannot produce a public job snapshot."
        )
    return public_snapshot


def _build_public_job_snapshot(
    *,
    resume_state: ResumeState,
    artifact_manifest: ArtifactManifest | None,
) -> PublicJobSnapshot:
    """Build the public object while private contracts remain package-local."""

    job = resume_state.job
    if job.request_hash != resume_state.request.request_hash:
        raise ValueError("Job and request identities do not agree.")
    if artifact_manifest is not None and artifact_manifest.job_id != job.job_id:
        raise ValueError("Artifact manifest belongs to another job.")

    validated_checkpoint = _validated_checkpoint_projection(resume_state)
    pipeline_checkpoint = (
        validated_checkpoint.pipeline_checkpoint
        if validated_checkpoint is not None
        else None
    )
    input_document = (
        validated_checkpoint.input_document
        if validated_checkpoint is not None
        else None
    )
    public_warnings = (
        _bounded_public_texts(input_document.warnings, maximum_items=20)
        if input_document is not None
        else ()
    )
    input_type = resume_state.request.input_payload.input_type
    public_input = PublicInputSummary(
        input_type=input_type,
        display_name=_safe_input_display_name(
            input_type=input_type,
            file_name=resume_state.request.input_payload.file_name,
        ),
        extraction_warnings=public_warnings,
    )

    course_title = _public_course_title(pipeline_checkpoint)
    sources = _public_source_summaries(pipeline_checkpoint)
    conflicts = _public_conflict_summaries(pipeline_checkpoint)
    artifact_count = (
        len(artifact_manifest.artifacts) if artifact_manifest is not None else 0
    )

    return PublicJobSnapshot(
        schema_version="1.0",
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        last_accepted_stage=(
            validated_checkpoint.stage if validated_checkpoint is not None else None
        ),
        progress=_public_progress(
            status=job.status,
            validated_checkpoint=validated_checkpoint,
        ),
        input=public_input,
        failure=_public_failure(status=job.status, private_code=job.failure_code),
        course_title=course_title,
        sources=sources,
        conflicts=conflicts,
        artifacts=PublicArtifactAvailability(
            available=artifact_count > 0,
            count=artifact_count,
        ),
    )


def _validated_checkpoint_projection(
    resume_state: ResumeState,
) -> _ValidatedCheckpointProjection | None:
    """Parse the stage-discriminated private checkpoint and copy safe leaves."""

    durable_checkpoint = resume_state.checkpoint
    if durable_checkpoint is None:
        return None
    if durable_checkpoint.job_id != resume_state.job.job_id:
        raise ValueError("Checkpoint belongs to another job.")

    if durable_checkpoint.stage == "prepare_input":
        if durable_checkpoint.sequence != 1:
            raise ValueError("Preparation checkpoint has an invalid sequence.")
        preparation = GenerationPreparation.model_validate(durable_checkpoint.artifact)
        preparation.require_request_hash(resume_state.request.request_hash)
        return _ValidatedCheckpointProjection(
            stage=durable_checkpoint.stage,
            sequence=durable_checkpoint.sequence,
            input_document=preparation.input_document,
            pipeline_checkpoint=None,
        )

    pipeline_checkpoint = PipelineCheckpoint.model_validate(durable_checkpoint.artifact)
    if (
        durable_checkpoint.stage != pipeline_checkpoint.stage
        or durable_checkpoint.sequence != pipeline_checkpoint.sequence
    ):
        raise ValueError("Checkpoint row and artifact do not agree.")
    pipeline_checkpoint.preparation.require_request_hash(
        resume_state.request.request_hash
    )
    return _ValidatedCheckpointProjection(
        stage=pipeline_checkpoint.stage,
        sequence=pipeline_checkpoint.sequence,
        input_document=pipeline_checkpoint.input_document,
        pipeline_checkpoint=pipeline_checkpoint,
    )


def _safe_input_display_name(
    *,
    input_type: InputType,
    file_name: str | None,
) -> str:
    """Return a basename or fixed label without copying raw input content."""

    if file_name:
        basename = _PATH_SEPARATOR_PATTERN.split(file_name)[-1]
        sanitized_basename = sanitize_public_text(
            basename,
            maximum_length=255,
        )
        if sanitized_basename and sanitized_basename not in {".", ".."}:
            return sanitized_basename
    labels: dict[InputType, str] = {
        "prompt": "Text prompt",
        "text": "Pasted text",
        "url": "Web source",
        "pdf": "PDF document",
        "document": "Document",
        "slides": "Presentation",
        "image": "Image",
        "audio": "Audio recording",
        "video": "Video recording",
    }
    return labels[input_type]


def _public_progress(
    *,
    status: JobStatus,
    validated_checkpoint: _ValidatedCheckpointProjection | None,
) -> PublicJobProgress:
    """Derive coherent units from accepted checkpoint sequence and course plan."""

    if validated_checkpoint is None:
        return PublicJobProgress(
            completed_units=0,
            total_units=_PUBLIC_DEFAULT_TOTAL_UNITS,
        )
    completed_units = min(
        _PUBLIC_PROGRESS_UNIT_LIMIT,
        max(0, validated_checkpoint.sequence),
    )
    pipeline_checkpoint = validated_checkpoint.pipeline_checkpoint
    if pipeline_checkpoint is None:
        return PublicJobProgress(
            completed_units=completed_units,
            total_units=max(_PUBLIC_DEFAULT_TOTAL_UNITS, completed_units),
        )
    if pipeline_checkpoint.course_plan is None:
        total_units = max(_PUBLIC_DEFAULT_TOTAL_UNITS, completed_units)
    else:
        # The cumulative pipeline has eight fixed checkpoints plus one per
        # planned module. This mirrors its sequence function without exposing
        # the course plan itself.
        total_units = min(
            _PUBLIC_PROGRESS_UNIT_LIMIT,
            8 + len(pipeline_checkpoint.course_plan.modules),
        )
        total_units = max(total_units, completed_units)
    if status is JobStatus.completed:
        completed_units = total_units
    return PublicJobProgress(
        completed_units=completed_units,
        total_units=total_units,
    )


def _public_failure(
    *,
    status: JobStatus,
    private_code: str | None,
) -> PublicJobFailure | None:
    """Map only reviewed durable codes; collapse every unknown provider value."""

    if status not in {JobStatus.failed, JobStatus.cancelled}:
        return None
    if status is JobStatus.cancelled:
        public_code = PublicFailureCode.cancelled
    else:
        try:
            candidate_code = PublicFailureCode(
                private_code or PublicFailureCode.generation_failed
            )
        except ValueError:
            candidate_code = PublicFailureCode.generation_failed
        if candidate_code is PublicFailureCode.cancelled:
            # Cancellation is authoritative only when the durable status says
            # the owner actually cancelled. A private failure string must not
            # contradict the public terminal state.
            candidate_code = PublicFailureCode.generation_failed
        public_code = candidate_code
    return PublicJobFailure(
        code=public_code,
        message=_PUBLIC_FAILURES[public_code],
    )


def _public_course_title(
    checkpoint: PipelineCheckpoint | None,
) -> str | None:
    """Prefer the approved course title, then the accepted course-plan title."""

    if checkpoint is None:
        return None
    private_title: str | None = None
    if checkpoint.course is not None:
        private_title = checkpoint.course.title
    elif checkpoint.course_plan is not None:
        private_title = checkpoint.course_plan.title
    return _bounded_optional_public_text(private_title)


def _public_source_summaries(
    checkpoint: PipelineCheckpoint | None,
) -> tuple[PublicSourceSummary, ...]:
    """Copy bibliographic leaves without evidence excerpts or source hashes."""

    if checkpoint is None:
        return ()
    if checkpoint.evidence_set is not None:
        source_records = checkpoint.evidence_set.sources
    elif checkpoint.course is not None:
        source_records = checkpoint.course.sources
    else:
        source_records = []
    return tuple(
        PublicSourceSummary(
            title=(_bounded_optional_public_text(source.title) or "Untitled source"),
            canonical_url=_safe_public_source_url(source.canonical_url),
            publisher=(
                _bounded_optional_public_text(source.publisher_or_author)
                or "Unknown publisher"
            ),
            retrieved_at=source.retrieved_at,
        )
        for source in source_records[:100]
    )


def _safe_public_source_url(url: str) -> str | None:
    """Drop credentials, queries, and fragments from a displayable HTTP URL."""

    try:
        parsed_url = urlsplit(url)
        port = parsed_url.port
    except ValueError:
        return None
    if (
        parsed_url.scheme.casefold() not in {"http", "https"}
        or parsed_url.hostname is None
        or parsed_url.username is not None
        or parsed_url.password is not None
    ):
        return None
    decoded_path = unquote(parsed_url.path or "/")
    if any(
        character.isspace() or ord(character) < 32 or ord(character) == 127
        for character in decoded_path
    ):
        return None
    # Query strings are omitted entirely, but secrets may also be embedded in
    # a path segment. Reuse the public-text redactor as a detector and omit the
    # whole link rather than publishing a modified or misleading destination.
    if sanitize_public_text(decoded_path, maximum_length=2_048) != decoded_path:
        return None
    hostname = parsed_url.hostname.casefold()
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    netloc = hostname if port is None else f"{hostname}:{port}"
    return urlunsplit(
        (
            parsed_url.scheme.casefold(),
            netloc,
            parsed_url.path or "/",
            "",
            "",
        )
    )


def _public_conflict_summaries(
    checkpoint: PipelineCheckpoint | None,
) -> tuple[str, ...]:
    """Return unique accepted conflict summaries in deterministic order."""

    if checkpoint is None:
        return ()
    private_conflicts: list[str] = []
    for module_draft in checkpoint.course_module_drafts:
        private_conflicts.extend(module_draft.unresolved_or_conflicting_claims)
    if checkpoint.course is not None:
        private_conflicts.extend(checkpoint.course.unresolved_or_conflicting_claims)

    public_conflicts: list[str] = []
    normalized_conflicts: set[str] = set()
    for private_conflict in private_conflicts:
        public_conflict = _bounded_optional_public_text(private_conflict)
        if public_conflict is None:
            continue
        normalized_conflict = " ".join(public_conflict.casefold().split())
        if normalized_conflict in normalized_conflicts:
            continue
        normalized_conflicts.add(normalized_conflict)
        public_conflicts.append(public_conflict)
        if len(public_conflicts) == 20:
            break
    return tuple(public_conflicts)


def _bounded_public_texts(
    values: list[str],
    *,
    maximum_items: int,
) -> tuple[str, ...]:
    """Sanitize, omit empty strings, and clamp one public display list."""

    public_values: list[str] = []
    for value in values:
        public_value = _bounded_optional_public_text(value)
        if public_value is not None:
            public_values.append(public_value)
        if len(public_values) == maximum_items:
            break
    return tuple(public_values)


def _bounded_optional_public_text(value: str | None) -> str | None:
    """Return one non-empty redacted display value with a 500-character cap."""

    if value is None:
        return None
    public_value = sanitize_public_text(value, maximum_length=500)
    return public_value or None


__all__ = [
    "PublicArtifactAvailability",
    "PublicFailureCode",
    "PublicInputSummary",
    "PublicJobFailure",
    "PublicJobProgress",
    "PublicJobProjectionError",
    "PublicJobSnapshot",
    "PublicSourceSummary",
    "project_public_job_snapshot",
]
