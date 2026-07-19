# SPDX-License-Identifier: MIT-0

"""Durable job, checkpoint, resume, and delivery contracts."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import ConfigDict, Field

from txt2crs.domain.models import HashValue, Identifier, SchemaVersion, StrictContract
from txt2crs.jobs.requests import GenerationRequest
from txt2crs.rendering.artifacts import RenderedArtifact


class JobStatus(StrEnum):
    """Explicit job states visible to the authorized owner."""

    accepted = "accepted"
    researching = "researching"
    drafting = "drafting"
    validating = "validating"
    rendering = "rendering"
    delivering = "delivering"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


_STATUS_ORDER = {
    JobStatus.accepted: 0,
    JobStatus.researching: 1,
    JobStatus.drafting: 2,
    JobStatus.validating: 3,
    JobStatus.rendering: 4,
    JobStatus.delivering: 5,
    JobStatus.completed: 6,
}
_TERMINAL_STATUSES = frozenset(
    {JobStatus.completed, JobStatus.failed, JobStatus.cancelled}
)


def validate_status_transition(
    current_status: JobStatus,
    new_status: JobStatus,
    *,
    allow_same: bool = False,
) -> None:
    """Permit forward progress, failure/cancellation, and no terminal rewrites."""

    if current_status in _TERMINAL_STATUSES:
        raise ValueError(
            f"Invalid job status transition: {current_status} -> {new_status}."
        )
    if new_status in {JobStatus.failed, JobStatus.cancelled}:
        return
    if new_status is JobStatus.completed and current_status is not JobStatus.delivering:
        raise ValueError(
            f"Invalid job status transition: {current_status} -> {new_status}."
        )
    if new_status not in _STATUS_ORDER or current_status not in _STATUS_ORDER:
        raise ValueError(
            f"Invalid job status transition: {current_status} -> {new_status}."
        )
    if allow_same and new_status is current_status:
        return
    if _STATUS_ORDER[new_status] <= _STATUS_ORDER[current_status]:
        raise ValueError(
            f"Invalid job status transition: {current_status} -> {new_status}."
        )


class JobRecord(StrictContract):
    """Current durable state for one tenant-owned generation job."""

    schema_version: SchemaVersion
    job_id: Identifier
    user_id: Identifier
    idempotency_key: Identifier
    request_hash: HashValue
    status: JobStatus
    revision: int = Field(ge=0)
    failure_code: Identifier | None = None
    created_at: datetime
    updated_at: datetime


class JobSubmissionIdentity(StrictContract):
    """Normalized owner and idempotency identifiers validated before writes."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    user_id: Identifier
    idempotency_key: Identifier


class JobCheckpoint(StrictContract):
    """Last accepted stage artifact and exact resume metadata."""

    schema_version: SchemaVersion
    checkpoint_id: Identifier
    job_id: Identifier
    stage: Identifier
    sequence: int = Field(gt=0)
    artifact_version: HashValue
    evidence_version: HashValue | None
    artifact: dict[str, Any]
    budget_snapshot: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ResumeState:
    """Job, exact accepted request, and most recent accepted checkpoint."""

    job: JobRecord
    request: GenerationRequest
    checkpoint: JobCheckpoint | None


@dataclass(frozen=True, slots=True)
class CompletedJobPayload:
    """Validated rendered artifacts and public-safe aggregate accounting."""

    artifacts: dict[str, RenderedArtifact]
    usage_summary: dict[str, Any]
