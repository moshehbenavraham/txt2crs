# SPDX-License-Identifier: MIT-0

"""Provider-free generation preparation and cumulative checkpoint behavior."""

import pytest
from pydantic import ValidationError

from tests.factories import valid_generation_request
from txt2crs.domain.models import InputDocument
from txt2crs.ingestion.models import InputPayload
from txt2crs.jobs.preparation import (
    GenerationPreparationService,
    PreparationPolicyError,
)
from txt2crs.jobs.requests import LearnerAgeGroup, LearningPreferenceIntent
from txt2crs.security.policy import ContentPolicy, PolicyOutcome


class RecordingIngestionService:
    """Return a fixed document and count exact input preparation attempts."""

    def __init__(self, *, normalized_text: str, language: str = "en") -> None:
        self._normalized_text = normalized_text
        self._language = language
        self.payloads: list[InputPayload] = []

    def ingest(self, payload: InputPayload) -> InputDocument:
        """Record one bounded input adapter call."""

        self.payloads.append(payload)
        return InputDocument(
            schema_version="1.0",
            document_id="input-prepared",
            input_type=payload.input_type,
            media_type=payload.media_type,
            normalized_text=self._normalized_text,
            language=self._language,
            metadata={},
            content_hash=(
                "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            ),
            warnings=[],
            locations=[],
        )


def _preparation_service(
    ingestion_service: RecordingIngestionService,
) -> GenerationPreparationService:
    """Build the deterministic provider-free preparation graph."""

    return GenerationPreparationService(
        ingestion_service=ingestion_service,
        content_policy=ContentPolicy(policy_version="content-policy-v1"),
    )


def test_missing_consent_stops_before_ingestion() -> None:
    """Cheap preflight cannot consume input transport work on a known denial."""

    ingestion_service = RecordingIngestionService(normalized_text="Safe content.")
    generation_request = valid_generation_request(provider_consent=False)

    with pytest.raises(PreparationPolicyError) as captured_error:
        _preparation_service(ingestion_service).prepare(generation_request)

    assert captured_error.value.reason_code == "provider_consent_required"
    assert ingestion_service.payloads == []


def test_post_ingestion_policy_denial_occurs_after_exactly_one_ingestion() -> None:
    """A binary source body is checked once and cannot reach generation."""

    ingestion_service = RecordingIngestionService(
        normalized_text="A guide to adjusting insulin dosage."
    )
    generation_request = valid_generation_request(
        input_payload=InputPayload(
            input_type="pdf",
            value=b"%PDF-safe",
            media_type="application/pdf",
            file_name="course.pdf",
            metadata={},
        )
    )

    with pytest.raises(PreparationPolicyError) as captured_error:
        _preparation_service(ingestion_service).prepare(generation_request)

    assert captured_error.value.reason_code == "high_risk_review_required"
    assert len(ingestion_service.payloads) == 1
    assert captured_error.value.__cause__ is None
    assert "insulin" not in str(captured_error.value).casefold()


def test_allowed_preparation_freezes_document_policy_and_planning_preferences() -> None:
    """The accepted preparation contains all state needed before providers start."""

    ingestion_service = RecordingIngestionService(
        normalized_text="Mishtanim shomrim arakhim.",
        language="he",
    )
    generation_request = valid_generation_request(
        preferences=LearningPreferenceIntent(
            audience=None,
            prior_knowledge=None,
            learning_goals=(),
            level="auto",
            language="auto",
        ),
        learner_age_group=LearnerAgeGroup.not_provided,
    )

    preparation = _preparation_service(ingestion_service).prepare(generation_request)

    assert preparation.request_hash == generation_request.request_hash
    assert preparation.input_document.normalized_text == "Mishtanim shomrim arakhim."
    assert preparation.policy_decision.outcome is PolicyOutcome.allowed
    assert preparation.policy_decision.reason_code == "allowed"
    assert preparation.planning_preferences.language == "he"
    assert preparation.planning_preferences.level == "auto"
    assert preparation.planning_preferences.duration_minutes == 120
    assert len(ingestion_service.payloads) == 1
    with pytest.raises(ValidationError, match="frozen"):
        preparation.planning_preferences.duration_minutes = 90


def test_explicit_language_is_frozen_even_when_input_detection_differs() -> None:
    """Explicit language remains the course output contract, not a detection hint."""

    ingestion_service = RecordingIngestionService(
        normalized_text="English source text.",
        language="en",
    )
    generation_request = valid_generation_request(
        preferences=LearningPreferenceIntent(
            audience=None,
            prior_knowledge=None,
            learning_goals=(),
            level="auto",
            language="he",
        )
    )

    preparation = _preparation_service(ingestion_service).prepare(generation_request)

    assert preparation.input_document.language == "en"
    assert preparation.planning_preferences.language == "he"


def test_preparation_rejects_unknown_fields_and_request_hash_tampering() -> None:
    """Stored preparation is strict and bound to the accepted request identity."""

    request = valid_generation_request()
    preparation = _preparation_service(
        RecordingIngestionService(normalized_text="Safe educational material.")
    ).prepare(request)
    stored_data = preparation.model_dump(mode="python")
    stored_data["unexpected"] = "unsafe"

    with pytest.raises(ValidationError, match="Extra inputs"):
        type(preparation).model_validate(stored_data)
    with pytest.raises(ValueError, match="different generation request"):
        preparation.require_request_hash(
            "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"
        )


def test_preparation_rejects_mismatched_adapter_input_type() -> None:
    """A buggy ingestion boundary cannot relabel the accepted source type."""

    class MismatchedInputTypeIngestionService(RecordingIngestionService):
        """Return a structurally valid document for the wrong input type."""

        def ingest(self, payload: InputPayload) -> InputDocument:
            input_document = super().ingest(payload)
            return input_document.model_copy(update={"input_type": "pdf"})

    generation_request = valid_generation_request()

    with pytest.raises(ValueError, match="mismatched input type"):
        _preparation_service(
            MismatchedInputTypeIngestionService(
                normalized_text="Safe educational material."
            )
        ).prepare(generation_request)


def test_preparation_rejects_adapter_output_above_stored_character_limit() -> None:
    """The accepted request limit remains authoritative after ingestion."""

    baseline_request = valid_generation_request()
    constrained_input_limits = (
        baseline_request.execution_profile.input_limits.model_copy(
            update={"maximum_normalized_characters": 10}
        )
    )
    constrained_profile = baseline_request.execution_profile.model_copy(
        update={"input_limits": constrained_input_limits}
    )
    generation_request = valid_generation_request(execution_profile=constrained_profile)

    with pytest.raises(ValueError, match="normalized-content limit"):
        _preparation_service(
            RecordingIngestionService(normalized_text="Eleven chars")
        ).prepare(generation_request)
