"""Request logging privacy regressions."""

import asyncio
import logging
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.core.exception_handlers import generic_exception_handler
from app.core.middleware import RequestLoggingMiddleware


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
