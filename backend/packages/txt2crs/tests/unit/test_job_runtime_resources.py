# SPDX-License-Identifier: MIT-0

"""Tests for fresh job state and reverse-ordered provider resource cleanup."""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest

from tests.factories import valid_generation_request
from txt2crs.ai.job_runtime import (
    JobRuntimeResources,
    JobRuntimeResourcesFactory,
    ManagedProviderSessionFactory,
)
from txt2crs.ai.model_policy import Gpt56ModelPolicy
from txt2crs.ai.runtime import CancellationToken, CodexAdapterResult, TurnRequest


class RecordingCodexAdapter:
    """Minimal closeable adapter that records its resource lifetime."""

    def __init__(
        self,
        lifecycle_events: list[str],
        *,
        fail_close: bool = False,
        account_type: str = "chatgpt",
    ) -> None:
        self._lifecycle_events = lifecycle_events
        self._fail_close = fail_close
        self._account_type = account_type
        self._lifecycle_events.append("codex.enter")

    def inspect_account_type(self) -> str:
        """Return the subscription account type required by the runtime."""

        return self._account_type

    def list_model_ids(self) -> tuple[str, ...]:
        """Return the exact configured GPT-5.6 alias."""

        return ("gpt-5.6",)

    def run_turn(
        self,
        *,
        request: TurnRequest,
        output_schema: dict[str, Any] | None,
        cancellation: CancellationToken,
    ) -> CodexAdapterResult:
        """The lifecycle tests do not need to execute a real turn."""

        raise AssertionError("Provider lifecycle tests must not run a model turn.")

    def close(self) -> None:
        """Record that Codex closes before the MCP listener."""

        self._lifecycle_events.append("codex.exit")
        if self._fail_close:
            raise RuntimeError("private adapter cleanup failure")


class ReadyResearchMcp:
    """Narrow managed-MCP value yielded after its context is ready."""

    url = "http://127.0.0.1:8765/mcp"


@contextmanager
def recording_value_context[ValueType](
    *,
    name: str,
    value: ValueType,
    lifecycle_events: list[str],
    fail_exit: bool = False,
) -> Iterator[ValueType]:
    """Record deterministic enter/exit order for one managed dependency."""

    lifecycle_events.append(f"{name}.enter")
    try:
        yield value
    finally:
        lifecycle_events.append(f"{name}.exit")
        if fail_exit:
            raise RuntimeError(f"private {name} cleanup failure")


def provider_session_factory(
    *,
    tmp_path: Path,
    lifecycle_events: list[str],
    fail_codex_construction: bool = False,
    fail_codex_close: bool = False,
    fail_mcp_exit: bool = False,
    account_type: str = "chatgpt",
) -> ManagedProviderSessionFactory:
    """Compose recording context factories around the production owner."""

    worker_directory = tmp_path / "worker"

    def temporary_worker_context() -> Any:
        return recording_value_context(
            name="temporary",
            value=worker_directory,
            lifecycle_events=lifecycle_events,
        )

    def http_client_context() -> Any:
        return recording_value_context(
            name="http",
            value=object(),
            lifecycle_events=lifecycle_events,
        )

    def research_mcp_context(
        _resources: JobRuntimeResources,
        _http_client: object,
    ) -> Any:
        return recording_value_context(
            name="mcp",
            value=ReadyResearchMcp(),
            lifecycle_events=lifecycle_events,
            fail_exit=fail_mcp_exit,
        )

    def codex_adapter_factory(
        _worker_directory: Path,
        _research_mcp_connection: object,
    ) -> RecordingCodexAdapter:
        if fail_codex_construction:
            raise RuntimeError("private adapter construction failure")
        return RecordingCodexAdapter(
            lifecycle_events,
            fail_close=fail_codex_close,
            account_type=account_type,
        )

    return ManagedProviderSessionFactory(
        temporary_worker_context_factory=temporary_worker_context,
        http_client_context_factory=http_client_context,
        research_mcp_context_factory=research_mcp_context,
        codex_adapter_factory=codex_adapter_factory,
        model_policy=Gpt56ModelPolicy(),
    )


def test_job_runtime_resources_are_fresh_and_derived_from_stored_limits() -> None:
    """No mutable counter or cancellation flag may cross job boundaries."""

    execution_profile = valid_generation_request().execution_profile
    factory = JobRuntimeResourcesFactory()

    first_resources = factory.create(execution_profile)
    second_resources = factory.create(execution_profile)
    first_resources.budget.reserve_turn()
    first_resources.cancellation.cancel()

    assert first_resources is not second_resources
    assert first_resources.budget is not second_resources.budget
    assert first_resources.cancellation is not second_resources.cancellation
    assert first_resources.budget.limits.maximum_turns == (
        execution_profile.run_limits.maximum_turns
    )
    assert first_resources.budget.snapshot().turns == 1
    assert second_resources.budget.snapshot().turns == 0
    assert first_resources.cancellation.is_cancelled is True
    assert second_resources.cancellation.is_cancelled is False


def test_provider_session_closes_codex_mcp_http_and_temporary_in_reverse_order(
    tmp_path: Path,
) -> None:
    """Normal completion unwinds the complete provider ownership stack."""

    lifecycle_events: list[str] = []
    resources = JobRuntimeResourcesFactory().create(
        valid_generation_request().execution_profile
    )
    factory = provider_session_factory(
        tmp_path=tmp_path,
        lifecycle_events=lifecycle_events,
    )

    with factory.open(resources) as provider_session:
        assert provider_session.resources is resources
        assert provider_session.worker_directory == tmp_path / "worker"
        assert provider_session.research_mcp.url.endswith("/mcp")

    assert lifecycle_events == [
        "temporary.enter",
        "http.enter",
        "mcp.enter",
        "codex.enter",
        "codex.exit",
        "mcp.exit",
        "http.exit",
        "temporary.exit",
    ]


def test_provider_session_unwinds_partial_construction_failure(tmp_path: Path) -> None:
    """A failed Codex launch still closes MCP, HTTP, and temporary resources."""

    lifecycle_events: list[str] = []
    resources = JobRuntimeResourcesFactory().create(
        valid_generation_request().execution_profile
    )
    factory = provider_session_factory(
        tmp_path=tmp_path,
        lifecycle_events=lifecycle_events,
        fail_codex_construction=True,
    )

    with pytest.raises(RuntimeError, match="construction"):
        with factory.open(resources):
            raise AssertionError("A failed adapter must never yield a session.")

    assert lifecycle_events == [
        "temporary.enter",
        "http.enter",
        "mcp.enter",
        "mcp.exit",
        "http.exit",
        "temporary.exit",
    ]


def test_provider_session_rejects_not_ready_codex_before_yield(tmp_path: Path) -> None:
    """A constructed API-key adapter cannot become a subscription session."""

    lifecycle_events: list[str] = []
    resources = JobRuntimeResourcesFactory().create(
        valid_generation_request().execution_profile
    )
    factory = provider_session_factory(
        tmp_path=tmp_path,
        lifecycle_events=lifecycle_events,
        account_type="api_key",
    )

    with pytest.raises(RuntimeError, match="not ready"):
        with factory.open(resources):
            raise AssertionError("An unavailable runtime must never yield.")

    assert lifecycle_events == [
        "temporary.enter",
        "http.enter",
        "mcp.enter",
        "codex.enter",
        "codex.exit",
        "mcp.exit",
        "http.exit",
        "temporary.exit",
    ]


@pytest.mark.parametrize("exit_kind", ["runtime_failure", "cancellation", "shutdown"])
def test_provider_session_cleans_every_outer_exit(
    tmp_path: Path,
    exit_kind: str,
) -> None:
    """Provider ownership is independent from the caller's exit reason."""

    lifecycle_events: list[str] = []
    resources = JobRuntimeResourcesFactory().create(
        valid_generation_request().execution_profile
    )
    factory = provider_session_factory(
        tmp_path=tmp_path,
        lifecycle_events=lifecycle_events,
    )

    with pytest.raises(RuntimeError):
        with factory.open(resources):
            if exit_kind == "cancellation":
                resources.cancellation.cancel()
                resources.cancellation.raise_if_cancelled()
            raise RuntimeError(exit_kind)

    assert lifecycle_events[-4:] == [
        "codex.exit",
        "mcp.exit",
        "http.exit",
        "temporary.exit",
    ]


def test_provider_session_preserves_primary_error_when_adapter_close_fails(
    tmp_path: Path,
) -> None:
    """Cleanup failure is visible without replacing the generation failure."""

    lifecycle_events: list[str] = []
    resources = JobRuntimeResourcesFactory().create(
        valid_generation_request().execution_profile
    )
    factory = provider_session_factory(
        tmp_path=tmp_path,
        lifecycle_events=lifecycle_events,
        fail_codex_close=True,
    )

    with pytest.raises(RuntimeError, match="primary generation failure") as error_info:
        with factory.open(resources):
            raise RuntimeError("primary generation failure")

    assert "private adapter cleanup failure" not in str(error_info.value)
    assert lifecycle_events[-4:] == [
        "codex.exit",
        "mcp.exit",
        "http.exit",
        "temporary.exit",
    ]


def test_provider_session_preserves_primary_error_when_mcp_exit_fails(
    tmp_path: Path,
) -> None:
    """An external context exit cannot replace the generation failure."""

    lifecycle_events: list[str] = []
    resources = JobRuntimeResourcesFactory().create(
        valid_generation_request().execution_profile
    )
    factory = provider_session_factory(
        tmp_path=tmp_path,
        lifecycle_events=lifecycle_events,
        fail_mcp_exit=True,
    )

    with pytest.raises(RuntimeError, match="primary generation failure") as error_info:
        with factory.open(resources):
            raise RuntimeError("primary generation failure")

    assert "private mcp cleanup failure" not in str(error_info.value)
    assert lifecycle_events[-4:] == [
        "codex.exit",
        "mcp.exit",
        "http.exit",
        "temporary.exit",
    ]
