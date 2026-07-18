"""
User management API routes.

This module provides user CRUD operations, authentication, profile management,
and self-service registration. Includes admin-only endpoints for superusers.

Access Levels:
- Public: /signup (rate limited)
- Authenticated: /me endpoints for self-service
- Superuser: Full user management (list, create, update, delete any user)
"""

import uuid
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Path,
    Query,
    Request,
)
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.constants import ErrorCode
from app.core.exceptions import (
    AppException,
    AuthorizationError,
    ConflictError,
    NotFoundError,
)
from app.core.rate_limit import SIGNUP_RATE_LIMIT, limiter
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email_with_retry,
)

router = APIRouter(prefix="/users", tags=["users"])


def _raise_user_update_integrity_error(exc: IntegrityError) -> None:
    """
    Translate DB-level write failures into deterministic 4xx API responses.

    Update endpoints should not leak backend integrity failures as 500s for
    invalid user input or expected uniqueness conflicts.
    """
    detail = str(exc.orig).lower() if exc.orig is not None else str(exc).lower()
    if "duplicate key value" in detail and "email" in detail:
        raise ConflictError(
            code=ErrorCode.USER_ALREADY_EXISTS,
            detail="User with this email already exists",
        )
    if 'null value in column "email"' in detail:
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            detail="Email may be omitted, but cannot be null",
        )
    raise AppException(
        code=ErrorCode.INVALID_INPUT, detail="Invalid user update payload"
    )


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
    summary="List users (Admin)",
    description="""
Retrieve a paginated list of all users in the system.

**Access:** Superuser only

Returns user data without sensitive fields (password hashes).
    """,
    responses={
        200: {
            "description": "Successfully retrieved users",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "email": "user@example.com",
                                "full_name": "John Doe",
                                "is_active": True,
                                "is_superuser": False,
                            }
                        ],
                        "count": 1,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough privileges (superuser required)"},
    },
)
def read_users(
    session: SessionDep,
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="Number of users to skip for pagination",
            examples=[0],
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Maximum number of users to return (1-100)",
            examples=[20],
        ),
    ] = 100,
) -> Any:
    """Retrieve users."""
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = (
        select(User)
        .order_by(col(User.created_at).desc().nulls_last())
        .offset(skip)
        .limit(limit)
    )
    users = session.exec(statement).all()

    users_public = [UserPublic.model_validate(user) for user in users]
    return UsersPublic(data=users_public, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    status_code=201,
    summary="Create user (Admin)",
    description="""
Create a new user account with full control over all fields.

**Access:** Superuser only

Allows setting:
- Email and password
- Full name
- Active status
- Superuser privileges

If email sending is enabled, sends a secure onboarding email with a
password setup link.
    """,
    responses={
        201: {
            "description": "User successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "newuser@example.com",
                        "full_name": "Jane Doe",
                        "is_active": True,
                        "is_superuser": False,
                    }
                }
            },
        },
        409: {"description": "User with this email already exists"},
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough privileges (superuser required)"},
        422: {"description": "Validation error in request body"},
    },
)
def create_user(
    *,
    session: SessionDep,
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """Create new user."""
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise ConflictError(
            code=ErrorCode.USER_ALREADY_EXISTS,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        password_reset_token = generate_password_reset_token(
            email=user_in.email, current_password_hash=user.hashed_password
        )
        email_data = generate_reset_password_email(
            email_to=user_in.email,
            email=user_in.email,
            token=password_reset_token,
        )
        background_tasks.add_task(
            send_email_with_retry,
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch(
    "/me",
    response_model=UserPublic,
    summary="Update current user profile",
    description="""
Update the current authenticated user's profile information.

**Updatable fields:**
- email (must be unique)
- full_name

**Note:** To change password, use the `/me/password` endpoint.
    """,
    responses={
        200: {
            "description": "Profile successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "updated@example.com",
                        "full_name": "Updated Name",
                        "is_active": True,
                        "is_superuser": False,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        409: {"description": "User with this email already exists"},
        422: {"description": "Validation error in request body"},
    },
)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """Update own user."""
    user_data = user_in.model_dump(exclude_unset=True)
    if "email" in user_data:
        email = user_data["email"]
        if email is None:
            raise AppException(
                code=ErrorCode.VALIDATION_ERROR,
                detail="Email may be omitted, but cannot be null",
            )
        existing_user = crud.get_user_by_email(session=session, email=email)
        if existing_user and existing_user.id != current_user.id:
            raise ConflictError(
                code=ErrorCode.USER_ALREADY_EXISTS,
                detail="User with this email already exists",
            )
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        _raise_user_update_integrity_error(exc)
    session.refresh(current_user)
    return current_user


@router.patch(
    "/me/password",
    response_model=Message,
    summary="Change current user password",
    description="""
Change the password for the current authenticated user.

**Requirements:**
- Must provide current password for verification
- New password must be different from current password
- Password must meet minimum requirements (8+ characters)
    """,
    responses={
        200: {
            "description": "Password successfully updated",
            "content": {
                "application/json": {
                    "example": {"message": "Password updated successfully"}
                }
            },
        },
        400: {
            "description": "Invalid current password or new password same as current"
        },
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error in request body"},
    },
)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """Update own password."""
    verified, _ = verify_password(body.current_password, current_user.hashed_password)
    if not verified:
        raise AppException(
            code=ErrorCode.USER_INVALID_PASSWORD, detail="Incorrect password"
        )
    if body.current_password == body.new_password:
        raise AppException(
            code=ErrorCode.USER_PASSWORD_MISMATCH,
            detail="New password cannot be the same as the current one",
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Get current user profile",
    description="""
Retrieve the profile information for the currently authenticated user.

Returns user data without sensitive fields (password hash).
    """,
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "is_active": True,
                        "is_superuser": False,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
    },
)
def read_user_me(current_user: CurrentUser) -> Any:
    """Get current user."""
    return current_user


@router.delete(
    "/me",
    response_model=Message,
    summary="Delete current user account",
    description="""
Permanently delete the current user's account.

**Warning:** This action cannot be undone. All associated data will be deleted.

**Restriction:** Superusers cannot delete themselves through this endpoint
to prevent accidental loss of admin access.
    """,
    responses={
        200: {
            "description": "Account successfully deleted",
            "content": {
                "application/json": {
                    "example": {"message": "User deleted successfully"}
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Superusers cannot delete themselves"},
    },
)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """Delete own user."""
    if current_user.is_superuser:
        raise AuthorizationError(
            detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post(
    "/signup",
    response_model=UserPublic,
    status_code=201,
    summary="Register new user (Public)",
    description="""
Public registration endpoint for new user self-signup.

**Rate Limited:** This endpoint is rate-limited to prevent abuse.

**No Authentication Required:** This is a public endpoint.

New users are created with:
- `is_active = True`
- `is_superuser = False`
    """,
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "newuser@example.com",
                        "full_name": "New User",
                        "is_active": True,
                        "is_superuser": False,
                    }
                }
            },
        },
        409: {"description": "User with this email already exists"},
        422: {"description": "Validation error in request body"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(SIGNUP_RATE_LIMIT)
def register_user(
    request: Request,  # noqa: ARG001 - used by @limiter.limit decorator
    session: SessionDep,
    user_in: UserRegister,
) -> Any:
    """Create new user without the need to be logged in."""
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise ConflictError(
            code=ErrorCode.USER_ALREADY_EXISTS,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    summary="Get user by ID",
    description="""
Retrieve a specific user by their unique identifier.

**Access Control:**
- Regular users: Can only retrieve their own profile
- Superusers: Can retrieve any user
    """,
    responses={
        200: {
            "description": "User successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                        "full_name": "John Doe",
                        "is_active": True,
                        "is_superuser": False,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough privileges to access this user"},
        404: {"description": "User not found"},
    },
)
def read_user_by_id(
    user_id: Annotated[
        uuid.UUID,
        Path(
            description="Unique identifier of the user",
            examples=["123e4567-e89b-12d3-a456-426614174000"],
        ),
    ],
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Get a specific user by id."""
    if not current_user.is_superuser and user_id != current_user.id:
        raise AuthorizationError(detail="The user doesn't have enough privileges")

    user = session.get(User, user_id)
    if not user:
        raise NotFoundError(resource="User", identifier=str(user_id))
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
    summary="Update user (Admin)",
    description="""
Update any user's information by their ID.

**Access:** Superuser only

**Updatable fields:**
- email (must be unique)
- full_name
- password
- is_active
- is_superuser
    """,
    responses={
        200: {
            "description": "User successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "updated@example.com",
                        "full_name": "Updated Name",
                        "is_active": True,
                        "is_superuser": False,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough privileges (superuser required)"},
        404: {"description": "User not found"},
        409: {"description": "User with this email already exists"},
        422: {"description": "Validation error in request body"},
    },
)
def update_user(
    *,
    session: SessionDep,
    user_id: Annotated[
        uuid.UUID,
        Path(
            description="Unique identifier of the user to update",
            examples=["123e4567-e89b-12d3-a456-426614174000"],
        ),
    ],
    user_in: UserUpdate,
) -> Any:
    """Update a user."""
    db_user = session.get(User, user_id)
    if not db_user:
        raise NotFoundError(resource="User", identifier=str(user_id))
    user_data = user_in.model_dump(exclude_unset=True)
    if "email" in user_data:
        email = user_data["email"]
        if email is None:
            raise AppException(
                code=ErrorCode.VALIDATION_ERROR,
                detail="Email may be omitted, but cannot be null",
            )
        existing_user = crud.get_user_by_email(session=session, email=email)
        if existing_user and existing_user.id != user_id:
            raise ConflictError(
                code=ErrorCode.USER_ALREADY_EXISTS,
                detail="User with this email already exists",
            )

    try:
        db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    except IntegrityError as exc:
        session.rollback()
        _raise_user_update_integrity_error(exc)
    return db_user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
    summary="Delete user (Admin)",
    description="""
Permanently delete a user and all their associated data.

**Access:** Superuser only

**Warning:** This action cannot be undone. All user's items will also be deleted.

**Restriction:** Superusers cannot delete themselves through this endpoint.
    """,
    responses={
        200: {
            "description": "User successfully deleted",
            "content": {
                "application/json": {
                    "example": {"message": "User deleted successfully"}
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough privileges or attempting self-deletion"},
        404: {"description": "User not found"},
    },
)
def delete_user(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: Annotated[
        uuid.UUID,
        Path(
            description="Unique identifier of the user to delete",
            examples=["123e4567-e89b-12d3-a456-426614174000"],
        ),
    ],
) -> Message:
    """Delete a user."""
    user = session.get(User, user_id)
    if not user:
        raise NotFoundError(resource="User", identifier=str(user_id))
    if user == current_user:
        raise AuthorizationError(
            detail="Super users are not allowed to delete themselves"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
