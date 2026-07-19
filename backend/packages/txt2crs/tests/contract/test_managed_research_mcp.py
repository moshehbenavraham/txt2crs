# SPDX-License-Identifier: MIT-0

"""Contract tests for the managed two-tool loopback research server."""

import socket
from collections.abc import Sequence
from threading import Event

import pytest

from txt2crs.research.managed_mcp import (
    ManagedResearchMcpServer,
    ResearchMcpBindError,
    ResearchMcpLifecycleError,
    ResearchMcpReadinessTimeoutError,
    ResearchMcpShutdownError,
    ResearchMcpStartupError,
    ResearchMcpToolContractError,
)
from txt2crs.research.mcp_server import ResearchMcpApplication
from txt2crs.research.models import (
    ExtractRequest,
    ExtractResult,
    SearchRequest,
    SearchResult,
)


class EmptyResearchService:
    """Return strict empty results without making external network calls."""

    def search(self, request: SearchRequest) -> SearchResult:
        """Return a result tied to the exact validated query."""

        return SearchResult(query=request.query, hits=[])

    def extract(self, request: ExtractRequest) -> ExtractResult:
        """Return no documents for the validated URL list."""

        assert request.urls
        return ExtractResult(documents=[], failed_urls=list(request.urls))


class ScriptedServerController:
    """Small Uvicorn-shaped controller for deterministic lifecycle failures."""

    def __init__(
        self,
        *,
        starts: bool = True,
        startup_error: BaseException | None = None,
        obeys_shutdown: bool = True,
        exits_after_start: bool = False,
    ) -> None:
        self.started = False
        self.should_exit = False
        self._starts = starts
        self._startup_error = startup_error
        self._obeys_shutdown = obeys_shutdown
        self._exits_after_start = exits_after_start
        self._release = Event()
        self.stopped = Event()
        self.run_calls = 0

    def run(self, *, sockets: Sequence[socket.socket]) -> None:
        """Report readiness or a scripted failure, then model a server loop."""

        try:
            assert len(sockets) == 1
            self.run_calls += 1
            if self._startup_error is not None:
                raise self._startup_error
            self.started = self._starts
            if self._exits_after_start:
                return
            while not self._release.wait(timeout=0.001):
                if self.should_exit and self._obeys_shutdown:
                    return
        finally:
            self.stopped.set()

    def release(self) -> None:
        """Allow a shutdown-ignoring fake thread to finish after its assertion."""

        self._release.set()


def research_application() -> ResearchMcpApplication:
    """Build the exact static two-tool application used by every scenario."""

    return ResearchMcpApplication(EmptyResearchService(), port=0)


def test_managed_server_publishes_url_only_while_real_listener_is_ready() -> None:
    """The provider cannot receive a URL before readiness or after cleanup."""

    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=0,
        startup_timeout_seconds=2,
        shutdown_timeout_seconds=2,
        poll_interval_seconds=0.005,
    )

    with pytest.raises(ResearchMcpLifecycleError, match="not ready"):
        _ = server.url

    with server as ready_server:
        ready_url = ready_server.url
        ready_port = int(ready_url.split(":")[2].split("/")[0])
        with socket.create_connection(("127.0.0.1", ready_port), timeout=1):
            pass
        assert ready_server.registered_tool_names == (
            "research_search",
            "research_extract",
        )

    with pytest.raises(ResearchMcpLifecycleError, match="not ready"):
        _ = server.url
    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", ready_port), timeout=0.1)

    # Cleanup is deliberately idempotent because both an ExitStack and an
    # application shutdown hook may defensively call it.
    server.close()


@pytest.mark.parametrize("host", ["0.0.0.0", "localhost"])
def test_managed_server_rejects_non_explicit_loopback_bind_before_start(
    host: str,
) -> None:
    """The research MCP accepts only numeric loopback bind addresses."""

    with pytest.raises(ValueError, match="loopback"):
        ManagedResearchMcpServer(
            research_application(),
            host=host,
            port=8765,
        )


def test_managed_server_reports_bind_conflict_without_starting_thread() -> None:
    """Binding in the calling thread makes address conflicts deterministic."""

    occupied_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    occupied_socket.bind(("127.0.0.1", 0))
    occupied_socket.listen(1)
    occupied_port = int(occupied_socket.getsockname()[1])
    controller = ScriptedServerController()
    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=occupied_port,
        server_controller_factory=lambda _asgi_app: controller,
    )

    try:
        with pytest.raises(ResearchMcpBindError, match="bind"):
            server.start()
    finally:
        occupied_socket.close()

    assert controller.run_calls == 0


def test_managed_server_translates_background_startup_failure() -> None:
    """Raw Uvicorn or thread errors never cross the package boundary."""

    controller = ScriptedServerController(
        startup_error=RuntimeError("private /tmp/server traceback")
    )
    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=0,
        server_controller_factory=lambda _asgi_app: controller,
    )

    with pytest.raises(ResearchMcpStartupError) as captured_error:
        server.start()

    assert "/tmp/server" not in str(captured_error.value)
    assert server.is_running is False


def test_managed_server_closes_prebound_socket_when_controller_build_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Synchronous controller construction is a typed cleanup-safe startup."""

    private_error = "private controller factory /tmp/config failure"
    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=0,
        server_controller_factory=lambda _asgi_app: (_ for _ in ()).throw(
            RuntimeError(private_error)
        ),
    )
    bound_sockets: list[socket.socket] = []
    original_bind_listener = server._bind_listener

    def capture_bound_listener() -> socket.socket:
        listener_socket = original_bind_listener()
        bound_sockets.append(listener_socket)
        return listener_socket

    monkeypatch.setattr(server, "_bind_listener", capture_bound_listener)

    with pytest.raises(ResearchMcpStartupError) as error_info:
        server.start()

    assert private_error not in str(error_info.value)
    assert len(bound_sockets) == 1
    assert bound_sockets[0].fileno() == -1
    assert server.is_running is False


def test_managed_server_never_publishes_a_controller_that_exited_after_start() -> None:
    """A transient started flag cannot make a dead listener provider-visible."""

    controller = ScriptedServerController(exits_after_start=True)
    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=0,
        server_controller_factory=lambda _asgi_app: controller,
    )

    with pytest.raises(ResearchMcpStartupError, match="startup"):
        server.start()

    with pytest.raises(ResearchMcpLifecycleError, match="not ready"):
        _ = server.url
    assert server.is_running is False


def test_managed_server_translates_registry_inspection_failure_and_stops(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A broken FastMCP registry read cannot leak its listener or raw error."""

    application = research_application()
    private_error = "private registry /home/owner failure"

    def fail_registry_inspection() -> tuple[str, ...]:
        raise RuntimeError(private_error)

    monkeypatch.setattr(
        application,
        "registered_tool_names",
        fail_registry_inspection,
    )
    server = ManagedResearchMcpServer(
        application,
        host="127.0.0.1",
        port=0,
        startup_timeout_seconds=2,
        shutdown_timeout_seconds=2,
        poll_interval_seconds=0.005,
    )

    try:
        with pytest.raises(ResearchMcpToolContractError) as error_info:
            server.start()
    finally:
        server.close()

    assert private_error not in str(error_info.value)
    assert server.is_running is False


def test_managed_server_closes_listener_after_unexpected_ready_exit() -> None:
    """An independently stopped server cannot leave a bound stale endpoint."""

    controller = ScriptedServerController()
    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=0,
        startup_timeout_seconds=0.1,
        shutdown_timeout_seconds=0.1,
        poll_interval_seconds=0.001,
        server_controller_factory=lambda _asgi_app: controller,
    )
    server.start()
    listener_socket = server._listener_socket
    server_thread = server._server_thread
    assert listener_socket is not None
    assert server_thread is not None

    controller.release()
    assert controller.stopped.wait(timeout=0.1)
    server_thread.join(timeout=0.1)

    with pytest.raises(ResearchMcpLifecycleError, match="not ready"):
        _ = server.url
    assert server_thread.is_alive() is False
    assert listener_socket.fileno() == -1
    server.close()


def test_managed_server_times_out_and_joins_a_non_ready_controller() -> None:
    """A child that never reports ready is stopped within the finite deadline."""

    controller = ScriptedServerController(starts=False)
    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=0,
        startup_timeout_seconds=0.02,
        shutdown_timeout_seconds=0.1,
        poll_interval_seconds=0.001,
        server_controller_factory=lambda _asgi_app: controller,
    )

    with pytest.raises(ResearchMcpReadinessTimeoutError, match="ready"):
        server.start()

    assert controller.should_exit is True
    assert server.is_running is False


def test_managed_server_rejects_registry_drift_and_closes_listener(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Even a running server is unusable when FastMCP exposes another tool."""

    application = research_application()
    monkeypatch.setattr(
        application,
        "registered_tool_names",
        lambda: ("research_search", "research_extract", "shell_execute"),
    )
    server = ManagedResearchMcpServer(
        application,
        host="127.0.0.1",
        port=0,
        startup_timeout_seconds=2,
        shutdown_timeout_seconds=2,
        poll_interval_seconds=0.005,
    )

    with pytest.raises(ResearchMcpToolContractError, match="tool"):
        server.start()

    assert server.is_running is False


def test_managed_server_reports_bounded_shutdown_failure_then_can_finish() -> None:
    """A stuck server is visible and can still be released by outer shutdown."""

    controller = ScriptedServerController(obeys_shutdown=False)
    server = ManagedResearchMcpServer(
        research_application(),
        host="127.0.0.1",
        port=0,
        startup_timeout_seconds=0.1,
        shutdown_timeout_seconds=0.01,
        poll_interval_seconds=0.001,
        server_controller_factory=lambda _asgi_app: controller,
    )
    server.start()
    ready_port = int(server.url.split(":")[2].split("/")[0])

    with pytest.raises(ResearchMcpShutdownError, match="stop"):
        server.close()

    with pytest.raises(OSError):
        socket.create_connection(("127.0.0.1", ready_port), timeout=0.1)
    controller.release()
    server.close()
    assert server.is_running is False
