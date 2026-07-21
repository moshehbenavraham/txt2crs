# SPDX-License-Identifier: MIT-0

"""Durable job, stage-result, and checkpoint services."""

from typing import Any

from txt2crs.ingestion.models import InputPayload
from txt2crs.jobs.artifact_queries import (
    ArtifactDeliverable,
    ArtifactFormat,
    ArtifactIntegrityError,
    ArtifactManifest,
    ArtifactMetadata,
)
from txt2crs.jobs.models import JobCheckpoint, JobRecord, JobStatus
from txt2crs.jobs.notifications import (
    DeliveryNotificationMode,
    DeliveryNotificationPolicy,
    DeliveryNotificationState,
    DeliveryNotificationStatus,
)
from txt2crs.jobs.quota import AdmissionReservation
from txt2crs.jobs.requests import (
    CurriculumShapeLimits,
    ExecutionProfile,
    GenerationRequest,
    InputExecutionLimits,
    LearnerAgeGroup,
    LearningPreferenceDefaults,
    LearningPreferenceIntent,
    RequestRetryPolicy,
    RunExecutionLimits,
)
from txt2crs.jobs.stage_result import StageResult, StageStatus
from txt2crs.jobs.store import (
    AdmissionQuotaExceededError,
    ConcurrencyConflictError,
    IdempotencyConflictError,
    InvalidJobListRequestError,
    InvalidJobSubmissionError,
    JobNotFoundError,
    JobRequestCompatibilityError,
    JobStoreError,
)

_PUBLIC_QUERY_EXPORTS = frozenset(
    {
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
    }
)
_PREPARATION_EXPORTS = frozenset(
    {
        "GenerationPreparation",
        "GenerationPreparationService",
        "InputIngestionService",
        "PreparationPolicyError",
    }
)


def __getattr__(name: str) -> Any:
    """Load cross-package contracts only after package initialization."""

    if name in _PUBLIC_QUERY_EXPORTS:
        from txt2crs.jobs import public_queries

        return getattr(public_queries, name)
    if name in _PREPARATION_EXPORTS:
        from txt2crs.jobs import preparation

        return getattr(preparation, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ArtifactDeliverable",
    "ArtifactFormat",
    "ArtifactIntegrityError",
    "ArtifactManifest",
    "ArtifactMetadata",
    "AdmissionReservation",
    "AdmissionQuotaExceededError",
    "ConcurrencyConflictError",
    "CurriculumShapeLimits",
    "DeliveryNotificationMode",
    "DeliveryNotificationPolicy",
    "DeliveryNotificationState",
    "DeliveryNotificationStatus",
    "ExecutionProfile",
    "GenerationPreparation",
    "GenerationPreparationService",
    "GenerationRequest",
    "InputExecutionLimits",
    "InputIngestionService",
    "InputPayload",
    "IdempotencyConflictError",
    "InvalidJobListRequestError",
    "InvalidJobSubmissionError",
    "JobCheckpoint",
    "JobRecord",
    "JobNotFoundError",
    "JobRequestCompatibilityError",
    "JobStoreError",
    "JobStatus",
    "LearnerAgeGroup",
    "LearningPreferenceDefaults",
    "LearningPreferenceIntent",
    "PreparationPolicyError",
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
    "RequestRetryPolicy",
    "RunExecutionLimits",
    "StageResult",
    "StageStatus",
]
