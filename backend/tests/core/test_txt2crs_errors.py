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
    PreparationPolicyError,
)
from txt2crs.security.policy import PolicyDecision, PolicyOutcome, PolicyStage

from app.core.constants import ERROR_STATUS_MAP, ErrorCode, HTTPStatusCode
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
        (
            PreparationPolicyError(
                decision=PolicyDecision(
                    policy_version="content-policy-v1",
                    stage=PolicyStage.preflight,
                    outcome=PolicyOutcome.rejected,
                    reason_code="provider_consent_required",
                    high_risk=False,
                    public_message="Private policy response.",
                )
            ),
            ErrorCode.JOB_POLICY_REJECTED,
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


def test_new_job_error_codes_preserve_released_range_and_statuses() -> None:
    """Phase 03 extends the released 7xxx job range without renumbering it."""

    assert ErrorCode.JOB_PAYLOAD_TOO_LARGE.value == "JOB_7005"
    assert ErrorCode.JOB_UNSUPPORTED_MEDIA.value == "JOB_7006"
    assert ErrorCode.JOB_POLICY_REJECTED.value == "JOB_7007"
    assert ERROR_STATUS_MAP[ErrorCode.JOB_PAYLOAD_TOO_LARGE] == (
        HTTPStatusCode.PAYLOAD_TOO_LARGE
    )
    assert ERROR_STATUS_MAP[ErrorCode.JOB_UNSUPPORTED_MEDIA] == (
        HTTPStatusCode.UNSUPPORTED_MEDIA_TYPE
    )
    assert ERROR_STATUS_MAP[ErrorCode.JOB_POLICY_REJECTED] == (
        HTTPStatusCode.UNPROCESSABLE_ENTITY
    )
