"""Central safe translation for public txt2crs package exceptions."""

from txt2crs.application import (
    ApplicationClosedError,
    ApplicationCloseError,
    ExecutorAlreadyUsedError,
    OwnerPurgeError,
    SystemAuthenticationError,
)
from txt2crs.jobs import (
    AdmissionQuotaExceededError,
    ArtifactIntegrityError,
    ConcurrencyConflictError,
    IdempotencyConflictError,
    InvalidJobSubmissionError,
    JobNotFoundError,
    JobRequestCompatibilityError,
    PreparationPolicyError,
    PublicJobProjectionError,
)

from app.core.constants import ErrorCode, ErrorMessages
from app.core.exceptions import AppException


def translate_txt2crs_exception(error: Exception) -> AppException:
    """
    Return one context-free shell error without copying package error text.

    Route handlers should raise the returned exception ``from None``. Keeping
    the mapping here prevents each endpoint from learning private engine
    failure shapes or accidentally reflecting provider and filesystem detail.
    """

    if isinstance(error, ApplicationClosedError):
        translated = AppException(
            code=ErrorCode.SYSTEM_NOT_READY,
            detail="The course system is not ready.",
        )
    elif isinstance(error, SystemAuthenticationError):
        translated = AppException(
            code=ErrorCode.SYSTEM_AUTH_FAILED,
            detail="System authentication could not be completed.",
        )
    elif isinstance(error, AdmissionQuotaExceededError):
        translated = AppException(
            code=ErrorCode.JOB_ADMISSION_REJECTED,
            detail="Course job admission capacity is unavailable.",
        )
    elif isinstance(error, IdempotencyConflictError):
        translated = AppException(
            code=ErrorCode.JOB_IDEMPOTENCY_CONFLICT,
            detail="The request key was already used for different work.",
        )
    elif isinstance(error, PreparationPolicyError):
        translated = AppException(
            code=ErrorCode.JOB_POLICY_REJECTED,
            detail="This course request cannot be processed automatically.",
        )
    elif isinstance(error, JobNotFoundError):
        translated = AppException(
            code=ErrorCode.JOB_NOT_FOUND,
            detail="The requested course job was not found.",
        )
    elif isinstance(error, OwnerPurgeError):
        # Account deletion is the only shell operation that invokes owner
        # purge. Report a retryable account error without retaining artifact,
        # SQLite, executor, or provider context from the package exception.
        translated = AppException(
            code=ErrorCode.USER_PURGE_FAILED,
            detail=ErrorMessages.ACCOUNT_PURGE_FAILED,
        )
    elif isinstance(error, (ConcurrencyConflictError, ExecutorAlreadyUsedError)):
        translated = AppException(
            code=ErrorCode.JOB_CONFLICT,
            detail="The course job changed during this operation.",
        )
    elif isinstance(error, InvalidJobSubmissionError):
        translated = AppException(
            code=ErrorCode.INVALID_INPUT,
            detail="The course request is invalid.",
        )
    elif isinstance(
        error,
        (
            ApplicationCloseError,
            ArtifactIntegrityError,
            JobRequestCompatibilityError,
            PublicJobProjectionError,
        ),
    ):
        translated = AppException(
            code=ErrorCode.ENGINE_OPERATION_FAILED,
            detail="The course engine operation could not be completed.",
        )
    else:
        translated = AppException(
            code=ErrorCode.INTERNAL_ERROR,
            detail="An unexpected engine error occurred.",
        )

    # Translation happens before a route raises the shell exception. Clear any
    # manually attached chain now; the caller's ``raise ... from None`` then
    # keeps private package context out of rendered diagnostics.
    translated.__cause__ = None
    translated.__context__ = None
    return translated


__all__ = ["translate_txt2crs_exception"]
