# SPDX-License-Identifier: MIT-0

"""Tests for reviewed research-provider declarations."""

from datetime import date

import pytest

from txt2crs.research.source_policy import (
    ProviderReviewStatus,
    ResearchSourcePolicy,
    SourcePolicyRegistry,
    SourcePolicyViolation,
)


def reviewed_tavily_policy() -> ResearchSourcePolicy:
    """Return the fixed provider declaration used by service tests."""

    return ResearchSourcePolicy(
        schema_version="1.0",
        policy_version="research-policy-1",
        provider_id="tavily",
        review_status=ProviderReviewStatus.reviewed,
        enabled=True,
        reviewed_by="txt2crs maintainers",
        reviewed_on=date(2026, 7, 17),
        allowed_origin="https://api.tavily.com",
        model_controlled_fields=["query", "maximum_results"],
        maximum_items_per_request=10,
        maximum_items_per_job=30,
        maximum_bytes_per_job=2_000_000,
        maximum_seconds_per_request=30,
        allowed_course_domains=["general"],
        high_risk_allowed=False,
    )


def test_only_reviewed_enabled_providers_can_execute() -> None:
    """Availability and credentials never substitute for policy review."""

    reviewed_policy = reviewed_tavily_policy()
    pending_policy = reviewed_policy.model_copy(
        update={
            "provider_id": "unreviewed-provider",
            "review_status": ProviderReviewStatus.pending,
        }
    )
    registry = SourcePolicyRegistry([reviewed_policy, pending_policy])

    assert registry.require_executable("tavily").provider_id == "tavily"
    with pytest.raises(SourcePolicyViolation, match="not reviewed"):
        registry.require_executable("unreviewed-provider")


def test_configuration_cannot_promote_an_unknown_provider() -> None:
    """Environment values may disable policy, but never create approval."""

    registry = SourcePolicyRegistry([reviewed_tavily_policy()])

    with pytest.raises(SourcePolicyViolation, match="unknown"):
        registry.with_enabled_provider_ids({"tavily", "made-up-provider"})


def test_model_can_control_only_reviewed_query_fields() -> None:
    """A model cannot select origins, headers, secrets, or provider limits."""

    registry = SourcePolicyRegistry([reviewed_tavily_policy()])

    registry.validate_model_controlled_fields(
        provider_id="tavily",
        field_names={"query", "maximum_results"},
    )
    with pytest.raises(SourcePolicyViolation, match="base_url"):
        registry.validate_model_controlled_fields(
            provider_id="tavily",
            field_names={"query", "base_url"},
        )


def test_high_risk_course_requires_an_explicit_provider_review() -> None:
    """General web research cannot silently support medical/legal guidance."""

    registry = SourcePolicyRegistry([reviewed_tavily_policy()])

    with pytest.raises(SourcePolicyViolation, match="high-risk"):
        registry.require_executable("tavily", high_risk_course=True)
