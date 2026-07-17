# SPDX-License-Identifier: MIT-0

"""Provider readiness without conflating it with job execution state."""

from enum import StrEnum
from typing import Self

from pydantic import Field

from txt2crs.ai.usage import SubscriptionQuotaState
from txt2crs.domain.models import StrictContract
from txt2crs.security.redaction import sanitize_public_text


class RuntimeReadinessStatus(StrEnum):
    """Whether a configured runtime can currently accept a turn."""

    ready = "ready"
    degraded = "degraded"
    unavailable = "unavailable"


class CredentialStatus(StrEnum):
    """Credential state reported without exposing credential material."""

    valid = "valid"
    missing = "missing"
    expired = "expired"
    reauthentication_required = "reauthentication_required"
    unknown = "unknown"


class RuntimeReadiness(StrictContract):
    """A browser-safe readiness projection for the current runtime."""

    status: RuntimeReadinessStatus
    credential_status: CredentialStatus
    model_entitled: bool
    subscription_quota_state: SubscriptionQuotaState
    warnings: list[str] = Field(max_length=20)
    recovery_actions: list[str] = Field(max_length=20)
    job_completed: bool = False

    @classmethod
    def create(
        cls,
        *,
        status: RuntimeReadinessStatus,
        credential_status: CredentialStatus,
        model_entitled: bool,
        subscription_quota_state: SubscriptionQuotaState,
        warnings: list[str],
        recovery_actions: list[str],
    ) -> Self:
        """Sanitize readiness once instead of trusting every API consumer."""

        return cls(
            status=status,
            credential_status=credential_status,
            model_entitled=model_entitled,
            subscription_quota_state=subscription_quota_state,
            warnings=[sanitize_public_text(warning) for warning in warnings[:20]],
            recovery_actions=[
                sanitize_public_text(action) for action in recovery_actions[:20]
            ],
            job_completed=False,
        )
