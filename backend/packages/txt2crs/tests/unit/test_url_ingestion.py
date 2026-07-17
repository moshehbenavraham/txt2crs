# SPDX-License-Identifier: MIT-0

"""Tests for safe URL input normalization through research extraction."""

import pytest

from txt2crs.ingestion.models import InputPayload
from txt2crs.ingestion.url import UrlAdapter
from txt2crs.research.models import ExtractedDocument, ExtractRequest, ExtractResult


class StubExtractor:
    """Return one normalized public document."""

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Echo the safe URL with fixture content."""

        return ExtractResult(
            documents=[
                ExtractedDocument(
                    url=request.urls[0],
                    title="Course page",
                    content="Variables bind names.",
                    content_bytes=21,
                )
            ],
            failed_urls=[],
        )


def test_url_adapter_returns_displayable_source_boundary() -> None:
    """URL input uses the same safe extraction boundary as research."""

    extracted = UrlAdapter(extractor=StubExtractor()).extract(
        InputPayload(
            input_type="url",
            value="https://example.com/course",
            media_type="text/uri-list",
            file_name=None,
            metadata={},
        )
    )

    assert extracted.normalized_text == "Variables bind names."
    assert extracted.locations[0].label == "https://example.com/course"
    assert extracted.metadata["title"] == "Course page"


def test_url_adapter_rejects_non_string_and_empty_extraction() -> None:
    """Uploaded bytes and provider-empty pages never become URL documents."""

    adapter = UrlAdapter(extractor=StubExtractor())
    with pytest.raises(ValueError, match="URL"):
        adapter.extract(
            InputPayload(
                input_type="url",
                value=b"not a URL",
                media_type="text/uri-list",
                file_name=None,
                metadata={},
            )
        )
