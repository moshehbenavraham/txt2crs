# SPDX-License-Identifier: MIT-0

"""Tests for versioned consent, age-group, and two-stage content policy."""

import pytest

from tests.factories import valid_generation_request
from txt2crs.domain.models import InputDocument
from txt2crs.jobs.requests import LearnerAgeGroup
from txt2crs.security.policy import (
    ContentPolicy,
    PolicyCompatibilityError,
    PolicyOutcome,
    PolicyStage,
)


def _input_document(normalized_text: str) -> InputDocument:
    """Build one bounded document without involving a provider or adapter."""

    return InputDocument(
        schema_version="1.0",
        document_id="input-policy-test",
        input_type="pdf",
        media_type="application/pdf",
        normalized_text=normalized_text,
        language="en",
        metadata={},
        content_hash=(
            "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        ),
        warnings=[],
        locations=[],
    )


def test_provider_consent_is_rejected_during_preflight() -> None:
    """No ingestion or provider work is needed to reject missing consent."""

    decision = ContentPolicy(policy_version="content-policy-v1").evaluate_preflight(
        valid_generation_request(provider_consent=False)
    )

    assert decision.stage is PolicyStage.preflight
    assert decision.policy_version == "content-policy-v1"
    assert decision.outcome is PolicyOutcome.rejected
    assert decision.reason_code == "provider_consent_required"
    assert decision.high_risk is False


@pytest.mark.parametrize(
    "request_text",
    [
        "Create a course on adjusting insulin dosage.",
        "Teach how to file a criminal appeal.",
        "Build an investment strategy for retirement.",
        "Explain high-voltage electrical repair.",
    ],
)
def test_available_high_risk_request_text_requires_review_at_preflight(
    request_text: str,
) -> None:
    """High-stakes prompt/text requests stop before source preparation."""

    decision = ContentPolicy(policy_version="content-policy-v1").evaluate_preflight(
        valid_generation_request(value=request_text)
    )

    assert decision.stage is PolicyStage.preflight
    assert decision.outcome is PolicyOutcome.human_review
    assert decision.reason_code == "high_risk_domain"
    assert decision.high_risk is True


def test_minor_age_group_and_copyright_reproduction_are_rejected() -> None:
    """The privacy-minimized enum drives age behavior without storing birth age."""

    policy = ContentPolicy(policy_version="content-policy-v1")
    age_decision = policy.evaluate_preflight(
        valid_generation_request(
            value="Create explicit sexual content as a lesson.",
            learner_age_group=LearnerAgeGroup.minor,
        )
    )
    copyright_decision = policy.evaluate_preflight(
        valid_generation_request(
            value="Reproduce the entire copyrighted textbook verbatim."
        )
    )

    assert age_decision.outcome is PolicyOutcome.rejected
    assert age_decision.reason_code == "age_inappropriate"
    assert copyright_decision.outcome is PolicyOutcome.rejected
    assert copyright_decision.reason_code == "copyright_reproduction"


def test_binary_filename_is_not_misclassified_as_document_content() -> None:
    """Only normalized binary contents are authoritative for the second gate."""

    request = valid_generation_request(
        input_payload=valid_generation_request().input_payload.model_copy(
            update={
                "input_type": "pdf",
                "value": b"%PDF-safe",
                "media_type": "application/pdf",
                "file_name": "explicit sexual content.pdf",
            }
        ),
        learner_age_group=LearnerAgeGroup.minor,
    )
    policy = ContentPolicy(policy_version="content-policy-v1")

    preflight = policy.evaluate_preflight(request)
    post_ingestion = policy.evaluate_ingested_content(
        generation_request=request,
        input_document=_input_document("Create explicit sexual content as a lesson."),
    )

    assert preflight.outcome is PolicyOutcome.allowed
    assert post_ingestion.stage is PolicyStage.post_ingestion
    assert post_ingestion.outcome is PolicyOutcome.rejected
    assert post_ingestion.reason_code == "age_inappropriate"


def test_binary_normalized_high_risk_content_requires_review() -> None:
    """Fetched or parsed source bodies cannot bypass the second gate."""

    request = valid_generation_request(
        input_payload=valid_generation_request().input_payload.model_copy(
            update={
                "input_type": "pdf",
                "value": b"%PDF-safe",
                "media_type": "application/pdf",
                "file_name": "course.pdf",
            }
        )
    )

    decision = ContentPolicy(
        policy_version="content-policy-v1"
    ).evaluate_ingested_content(
        generation_request=request,
        input_document=_input_document("A guide to adjusting insulin dosage."),
    )

    assert decision.stage is PolicyStage.post_ingestion
    assert decision.outcome is PolicyOutcome.human_review
    assert decision.high_risk is True


def test_ordinary_education_request_is_allowed_at_both_stages() -> None:
    """Low-risk teaching receives explicit versioned allow decisions."""

    request = valid_generation_request(value="Teach Python variables.")
    policy = ContentPolicy(policy_version="content-policy-v1")

    preflight = policy.evaluate_preflight(request)
    post_ingestion = policy.evaluate_ingested_content(
        generation_request=request,
        input_document=_input_document("Variables bind names to values."),
    )

    assert preflight.outcome is PolicyOutcome.allowed
    assert post_ingestion.outcome is PolicyOutcome.allowed
    assert post_ingestion.reason_code == "allowed"
    assert post_ingestion.policy_version == request.execution_profile.policy_version


def test_policy_version_mismatch_fails_without_echoing_private_content() -> None:
    """Recovery never silently applies a different policy implementation."""

    private_source = "private learner content"
    request = valid_generation_request(value=private_source)

    with pytest.raises(PolicyCompatibilityError) as captured_error:
        ContentPolicy(policy_version="content-policy-v2").evaluate_preflight(request)

    assert str(captured_error.value) == (
        "The stored request requires an incompatible content policy."
    )
    assert private_source not in str(captured_error.value)
    assert captured_error.value.__cause__ is None
