# SPDX-License-Identifier: MIT-0

"""Tests for the budgeted two-tool research service."""

from datetime import date

import pytest

from txt2crs.ai.budgets import BudgetExceededError, RunBudget, RunBudgetLimits
from txt2crs.ai.retry import RetryController, RetrySettings
from txt2crs.ai.runtime import CancellationToken
from txt2crs.ai.tool_guardrails import (
    ToolCallGuardrailConfig,
    ToolCallGuardrailController,
)
from txt2crs.research.models import (
    ExtractedDocument,
    ExtractRequest,
    ExtractResult,
    SearchHit,
    SearchRequest,
    SearchResult,
)
from txt2crs.research.service import ResearchToolService
from txt2crs.research.source_policy import (
    ProviderReviewStatus,
    ResearchSourcePolicy,
    SourcePolicyRegistry,
)


class StubResearchProvider:
    """Return one deterministic hit and document without network access."""

    def search(self, request: SearchRequest) -> SearchResult:
        """Return one public search hit."""

        return SearchResult(
            query=request.query,
            hits=[
                SearchHit(
                    title="Python docs",
                    url="https://docs.python.org/3/tutorial/",
                    snippet="Python tutorial",
                    relevance_score=0.9,
                )
            ],
        )

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Return one bounded extracted document."""

        return ExtractResult(
            documents=[
                ExtractedDocument(
                    url=request.urls[0],
                    title="Python docs",
                    content="Python is a programming language.",
                    content_bytes=33,
                )
            ],
            failed_urls=[],
        )


def reviewed_tavily_policy() -> ResearchSourcePolicy:
    """Return the reviewed declaration used by the tool service."""

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


def default_budget() -> RunBudget:
    """Return a deliberately small research budget for service tests."""

    return RunBudget(
        RunBudgetLimits(
            maximum_turns=2,
            maximum_research_calls=2,
            maximum_search_calls=1,
            maximum_extract_calls=1,
            maximum_sources=2,
            maximum_extracted_bytes=100,
            maximum_input_tokens=100,
            maximum_output_tokens=100,
            maximum_retries=1,
            maximum_repairs=1,
            maximum_elapsed_seconds=60,
        )
    )


def research_service(
    *,
    budget: RunBudget | None = None,
    cancellation: CancellationToken | None = None,
) -> ResearchToolService:
    """Build the service with fixed policy and deterministic collaborators."""

    selected_budget = budget or default_budget()
    selected_cancellation = cancellation or CancellationToken()
    return ResearchToolService(
        provider_id="tavily",
        provider=StubResearchProvider(),
        source_policy_registry=SourcePolicyRegistry([reviewed_tavily_policy()]),
        budget=selected_budget,
        guardrail=ToolCallGuardrailController(
            ToolCallGuardrailConfig(
                maximum_exact_repeats=1,
                maximum_failure_repeats=1,
            )
        ),
        cancellation=selected_cancellation,
        retry_controller=RetryController(
            settings=RetrySettings(
                maximum_attempts=2,
                base_seconds=0.001,
                maximum_seconds=0.001,
                jitter_ratio=0,
            ),
            budget=selected_budget,
            cancellation=selected_cancellation,
            sleeper=lambda _delay: None,
            random_unit=lambda: 0.5,
        ),
    )


def test_service_exposes_only_search_and_extract_schemas() -> None:
    """The Codex-facing service cannot discover shell or arbitrary fetch tools."""

    service = research_service()

    assert service.tool_names == ("research_search", "research_extract")
    assert set(service.tool_schemas) == {"research_search", "research_extract"}


def test_service_enforces_budget_and_records_sources_and_bytes() -> None:
    """Tool execution reserves all scarce resources before accepting results."""

    budget = default_budget()
    service = research_service(budget=budget)

    search_result = service.search(
        SearchRequest(query="Python tutorial", maximum_results=1)
    )
    extract_result = service.extract(ExtractRequest(urls=[search_result.hits[0].url]))
    snapshot = budget.snapshot()

    assert len(extract_result.documents) == 1
    assert snapshot.research_calls == 2
    assert snapshot.sources == 1
    assert snapshot.extracted_bytes == 33


def test_repeated_equivalent_calls_are_rejected() -> None:
    """A stuck model cannot repeat an already completed search."""

    service = research_service()
    request = SearchRequest(query="Python tutorial", maximum_results=1)

    service.search(request)
    with pytest.raises(PermissionError, match="repeated"):
        service.search(request)


def test_cancellation_stops_before_provider_execution() -> None:
    """Cancellation is checked before policy, budget, or network work."""

    cancellation = CancellationToken()
    cancellation.cancel()
    service = research_service(cancellation=cancellation)

    with pytest.raises(RuntimeError, match="cancelled"):
        service.search(SearchRequest(query="Python", maximum_results=1))


def test_budget_exhaustion_fails_before_a_second_tool_side_effect() -> None:
    """Research work never starts when its total call reservation fails."""

    budget = default_budget()
    service = research_service(budget=budget)
    service.search(SearchRequest(query="Python", maximum_results=1))
    service.extract(ExtractRequest(urls=["https://example.com/course"]))

    with pytest.raises((BudgetExceededError, PermissionError)):
        service.search(SearchRequest(query="Different query", maximum_results=1))
