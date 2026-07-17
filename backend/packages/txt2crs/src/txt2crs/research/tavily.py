# SPDX-License-Identifier: MIT

"""Fixed-origin Tavily search and extraction adapter.

The request/normalization split was adapted from Hermes' MIT-licensed
``plugins/web/tavily/provider.py`` at commit
``0f102fa4dc04b7dfdab048169aaaa640d09d7523``. Registry coupling, environment
globals, and arbitrary provider origins were removed.
"""

from collections.abc import Mapping
from typing import Any

import httpx
from pydantic import Field, SecretStr

from txt2crs.domain.models import StrictContract
from txt2crs.research.models import (
    ExtractedDocument,
    ExtractRequest,
    ExtractResult,
    SearchHit,
    SearchRequest,
    SearchResult,
)
from txt2crs.security.url_safety import Resolver, UnsafeUrlError, normalize_public_url

TAVILY_ORIGIN = "https://api.tavily.com"


class TavilySettings(StrictContract):
    """Reviewed provider limits; the model cannot change these values."""

    api_key: SecretStr
    timeout_seconds: float = Field(default=20, gt=0, le=60)
    maximum_document_bytes: int = Field(default=1_000_000, gt=0, le=10_000_000)


class ResearchProviderError(RuntimeError):
    """Permanent provider, policy, or payload failure."""


class ResearchProviderRetryableError(ResearchProviderError):
    """Transient provider failure with an optional server retry hint."""

    def __init__(
        self,
        message: str,
        *,
        retry_after_seconds: float | None = None,
    ) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__(message)


class TavilyClient:
    """Search and extract through one fixed production HTTPS origin."""

    def __init__(
        self,
        *,
        settings: TavilySettings,
        http_client: httpx.Client,
        url_resolver: Resolver,
    ) -> None:
        self._settings = settings
        self._http_client = http_client
        self._url_resolver = url_resolver

    def _post(self, endpoint: str, payload: dict[str, Any]) -> Mapping[str, Any]:
        """POST provider JSON and translate transport/status failures."""

        payload_with_secret = {
            "api_key": self._settings.api_key.get_secret_value(),
            **payload,
        }
        try:
            response = self._http_client.post(
                f"{TAVILY_ORIGIN}/{endpoint}",
                json=payload_with_secret,
                timeout=self._settings.timeout_seconds,
            )
        except (httpx.TimeoutException, httpx.TransportError) as transport_error:
            raise ResearchProviderRetryableError(
                "The research provider is temporarily unavailable."
            ) from transport_error

        if response.status_code == 429 or response.status_code >= 500:
            retry_after_header = response.headers.get("retry-after")
            try:
                retry_after_seconds = (
                    float(retry_after_header)
                    if retry_after_header is not None
                    else None
                )
            except ValueError:
                retry_after_seconds = None
            raise ResearchProviderRetryableError(
                "The research provider requested a bounded retry.",
                retry_after_seconds=retry_after_seconds,
            )
        if response.status_code >= 400:
            raise ResearchProviderError(
                f"The research provider rejected the request ({response.status_code})."
            )
        try:
            response_payload = response.json()
        except ValueError as json_error:
            raise ResearchProviderError(
                "The research provider returned malformed JSON."
            ) from json_error
        if not isinstance(response_payload, Mapping):
            raise ResearchProviderError(
                "The research provider returned a malformed payload."
            )
        return response_payload

    def search(self, request: SearchRequest) -> SearchResult:
        """Run one bounded search and normalize public candidate URLs."""

        response_payload = self._post(
            "search",
            {
                "query": request.query,
                "max_results": request.maximum_results,
                "search_depth": "advanced",
            },
        )
        raw_results = response_payload.get("results")
        if not isinstance(raw_results, list):
            raise ResearchProviderError(
                "The research provider returned malformed search results."
            )

        normalized_hits: list[SearchHit] = []
        for raw_result in raw_results[: request.maximum_results]:
            if not isinstance(raw_result, Mapping):
                raise ResearchProviderError(
                    "The research provider returned a malformed search item."
                )
            try:
                canonical_url = normalize_public_url(
                    str(raw_result["url"]),
                    resolver=self._url_resolver,
                )
                normalized_hits.append(
                    SearchHit(
                        title=str(raw_result["title"]),
                        url=canonical_url,
                        snippet=str(raw_result.get("content", "")),
                        relevance_score=float(raw_result.get("score", 0)),
                    )
                )
            except (KeyError, TypeError, ValueError, UnsafeUrlError) as item_error:
                raise ResearchProviderError(
                    "The research provider returned a malformed or unsafe search item."
                ) from item_error
        return SearchResult(query=request.query, hits=normalized_hits)

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Validate every URL, then extract bounded provider documents."""

        try:
            canonical_urls = [
                normalize_public_url(url, resolver=self._url_resolver)
                for url in request.urls
            ]
        except UnsafeUrlError as unsafe_url_error:
            raise ResearchProviderError(
                "The extraction request contained an unsafe URL."
            ) from unsafe_url_error

        response_payload = self._post("extract", {"urls": canonical_urls})
        raw_documents = response_payload.get("results")
        raw_failures = response_payload.get("failed_results", [])
        if not isinstance(raw_documents, list) or not isinstance(raw_failures, list):
            raise ResearchProviderError(
                "The research provider returned malformed extraction results."
            )

        normalized_documents: list[ExtractedDocument] = []
        for raw_document in raw_documents:
            if not isinstance(raw_document, Mapping):
                raise ResearchProviderError(
                    "The research provider returned a malformed document."
                )
            content = str(
                raw_document.get("raw_content") or raw_document.get("content") or ""
            )
            content_bytes = len(content.encode("utf-8"))
            if content_bytes > self._settings.maximum_document_bytes:
                raise ResearchProviderError(
                    "An extracted document exceeded the configured byte limit."
                )
            if not content:
                raise ResearchProviderError(
                    "The research provider returned an empty document."
                )
            try:
                canonical_url = normalize_public_url(
                    str(raw_document["url"]),
                    resolver=self._url_resolver,
                )
            except (KeyError, UnsafeUrlError) as url_error:
                raise ResearchProviderError(
                    "The research provider returned an unsafe document URL."
                ) from url_error
            normalized_documents.append(
                ExtractedDocument(
                    url=canonical_url,
                    title=str(raw_document.get("title") or canonical_url),
                    content=content,
                    content_bytes=content_bytes,
                )
            )

        failed_urls = [
            str(failed_item.get("url", "unavailable"))
            if isinstance(failed_item, Mapping)
            else "unavailable"
            for failed_item in raw_failures[:10]
        ]
        return ExtractResult(
            documents=normalized_documents,
            failed_urls=failed_urls,
        )
