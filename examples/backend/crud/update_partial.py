"""
EXAMPLE: Partial administrator user update with permission checks.

PATTERN: CRUD Update with Authorization
USE WHEN: Updating a shell-owned user through an administrator PATCH endpoint
TAGS: crud, update, validation, permissions, partial-update

This example demonstrates:
1. Resolving the target before mutation
2. Enforcing administrator access before target lookup
3. Preserving PATCH semantics through the current UserUpdate contract
4. Delegating password hashing and persistence to the real CRUD boundary

Based on: app/api/routes/users.py:update_user
"""

import uuid

from sqlmodel import Session

from app import crud
from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.models import User, UserUpdate


def update_user_as_superuser(
    *,
    session: Session,
    target_user_id: uuid.UUID,
    user_update: UserUpdate,
    current_user: User,
) -> User:
    """Update one target only after the acting user is authorized."""

    # Authorize before lookup so a regular user cannot enumerate target IDs.
    if not current_user.is_superuser:
        raise AppException(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail="Administrator access is required",
        )

    target_user = session.get(User, target_user_id)
    if target_user is None:
        raise AppException(
            code=ErrorCode.USER_NOT_FOUND,
            detail=f"User with ID '{target_user_id}' not found",
        )

    # Use the repository CRUD helper instead of calling ``sqlmodel_update``
    # directly. It removes the input-only password field, hashes any supplied
    # password, applies only explicitly set values, and commits the update.
    return crud.update_user(
        session=session,
        db_user=target_user,
        user_in=user_update,
    )


# Route usage:
#
# @router.patch("/users/{user_id}", response_model=UserPublic)
# def update_user_example(
#     user_id: uuid.UUID,
#     user_update: UserUpdate,
#     session: SessionDep,
#     current_user: CurrentUser,
# ) -> User:
#     return update_user_as_superuser(
#         session=session,
#         target_user_id=user_id,
#         user_update=user_update,
#         current_user=current_user,
#     )
#
# Key rule: never stage a database mutation before the authorization check.
