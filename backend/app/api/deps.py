"""
FastAPI dependency injection functions and type aliases.

This module provides reusable dependencies for FastAPI route handlers including:
- Database session management
- JWT token extraction and validation
- User authentication and authorization

Type Aliases:
    SessionDep: Annotated type for database session injection
    TokenDep: Annotated type for JWT token extraction
    CurrentUser: Annotated type for authenticated user injection

Usage:
    from app.api.deps import SessionDep, CurrentUser

    @router.get("/profile")
    def get_profile(current_user: CurrentUser):
        # current_user is the authenticated User object
        return current_user

Security Model:
    - OAuth2 password flow with JWT Bearer tokens
    - Token validation includes expiration and signature verification
    - User existence and active status are verified on each request

Note:
    The dependency injection pattern ensures that resources like database
    sessions are properly managed and cleaned up after each request.
"""

from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from txt2crs.application import Txt2CrsApplication

from app.core import security
from app.core.config import settings
from app.core.constants import ErrorCode, ErrorMessages
from app.core.db import engine
from app.core.exceptions import AppException, AuthenticationError, AuthorizationError
from app.models import TokenPayload, User
from app.services.txt2crs_authentication import SystemAuthenticationCoordinator
from app.services.txt2crs_readiness import CachedReadinessCoordinator
from app.services.txt2crs_submission import Txt2CrsSubmissionService
from app.services.txt2crs_worker import SerialTxt2CrsWorker

# OAuth2 scheme for extracting Bearer tokens from Authorization header
# Points to the login endpoint for automatic documentation
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session]:
    """
    Create a database session for a single request.

    This dependency provides a SQLModel Session that is automatically
    closed when the request completes. Uses a context manager to ensure
    proper cleanup even if an exception occurs.

    Yields:
        A SQLModel Session connected to the database engine.

    Example:
        >>> @router.get("/users")
        >>> def get_users(session: SessionDep):
        ...     return session.exec(select(User)).all()

    Note:
        Each request gets its own session. Sessions are not shared between
        requests to ensure proper transaction isolation.
    """
    with Session(engine) as session:
        yield session


# Type alias for database session dependency injection
# Use this in route function signatures: def handler(session: SessionDep)
SessionDep = Annotated[Session, Depends(get_db)]

# Type alias for JWT token extraction from Authorization header
# The token is extracted but not validated at this stage
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """
    Validate JWT token and return the authenticated user.

    This dependency extracts the user from a JWT Bearer token by:
    1. Decoding and validating the token signature and expiration
    2. Extracting the user ID from the token's 'sub' claim
    3. Fetching the user from the database
    4. Verifying the user exists and is active

    Args:
        session: Database session for user lookup.
        token: JWT token extracted from the Authorization header.

    Returns:
        The authenticated User object if all validations pass.

    Raises:
        AuthenticationError: If the token is invalid, expired, or malformed.
        AuthenticationError: If the user ID in the token doesn't exist.
        AuthorizationError: If the user account is inactive.

    Example:
        >>> @router.get("/me")
        >>> def get_me(current_user: CurrentUser):
        ...     return current_user

    Security Note:
        This function is called on every authenticated request, ensuring
        that even if a user is deactivated, their existing tokens will
        stop working immediately.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        raise AuthenticationError(
            code=ErrorCode.AUTH_TOKEN_INVALID,
            detail=ErrorMessages.TOKEN_INVALID,
        ) from None
    user = session.get(User, token_data.sub)
    if not user:
        raise AuthenticationError(
            code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            detail=ErrorMessages.TOKEN_INVALID,
        )
    if not user.is_active:
        raise AuthorizationError(
            code=ErrorCode.AUTH_INACTIVE_USER,
            detail=ErrorMessages.INACTIVE_USER,
        )
    return user


# Type alias for authenticated user dependency injection
# Use this in route function signatures: def handler(current_user: CurrentUser)
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """
    Verify the current user has superuser privileges.

    This dependency extends get_current_user to additionally check that
    the authenticated user has superuser (admin) privileges. Use this
    for administrative endpoints.

    Args:
        current_user: The authenticated user from get_current_user dependency.

    Returns:
        The authenticated User object if they are a superuser.

    Raises:
        AuthorizationError: If the user is not a superuser.

    Example:
        >>> @router.delete("/users/{user_id}")
        >>> def delete_user(
        ...     user_id: UUID,
        ...     superuser: Annotated[User, Depends(get_current_active_superuser)]
        ... ):
        ...     # Only superusers can reach this code
        ...     ...

    Note:
        This dependency chains with get_current_user, so all authentication
        checks are performed first. A non-authenticated request will receive
        a 401/403 before this check is reached.
    """
    if not current_user.is_superuser:
        raise AuthorizationError(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail=ErrorMessages.USER_SUPERUSER_REQUIRED,
        )
    return current_user


def validate_csrf_origin(request: Request) -> None:
    """Validate Origin header against allowed CORS origins for form-encoded endpoints.

    Defense-in-depth CSRF protection for endpoints that accept
    ``application/x-www-form-urlencoded`` bodies (e.g. OAuth2 password flow).

    Rules:
        - If Origin header is present and does NOT match any allowed CORS
          origin, the request is rejected with 403.
        - If Origin header is absent (curl, Postman, server-to-server),
          the request is allowed for API client compatibility.

    Raises:
        AuthorizationError: When Origin is present but not in the allowed list.
    """
    origin = request.headers.get("origin")
    if origin is None:
        return
    allowed = settings.all_cors_origins
    if origin.rstrip("/") not in allowed:
        raise AuthorizationError(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail="Cross-origin form submission is not allowed",
        )


CsrfOriginDep = Annotated[None, Depends(validate_csrf_origin)]


def get_txt2crs_readiness(request: Request) -> CachedReadinessCoordinator:
    """Return the lifespan cache or fail closed before route work begins."""

    readiness = getattr(request.app.state, "txt2crs_readiness", None)
    if not isinstance(readiness, CachedReadinessCoordinator):
        raise AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="The course system is not ready.",
        )
    return readiness


def get_txt2crs_application(request: Request) -> Txt2CrsApplication:
    """Return only the facade owned by the active FastAPI lifespan."""

    lifecycle = getattr(request.app.state, "txt2crs_lifecycle", None)
    application = getattr(lifecycle, "application", None)
    if not isinstance(application, Txt2CrsApplication):
        raise AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="The course system is not ready.",
        )
    return application


def get_txt2crs_worker(request: Request) -> SerialTxt2CrsWorker:
    """Return the active serial worker or reject before route work."""

    worker = getattr(request.app.state, "txt2crs_worker", None)
    if not isinstance(worker, SerialTxt2CrsWorker):
        raise AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="The course worker is not ready.",
        )
    return worker


def get_txt2crs_submission(request: Request) -> Txt2CrsSubmissionService:
    """Return the startup-composed submission adapter without provider work."""

    submission = getattr(request.app.state, "txt2crs_submission", None)
    if not isinstance(submission, Txt2CrsSubmissionService):
        raise AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="Course job submission is unavailable.",
        )
    return submission


def get_txt2crs_authentication(
    request: Request,
) -> SystemAuthenticationCoordinator:
    """Return the lifespan authentication cache without touching providers."""

    authentication = getattr(request.app.state, "txt2crs_authentication", None)
    if not isinstance(authentication, SystemAuthenticationCoordinator):
        raise AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="System authentication is unavailable.",
        )
    return authentication


Txt2CrsReadinessDep = Annotated[
    CachedReadinessCoordinator,
    Depends(get_txt2crs_readiness),
]
Txt2CrsApplicationDep = Annotated[
    Txt2CrsApplication,
    Depends(get_txt2crs_application),
]
Txt2CrsWorkerDep = Annotated[
    SerialTxt2CrsWorker,
    Depends(get_txt2crs_worker),
]
Txt2CrsSubmissionDep = Annotated[
    Txt2CrsSubmissionService,
    Depends(get_txt2crs_submission),
]
Txt2CrsAuthenticationDep = Annotated[
    SystemAuthenticationCoordinator,
    Depends(get_txt2crs_authentication),
]
