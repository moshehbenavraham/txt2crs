# SPDX-License-Identifier: MIT-0

"""Explicit live proof of ChatGPT subscription, MCP, schema, events, and usage."""

import os
import socket
from pathlib import Path
from threading import Thread
from time import monotonic, sleep
from typing import Literal

import pytest
import uvicorn

from txt2crs.ai.codex_runtime import (
    CodexSubscriptionRuntime,
    OfficialCodexSdkAdapter,
    ResearchMcpConnection,
)
from txt2crs.ai.events import RuntimeEvent, RuntimeEventType
from txt2crs.ai.runtime import CancellationToken, TurnRequest
from txt2crs.domain.models import StrictContract
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


def _available_loopback_port() -> int:
    """Reserve an ephemeral port number for the short-lived local server."""

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe_socket:
        probe_socket.bind(("127.0.0.1", 0))
        return int(probe_socket.getsockname()[1])


def _wait_until_server_started(server: uvicorn.Server) -> None:
    """Bound startup so a broken ASGI server cannot hang acceptance."""

    deadline = monotonic() + 10
    while not server.started:
        if monotonic() >= deadline:
            raise TimeoutError("The live research MCP server did not start.")
        sleep(0.05)


def test_live_chatgpt_turn_calls_allowlisted_research_tool(
    tmp_path: Path,
) -> None:
    """Verify the donor-independent subscription path against the real SDK."""

    port = _available_loopback_port()
    research_application = create_research_mcp_application(
        DeterministicResearchService(),
        port=port,
    )
    server = uvicorn.Server(
        uvicorn.Config(
            research_application.fastmcp.streamable_http_app(),
            host="127.0.0.1",
            port=port,
            log_level="error",
        )
    )
    server_thread = Thread(
        target=server.run,
        name="txt2crs-live-research-mcp",
        daemon=True,
    )
    server_thread.start()
    _wait_until_server_started(server)

    emitted_events: list[RuntimeEvent] = []
    parent_environment = dict(os.environ)
    configured_codex_home = os.getenv("TXT2CRS_LIVE_CODEX_HOME")
    isolated_codex_home = (
        Path(configured_codex_home)
        if configured_codex_home
        else Path.home() / ".codex"
    )
    adapter = OfficialCodexSdkAdapter.create(
        worker_directory=tmp_path / "codex-worker",
        codex_home=isolated_codex_home,
        parent_environment=parent_environment,
        research_mcp=ResearchMcpConnection(
            url=research_application.streamable_http_url,
        ),
        event_sink=emitted_events.append,
    )
    try:
        assert adapter.inspect_account_type() == "chatgpt"
        model_ids = adapter.list_model_ids()
        assert model_ids
        configured_model = os.getenv("TXT2CRS_LIVE_MODEL")
        model_id = configured_model or next(
            (candidate for candidate in model_ids if "gpt-5.4" in candidate),
            model_ids[0],
        )
        assert model_id in model_ids

        result = CodexSubscriptionRuntime(adapter=adapter).run_validated_turn(
            request=TurnRequest(
                request_id="live-subscription-probe",
                stage="live_research_probe",
                model_id=model_id,
                prompt_version="live-probe-v1",
                trusted_instructions=(
                    "Call research_search exactly once with query "
                    "'txt2crs live probe'. Then return the required schema with "
                    "tool_used='research_search' and the exact source title."
                ),
                untrusted_data='{"purpose":"subscription acceptance"}',
                timeout_seconds=120,
            ),
            artifact_model=LiveProbeResult,
            cancellation=CancellationToken(),
        )
    finally:
        adapter.close()
        server.should_exit = True
        server_thread.join(timeout=10)

    assert result.artifact.source_title == "TXT2CRS LIVE MCP PROBE SOURCE"
    assert result.usage.billing_source == "chatgpt_subscription"
    assert any(
        event.event_type is RuntimeEventType.tool_completed for event in emitted_events
    )
