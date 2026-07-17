# SPDX-License-Identifier: MIT-0

"""Tests for injected OCR/transcription and YouTube helpers."""

import pytest

from txt2crs.ingestion.media import (
    ImageOcrAdapter,
    TimestampedSegment,
    TranscriptionAdapter,
)
from txt2crs.ingestion.models import InputPayload, InputType
from txt2crs.ingestion.youtube import (
    YouTubeTranscriptAdapter,
    extract_youtube_video_id,
)


class StubOcrEngine:
    """Return deterministic OCR text without requiring a system binary."""

    def extract_text(self, image_bytes: bytes) -> str:
        """Verify bytes are forwarded and return fixture text."""

        assert image_bytes == b"image bytes"
        return "Diagram: variable points to value."


class StubTranscriber:
    """Return timestamped segments for audio/video tests."""

    def transcribe(
        self, media_bytes: bytes, media_type: str
    ) -> list[TimestampedSegment]:
        """Return two stable segments and verify input metadata."""

        assert media_bytes == b"media bytes"
        assert media_type in {"audio/wav", "video/mp4"}
        return [
            TimestampedSegment(start_seconds=0, text="Variables bind names."),
            TimestampedSegment(start_seconds=3.5, text="Values may change."),
        ]


class StubYouTubeTranscriptFetcher:
    """Return provider-like transcript dictionaries."""

    def fetch(
        self, video_id: str, languages: list[str] | None
    ) -> list[dict[str, object]]:
        """Return one bounded segment."""

        assert video_id == "dQw4w9WgXcQ"
        assert languages == ["en"]
        return [{"text": "Course introduction", "start": 1.25, "duration": 2.0}]


def test_image_ocr_adapter_returns_textual_equivalent() -> None:
    """Image input becomes accessible text through an injected OCR engine."""

    extracted = ImageOcrAdapter(ocr_engine=StubOcrEngine()).extract(
        InputPayload(
            input_type="image",
            value=b"image bytes",
            media_type="image/png",
            file_name="diagram.png",
            metadata={},
        )
    )

    assert extracted.normalized_text.startswith("Diagram:")
    assert "ocr-generated-text" in extracted.warnings


@pytest.mark.parametrize(
    ("input_type", "media_type"),
    [("audio", "audio/wav"), ("video", "video/mp4")],
)
def test_transcription_preserves_timestamp_boundaries(
    input_type: InputType,
    media_type: str,
) -> None:
    """Audio and local video keep timestamps for learner citations."""

    extracted = TranscriptionAdapter(transcriber=StubTranscriber()).extract(
        InputPayload(
            input_type=input_type,
            value=b"media bytes",
            media_type=media_type,
            file_name=f"course.{input_type}",
            metadata={},
        )
    )

    assert "Variables bind names." in extracted.normalized_text
    assert [location.timestamp_seconds for location in extracted.locations] == [
        0,
        3.5,
    ]


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ?t=10",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "dQw4w9WgXcQ",
    ],
)
def test_youtube_video_id_supports_common_url_forms(url: str) -> None:
    """Common YouTube links resolve to one stable video identifier."""

    assert extract_youtube_video_id(url) == "dQw4w9WgXcQ"


def test_youtube_transcript_adapter_returns_timestamped_content() -> None:
    """Remote video transcripts use the same normalized video contract."""

    extracted = YouTubeTranscriptAdapter(
        transcript_fetcher=StubYouTubeTranscriptFetcher(),
        preferred_languages=["en"],
    ).extract(
        InputPayload(
            input_type="video",
            value="https://youtu.be/dQw4w9WgXcQ",
            media_type="text/x-youtube-url",
            file_name=None,
            metadata={},
        )
    )

    assert extracted.normalized_text == "Course introduction"
    assert extracted.locations[0].timestamp_seconds == 1.25


def test_invalid_youtube_identifier_is_rejected() -> None:
    """Malformed URLs never reach the transcript provider."""

    with pytest.raises(ValueError, match="YouTube"):
        extract_youtube_video_id("https://example.com/not-youtube")
