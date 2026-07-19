# SPDX-License-Identifier: MIT-0

"""Versioned completion-notification policy and durable state.

The initial application deliberately ships without an outbound completion
provider. Persisting that decision explicitly avoids treating a nullable
timestamp as either "pending", "failed", or "feature disabled" during job
recovery.
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator


class DeliveryNotificationMode(StrEnum):
    """Supported completion-notification provider modes."""

    disabled = "disabled"


class DeliveryNotificationStatus(StrEnum):
    """Durable result states for the selected notification mode."""

    not_applicable = "not_applicable"


class DeliveryNotificationState(BaseModel):
    """Exact versioned notification state stored beside one delivery."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
        str_strip_whitespace=True,
    )

    schema_version: str
    mode: DeliveryNotificationMode
    status: DeliveryNotificationStatus

    @field_validator("schema_version")
    @classmethod
    def require_supported_schema_version(cls, schema_version: str) -> str:
        """Reject notification state from an unknown durable schema."""

        if schema_version != "1.0":
            raise ValueError("Unsupported delivery notification schema version.")
        return schema_version


class DeliveryNotificationPolicy(BaseModel):
    """Immutable application policy that derives completion delivery state."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        hide_input_in_errors=True,
        str_strip_whitespace=True,
    )

    schema_version: str
    mode: DeliveryNotificationMode

    @field_validator("schema_version")
    @classmethod
    def require_supported_schema_version(cls, schema_version: str) -> str:
        """Reject notification policy from an unknown durable schema."""

        if schema_version != "1.0":
            raise ValueError("Unsupported delivery notification schema version.")
        return schema_version

    @classmethod
    def disabled(cls) -> "DeliveryNotificationPolicy":
        """Build the only reviewed notification policy for this release."""

        return cls(
            schema_version="1.0",
            mode=DeliveryNotificationMode.disabled,
        )

    def state_for_completion(self) -> DeliveryNotificationState:
        """Return the exact state persisted after private artifact storage."""

        return DeliveryNotificationState(
            schema_version=self.schema_version,
            mode=self.mode,
            status=DeliveryNotificationStatus.not_applicable,
        )
