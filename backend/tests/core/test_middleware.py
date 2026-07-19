"""Request logging privacy regressions."""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.types import Message, Receive, Scope, Send

from app.core.exception_handlers import generic_exception_handler
from app.core.middleware import RequestLoggingMiddleware, UploadBodyLimitMiddleware

AsgiApplication = Callable[[Scope, Receive, Send], Awaitable[None]]


def test_request_logs_omit_raw_path_query_and_client_address(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Source-bearing URL components must never enter application logs."""

    application = FastAPI()
    application.add_middleware(RequestLoggingMiddleware)

    @application.get("/recovery/{recovery_token}", name="password-recovery")
    def recovery_route(recovery_token: str) -> dict[str, bool]:
        del recovery_token
        return {"ok": True}

    with caplog.at_level(logging.INFO):
        response = TestClient(application).get(
            "/recovery/private-token?email=learner@example.com"
        )

    assert response.status_code == 200
    records = caplog.records
    request_records = [
        record for record in records if str(record.getMessage()).startswith("request.")
    ]
    assert request_records
    rendered = " ".join(str(record.__dict__) for record in request_records)
    assert "private-token" not in rendered
    assert "learner@example.com" not in rendered
    assert "client_ip" not in rendered
    assert "query" not in rendered
    assert any(
        getattr(record, "route_name", None) == "password-recovery"
        for record in request_records
    )


def test_exception_logs_omit_private_path_and_exception_detail(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Unhandled provider and filesystem details stay out of global logs."""

    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/jobs/private-job-id",
            "query_string": b"source=learner-secret",
            "headers": [],
            "route": SimpleNamespace(name="jobs-create"),
        }
    )
    with caplog.at_level(logging.ERROR):
        response = asyncio.run(
            generic_exception_handler(
                request,
                RuntimeError("Bearer private-token at /home/ada/.codex/auth.json"),
            )
        )

    assert response.status_code == 500
    rendered = " ".join(str(record.__dict__) for record in caplog.records)
    assert "private-job-id" not in rendered
    assert "learner-secret" not in rendered
    assert "private-token" not in rendered
    assert "/home/ada" not in rendered
    assert "jobs-create" in rendered


def _http_scope(
    *,
    path: str = "/api/v1/jobs/upload",
    headers: list[tuple[bytes, bytes]] | None = None,
) -> Scope:
    """Return a small valid ASGI HTTP scope for middleware unit tests."""

    return cast(
        Scope,
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("ascii"),
            "query_string": b"",
            "root_path": "",
            "headers": headers or [],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        },
    )


async def _run_asgi(
    application: AsgiApplication,
    *,
    scope: Scope,
    incoming_messages: list[Message],
) -> list[Message]:
    """Run one ASGI exchange and return every response message."""

    queued_messages = list(incoming_messages)
    sent_messages: list[Message] = []

    async def receive() -> Message:
        if queued_messages:
            return queued_messages.pop(0)
        return {"type": "http.disconnect"}

    async def send(message: Message) -> None:
        sent_messages.append(message)

    await application(scope, receive, send)
    return sent_messages


def _body_reading_application(
    received: list[Message],
    call_count: list[int],
) -> AsgiApplication:
    """Return an ASGI app that consumes the body before sending success."""

    async def application(scope: Scope, receive: Receive, send: Send) -> None:
        del scope
        call_count.append(1)
        while True:
            message = await receive()
            received.append(message)
            if message["type"] == "http.disconnect":
                break
            if message["type"] == "http.request" and not message.get(
                "more_body", False
            ):
                break
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    return application


def _problem_from_messages(messages: list[Message]) -> dict[str, Any]:
    """Decode the single bounded Problem Details response body."""

    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    parsed_body = json.loads(response_body)
    assert isinstance(parsed_body, dict)
    return parsed_body


def test_upload_body_limit_rejects_declared_oversize_before_downstream() -> None:
    downstream_calls: list[int] = []

    async def downstream(scope: Scope, receive: Receive, send: Send) -> None:
        del scope, receive, send
        downstream_calls.append(1)

    middleware = UploadBodyLimitMiddleware(
        downstream,
        maximum_body_bytes=10,
        upload_path="/api/v1/jobs/upload",
    )
    messages = asyncio.run(
        _run_asgi(
            middleware,
            scope=_http_scope(headers=[(b"content-length", b"11")]),
            incoming_messages=[],
        )
    )

    assert downstream_calls == []
    assert messages[0]["status"] == 413
    assert (b"content-type", b"application/problem+json") in messages[0]["headers"]
    assert _problem_from_messages(messages)["code"] == "JOB_7005"


@pytest.mark.parametrize(
    "content_length_headers",
    [
        [(b"content-length", b"not-a-number")],
        [(b"content-length", b"-1")],
        [(b"content-length", b"+10")],
        [(b"content-length", b" 10")],
        [(b"content-length", b"1_0")],
        [(b"content-length", b"5"), (b"content-length", b"6")],
    ],
)
def test_upload_body_limit_rejects_invalid_or_duplicate_length(
    content_length_headers: list[tuple[bytes, bytes]],
) -> None:
    downstream_calls: list[int] = []

    async def downstream(scope: Scope, receive: Receive, send: Send) -> None:
        del scope, receive, send
        downstream_calls.append(1)

    middleware = UploadBodyLimitMiddleware(
        downstream,
        maximum_body_bytes=10,
        upload_path="/api/v1/jobs/upload",
    )
    messages = asyncio.run(
        _run_asgi(
            middleware,
            scope=_http_scope(headers=content_length_headers),
            incoming_messages=[],
        )
    )

    assert downstream_calls == []
    assert messages[0]["status"] == 400
    assert _problem_from_messages(messages)["code"] == "VALIDATION_4004"


def test_upload_body_limit_counts_chunked_or_dishonest_body() -> None:
    received: list[Message] = []
    downstream_calls: list[int] = []
    middleware = UploadBodyLimitMiddleware(
        _body_reading_application(received, downstream_calls),
        maximum_body_bytes=10,
        upload_path="/api/v1/jobs/upload",
    )

    messages = asyncio.run(
        _run_asgi(
            middleware,
            scope=_http_scope(headers=[(b"content-length", b"5")]),
            incoming_messages=[
                {"type": "http.request", "body": b"123456", "more_body": True},
                {"type": "http.request", "body": b"78901", "more_body": False},
            ],
        )
    )

    assert downstream_calls == [1]
    assert messages[0]["status"] == 413
    assert _problem_from_messages(messages) == {
        "type": "https://api.example.com/problems/JOB_7005",
        "title": "Job Payload Too Large",
        "status": 413,
        "detail": "Upload request body exceeds the configured limit.",
        "code": "JOB_7005",
    }


def test_upload_body_limit_allows_exact_limit_and_preserves_frames() -> None:
    received: list[Message] = []
    downstream_calls: list[int] = []
    middleware = UploadBodyLimitMiddleware(
        _body_reading_application(received, downstream_calls),
        maximum_body_bytes=10,
        upload_path="/api/v1/jobs/upload",
    )
    incoming_messages: list[Message] = [
        {"type": "http.request", "body": b"1234", "more_body": True},
        {"type": "http.request", "body": b"567890", "more_body": False},
    ]

    messages = asyncio.run(
        _run_asgi(
            middleware,
            scope=_http_scope(),
            incoming_messages=incoming_messages,
        )
    )

    assert downstream_calls == [1]
    assert received == incoming_messages
    assert messages[0]["status"] == 204


def test_upload_body_limit_preserves_disconnect_without_fabricating_error() -> None:
    received: list[Message] = []
    downstream_calls: list[int] = []
    middleware = UploadBodyLimitMiddleware(
        _body_reading_application(received, downstream_calls),
        maximum_body_bytes=10,
        upload_path="/api/v1/jobs/upload",
    )

    messages = asyncio.run(
        _run_asgi(
            middleware,
            scope=_http_scope(),
            incoming_messages=[
                {"type": "http.request", "body": b"1234", "more_body": True},
                {"type": "http.disconnect"},
            ],
        )
    )

    assert downstream_calls == [1]
    assert received[-1] == {"type": "http.disconnect"}
    assert messages[0]["status"] == 204


def test_upload_body_limit_does_not_apply_to_unrelated_routes() -> None:
    received: list[Message] = []
    downstream_calls: list[int] = []
    middleware = UploadBodyLimitMiddleware(
        _body_reading_application(received, downstream_calls),
        maximum_body_bytes=10,
        upload_path="/api/v1/jobs/upload",
    )

    messages = asyncio.run(
        _run_asgi(
            middleware,
            scope=_http_scope(
                path="/api/v1/login/access-token",
                headers=[(b"content-length", b"10000")],
            ),
            incoming_messages=[
                {"type": "http.request", "body": b"x" * 100, "more_body": False}
            ],
        )
    )

    assert downstream_calls == [1]
    assert len(received[0]["body"]) == 100
    assert messages[0]["status"] == 204
