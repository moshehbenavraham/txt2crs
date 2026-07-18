"""
Authentication and login API routes.

This module provides OAuth2-compatible authentication endpoints including:
- Login with email/password to obtain JWT access tokens
- Token validation
- Password recovery via email
- Password reset with time-limited tokens

All authentication endpoints are rate-limited to prevent brute-force attacks.
Rate limit: 5 requests per minute for sensitive operations.

Security Notes:
    - Passwords are hashed using Argon2id before storage
    - JWT tokens expire after the configured duration (default: 24 hours)
    - Password reset tokens expire after the configured duration (default: 24 hours)
    - Invalid login attempts do not reveal whether the email exists
"""

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Depends, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import (
    CsrfOriginDep,
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core import security
from app.core.config import settings
from app.core.constants import ErrorCode, HTTPStatusCode
from app.core.exceptions import (
    AppException,
    AuthenticationError,
    NotFoundError,
)
from app.core.rate_limit import AUTH_RATE_LIMIT, limiter
from app.models import (
    Message,
    NewPassword,
    PasswordRecoveryRequest,
    Token,
    UserPublic,
    UserUpdate,
)
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    password_reset_token_matches_user,
    send_email_with_retry,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])
PASSWORD_RECOVERY_GENERIC_MESSAGE = (
    "If the account exists, a password recovery email has been sent."
)


def _enqueue_password_recovery_email(
    *,
    session: SessionDep,
    email: str,
    background_tasks: BackgroundTasks,
) -> None:
    """Queue a password recovery email for existing users."""
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        return

    password_reset_token = generate_password_reset_token(
        email=email, current_password_hash=user.hashed_password
    )
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    background_tasks.add_task(
        send_email_with_retry,
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )


@router.post(
    "/login/access-token",
    response_model=Token,
    summary="Login for access token",
    description="""
OAuth2-compatible token login endpoint.

Authenticates a user with email and password, returning a JWT access token
for authenticating subsequent API requests.

**Authentication:**
This endpoint follows the OAuth2 password flow. The `username` field should
contain the user's email address.

**Rate Limiting:**
Limited to 5 requests per minute to prevent brute-force attacks.

**Token Usage:**
Include the returned token in the `Authorization` header of subsequent requests:
```
Authorization: Bearer <access_token>
```
    """,
    responses={
        HTTPStatusCode.OK: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        400: {
            "description": "Invalid credentials or inactive user",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Invalid email or password",
                            "value": {"detail": "Incorrect email or password"},
                        },
                        "inactive_user": {
                            "summary": "User account is inactive",
                            "value": {"detail": "Inactive user"},
                        },
                    }
                }
            },
        },
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(AUTH_RATE_LIMIT)
def login_access_token(
    request: Request,  # noqa: ARG001 - used by @limiter.limit decorator
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    _csrf: CsrfOriginDep,
) -> Token:
    """Authenticate user and return JWT access token."""
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise AuthenticationError(detail="Incorrect email or password")
    elif not user.is_active:
        raise AppException(code=ErrorCode.AUTH_INACTIVE_USER, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post(
    "/login/test-token",
    response_model=UserPublic,
    summary="Test access token",
    description="""
Validate an access token and return the current user's information.

**Use Cases:**
- Verify token is still valid and not expired
- Retrieve current user profile data
- Check authentication status in frontend applications

**Authentication Required:**
Include the JWT token in the Authorization header.
    """,
    responses={
        200: {
            "description": "Token is valid, returns user data",
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
        403: {"description": "Invalid or expired token"},
    },
)
def test_token(current_user: CurrentUser) -> Any:
    """Validate access token and return current user."""
    return current_user


@router.post(
    "/password-recovery",
    response_model=Message,
    summary="Request password recovery",
    description="""
Initiate password recovery by sending a reset link to the user's email.

**Process:**
1. User provides their registered email address in the JSON request body
2. System generates a time-limited password reset token (valid for 24 hours)
3. An email with reset instructions is sent to the user
4. User clicks the link and is directed to the password reset form

**Rate Limiting:**
Limited to 5 requests per minute to prevent abuse.

**Security Notes:**
- The reset token is a JWT with a short expiration time
- Always returns a generic success response to prevent account enumeration
    """,
    responses={
        200: {
            "description": "Generic password recovery response",
            "content": {
                "application/json": {
                    "example": {"message": PASSWORD_RECOVERY_GENERIC_MESSAGE}
                }
            },
        },
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(AUTH_RATE_LIMIT)
def recover_password(
    request: Request,  # noqa: ARG001 - used by @limiter.limit decorator
    body: PasswordRecoveryRequest,
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Message:
    """Send password recovery email to user."""
    _enqueue_password_recovery_email(
        session=session,
        email=body.email,
        background_tasks=background_tasks,
    )
    return Message(message=PASSWORD_RECOVERY_GENERIC_MESSAGE)


@router.post(
    "/password-recovery/{email}",
    response_model=Message,
    include_in_schema=False,
)
@limiter.limit(AUTH_RATE_LIMIT)
def recover_password_legacy(
    request: Request,  # noqa: ARG001 - used by @limiter.limit decorator
    email: Annotated[
        str,
        Path(
            description="Deprecated compatibility path parameter for password recovery",
            examples=["user@example.com"],
        ),
    ],
    session: SessionDep,
    background_tasks: BackgroundTasks,
) -> Message:
    """Deprecated compatibility endpoint for password recovery."""
    _enqueue_password_recovery_email(
        session=session,
        email=email,
        background_tasks=background_tasks,
    )
    return Message(message=PASSWORD_RECOVERY_GENERIC_MESSAGE)


@router.post(
    "/reset-password/",
    response_model=Message,
    summary="Reset password",
    description="""
Reset a user's password using a valid reset token.

**Requirements:**
- A valid, non-expired password reset token (obtained via password recovery email)
- New password must be 8-128 characters long

**Process:**
1. User receives password recovery email with reset link
2. Link contains a JWT token that identifies the user
3. User submits the token along with their new password
4. System validates the token, updates the password, and returns success

**Rate Limiting:**
Limited to 5 requests per minute.

**Security Notes:**
- Tokens are single-use and expire after 24 hours
- Old password is not required (user may have forgotten it)
- Password is hashed with Argon2id before storage
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
        HTTPStatusCode.UNAUTHORIZED: {
            "description": "Invalid or expired token",
            "content": {"application/json": {"example": {"detail": "Invalid token"}}},
        },
        HTTPStatusCode.FORBIDDEN: {
            "description": "User account is inactive",
            "content": {"application/json": {"example": {"detail": "Inactive user"}}},
        },
        HTTPStatusCode.UNPROCESSABLE_ENTITY: {
            "description": "Validation error (password requirements not met)"
        },
        HTTPStatusCode.TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(AUTH_RATE_LIMIT)
def reset_password(
    request: Request,  # noqa: ARG001 - used by @limiter.limit decorator
    session: SessionDep,
    body: NewPassword,
) -> Message:
    """Reset user password using a valid reset token."""
    token_data = verify_password_reset_token(token=body.token)
    if not token_data:
        raise AuthenticationError(
            code=ErrorCode.AUTH_TOKEN_INVALID, detail="Invalid token"
        )
    user = crud.get_user_by_email(session=session, email=token_data.email)
    if not user:
        raise AuthenticationError(
            code=ErrorCode.AUTH_TOKEN_INVALID, detail="Invalid token"
        )
    if not password_reset_token_matches_user(
        token_data=token_data, current_password_hash=user.hashed_password
    ):
        raise AuthenticationError(
            code=ErrorCode.AUTH_TOKEN_INVALID, detail="Invalid token"
        )
    elif not user.is_active:
        raise AppException(code=ErrorCode.AUTH_INACTIVE_USER, detail="Inactive user")
    crud.update_user(
        session=session,
        db_user=user,
        user_in=UserUpdate(password=body.new_password),
    )
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
    summary="Preview password recovery email",
    description="""
Generate and preview the HTML content of a password recovery email.

**Superuser Only:**
This endpoint is restricted to superusers for administrative purposes.

**Use Cases:**
- Preview email templates during development
- Debug email rendering issues
- Generate manual password reset links for users

**Response:**
Returns the rendered HTML email content with the subject in a response header.
    """,
    responses={
        200: {
            "description": "HTML email content returned",
            "content": {
                "text/html": {
                    "example": "<html><body>Password reset email content...</body></html>"
                }
            },
        },
        401: {"description": "Not authenticated"},
        403: {"description": "Not enough privileges (superuser required)"},
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "The user with this username does not exist in the system."
                    }
                }
            },
        },
    },
)
def recover_password_html_content(
    email: Annotated[
        str,
        Path(
            description="Email address of the user to generate recovery email for",
            examples=["user@example.com"],
        ),
    ],
    session: SessionDep,
) -> Any:
    """Generate password recovery email HTML content for preview."""
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise NotFoundError(resource="User", identifier=email)
    # Use a dummy token for preview - never expose real reset tokens
    dummy_token = "PREVIEW_TOKEN_NOT_VALID_FOR_RESET"
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=dummy_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject": email_data.subject}
    )
