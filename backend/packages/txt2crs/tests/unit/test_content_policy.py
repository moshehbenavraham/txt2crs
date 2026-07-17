# SPDX-License-Identifier: MIT-0

"""Tests for consent, high-risk review, age, and copyright policy gates."""

from txt2crs.security.policy import (
    ContentPolicy,
    PolicyOutcome,
)


def test_provider_consent_is_required_before_model_processing() -> None:
    """Submitted content cannot be sent to providers without explicit consent."""

    decision = ContentPolicy().evaluate(
        request_text="Teach Python variables.",
        learner_age=18,
        provider_consent=False,
    )

    assert decision.outcome is PolicyOutcome.rejected
    assert decision.reason_code == "provider_consent_required"


def test_medical_legal_financial_and_safety_topics_require_human_review() -> None:
    """High-stakes educational content never auto-delivers as ordinary advice."""

    policy = ContentPolicy()

    for request_text in [
        "Create a course on adjusting insulin dosage.",
        "Teach how to file a criminal appeal.",
        "Build an investment strategy for retirement.",
        "Explain high-voltage electrical repair.",
    ]:
        decision = policy.evaluate(
            request_text=request_text,
            learner_age=25,
            provider_consent=True,
        )
        assert decision.outcome is PolicyOutcome.human_review
        assert decision.high_risk is True


def test_age_inappropriate_and_copyright_reproduction_requests_are_rejected() -> None:
    """The policy rejects clearly unsuitable or full-copy transformations."""

    policy = ContentPolicy()

    age_decision = policy.evaluate(
        request_text="Create explicit sexual content as a lesson.",
        learner_age=12,
        provider_consent=True,
    )
    copyright_decision = policy.evaluate(
        request_text="Reproduce the entire copyrighted textbook verbatim.",
        learner_age=18,
        provider_consent=True,
    )

    assert age_decision.outcome is PolicyOutcome.rejected
    assert age_decision.reason_code == "age_inappropriate"
    assert copyright_decision.outcome is PolicyOutcome.rejected
    assert copyright_decision.reason_code == "copyright_reproduction"


def test_ordinary_education_request_is_allowed() -> None:
    """Low-risk teaching proceeds with an explicit non-high-risk decision."""

    decision = ContentPolicy().evaluate(
        request_text="Teach Python variables to first-year students.",
        learner_age=18,
        provider_consent=True,
    )

    assert decision.outcome is PolicyOutcome.allowed
    assert decision.high_risk is False
