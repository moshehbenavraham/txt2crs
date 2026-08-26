# SPDX-License-Identifier: MIT-0

"""Tests for exact configured-model discovery and no-fallback policy."""

import pytest
from pydantic import ValidationError

from txt2crs.ai.model_policy import (
    DEFAULT_MODEL_ID,
    ExactModelPolicy,
    ModelPolicyError,
)


def test_model_policy_keeps_the_existing_default_identifier() -> None:
    """Existing installations keep their model until an operator changes it."""

    policy = ExactModelPolicy()

    assert DEFAULT_MODEL_ID == "gpt-5.6-sol"
    assert policy.configured_model_id == "gpt-5.6-sol"


@pytest.mark.parametrize(
    "model_id",
    ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-6", "o4-mini"],
)
def test_model_policy_accepts_any_safe_exact_model_identifier(model_id: str) -> None:
    """Post-event configuration is not restricted to the Build Week family."""

    policy = ExactModelPolicy(configured_model_id=model_id)

    assert policy.configured_model_id == model_id


@pytest.mark.parametrize(
    "model_id",
    [
        "",
        "model with spaces",
        "../private-model",
        "/absolute-model",
        "model\nsecret",
        "x" * 129,
    ],
)
def test_model_policy_rejects_unsafe_or_ambiguous_identifiers(model_id: str) -> None:
    """Configuration remains bounded and safe to pass to the provider."""

    with pytest.raises(ValidationError):
        ExactModelPolicy(configured_model_id=model_id)


def test_model_policy_requires_exact_configured_discovery_without_fallback() -> None:
    """Discovery proves entitlement but never selects the first returned model."""

    policy = ExactModelPolicy(configured_model_id="gpt-6")

    assert (
        policy.require_discovered(
            ("gpt-5.6-sol", "o4-mini", "gpt-6"),
        )
        == "gpt-6"
    )
    with pytest.raises(ModelPolicyError, match="configured model"):
        policy.require_discovered(("gpt-5.6-sol", "o4-mini"))


def test_model_policy_rejects_turn_and_result_substitution_safely() -> None:
    """Request and provider result identities must match the configured ID."""

    policy = ExactModelPolicy(configured_model_id="gpt-6")

    with pytest.raises(ModelPolicyError, match="configured model"):
        policy.require_turn_model(
            requested_model_id="o4-mini",
            discovered_model_ids=("gpt-6", "o4-mini"),
        )
    with pytest.raises(ModelPolicyError, match="configured model"):
        policy.require_result_model(
            requested_model_id="gpt-6",
            result_model_id="o4-mini",
        )


def test_model_policy_error_does_not_echo_discovered_provider_values() -> None:
    """Private or malformed discovery values stay out of safe package errors."""

    policy = ExactModelPolicy()
    secret_discovery_value = "private-model-/home/owner/auth.json"

    with pytest.raises(ModelPolicyError) as captured_error:
        policy.require_discovered((secret_discovery_value,))

    assert secret_discovery_value not in str(captured_error.value)
    assert "/home/owner" not in str(captured_error.value)
