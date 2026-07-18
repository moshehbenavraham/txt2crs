from unittest.mock import patch

from fastapi.testclient import TestClient
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import Session

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.crud import create_user
from app.models import User, UserCreate
from app.utils import generate_password_reset_token
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 401


def test_use_access_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


def test_recovery_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.login.send_email_with_retry", return_value=None
    ) as send_email_mock:
        known_email = "test@example.com"
        unknown_email = "jVgQr@example.com"

        known_response = client.post(
            f"{settings.API_V1_STR}/password-recovery",
            headers=normal_user_token_headers,
            json={"email": known_email},
        )
        unknown_response = client.post(
            f"{settings.API_V1_STR}/password-recovery",
            headers=normal_user_token_headers,
            json={"email": unknown_email},
        )

        expected_body = {
            "message": "If the account exists, a password recovery email has been sent."
        }
        assert known_response.status_code == 200
        assert unknown_response.status_code == 200
        assert known_response.json() == expected_body
        assert unknown_response.json() == expected_body
        send_email_mock.assert_called_once()


def test_recovery_password_legacy_route(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    with patch(
        "app.api.routes.login.send_email_with_retry", return_value=None
    ) as send_email_mock:
        response = client.post(
            f"{settings.API_V1_STR}/password-recovery/test@example.com",
            headers=normal_user_token_headers,
        )

        assert response.status_code == 200
        assert response.json() == {
            "message": "If the account exists, a password recovery email has been sent."
        }
        send_email_mock.assert_called_once()


def test_reset_password(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    user = create_user(session=db, user_create=user_create)
    token = generate_password_reset_token(
        email=email, current_password_hash=user.hashed_password
    )
    headers = user_authentication_headers(client=client, email=email, password=password)
    data = {"new_password": new_password, "token": token}

    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    db.refresh(user)
    verified, _ = verify_password(new_password, user.hashed_password)
    assert verified


def test_reset_password_token_cannot_be_reused(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    first_new_password = random_lower_string()
    second_new_password = random_lower_string()

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    user = create_user(session=db, user_create=user_create)
    token = generate_password_reset_token(
        email=email, current_password_hash=user.hashed_password
    )
    headers = user_authentication_headers(client=client, email=email, password=password)

    first_response = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json={"new_password": first_new_password, "token": token},
    )
    assert first_response.status_code == 200
    assert first_response.json() == {"message": "Password updated successfully"}

    second_response = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json={"new_password": second_new_password, "token": token},
    )
    assert second_response.status_code == 401
    assert second_response.json()["detail"] == "Invalid token"

    db.refresh(user)
    first_verified, _ = verify_password(first_new_password, user.hashed_password)
    second_verified, _ = verify_password(second_new_password, user.hashed_password)
    assert first_verified
    assert not second_verified


def test_reset_password_invalid_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 401
    assert response["detail"] == "Invalid token"


def test_reset_password_missing_user_is_invalid_token(client: TestClient) -> None:
    token = generate_password_reset_token(
        email=random_email(),
        current_password_hash=get_password_hash(random_lower_string()),
    )

    response = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        json={"new_password": random_lower_string(), "token": token},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


def test_reset_password_openapi_advertises_runtime_error_statuses() -> None:
    from app.main import app

    responses = app.openapi()["paths"]["/api/v1/reset-password/"]["post"]["responses"]

    assert "401" in responses
    assert "403" in responses
    assert "400" not in responses
    assert "404" not in responses


def test_login_with_bcrypt_password_upgrades_to_argon2(
    client: TestClient, db: Session
) -> None:
    email = random_email()
    password = random_lower_string()
    user = User(
        email=email,
        hashed_password=BcryptHasher().hash(password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )

    assert response.status_code == 200
    db.refresh(user)
    assert user.hashed_password.startswith("$argon2")


def test_login_with_argon2_password_keeps_hash(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    original_hash = get_password_hash(password)
    user = User(email=email, hashed_password=original_hash, is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )

    assert response.status_code == 200
    db.refresh(user)
    assert user.hashed_password == original_hash
