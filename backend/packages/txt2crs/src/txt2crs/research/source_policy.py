# SPDX-License-Identifier: MIT-0

"""Static reviewed-provider policy independent of runtime configuration."""

from datetime import date
from enum import StrEnum
from typing import Self

from pydantic import Field

from txt2crs.domain.models import Identifier, SchemaVersion, StrictContract


class ProviderReviewStatus(StrEnum):
    """Human review state for a provider declaration."""

    reviewed = "reviewed"
    pending = "pending"
    rejected = "rejected"


class ResearchSourcePolicy(StrictContract):
    """Versioned caps and governance for one research provider."""

    schema_version: SchemaVersion
    policy_version: Identifier
    provider_id: Identifier
    review_status: ProviderReviewStatus
    enabled: bool
    reviewed_by: str = Field(min_length=1, max_length=500)
    reviewed_on: date
    allowed_origin: str = Field(min_length=8, max_length=2_048)
    model_controlled_fields: list[Identifier] = Field(max_length=20)
    maximum_items_per_request: int = Field(gt=0, le=100)
    maximum_items_per_job: int = Field(gt=0, le=1_000)
    maximum_bytes_per_job: int = Field(gt=0, le=100_000_000)
    maximum_seconds_per_request: float = Field(gt=0, le=300)
    allowed_course_domains: list[Identifier] = Field(min_length=1, max_length=50)
    high_risk_allowed: bool


class SourcePolicyViolation(PermissionError):
    """Raised before unreviewed research can execute."""


class SourcePolicyRegistry:
    """Fail-closed registry constructed only from reviewed source declarations."""

    def __init__(self, policies: list[ResearchSourcePolicy]) -> None:
        policy_ids = [policy.provider_id for policy in policies]
        if len(policy_ids) != len(set(policy_ids)):
            raise ValueError("Research provider IDs must be unique.")
        self._policies = {policy.provider_id: policy for policy in policies}

    def require_executable(
        self,
        provider_id: str,
        *,
        high_risk_course: bool = False,
    ) -> ResearchSourcePolicy:
        """Return a provider only when review, enablement, and risk permit it."""

        policy = self._policies.get(provider_id)
        if policy is None:
            raise SourcePolicyViolation(
                f"Research provider {provider_id!r} is unknown."
            )
        if policy.review_status is not ProviderReviewStatus.reviewed:
            raise SourcePolicyViolation(
                f"Research provider {provider_id!r} is not reviewed."
            )
        if not policy.enabled:
            raise SourcePolicyViolation(
                f"Research provider {provider_id!r} is disabled."
            )
        if high_risk_course and not policy.high_risk_allowed:
            raise SourcePolicyViolation(
                f"Research provider {provider_id!r} is not approved "
                "for high-risk courses."
            )
        return policy

    def with_enabled_provider_ids(self, enabled_provider_ids: set[str]) -> Self:
        """Apply configuration as a disable-only filter."""

        unknown_provider_ids = enabled_provider_ids - set(self._policies)
        if unknown_provider_ids:
            unknown_provider_id = sorted(unknown_provider_ids)[0]
            raise SourcePolicyViolation(
                f"Configured research provider {unknown_provider_id!r} is unknown."
            )
        filtered_policies = [
            policy.model_copy(
                update={
                    "enabled": policy.enabled
                    and policy.provider_id in enabled_provider_ids
                }
            )
            for policy in self._policies.values()
        ]
        return type(self)(filtered_policies)

    def validate_model_controlled_fields(
        self,
        *,
        provider_id: str,
        field_names: set[str],
    ) -> None:
        """Reject any model-supplied field absent from the reviewed allowlist."""

        policy = self.require_executable(provider_id)
        unreviewed_fields = field_names - set(policy.model_controlled_fields)
        if unreviewed_fields:
            unreviewed_field = sorted(unreviewed_fields)[0]
            raise SourcePolicyViolation(
                f"Model-controlled field {unreviewed_field!r} is not reviewed."
            )
