# SPDX-License-Identifier: MIT-0

"""Small local runtime error taxonomy with safe public messages."""

from dataclasses import dataclass
from enum import StrEnum


class RuntimeErrorCode(StrEnum):
    """Stable categories that drive retry and recovery policy."""

    reauthentication_required = "reauthentication_required"
    subscription_quota = "subscription_quota"
    retryable_transport = "retryable_transport"
    timeout = "cancellation_or_timeout"
    cancellation = "cancellation_or_timeout"
    tool_policy_rejection = "tool_policy_rejection"
    schema_or_quality_rejection = "schema_or_quality_rejection"
    permanent_provider = "permanent_provider"


class RuntimeTimeoutError(TimeoutError):
    """The local turn deadline elapsed and interruption was requested."""


@dataclass(frozen=True, slots=True)
class ClassifiedRuntimeError:
    """Private classification plus browser-safe recovery information."""

    code: RuntimeErrorCode
    retryable: bool
    public_message: str


def classify_runtime_error(error: Exception) -> ClassifiedRuntimeError:
    """Map known failure shapes without exposing raw provider bodies."""

    normalized_error = str(error).casefold()
    if isinstance(error, (TimeoutError, RuntimeTimeoutError)):
        return ClassifiedRuntimeError(
            code=RuntimeErrorCode.timeout,
            retryable=True,
            public_message=(
                "The operation exceeded its configured deadline and may be retried."
            ),
        )
    if any(marker in normalized_error for marker in ("cancelled", "canceled")):
        return ClassifiedRuntimeError(
            code=RuntimeErrorCode.cancellation,
            retryable=False,
            public_message="The model turn was cancelled.",
        )
    if any(
        marker in normalized_error
        for marker in ("429", "quota", "rate limit", "rate_limit")
    ):
        return ClassifiedRuntimeError(
            code=RuntimeErrorCode.subscription_quota,
            retryable=False,
            public_message="The subscription quota is unavailable or exhausted.",
        )
    if any(
        marker in normalized_error
        for marker in ("401", "authentication", "expired credential", "login")
    ):
        return ClassifiedRuntimeError(
            code=RuntimeErrorCode.reauthentication_required,
            retryable=False,
            public_message="ChatGPT reauthentication is required.",
        )
    if isinstance(error, (ConnectionError, OSError)):
        return ClassifiedRuntimeError(
            code=RuntimeErrorCode.retryable_transport,
            retryable=True,
            public_message="The model transport failed temporarily.",
        )
    if isinstance(error, ValueError) or any(
        marker in normalized_error for marker in ("schema", "validation", "quality")
    ):
        return ClassifiedRuntimeError(
            code=RuntimeErrorCode.schema_or_quality_rejection,
            retryable=False,
            public_message="Generated output failed validation.",
        )
    if "tool" in normalized_error and any(
        marker in normalized_error for marker in ("policy", "forbidden", "unsafe")
    ):
        return ClassifiedRuntimeError(
            code=RuntimeErrorCode.tool_policy_rejection,
            retryable=False,
            public_message="A research tool request was rejected by policy.",
        )
    return ClassifiedRuntimeError(
        code=RuntimeErrorCode.permanent_provider,
        retryable=False,
        public_message="The model provider could not complete the turn.",
    )
