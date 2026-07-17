# SPDX-License-Identifier: MIT-0

"""Budgeted service exposing exactly two typed research operations."""

from typing import Protocol

from txt2crs.ai.budgets import RunBudget
from txt2crs.ai.retry import RetryController
from txt2crs.ai.runtime import CancellationToken
from txt2crs.ai.tool_guardrails import ToolCallGuardrailController
from txt2crs.research.models import (
    ExtractRequest,
    ExtractResult,
    SearchRequest,
    SearchResult,
)
from txt2crs.research.source_policy import SourcePolicyRegistry
from txt2crs.research.tavily import ResearchProviderRetryableError


class ResearchProvider(Protocol):
    """Provider behavior needed by the local tool service."""

    def search(self, request: SearchRequest) -> SearchResult:
        """Return normalized public search candidates."""

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Return normalized public source documents."""


class ResearchToolService:
    """Apply cancellation, policy, guardrails, and budgets around research."""

    tool_names = ("research_search", "research_extract")
    tool_schemas = {
        "research_search": SearchRequest.model_json_schema(),
        "research_extract": ExtractRequest.model_json_schema(),
    }

    def __init__(
        self,
        *,
        provider_id: str,
        provider: ResearchProvider,
        source_policy_registry: SourcePolicyRegistry,
        budget: RunBudget,
        guardrail: ToolCallGuardrailController,
        cancellation: CancellationToken,
        retry_controller: RetryController,
    ) -> None:
        self._provider_id = provider_id
        self._provider = provider
        self._source_policy_registry = source_policy_registry
        self._budget = budget
        self._guardrail = guardrail
        self._cancellation = cancellation
        self._retry_controller = retry_controller

    def search(self, request: SearchRequest) -> SearchResult:
        """Execute an approved, bounded search."""

        self._cancellation.raise_if_cancelled()
        self._source_policy_registry.require_executable(self._provider_id)
        self._source_policy_registry.validate_model_controlled_fields(
            provider_id=self._provider_id,
            field_names={"query", "maximum_results"},
        )
        arguments = request.model_dump(mode="json")
        decision = self._guardrail.inspect("research_search", arguments)
        if not decision.allowed:
            raise PermissionError(f"Research search rejected: {decision.reason_code}.")
        self._budget.reserve_research_call(tool_name="research_search")

        try:
            result = self._retry_controller.run(
                lambda: self._provider.search(request),
                is_retryable=lambda error: isinstance(
                    error,
                    ResearchProviderRetryableError,
                ),
                retry_after_seconds=_provider_retry_after_seconds,
            )
            self._cancellation.raise_if_cancelled()
            self._budget.reserve_sources(len(result.hits))
        except Exception:
            self._guardrail.record_result(
                tool_name="research_search",
                arguments=arguments,
                succeeded=False,
            )
            raise
        self._guardrail.record_result(
            tool_name="research_search",
            arguments=arguments,
            succeeded=True,
        )
        return result

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Execute approved extraction and reserve the accepted bytes."""

        self._cancellation.raise_if_cancelled()
        self._source_policy_registry.require_executable(self._provider_id)
        # URLs originate from reviewed search candidates and are not arbitrary
        # provider configuration; the provider validates each URL again.
        arguments = request.model_dump(mode="json")
        decision = self._guardrail.inspect("research_extract", arguments)
        if not decision.allowed:
            raise PermissionError(f"Research extract rejected: {decision.reason_code}.")
        self._budget.reserve_research_call(tool_name="research_extract")

        try:
            result = self._retry_controller.run(
                lambda: self._provider.extract(request),
                is_retryable=lambda error: isinstance(
                    error,
                    ResearchProviderRetryableError,
                ),
                retry_after_seconds=_provider_retry_after_seconds,
            )
            self._cancellation.raise_if_cancelled()
            total_document_bytes = sum(
                document.content_bytes for document in result.documents
            )
            self._budget.reserve_extracted_bytes(total_document_bytes)
        except Exception:
            self._guardrail.record_result(
                tool_name="research_extract",
                arguments=arguments,
                succeeded=False,
            )
            raise
        self._guardrail.record_result(
            tool_name="research_extract",
            arguments=arguments,
            succeeded=True,
        )
        return result


def _provider_retry_after_seconds(error: Exception) -> float | None:
    """Read only the reviewed retry hint from a typed Tavily failure."""

    if isinstance(error, ResearchProviderRetryableError):
        return error.retry_after_seconds
    return None
