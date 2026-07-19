"""System readiness and privileged device-auth API contracts."""

from collections.abc import Iterator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from txt2crs.application import (
    SystemAuthenticationError,
    SystemAuthenticationSnapshot,
    SystemAuthenticationState,
)

from app.api.deps import get_txt2crs_authentication, get_txt2crs_readiness
from app.core.config import settings
from app.core.constants import ErrorCode
from app.core.rate_limit import limiter
from app.main import app
from app.services.txt2crs_authentication import SystemAuthenticationBusyError
from app.services.txt2crs_readiness import (
    ReadinessChecks,
    ReadinessCheckState,
    ReadinessSnapshot,
    ReadinessStatus,
)


class RecordingReadiness:
    """Return one fixed snapshot and count cache reads only."""

    def __init__(self) -> None:
        self.snapshot_calls = 0

    def snapshot(self) -> ReadinessSnapshot:
        self.snapshot_calls += 1
        return ReadinessSnapshot(
            status=ReadinessStatus.degraded,
            accepting_jobs=False,
            configured_model_id="gpt-5.6",
            enabled_input_modes=("prompt", "text"),
            checks=ReadinessChecks(
                **dict.fromkeys(ReadinessChecks.model_fields, ReadinessCheckState.ready)
            ),
            warnings=("The provider runtime is currently busy.",),
            recovery_actions=("Wait for the active operation to finish.",),
            checked_at=datetime(2026, 7, 19, tzinfo=UTC),
            is_fresh=True,
        )


class RecordingAuthentication:
    """Return safe auth snapshots or one configured failure."""

    def __init__(self) -> None:
        self.start_calls = 0
        self.snapshot_calls = 0
        self.start_error: Exception | None = None

    def start_authentication(self) -> SystemAuthenticationSnapshot:
        self.start_calls += 1
        if self.start_error is not None:
            raise self.start_error
        return SystemAuthenticationSnapshot(
            state=SystemAuthenticationState.waiting_for_user,
            verification_url="https://auth.openai.com/codex/device",
            user_code="ABCD-1234",
            message="Open the verification page.",
        )

    def snapshot(self) -> SystemAuthenticationSnapshot:
        self.snapshot_calls += 1
        return SystemAuthenticationSnapshot(
            state=SystemAuthenticationState.signed_out,
            verification_url=None,
            user_code=None,
            message="Dedicated ChatGPT subscription is not connected.",
        )


@pytest.fixture()
def system_services() -> Iterator[tuple[RecordingReadiness, RecordingAuthentication]]:
    readiness = RecordingReadiness()
    authentication = RecordingAuthentication()
    app.dependency_overrides[get_txt2crs_readiness] = lambda: readiness
    app.dependency_overrides[get_txt2crs_authentication] = lambda: authentication
    yield readiness, authentication
    app.dependency_overrides.pop(get_txt2crs_readiness, None)
    app.dependency_overrides.pop(get_txt2crs_authentication, None)
    limiter.reset()


def test_readiness_requires_auth_and_returns_only_cached_projection(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    system_services: tuple[RecordingReadiness, RecordingAuthentication],
) -> None:
    readiness, _authentication = system_services

    assert client.get(f"{settings.API_V1_STR}/system/readiness").status_code == 401
    response = client.get(
        f"{settings.API_V1_STR}/system/readiness",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert "private_path" not in response.text
    assert readiness.snapshot_calls == 1


def test_device_routes_require_superuser_before_service_access(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
    system_services: tuple[RecordingReadiness, RecordingAuthentication],
) -> None:
    _readiness, authentication = system_services

    for method, path in (
        ("post", "/system/auth/start"),
        ("get", "/system/auth/status"),
    ):
        response = client.request(
            method,
            f"{settings.API_V1_STR}{path}",
            headers=normal_user_token_headers,
        )
        assert response.status_code == 403
        assert response.json()["code"] == ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS.value

    assert authentication.start_calls == 0
    assert authentication.snapshot_calls == 0


def test_superuser_can_start_and_poll_safe_authentication(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    system_services: tuple[RecordingReadiness, RecordingAuthentication],
) -> None:
    _readiness, authentication = system_services

    started = client.post(
        f"{settings.API_V1_STR}/system/auth/start",
        headers=superuser_token_headers,
    )
    status = client.get(
        f"{settings.API_V1_STR}/system/auth/status",
        headers=superuser_token_headers,
    )

    assert started.status_code == 200
    assert started.json()["verification_url"].startswith("https://auth.openai.com/")
    assert status.status_code == 200
    assert status.json()["state"] == "signed_out"
    assert "token" not in (started.text + status.text).casefold()
    assert authentication.start_calls == 1
    assert authentication.snapshot_calls == 1


@pytest.mark.parametrize(
    ("service_error", "expected_status", "expected_code"),
    [
        (SystemAuthenticationBusyError(), 503, ErrorCode.SYSTEM_NOT_READY),
        (
            SystemAuthenticationError("Bearer private-provider-response"),
            502,
            ErrorCode.SYSTEM_AUTH_FAILED,
        ),
    ],
)
def test_auth_start_maps_safe_rfc9457_errors(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    system_services: tuple[RecordingReadiness, RecordingAuthentication],
    service_error: Exception,
    expected_status: int,
    expected_code: ErrorCode,
) -> None:
    _readiness, authentication = system_services
    authentication.start_error = service_error

    response = client.post(
        f"{settings.API_V1_STR}/system/auth/start",
        headers=superuser_token_headers,
    )

    assert response.status_code == expected_status
    assert response.json()["code"] == expected_code.value
    assert response.headers["content-type"].startswith("application/problem+json")
    assert "private-provider-response" not in response.text


def test_auth_start_has_finite_rate_limit(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    system_services: tuple[RecordingReadiness, RecordingAuthentication],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del system_services
    monkeypatch.setattr(limiter, "enabled", True)
    limiter.reset()

    responses = [
        client.post(
            f"{settings.API_V1_STR}/system/auth/start",
            headers=superuser_token_headers,
        )
        for _ in range(6)
    ]

    assert responses[-1].status_code == 429
    assert responses[-1].json()["code"] == ErrorCode.RATE_LIMIT_EXCEEDED.value
