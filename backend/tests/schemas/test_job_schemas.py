"""Tests for the strict public job-submission transport contracts."""

from typing import cast

import pytest
from pydantic import TypeAdapter, ValidationError

from app.schemas.jobs import (
    IdempotencyKey,
    JobAcceptedPublic,
    JobSubmissionRequest,
    JobUploadMetadata,
    PromptJobInput,
    TextJobInput,
    UrlJobInput,
    YouTubeJobInput,
    parse_job_upload_metadata,
)


def _preferences() -> dict[str, object]:
    """Return one complete valid learner-preference object."""

    return {
        "level": "auto",
        "audience": None,
        "prior_knowledge": None,
        "learning_goals": [],
        "language": "auto",
    }


def _submission(input_value: dict[str, object]) -> dict[str, object]:
    """Return a valid submission around the supplied discriminated input."""

    return {
        "input": input_value,
        "preferences": _preferences(),
        "consent_to_ai_processing": True,
        "learner_age_group": "adult",
    }


@pytest.mark.parametrize(
    ("input_value", "expected_type"),
    [
        ({"type": "prompt", "value": "Teach database indexes."}, PromptJobInput),
        ({"type": "text", "value": "A"}, TextJobInput),
        ({"type": "url", "value": "https://example.com/course"}, UrlJobInput),
        (
            {"type": "youtube", "value": "https://video.example/watch?v=1"},
            YouTubeJobInput,
        ),
    ],
)
def test_submission_parses_each_reviewed_discriminated_input(
    input_value: dict[str, object],
    expected_type: type[object],
) -> None:
    request = JobSubmissionRequest.model_validate(_submission(input_value))

    assert isinstance(request.input, expected_type)
    assert request.preferences.language == "auto"


@pytest.mark.parametrize(
    "payload",
    [
        _submission({"type": "image", "value": "private"}),
        _submission({"type": "prompt", "value": "ab"}),
        _submission({"type": "prompt", "value": "x" * 10_001}),
        _submission({"type": "text", "value": "   "}),
        _submission({"type": "text", "value": "x" * 200_001}),
        _submission({"type": "url", "value": "http://example.com"}),
        _submission({"type": "url", "value": "/relative"}),
        _submission({"type": "url", "value": f"https://example.com/{'x' * 2_040}"}),
        _submission(
            {"type": "youtube", "value": "https://user:pass@example.com/watch"}
        ),
        _submission({"type": "youtube", "value": "https://example.com/#private"}),
    ],
)
def test_submission_rejects_unreviewed_or_out_of_bounds_input(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        JobSubmissionRequest.model_validate(payload)


@pytest.mark.parametrize(
    "payload",
    [
        {**_submission({"type": "prompt", "value": "Valid topic"}), "owner": "x"},
        _submission(
            {"type": "prompt", "value": "Valid topic", "private_path": "/tmp/x"}
        ),
        {
            **_submission({"type": "prompt", "value": "Valid topic"}),
            "preferences": {**_preferences(), "model_id": "gpt-private"},
        },
    ],
)
def test_submission_rejects_unknown_fields_at_every_level(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError, match="extra"):
        JobSubmissionRequest.model_validate(payload)


@pytest.mark.parametrize(
    "preference_changes",
    [
        {"level": "expert"},
        {"audience": ""},
        {"audience": "x" * 501},
        {"prior_knowledge": ""},
        {"prior_knowledge": "x" * 2_001},
        {"learning_goals": ["ab"]},
        {"learning_goals": ["x" * 501]},
        {"learning_goals": [f"Goal {index}" for index in range(11)]},
        {"learning_goals": ["Learn joins", "  learn   JOINS "]},
        {"language": ""},
        {"language": "x" * 36},
    ],
)
def test_submission_rejects_invalid_preferences(
    preference_changes: dict[str, object],
) -> None:
    payload = _submission({"type": "prompt", "value": "Valid topic"})
    payload["preferences"] = {**_preferences(), **preference_changes}

    with pytest.raises(ValidationError):
        JobSubmissionRequest.model_validate(payload)


def test_submission_strips_human_text_and_keeps_unique_goals() -> None:
    payload = _submission({"type": "prompt", "value": "  Teach indexes.  "})
    payload["preferences"] = {
        **_preferences(),
        "audience": "  first-year students  ",
        "prior_knowledge": "  basic SQL  ",
        "learning_goals": ["  Explain B-trees  ", "Compare index scans"],
    }

    request = JobSubmissionRequest.model_validate(payload)

    assert request.input.value == "Teach indexes."
    assert request.preferences.audience == "first-year students"
    assert request.preferences.prior_knowledge == "basic SQL"
    assert request.preferences.learning_goals == (
        "Explain B-trees",
        "Compare index scans",
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("consent_to_ai_processing", False),
        ("consent_to_ai_processing", 1),
        ("learner_age_group", "child"),
        ("learner_age_group", None),
    ],
)
def test_submission_requires_literal_consent_and_reviewed_age_group(
    field_name: str,
    invalid_value: object,
) -> None:
    payload = _submission({"type": "prompt", "value": "Valid topic"})
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        JobSubmissionRequest.model_validate(payload)


@pytest.mark.parametrize("age_group", ["minor", "adult", "not_provided"])
def test_submission_accepts_every_reviewed_age_group(age_group: str) -> None:
    payload = _submission({"type": "prompt", "value": "Valid topic"})
    payload["learner_age_group"] = age_group

    assert JobSubmissionRequest.model_validate(payload).learner_age_group == age_group


def test_upload_metadata_has_no_input_or_transport_override_fields() -> None:
    valid_metadata = {
        "preferences": _preferences(),
        "consent_to_ai_processing": True,
        "learner_age_group": "not_provided",
    }

    metadata = JobUploadMetadata.model_validate(valid_metadata)
    assert metadata.preferences.level == "auto"

    for forbidden_field in ("input", "file_path", "owner", "model_id", "budget"):
        with pytest.raises(ValidationError, match="extra"):
            JobUploadMetadata.model_validate(
                {**valid_metadata, forbidden_field: "private"}
            )


def test_upload_metadata_parser_rejects_invalid_json_and_duplicate_keys() -> None:
    for metadata_json in (
        "not-json",
        "[]",
        "\ud800",
        (
            '{"preferences":{"level":"auto","audience":null,'
            '"prior_knowledge":null,"learning_goals":[],"language":"auto"},'
            '"consent_to_ai_processing":true,"learner_age_group":"adult",'
            '"learner_age_group":"minor"}'
        ),
    ):
        with pytest.raises(ValueError, match="metadata is invalid"):
            parse_job_upload_metadata(metadata_json)


@pytest.mark.parametrize(
    "idempotency_key",
    [
        "request-01",
        "browser.retry_2",
        "owner:course:20260719",
        "a" * 128,
    ],
)
def test_idempotency_key_accepts_only_the_reviewed_pattern(
    idempotency_key: str,
) -> None:
    adapter = TypeAdapter(IdempotencyKey)

    assert adapter.validate_python(idempotency_key) == idempotency_key


@pytest.mark.parametrize(
    "idempotency_key",
    [
        "",
        " ",
        "contains space",
        "contains/slash",
        "contains@email",
        "a" * 129,
        7,
    ],
)
def test_idempotency_key_rejects_invalid_or_coerced_values(
    idempotency_key: object,
) -> None:
    adapter = TypeAdapter(IdempotencyKey)

    with pytest.raises(ValidationError):
        adapter.validate_python(idempotency_key)


def test_accepted_response_is_frozen_bounded_and_allowlisted() -> None:
    response = JobAcceptedPublic(
        schema_version="1.0",
        job_id="job-123",
        status="accepted",
        revision=0,
        status_url="/api/v1/jobs/job-123",
    )

    assert response.model_dump() == {
        "schema_version": "1.0",
        "job_id": "job-123",
        "status": "accepted",
        "revision": 0,
        "status_url": "/api/v1/jobs/job-123",
    }
    with pytest.raises(ValidationError):
        JobAcceptedPublic.model_validate(
            {**response.model_dump(), "idempotency_key": "private"}
        )
    with pytest.raises(ValidationError):
        JobAcceptedPublic(
            schema_version="1.0",
            job_id="job-123",
            status="accepted",
            revision=cast(int, -1),
            status_url="/api/v1/jobs/job-123",
        )
