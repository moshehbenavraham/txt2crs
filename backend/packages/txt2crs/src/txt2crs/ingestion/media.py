# SPDX-License-Identifier: MIT-0

"""Injected OCR and timestamped transcription adapters."""

from importlib import import_module
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import Any, Protocol

from PIL import Image
from pydantic import Field

from txt2crs.domain.models import InputLocation, StrictContract
from txt2crs.ingestion.errors import EmptyInputError, UnsupportedInputError
from txt2crs.ingestion.models import ExtractedContent, InputPayload


class TimestampedSegment(StrictContract):
    """One transcription segment with a displayable start time."""

    start_seconds: float = Field(ge=0)
    text: str = Field(min_length=1, max_length=100_000)


class OcrEngine(Protocol):
    """Minimal OCR dependency boundary."""

    def extract_text(self, image_bytes: bytes) -> str:
        """Return a textual equivalent of an image."""


class MediaTranscriber(Protocol):
    """Minimal local audio/video transcription boundary."""

    def transcribe(
        self,
        media_bytes: bytes,
        media_type: str,
    ) -> list[TimestampedSegment]:
        """Return timestamped transcript segments."""


class PytesseractOcrEngine:
    """Production OCR engine backed by Pillow and the Tesseract executable."""

    def extract_text(self, image_bytes: bytes) -> str:
        """Decode the image and invoke maintained pytesseract bindings."""

        try:
            pytesseract = import_module("pytesseract")
            with Image.open(BytesIO(image_bytes)) as image:
                extracted_text = pytesseract.image_to_string(image)
        except Exception as ocr_error:
            raise UnsupportedInputError(
                "Image OCR failed; verify the image and Tesseract installation."
            ) from ocr_error
        return str(extracted_text)


class FasterWhisperTranscriber:
    """Optional local transcriber loaded only with the ``transcription`` extra."""

    def __init__(self, *, model_name: str = "small") -> None:
        try:
            faster_whisper = import_module("faster_whisper")
        except ImportError as import_error:
            raise UnsupportedInputError(
                "Install txt2crs[transcription] for local audio/video transcription."
            ) from import_error
        self._model: Any = faster_whisper.WhisperModel(model_name)

    def transcribe(
        self,
        media_bytes: bytes,
        media_type: str,
    ) -> list[TimestampedSegment]:
        """Write an isolated temporary media file and return model segments."""

        suffix = ".mp4" if media_type.startswith("video/") else ".audio"
        with NamedTemporaryFile(suffix=suffix) as media_file:
            media_file.write(media_bytes)
            media_file.flush()
            raw_segments, _information = self._model.transcribe(media_file.name)
            return [
                TimestampedSegment(
                    start_seconds=float(segment.start),
                    text=str(segment.text).strip(),
                )
                for segment in raw_segments
                if str(segment.text).strip()
            ]


class ImageOcrAdapter:
    """Turn an uploaded image into accessible text."""

    def __init__(self, *, ocr_engine: OcrEngine) -> None:
        self._ocr_engine = ocr_engine

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Run OCR and label the result honestly."""

        if not isinstance(payload.value, bytes):
            raise UnsupportedInputError("Image input must be uploaded as bytes.")
        extracted_text = self._ocr_engine.extract_text(payload.value).strip()
        if not extracted_text:
            raise EmptyInputError("Image OCR produced no text.")
        return ExtractedContent(
            normalized_text=extracted_text,
            media_type=payload.media_type,
            metadata={"format": "image"},
            warnings=["ocr-generated-text"],
            locations=[InputLocation(label="Image")],
        )


class TranscriptionAdapter:
    """Turn an uploaded audio/video file into timestamped text."""

    def __init__(self, *, transcriber: MediaTranscriber) -> None:
        self._transcriber = transcriber

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Transcribe bytes and preserve every segment start time."""

        if not isinstance(payload.value, bytes):
            raise UnsupportedInputError("Media input must be uploaded as bytes.")
        segments = self._transcriber.transcribe(payload.value, payload.media_type)
        if not segments:
            raise EmptyInputError("Media transcription produced no text.")
        return ExtractedContent(
            normalized_text="\n".join(segment.text for segment in segments),
            media_type=payload.media_type,
            metadata={"format": payload.input_type},
            warnings=["machine-generated-transcript"],
            locations=[
                InputLocation(
                    label=f"Timestamp {segment.start_seconds:.2f}s",
                    timestamp_seconds=segment.start_seconds,
                )
                for segment in segments
            ],
        )
