# SPDX-License-Identifier: MIT-0

"""Truthful token, quota, and billing-state accounting."""

from collections.abc import Iterable, Mapping
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import Field, model_validator

from txt2crs.domain.models import StrictContract


class BillingSource(StrEnum):
    """The account or provider that funded one stage."""

    chatgpt_subscription = "chatgpt_subscription"
    platform_api = "platform_api"
    research_provider = "research_provider"
    no_charge = "no_charge"
    mixed = "mixed"


class TokenUsageState(StrEnum):
    """How much confidence callers may place in token totals."""

    reported = "reported"
    estimated = "estimated"
    unavailable = "unavailable"
    partial = "partial"


class SubscriptionQuotaState(StrEnum):
    """Quota state separately reported from credential validity."""

    available = "available"
    limited = "limited"
    exhausted = "exhausted"
    unknown = "unknown"


class UsageRecord(StrictContract):
    """Common accounting fields accepted by aggregate calculations."""

    billing_source: BillingSource
    token_usage_state: TokenUsageState
    subscription_quota_state: SubscriptionQuotaState
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    estimated_api_cost: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def reported_tokens_must_be_present(self) -> "UsageRecord":
        """Prevent a record from claiming precision without values."""

        if self.token_usage_state is TokenUsageState.reported and (
            self.input_tokens is None or self.output_tokens is None
        ):
            raise ValueError("reported token usage requires input and output totals")
        return self


class RuntimeUsage(UsageRecord):
    """Usage and latency recorded for one model turn."""

    model_id: str = Field(min_length=1, max_length=128)
    latency_ms: int = Field(ge=0)
    retries: int = Field(default=0, ge=0)

    @classmethod
    def for_chatgpt_subscription(
        cls,
        *,
        model_id: str,
        input_tokens: int | None,
        output_tokens: int | None,
        latency_ms: int,
        quota_state: SubscriptionQuotaState = SubscriptionQuotaState.unknown,
        retries: int = 0,
    ) -> "RuntimeUsage":
        """Build subscription usage without inventing an API-dollar cost."""

        token_state = (
            TokenUsageState.reported
            if input_tokens is not None and output_tokens is not None
            else TokenUsageState.unavailable
        )
        return cls(
            billing_source=BillingSource.chatgpt_subscription,
            token_usage_state=token_state,
            subscription_quota_state=quota_state,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_api_cost=None,
            model_id=model_id,
            latency_ms=latency_ms,
            retries=retries,
        )

    @classmethod
    def for_platform_api(
        cls,
        *,
        model_id: str,
        input_tokens: int | None,
        output_tokens: int | None,
        latency_ms: int,
        retries: int = 0,
    ) -> "RuntimeUsage":
        """Build API-key usage without inventing provider pricing or quota."""

        token_state = (
            TokenUsageState.reported
            if input_tokens is not None and output_tokens is not None
            else TokenUsageState.unavailable
        )
        return cls(
            billing_source=BillingSource.platform_api,
            token_usage_state=token_state,
            subscription_quota_state=SubscriptionQuotaState.unknown,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_api_cost=None,
            model_id=model_id,
            latency_ms=latency_ms,
            retries=retries,
        )


class AggregateUsage(UsageRecord):
    """Best available totals across heterogeneous workflow stages."""

    stage_count: int = Field(ge=0)


def aggregate_usage(
    usage_records: Iterable[UsageRecord | Mapping[str, Any]],
) -> AggregateUsage:
    """Aggregate known values without coercing unknown values to exact zero."""

    records = [
        record
        if isinstance(record, UsageRecord)
        else UsageRecord.model_validate(record)
        for record in usage_records
    ]
    token_states = {record.token_usage_state for record in records}
    if not records or token_states == {TokenUsageState.unavailable}:
        token_usage_state = TokenUsageState.unavailable
    elif len(token_states) == 1:
        token_usage_state = next(iter(token_states))
    else:
        token_usage_state = TokenUsageState.partial

    known_input_values = [
        record.input_tokens for record in records if record.input_tokens is not None
    ]
    known_output_values = [
        record.output_tokens for record in records if record.output_tokens is not None
    ]
    known_cost_values = [
        record.estimated_api_cost
        for record in records
        if record.estimated_api_cost is not None
    ]
    billing_sources = {record.billing_source for record in records}
    quota_states = {record.subscription_quota_state for record in records}

    return AggregateUsage(
        billing_source=(
            next(iter(billing_sources))
            if len(billing_sources) == 1
            else BillingSource.mixed
        ),
        token_usage_state=token_usage_state,
        subscription_quota_state=(
            next(iter(quota_states))
            if len(quota_states) == 1
            else SubscriptionQuotaState.unknown
        ),
        input_tokens=sum(known_input_values) if known_input_values else None,
        output_tokens=sum(known_output_values) if known_output_values else None,
        estimated_api_cost=(
            sum(known_cost_values, start=Decimal("0")) if known_cost_values else None
        ),
        stage_count=len(records),
    )
