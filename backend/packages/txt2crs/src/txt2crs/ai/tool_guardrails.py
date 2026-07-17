# SPDX-License-Identifier: MIT

"""Prevent unavailable tools and repeated research-tool loops.

The canonical-signature idea was adapted from Hermes' MIT-licensed
``agent/tool_guardrails.py`` at commit
``0f102fa4dc04b7dfdab048169aaaa640d09d7523``. The controller and its types are
purpose-built for txt2crs' two research tools.
"""

import json
from dataclasses import dataclass
from hashlib import sha256
from threading import Lock
from typing import Any

ALLOWED_RESEARCH_TOOLS = frozenset({"research_search", "research_extract"})


def canonical_tool_arguments(arguments: dict[str, Any]) -> str:
    """Serialize nested arguments deterministically for repeat detection."""

    return json.dumps(
        arguments,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def tool_call_signature(tool_name: str, arguments: dict[str, Any]) -> str:
    """Return a compact, stable digest for one named tool call."""

    canonical_call = f"{tool_name}\n{canonical_tool_arguments(arguments)}"
    return sha256(canonical_call.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class ToolCallGuardrailConfig:
    """Maximum equivalent attempts permitted for one tool signature."""

    maximum_exact_repeats: int = 2
    maximum_failure_repeats: int = 1

    def __post_init__(self) -> None:
        if self.maximum_exact_repeats < 1:
            raise ValueError("maximum_exact_repeats must be at least one.")
        if self.maximum_failure_repeats < 1:
            raise ValueError("maximum_failure_repeats must be at least one.")


@dataclass(frozen=True, slots=True)
class ToolGuardrailDecision:
    """Explicit allow/deny decision recorded before a tool executes."""

    allowed: bool
    reason_code: str
    signature: str


class ToolCallGuardrailController:
    """Track equivalent calls and failures safely across concurrent workers."""

    def __init__(self, config: ToolCallGuardrailConfig) -> None:
        self._config = config
        self._attempt_counts: dict[str, int] = {}
        self._failure_counts: dict[str, int] = {}
        self._lock = Lock()

    def inspect(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolGuardrailDecision:
        """Check and reserve a call attempt before any side effect occurs."""

        signature = tool_call_signature(tool_name, arguments)
        if tool_name not in ALLOWED_RESEARCH_TOOLS:
            return ToolGuardrailDecision(
                allowed=False,
                reason_code="tool_not_allowed",
                signature=signature,
            )

        with self._lock:
            failure_count = self._failure_counts.get(signature, 0)
            if failure_count >= self._config.maximum_failure_repeats:
                return ToolGuardrailDecision(
                    allowed=False,
                    reason_code="repeated_failed_call",
                    signature=signature,
                )

            attempt_count = self._attempt_counts.get(signature, 0)
            if attempt_count >= self._config.maximum_exact_repeats:
                return ToolGuardrailDecision(
                    allowed=False,
                    reason_code="repeated_equivalent_call",
                    signature=signature,
                )

            self._attempt_counts[signature] = attempt_count + 1
            return ToolGuardrailDecision(
                allowed=True,
                reason_code="allowed",
                signature=signature,
            )

    def record_result(
        self,
        *,
        tool_name: str,
        arguments: dict[str, Any],
        succeeded: bool,
    ) -> None:
        """Record a typed result without inspecting provider error text."""

        if succeeded:
            return
        signature = tool_call_signature(tool_name, arguments)
        with self._lock:
            self._failure_counts[signature] = self._failure_counts.get(signature, 0) + 1
