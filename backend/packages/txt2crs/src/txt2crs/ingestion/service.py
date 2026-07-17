# SPDX-License-Identifier: MIT-0

"""Input dispatcher that produces one canonical :class:`InputDocument`."""

import re
from collections.abc import Mapping
from typing import Protocol

from txt2crs.domain.models import InputDocument, InputLocation
from txt2crs.ingestion.errors import (
    EmptyInputError,
    InputTooLargeError,
    UnsupportedInputError,
)
from txt2crs.ingestion.models import (
    ExtractedContent,
    IngestionLimits,
    InputPayload,
)
from txt2crs.research.evidence import hash_text

_HEBREW_PATTERN = re.compile(r"[\u0590-\u05ff]")
_ARABIC_PATTERN = re.compile(r"[\u0600-\u06ff\u0750-\u077f]")
_LATIN_PATTERN = re.compile(r"[A-Za-z]")
_CJK_PATTERN = re.compile(r"[\u3400-\u9fff]")


class InputAdapter(Protocol):
    """Extract bounded normalized content from one typed input."""

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Parse one authorized payload."""


class IngestionService:
    """Normalize text directly and delegate all other input types explicitly."""

    def __init__(
        self,
        *,
        limits: IngestionLimits,
        adapters: Mapping[str, InputAdapter],
    ) -> None:
        self._limits = limits
        self._adapters = dict(adapters)

    def ingest(self, payload: InputPayload) -> InputDocument:
        """Validate sizes, dispatch extraction, detect language, and hash text."""

        raw_bytes = (
            payload.value.encode("utf-8")
            if isinstance(payload.value, str)
            else payload.value
        )
        if len(raw_bytes) > self._limits.maximum_input_bytes:
            raise InputTooLargeError("Input exceeds the configured byte limit.")

        if payload.input_type in {"prompt", "text"}:
            extracted_content = ExtractedContent(
                normalized_text=(
                    payload.value
                    if isinstance(payload.value, str)
                    else payload.value.decode("utf-8", errors="strict")
                ),
                media_type=payload.media_type,
                metadata={},
                warnings=[],
                locations=[
                    InputLocation(
                        label=(
                            "Course prompt"
                            if payload.input_type == "prompt"
                            else "Pasted text"
                        )
                    )
                ],
            )
        else:
            adapter = self._adapters.get(payload.input_type)
            if adapter is None:
                raise UnsupportedInputError(
                    f"No {payload.input_type} ingestion adapter is configured."
                )
            extracted_content = adapter.extract(payload)

        normalized_text = _normalize_text(extracted_content.normalized_text)
        if not normalized_text:
            raise EmptyInputError("Input is empty after extraction.")
        if len(normalized_text) > self._limits.maximum_normalized_characters:
            raise InputTooLargeError(
                "Extracted normalized text exceeds the configured character limit."
            )

        language, language_warnings = _detect_language(normalized_text)
        warnings = list(
            dict.fromkeys([*extracted_content.warnings, *language_warnings])
        )
        content_hash = hash_text(normalized_text)
        metadata = {
            **payload.metadata,
            **extracted_content.metadata,
        }
        if payload.file_name is not None:
            metadata["file_name"] = payload.file_name

        return InputDocument(
            schema_version="1.0",
            document_id=f"input-{content_hash.removeprefix('sha256:')[:24]}",
            input_type=payload.input_type,
            media_type=extracted_content.media_type,
            normalized_text=normalized_text,
            language=language,
            metadata=metadata,
            content_hash=content_hash,
            warnings=warnings,
            locations=extracted_content.locations,
        )


def _normalize_text(value: str) -> str:
    """Normalize line endings and trailing whitespace without truncation."""

    normalized_lines = [
        line.rstrip()
        for line in value.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    ]
    return "\n".join(normalized_lines).strip()


def _detect_language(value: str) -> tuple[str, list[str]]:
    """Apply a deterministic script-level language/direction hint."""

    contains_hebrew = _HEBREW_PATTERN.search(value) is not None
    contains_arabic = _ARABIC_PATTERN.search(value) is not None
    contains_latin = _LATIN_PATTERN.search(value) is not None
    contains_cjk = _CJK_PATTERN.search(value) is not None
    detected_script_count = sum(
        [contains_hebrew, contains_arabic, contains_latin, contains_cjk]
    )
    warnings: list[str] = []
    if detected_script_count > 1:
        language = "mixed"
        warnings.append("mixed-language")
    elif contains_hebrew:
        language = "he"
    elif contains_arabic:
        language = "ar"
    elif contains_cjk:
        language = "zh"
    else:
        language = "en"
    if contains_hebrew or contains_arabic:
        warnings.append("right-to-left-content")
    return language, warnings


__all__ = [
    "EmptyInputError",
    "IngestionService",
    "InputTooLargeError",
    "UnsupportedInputError",
]
