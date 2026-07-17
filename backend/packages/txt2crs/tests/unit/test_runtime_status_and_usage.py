# SPDX-License-Identifier: MIT-0

"""Tests for truthful readiness and usage reporting."""

from txt2crs.ai.runtime_status import (
    CredentialStatus,
    RuntimeReadiness,
    RuntimeReadinessStatus,
)
from txt2crs.ai.usage import (
    BillingSource,
    SubscriptionQuotaState,
    TokenUsageState,
    aggregate_usage,
)


def test_readiness_is_distinct_from_job_completion_and_sanitizes_warnings() -> None:
    """A ready credential is not a completed course or a place for secrets."""

    readiness = RuntimeReadiness.create(
        status=RuntimeReadinessStatus.ready,
        credential_status=CredentialStatus.valid,
        model_entitled=True,
        subscription_quota_state=SubscriptionQuotaState.available,
        warnings=["Credential at /home/ada/.codex/auth.json contains sk-secret-value"],
        recovery_actions=[],
    )

    assert readiness.status == RuntimeReadinessStatus.ready
    assert readiness.job_completed is False
    rendered_readiness = readiness.model_dump_json()
    assert "/home/ada" not in rendered_readiness
    assert "sk-secret-value" not in rendered_readiness


def test_unknown_token_and_quota_values_remain_unknown() -> None:
    """Missing subscription telemetry must not be reported as exact zero."""

    usage_summary = aggregate_usage(
        [
            {
                "billing_source": BillingSource.chatgpt_subscription,
                "token_usage_state": TokenUsageState.unavailable,
                "subscription_quota_state": SubscriptionQuotaState.unknown,
                "input_tokens": None,
                "output_tokens": None,
                "estimated_api_cost": None,
            }
        ]
    )

    assert usage_summary.input_tokens is None
    assert usage_summary.output_tokens is None
    assert usage_summary.estimated_api_cost is None
    assert usage_summary.token_usage_state == TokenUsageState.unavailable


def test_mixed_exact_and_unknown_usage_is_not_claimed_as_exact() -> None:
    """One unknown stage makes aggregate token precision explicitly estimated."""

    usage_summary = aggregate_usage(
        [
            {
                "billing_source": BillingSource.chatgpt_subscription,
                "token_usage_state": TokenUsageState.reported,
                "subscription_quota_state": SubscriptionQuotaState.available,
                "input_tokens": 100,
                "output_tokens": 50,
                "estimated_api_cost": None,
            },
            {
                "billing_source": BillingSource.research_provider,
                "token_usage_state": TokenUsageState.unavailable,
                "subscription_quota_state": SubscriptionQuotaState.unknown,
                "input_tokens": None,
                "output_tokens": None,
                "estimated_api_cost": None,
            },
        ]
    )

    assert usage_summary.token_usage_state == TokenUsageState.partial
    assert usage_summary.input_tokens == 100
    assert usage_summary.output_tokens == 50
