"""
Exception handlers for FastAPI application.

This module provides centralized exception handlers that convert
exceptions to RFC 9457 Problem Details format.

Usage:
    In main.py:
        from app.core.exception_handlers import register_exception_handlers
        register_exception_handlers(app)
"""

from typing import cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.types import ExceptionHandler

from app.core.constants import (
    ContentTypes,
    ErrorCode,
    ErrorMessages,
    HTTPStatusCode,
)
from app.core.exceptions import AppException, ProblemDetail
from app.core.logging import get_logger, trace_id_var

logger = get_logger(__name__)


def _build_problem_detail(
    *,
    code: ErrorCode,
    status: int,
    detail: str | None = None,
    errors: list[dict[str, str]] | None = None,
) -> ProblemDetail:
    """Create a standard Problem Detail payload for an error code."""
    return ProblemDetail(
        type=f"https://api.example.com/problems/{code.value}",
        title=code.name.replace("_", " ").title(),
        status=status,
        detail=detail,
        code=code,
        errors=errors,
        trace_id=trace_id_var.get() or None,
    )


def _normalize_http_error_detail(detail: object) -> str:
    """Normalize FastAPI HTTPException detail values to string."""
    if isinstance(detail, str):
        return detail
    if detail is None:
        return ""
    return str(detail)


def _map_http_exception_to_error_code(status_code: int, detail: str) -> ErrorCode:
    """Map legacy HTTPException status/detail pairs to semantic codes."""
    detail_lc = detail.lower()

    if "not enough permissions" in detail_lc or "enough privileges" in detail_lc:
        return ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS
    if "inactive user" in detail_lc:
        return ErrorCode.AUTH_INACTIVE_USER
    if "incorrect email or password" in detail_lc:
        return ErrorCode.AUTH_INVALID_CREDENTIALS
    if (
        "could not validate credentials" in detail_lc
        or "not authenticated" in detail_lc
    ):
        return ErrorCode.AUTH_TOKEN_INVALID
    if "invalid token" in detail_lc:
        return ErrorCode.AUTH_TOKEN_INVALID

    if "password cannot be the same as the current one" in detail_lc:
        return ErrorCode.USER_PASSWORD_MISMATCH
    if "incorrect password" in detail_lc:
        return ErrorCode.USER_INVALID_PASSWORD
    if "already exists" in detail_lc:
        return ErrorCode.USER_ALREADY_EXISTS
    if "item not found" in detail_lc:
        return ErrorCode.ITEM_NOT_FOUND
    if "user not found" in detail_lc or "user with this" in detail_lc:
        return ErrorCode.USER_NOT_FOUND

    if status_code == HTTPStatusCode.UNAUTHORIZED:
        return ErrorCode.AUTH_TOKEN_INVALID
    if status_code == HTTPStatusCode.FORBIDDEN:
        return ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS
    if status_code == HTTPStatusCode.NOT_FOUND:
        return ErrorCode.USER_NOT_FOUND
    if status_code == HTTPStatusCode.CONFLICT:
        return ErrorCode.USER_ALREADY_EXISTS
    if status_code == HTTPStatusCode.UNPROCESSABLE_ENTITY:
        return ErrorCode.VALIDATION_ERROR
    if status_code == HTTPStatusCode.TOO_MANY_REQUESTS:
        return ErrorCode.RATE_LIMIT_EXCEEDED
    if status_code >= HTTPStatusCode.INTERNAL_SERVER_ERROR:
        return ErrorCode.INTERNAL_ERROR
    return ErrorCode.INVALID_INPUT


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Handle AppException with RFC 9457 Problem Details format.

    Args:
        request: FastAPI request object
        exc: AppException instance

    Returns:
        JSONResponse with Problem Details format
    """
    problem = exc.to_problem_detail()

    logger.warning(
        "app.exception_handled",
        extra={
            "error_code": exc.code.value,
            "status": exc.status,
            "detail": exc.detail,
            "path": str(request.scope.get("path", "")),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status,
        content=problem.model_dump(exclude_none=True),
        media_type=ContentTypes.PROBLEM_JSON,
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Convert Pydantic validation errors to RFC 9457 Problem Details format.

    Args:
        request: FastAPI request object
        exc: RequestValidationError from Pydantic

    Returns:
        JSONResponse with Problem Details format including field errors
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": ".".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    problem = _build_problem_detail(
        code=ErrorCode.VALIDATION_ERROR,
        status=HTTPStatusCode.UNPROCESSABLE_ENTITY,
        detail=ErrorMessages.VALIDATION_FAILED,
        errors=errors,
    )

    logger.warning(
        "validation.request_failed",
        extra={
            "error_count": len(errors),
            "path": str(request.scope.get("path", "")),
            "method": request.method,
            "errors": errors,
        },
    )

    return JSONResponse(
        status_code=HTTPStatusCode.UNPROCESSABLE_ENTITY,
        content=problem.model_dump(exclude_none=True),
        media_type=ContentTypes.PROBLEM_JSON,
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Convert FastAPI HTTPException responses to RFC 9457 Problem Details."""
    detail = _normalize_http_error_detail(exc.detail)
    code = _map_http_exception_to_error_code(exc.status_code, detail)
    problem = _build_problem_detail(
        code=code,
        status=exc.status_code,
        detail=detail or None,
    )

    logger.warning(
        "http_exception.handled",
        extra={
            "error_code": code.value,
            "status": exc.status_code,
            "detail": detail,
            "path": str(request.scope.get("path", "")),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=problem.model_dump(exclude_none=True),
        media_type=ContentTypes.PROBLEM_JSON,
    )


async def rate_limit_exception_handler(
    request: Request,
    exc: RateLimitExceeded,  # noqa: ARG001 - included for handler signature
) -> JSONResponse:
    """Normalize rate-limit responses to RFC 9457 Problem Details."""
    problem = _build_problem_detail(
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        status=HTTPStatusCode.TOO_MANY_REQUESTS,
        detail=ErrorMessages.RATE_LIMIT_EXCEEDED,
    )

    logger.warning(
        "rate_limit.request_rejected",
        extra={
            "error_code": ErrorCode.RATE_LIMIT_EXCEEDED.value,
            "status": HTTPStatusCode.TOO_MANY_REQUESTS,
            "path": str(request.scope.get("path", "")),
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=HTTPStatusCode.TOO_MANY_REQUESTS,
        content=problem.model_dump(exclude_none=True),
        media_type=ContentTypes.PROBLEM_JSON,
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected exceptions with RFC 9457 Problem Details format.

    Args:
        request: FastAPI request object
        exc: Unhandled exception

    Returns:
        JSONResponse with Problem Details format (generic server error)
    """
    problem = _build_problem_detail(
        code=ErrorCode.INTERNAL_ERROR,
        status=HTTPStatusCode.INTERNAL_SERVER_ERROR,
        detail=ErrorMessages.INTERNAL_ERROR,
    )

    logger.error(
        "server.unhandled_exception",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": str(request.scope.get("path", "")),
            "method": request.method,
        },
        exc_info=True,
    )

    return JSONResponse(
        status_code=HTTPStatusCode.INTERNAL_SERVER_ERROR,
        content=problem.model_dump(exclude_none=True),
        media_type=ContentTypes.PROBLEM_JSON,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application.

    Args:
        app: FastAPI application instance

    Usage:
        >>> from app.core.exception_handlers import register_exception_handlers
        >>> register_exception_handlers(app)
    """
    app.add_exception_handler(
        AppException,
        cast(ExceptionHandler, app_exception_handler),
    )
    app.add_exception_handler(
        RequestValidationError,
        cast(ExceptionHandler, validation_exception_handler),
    )
    app.add_exception_handler(
        HTTPException,
        cast(ExceptionHandler, http_exception_handler),
    )
    app.add_exception_handler(
        RateLimitExceeded,
        cast(ExceptionHandler, rate_limit_exception_handler),
    )
    app.add_exception_handler(
        Exception,
        generic_exception_handler,
    )
