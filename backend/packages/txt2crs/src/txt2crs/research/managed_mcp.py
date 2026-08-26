# SPDX-License-Identifier: MIT-0

"""Bounded ownership for the loopback research MCP listener."""

import socket
from collections.abc import Callable, Sequence
from ipaddress import ip_address
from threading import RLock, Thread
from time import monotonic, sleep
from types import TracebackType
from typing import Any, Literal, Protocol, Self, cast

import uvicorn

from txt2crs.research.mcp_server import ResearchMcpApplication

_EXPECTED_RESEARCH_TOOL_NAMES = ("research_search", "research_extract")


class ResearchMcpLifecycleError(RuntimeError):
    """Base error for managed listener ownership failures."""


class ResearchMcpBindError(ResearchMcpLifecycleError):
    """The configured loopback address could not be reserved."""


class ResearchMcpStartupError(ResearchMcpLifecycleError):
    """The ASGI server stopped or failed before reporting readiness."""


class ResearchMcpReadinessTimeoutError(ResearchMcpLifecycleError):
    """The ASGI server did not become ready before its finite deadline."""


class ResearchMcpToolContractError(ResearchMcpLifecycleError):
    """The ready MCP registry differs from the reviewed two-tool set."""


class ResearchMcpShutdownError(ResearchMcpLifecycleError):
    """The ASGI server thread did not stop before its finite deadline."""


class ServerController(Protocol):
    """Small Uvicorn-shaped surface used by deterministic lifecycle tests."""

    started: bool
    should_exit: bool

    def run(self, *, sockets: Sequence[socket.socket]) -> None:
        """Serve the ASGI app using an already-bound listener socket."""


ServerControllerFactory = Callable[[Any], ServerController]


def _default_server_controller(asgi_application: Any) -> ServerController:
    """Build the production Uvicorn controller with quiet bounded defaults."""

    return cast(
        ServerController,
        uvicorn.Server(
            uvicorn.Config(
                asgi_application,
                log_level="error",
                access_log=False,
                timeout_graceful_shutdown=5,
            )
        ),
    )


class ManagedResearchMcpServer:
    """Pre-bind, start, verify, publish, and close one loopback MCP server."""

    def __init__(
        self,
        application: ResearchMcpApplication,
        *,
        host: str = "127.0.0.1",
        port: int = 0,
        startup_timeout_seconds: float = 10,
        shutdown_timeout_seconds: float = 10,
        poll_interval_seconds: float = 0.01,
        server_controller_factory: ServerControllerFactory = (
            _default_server_controller
        ),
    ) -> None:
        if not _is_loopback_host(host):
            raise ValueError("Research MCP must bind to a loopback host.")
        if not 0 <= port <= 65_535:
            raise ValueError("Research MCP port must be between 0 and 65535.")
        if (
            startup_timeout_seconds <= 0
            or shutdown_timeout_seconds <= 0
            or poll_interval_seconds <= 0
        ):
            raise ValueError("Research MCP lifecycle timeouts must be positive.")

        self._application = application
        self._host = host
        self._port = port
        self._startup_timeout_seconds = startup_timeout_seconds
        self._shutdown_timeout_seconds = shutdown_timeout_seconds
        self._poll_interval_seconds = poll_interval_seconds
        self._server_controller_factory = server_controller_factory
        self._controller: ServerController | None = None
        self._listener_socket: socket.socket | None = None
        self._server_thread: Thread | None = None
        self._background_failed = False
        self._published_url: str | None = None
        self._lock = RLock()

    @property
    def url(self) -> str:
        """Return the endpoint only after readiness and registry verification."""

        with self._lock:
            if self._published_url is None:
                raise ResearchMcpLifecycleError("The research MCP server is not ready.")
            return self._published_url

    @property
    def registered_tool_names(self) -> tuple[str, ...]:
        """Return the verified actual MCP registry while ready."""

        with self._lock:
            if self._published_url is None:
                raise ResearchMcpLifecycleError("The research MCP server is not ready.")
            return self._application.registered_tool_names()

    @property
    def is_running(self) -> bool:
        """Return whether the owned background server thread is alive."""

        with self._lock:
            return self._server_thread is not None and self._server_thread.is_alive()

    def start(self) -> Self:
        """Start the pre-bound server and publish only a verified ready URL."""

        with self._lock:
            if self._published_url is not None:
                return self
            if self._server_thread is not None and self._server_thread.is_alive():
                raise ResearchMcpLifecycleError(
                    "The research MCP server is already starting."
                )

            listener_socket = self._bind_listener()
            try:
                asgi_application = (
                    self._application.create_streamable_http_application()
                )
                controller = self._server_controller_factory(asgi_application)
            except BaseException as construction_error:
                listener_socket.close()
                if isinstance(construction_error, Exception):
                    raise ResearchMcpStartupError(
                        "The research MCP server failed during startup."
                    ) from None
                raise
            self._listener_socket = listener_socket
            self._controller = controller
            self._background_failed = False
            server_thread = Thread(
                target=self._run_controller,
                args=(controller, listener_socket),
                name="txt2crs-research-mcp",
                daemon=True,
            )
            self._server_thread = server_thread
            try:
                server_thread.start()
            except BaseException as thread_error:
                self._discard_finished_resources()
                if isinstance(thread_error, Exception):
                    raise ResearchMcpStartupError(
                        "The research MCP server failed during startup."
                    ) from None
                raise

        startup_deadline = monotonic() + self._startup_timeout_seconds
        while monotonic() < startup_deadline:
            if not server_thread.is_alive():
                self._discard_finished_resources()
                raise ResearchMcpStartupError(
                    "The research MCP server failed during startup."
                ) from None
            if controller.started:
                # A controller may set ``started`` immediately before its
                # thread exits. Give that thread one bounded poll interval to
                # prove the ready state remains alive before publishing.
                server_thread.join(timeout=self._poll_interval_seconds)
                if not server_thread.is_alive():
                    self._discard_finished_resources()
                    raise ResearchMcpStartupError(
                        "The research MCP server failed during startup."
                    ) from None
                return self._verify_and_publish(listener_socket)
            sleep(self._poll_interval_seconds)

        self._stop_after_failed_start()
        raise ResearchMcpReadinessTimeoutError(
            "The research MCP server did not become ready in time."
        ) from None

    def close(self) -> None:
        """Stop, join, and release the listener; repeated calls are safe."""

        with self._lock:
            self._published_url = None
            controller = self._controller
            server_thread = self._server_thread
            if controller is None or server_thread is None:
                self._close_listener()
                self._controller = None
                self._server_thread = None
                return
            controller.should_exit = True

        server_thread.join(timeout=self._shutdown_timeout_seconds)
        if server_thread.is_alive():
            # The controller may be broken, but the listener remains owned by
            # this object and must stop accepting connections immediately.
            with self._lock:
                self._close_listener()
            raise ResearchMcpShutdownError(
                "The research MCP server did not stop in time."
            )
        self._discard_finished_resources()

    def __enter__(self) -> Self:
        """Start and return the ready managed server."""

        return self.start()

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        """Close without replacing an exception already raised by the caller."""

        del exception_type, traceback
        try:
            self.close()
        except ResearchMcpShutdownError as shutdown_error:
            if exception_value is None:
                raise
            exception_value.add_note(str(shutdown_error))
        return False

    def _bind_listener(self) -> socket.socket:
        """Reserve and listen on the configured address in the calling thread."""

        address_family = socket.AF_INET6 if ":" in self._host else socket.AF_INET
        listener_socket = socket.socket(address_family, socket.SOCK_STREAM)
        try:
            listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener_socket.bind((self._host, self._port))
            listener_socket.listen(128)
            listener_socket.setblocking(False)
        except OSError:
            listener_socket.close()
            raise ResearchMcpBindError(
                "The research MCP server could not bind its loopback address."
            ) from None
        return listener_socket

    def _run_controller(
        self,
        controller: ServerController,
        listener_socket: socket.socket,
    ) -> None:
        """Run the controller and retain only its private failure identity."""

        try:
            controller.run(sockets=[listener_socket])
        except BaseException:
            # Retain only a boolean. Holding the exception object would retain
            # its traceback and potentially provider-private local values.
            with self._lock:
                self._background_failed = True
        finally:
            # If Uvicorn stops after publication, revoke the provider-visible
            # URL immediately. Normal close already did this before joining,
            # while an unexpected stop must not leave a stale ready endpoint.
            with self._lock:
                if self._controller is controller:
                    self._published_url = None
                    self._close_listener()

    def _verify_and_publish(self, listener_socket: socket.socket) -> Self:
        """Verify actual tools and atomically make the listener discoverable."""

        with self._lock:
            server_thread = self._server_thread
            if server_thread is None or not server_thread.is_alive():
                self._discard_finished_resources()
                raise ResearchMcpStartupError(
                    "The research MCP server failed during startup."
                ) from None
            try:
                registered_tool_names = self._application.registered_tool_names()
            except Exception:
                registered_tool_names = None
            bound_port = int(listener_socket.getsockname()[1])
        if registered_tool_names is None:
            try:
                self.close()
            except ResearchMcpShutdownError:
                pass
            raise ResearchMcpToolContractError(
                "The research MCP tool registry could not be verified."
            ) from None
        if registered_tool_names != _EXPECTED_RESEARCH_TOOL_NAMES:
            try:
                self.close()
            except ResearchMcpShutdownError:
                pass
            raise ResearchMcpToolContractError(
                "The research MCP tool registry does not match its contract."
            ) from None

        url_host = f"[{self._host}]" if ":" in self._host else self._host
        with self._lock:
            if self._server_thread is None or not self._server_thread.is_alive():
                self._discard_finished_resources()
                raise ResearchMcpStartupError(
                    "The research MCP server failed during startup."
                ) from None
            self._published_url = f"http://{url_host}:{bound_port}/mcp"
        return self

    def _stop_after_failed_start(self) -> None:
        """Request shutdown and close resources after a readiness timeout."""

        with self._lock:
            controller = self._controller
            server_thread = self._server_thread
            if controller is not None:
                controller.should_exit = True
        if server_thread is not None:
            server_thread.join(timeout=self._shutdown_timeout_seconds)
        if server_thread is None or not server_thread.is_alive():
            self._discard_finished_resources()
        else:
            # Withhold the URL and close the owned listener even if a broken
            # controller ignores shutdown. The daemon thread retains no
            # provider-visible endpoint.
            with self._lock:
                self._published_url = None
                self._close_listener()

    def _discard_finished_resources(self) -> None:
        """Clear state and close the socket after its thread has finished."""

        with self._lock:
            self._published_url = None
            self._close_listener()
            self._controller = None
            self._server_thread = None
            self._background_failed = False

    def _close_listener(self) -> None:
        """Close the owned pre-bound listener exactly once."""

        if self._listener_socket is not None:
            self._listener_socket.close()
            self._listener_socket = None


def _is_loopback_host(host: str) -> bool:
    """Return whether the bind host is an explicit numeric loopback address."""

    try:
        return ip_address(host).is_loopback
    except ValueError:
        return False
