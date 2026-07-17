# SPDX-License-Identifier: MIT-0

"""Tests for bounded input classification, normalization, and dispatch."""

from typing import Any

import pytest

from txt2crs.domain.models import InputLocation
from txt2crs.ingestion.models import (
    ExtractedContent,
    IngestionLimits,
    InputPayload,
    InputType,
)
from txt2crs.ingestion.service import (
    EmptyInputError,
    IngestionService,
    InputTooLargeError,
    UnsupportedInputError,
)


class StubInputAdapter:
    """Return source boundaries supplied by a test fixture."""

    def __init__(self, extracted_content: ExtractedContent) -> None:
        self.extracted_content = extracted_content
        self.received_payload: InputPayload | None = None

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Record the payload and return deterministic extracted content."""

        self.received_payload = payload
        return self.extracted_content


def default_service(
    adapters: dict[str, StubInputAdapter] | None = None,
) -> IngestionService:
    """Build a service with deliberately small test limits."""

    return IngestionService(
        limits=IngestionLimits(
            maximum_input_bytes=1_000,
            maximum_normalized_characters=2_000,
        ),
        adapters=adapters or {},
    )


def test_plain_text_is_normalized_and_hashed_with_stable_identity() -> None:
    """Equivalent line endings produce one normalized input document."""

    service = default_service()

    windows_document = service.ingest(
        InputPayload(
            input_type="text",
            value="Python variables\r\nbind names.\r\n",
            media_type="text/plain",
            file_name=None,
            metadata={"origin": "pasted"},
        )
    )
    unix_document = service.ingest(
        InputPayload(
            input_type="text",
            value="Python variables\nbind names.\n",
            media_type="text/plain",
            file_name=None,
            metadata={"origin": "pasted"},
        )
    )

    assert windows_document.normalized_text == "Python variables\nbind names."
    assert windows_document.content_hash == unix_document.content_hash
    assert windows_document.document_id == unix_document.document_id
    assert windows_document.locations[0].label == "Pasted text"


@pytest.mark.parametrize(
    "input_type",
    ["url", "pdf", "document", "slides", "image", "audio", "video"],
)
def test_each_non_text_input_dispatches_to_its_typed_adapter(
    input_type: InputType,
) -> None:
    """Every advertised input type uses an explicit extraction adapter."""

    adapter = StubInputAdapter(
        ExtractedContent(
            normalized_text=f"Extracted {input_type} content.",
            media_type=f"application/x-{input_type}",
            metadata={"adapter": input_type},
            warnings=[],
            locations=[
                InputLocation(
                    label=f"{input_type} location",
                    page=1 if input_type in {"pdf", "document", "slides"} else None,
                    timestamp_seconds=(
                        0.0 if input_type in {"audio", "video"} else None
                    ),
                )
            ],
        )
    )
    service = default_service(adapters={input_type: adapter})
    payload = InputPayload(
        input_type=input_type,
        value=b"binary input" if input_type != "url" else "https://example.com",
        media_type=f"application/x-{input_type}",
        file_name=f"course.{input_type}",
        metadata={},
    )

    document = service.ingest(payload)

    assert adapter.received_payload == payload
    assert document.input_type == input_type
    assert document.normalized_text == f"Extracted {input_type} content."
    assert document.locations[0].label == f"{input_type} location"


def test_empty_unsupported_and_oversized_inputs_fail_with_specific_errors() -> None:
    """Bad input never becomes a silently truncated or guessed document."""

    service = default_service()

    with pytest.raises(EmptyInputError, match="empty"):
        service.ingest(
            InputPayload(
                input_type="text",
                value=" \r\n\t ",
                media_type="text/plain",
                file_name=None,
                metadata={},
            )
        )
    with pytest.raises(UnsupportedInputError, match="image"):
        service.ingest(
            InputPayload(
                input_type="image",
                value=b"not configured",
                media_type="image/png",
                file_name="diagram.png",
                metadata={},
            )
        )
    with pytest.raises(InputTooLargeError, match="byte"):
        service.ingest(
            InputPayload(
                input_type="text",
                value="x" * 1_001,
                media_type="text/plain",
                file_name=None,
                metadata={},
            )
        )


def test_extracted_text_is_never_silently_truncated() -> None:
    """An adapter that exceeds the normalized limit causes an actionable error."""

    adapter = StubInputAdapter(
        ExtractedContent(
            normalized_text="x" * 2_001,
            media_type="application/pdf",
            metadata={},
            warnings=[],
            locations=[InputLocation(label="Page 1", page=1)],
        )
    )
    service = default_service(adapters={"pdf": adapter})

    with pytest.raises(InputTooLargeError, match="normalized"):
        service.ingest(
            InputPayload(
                input_type="pdf",
                value=b"small file",
                media_type="application/pdf",
                file_name="course.pdf",
                metadata={},
            )
        )


def test_language_detection_flags_mixed_and_right_to_left_content() -> None:
    """Language and direction warnings survive into the normalized document."""

    service = default_service()
    document = service.ingest(
        InputPayload(
            input_type="text",
            value="Python variables. משתנים שומרים ערכים.",
            media_type="text/plain",
            file_name=None,
            metadata={},
        )
    )

    assert document.language == "mixed"
    assert "mixed-language" in document.warnings
    assert "right-to-left-content" in document.warnings


def test_payload_rejects_unknown_fields_and_wrong_value_types() -> None:
    """The public ingestion request remains a strict versioned contract."""

    invalid_payload: dict[str, Any] = {
        "input_type": "text",
        "value": "content",
        "media_type": "text/plain",
        "file_name": None,
        "metadata": {},
        "guess_this": True,
    }

    with pytest.raises(ValueError):
        InputPayload.model_validate(invalid_payload)
