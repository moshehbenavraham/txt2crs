# SPDX-License-Identifier: MIT-0

"""Allowlisted, bounded job state for authorized application callers.

The durable request and checkpoint contain raw learner input, model accounting,
evidence excerpts, and provider-private values. Those objects must never be
serialized and filtered after the fact. This module instead defines small
public contracts that projection code fills one reviewed field at a time.
"""

import base64
import binascii
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal
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
from txt2crs.jobs.models import JobRecord, JobStatus, ResumeState
from txt2crs.jobs.preparation import GenerationPreparation
from txt2crs.jobs.store import InvalidJobListRequestError
from txt2crs.security.redaction import sanitize_public_text

PublicDisplayText = Annotated[str, Field(min_length=1, max_length=500)]
_PUBLIC_PROGRESS_UNIT_LIMIT = 108
_PUBLIC_SOURCE_LIMIT = 12
_PUBLIC_WARNING_LIMIT = 20
_PUBLIC_CONFLICT_LIMIT = 20
_PUBLIC_JOB_PAGE_LIMIT = 50
_PUBLIC_JOB_CURSOR_MAXIMUM_LENGTH = 512
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
    # The plan, not a UI guess, establishes how many module checkpoints exist.
    # Keeping the value null before that point prevents a fabricated percentage.
    total_units: int | None = Field(default=None, ge=0, le=108)

    @model_validator(mode="after")
    def completed_work_cannot_exceed_total(self) -> "PublicJobProgress":
        """Reject internally contradictory progress before it reaches a UI."""

        if self.total_units is not None and self.completed_units > self.total_units:
            raise ValueError("Completed progress cannot exceed total progress.")
        return self


class PublicInputSummary(_PublicQueryContract):
    """Safe display metadata without the request value or normalized text."""

    input_type: InputType
    display_name: Annotated[str, Field(min_length=1, max_length=255)]
    size_bytes: int = Field(ge=0, le=1_000_000_000)
    extraction_warnings: tuple[PublicDisplayText, ...] = Field(
        max_length=_PUBLIC_WARNING_LIMIT
    )
    extraction_warnings_truncated: bool

    @model_validator(mode="after")
    def truncation_requires_a_full_warning_page(self) -> "PublicInputSummary":
        """A truncation flag is credible only after the public page is full."""

        if (
            self.extraction_warnings_truncated
            and len(self.extraction_warnings) != _PUBLIC_WARNING_LIMIT
        ):
            raise ValueError("Truncated warnings must fill the public warning page.")
        return self


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
    revision: int = Field(ge=0, le=9_223_372_036_854_775_807)
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    last_accepted_stage: Identifier | None
    progress: PublicJobProgress
    input: PublicInputSummary
    failure: PublicJobFailure | None
    course_title: PublicDisplayText | None
    resolved_audience: PublicDisplayText | None
    resolved_level: Literal["beginner", "intermediate", "advanced", "mixed"] | None
    resolved_language: Annotated[str, Field(min_length=2, max_length=35)] | None
    objective_count: int | None = Field(default=None, ge=1, le=100)
    module_count: int | None = Field(default=None, ge=1, le=100)
    sources: tuple[PublicSourceSummary, ...] = Field(max_length=_PUBLIC_SOURCE_LIMIT)
    sources_truncated: bool
    conflicts: tuple[PublicDisplayText, ...] = Field(max_length=_PUBLIC_CONFLICT_LIMIT)
    conflicts_truncated: bool
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
        result_leaves = (
            self.course_title,
            self.resolved_audience,
            self.resolved_level,
            self.resolved_language,
            self.objective_count,
            self.module_count,
        )
        has_any_result_leaf = any(value is not None for value in result_leaves)
        has_every_result_leaf = all(value is not None for value in result_leaves)
        if has_any_result_leaf != has_every_result_leaf:
            raise ValueError("Public result fields must appear as one coherent set.")
        if self.status is JobStatus.completed and self.progress.total_units is None:
            raise ValueError("A completed job must have finite total progress.")
        if self.sources_truncated and len(self.sources) != _PUBLIC_SOURCE_LIMIT:
            raise ValueError("Truncated sources must fill the public source page.")
        if self.conflicts_truncated and len(self.conflicts) != _PUBLIC_CONFLICT_LIMIT:
            raise ValueError("Truncated conflicts must fill the public conflict page.")
        return self


class PublicJobSummary(_PublicQueryContract):
    """Small allowlisted library row derived from one full public snapshot."""

    schema_version: SchemaVersion
    job_id: Identifier
    revision: int = Field(ge=0, le=9_223_372_036_854_775_807)
    status: JobStatus
    title: PublicDisplayText
    input_type: InputType
    created_at: datetime
    updated_at: datetime
    progress: PublicJobProgress
    failure: PublicJobFailure | None
    artifacts: PublicArtifactAvailability

    @model_validator(mode="after")
    def validate_summary_coherence(self) -> "PublicJobSummary":
        """Keep timestamps and terminal failure presentation exhaustive."""

        if self.updated_at < self.created_at:
            raise ValueError("Job update time cannot precede creation time.")
        needs_failure = self.status in {JobStatus.failed, JobStatus.cancelled}
        if (self.failure is not None) != needs_failure:
            raise ValueError("Terminal job summaries must include a failure.")
        return self


class PublicJobPage(_PublicQueryContract):
    """One bounded owner library page with an opaque forward continuation."""

    schema_version: SchemaVersion
    items: tuple[PublicJobSummary, ...] = Field(max_length=_PUBLIC_JOB_PAGE_LIMIT)
    next_cursor: (
        Annotated[
            str,
            Field(min_length=1, max_length=_PUBLIC_JOB_CURSOR_MAXIMUM_LENGTH),
        ]
        | None
    ) = None


class _PublicJobCursor(_PublicQueryContract):
    """Validated private cursor payload; callers see only its opaque encoding."""

    version: Literal["1"]
    created_at: datetime
    job_id: Identifier

    @model_validator(mode="after")
    def require_aware_timestamp(self) -> "_PublicJobCursor":
        """Cursor comparisons must never mix local and UTC-naive timestamps."""

        if self.created_at.tzinfo is None:
            raise ValueError("The cursor timestamp must include a timezone.")
        return self


def project_public_job_summary(snapshot: PublicJobSnapshot) -> PublicJobSummary:
    """Reduce one reviewed snapshot to the finite course-library contract."""

    return PublicJobSummary(
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
    )


def encode_public_job_cursor(job: JobRecord) -> str:
    """Encode stable sort leaves without exposing a client-interpreted shape."""

    payload = (
        _PublicJobCursor(
            version="1",
            created_at=job.created_at,
            job_id=job.job_id,
        )
        .model_dump_json()
        .encode("ascii")
    )
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def decode_public_job_cursor(cursor: str | None) -> tuple[datetime, str] | None:
    """Validate one opaque continuation without retaining malformed content."""

    if cursor is None:
        return None
    decoded_cursor: _PublicJobCursor | None = None
    if 1 <= len(cursor) <= _PUBLIC_JOB_CURSOR_MAXIMUM_LENGTH:
        try:
            padded_cursor = cursor + ("=" * (-len(cursor) % 4))
            payload = base64.b64decode(
                padded_cursor,
                altchars=b"-_",
                validate=True,
            )
            decoded_cursor = _PublicJobCursor.model_validate(
                json.loads(payload.decode("ascii"))
            )
        except (
            UnicodeDecodeError,
            binascii.Error,
            json.JSONDecodeError,
            TypeError,
            ValueError,
            ValidationError,
        ):
            pass
    if decoded_cursor is None:
        raise InvalidJobListRequestError("The job-list cursor is invalid.")
    return decoded_cursor.created_at, decoded_cursor.job_id


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
    public_warnings, warnings_truncated = (
        _bounded_public_texts(
            input_document.warnings,
            maximum_items=_PUBLIC_WARNING_LIMIT,
        )
        if input_document is not None
        else ((), False)
    )
    input_type = resume_state.request.input_payload.input_type
    input_value = resume_state.request.input_payload.value
    public_input = PublicInputSummary(
        input_type=input_type,
        display_name=_safe_input_display_name(
            input_type=input_type,
            file_name=resume_state.request.input_payload.file_name,
        ),
        size_bytes=(
            len(input_value)
            if isinstance(input_value, bytes)
            else len(input_value.encode("utf-8"))
        ),
        extraction_warnings=public_warnings,
        extraction_warnings_truncated=warnings_truncated,
    )

    course_title = _public_course_title(pipeline_checkpoint)
    (
        resolved_audience,
        resolved_level,
        resolved_language,
        objective_count,
        module_count,
    ) = _public_result_leaves(pipeline_checkpoint)
    sources, sources_truncated = _public_source_summaries(pipeline_checkpoint)
    conflicts, conflicts_truncated = _public_conflict_summaries(pipeline_checkpoint)
    artifact_count = (
        len(artifact_manifest.artifacts) if artifact_manifest is not None else 0
    )

    return PublicJobSnapshot(
        schema_version="1.0",
        job_id=job.job_id,
        revision=job.revision,
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
        resolved_audience=resolved_audience,
        resolved_level=resolved_level,
        resolved_language=resolved_language,
        objective_count=objective_count,
        module_count=module_count,
        sources=sources,
        sources_truncated=sources_truncated,
        conflicts=conflicts,
        conflicts_truncated=conflicts_truncated,
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
            total_units=None,
        )
    completed_units = min(
        _PUBLIC_PROGRESS_UNIT_LIMIT,
        max(0, validated_checkpoint.sequence),
    )
    pipeline_checkpoint = validated_checkpoint.pipeline_checkpoint
    if pipeline_checkpoint is None:
        return PublicJobProgress(
            completed_units=completed_units,
            total_units=None,
        )
    if pipeline_checkpoint.course_plan is None:
        total_units = None
    else:
        # The cumulative pipeline has eight fixed checkpoints plus one per
        # planned module. This mirrors its sequence function without exposing
        # the course plan itself.
        total_units = min(
            _PUBLIC_PROGRESS_UNIT_LIMIT,
            8 + len(pipeline_checkpoint.course_plan.modules),
        )
        total_units = max(total_units, completed_units)
    if status is JobStatus.completed and total_units is not None:
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


def _public_result_leaves(
    checkpoint: PipelineCheckpoint | None,
) -> tuple[
    str | None,
    Literal["beginner", "intermediate", "advanced", "mixed"] | None,
    str | None,
    int | None,
    int | None,
]:
    """Copy only the resolved plan leaves needed by the public result summary."""

    if (
        checkpoint is None
        or checkpoint.course_plan is None
        or checkpoint.resolved_preferences is None
    ):
        return None, None, None, None, None

    # Learner intent may have used ``auto``. Only the accepted resolved
    # preferences are truthful after the course plan has passed validation.
    resolved_preferences = checkpoint.resolved_preferences
    course_plan = checkpoint.course_plan
    return (
        _bounded_optional_public_text(resolved_preferences.audience),
        resolved_preferences.level,
        resolved_preferences.language,
        len(course_plan.learning_objectives),
        len(course_plan.modules),
    )


def _public_source_summaries(
    checkpoint: PipelineCheckpoint | None,
) -> tuple[tuple[PublicSourceSummary, ...], bool]:
    """Copy bibliographic leaves without evidence excerpts or source hashes."""

    if checkpoint is None:
        return (), False
    if checkpoint.evidence_set is not None:
        source_records = checkpoint.evidence_set.sources
    elif checkpoint.course is not None:
        source_records = checkpoint.course.sources
    else:
        source_records = []
    public_sources = tuple(
        PublicSourceSummary(
            title=(_bounded_optional_public_text(source.title) or "Untitled source"),
            canonical_url=_safe_public_source_url(source.canonical_url),
            publisher=(
                _bounded_optional_public_text(source.publisher_or_author)
                or "Unknown publisher"
            ),
            retrieved_at=source.retrieved_at,
        )
        for source in source_records[:_PUBLIC_SOURCE_LIMIT]
    )
    return public_sources, len(source_records) > _PUBLIC_SOURCE_LIMIT


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
) -> tuple[tuple[str, ...], bool]:
    """Return unique accepted conflict summaries in deterministic order."""

    if checkpoint is None:
        return (), False
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
        if len(public_conflicts) == _PUBLIC_CONFLICT_LIMIT:
            # This is a further valid, unique public value. Invalid, empty, or
            # duplicate private values above do not create false truncation.
            return tuple(public_conflicts), True
        public_conflicts.append(public_conflict)
    return tuple(public_conflicts), False


def _bounded_public_texts(
    values: list[str],
    *,
    maximum_items: int,
) -> tuple[tuple[str, ...], bool]:
    """Sanitize, omit empty strings, and clamp one public display list."""

    public_values: list[str] = []
    for value in values:
        public_value = _bounded_optional_public_text(value)
        if public_value is None:
            continue
        if len(public_values) == maximum_items:
            return tuple(public_values), True
        public_values.append(public_value)
    return tuple(public_values), False


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
    "PublicJobPage",
    "PublicJobProgress",
    "PublicJobProjectionError",
    "PublicJobSnapshot",
    "PublicJobSummary",
    "PublicSourceSummary",
    "decode_public_job_cursor",
    "encode_public_job_cursor",
    "project_public_job_summary",
    "project_public_job_snapshot",
]
