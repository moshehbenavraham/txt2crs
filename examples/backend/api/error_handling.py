"""
EXAMPLE: Error handling with RFC 9457 Problem Details

PATTERN: Structured Error Responses
USE WHEN: Returning error responses from API endpoints
TAGS: api, error-handling, rfc9457, exceptions

This example demonstrates:
1. Using AppException for structured errors
2. Error codes from constants
3. RFC 9457 Problem Details response format
4. Different exception types for different error categories

Based on: app/core/exceptions.py, app/core/constants.py
"""

import uuid

from sqlmodel import Session, select

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.models import User


def authenticate_user_example(
    *,
    session: Session,
    email: str,
    password: str,
) -> User:
    """
    Example showing proper error handling patterns.

    Demonstrates:
    - Using AppException with ErrorCode
    - Different error codes for different failure modes
    - Descriptive detail messages
    """
    from app.core.security import verify_password

    # Step 1: Find user by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    # Error pattern 1: Resource not found
    if not user:
        # Use USER_NOT_FOUND for missing users
        # This becomes a 404 response automatically
        raise AppException(
            code=ErrorCode.USER_NOT_FOUND,
            detail="No account exists with this email address",
        )

    # Error pattern 2: Invalid credentials
    password_verified, _ = verify_password(password, user.hashed_password)
    if not password_verified:
        # Use AUTH_INVALID_CREDENTIALS for bad password
        # This becomes a 401 response automatically
        raise AppException(
            code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            detail="Invalid email or password",
        )

    # Error pattern 3: Account state issues
    if not user.is_active:
        # Use USER_INACTIVE for disabled accounts
        raise AppException(
            code=ErrorCode.USER_INACTIVE,
            detail="This account has been deactivated",
        )

    return user


def check_resource_ownership_example(
    *,
    session: Session,
    resource_id: uuid.UUID,
    user_id: uuid.UUID,
    is_superuser: bool = False,
) -> None:
    """
    Example showing permission check error patterns.
    """
    from app.models import Item

    # Step 1: Check resource exists
    item = session.get(Item, resource_id)
    if not item:
        raise AppException(
            code=ErrorCode.ITEM_NOT_FOUND,
            detail=f"Item with ID '{resource_id}' not found",
        )

    # Step 2: Check ownership (superusers bypass)
    if not is_superuser and item.owner_id != user_id:
        raise AppException(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail="You do not have permission to access this resource",
        )


# === ERROR CODE REFERENCE ===
#
# Authentication errors (1xxx):
#   AUTH_INVALID_CREDENTIALS = "AUTH_1001"  # 401
#   AUTH_TOKEN_EXPIRED = "AUTH_1002"        # 401
#   AUTH_TOKEN_INVALID = "AUTH_1003"        # 401
#   AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_1004"  # 403
#
# User errors (2xxx):
#   USER_NOT_FOUND = "USER_2001"            # 404
#   USER_ALREADY_EXISTS = "USER_2002"       # 409
#   USER_EMAIL_NOT_VERIFIED = "USER_2003"   # 403
#   USER_INACTIVE = "USER_2004"             # 403
#
# Item errors (3xxx):
#   ITEM_NOT_FOUND = "ITEM_3001"            # 404
#   ITEM_ALREADY_EXISTS = "ITEM_3002"       # 409
#
# Validation errors (4xxx):
#   VALIDATION_ERROR = "VALIDATION_4001"    # 422
#   INVALID_INPUT = "VALIDATION_4002"       # 400
#
# Rate limiting (5xxx):
#   RATE_LIMIT_EXCEEDED = "RATE_5001"       # 429
#
# Server errors (9xxx):
#   INTERNAL_ERROR = "SERVER_9001"          # 500
#   SERVICE_UNAVAILABLE = "SERVER_9002"     # 503


# === RFC 9457 RESPONSE FORMAT ===
#
# When AppException is raised, it produces this response:
#
# {
#   "type": "https://api.example.com/problems/AUTH_1001",
#   "title": "Auth Invalid Credentials",
#   "status": 401,
#   "detail": "Invalid email or password",
#   "code": "AUTH_1001",
#   "trace_id": "abc-123-def-456"
# }
#
# The trace_id allows correlation with logs for debugging.


# === ANTI-PATTERN: DON'T DO THIS ===
#
# # BAD: Generic HTTPException without semantic code
# raise HTTPException(status_code=401, detail="Invalid credentials")
#
# # BAD: Exposing internal error details
# raise HTTPException(status_code=500, detail=str(exception))
#
# # BAD: Using wrong status code
# raise HTTPException(status_code=400, detail="User not found")  # Should be 404
#
# # GOOD: Use AppException with proper ErrorCode
# raise AppException(
#     code=ErrorCode.AUTH_INVALID_CREDENTIALS,
#     detail="Invalid email or password",
# )
