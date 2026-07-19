"""Strict browser-to-shell contracts for durable course-job submission.

These models intentionally contain only learner-selectable values. Owner
identity, provider model, budgets, policy flags, filesystem paths, and
admission reservations are server-owned and therefore cannot appear here.
"""

import json
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictStr,
    field_validator,
    model_validator,
)
from txt2crs.jobs import (
    ArtifactDeliverable,
    ArtifactFormat,
    ArtifactManifest,
    ArtifactMetadata,
    JobStatus,
    PublicFailureCode,
    PublicJobSnapshot,
    PublicSourceSummary,
)

IdempotencyKey = Annotated[
    StrictStr,
    Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9._:-]{1,128}$",
    ),
]
JobIdentifier = Annotated[
    StrictStr,
    Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]
PromptText = Annotated[StrictStr, Field(min_length=3, max_length=10_000)]
PastedText = Annotated[StrictStr, Field(min_length=1, max_length=200_000)]
HttpsUrlText = Annotated[StrictStr, Field(min_length=9, max_length=2_048)]
OptionalAudience = Annotated[StrictStr, Field(min_length=1, max_length=500)] | None
OptionalPriorKnowledge = (
    Annotated[StrictStr, Field(min_length=1, max_length=2_000)] | None
)
LearningGoal = Annotated[StrictStr, Field(min_length=3, max_length=500)]
LanguageIntent = Annotated[StrictStr, Field(min_length=2, max_length=35)]
StatusUrl = Annotated[
    StrictStr,
    Field(
        min_length=14,
        max_length=160,
        pattern=r"^/api/v1/jobs/[A-Za-z0-9][A-Za-z0-9._:-]*$",
    ),
]
ManifestUrl = Annotated[
    StrictStr,
    Field(
        min_length=24,
        max_length=170,
        pattern=(r"^/api/v1/jobs/[A-Za-z0-9][A-Za-z0-9._:-]*/artifacts$"),
    ),
]
PublicText = Annotated[StrictStr, Field(min_length=1, max_length=500)]
PublicInputType = Literal[
    "prompt",
    "text",
    "url",
    "pdf",
    "document",
    "slides",
    "image",
    "audio",
    "video",
]
ResolvedLearningLevel = Literal[
    "beginner",
    "intermediate",
    "advanced",
    "mixed",
]
ArtifactIdentifier = JobIdentifier
DownloadUrl = Annotated[
    StrictStr,
    Field(
        min_length=26,
        max_length=310,
        pattern=(
            r"^/api/v1/jobs/[A-Za-z0-9][A-Za-z0-9._:-]*/artifacts/"
            r"[A-Za-z0-9][A-Za-z0-9._:-]*$"
        ),
    ),
]
ContentHash = Annotated[
    StrictStr,
    Field(
        min_length=71,
        max_length=71,
        pattern=r"^sha256:[0-9a-f]{64}$",
    ),
]


class _StrictFrozenModel(BaseModel):
    """Reject unknown fields, trim strings, and detach immutable values."""

    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )


class PromptJobInput(_StrictFrozenModel):
    """A short topic or course-generation instruction."""

    type: Literal["prompt"]
    value: PromptText


class TextJobInput(_StrictFrozenModel):
    """Finite learner-pasted source text."""

    type: Literal["text"]
    value: PastedText


class _HttpsJobInput(_StrictFrozenModel):
    """Shared shape-only HTTPS validation for package-owned URL handling."""

    value: HttpsUrlText

    @field_validator("value")
    @classmethod
    def require_absolute_public_shape(cls, value: str) -> str:
        """Accept HTTPS syntax without duplicating package host/DNS policy."""

        try:
            parsed_url = urlsplit(value)
            # Reading ``port`` forces malformed bracket/port syntax to fail.
            _parsed_port = parsed_url.port
        except ValueError:
            raise ValueError("URL must be a valid absolute HTTPS URL.") from None
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname is None
            or parsed_url.username is not None
            or parsed_url.password is not None
            or parsed_url.fragment
        ):
            raise ValueError(
                "URL must be absolute HTTPS without credentials or fragments."
            )
        return value


class UrlJobInput(_HttpsJobInput):
    """A public URL whose safety and retrieval remain package-owned."""

    type: Literal["url"]


class YouTubeJobInput(_HttpsJobInput):
    """YouTube intent routed through the package URL adapter."""

    type: Literal["youtube"]


JobInput = Annotated[
    PromptJobInput | TextJobInput | UrlJobInput | YouTubeJobInput,
    Field(discriminator="type"),
]


class JobLearningLevel(StrEnum):
    """Reviewed P0 learner-selectable depth intent."""

    auto = "auto"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    mixed = "mixed"


class JobLearnerAgeGroup(StrEnum):
    """Privacy-minimized age context passed to package policy."""

    minor = "minor"
    adult = "adult"
    not_provided = "not_provided"


class JobPreferences(_StrictFrozenModel):
    """Finite learning intent; all other generation defaults are server-owned."""

    level: JobLearningLevel
    audience: OptionalAudience
    prior_knowledge: OptionalPriorKnowledge
    learning_goals: tuple[LearningGoal, ...] = Field(max_length=10)
    language: LanguageIntent

    @model_validator(mode="after")
    def require_unique_learning_goals(self) -> Self:
        """Reject goals whose text differs only by case or whitespace."""

        normalized_goals = tuple(
            " ".join(learning_goal.casefold().split())
            for learning_goal in self.learning_goals
        )
        if len(normalized_goals) != len(set(normalized_goals)):
            raise ValueError("Learning goals must be unique.")
        return self


class _JobSubmissionMetadata(_StrictFrozenModel):
    """Fields shared by JSON and multipart submissions."""

    preferences: JobPreferences
    consent_to_ai_processing: Literal[True]
    learner_age_group: JobLearnerAgeGroup

    @field_validator("consent_to_ai_processing", mode="before")
    @classmethod
    def require_exact_boolean_true(cls, value: object) -> object:
        """Reject truthy integers or strings instead of coercing consent."""

        if value is not True:
            raise ValueError("Explicit AI processing consent is required.")
        return value


class JobSubmissionRequest(_JobSubmissionMetadata):
    """Strict JSON request with one discriminated source input."""

    input: JobInput


class JobUploadMetadata(_JobSubmissionMetadata):
    """Strict multipart metadata with no file or server-owned fields."""


class JobAcceptedPublic(_StrictFrozenModel):
    """Allowlisted response returned only after a durable package commit."""

    schema_version: Literal["1.0"]
    job_id: JobIdentifier
    status: Literal["accepted"]
    revision: int = Field(ge=0)
    status_url: StatusUrl


class JobProgressStage(StrEnum):
    """Stable browser stages that never reflect a private checkpoint label."""

    queued = "queued"
    researching = "researching"
    drafting = "drafting"
    validating = "validating"
    rendering = "rendering"
    delivering = "delivering"
    ready = "ready"
    failed = "failed"
    cancelled = "cancelled"


_PROGRESS_COPY_BY_STATUS: dict[JobStatus, tuple[JobProgressStage, str]] = {
    JobStatus.accepted: (
        JobProgressStage.queued,
        "Your course is queued securely.",
    ),
    JobStatus.researching: (
        JobProgressStage.researching,
        "Researching the course source.",
    ),
    JobStatus.drafting: (
        JobProgressStage.drafting,
        "Writing the course modules.",
    ),
    JobStatus.validating: (
        JobProgressStage.validating,
        "Checking all course materials.",
    ),
    JobStatus.rendering: (
        JobProgressStage.rendering,
        "Creating publication formats.",
    ),
    JobStatus.delivering: (
        JobProgressStage.delivering,
        "Securing the finished files.",
    ),
    JobStatus.completed: (
        JobProgressStage.ready,
        "Your course materials are ready.",
    ),
    JobStatus.failed: (
        JobProgressStage.failed,
        "Course generation stopped safely.",
    ),
    JobStatus.cancelled: (
        JobProgressStage.cancelled,
        "Course generation was cancelled.",
    ),
}


class JobProgressPublic(_StrictFrozenModel):
    """Monotonic accepted work with fixed browser-safe explanatory copy."""

    stage: JobProgressStage
    message: PublicText
    completed_units: int = Field(ge=0, le=108)
    total_units: int | None = Field(default=None, ge=0, le=108)

    @model_validator(mode="after")
    def completed_work_cannot_exceed_total(self) -> Self:
        """Retain package progress coherence at the HTTP boundary."""

        if self.total_units is not None and self.completed_units > self.total_units:
            raise ValueError("Completed progress cannot exceed total progress.")
        return self


class JobInputPublic(_StrictFrozenModel):
    """Bounded input display metadata without learner-provided source content."""

    type: PublicInputType
    display_name: Annotated[StrictStr, Field(min_length=1, max_length=255)]
    size_bytes: int = Field(ge=0, le=1_000_000_000)
    extraction_warnings: tuple[PublicText, ...] = Field(max_length=20)
    warnings_truncated: bool

    @model_validator(mode="after")
    def truncation_requires_a_full_warning_page(self) -> Self:
        """Prevent a misleading truncation flag on a short warning list."""

        if self.warnings_truncated and len(self.extraction_warnings) != 20:
            raise ValueError("Truncated warnings must fill the public page.")
        return self


class JobFailurePublic(_StrictFrozenModel):
    """Reviewed package failure code and fixed safe learner-facing message."""

    code: PublicFailureCode
    message: PublicText


class JobSourcePublic(_StrictFrozenModel):
    """Display-safe bibliographic metadata with no evidence body."""

    title: PublicText
    url: Annotated[StrictStr, Field(min_length=8, max_length=2_048)] | None
    publisher: PublicText
    retrieved_at: datetime

    @classmethod
    def from_package(cls, source: PublicSourceSummary) -> Self:
        """Copy one already-sanitized package source field by field."""

        return cls(
            title=source.title,
            url=source.canonical_url,
            publisher=source.publisher,
            retrieved_at=source.retrieved_at,
        )


class JobResultPublic(_StrictFrozenModel):
    """Coherent bounded result summary once an accepted course plan exists."""

    title: PublicText
    audience: PublicText
    level: ResolvedLearningLevel
    language: Annotated[StrictStr, Field(min_length=2, max_length=35)]
    objective_count: int = Field(ge=1, le=100)
    module_count: int = Field(ge=1, le=100)
    sources: tuple[JobSourcePublic, ...] = Field(max_length=12)
    sources_truncated: bool
    conflicts: tuple[PublicText, ...] = Field(max_length=20)
    conflicts_truncated: bool

    @model_validator(mode="after")
    def truncation_flags_require_full_public_pages(self) -> Self:
        """Keep list bounds and their explicit truncation indicators coherent."""

        if self.sources_truncated and len(self.sources) != 12:
            raise ValueError("Truncated sources must fill the public page.")
        if self.conflicts_truncated and len(self.conflicts) != 20:
            raise ValueError("Truncated conflicts must fill the public page.")
        return self


class JobArtifactAvailabilityPublic(_StrictFrozenModel):
    """Link to the verified manifest only after package publication."""

    available: bool
    count: int = Field(ge=0, le=16)
    manifest_url: ManifestUrl | None

    @model_validator(mode="after")
    def availability_must_match_count_and_link(self) -> Self:
        """Do not advertise a manifest that package delivery has not published."""

        should_be_available = self.count > 0
        if (
            self.available != should_be_available
            or (self.manifest_url is not None) != should_be_available
        ):
            raise ValueError("Artifact availability, count, and URL must agree.")
        return self


class JobStatusPublic(_StrictFrozenModel):
    """Complete owner-scoped polling response built from one package snapshot."""

    schema_version: Literal["1.0"]
    job_id: JobIdentifier
    status: JobStatus
    revision: int = Field(ge=0, le=9_223_372_036_854_775_807)
    created_at: datetime
    updated_at: datetime
    progress: JobProgressPublic
    input: JobInputPublic
    failure: JobFailurePublic | None
    result: JobResultPublic | None
    artifacts: JobArtifactAvailabilityPublic

    @classmethod
    def from_package(cls, snapshot: PublicJobSnapshot) -> Self:
        """Translate only reviewed package leaves into the HTTP contract."""

        progress_stage, progress_message = _PROGRESS_COPY_BY_STATUS[snapshot.status]
        result = _result_from_package(snapshot)
        manifest_url = (
            f"/api/v1/jobs/{snapshot.job_id}/artifacts"
            if snapshot.artifacts.available
            else None
        )
        return cls(
            schema_version="1.0",
            job_id=snapshot.job_id,
            status=snapshot.status,
            revision=snapshot.revision,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
            progress=JobProgressPublic(
                stage=progress_stage,
                message=progress_message,
                completed_units=snapshot.progress.completed_units,
                total_units=snapshot.progress.total_units,
            ),
            input=JobInputPublic(
                type=snapshot.input.input_type,
                display_name=snapshot.input.display_name,
                size_bytes=snapshot.input.size_bytes,
                extraction_warnings=snapshot.input.extraction_warnings,
                warnings_truncated=(snapshot.input.extraction_warnings_truncated),
            ),
            failure=(
                JobFailurePublic(
                    code=snapshot.failure.code,
                    message=snapshot.failure.message,
                )
                if snapshot.failure is not None
                else None
            ),
            result=result,
            artifacts=JobArtifactAvailabilityPublic(
                available=snapshot.artifacts.available,
                count=snapshot.artifacts.count,
                manifest_url=manifest_url,
            ),
        )


def _result_from_package(snapshot: PublicJobSnapshot) -> JobResultPublic | None:
    """Build one all-or-none result without importing a private checkpoint."""

    if snapshot.course_title is None:
        return None
    if (
        snapshot.resolved_audience is None
        or snapshot.resolved_level is None
        or snapshot.resolved_language is None
        or snapshot.objective_count is None
        or snapshot.module_count is None
    ):
        # The package model normally makes this unreachable. Keeping a
        # context-free guard here prevents a future contract drift from
        # becoming a partial browser result.
        raise ValueError("The public package result is incomplete.")
    return JobResultPublic(
        title=snapshot.course_title,
        audience=snapshot.resolved_audience,
        level=snapshot.resolved_level,
        language=snapshot.resolved_language,
        objective_count=snapshot.objective_count,
        module_count=snapshot.module_count,
        sources=tuple(
            JobSourcePublic.from_package(source) for source in snapshot.sources
        ),
        sources_truncated=snapshot.sources_truncated,
        conflicts=snapshot.conflicts,
        conflicts_truncated=snapshot.conflicts_truncated,
    )


class ArtifactMetadataPublic(_StrictFrozenModel):
    """Path-free metadata and stable download URL for one rendered artifact."""

    artifact_id: ArtifactIdentifier
    format: ArtifactFormat
    file_name: Annotated[StrictStr, Field(min_length=1, max_length=255)]
    media_type: Annotated[StrictStr, Field(min_length=3, max_length=255)]
    size_bytes: int = Field(ge=0, le=1_000_000_000)
    content_hash: ContentHash
    download_url: DownloadUrl

    @field_validator("file_name")
    @classmethod
    def reject_path_or_control_file_names(cls, file_name: str) -> str:
        """Retain a display name without making it a browser header value."""

        if (
            file_name in {".", ".."}
            or "/" in file_name
            or "\\" in file_name
            or _has_control_characters(file_name)
        ):
            raise ValueError("Artifact file name is unsafe.")
        return file_name

    @field_validator("media_type")
    @classmethod
    def reject_invalid_media_types(cls, media_type: str) -> str:
        """Require one bounded non-injectable MIME spelling."""

        if "/" not in media_type or _has_control_characters(media_type):
            raise ValueError("Artifact media type is unsafe.")
        return media_type

    @classmethod
    def from_package(
        cls,
        artifact: ArtifactMetadata,
        *,
        job_id: str,
    ) -> Self:
        """Copy one verified descriptor without a private filesystem path."""

        return cls(
            artifact_id=artifact.artifact_id,
            format=artifact.format,
            file_name=artifact.safe_file_name,
            media_type=artifact.media_type,
            size_bytes=artifact.size_bytes,
            content_hash=artifact.content_hash,
            download_url=(f"/api/v1/jobs/{job_id}/artifacts/{artifact.artifact_id}"),
        )


class ArtifactDeliverableGroupPublic(_StrictFrozenModel):
    """One educational deliverable with at most four canonical formats."""

    deliverable: ArtifactDeliverable
    artifacts: tuple[ArtifactMetadataPublic, ...] = Field(
        min_length=1,
        max_length=4,
    )

    @model_validator(mode="after")
    def require_unique_stable_artifacts(self) -> Self:
        """Reject duplicate IDs/formats and preserve package ID ordering."""

        artifact_ids = [artifact.artifact_id for artifact in self.artifacts]
        artifact_formats = [artifact.format for artifact in self.artifacts]
        if artifact_ids != sorted(artifact_ids):
            raise ValueError("Grouped artifact IDs must use stable order.")
        if len(artifact_ids) != len(set(artifact_ids)):
            raise ValueError("Grouped artifact IDs must be unique.")
        if len(artifact_formats) != len(set(artifact_formats)):
            raise ValueError("Grouped artifact formats must be unique.")
        return self


class ArtifactManifestPublic(_StrictFrozenModel):
    """Verified canonical metadata grouped as four educational products."""

    schema_version: Literal["1.0"]
    job_id: JobIdentifier
    created_at: datetime
    deliverables: tuple[ArtifactDeliverableGroupPublic, ...] = Field(
        min_length=1,
        max_length=4,
    )

    @model_validator(mode="after")
    def require_canonical_deliverable_order(self) -> Self:
        """Keep grouping stable and prevent duplicate product cards."""

        deliverables = [group.deliverable for group in self.deliverables]
        canonical_order = [
            deliverable
            for deliverable in ArtifactDeliverable
            if deliverable in deliverables
        ]
        if deliverables != canonical_order:
            raise ValueError("Deliverables must use canonical order.")
        if len(deliverables) != len(set(deliverables)):
            raise ValueError("Deliverables must be unique.")
        return self

    @classmethod
    def from_package(cls, manifest: ArtifactManifest) -> Self:
        """Group an already-verified path-free package manifest."""

        deliverable_groups: list[ArtifactDeliverableGroupPublic] = []
        for deliverable in ArtifactDeliverable:
            matching_artifacts = tuple(
                ArtifactMetadataPublic.from_package(
                    artifact,
                    job_id=manifest.job_id,
                )
                for artifact in manifest.artifacts
                if artifact.deliverable is deliverable
            )
            if matching_artifacts:
                deliverable_groups.append(
                    ArtifactDeliverableGroupPublic(
                        deliverable=deliverable,
                        artifacts=matching_artifacts,
                    )
                )
        return cls(
            schema_version="1.0",
            job_id=manifest.job_id,
            created_at=manifest.created_at,
            deliverables=tuple(deliverable_groups),
        )


def _has_control_characters(value: str) -> bool:
    """Return whether one header-adjacent value contains control characters."""

    return any(
        ord(character) < 32 or 127 <= ord(character) <= 159 for character in value
    )


def parse_job_upload_metadata(
    metadata_json: str,
    *,
    maximum_metadata_bytes: int = 262_144,
) -> JobUploadMetadata:
    """Parse bounded JSON while rejecting duplicate keys at every object level.

    Python's normal JSON decoder silently keeps the last duplicate key. That
    behavior is unsafe for consent and generation-affecting fields, so this
    parser detects duplicates before Pydantic validates the resulting object.
    """

    try:
        metadata_bytes = metadata_json.encode("utf-8")
    except UnicodeError:
        # Invalid Unicode can arrive from direct Python callers even though a
        # conforming HTTP client cannot encode a lone surrogate as UTF-8.
        raise ValueError("Upload metadata is invalid.") from None

    if maximum_metadata_bytes <= 0 or len(metadata_bytes) > maximum_metadata_bytes:
        raise ValueError("Upload metadata is invalid.")

    def reject_duplicate_keys(
        object_pairs: list[tuple[str, object]],
    ) -> dict[str, object]:
        parsed_object: dict[str, object] = {}
        for key, value in object_pairs:
            if key in parsed_object:
                raise ValueError("duplicate JSON object key")
            parsed_object[key] = value
        return parsed_object

    try:
        parsed_metadata = json.loads(
            metadata_json,
            object_pairs_hook=reject_duplicate_keys,
        )
        if not isinstance(parsed_metadata, dict):
            raise ValueError
        return JobUploadMetadata.model_validate(parsed_metadata)
    except RecursionError, UnicodeError, ValueError:
        # Raise outside the decoder's error text so learner values and keys do
        # not survive in a public exception chain.
        pass
    raise ValueError("Upload metadata is invalid.")


__all__ = [
    "ArtifactDeliverableGroupPublic",
    "ArtifactManifestPublic",
    "ArtifactMetadataPublic",
    "IdempotencyKey",
    "JobAcceptedPublic",
    "JobArtifactAvailabilityPublic",
    "JobFailurePublic",
    "JobInput",
    "JobInputPublic",
    "JobLearnerAgeGroup",
    "JobLearningLevel",
    "JobPreferences",
    "JobProgressPublic",
    "JobProgressStage",
    "JobResultPublic",
    "JobSourcePublic",
    "JobStatusPublic",
    "JobSubmissionRequest",
    "JobUploadMetadata",
    "PromptJobInput",
    "TextJobInput",
    "UrlJobInput",
    "YouTubeJobInput",
    "parse_job_upload_metadata",
]
