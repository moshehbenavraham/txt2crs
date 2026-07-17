# SPDX-License-Identifier: MIT-0

"""Bounded, page-aware PDF text extraction using maintained PyMuPDF."""

from typing import Any

import fitz  # type: ignore[import-untyped]

from txt2crs.domain.models import InputLocation
from txt2crs.ingestion.errors import EmptyInputError, UnsupportedInputError
from txt2crs.ingestion.models import ExtractedContent, InputPayload


class PdfAdapter:
    """Extract textual PDFs while rejecting corruption and encryption."""

    def __init__(self, *, maximum_pages: int) -> None:
        if maximum_pages < 1:
            raise ValueError("maximum_pages must be positive")
        self._maximum_pages = maximum_pages

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Return page text and stable 1-based page locations."""

        if not isinstance(payload.value, bytes):
            raise UnsupportedInputError("PDF input must be uploaded as bytes.")
        try:
            pdf_document = fitz.open(stream=payload.value, filetype="pdf")
        except Exception as parsing_error:
            raise UnsupportedInputError(
                "PDF input is corrupt or unsupported."
            ) from parsing_error

        try:
            if pdf_document.needs_pass:
                raise UnsupportedInputError(
                    "Password-protected or encrypted PDF input is unsupported."
                )
            if pdf_document.page_count > self._maximum_pages:
                raise UnsupportedInputError(
                    "PDF input exceeds the configured page limit."
                )

            page_texts: list[str] = []
            locations: list[InputLocation] = []
            for page_index, page in enumerate(pdf_document):
                page_text = str(page.get_text("text")).strip()
                if not page_text:
                    continue
                page_texts.append(page_text)
                locations.append(
                    InputLocation(
                        label=f"Page {page_index + 1}",
                        page=page_index + 1,
                    )
                )
            if not page_texts:
                raise EmptyInputError("PDF contains no extractable text.")
            metadata: dict[str, Any] = {
                "page_count": pdf_document.page_count,
                "format": "pdf",
            }
            return ExtractedContent(
                normalized_text="\n\n".join(page_texts),
                media_type="application/pdf",
                metadata=metadata,
                warnings=[],
                locations=locations,
            )
        finally:
            pdf_document.close()
