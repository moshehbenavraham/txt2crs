from typing import Any

from fastapi import APIRouter
from pydantic import EmailStr, Field

from app.api.deps import SessionDep
from app.core.security import get_password_hash
from app.models import (
    StrictAPIModel,
    User,
    UserPublic,
)

router = APIRouter(tags=["private"], prefix="/private")


class PrivateUserCreate(StrictAPIModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """
    Create a new user.
    """

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )

    session.add(user)
    session.commit()

    return user
