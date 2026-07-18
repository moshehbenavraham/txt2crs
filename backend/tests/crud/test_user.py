from unittest.mock import call, patch

import pytest
from fastapi.encoders import jsonable_encoder
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import Session

from app import crud
from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    authenticated_user = crud.authenticate(session=db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.authenticate(session=db, email=email, password=password)
    assert user is None


def test_unknown_user_authentication_runs_dummy_verification(db: Session) -> None:
    password = random_lower_string()

    with patch(
        "app.crud.verify_password", return_value=(False, None)
    ) as verify_password_mock:
        user = crud.authenticate(
            session=db,
            email=random_email(),
            password=password,
        )

    assert user is None
    assert verify_password_mock.call_args_list == [
        call(password, crud.DUMMY_ARGON2_PASSWORD_HASH),
        call(password, crud.DUMMY_BCRYPT_PASSWORD_HASH),
    ]


@pytest.mark.parametrize(
    ("stored_hash", "complementary_hash"),
    [
        (
            crud.DUMMY_ARGON2_PASSWORD_HASH,
            crud.DUMMY_BCRYPT_PASSWORD_HASH,
        ),
        (
            crud.DUMMY_BCRYPT_PASSWORD_HASH,
            crud.DUMMY_ARGON2_PASSWORD_HASH,
        ),
    ],
    ids=["argon2-account", "bcrypt-account"],
)
def test_failed_known_user_authentication_runs_both_hash_algorithms(
    db: Session,
    stored_hash: str,
    complementary_hash: str,
) -> None:
    password = random_lower_string()
    db_user = User(email=random_email(), hashed_password=stored_hash)

    with (
        patch("app.crud.get_user_by_email", return_value=db_user),
        patch(
            "app.crud.verify_password", return_value=(False, None)
        ) as verify_password_mock,
    ):
        user = crud.authenticate(
            session=db,
            email=db_user.email,
            password=password,
        )

    assert user is None
    assert verify_password_mock.call_args_list == [
        call(password, stored_hash),
        call(password, complementary_hash),
    ]


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    assert user.is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = UserCreate(email=username, password=password, is_superuser=True)
    user = crud.create_user(session=db, user_create=user_in)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.create_user(session=db, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    if user.id is not None:
        crud.update_user(session=db, db_user=user, user_in=user_in_update)
    user_2 = db.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    verified, _ = verify_password(new_password, user_2.hashed_password)
    assert verified


def test_authenticate_upgrades_bcrypt_hash_to_argon2(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    bcrypt_hash = BcryptHasher().hash(password)
    user = User(email=email, hashed_password=bcrypt_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    authenticated_user = crud.authenticate(
        session=db,
        email=email,
        password=password,
    )

    assert authenticated_user is not None
    assert authenticated_user.hashed_password.startswith("$argon2")
    verified, updated_hash = verify_password(
        password, authenticated_user.hashed_password
    )
    assert verified
    assert updated_hash is None


def test_authenticate_keeps_current_argon2_hash(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    original_hash = get_password_hash(password)
    user = User(email=email, hashed_password=original_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    authenticated_user = crud.authenticate(
        session=db,
        email=email,
        password=password,
    )

    assert authenticated_user is not None
    assert authenticated_user.hashed_password == original_hash
