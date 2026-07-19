# SPDX-License-Identifier: MIT-0

"""Tests for immutable, canonical, and safely persisted generation requests."""

import json
from collections.abc import Callable
from typing import Any, cast

import pytest
from pydantic import ValidationError

from tests.factories import valid_execution_profile, valid_generation_request
from txt2crs.ingestion.models import InputPayload
from txt2crs.jobs import requests as request_contracts
from txt2crs.jobs.requests import (
    CurriculumShapeLimits,
    ExecutionProfile,
    GenerationRequest,
    LearnerAgeGroup,
    LearningPreferenceDefaults,
    LearningPreferenceIntent,
    RunExecutionLimits,
    deserialize_generation_request,
    serialize_generation_request,
)


def test_request_contracts_reject_unknown_fields_and_mutation() -> None:
    """Persisted request/profile contracts reject drift and in-place changes."""

    request = valid_generation_request()
    unknown_request_data = request.model_dump(mode="python")
    unknown_request_data["unexpected"] = "unsafe"
    unknown_profile_data = request.execution_profile.model_dump(mode="python")
    unknown_profile_data["provider_fallback"] = "gpt-5.4"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        GenerationRequest.model_validate(unknown_request_data)
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ExecutionProfile.model_validate(unknown_profile_data)
    with pytest.raises(ValidationError, match="frozen"):
        request.execution_profile.model_id = "gpt-5.4"


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("audience", "a" * 501),
        ("prior_knowledge", "p" * 2_001),
        ("learning_goals", tuple(f"Goal {index}." for index in range(11))),
        ("learning_goals", ("ab",)),
        ("learning_goals", ("g" * 501,)),
    ],
)
def test_preference_intent_enforces_p0_transport_bounds(
    field_name: str,
    invalid_value: object,
) -> None:
    """Persisted preferences match the authoritative public P0 limits."""

    preference_data = valid_generation_request().preferences.model_dump(mode="python")
    preference_data[field_name] = invalid_value

    with pytest.raises(ValidationError):
        LearningPreferenceIntent.model_validate(preference_data)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("maximum_turns", 0),
        ("maximum_research_calls", -1),
        ("maximum_elapsed_seconds", 0),
    ],
)
def test_execution_profile_requires_finite_positive_run_limits(
    field_name: str,
    invalid_value: int,
) -> None:
    """A persisted profile cannot encode an unlimited or ineffective budget."""

    run_limit_data = valid_execution_profile().run_limits.model_dump(mode="python")
    run_limit_data[field_name] = invalid_value

    with pytest.raises(ValidationError):
        RunExecutionLimits.model_validate(run_limit_data)


def test_execution_profile_rejects_inconsistent_research_and_retry_limits() -> None:
    """Tool-specific calls and retries cannot exceed their aggregate ceilings."""

    profile = valid_execution_profile()
    run_limit_data = profile.run_limits.model_dump(mode="python")
    run_limit_data["maximum_search_calls"] = 8
    run_limit_data["maximum_extract_calls"] = 7

    with pytest.raises(ValidationError, match="search and extract"):
        RunExecutionLimits.model_validate(run_limit_data)

    profile_data = profile.model_dump(mode="python")
    profile_data["run_limits"]["maximum_retries"] = 1
    with pytest.raises(ValidationError, match="retry"):
        ExecutionProfile.model_validate(profile_data)


def test_execution_profile_freezes_documented_p0_defaults_and_shape_limits() -> None:
    """Recovery receives every server-selected preference and curriculum bound."""

    profile = valid_execution_profile()

    assert profile.preference_defaults == LearningPreferenceDefaults(
        desired_depth="Comprehensive, foundational-to-applied",
        duration_minutes=120,
        tone="Clear, rigorous, and encouraging",
        accessibility_requirements=(
            "Semantic headings",
            "Plain-language definitions",
            "Textual explanations of visual concepts",
        ),
        assessment_item_count=15,
        passing_percentage=70,
    )
    assert profile.curriculum_shape_limits == CurriculumShapeLimits(
        minimum_objectives=5,
        maximum_objectives=12,
        minimum_modules=3,
        maximum_modules=6,
        minimum_sections_per_module=2,
        maximum_sections_per_module=5,
        minimum_content_blocks_per_section=3,
        maximum_content_blocks_per_section=12,
    )


@pytest.mark.parametrize(
    ("minimum_field", "maximum_field"),
    [
        ("minimum_objectives", "maximum_objectives"),
        ("minimum_modules", "maximum_modules"),
        ("minimum_sections_per_module", "maximum_sections_per_module"),
        (
            "minimum_content_blocks_per_section",
            "maximum_content_blocks_per_section",
        ),
    ],
)
def test_curriculum_shape_limits_require_ordered_finite_ranges(
    minimum_field: str,
    maximum_field: str,
) -> None:
    """A stored minimum can never exceed the corresponding maximum."""

    shape_data = valid_execution_profile().curriculum_shape_limits.model_dump(
        mode="python"
    )
    shape_data[minimum_field] = shape_data[maximum_field] + 1

    with pytest.raises(ValidationError, match="minimum"):
        CurriculumShapeLimits.model_validate(shape_data)


def test_preference_defaults_and_shape_limits_are_immutable_and_hashed() -> None:
    """Changing any server default or curriculum bound changes request identity."""

    baseline_request = valid_generation_request()
    baseline_profile = baseline_request.execution_profile
    changed_defaults = baseline_profile.preference_defaults.model_copy(
        update={"duration_minutes": 180}
    )
    changed_shape = baseline_profile.curriculum_shape_limits.model_copy(
        update={"maximum_modules": 5}
    )

    default_changed_request = valid_generation_request(
        execution_profile=baseline_profile.model_copy(
            update={"preference_defaults": changed_defaults}
        )
    )
    shape_changed_request = valid_generation_request(
        execution_profile=baseline_profile.model_copy(
            update={"curriculum_shape_limits": changed_shape}
        )
    )

    assert default_changed_request.request_hash != baseline_request.request_hash
    assert shape_changed_request.request_hash != baseline_request.request_hash
    with pytest.raises(ValidationError, match="frozen"):
        baseline_profile.preference_defaults.duration_minutes = 180


@pytest.mark.parametrize("empty_value", ["", b""])
def test_generation_request_rejects_empty_input(empty_value: str | bytes) -> None:
    """A durable accepted request always contains actual source material."""

    with pytest.raises(ValidationError, match="input cannot be empty"):
        valid_generation_request(value=empty_value)


def test_generation_request_enforces_stored_input_byte_limit() -> None:
    """The immutable profile bounds exact input before persistence."""

    with pytest.raises(ValidationError, match="input exceeds"):
        valid_generation_request(
            value=b"01234567890",
            execution_profile=valid_execution_profile(maximum_input_bytes=10),
        )


def test_generation_request_rejects_oversized_input_before_encoding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An obviously oversized upload is rejected before base64 expansion."""

    def fail_if_input_is_encoded(_input_value: str | bytes) -> dict[str, str]:
        pytest.fail("oversized input reached canonical encoding")

    monkeypatch.setattr(
        request_contracts,
        "_encode_input_value",
        fail_if_input_is_encoded,
    )

    with pytest.raises(ValidationError, match="input exceeds"):
        valid_generation_request(
            value=b"01234567890",
            execution_profile=valid_execution_profile(maximum_input_bytes=10),
        )


def test_generation_request_factory_hashes_normalized_values() -> None:
    """The convenience factory hashes the same normalized values it returns."""

    baseline_request = valid_generation_request()
    normalized_request = GenerationRequest.create(
        schema_version="1.0",
        request_version="generation-request-v1",
        input_payload=InputPayload(
            input_type="text",
            value="Teach Python variables with worked examples.",
            media_type=" text/plain ",
            file_name=None,
            metadata={"source": "learner"},
        ),
        preferences=baseline_request.preferences,
        provider_consent=True,
        learner_age_group=LearnerAgeGroup.adult,
        policy_flags=(" allow_external_research ",),
        execution_profile=baseline_request.execution_profile,
    )

    assert normalized_request == baseline_request


def test_generation_request_rejects_unsupported_request_contract_version() -> None:
    """Recovery cannot guess how to interpret an unknown request contract."""

    baseline_request = valid_generation_request()

    with pytest.raises(ValidationError):
        GenerationRequest.create(
            schema_version="1.0",
            request_version=cast(Any, "generation-request-v2"),
            input_payload=baseline_request.input_payload,
            preferences=baseline_request.preferences,
            provider_consent=baseline_request.provider_consent,
            learner_age_group=baseline_request.learner_age_group,
            policy_flags=baseline_request.policy_flags,
            execution_profile=baseline_request.execution_profile,
        )


@pytest.mark.parametrize(
    "unsafe_metadata",
    [
        {"score": float("nan")},
        {"score": float("inf")},
        {"opaque": object()},
        {"tuple_value": ("private learner metadata",)},
    ],
)
def test_generation_request_rejects_metadata_that_cannot_round_trip_exactly(
    unsafe_metadata: dict[str, object],
) -> None:
    """Durable metadata is finite JSON, never silently normalized or coerced."""

    with pytest.raises(
        (ValidationError, ValueError),
        match="metadata must contain only finite JSON values",
    ) as captured_error:
        valid_generation_request(metadata=unsafe_metadata)

    assert "private learner metadata" not in str(captured_error.value)


def test_generation_request_enforces_stored_metadata_byte_limit() -> None:
    """Metadata cannot bypass the execution profile's durable byte ceiling."""

    with pytest.raises(ValidationError, match="metadata exceeds"):
        valid_generation_request(
            metadata={"note": "x" * 100},
            execution_profile=valid_execution_profile(maximum_metadata_bytes=32),
        )


def test_serialization_rejects_nested_mutation_with_a_context_free_error() -> None:
    """Mutable legacy payload fields cannot leak or persist after acceptance."""

    request = valid_generation_request()
    request.input_payload.metadata["opaque"] = object()

    with pytest.raises(
        ValueError,
        match="generation request cannot be serialized",
    ) as captured_error:
        serialize_generation_request(request)

    assert captured_error.value.__cause__ is None
    assert captured_error.value.__context__ is None


def test_canonical_hash_is_stable_across_mapping_insertion_order() -> None:
    """JSON mapping construction order cannot change request identity."""

    first_request = valid_generation_request(
        metadata={"alpha": 1, "nested": {"first": True, "second": False}},
    )
    second_request = valid_generation_request(
        metadata={"nested": {"second": False, "first": True}, "alpha": 1},
    )

    assert first_request.request_hash == second_request.request_hash
    assert serialize_generation_request(first_request) == serialize_generation_request(
        second_request
    )


@pytest.mark.parametrize(
    "changed_request",
    [
        lambda: valid_generation_request(value=b"Teach Python variables."),
        lambda: valid_generation_request(
            preferences=LearningPreferenceIntent(
                audience="Experienced analysts",
                prior_knowledge=None,
                learning_goals=("Apply variables.",),
                level="advanced",
                language="en",
            )
        ),
        lambda: valid_generation_request(provider_consent=False),
        lambda: valid_generation_request(
            learner_age_group=LearnerAgeGroup.minor,
        ),
        lambda: valid_generation_request(
            policy_flags=("allow_external_research", "minor_safe_mode"),
        ),
        lambda: valid_generation_request(
            execution_profile=valid_execution_profile(maximum_input_bytes=1_000_000)
        ),
    ],
)
def test_canonical_hash_changes_for_every_affecting_contract_area(
    changed_request: Callable[[], GenerationRequest],
) -> None:
    """No changed source, preference, policy, or profile can replay paid work."""

    baseline_request = valid_generation_request()

    assert changed_request().request_hash != baseline_request.request_hash


def test_canonical_hash_distinguishes_text_from_same_utf8_bytes() -> None:
    """Input type tags prevent text and binary sources from sharing identity."""

    text_request = valid_generation_request(value="same bytes")
    binary_request = valid_generation_request(value=b"same bytes")

    assert text_request.request_hash != binary_request.request_hash


def test_arbitrary_binary_input_round_trips_exactly() -> None:
    """Non-UTF-8 bytes survive the canonical persisted representation."""

    raw_bytes = b"\x00\x80\xffPK\x03\x04"
    request = valid_generation_request(value=raw_bytes)

    restored_request = deserialize_generation_request(
        serialize_generation_request(request)
    )

    assert restored_request == request
    assert restored_request.input_payload.value == raw_bytes
    assert isinstance(restored_request.input_payload.value, bytes)


def test_deserialization_rejects_tampering_without_echoing_input() -> None:
    """A modified stored body fails safely instead of trusting its old hash."""

    private_input = "private learner source"
    request = valid_generation_request(value=private_input)
    serialized_data = json.loads(serialize_generation_request(request))
    serialized_data["input_payload"]["value"]["data"] = "tampered"
    tampered_json = json.dumps(
        serialized_data,
        sort_keys=True,
        separators=(",", ":"),
    )

    with pytest.raises(ValueError) as captured_error:
        deserialize_generation_request(tampered_json)

    assert "stored generation request is invalid" in str(captured_error.value)
    assert private_input not in str(captured_error.value)
    assert captured_error.value.__context__ is None


def test_policy_flags_must_be_sorted_and_unique() -> None:
    """Set-like server policy flags have one unambiguous canonical order."""

    with pytest.raises(ValidationError, match="sorted and unique"):
        valid_generation_request(
            policy_flags=("minor_safe_mode", "allow_external_research")
        )
    with pytest.raises(ValidationError, match="sorted and unique"):
        valid_generation_request(
            policy_flags=("allow_external_research", "allow_external_research")
        )
