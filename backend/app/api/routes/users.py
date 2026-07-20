"""
User management API routes.

This module provides user CRUD operations, authentication, profile management,
and self-service registration. Includes admin-only endpoints for superusers.

Access Levels:
- Conditional public: /signup (local opt-in and rate limited)
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
from sqlmodel import col, func, select
from txt2crs.application import (
    ApplicationClosedError,
    OwnerPurgeError,
    Txt2CrsApplication,
)

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    Txt2CrsApplicationDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.constants import (
    ContentTypes,
    ErrorCode,
    ErrorMessages,
    HTTPStatusCode,
)
from app.core.exceptions import (
    AppException,
    AuthorizationError,
    ConflictError,
    NotFoundError,
)
from app.core.logging import get_logger
from app.core.rate_limit import SIGNUP_RATE_LIMIT, limiter
from app.core.security import get_password_hash, verify_password
from app.core.txt2crs_errors import translate_txt2crs_exception
from app.models import (
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
logger = get_logger(__name__)
_ACCOUNT_DELETE_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    # Purge can finish before PostgreSQL fails. The response must not imply a
    # distributed rollback; callers can safely retry the idempotent operation.
    HTTPStatusCode.INTERNAL_SERVER_ERROR: {
        "description": (
            "Engine erasure may already be complete; retrying account deletion is safe."
        ),
        "content": {ContentTypes.PROBLEM_JSON: {}},
    },
    HTTPStatusCode.SERVICE_UNAVAILABLE: {
        "description": ErrorMessages.ACCOUNT_PURGE_FAILED,
        "content": {ContentTypes.PROBLEM_JSON: {}},
    },
}


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


def _purge_user_engine_state(
    *,
    application: Txt2CrsApplication,
    user_id: uuid.UUID,
) -> None:
    """
    Establish the package owner barrier before PostgreSQL identity deletion.

    The public facade already cancels and joins matching executor work, then
    removes artifacts before transactionally deleting engine job parents. The
    shell deliberately does not reproduce any of that behavior here.
    """

    safe_user_id = str(user_id)
    logger.info(
        "user.engine_purge_started",
        extra={"user_id": safe_user_id},
    )
    translated_error: AppException | None = None
    try:
        application.purge_owner(user_id=safe_user_id)
    except (ApplicationClosedError, OwnerPurgeError) as error:
        # Never log ``error``: package exceptions may contain an artifact path,
        # provider detail, or persistence context. A finite reason is enough
        # for operations to distinguish readiness from purge failure.
        reason_code = (
            "application_closed"
            if isinstance(error, ApplicationClosedError)
            else "owner_purge_failed"
        )
        logger.error(
            "user.engine_purge_failed",
            extra={
                "user_id": safe_user_id,
                "reason_code": reason_code,
            },
        )
        translated_error = translate_txt2crs_exception(error)

    if translated_error is not None:
        # Raise after leaving the ``except`` block. This prevents Python from
        # attaching the private package exception as ``__context__``.
        raise translated_error from None

    logger.info(
        "user.engine_purge_completed",
        extra={"user_id": safe_user_id},
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

**Warning:** This action cannot be undone. Engine-owned course requests,
checkpoints, delivery records, and artifacts are purged before the account.
This operation does not erase retained logs or backup copies; their retention
is handled separately.

**Failure behavior:** A purge failure leaves the account intact. If engine
purge succeeds but PostgreSQL deletion fails, retrying is safe.

**Restriction:** Superusers cannot delete themselves through this endpoint
to prevent accidental loss of admin access.
    """,
    responses={
        **_ACCOUNT_DELETE_ERROR_RESPONSES,
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
def delete_user_me(
    session: SessionDep,
    current_user: CurrentUser,
    application: Txt2CrsApplicationDep,
) -> Any:
    """Delete own user."""
    if current_user.is_superuser:
        raise AuthorizationError(
            detail="Super users are not allowed to delete themselves"
        )
    # Engine-owned requests, checkpoints, delivery rows, artifacts, and any
    # active executor must settle before this authenticated identity can
    # disappear. If purge fails, the helper raises before the SQLModel session
    # is mutated, leaving the user available for a safe retry.
    _purge_user_engine_state(
        application=application,
        user_id=current_user.id,
    )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post(
    "/signup",
    response_model=UserPublic,
    status_code=201,
    summary="Register new user (Local opt-in)",
    description="""
Conditional registration endpoint for new user self-signup.

**Rate Limited:** This endpoint is rate-limited to prevent abuse.

**Local Opt-in:** No authentication is required only when
`ENVIRONMENT=local` and `ENABLE_PUBLIC_SIGNUP=true`. Signup is disabled by
default and cannot be enabled in staging or production.

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
        403: {"description": "Public signup is disabled"},
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
    # Check the deployment mode before reading the submitted email from the
    # database. Judge/demo deployments stay invite-only and do not reveal
    # whether an account already exists.
    if not settings.public_signup_enabled:
        raise AuthorizationError(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail="Public signup is disabled.",
        )
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
Permanently delete a user's live account and engine-owned course state.

**Access:** Superuser only

**Warning:** This action cannot be undone. Engine-owned course requests,
checkpoints, delivery records, and artifacts are purged before the account.
This operation does not erase retained logs or backup copies; their retention
is handled separately.

**Failure behavior:** A purge failure leaves the account intact. If engine
purge succeeds but PostgreSQL deletion fails, retrying is safe.

**Restriction:** Superusers cannot delete themselves through this endpoint.
    """,
    responses={
        **_ACCOUNT_DELETE_ERROR_RESPONSES,
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
    application: Txt2CrsApplicationDep,
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
    # Complete authorization before mutation, then establish the same public
    # owner barrier used by self-service deletion. The target UUID is passed
    # unchanged; the acting administrator's owner state is never touched.
    _purge_user_engine_state(
        application=application,
        user_id=user_id,
    )
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
