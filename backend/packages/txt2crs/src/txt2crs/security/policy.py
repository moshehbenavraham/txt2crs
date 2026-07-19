# SPDX-License-Identifier: MIT-0

"""Deterministic consent, age, copyright, and high-risk review policy."""

import re
from enum import StrEnum

from pydantic import ConfigDict

from txt2crs.domain.models import Identifier, InputDocument, StrictContract
from txt2crs.jobs.requests import GenerationRequest, LearnerAgeGroup

_HIGH_RISK_PATTERNS = (
    re.compile(
        r"(?i)\b(?:insulin|dosage|diagnos(?:is|e)|medical treatment|prescription)\b"
    ),
    re.compile(r"(?i)\b(?:criminal appeal|legal advice|lawsuit|file .* court)\b"),
    re.compile(r"(?i)\b(?:investment strategy|retirement portfolio|tax advice)\b"),
    re.compile(r"(?i)\b(?:high-voltage|electrical repair|explosive|firearm safety)\b"),
)
_AGE_INAPPROPRIATE_PATTERN = re.compile(
    r"(?i)\b(?:explicit sexual|pornograph|graphic sexual)\b"
)
_COPYRIGHT_REPRODUCTION_PATTERN = re.compile(
    r"(?i)\b(?:reproduce|copy|provide)\b.{0,60}"
    r"\b(?:entire|full|complete)\b.{0,40}"
    r"\b(?:copyrighted|book|textbook|novel|article)\b"
)


class PolicyOutcome(StrEnum):
    """Whether generation may continue automatically."""

    allowed = "allowed"
    human_review = "human_review"
    rejected = "rejected"


class PolicyStage(StrEnum):
    """The request boundary at which a decision was made."""

    preflight = "preflight"
    post_ingestion = "post_ingestion"


class PolicyDecision(StrictContract):
    """Safe policy decision recorded before provider processing."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        frozen=True,
        hide_input_in_errors=True,
    )

    policy_version: Identifier
    stage: PolicyStage
    outcome: PolicyOutcome
    reason_code: Identifier
    high_risk: bool
    public_message: str


class PolicyCompatibilityError(RuntimeError):
    """The worker cannot execute the exact policy stored with a request."""


class ContentPolicy:
    """Apply request and normalized-content gates before provider work."""

    def __init__(self, *, policy_version: str = "content-policy-v1") -> None:
        self._policy_version = policy_version

    def evaluate_preflight(
        self,
        generation_request: GenerationRequest,
    ) -> PolicyDecision:
        """Evaluate consent and any request language available before ingestion."""

        self._require_compatible_policy(generation_request)
        request_payload = generation_request.input_payload
        request_text = (
            request_payload.value[:100_000]
            if request_payload.input_type in {"prompt", "text", "url"}
            and isinstance(request_payload.value, str)
            else ""
        )
        return self._evaluate_text(
            request_text=request_text,
            learner_age_group=generation_request.learner_age_group,
            provider_consent=generation_request.provider_consent,
            stage=PolicyStage.preflight,
        )

    def evaluate_ingested_content(
        self,
        *,
        generation_request: GenerationRequest,
        input_document: InputDocument,
    ) -> PolicyDecision:
        """Evaluate the bounded normalized source after typed ingestion."""

        self._require_compatible_policy(generation_request)
        return self._evaluate_text(
            request_text=input_document.normalized_text,
            learner_age_group=generation_request.learner_age_group,
            provider_consent=generation_request.provider_consent,
            stage=PolicyStage.post_ingestion,
        )

    def _require_compatible_policy(
        self,
        generation_request: GenerationRequest,
    ) -> None:
        """Fail closed instead of applying current policy to stored work."""

        if generation_request.execution_profile.policy_version != self._policy_version:
            raise PolicyCompatibilityError(
                "The stored request requires an incompatible content policy."
            )

    def _evaluate_text(
        self,
        *,
        request_text: str,
        learner_age_group: LearnerAgeGroup,
        provider_consent: bool,
        stage: PolicyStage,
    ) -> PolicyDecision:
        """Return one context-free decision for bounded available text."""

        if not provider_consent:
            return PolicyDecision(
                policy_version=self._policy_version,
                stage=stage,
                outcome=PolicyOutcome.rejected,
                reason_code="provider_consent_required",
                high_risk=False,
                public_message=(
                    "Permission to use the configured providers is required."
                ),
            )
        if (
            learner_age_group is LearnerAgeGroup.minor
            and _AGE_INAPPROPRIATE_PATTERN.search(request_text)
        ):
            return PolicyDecision(
                policy_version=self._policy_version,
                stage=stage,
                outcome=PolicyOutcome.rejected,
                reason_code="age_inappropriate",
                high_risk=False,
                public_message="The requested material is not suitable for this age.",
            )
        if _COPYRIGHT_REPRODUCTION_PATTERN.search(request_text):
            return PolicyDecision(
                policy_version=self._policy_version,
                stage=stage,
                outcome=PolicyOutcome.rejected,
                reason_code="copyright_reproduction",
                high_risk=False,
                public_message=(
                    "The request asks for a full copyrighted-content reproduction."
                ),
            )
        if any(pattern.search(request_text) for pattern in _HIGH_RISK_PATTERNS):
            return PolicyDecision(
                policy_version=self._policy_version,
                stage=stage,
                outcome=PolicyOutcome.human_review,
                reason_code="high_risk_domain",
                high_risk=True,
                public_message=(
                    "High-stakes educational material requires qualified review."
                ),
            )
        return PolicyDecision(
            policy_version=self._policy_version,
            stage=stage,
            outcome=PolicyOutcome.allowed,
            reason_code="allowed",
            high_risk=False,
            public_message="The request may proceed.",
        )


__all__ = [
    "ContentPolicy",
    "PolicyCompatibilityError",
    "PolicyDecision",
    "PolicyOutcome",
    "PolicyStage",
]
