# SPDX-License-Identifier: MIT-0

"""Typed contracts at the research-tool boundary."""

from pydantic import Field, model_validator

from txt2crs.domain.models import StrictContract


class SearchRequest(StrictContract):
    """A focused, bounded public-web search."""

    query: str = Field(min_length=2, max_length=500)
    maximum_results: int = Field(default=5, ge=1, le=10)


class SearchHit(StrictContract):
    """One normalized candidate returned by a research provider."""

    title: str = Field(min_length=1, max_length=2_000)
    url: str = Field(min_length=8, max_length=2_048)
    snippet: str = Field(max_length=10_000)
    relevance_score: float = Field(ge=0, le=1)


class SearchResult(StrictContract):
    """Stable provider-neutral results for one search query."""

    query: str
    hits: list[SearchHit] = Field(max_length=10)


class ExtractRequest(StrictContract):
    """A bounded batch of already discovered public URLs."""

    urls: list[str] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def require_unique_urls(self) -> "ExtractRequest":
        """Avoid paying for the same extraction twice in one request."""

        if len(self.urls) != len(set(self.urls)):
            raise ValueError("extract URLs must be unique")
        return self


class ExtractedDocument(StrictContract):
    """Normalized text extracted from one approved public URL."""

    url: str = Field(min_length=8, max_length=2_048)
    title: str = Field(min_length=1, max_length=2_000)
    content: str = Field(min_length=1, max_length=1_000_000)
    content_bytes: int = Field(gt=0, le=10_000_000)


class ExtractResult(StrictContract):
    """Successful documents and safe failed URL labels."""

    documents: list[ExtractedDocument] = Field(max_length=10)
    failed_urls: list[str] = Field(max_length=10)
