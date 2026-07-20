"""
EXAMPLE: Error handling with RFC 9457 Problem Details.

PATTERN: Structured Error Responses
USE WHEN: Returning a controlled shell error from an API boundary
TAGS: api, error-handling, rfc9457, exceptions

Based on: app/core/exceptions.py, app/core/constants.py
"""

import uuid

from sqlmodel import Session

from app import crud
from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.models import User


def authenticate_user_example(
    *,
    session: Session,
    email: str,
    password: str,
) -> User:
    """Return an active user or one stable semantic authentication error."""

    # The shared helper performs equivalent password work for missing users,
    # preventing this example from introducing an account-enumeration timing
    # shortcut.
    user = crud.authenticate(session=session, email=email, password=password)
    if user is None:
        raise AppException(
            code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise AppException(
            code=ErrorCode.USER_INACTIVE,
            detail="This account has been deactivated",
        )
    return user


def require_self_or_superuser_example(
    *,
    target_user_id: uuid.UUID,
    current_user: User,
) -> None:
    """Reject cross-user access without copying private resource state."""

    if not current_user.is_superuser and current_user.id != target_user_id:
        raise AppException(
            code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            detail="You do not have permission to access this user",
        )


# Active error namespaces:
#
# - AUTH_1xxx: authentication and authorization
# - USER_2xxx: application identity and account erasure
# - VALIDATION_4xxx: malformed or invalid input
# - RATE_5xxx: rate limiting
# - SYSTEM_6xxx: readiness and public engine failures
# - JOB_7xxx: durable course-job contracts
# - SERVER_9xxx: controlled internal failures
#
# Anti-patterns:
#
# - Never expose ``str(exception)`` in a response or routine log.
# - Never use text parsing on the client in place of a semantic error code.
# - Never return a different missing-resource response to an unauthorized user
#   when the resource contract intentionally hides owner existence.
