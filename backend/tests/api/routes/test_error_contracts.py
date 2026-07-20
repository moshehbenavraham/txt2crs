import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response

from app.core.config import settings
from app.core.constants import ContentTypes, ErrorCode
from app.core.rate_limit import limiter


def _assert_problem_detail(
    response: Response,
    *,
    expected_status: int,
    expected_code: ErrorCode,
    expected_detail: str,
) -> None:
    payload = response.json()
    assert response.status_code == expected_status
    assert response.headers["content-type"].startswith(ContentTypes.PROBLEM_JSON)
    assert payload["status"] == expected_status
    assert payload["code"] == expected_code.value
    assert payload["type"].endswith(expected_code.value)
    assert payload["detail"] == expected_detail
    assert isinstance(payload["trace_id"], str)
    assert payload["trace_id"]


def test_users_me_without_token_returns_rfc9457_problem(
    client: TestClient,
) -> None:
    response = client.get(f"{settings.API_V1_STR}/users/me")
    _assert_problem_detail(
        response,
        expected_status=401,
        expected_code=ErrorCode.AUTH_TOKEN_INVALID,
        expected_detail="Not authenticated",
    )


def test_users_me_invalid_token_returns_semantic_auth_problem(
    client: TestClient,
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    _assert_problem_detail(
        response,
        expected_status=401,
        expected_code=ErrorCode.AUTH_TOKEN_INVALID,
        expected_detail="Could not validate credentials",
    )


def test_forbidden_route_returns_semantic_permission_problem(
    client: TestClient,
    normal_user_token_headers: dict[str, str],
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    _assert_problem_detail(
        response,
        expected_status=403,
        expected_code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
        expected_detail="The user doesn't have enough privileges",
    )


def test_not_found_route_returns_semantic_not_found_problem(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    user_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    _assert_problem_detail(
        response,
        expected_status=404,
        expected_code=ErrorCode.USER_NOT_FOUND,
        expected_detail=f"User with ID '{user_id}' not found",
    )


def test_rate_limit_returns_rfc9457_problem_detail(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(limiter, "enabled", True)
    limiter.reset()
    last_response = None
    for _ in range(10):
        last_response = client.post(
            f"{settings.API_V1_STR}/login/access-token",
            data={"username": "rate-limit-test@example.com", "password": "invalid"},
        )
        if last_response.status_code == 429:
            break
    assert last_response is not None
    _assert_problem_detail(
        last_response,
        expected_status=429,
        expected_code=ErrorCode.RATE_LIMIT_EXCEEDED,
        expected_detail="Too many requests. Please try again later.",
    )
    limiter.reset()


def test_unhandled_exception_returns_internal_problem_detail() -> None:
    with patch(
        "app.api.routes.login.crud.authenticate",
        side_effect=RuntimeError("forced failure"),
    ):
        from app.main import app

        with TestClient(app, raise_server_exceptions=False) as error_client:
            response = error_client.post(
                f"{settings.API_V1_STR}/login/access-token",
                data={"username": settings.FIRST_SUPERUSER, "password": "any-password"},
            )
    _assert_problem_detail(
        response,
        expected_status=500,
        expected_code=ErrorCode.INTERNAL_ERROR,
        expected_detail="An unexpected error occurred",
    )
