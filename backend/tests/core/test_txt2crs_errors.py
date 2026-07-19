"""Tests-first mapping from public engine failures to safe shell errors."""

from txt2crs.application import (
    ApplicationClosedError,
    OwnerPurgeError,
    SystemAuthenticationError,
)
from txt2crs.jobs import (
    AdmissionQuotaExceededError,
    IdempotencyConflictError,
    JobNotFoundError,
)

from app.core.constants import ErrorCode
from app.core.txt2crs_errors import translate_txt2crs_exception


def test_known_package_errors_map_to_stable_shell_codes() -> None:
    """Routes receive semantic codes without inspecting private error text."""

    cases = (
        (
            ApplicationClosedError("private provider shutdown detail"),
            ErrorCode.SYSTEM_NOT_READY,
        ),
        (
            AdmissionQuotaExceededError("global_jobs", 1),
            ErrorCode.JOB_ADMISSION_REJECTED,
        ),
        (
            IdempotencyConflictError("private request hash"),
            ErrorCode.JOB_IDEMPOTENCY_CONFLICT,
        ),
        (
            JobNotFoundError("private owner lookup"),
            ErrorCode.JOB_NOT_FOUND,
        ),
        (
            OwnerPurgeError("private filesystem path"),
            ErrorCode.ENGINE_OPERATION_FAILED,
        ),
        (
            SystemAuthenticationError("Bearer private provider response"),
            ErrorCode.SYSTEM_AUTH_FAILED,
        ),
    )

    for package_error, expected_code in cases:
        translated = translate_txt2crs_exception(package_error)
        assert translated.code is expected_code
        assert "private" not in (translated.detail or "")
        assert translated.__cause__ is None
        assert translated.__context__ is None


def test_unknown_package_failure_maps_to_generic_internal_error() -> None:
    """Unexpected failures cannot expose provider bodies or local paths."""

    translated = translate_txt2crs_exception(
        RuntimeError("Bearer private-token at /home/ada/.codex/auth.json")
    )

    assert translated.code is ErrorCode.INTERNAL_ERROR
    assert translated.detail == "An unexpected engine error occurred."
    assert "private-token" not in str(translated)
