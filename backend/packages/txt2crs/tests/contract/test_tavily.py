# SPDX-License-Identifier: MIT-0

"""Contract tests for the fixed-origin Tavily research adapter."""

import json

import httpx
import pytest
from pydantic import SecretStr

from txt2crs.research.models import ExtractRequest, SearchRequest
from txt2crs.research.tavily import (
    ResearchProviderError,
    ResearchProviderRetryableError,
    TavilyClient,
    TavilySettings,
)


def test_search_sends_bounded_request_and_normalizes_results() -> None:
    """Provider JSON becomes stable local search-hit contracts."""

    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://api.tavily.com/search"
        payload = json.loads(request.content)
        assert payload == {
            "api_key": "tavily-secret",
            "query": "Python assignment semantics",
            "max_results": 2,
            "search_depth": "advanced",
        }
        return httpx.Response(
            200,
            json={
                "query": payload["query"],
                "results": [
                    {
                        "title": "Python Reference",
                        "url": "https://docs.python.org/3/reference/simple_stmts.html",
                        "content": "Assignment statements bind names to values.",
                        "score": 0.97,
                    }
                ],
            },
        )

    client = TavilyClient(
        settings=TavilySettings(api_key=SecretStr("tavily-secret")),
        http_client=httpx.Client(transport=httpx.MockTransport(handle_request)),
        url_resolver=lambda _hostname: ("151.101.0.223",),
    )

    result = client.search(
        SearchRequest(
            query="Python assignment semantics",
            maximum_results=2,
        )
    )

    assert result.query == "Python assignment semantics"
    assert len(result.hits) == 1
    assert result.hits[0].title == "Python Reference"
    assert result.hits[0].relevance_score == pytest.approx(0.97)


def test_extract_rejects_unsafe_urls_before_provider_request() -> None:
    """The research provider is never used as an SSRF proxy."""

    request_count = 0

    def handle_request(_request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1
        return httpx.Response(200, json={"results": []})

    client = TavilyClient(
        settings=TavilySettings(api_key=SecretStr("tavily-secret")),
        http_client=httpx.Client(transport=httpx.MockTransport(handle_request)),
        url_resolver=lambda _hostname: ("93.184.216.34",),
    )

    with pytest.raises(ResearchProviderError, match="unsafe"):
        client.extract(ExtractRequest(urls=["http://127.0.0.1/private"]))

    assert request_count == 0


def test_extract_normalizes_documents_and_enforces_content_bytes() -> None:
    """Oversized provider documents cannot silently enter the evidence ledger."""

    def handle_request(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "url": "https://example.com/course",
                        "raw_content": "x" * 200,
                    }
                ],
                "failed_results": [],
            },
        )

    client = TavilyClient(
        settings=TavilySettings(
            api_key=SecretStr("tavily-secret"),
            maximum_document_bytes=100,
        ),
        http_client=httpx.Client(transport=httpx.MockTransport(handle_request)),
        url_resolver=lambda _hostname: ("93.184.216.34",),
    )

    with pytest.raises(ResearchProviderError, match="byte limit"):
        client.extract(ExtractRequest(urls=["https://example.com/course"]))


def test_rate_limit_is_retryable_but_never_leaks_the_api_key() -> None:
    """Typed errors preserve retry policy while redacting secrets."""

    def handle_request(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            text="quota rejected tavily-secret",
            headers={"retry-after": "2"},
        )

    client = TavilyClient(
        settings=TavilySettings(api_key=SecretStr("tavily-secret")),
        http_client=httpx.Client(transport=httpx.MockTransport(handle_request)),
        url_resolver=lambda _hostname: ("93.184.216.34",),
    )

    with pytest.raises(ResearchProviderRetryableError) as captured_error:
        client.search(SearchRequest(query="Python", maximum_results=1))

    assert captured_error.value.retry_after_seconds == 2
    assert "tavily-secret" not in str(captured_error.value)


def test_malformed_success_payload_is_a_permanent_typed_error() -> None:
    """A 200 response still needs the provider contract to be valid."""

    client = TavilyClient(
        settings=TavilySettings(api_key=SecretStr("tavily-secret")),
        http_client=httpx.Client(
            transport=httpx.MockTransport(
                lambda _request: httpx.Response(200, json={"results": "not-a-list"})
            )
        ),
        url_resolver=lambda _hostname: ("93.184.216.34",),
    )

    with pytest.raises(ResearchProviderError, match="malformed"):
        client.search(SearchRequest(query="Python", maximum_results=1))
