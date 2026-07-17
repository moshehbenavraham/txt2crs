# SPDX-License-Identifier: MIT-0

"""Focused redaction for bounded public status messages.

This helper intentionally complements allowlisted event schemas. It is not a
reason to collect arbitrary prompts, provider bodies, or credentials.
"""

import re

_HOME_PATH_PATTERN = re.compile(r"(?:(?:/home|/Users)/[^/\s]+/[^\s,;]*)")
_BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]+")
_SECRET_PATTERN = re.compile(r"(?i)\b(?:sk|token|secret|key)[-_][A-Za-z0-9_-]{6,}")


def sanitize_public_text(value: str, *, maximum_length: int = 500) -> str:
    """Redact common secret/path forms and clamp browser-visible text."""

    sanitized_value = _HOME_PATH_PATTERN.sub("[PRIVATE_PATH]", value)
    sanitized_value = _BEARER_PATTERN.sub("Bearer [REDACTED]", sanitized_value)
    sanitized_value = _SECRET_PATTERN.sub("[REDACTED]", sanitized_value)
    sanitized_value = " ".join(sanitized_value.split())
    return sanitized_value[:maximum_length]
