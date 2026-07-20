"""
Application-wide constants and enumerations.

This module centralizes magic strings, status codes, and other constants
to ensure consistency across the codebase and make it easier for AI agents
to understand and use the correct values.

Usage:
    from app.core.constants import HTTPStatusCode, ErrorMessages, ContentTypes

Note:
    Prefer using these constants over hardcoded strings/numbers throughout
    the application to maintain consistency and enable easy refactoring.
"""

from enum import IntEnum, StrEnum
from typing import Final


class HTTPStatusCode(IntEnum):
    """Standard HTTP status codes used in API responses.

    Use these constants instead of hardcoded integers for better
    readability and IDE support.

    Example:
        >>> from app.core.constants import HTTPStatusCode
        >>> raise HTTPException(status_code=HTTPStatusCode.NOT_FOUND)
    """

    # Success codes (2xx)
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # Redirection (3xx)
    MOVED_PERMANENTLY = 301
    FOUND = 302
    NOT_MODIFIED = 304

    # Client errors (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    GONE = 410
    PAYLOAD_TOO_LARGE = 413
    UNSUPPORTED_MEDIA_TYPE = 415
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server errors (5xx)
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503


class ErrorCode(StrEnum):
    """Semantic error codes for programmatic handling.

    Error code ranges:
        - 1xxx: Authentication errors
        - 2xxx: User-related errors
        - 4xxx: Validation errors
        - 5xxx: Rate limiting errors
        - 6xxx: System readiness and engine errors
        - 7xxx: Durable course-job errors
        - 9xxx: Server/internal errors

    Example:
        >>> from app.core.constants import ErrorCode
        >>> return ProblemDetail(code=ErrorCode.USER_NOT_FOUND)
    """

    # Authentication errors (1xxx)
    AUTH_INVALID_CREDENTIALS = "AUTH_1001"
    AUTH_TOKEN_EXPIRED = "AUTH_1002"
    AUTH_TOKEN_INVALID = "AUTH_1003"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_1004"
    AUTH_INACTIVE_USER = "AUTH_1005"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_1006"

    # User errors (2xxx)
    USER_NOT_FOUND = "USER_2001"
    USER_ALREADY_EXISTS = "USER_2002"
    USER_EMAIL_NOT_VERIFIED = "USER_2003"
    USER_INACTIVE = "USER_2004"
    USER_INVALID_PASSWORD = "USER_2005"
    USER_PASSWORD_MISMATCH = "USER_2006"
    USER_PURGE_FAILED = "USER_2007"

    # Validation errors (4xxx)
    VALIDATION_ERROR = "VALIDATION_4001"
    INVALID_INPUT = "VALIDATION_4002"
    MISSING_REQUIRED_FIELD = "VALIDATION_4003"
    INVALID_FORMAT = "VALIDATION_4004"

    # Rate limiting (5xxx)
    RATE_LIMIT_EXCEEDED = "RATE_5001"

    # System readiness and engine boundary errors (6xxx)
    SYSTEM_NOT_READY = "SYSTEM_6001"
    ENGINE_OPERATION_FAILED = "SYSTEM_6002"
    SYSTEM_AUTH_FAILED = "SYSTEM_6003"

    # Durable course-job errors (7xxx)
    JOB_NOT_FOUND = "JOB_7001"
    JOB_ADMISSION_REJECTED = "JOB_7002"
    JOB_IDEMPOTENCY_CONFLICT = "JOB_7003"
    JOB_CONFLICT = "JOB_7004"
    JOB_PAYLOAD_TOO_LARGE = "JOB_7005"
    JOB_UNSUPPORTED_MEDIA = "JOB_7006"
    JOB_POLICY_REJECTED = "JOB_7007"

    # Server errors (9xxx)
    INTERNAL_ERROR = "SERVER_9001"
    SERVICE_UNAVAILABLE = "SERVER_9002"
    DATABASE_ERROR = "SERVER_9003"
    EXTERNAL_SERVICE_ERROR = "SERVER_9004"


class ErrorMessages:
    """User-friendly error message templates.

    Use these predefined messages for consistent error responses.

    Example:
        >>> from app.core.constants import ErrorMessages
        >>> detail = ErrorMessages.USER_NOT_FOUND.format(email=email)
    """

    # Authentication messages
    INVALID_CREDENTIALS: Final = "Incorrect email or password"
    TOKEN_EXPIRED: Final = "Token has expired"
    TOKEN_INVALID: Final = "Could not validate credentials"
    INSUFFICIENT_PERMISSIONS: Final = "Not enough permissions"
    INACTIVE_USER: Final = "Inactive user"

    # User messages
    USER_NOT_FOUND: Final = "User not found"
    USER_NOT_FOUND_BY_EMAIL: Final = "User with email '{email}' not found"
    USER_ALREADY_EXISTS: Final = "User with this email already exists"
    USER_SUPERUSER_REQUIRED: Final = "The user doesn't have enough privileges"
    INVALID_CURRENT_PASSWORD: Final = "Current password is incorrect"
    PASSWORD_SAME_AS_CURRENT: Final = (
        "New password cannot be the same as the current password"
    )
    ACCOUNT_PURGE_FAILED: Final = (
        "Account deletion is temporarily unavailable. Please retry."
    )

    # Validation messages
    VALIDATION_FAILED: Final = "One or more fields failed validation"
    REQUIRED_FIELD_MISSING: Final = "Field '{field}' is required"
    INVALID_EMAIL_FORMAT: Final = "Invalid email format"
    PASSWORD_TOO_SHORT: Final = "Password must be at least {min_length} characters"
    PASSWORD_TOO_LONG: Final = "Password must be at most {max_length} characters"

    # Rate limiting
    RATE_LIMIT_EXCEEDED: Final = "Too many requests. Please try again later."

    # Server errors
    INTERNAL_ERROR: Final = "An unexpected error occurred"
    SERVICE_UNAVAILABLE: Final = "Service temporarily unavailable"


class ContentTypes:
    """MIME content types used in API responses.

    Example:
        >>> from app.core.constants import ContentTypes
        >>> return JSONResponse(media_type=ContentTypes.PROBLEM_JSON)
    """

    JSON: Final = "application/json"
    PROBLEM_JSON: Final = "application/problem+json"
    TEXT_PLAIN: Final = "text/plain"
    TEXT_HTML: Final = "text/html"
    FORM_URLENCODED: Final = "application/x-www-form-urlencoded"
    MULTIPART_FORM: Final = "multipart/form-data"


class Pagination:
    """Pagination-related constants.

    Example:
        >>> from app.core.constants import Pagination
        >>> requested_limit = 250
        >>> page_size = min(requested_limit, Pagination.MAX_LIMIT)
    """

    DEFAULT_SKIP: Final = 0
    DEFAULT_LIMIT: Final = 20
    MAX_LIMIT: Final = 100
    MAX_EXPORT_LIMIT: Final = 1000


class TokenSettings:
    """JWT token configuration constants.

    These values may be overridden by environment configuration
    but provide sensible defaults.

    Example:
        >>> from app.core.constants import TokenSettings
        >>> delta = timedelta(minutes=TokenSettings.ACCESS_TOKEN_EXPIRE_MINUTES)
    """

    ACCESS_TOKEN_EXPIRE_MINUTES: Final = 60 * 24  # 24 hours
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: Final = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: Final = 48
    TOKEN_TYPE: Final = "bearer"
    TOKEN_ALGORITHM: Final = "HS256"


class PasswordPolicy:
    """Password validation policy constants.

    Example:
        >>> from app.core.constants import PasswordPolicy
        >>> if len(password) < PasswordPolicy.MIN_LENGTH:
        ...     raise ValueError("Password too short")
    """

    MIN_LENGTH: Final = 8
    MAX_LENGTH: Final = 128


# Error code to HTTP status mapping
ERROR_STATUS_MAP: dict[ErrorCode, int] = {
    ErrorCode.AUTH_INVALID_CREDENTIALS: HTTPStatusCode.UNAUTHORIZED,
    ErrorCode.AUTH_TOKEN_EXPIRED: HTTPStatusCode.UNAUTHORIZED,
    ErrorCode.AUTH_TOKEN_INVALID: HTTPStatusCode.UNAUTHORIZED,
    ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS: HTTPStatusCode.FORBIDDEN,
    ErrorCode.AUTH_INACTIVE_USER: HTTPStatusCode.FORBIDDEN,
    ErrorCode.AUTH_EMAIL_NOT_VERIFIED: HTTPStatusCode.FORBIDDEN,
    ErrorCode.USER_NOT_FOUND: HTTPStatusCode.NOT_FOUND,
    ErrorCode.USER_ALREADY_EXISTS: HTTPStatusCode.CONFLICT,
    ErrorCode.USER_EMAIL_NOT_VERIFIED: HTTPStatusCode.FORBIDDEN,
    ErrorCode.USER_INACTIVE: HTTPStatusCode.FORBIDDEN,
    ErrorCode.USER_INVALID_PASSWORD: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.USER_PASSWORD_MISMATCH: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.USER_PURGE_FAILED: HTTPStatusCode.SERVICE_UNAVAILABLE,
    ErrorCode.VALIDATION_ERROR: HTTPStatusCode.UNPROCESSABLE_ENTITY,
    ErrorCode.INVALID_INPUT: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.MISSING_REQUIRED_FIELD: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.INVALID_FORMAT: HTTPStatusCode.BAD_REQUEST,
    ErrorCode.RATE_LIMIT_EXCEEDED: HTTPStatusCode.TOO_MANY_REQUESTS,
    ErrorCode.SYSTEM_NOT_READY: HTTPStatusCode.SERVICE_UNAVAILABLE,
    ErrorCode.ENGINE_OPERATION_FAILED: HTTPStatusCode.INTERNAL_SERVER_ERROR,
    ErrorCode.SYSTEM_AUTH_FAILED: HTTPStatusCode.BAD_GATEWAY,
    ErrorCode.JOB_NOT_FOUND: HTTPStatusCode.NOT_FOUND,
    ErrorCode.JOB_ADMISSION_REJECTED: HTTPStatusCode.TOO_MANY_REQUESTS,
    ErrorCode.JOB_IDEMPOTENCY_CONFLICT: HTTPStatusCode.CONFLICT,
    ErrorCode.JOB_CONFLICT: HTTPStatusCode.CONFLICT,
    ErrorCode.JOB_PAYLOAD_TOO_LARGE: HTTPStatusCode.PAYLOAD_TOO_LARGE,
    ErrorCode.JOB_UNSUPPORTED_MEDIA: HTTPStatusCode.UNSUPPORTED_MEDIA_TYPE,
    ErrorCode.JOB_POLICY_REJECTED: HTTPStatusCode.UNPROCESSABLE_ENTITY,
    ErrorCode.INTERNAL_ERROR: HTTPStatusCode.INTERNAL_SERVER_ERROR,
    ErrorCode.SERVICE_UNAVAILABLE: HTTPStatusCode.SERVICE_UNAVAILABLE,
    ErrorCode.DATABASE_ERROR: HTTPStatusCode.INTERNAL_SERVER_ERROR,
    ErrorCode.EXTERNAL_SERVICE_ERROR: HTTPStatusCode.BAD_GATEWAY,
}
