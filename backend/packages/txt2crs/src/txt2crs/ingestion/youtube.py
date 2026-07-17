# SPDX-License-Identifier: MIT-0

"""YouTube identifier parsing and timestamped transcript ingestion."""

import re
from typing import Protocol
from urllib.parse import parse_qs, urlsplit

from txt2crs.domain.models import InputLocation
from txt2crs.ingestion.errors import EmptyInputError, UnsupportedInputError
from txt2crs.ingestion.models import ExtractedContent, InputPayload

_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
_YOUTUBE_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }
)


class YouTubeTranscriptFetcher(Protocol):
    """Provider boundary kept separate for credential-free tests."""

    def fetch(
        self,
        video_id: str,
        languages: list[str] | None,
    ) -> list[dict[str, object]]:
        """Return provider transcript dictionaries."""


class DefaultYouTubeTranscriptFetcher:
    """Fetch transcripts with the maintained youtube-transcript-api package."""

    def fetch(
        self,
        video_id: str,
        languages: list[str] | None,
    ) -> list[dict[str, object]]:
        """Normalize the library's current object response to dictionaries."""

        try:
            transcript_module = __import__(
                "youtube_transcript_api",
                fromlist=["YouTubeTranscriptApi"],
            )
            api = transcript_module.YouTubeTranscriptApi()
            fetched_transcript = api.fetch(video_id, languages=languages)
            return [
                {
                    "text": segment.text,
                    "start": segment.start,
                    "duration": segment.duration,
                }
                for segment in fetched_transcript
            ]
        except Exception as transcript_error:
            raise UnsupportedInputError(
                "The YouTube transcript is unavailable."
            ) from transcript_error


def extract_youtube_video_id(value: str) -> str:
    """Return one 11-character ID from common YouTube URL forms."""

    stripped_value = value.strip()
    if _VIDEO_ID_PATTERN.fullmatch(stripped_value):
        return stripped_value

    parsed_url = urlsplit(stripped_value)
    hostname = (parsed_url.hostname or "").casefold()
    if hostname not in _YOUTUBE_HOSTS:
        raise ValueError("Input is not a supported YouTube URL.")
    if hostname.endswith("youtu.be"):
        candidate_id = parsed_url.path.strip("/").split("/", maxsplit=1)[0]
    elif parsed_url.path == "/watch":
        candidate_id = parse_qs(parsed_url.query).get("v", [""])[0]
    else:
        path_parts = [part for part in parsed_url.path.split("/") if part]
        candidate_id = (
            path_parts[1]
            if len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts"}
            else ""
        )
    if not _VIDEO_ID_PATTERN.fullmatch(candidate_id):
        raise ValueError("The YouTube URL does not contain a valid video ID.")
    return candidate_id


class YouTubeTranscriptAdapter:
    """Normalize one remote YouTube transcript into timestamped content."""

    def __init__(
        self,
        *,
        transcript_fetcher: YouTubeTranscriptFetcher,
        preferred_languages: list[str] | None,
    ) -> None:
        self._transcript_fetcher = transcript_fetcher
        self._preferred_languages = preferred_languages

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Fetch and normalize a transcript without accepting arbitrary URLs."""

        if not isinstance(payload.value, str):
            raise UnsupportedInputError("YouTube input must be a URL or video ID.")
        video_id = extract_youtube_video_id(payload.value)
        raw_segments = self._transcript_fetcher.fetch(
            video_id,
            self._preferred_languages,
        )
        transcript_lines: list[str] = []
        locations: list[InputLocation] = []
        for raw_segment in raw_segments:
            text = str(raw_segment.get("text", "")).strip()
            if not text:
                continue
            raw_start_seconds = raw_segment.get("start", 0)
            if not isinstance(raw_start_seconds, (int, float, str)):
                raise UnsupportedInputError(
                    "The YouTube transcript contains an invalid timestamp."
                )
            try:
                start_seconds = float(raw_start_seconds)
            except (TypeError, ValueError) as timestamp_error:
                raise UnsupportedInputError(
                    "The YouTube transcript contains an invalid timestamp."
                ) from timestamp_error
            if start_seconds < 0:
                raise UnsupportedInputError(
                    "The YouTube transcript contains a negative timestamp."
                )
            transcript_lines.append(text)
            locations.append(
                InputLocation(
                    label=f"Timestamp {start_seconds:.2f}s",
                    timestamp_seconds=start_seconds,
                )
            )
        if not transcript_lines:
            raise EmptyInputError("The YouTube transcript contains no text.")
        return ExtractedContent(
            normalized_text="\n".join(transcript_lines),
            media_type=payload.media_type,
            metadata={"video_id": video_id, "format": "youtube_transcript"},
            warnings=["provider-generated-transcript"],
            locations=locations,
        )
