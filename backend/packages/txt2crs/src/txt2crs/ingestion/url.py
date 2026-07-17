# SPDX-License-Identifier: MIT-0

"""URL ingestion through the same safe extraction boundary as research."""

from typing import Protocol

from txt2crs.domain.models import InputLocation
from txt2crs.ingestion.errors import EmptyInputError, UnsupportedInputError
from txt2crs.ingestion.models import ExtractedContent, InputPayload
from txt2crs.research.models import ExtractRequest, ExtractResult


class UrlExtractor(Protocol):
    """Provider-neutral URL extraction dependency."""

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Extract one public URL."""


class UrlAdapter:
    """Normalize one public webpage into an input document boundary."""

    def __init__(self, *, extractor: UrlExtractor) -> None:
        self._extractor = extractor

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Delegate URL safety/extraction and require one non-empty document."""

        if not isinstance(payload.value, str):
            raise UnsupportedInputError("URL input must be a string.")
        extraction_result = self._extractor.extract(
            ExtractRequest(urls=[payload.value])
        )
        if not extraction_result.documents:
            raise EmptyInputError("URL extraction returned no readable text.")
        document = extraction_result.documents[0]
        return ExtractedContent(
            normalized_text=document.content,
            media_type="text/html",
            metadata={
                "title": document.title,
                "canonical_url": document.url,
                "format": "webpage",
            },
            warnings=[],
            locations=[InputLocation(label=document.url)],
        )
