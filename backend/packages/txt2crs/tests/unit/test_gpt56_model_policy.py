# SPDX-License-Identifier: MIT-0

"""Tests for exact configured GPT-5.6 discovery and no-fallback policy."""

import pytest
from pydantic import ValidationError

from txt2crs.ai.model_policy import (
    DEFAULT_GPT56_MODEL_ID,
    REVIEWED_GPT56_MODEL_IDS,
    Gpt56ModelPolicy,
    ModelPolicyError,
)


def test_model_policy_defaults_to_the_exact_gpt56_sol_identifier() -> None:
    """The product default must be an exact model reported by app-server."""

    policy = Gpt56ModelPolicy()

    assert DEFAULT_GPT56_MODEL_ID == "gpt-5.6-sol"
    assert policy.configured_model_id == "gpt-5.6-sol"
    assert REVIEWED_GPT56_MODEL_IDS == frozenset(
        {
            "gpt-5.6-sol",
            "gpt-5.6-terra",
            "gpt-5.6-luna",
        }
    )


@pytest.mark.parametrize("model_id", sorted(REVIEWED_GPT56_MODEL_IDS))
def test_model_policy_accepts_only_the_reviewed_gpt56_family(model_id: str) -> None:
    """Every accepted override remains inside the explicit GPT-5.6 family."""

    policy = Gpt56ModelPolicy(configured_model_id=model_id)

    assert policy.configured_model_id == model_id


@pytest.mark.parametrize(
    "model_id",
    [
        "gpt-5.4",
        "gpt-5.5",
        "gpt-5.6",
        "gpt-5.6-preview",
        "GPT-5.6",
        "gpt-5.6-sol-latest",
    ],
)
def test_model_policy_rejects_older_nearby_and_case_changed_slugs(
    model_id: str,
) -> None:
    """A nearby name must not weaken exact reviewed configuration."""

    with pytest.raises(ValidationError):
        Gpt56ModelPolicy(configured_model_id=model_id)


def test_model_policy_requires_exact_configured_discovery_without_fallback() -> None:
    """Discovery proves entitlement but never selects the first returned model."""

    policy = Gpt56ModelPolicy(configured_model_id="gpt-5.6-sol")

    assert (
        policy.require_discovered(
            ("gpt-5.4", "gpt-5.6-terra", "gpt-5.6-sol"),
        )
        == "gpt-5.6-sol"
    )
    with pytest.raises(ModelPolicyError, match="configured GPT-5.6"):
        policy.require_discovered(("gpt-5.4", "gpt-5.6-terra"))


def test_model_policy_rejects_turn_and_result_substitution_safely() -> None:
    """Request and provider result identities must match the configured ID."""

    policy = Gpt56ModelPolicy(configured_model_id="gpt-5.6-sol")

    with pytest.raises(ModelPolicyError, match="configured GPT-5.6"):
        policy.require_turn_model(
            requested_model_id="gpt-5.6-terra",
            discovered_model_ids=("gpt-5.6-sol", "gpt-5.6-terra"),
        )
    with pytest.raises(ModelPolicyError, match="configured GPT-5.6"):
        policy.require_result_model(
            requested_model_id="gpt-5.6-sol",
            result_model_id="gpt-5.4",
        )


def test_model_policy_error_does_not_echo_discovered_provider_values() -> None:
    """Private or malformed discovery values stay out of safe package errors."""

    policy = Gpt56ModelPolicy()
    secret_discovery_value = "private-model-/home/owner/auth.json"

    with pytest.raises(ModelPolicyError) as captured_error:
        policy.require_discovered((secret_discovery_value,))

    assert secret_discovery_value not in str(captured_error.value)
    assert "/home/owner" not in str(captured_error.value)
