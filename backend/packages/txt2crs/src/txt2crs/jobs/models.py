# SPDX-License-Identifier: MIT-0

"""Durable job, checkpoint, resume, and delivery contracts."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from txt2crs.domain.models import HashValue, Identifier, SchemaVersion, StrictContract
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


class JobRecord(StrictContract):
    """Current durable state for one tenant-owned generation job."""

    schema_version: SchemaVersion
    job_id: Identifier
    user_id: Identifier
    idempotency_key: Identifier
    input_hash: HashValue
    status: JobStatus
    revision: int = Field(ge=0)
    failure_code: Identifier | None = None
    created_at: datetime
    updated_at: datetime


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
    """Job plus its most recent accepted checkpoint, if any."""

    job: JobRecord
    checkpoint: JobCheckpoint | None


@dataclass(frozen=True, slots=True)
class CompletedJobPayload:
    """Validated rendered artifacts and public-safe aggregate accounting."""

    artifacts: dict[str, RenderedArtifact]
    usage_summary: dict[str, Any]
