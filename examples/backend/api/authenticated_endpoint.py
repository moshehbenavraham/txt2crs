"""
EXAMPLE: Authenticated endpoint with authorization and rich OpenAPI metadata.

PATTERN: REST Endpoint with Auth, Validation, and Public Responses
USE WHEN: Adding a shell endpoint that reads a protected application resource
TAGS: api, auth, openapi, validation, endpoint

Based on: app/api/routes/users.py
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Path

from app.api.deps import CurrentUser, SessionDep
from app.core.constants import ErrorCode, HTTPStatusCode
from app.core.exceptions import AppException
from app.models import User, UserPublic

router = APIRouter(prefix="/example", tags=["example"])


@router.get(
    "/profile",
    response_model=UserPublic,
    summary="Read the current profile",
    description=(
        "Returns only the authenticated user's public fields. The dependency "
        "rejects missing, invalid, or inactive credentials before this handler."
    ),
    responses={
        HTTPStatusCode.OK: {"description": "Current public profile"},
        HTTPStatusCode.UNAUTHORIZED: {"description": "Authentication required"},
        HTTPStatusCode.FORBIDDEN: {"description": "Inactive account"},
    },
)
def read_profile_example(current_user: CurrentUser) -> UserPublic:
    """Project the authenticated table row through the public schema."""

    return UserPublic.model_validate(current_user)


@router.get(
    "/users/{user_id}",
    response_model=UserPublic,
    summary="Read one authorized user",
    description=(
        "A regular user may read only their own profile. A superuser may read "
        "another user after the target is resolved."
    ),
    responses={
        HTTPStatusCode.OK: {"description": "Authorized public profile"},
        HTTPStatusCode.UNAUTHORIZED: {"description": "Authentication required"},
        HTTPStatusCode.FORBIDDEN: {"description": "Insufficient permissions"},
        HTTPStatusCode.NOT_FOUND: {"description": "User not found"},
    },
)
def read_user_example(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: Annotated[
        uuid.UUID,
        Path(description="Application user UUID"),
    ],
) -> UserPublic:
    """Enforce access next to the protected user lookup."""

    if not current_user.is_superuser and current_user.id != user_id:
        raise AppException(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail="Not authorized to read this user",
        )

    user = session.get(User, user_id)
    if user is None:
        raise AppException(
            code=ErrorCode.USER_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found",
        )
    return UserPublic.model_validate(user)


# Key patterns:
# - Typed dependencies establish authentication and database ownership.
# - ``Annotated`` path types validate before business logic executes.
# - Every returned table row is projected through an allowlisted public model.
# - ``AppException`` plus ``ErrorCode`` preserves the RFC 9457 shell contract.
