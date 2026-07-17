# SPDX-License-Identifier: MIT-0

"""Contracts shared by the ingestion dispatcher and individual adapters."""

from typing import Any, Literal

from pydantic import Field

from txt2crs.domain.models import InputLocation, StrictContract

InputType = Literal[
    "prompt",
    "text",
    "url",
    "pdf",
    "document",
    "slides",
    "image",
    "audio",
    "video",
]


class InputPayload(StrictContract):
    """One authorized raw input before parsing or normalization."""

    input_type: InputType
    value: str | bytes
    media_type: str = Field(min_length=1, max_length=255)
    file_name: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any]


class ExtractedContent(StrictContract):
    """Provider-neutral output returned by every input adapter."""

    normalized_text: str = Field(max_length=2_000_000)
    media_type: str = Field(min_length=1, max_length=255)
    metadata: dict[str, Any]
    warnings: list[str] = Field(max_length=100)
    locations: list[InputLocation] = Field(max_length=10_000)


class IngestionLimits(StrictContract):
    """Hard byte and character limits applied before and after extraction."""

    maximum_input_bytes: int = Field(gt=0, le=1_000_000_000)
    maximum_normalized_characters: int = Field(gt=0, le=10_000_000)
