"""
RFC 9457 Problem Details exception handling.

This module provides structured exceptions that produce machine-readable
error responses following the RFC 9457 Problem Details specification.

Usage:
    from app.core.exceptions import AppException, NotFoundError
    from app.core.constants import ErrorCode

    # Generic exception
    raise AppException(
        code=ErrorCode.USER_NOT_FOUND,
        detail="User with this email does not exist"
    )

    # Convenience exceptions
    raise NotFoundError(resource="User", identifier="abc-123")
    raise AuthenticationError()
    raise ValidationError(errors=[{"field": "email", "message": "Invalid format"}])

Response Format (RFC 9457):
    {
        "type": "https://api.example.com/problems/USER_2001",
        "title": "User Not Found",
        "status": 404,
        "detail": "User with this email does not exist",
        "code": "USER_2001",
        "trace_id": "abc-123-def-456"
    }
"""

from typing import Any

from pydantic import BaseModel

from app.core.constants import ERROR_STATUS_MAP, ErrorCode
from app.core.logging import trace_id_var


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Details response format.

    All API errors are returned in this standardized format for
    consistent, machine-parseable error handling.

    Attributes:
        type: URI reference identifying the problem type
        title: Short, human-readable summary
        status: HTTP status code
        detail: Human-readable explanation specific to this occurrence
        instance: URI reference to specific occurrence (optional)
        code: Machine-readable error code from ErrorCode enum
        errors: Validation error details (optional, for VALIDATION_ERROR)
        trace_id: Request correlation ID for error tracking

    Example:
        >>> problem = ProblemDetail(
        ...     type="https://api.example.com/problems/USER_2001",
        ...     title="User Not Found",
        ...     status=404,
        ...     code=ErrorCode.USER_NOT_FOUND,
        ...     detail="User with ID 'abc-123' not found",
        ... )
    """

    type: str = "about:blank"
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    code: ErrorCode
    errors: list[dict[str, Any]] | None = None
    trace_id: str | None = None


class AppException(Exception):
    """Base exception with structured RFC 9457 error details.

    Use this exception for all application-level errors. It automatically
    maps error codes to HTTP status codes and formats responses as
    RFC 9457 Problem Details.

    Args:
        code: Semantic error code from ErrorCode enum
        detail: Human-readable error explanation
        errors: List of validation errors (for VALIDATION_ERROR)

    Example:
        >>> from app.core.constants import ErrorCode
        >>> raise AppException(
        ...     code=ErrorCode.USER_NOT_FOUND,
        ...     detail="User with this email does not exist"
        ... )
    """

    def __init__(
        self,
        code: ErrorCode,
        detail: str | None = None,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.code = code
        self.status = ERROR_STATUS_MAP.get(code, 500)
        self.detail = detail
        self.errors = errors
        super().__init__(detail or code.value)

    def to_problem_detail(self) -> ProblemDetail:
        """Convert exception to RFC 9457 Problem Details format.

        Returns:
            ProblemDetail model ready for JSON serialization
        """
        return ProblemDetail(
            type=f"https://api.example.com/problems/{self.code.value}",
            title=self.code.name.replace("_", " ").title(),
            status=self.status,
            detail=self.detail,
            code=self.code,
            errors=self.errors,
            trace_id=trace_id_var.get() or None,
        )


# Convenience exception classes for common error types


class AuthenticationError(AppException):
    """Exception for authentication failures.

    Example:
        >>> raise AuthenticationError()  # Uses default message
        >>> raise AuthenticationError(detail="Token has expired")
    """

    def __init__(
        self,
        code: ErrorCode = ErrorCode.AUTH_INVALID_CREDENTIALS,
        detail: str | None = None,
    ) -> None:
        super().__init__(code, detail)


class AuthorizationError(AppException):
    """Exception for authorization/permission failures.

    Example:
        >>> raise AuthorizationError()
        >>> raise AuthorizationError(detail="Admin access required")
    """

    def __init__(
        self,
        code: ErrorCode = ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
        detail: str | None = None,
    ) -> None:
        super().__init__(code, detail)


class NotFoundError(AppException):
    """Exception for a shell-owned user that was not found.

    Args:
        resource: Public resource label used in the safe detail.
        identifier: Resource identifier that was not found

    Example:
        >>> raise NotFoundError(resource="User", identifier="abc-123")
        # Produces: "User with ID 'abc-123' not found"
    """

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            code=ErrorCode.USER_NOT_FOUND,
            detail=f"{resource} with ID '{identifier}' not found",
        )


class ConflictError(AppException):
    """Exception for resource conflict errors (e.g., duplicate).

    Example:
        >>> raise ConflictError(
        ...     code=ErrorCode.USER_ALREADY_EXISTS,
        ...     detail="User with this email already exists"
        ... )
    """

    def __init__(self, code: ErrorCode, detail: str) -> None:
        super().__init__(code, detail)


class ValidationError(AppException):
    """Exception for input validation failures.

    Args:
        errors: List of validation error details
        detail: Optional summary message

    Example:
        >>> raise ValidationError(errors=[
        ...     {"field": "email", "message": "Invalid email format"},
        ...     {"field": "password", "message": "Too short"},
        ... ])
    """

    def __init__(
        self,
        errors: list[dict[str, Any]] | None = None,
        detail: str = "One or more fields failed validation",
    ) -> None:
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            detail=detail,
            errors=errors,
        )


class RateLimitError(AppException):
    """Exception for rate limit exceeded.

    Example:
        >>> raise RateLimitError()
        >>> raise RateLimitError(detail="Try again in 60 seconds")
    """

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            code=ErrorCode.RATE_LIMIT_EXCEEDED,
            detail=detail or "Too many requests. Please try again later.",
        )


class InternalError(AppException):
    """Exception for internal server errors.

    Use sparingly - prefer specific error codes when possible.

    Example:
        >>> raise InternalError(detail="Database connection failed")
    """

    def __init__(
        self,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        detail: str | None = None,
    ) -> None:
        super().__init__(code, detail or "An unexpected error occurred")
