# SPDX-License-Identifier: MIT-0

"""Contract tests for the static two-tool FastMCP application."""

import asyncio

import pytest

from txt2crs.research.mcp_server import create_research_mcp_application
from txt2crs.research.models import (
    ExtractedDocument,
    ExtractRequest,
    ExtractResult,
    SearchHit,
    SearchRequest,
    SearchResult,
)


class StubResearchService:
    """Return deterministic model-dumpable research results."""

    def search(self, request: SearchRequest) -> SearchResult:
        """Return one hit."""

        return SearchResult(
            query=request.query,
            hits=[
                SearchHit(
                    title="Python",
                    url="https://example.com/python",
                    snippet="Course",
                    relevance_score=0.9,
                )
            ],
        )

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Return one document."""

        return ExtractResult(
            documents=[
                ExtractedDocument(
                    url=request.urls[0],
                    title="Python",
                    content="Variables bind names.",
                    content_bytes=21,
                )
            ],
            failed_urls=[],
        )


def test_fastmcp_application_registers_only_two_static_tools() -> None:
    """Codex cannot discover shell, files, arbitrary HTTP, or plugin registries."""

    application = create_research_mcp_application(StubResearchService())

    assert application.tool_names == ("research_search", "research_extract")
    assert type(application.mcpserver).__module__.startswith("mcp.")
    assert application.streamable_http_url == "http://127.0.0.1:8765/mcp"


def test_local_dispatch_validates_input_and_returns_structured_content() -> None:
    """The same strict schemas protect local tests and FastMCP dispatch."""

    application = create_research_mcp_application(StubResearchService())

    search_result = asyncio.run(
        application.call_tool(
            "research_search",
            {"query": "Python variables", "maximum_results": 1},
        )
    )
    extract_result = asyncio.run(
        application.call_tool(
            "research_extract",
            {"urls": ["https://example.com/python"]},
        )
    )

    assert search_result["query"] == "Python variables"
    assert search_result["hits"][0]["title"] == "Python"
    assert extract_result["documents"][0]["content"] == "Variables bind names."


def test_unknown_tools_and_unknown_fields_fail_closed() -> None:
    """Dynamic or malformed tool requests never reach the service."""

    application = create_research_mcp_application(StubResearchService())

    with pytest.raises(PermissionError, match="not registered"):
        asyncio.run(application.call_tool("shell_execute", {"command": "env"}))
    with pytest.raises(ValueError):
        asyncio.run(
            application.call_tool(
                "research_search",
                {
                    "query": "Python",
                    "maximum_results": 1,
                    "base_url": "https://evil.test",
                },
            )
        )
