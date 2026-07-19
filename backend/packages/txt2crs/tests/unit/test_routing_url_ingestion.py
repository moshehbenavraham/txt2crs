# SPDX-License-Identifier: MIT-0

"""Package-owned URL routing between transcript and webpage ingestion."""

from collections.abc import Callable
from typing import cast

import pytest

from txt2crs.domain.models import InputLocation
from txt2crs.ingestion.errors import UnsupportedInputError
from txt2crs.ingestion.models import ExtractedContent, InputPayload
from txt2crs.ingestion.routing_url import RoutingUrlAdapter


class RecordingInputAdapter:
    """Return stable content while recording the exact delegated payload."""

    def __init__(self, *, format_name: str) -> None:
        self._format_name = format_name
        self.payloads: list[InputPayload] = []

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Record the selected payload and return one displayable document."""

        self.payloads.append(payload)
        return ExtractedContent(
            normalized_text=f"Content from {self._format_name}",
            media_type="text/plain",
            metadata={"format": self._format_name},
            warnings=[],
            locations=[InputLocation(label=self._format_name)],
        )


class RecordingUrlNormalizer:
    """Expose how often routing performs the authoritative URL check."""

    def __init__(self, normalized_url: str) -> None:
        self._normalized_url = normalized_url
        self.values: list[str] = []

    def __call__(self, value: str) -> str:
        """Return the configured canonical URL after recording the raw value."""

        self.values.append(value)
        return self._normalized_url


def _url_payload(value: str | bytes) -> InputPayload:
    """Build the one existing URL input type used by application callers."""

    return InputPayload(
        input_type="url",
        value=value,
        media_type="text/uri-list",
        file_name=None,
        metadata={"request_label": "learner source"},
    )


@pytest.mark.parametrize(
    "canonical_url",
    [
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://m.youtube.com/embed/dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtu.be/dQw4w9WgXcQ",
    ],
)
def test_recognized_youtube_hosts_use_only_transcript_ingestion(
    canonical_url: str,
) -> None:
    """Exact reviewed YouTube hosts must never fall through to webpages."""

    normalizer = RecordingUrlNormalizer(canonical_url)
    youtube_adapter = RecordingInputAdapter(format_name="youtube_transcript")
    general_url_adapter = RecordingInputAdapter(format_name="webpage")
    router = RoutingUrlAdapter(
        normalize_public_url=normalizer,
        youtube_adapter=youtube_adapter,
        general_url_adapter=general_url_adapter,
    )

    result = router.extract(_url_payload(" HTTPS://YouTube.com/raw "))

    assert result.metadata["format"] == "youtube_transcript"
    # InputPayload applies the package-wide strict whitespace normalization
    # before adapters see the accepted value.
    assert normalizer.values == ["HTTPS://YouTube.com/raw"]
    assert [payload.value for payload in youtube_adapter.payloads] == [canonical_url]
    assert youtube_adapter.payloads[0].metadata == {"request_label": "learner source"}
    assert general_url_adapter.payloads == []


def test_other_public_hosts_use_only_general_url_ingestion() -> None:
    """A host merely containing 'youtube' is not part of the allowlist."""

    canonical_url = "https://youtube.example.edu/course"
    normalizer = RecordingUrlNormalizer(canonical_url)
    youtube_adapter = RecordingInputAdapter(format_name="youtube_transcript")
    general_url_adapter = RecordingInputAdapter(format_name="webpage")
    router = RoutingUrlAdapter(
        normalize_public_url=normalizer,
        youtube_adapter=youtube_adapter,
        general_url_adapter=general_url_adapter,
    )

    result = router.extract(_url_payload("https://youtube.example.edu/course#part"))

    assert result.metadata["format"] == "webpage"
    assert normalizer.values == ["https://youtube.example.edu/course#part"]
    assert [payload.value for payload in general_url_adapter.payloads] == [
        canonical_url
    ]
    assert youtube_adapter.payloads == []


def test_router_rejects_non_string_url_before_validation_or_delegation() -> None:
    """Binary input cannot be smuggled through the shared URL input type."""

    normalizer = RecordingUrlNormalizer("https://example.edu/")
    youtube_adapter = RecordingInputAdapter(format_name="youtube_transcript")
    general_url_adapter = RecordingInputAdapter(format_name="webpage")
    router = RoutingUrlAdapter(
        normalize_public_url=normalizer,
        youtube_adapter=youtube_adapter,
        general_url_adapter=general_url_adapter,
    )

    with pytest.raises(UnsupportedInputError, match="URL input must be a string"):
        router.extract(_url_payload(b"https://example.edu/"))

    assert normalizer.values == []
    assert youtube_adapter.payloads == []
    assert general_url_adapter.payloads == []


def test_router_propagates_safe_url_rejection_without_delegating() -> None:
    """The routing boundary must fail closed when public URL policy rejects."""

    validation_calls: list[str] = []

    def reject_url(value: str) -> str:
        validation_calls.append(value)
        raise ValueError("The submitted URL is not public.")

    youtube_adapter = RecordingInputAdapter(format_name="youtube_transcript")
    general_url_adapter = RecordingInputAdapter(format_name="webpage")
    router = RoutingUrlAdapter(
        normalize_public_url=reject_url,
        youtube_adapter=youtube_adapter,
        general_url_adapter=general_url_adapter,
    )

    with pytest.raises(ValueError, match="not public"):
        router.extract(_url_payload("http://127.0.0.1/private"))

    assert validation_calls == ["http://127.0.0.1/private"]
    assert youtube_adapter.payloads == []
    assert general_url_adapter.payloads == []


def test_router_requires_a_parseable_hostname_after_normalization() -> None:
    """A buggy normalizer cannot make hostname-free data reach an adapter."""

    def normalizer(_value: str) -> str:
        return "https:///missing-host"

    typed_normalizer: Callable[[str], str] = normalizer
    router = RoutingUrlAdapter(
        normalize_public_url=typed_normalizer,
        youtube_adapter=RecordingInputAdapter(format_name="youtube_transcript"),
        general_url_adapter=RecordingInputAdapter(format_name="webpage"),
    )

    with pytest.raises(UnsupportedInputError, match="canonical hostname"):
        router.extract(_url_payload("https://example.edu/"))


def test_router_rejects_non_string_normalizer_output_without_delegating() -> None:
    """A broken URL normalizer cannot bypass typed child-adapter payloads."""

    unsafe_normalizer = cast(
        Callable[[str], str],
        lambda _value: b"https://youtube.com/watch?v=dQw4w9WgXcQ",
    )
    youtube_adapter = RecordingInputAdapter(format_name="youtube_transcript")
    general_url_adapter = RecordingInputAdapter(format_name="webpage")
    router = RoutingUrlAdapter(
        normalize_public_url=unsafe_normalizer,
        youtube_adapter=youtube_adapter,
        general_url_adapter=general_url_adapter,
    )

    with pytest.raises(UnsupportedInputError, match="canonical URL must be a string"):
        router.extract(_url_payload("https://example.edu/"))

    assert youtube_adapter.payloads == []
    assert general_url_adapter.payloads == []
