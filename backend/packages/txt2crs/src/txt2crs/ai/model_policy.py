# SPDX-License-Identifier: MIT-0

"""Exact GPT-5.6 configuration and discovery policy.

Codex model discovery is an entitlement check, not a model-selection
algorithm. Keeping that distinction here prevents an account-specific list
order from silently changing the model used for a learner's course.
"""

from collections.abc import Collection

from pydantic import BaseModel, ConfigDict, field_validator

DEFAULT_GPT56_MODEL_ID = "gpt-5.6"
REVIEWED_GPT56_MODEL_IDS = frozenset(
    {
        "gpt-5.6",
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "gpt-5.6-luna",
    }
)


class ModelPolicyError(RuntimeError):
    """The configured model failed an exact local or discovery check."""


class Gpt56ModelPolicy(BaseModel):
    """Immutable reviewed GPT-5.6 selection used by every subscription turn."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
        str_strip_whitespace=True,
    )

    configured_model_id: str = DEFAULT_GPT56_MODEL_ID

    @field_validator("configured_model_id")
    @classmethod
    def require_reviewed_model_id(cls, configured_model_id: str) -> str:
        """Reject any slug outside the exact locally reviewed family."""

        if configured_model_id not in REVIEWED_GPT56_MODEL_IDS:
            raise ValueError("Model must belong to the reviewed GPT-5.6 family.")
        return configured_model_id

    def require_discovered(
        self,
        discovered_model_ids: Collection[str],
    ) -> str:
        """Return the configured slug only when Codex reports that exact slug."""

        if self.configured_model_id not in discovered_model_ids:
            # Discovery values are provider-private and can be malformed.
            # Never include them in a package error or error context.
            raise ModelPolicyError(
                "The configured GPT-5.6 model is not available for this account."
            )
        return self.configured_model_id

    def require_turn_model(
        self,
        *,
        requested_model_id: str,
        discovered_model_ids: Collection[str],
    ) -> str:
        """Require both request identity and current exact discovery."""

        if requested_model_id != self.configured_model_id:
            raise ModelPolicyError("The turn must use the configured GPT-5.6 model.")
        return self.require_discovered(discovered_model_ids)

    def require_result_model(
        self,
        *,
        requested_model_id: str,
        result_model_id: str,
    ) -> str:
        """Reject an adapter result attributed to another model slug."""

        if (
            requested_model_id != self.configured_model_id
            or result_model_id != self.configured_model_id
        ):
            raise ModelPolicyError("The result must use the configured GPT-5.6 model.")
        return self.configured_model_id
