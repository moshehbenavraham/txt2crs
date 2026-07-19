# SPDX-License-Identifier: MIT-0

"""Tests for explicit disabled completion-notification contracts."""

import pytest
from pydantic import ValidationError

from txt2crs.jobs.notifications import (
    DeliveryNotificationMode,
    DeliveryNotificationPolicy,
    DeliveryNotificationState,
    DeliveryNotificationStatus,
)


def test_disabled_policy_produces_one_explicit_not_applicable_state() -> None:
    """Disabled delivery is durable state, not a nullable provider decision."""

    policy = DeliveryNotificationPolicy.disabled()

    assert policy == DeliveryNotificationPolicy(
        schema_version="1.0",
        mode=DeliveryNotificationMode.disabled,
    )
    assert policy.state_for_completion() == DeliveryNotificationState(
        schema_version="1.0",
        mode=DeliveryNotificationMode.disabled,
        status=DeliveryNotificationStatus.not_applicable,
    )


def test_notification_contracts_are_strict_and_immutable() -> None:
    """Unknown or mutated notification state cannot enter durable delivery."""

    policy = DeliveryNotificationPolicy.disabled()
    state = policy.state_for_completion()

    with pytest.raises(ValidationError):
        DeliveryNotificationPolicy.model_validate(
            {
                "schema_version": "1.0",
                "mode": "disabled",
                "provider": "not-configured",
            }
        )
    with pytest.raises(ValidationError):
        DeliveryNotificationState.model_validate(
            {
                "schema_version": "1.0",
                "mode": "disabled",
                "status": "pending",
            }
        )
    with pytest.raises(ValidationError):
        DeliveryNotificationState(
            schema_version="2.0",
            mode=DeliveryNotificationMode.disabled,
            status=DeliveryNotificationStatus.not_applicable,
        )
    with pytest.raises(ValidationError):
        policy.mode = DeliveryNotificationMode.disabled
    with pytest.raises(ValidationError):
        state.status = DeliveryNotificationStatus.not_applicable


def test_notification_enums_expose_no_implicit_provider_or_pending_state() -> None:
    """Session 04 cannot silently retain the old nullable notification outbox."""

    assert list(DeliveryNotificationMode) == [DeliveryNotificationMode.disabled]
    assert list(DeliveryNotificationStatus) == [
        DeliveryNotificationStatus.not_applicable
    ]
