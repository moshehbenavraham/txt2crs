# SPDX-License-Identifier: MIT-0

"""Provider-free input preparation persisted before course generation."""

from typing import Protocol, Self

from pydantic import ConfigDict, model_validator

from txt2crs.domain.models import (
    HashValue,
    InputDocument,
    SchemaVersion,
    StrictContract,
)
from txt2crs.generation.preferences import PreparedLearningPreferences
from txt2crs.ingestion.models import InputPayload
from txt2crs.jobs.requests import CurriculumShapeLimits, GenerationRequest
from txt2crs.security.policy import (
    ContentPolicy,
    PolicyDecision,
    PolicyOutcome,
    PolicyStage,
)


class InputIngestionService(Protocol):
    """The one provider-independent operation preparation is allowed to call."""

    def ingest(self, payload: InputPayload) -> InputDocument:
        """Return one bounded normalized input document."""


class PreparationPolicyError(RuntimeError):
    """A safe terminal P0 policy decision raised before provider work."""

    def __init__(self, *, decision: PolicyDecision) -> None:
        self.stage = decision.stage
        self.reason_code = (
            "high_risk_review_required"
            if decision.outcome is PolicyOutcome.human_review
            else decision.reason_code
        )
        super().__init__(decision.public_message)


class GenerationPreparation(StrictContract):
    """Cumulative accepted content and policy state for durable recovery."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    schema_version: SchemaVersion
    request_hash: HashValue
    input_document: InputDocument
    policy_decision: PolicyDecision
    planning_preferences: PreparedLearningPreferences
    curriculum_shape_limits: CurriculumShapeLimits

    @model_validator(mode="after")
    def require_accepted_coherent_preparation(self) -> Self:
        """Reject a checkpoint that does not prove post-ingestion acceptance."""

        if self.policy_decision.stage is not PolicyStage.post_ingestion:
            raise ValueError("preparation requires a post-ingestion policy decision")
        if self.policy_decision.outcome is not PolicyOutcome.allowed:
            raise ValueError("only allowed policy decisions can be prepared")
        if self.policy_decision.high_risk:
            raise ValueError("P0 preparation cannot accept high-risk content")
        if self.planning_preferences.request_hash != self.request_hash:
            raise ValueError("prepared preferences belong to a different request")
        return self

    def require_request_hash(self, request_hash: str) -> None:
        """Bind private recovery state to the exact stored request identity."""

        if self.request_hash != request_hash:
            raise ValueError(
                "The preparation belongs to a different generation request."
            )


class GenerationPreparationService:
    """Run all input and policy work before a provider graph may be created."""

    def __init__(
        self,
        *,
        ingestion_service: InputIngestionService,
        content_policy: ContentPolicy,
    ) -> None:
        self._ingestion_service = ingestion_service
        self._content_policy = content_policy

    def evaluate_preflight(
        self,
        generation_request: GenerationRequest,
    ) -> PolicyDecision:
        """Expose the cheap package gate for future submission admission."""

        return self._content_policy.evaluate_preflight(generation_request)

    def prepare(
        self,
        generation_request: GenerationRequest,
    ) -> GenerationPreparation:
        """Ingest once, apply both policy stages, and freeze accepted state."""

        preflight_decision = self.evaluate_preflight(generation_request)
        _require_allowed_policy(preflight_decision)

        input_document = self._ingestion_service.ingest(
            generation_request.input_payload
        )
        _validate_input_document_against_request(
            generation_request=generation_request,
            input_document=input_document,
        )
        post_ingestion_decision = self._content_policy.evaluate_ingested_content(
            generation_request=generation_request,
            input_document=input_document,
        )
        _require_allowed_policy(post_ingestion_decision)

        planning_preferences = PreparedLearningPreferences.from_request(
            generation_request=generation_request,
            detected_input_language=input_document.language,
            # Any high-risk policy outcome was terminal above. This field is
            # package-derived and can never be supplied by an application.
            high_risk_course=post_ingestion_decision.high_risk,
        )
        return GenerationPreparation(
            schema_version="1.0",
            request_hash=generation_request.request_hash,
            input_document=input_document.model_copy(deep=True),
            policy_decision=post_ingestion_decision,
            planning_preferences=planning_preferences,
            curriculum_shape_limits=(
                generation_request.execution_profile.curriculum_shape_limits
            ),
        )


def _require_allowed_policy(decision: PolicyDecision) -> None:
    """Convert every P0 review/reject decision into one safe terminal error."""

    if decision.outcome is not PolicyOutcome.allowed:
        raise PreparationPolicyError(decision=decision)


def _validate_input_document_against_request(
    *,
    generation_request: GenerationRequest,
    input_document: InputDocument,
) -> None:
    """Distrust adapter output before it becomes durable accepted state."""

    if input_document.input_type != generation_request.input_payload.input_type:
        raise ValueError("Ingestion returned a mismatched input type.")
    maximum_characters = (
        generation_request.execution_profile.input_limits.maximum_normalized_characters
    )
    if len(input_document.normalized_text) > maximum_characters:
        raise ValueError("Ingestion exceeded the stored normalized-content limit.")


__all__ = [
    "GenerationPreparation",
    "GenerationPreparationService",
    "InputIngestionService",
    "PreparationPolicyError",
]
