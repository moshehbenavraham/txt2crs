"""Direct ASGI tests for response-owned verified artifact cleanup."""

import asyncio
import time
from collections.abc import Iterator
from contextlib import AbstractContextManager
from types import TracebackType
from typing import cast

import pytest
from starlette.requests import ClientDisconnect
from starlette.types import Message, Scope

from app.api.artifact_response import (
    ArtifactStreamingResponse,
    EnteredArtifactBody,
)


class _CountingArtifactContext(AbstractContextManager[Iterator[bytes]]):
    """Expose deterministic chunks while counting context lifecycle calls."""

    def __init__(
        self,
        iterator: Iterator[bytes],
        *,
        entry_error: BaseException | None = None,
        exit_error: BaseException | None = None,
    ) -> None:
        self.iterator = iterator
        self.entry_error = entry_error
        self.exit_error = exit_error
        self.enter_count = 0
        self.exit_count = 0

    def __enter__(self) -> Iterator[bytes]:
        self.enter_count += 1
        if self.entry_error is not None:
            raise self.entry_error
        return self.iterator

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        del exception_type, exception_value, traceback
        self.exit_count += 1
        if self.exit_error is not None:
            raise self.exit_error


class _FailingIterator:
    """Yield one chunk, then fail to exercise iterator-error cleanup."""

    def __init__(self) -> None:
        self._call_count = 0

    def __iter__(self) -> _FailingIterator:
        return self

    def __next__(self) -> bytes:
        self._call_count += 1
        if self._call_count == 1:
            return b"first"
        raise RuntimeError("private iterator failure")


class _SlowIterator:
    """Keep the legacy ASGI stream active long enough to receive disconnect."""

    def __iter__(self) -> _SlowIterator:
        return self

    def __next__(self) -> bytes:
        time.sleep(0.01)
        return b"chunk"


def _http_scope(*, specification_version: str = "2.4") -> Scope:
    """Return the minimum valid HTTP scope used by StreamingResponse."""

    return cast(
        Scope,
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": specification_version},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/api/v1/jobs/job-1/artifacts/course_pdf",
            "raw_path": b"/api/v1/jobs/job-1/artifacts/course_pdf",
            "query_string": b"",
            "root_path": "",
            "headers": [],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        },
    )


async def _request_message() -> Message:
    """Return a completed empty request body for modern ASGI exchanges."""

    return {"type": "http.request", "body": b"", "more_body": False}


def _response_for(
    context: _CountingArtifactContext,
) -> tuple[EnteredArtifactBody, ArtifactStreamingResponse]:
    """Enter one verified context before constructing the streaming response."""

    body = EnteredArtifactBody.enter(context)
    response = ArtifactStreamingResponse(
        body,
        media_type="application/pdf",
        headers={"Content-Length": "10"},
    )
    return body, response


def test_response_closes_entered_context_once_after_successful_exhaustion() -> None:
    """Normal iteration closes after the terminating ASGI body frame."""

    context = _CountingArtifactContext(iter((b"course", b"-pdf")))
    _body, response = _response_for(context)
    sent_messages: list[Message] = []

    async def send(message: Message) -> None:
        sent_messages.append(message)

    asyncio.run(response(_http_scope(), _request_message, send))

    assert (
        b"".join(
            message.get("body", b"")
            for message in sent_messages
            if message["type"] == "http.response.body"
        )
        == b"course-pdf"
    )
    assert context.enter_count == 1
    assert context.exit_count == 1


def test_response_closes_entered_context_once_after_legacy_disconnect() -> None:
    """ASGI 2.3 receive-side cancellation still releases the descriptor."""

    context = _CountingArtifactContext(iter(_SlowIterator()))
    _body, response = _response_for(context)

    async def disconnect() -> Message:
        return {"type": "http.disconnect"}

    async def send(_message: Message) -> None:
        return None

    asyncio.run(response(_http_scope(specification_version="2.3"), disconnect, send))

    assert context.enter_count == 1
    assert context.exit_count == 1


def test_response_closes_entered_context_once_after_send_failure() -> None:
    """ASGI 2.4 socket failure becomes ClientDisconnect after cleanup."""

    context = _CountingArtifactContext(iter((b"course-pdf",)))
    _body, response = _response_for(context)
    send_count = 0

    async def fail_on_body(message: Message) -> None:
        nonlocal send_count
        send_count += 1
        if message["type"] == "http.response.body":
            raise OSError("private socket failure")

    with pytest.raises(ClientDisconnect):
        asyncio.run(response(_http_scope(), _request_message, fail_on_body))

    assert send_count == 2
    assert context.exit_count == 1


def test_response_closes_entered_context_once_after_iterator_failure() -> None:
    """A producer failure cannot strand the package-owned file descriptor."""

    context = _CountingArtifactContext(iter(_FailingIterator()))
    _body, response = _response_for(context)

    async def send(_message: Message) -> None:
        return None

    with pytest.raises(RuntimeError, match="private iterator failure"):
        asyncio.run(response(_http_scope(), _request_message, send))

    assert context.exit_count == 1


def test_context_entry_failure_happens_before_a_response_exists() -> None:
    """Integrity/auth failures remain renderable before HTTP headers are sent."""

    entry_error = RuntimeError("private entry failure")
    context = _CountingArtifactContext(iter(()), entry_error=entry_error)

    with pytest.raises(RuntimeError, match="private entry failure"):
        EnteredArtifactBody.enter(context)

    assert context.enter_count == 1
    assert context.exit_count == 0


def test_body_construction_failure_releases_the_entered_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Acquired package ownership cannot leak if local construction fails."""

    construction_error = RuntimeError("private body construction failure")
    cleanup_error = RuntimeError("private cleanup failure")
    context = _CountingArtifactContext(iter(()), exit_error=cleanup_error)

    def fail_lock_construction() -> None:
        raise construction_error

    monkeypatch.setattr(
        "app.api.artifact_response.Lock",
        fail_lock_construction,
    )

    with pytest.raises(
        RuntimeError, match="private body construction failure"
    ) as error:
        EnteredArtifactBody.enter(context)

    assert error.value is construction_error
    assert context.enter_count == 1
    assert context.exit_count == 1


def test_construction_failure_remains_authoritative_when_cleanup_also_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A cleanup error cannot replace the Starlette construction failure."""

    construction_error = RuntimeError("private construction failure")
    cleanup_error = RuntimeError("private cleanup failure")
    context = _CountingArtifactContext(iter(()), exit_error=cleanup_error)
    body = EnteredArtifactBody.enter(context)

    def fail_response_construction(*_args: object, **_kwargs: object) -> None:
        raise construction_error

    monkeypatch.setattr(
        "app.api.artifact_response.StreamingResponse.__init__",
        fail_response_construction,
    )

    with pytest.raises(RuntimeError, match="private construction failure") as error:
        ArtifactStreamingResponse(body)

    assert error.value is construction_error
    assert context.enter_count == 1
    assert context.exit_count == 1


def test_explicit_and_response_cleanup_are_idempotent() -> None:
    """Route failure plus ASGI cleanup cannot close one context twice."""

    context = _CountingArtifactContext(iter((b"unread",)))
    body, response = _response_for(context)
    body.close()
    body.close()

    async def send(_message: Message) -> None:
        return None

    asyncio.run(response(_http_scope(), _request_message, send))

    assert context.exit_count == 1
