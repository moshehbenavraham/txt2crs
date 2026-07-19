# SPDX-License-Identifier: MIT-0

"""Canonical public-URL routing between transcript and webpage adapters."""

from collections.abc import Callable
from urllib.parse import urlsplit

from txt2crs.ingestion.errors import UnsupportedInputError
from txt2crs.ingestion.models import ExtractedContent, InputPayload
from txt2crs.ingestion.service import InputAdapter

_YOUTUBE_HOSTS = frozenset(
    {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }
)


class RoutingUrlAdapter:
    """Validate one URL and delegate to exactly one package-owned adapter."""

    def __init__(
        self,
        *,
        normalize_public_url: Callable[[str], str],
        youtube_adapter: InputAdapter,
        general_url_adapter: InputAdapter,
    ) -> None:
        self._normalize_public_url = normalize_public_url
        self._youtube_adapter = youtube_adapter
        self._general_url_adapter = general_url_adapter

    def extract(self, payload: InputPayload) -> ExtractedContent:
        """Canonicalize once for routing and pass only that value downstream."""

        if not isinstance(payload.value, str):
            raise UnsupportedInputError("URL input must be a string.")

        canonical_url = self._normalize_public_url(payload.value)
        if not isinstance(canonical_url, str):
            # Callable annotations do not validate values returned by an
            # injected implementation. Fail before ``urlsplit`` can produce a
            # bytes hostname or a child receives an unvalidated payload.
            raise UnsupportedInputError("The canonical URL must be a string.")
        try:
            hostname = (urlsplit(canonical_url).hostname or "").casefold()
        except (TypeError, ValueError) as parsing_error:
            raise UnsupportedInputError(
                "The normalized URL has no canonical hostname."
            ) from parsing_error
        if not hostname:
            raise UnsupportedInputError("The normalized URL has no canonical hostname.")

        # Rebuild instead of mutating the accepted payload. The routing adapter
        # owns only the canonical URL value; media type and metadata remain the
        # exact application request fields needed by the selected child.
        canonical_payload = payload.model_copy(
            update={"value": canonical_url},
            deep=True,
        )
        selected_adapter = (
            self._youtube_adapter
            if hostname in _YOUTUBE_HOSTS
            else self._general_url_adapter
        )
        return selected_adapter.extract(canonical_payload)


__all__ = ["RoutingUrlAdapter"]
