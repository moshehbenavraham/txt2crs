# SPDX-License-Identifier: MIT-0

"""Actionable ingestion failures shared by all adapters."""


class IngestionError(ValueError):
    """Base class for input that cannot become a normalized document."""


class EmptyInputError(IngestionError):
    """No useful text remained after extraction."""


class UnsupportedInputError(IngestionError):
    """The media type or required adapter cannot be handled safely."""


class InputTooLargeError(IngestionError):
    """Raw or normalized content crossed a hard size limit."""
