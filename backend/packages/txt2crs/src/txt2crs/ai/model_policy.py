# SPDX-License-Identifier: MIT-0

"""Exact configured-model discovery and no-fallback policy.

Codex model discovery is an entitlement check, not a model-selection
algorithm. Keeping that distinction here prevents an account-specific list
order from silently changing the model used for a learner's course.
"""

from collections.abc import Collection

from pydantic import BaseModel, ConfigDict, Field

# Keep the release's established model as the compatibility default. Operators
# may select any other exact model identifier that their Codex account reports.
DEFAULT_MODEL_ID = "gpt-5.6-sol"
MODEL_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$"

# Deprecated compatibility exports remain available to package consumers that
# imported the pre-1.3 names. They no longer define an allowlist.
DEFAULT_GPT56_MODEL_ID = DEFAULT_MODEL_ID
REVIEWED_GPT56_MODEL_IDS = frozenset(
    {
        "gpt-5.6-sol",
        "gpt-5.6-terra",
        "gpt-5.6-luna",
    }
)


class ModelPolicyError(RuntimeError):
    """The configured model failed an exact local or discovery check."""


class ExactModelPolicy(BaseModel):
    """Immutable exact model selection used by every Codex turn."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
        str_strip_whitespace=True,
    )

    configured_model_id: str = Field(
        default=DEFAULT_MODEL_ID,
        min_length=1,
        max_length=128,
        pattern=MODEL_ID_PATTERN,
    )

    def require_discovered(
        self,
        discovered_model_ids: Collection[str],
    ) -> str:
        """Return the configured slug only when Codex reports that exact slug."""

        if self.configured_model_id not in discovered_model_ids:
            # Discovery values are provider-private and can be malformed.
            # Never include them in a package error or error context.
            raise ModelPolicyError(
                "The configured model is not available for this account."
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
            raise ModelPolicyError("The turn must use the configured model.")
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
            raise ModelPolicyError("The result must use the configured model.")
        return self.configured_model_id


# Backward-compatible alias for the public class name used through release
# 1.2.x. The policy is now model-family neutral despite the historical name.
Gpt56ModelPolicy = ExactModelPolicy
