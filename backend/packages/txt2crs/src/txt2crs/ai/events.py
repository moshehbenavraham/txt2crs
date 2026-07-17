# SPDX-License-Identifier: MIT-0

"""Bounded provider-neutral runtime event vocabulary."""

from enum import StrEnum
from hashlib import sha256

from pydantic import Field

from txt2crs.domain.models import Identifier, StrictContract


class RuntimeEventType(StrEnum):
    """Events retained from a model turn without hidden reasoning."""

    turn_started = "turn_started"
    assistant_progress = "assistant_progress"
    tool_started = "tool_started"
    tool_completed = "tool_completed"
    usage_updated = "usage_updated"
    turn_completed = "turn_completed"
    turn_failed = "turn_failed"
    turn_cancelled = "turn_cancelled"


class RuntimeEvent(StrictContract):
    """One safe event suitable for private-to-public projection."""

    event_id: Identifier
    event_type: RuntimeEventType
    stage: Identifier
    safe_message: str = Field(max_length=500)
    tool_call_id: Identifier | None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)


def stable_tool_call_id(
    *,
    thread_id: str,
    turn_id: str,
    provider_call_id: str,
    tool_name: str,
) -> str:
    """Derive stable local identity without exposing provider request IDs."""

    identity_material = "\n".join(
        [thread_id, turn_id, provider_call_id, tool_name]
    ).encode("utf-8")
    return f"call-{sha256(identity_material).hexdigest()[:24]}"
