# SPDX-License-Identifier: MIT-0

"""Contract tests for the concrete official Python SDK adapter."""

import json
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from threading import Event, Thread
from time import sleep
from types import SimpleNamespace
from typing import Any

import pytest

from txt2crs.ai.codex_runtime import (
    OfficialCodexSdkAdapter,
    ResearchMcpConnection,
)
from txt2crs.ai.errors import RuntimeTimeoutError
from txt2crs.ai.events import RuntimeEvent, RuntimeEventType
from txt2crs.ai.runtime import CancellationToken, TurnRequest


@dataclass(slots=True)
class FakeAccountRoot:
    """SDK-like account root."""

    type: str


@dataclass(slots=True)
class FakeAccount:
    """SDK-like root wrapper."""

    root: FakeAccountRoot


@dataclass(slots=True)
class FakeAccountResponse:
    """SDK-like account response."""

    account: FakeAccount | None


@dataclass(slots=True)
class FakeModel:
    """SDK-like model entry."""

    model: str


@dataclass(slots=True)
class FakeModelsResponse:
    """SDK-like model-list response."""

    data: list[FakeModel]


@dataclass(slots=True)
class FakeTokenBreakdown:
    """SDK-like token usage."""

    input_tokens: int
    output_tokens: int


@dataclass(slots=True)
class FakeUsage:
    """SDK-like usage wrapper."""

    last: FakeTokenBreakdown


@dataclass(slots=True)
class FakeTurnResult:
    """SDK-like completed turn result."""

    status: object
    final_response: str | None
    usage: FakeUsage | None
    id: str = "turn-1"


class FakeTurnStatus(Enum):
    """Match the official generated Enum string/value distinction."""

    completed = "completed"


class FakeTurnHandle:
    """SDK-like controllable handle with optional blocking behavior."""

    def __init__(self, result: FakeTurnResult, *, block: bool = False) -> None:
        self.id = result.id
        self._result = result
        self._block = block
        self.interrupted = Event()

    def run(self) -> FakeTurnResult:
        """Return immediately or wait until interrupted."""

        if self._block:
            self.interrupted.wait(timeout=2)
        return self._result

    def interrupt(self) -> None:
        """Record provider interruption and release the fake turn."""

        self.interrupted.set()


class FakeStreamingTurnHandle(FakeTurnHandle):
    """SDK-like handle that yields typed-shape notifications."""

    def __init__(
        self,
        result: FakeTurnResult,
        notifications: tuple[SimpleNamespace, ...],
    ) -> None:
        super().__init__(result)
        self._notifications = notifications

    def stream(self) -> Iterator[SimpleNamespace]:
        """Yield the scripted notification sequence."""

        yield from self._notifications


class FakeSdkThread:
    """SDK-like thread that records turn policy arguments."""

    def __init__(self, handle: FakeTurnHandle) -> None:
        self.id = "thread-1"
        self.handle = handle
        self.received_prompt: str | None = None
        self.received_schema: dict[str, Any] | None = None

    def turn(
        self,
        prompt: str,
        *,
        output_schema: dict[str, Any] | None,
        model: str,
    ) -> FakeTurnHandle:
        """Record the schema-constrained turn."""

        assert model == "gpt-5.6"
        self.received_prompt = prompt
        self.received_schema = output_schema
        return self.handle


class FakeSdkClient:
    """SDK-like client used without importing SDK internals into tests."""

    def __init__(self, thread: FakeSdkThread, *, account_type: str = "chatgpt") -> None:
        self.thread = thread
        self.account_type = account_type
        self.closed = False
        self.account_refresh_requested = False
        self.thread_start_arguments: dict[str, Any] = {}

    def account(self, *, refresh_token: bool = False) -> FakeAccountResponse:
        """Return an SDK-shaped account and record delegated refresh."""

        self.account_refresh_requested = refresh_token
        return FakeAccountResponse(
            account=FakeAccount(root=FakeAccountRoot(type=self.account_type))
        )

    def models(self) -> FakeModelsResponse:
        """Return one entitled model."""

        return FakeModelsResponse(data=[FakeModel(model="gpt-5.6")])

    def thread_start(self, **arguments: Any) -> FakeSdkThread:
        """Record isolation policy and return the fake thread."""

        self.thread_start_arguments = arguments
        return self.thread

    def close(self) -> None:
        """Record cleanup."""

        self.closed = True


def turn_request(*, timeout_seconds: float = 1) -> TurnRequest:
    """Build the SDK adapter's trusted/untrusted prompt fixture."""

    return TurnRequest(
        request_id="request-1",
        stage="write_lessons",
        model_id="gpt-5.6",
        prompt_version="write-v1",
        trusted_instructions="Return the course schema.",
        untrusted_data="<learner_input>Variables</learner_input>",
        timeout_seconds=timeout_seconds,
    )


def successful_client(*, block: bool = False) -> FakeSdkClient:
    """Return an SDK double with one JSON result."""

    result = FakeTurnResult(
        status=FakeTurnStatus.completed,
        final_response=json.dumps({"course_id": "course-1"}),
        usage=FakeUsage(last=FakeTokenBreakdown(10, 5)),
    )
    return FakeSdkClient(FakeSdkThread(FakeTurnHandle(result, block=block)))


def test_adapter_projects_account_models_schema_output_and_usage() -> None:
    """Official SDK shapes stop at the provider-neutral adapter result."""

    sdk_client = successful_client()
    adapter = OfficialCodexSdkAdapter(client=sdk_client, polling_seconds=0.01)

    assert adapter.inspect_account_type() == "chatgpt"
    assert sdk_client.account_refresh_requested is True
    assert adapter.list_model_ids() == ("gpt-5.6",)
    result = adapter.run_turn(
        request=turn_request(),
        output_schema={"type": "object"},
        cancellation=CancellationToken(),
    )

    assert result.output == {"course_id": "course-1"}
    assert result.thread_id == "thread-1"
    assert result.turn_id == "turn-1"
    assert result.input_tokens == 10
    assert result.output_tokens == 5
    assert sdk_client.thread.received_schema == {"type": "object"}
    assert "untrusted data" in (sdk_client.thread.received_prompt or "")
    assert sdk_client.thread_start_arguments["ephemeral"] is True
    adapter.close()
    assert sdk_client.closed is True


def test_adapter_interrupts_on_cancellation() -> None:
    """Cancellation invokes the SDK turn interrupt and returns promptly."""

    sdk_client = successful_client(block=True)
    adapter = OfficialCodexSdkAdapter(client=sdk_client, polling_seconds=0.01)
    cancellation = CancellationToken()

    def cancel_after_delay() -> None:
        """Request cancellation after the adapter has started polling."""

        sleep(0.03)
        cancellation.cancel()

    cancellation_thread = Thread(target=cancel_after_delay)
    cancellation_thread.start()
    with pytest.raises(RuntimeError, match="cancelled"):
        adapter.run_turn(
            request=turn_request(timeout_seconds=1),
            output_schema={"type": "object"},
            cancellation=cancellation,
        )
    cancellation_thread.join()

    assert sdk_client.thread.handle.interrupted.is_set()


def test_adapter_interrupts_on_deadline() -> None:
    """A provider that hangs cannot leave the local stage pending forever."""

    sdk_client = successful_client(block=True)
    adapter = OfficialCodexSdkAdapter(client=sdk_client, polling_seconds=0.005)

    with pytest.raises(RuntimeTimeoutError):
        adapter.run_turn(
            request=turn_request(timeout_seconds=0.02),
            output_schema={"type": "object"},
            cancellation=CancellationToken(),
        )

    assert sdk_client.thread.handle.interrupted.is_set()


def test_research_mcp_connection_allows_only_loopback_and_two_tools() -> None:
    """The app-server receives a required local server with a static allowlist."""

    connection = ResearchMcpConnection(
        url="http://127.0.0.1:8765/mcp",
        startup_timeout_seconds=5,
        tool_timeout_seconds=30,
    )

    overrides = connection.codex_config_overrides()

    assert 'mcp_servers.txt2crs_research.url="http://127.0.0.1:8765/mcp"' in (overrides)
    assert (
        "mcp_servers.txt2crs_research.enabled_tools="
        '["research_search","research_extract"]'
    ) in overrides
    assert "mcp_servers.txt2crs_research.required=true" in overrides
    assert not any("shell" in override for override in overrides)
    with pytest.raises(ValueError, match="loopback"):
        ResearchMcpConnection(url="https://research.example.com/mcp")


def test_adapter_config_clears_inherited_tools_and_uses_pinned_safe_defaults() -> None:
    """A newer user config cannot add tools or break the pinned app-server."""

    connection = ResearchMcpConnection(url="http://127.0.0.1:8765/mcp")

    overrides = OfficialCodexSdkAdapter.build_config_overrides(research_mcp=connection)
    no_research_overrides = OfficialCodexSdkAdapter.build_config_overrides(
        research_mcp=None
    )

    assert overrides[0] == "mcp_servers={}"
    assert 'model_reasoning_effort="high"' in overrides
    assert no_research_overrides == (
        "mcp_servers={}",
        'model_reasoning_effort="high"',
    )
    assert sum(override == "mcp_servers={}" for override in overrides) == 1


def test_adapter_projects_streamed_tool_progress_without_reasoning() -> None:
    """The official stream exposes stable safe progress and truthful usage."""

    turn_result = FakeTurnResult(
        status="completed",
        final_response='{"course_id":"course-1"}',
        usage=FakeUsage(last=FakeTokenBreakdown(10, 5)),
    )
    tool_item = SimpleNamespace(
        root=SimpleNamespace(
            type="mcpToolCall",
            id="provider-tool-call-1",
            server="txt2crs_research",
            tool="research_search",
        )
    )
    agent_item = SimpleNamespace(
        root=SimpleNamespace(
            type="agentMessage",
            id="message-1",
            text='{"course_id":"course-1"}',
            phase="finalAnswer",
        )
    )
    usage = SimpleNamespace(last=SimpleNamespace(input_tokens=10, output_tokens=5))
    completed_turn = SimpleNamespace(id="turn-1", status="completed", error=None)
    notifications = (
        SimpleNamespace(
            method="turn/started",
            payload=SimpleNamespace(turn=SimpleNamespace(id="turn-1")),
        ),
        SimpleNamespace(
            method="item/started",
            payload=SimpleNamespace(item=tool_item),
        ),
        SimpleNamespace(
            method="item/completed",
            payload=SimpleNamespace(item=tool_item),
        ),
        SimpleNamespace(
            method="thread/tokenUsage/updated",
            payload=SimpleNamespace(token_usage=usage),
        ),
        SimpleNamespace(
            method="item/completed",
            payload=SimpleNamespace(item=agent_item),
        ),
        SimpleNamespace(
            method="turn/completed",
            payload=SimpleNamespace(turn=completed_turn),
        ),
    )
    sdk_client = FakeSdkClient(
        FakeSdkThread(FakeStreamingTurnHandle(turn_result, notifications))
    )
    emitted_events: list[RuntimeEvent] = []
    adapter = OfficialCodexSdkAdapter(
        client=sdk_client,
        polling_seconds=0.01,
        event_sink=emitted_events.append,
    )

    result = adapter.run_turn(
        request=turn_request(),
        output_schema={"type": "object"},
        cancellation=CancellationToken(),
    )

    assert result.output == {"course_id": "course-1"}
    assert [event.event_type for event in emitted_events] == [
        RuntimeEventType.turn_started,
        RuntimeEventType.tool_started,
        RuntimeEventType.tool_completed,
        RuntimeEventType.usage_updated,
        RuntimeEventType.turn_completed,
    ]
    assert emitted_events[1].tool_call_id == emitted_events[2].tool_call_id
    serialized_events = "".join(event.model_dump_json() for event in emitted_events)
    assert "provider-tool-call-1" not in serialized_events
    assert "reasoning" not in serialized_events
