# SPDX-License-Identifier: MIT-0

"""Tests for deterministic research-tool call guardrails."""

from txt2crs.ai.tool_guardrails import (
    ToolCallGuardrailConfig,
    ToolCallGuardrailController,
)


def test_equivalent_nested_arguments_have_one_canonical_signature() -> None:
    """Dictionary order must not let a model evade repeated-call detection."""

    guardrail = ToolCallGuardrailController(
        ToolCallGuardrailConfig(maximum_exact_repeats=1, maximum_failure_repeats=1)
    )

    first = guardrail.inspect(
        tool_name="research_search",
        arguments={"query": "python", "filters": {"language": "en", "year": 2026}},
    )
    second = guardrail.inspect(
        tool_name="research_search",
        arguments={"filters": {"year": 2026, "language": "en"}, "query": "python"},
    )

    assert first.allowed is True
    assert second.allowed is False
    assert second.reason_code == "repeated_equivalent_call"


def test_failure_repeats_are_counted_separately_from_successes() -> None:
    """A repeatedly failing extraction should stop sooner than useful new work."""

    guardrail = ToolCallGuardrailController(
        ToolCallGuardrailConfig(maximum_exact_repeats=3, maximum_failure_repeats=1)
    )
    arguments = {"url": "https://example.com/course"}

    assert guardrail.inspect("research_extract", arguments).allowed is True
    guardrail.record_result(
        tool_name="research_extract",
        arguments=arguments,
        succeeded=False,
    )
    rejected_call = guardrail.inspect("research_extract", arguments)

    assert rejected_call.allowed is False
    assert rejected_call.reason_code == "repeated_failed_call"


def test_only_the_two_research_tools_are_allowed() -> None:
    """Shell, filesystem, and arbitrary network tools remain unavailable."""

    guardrail = ToolCallGuardrailController(ToolCallGuardrailConfig())

    rejected_call = guardrail.inspect(
        tool_name="shell_execute",
        arguments={"command": "env"},
    )

    assert rejected_call.allowed is False
    assert rejected_call.reason_code == "tool_not_allowed"
