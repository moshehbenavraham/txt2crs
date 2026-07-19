# SPDX-License-Identifier: MIT-0

"""Explicit live proof of ChatGPT subscription, MCP, schema, events, and usage."""

import os
from pathlib import Path
from typing import Literal

import pytest

from txt2crs.ai.codex_runtime import (
    CodexSubscriptionRuntime,
    OfficialCodexSdkAdapter,
    ResearchMcpConnection,
)
from txt2crs.ai.events import RuntimeEvent, RuntimeEventType
from txt2crs.ai.model_policy import DEFAULT_GPT56_MODEL_ID, Gpt56ModelPolicy
from txt2crs.ai.runtime import CancellationToken, TurnRequest
from txt2crs.domain.models import StrictContract
from txt2crs.research.managed_mcp import ManagedResearchMcpServer
from txt2crs.research.mcp_server import create_research_mcp_application
from txt2crs.research.models import (
    ExtractedDocument,
    ExtractRequest,
    ExtractResult,
    SearchHit,
    SearchRequest,
    SearchResult,
)

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("TXT2CRS_RUN_LIVE_CODEX") != "1",
        reason="Set TXT2CRS_RUN_LIVE_CODEX=1 for subscription acceptance.",
    ),
]


class LiveProbeResult(StrictContract):
    """Small schema proving the model consumed the allowlisted tool result."""

    schema_version: Literal["1.0"]
    tool_used: Literal["research_search"]
    source_title: str


class DeterministicResearchService:
    """Serve public-shaped evidence without spending a research API quota."""

    def search(self, request: SearchRequest) -> SearchResult:
        """Return one unmistakable title for the live model to report."""

        return SearchResult(
            query=request.query,
            hits=[
                SearchHit(
                    title="TXT2CRS LIVE MCP PROBE SOURCE",
                    url="https://example.com/txt2crs-live-probe",
                    snippet="A deterministic subscription acceptance source.",
                    relevance_score=1.0,
                )
            ],
        )

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Support extraction if the model chooses the second allowed tool."""

        return ExtractResult(
            documents=[
                ExtractedDocument(
                    url=request.urls[0],
                    title="TXT2CRS LIVE MCP PROBE SOURCE",
                    content="This is deterministic acceptance evidence.",
                    content_bytes=42,
                )
            ],
            failed_urls=[],
        )


def test_live_chatgpt_turn_calls_allowlisted_research_tool(
    tmp_path: Path,
) -> None:
    """Verify the donor-independent subscription path against the real SDK."""

    model_policy = Gpt56ModelPolicy(
        configured_model_id=os.getenv(
            "TXT2CRS_MODEL_ID",
            DEFAULT_GPT56_MODEL_ID,
        )
    )
    research_application = create_research_mcp_application(
        DeterministicResearchService(),
        port=0,
    )
    emitted_events: list[RuntimeEvent] = []
    parent_environment = dict(os.environ)
    configured_codex_home = os.getenv("TXT2CRS_LIVE_CODEX_HOME")
    isolated_codex_home = (
        Path(configured_codex_home) if configured_codex_home else Path.home() / ".codex"
    )
    managed_research_mcp = ManagedResearchMcpServer(
        research_application,
        host="127.0.0.1",
        port=0,
    )
    with managed_research_mcp as ready_research_mcp:
        adapter = OfficialCodexSdkAdapter.create(
            worker_directory=tmp_path / "codex-worker",
            codex_home=isolated_codex_home,
            parent_environment=parent_environment,
            research_mcp=ResearchMcpConnection(
                url=ready_research_mcp.url,
            ),
            event_sink=emitted_events.append,
        )
        try:
            runtime = CodexSubscriptionRuntime(
                adapter=adapter,
                model_policy=model_policy,
            )
            assert runtime.inspect_readiness().model_entitled is True
            result = runtime.run_validated_turn(
                request=TurnRequest(
                    request_id="live-subscription-probe",
                    stage="live_research_probe",
                    model_id=model_policy.configured_model_id,
                    prompt_version="live-probe-v1",
                    trusted_instructions=(
                        "Call research_search exactly once with query "
                        "'txt2crs live probe'. Then return the required schema "
                        "with tool_used='research_search' and the exact source "
                        "title."
                    ),
                    untrusted_data='{"purpose":"subscription acceptance"}',
                    timeout_seconds=120,
                ),
                artifact_model=LiveProbeResult,
                cancellation=CancellationToken(),
            )
        finally:
            adapter.close()

    assert result.artifact.tool_used == "research_search"
    assert result.artifact.source_title == "TXT2CRS LIVE MCP PROBE SOURCE"
    assert result.usage.model_id == model_policy.configured_model_id
    assert result.usage.billing_source == "chatgpt_subscription"
    completed_tool_events = [
        event
        for event in emitted_events
        if event.event_type is RuntimeEventType.tool_completed
    ]
    assert len(completed_tool_events) == 1
    assert "research_search" in completed_tool_events[0].safe_message
