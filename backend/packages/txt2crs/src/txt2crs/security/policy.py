# SPDX-License-Identifier: MIT-0

"""Deterministic consent, age, copyright, and high-risk review policy."""

import re
from enum import StrEnum

from txt2crs.domain.models import StrictContract

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


class PolicyDecision(StrictContract):
    """Safe policy decision recorded before provider processing."""

    outcome: PolicyOutcome
    reason_code: str
    high_risk: bool
    public_message: str


class ContentPolicy:
    """Apply narrow deterministic gates before AI or research spend."""

    def evaluate(
        self,
        *,
        request_text: str,
        learner_age: int | None,
        provider_consent: bool,
    ) -> PolicyDecision:
        """Return one explicit allow, review, or reject decision."""

        if not provider_consent:
            return PolicyDecision(
                outcome=PolicyOutcome.rejected,
                reason_code="provider_consent_required",
                high_risk=False,
                public_message=(
                    "Consent is required before content is sent to AI providers."
                ),
            )
        if (
            learner_age is not None
            and learner_age < 18
            and _AGE_INAPPROPRIATE_PATTERN.search(request_text)
        ):
            return PolicyDecision(
                outcome=PolicyOutcome.rejected,
                reason_code="age_inappropriate",
                high_risk=False,
                public_message="The requested material is not suitable for this age.",
            )
        if _COPYRIGHT_REPRODUCTION_PATTERN.search(request_text):
            return PolicyDecision(
                outcome=PolicyOutcome.rejected,
                reason_code="copyright_reproduction",
                high_risk=False,
                public_message=(
                    "The request asks for a full copyrighted-content reproduction."
                ),
            )
        if any(pattern.search(request_text) for pattern in _HIGH_RISK_PATTERNS):
            return PolicyDecision(
                outcome=PolicyOutcome.human_review,
                reason_code="high_risk_domain",
                high_risk=True,
                public_message=(
                    "High-stakes educational material requires qualified review."
                ),
            )
        return PolicyDecision(
            outcome=PolicyOutcome.allowed,
            reason_code="allowed",
            high_risk=False,
            public_message="The request may proceed.",
        )
