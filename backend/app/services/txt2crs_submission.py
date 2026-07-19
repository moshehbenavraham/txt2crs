"""Thin shell composition for authenticated durable job submission."""

from typing import Literal, Protocol

from txt2crs.application import Txt2CrsApplication
from txt2crs.jobs import (
    ExecutionProfile,
    GenerationRequest,
    InputPayload,
    JobRecord,
    JobStatus,
    LearnerAgeGroup,
    LearningPreferenceIntent,
)

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.core.txt2crs_errors import translate_txt2crs_exception
from app.schemas.jobs import (
    JobPreferences,
    JobSubmissionRequest,
    JobUploadMetadata,
)
from app.services.txt2crs_readiness import ReadinessSnapshot
from app.services.txt2crs_uploads import ValidatedCourseUpload

logger = get_logger(__name__)

_TERMINAL_JOB_STATUSES = frozenset(
    {
        JobStatus.completed,
        JobStatus.failed,
        JobStatus.cancelled,
    }
)


class SubmissionReadiness(Protocol):
    """Return cached admission state without triggering live probes."""

    def snapshot(self) -> ReadinessSnapshot:
        """Return the current immutable shell projection."""


class SubmissionWorker(Protocol):
    """Wake a serial worker after, never before, a durable commit."""

    def notify_runnable(self) -> None:
        """Publish a latency-only wake hint."""


class Txt2CrsSubmissionService:
    """Map reviewed HTTP values into one public package facade call."""

    def __init__(
        self,
        *,
        application: Txt2CrsApplication,
        readiness: SubmissionReadiness,
        worker: SubmissionWorker,
        execution_profile: ExecutionProfile,
    ) -> None:
        self._application = application
        self._readiness = readiness
        self._worker = worker
        # The engine contract is frozen. Keeping the exact object ensures all
        # accepted requests use the same startup-reviewed generation defaults.
        self._execution_profile = execution_profile

    def submit_json(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        request: JobSubmissionRequest,
    ) -> JobRecord:
        """Build one text/URL package payload and submit it durably."""

        package_input_type: Literal["prompt", "text", "url"]
        if request.input.type in {"prompt", "text"}:
            package_input_type = request.input.type
            media_type = "text/plain"
        else:
            # YouTube intent is recorded but host recognition and redirect/DNS
            # policy stay inside the package's routing URL adapter.
            package_input_type = "url"
            media_type = "text/uri-list"
        input_payload = InputPayload(
            input_type=package_input_type,
            value=request.input.value,
            media_type=media_type,
            file_name=None,
            metadata={"input_mode": request.input.type},
        )
        return self._submit(
            user_id=user_id,
            idempotency_key=idempotency_key,
            input_payload=input_payload,
            preferences=request.preferences,
            consent_to_ai_processing=request.consent_to_ai_processing,
            learner_age_group=request.learner_age_group.value,
            input_mode=request.input.type,
        )

    def submit_upload(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        metadata: JobUploadMetadata,
        upload: ValidatedCourseUpload,
    ) -> JobRecord:
        """Build one exact byte package payload and submit it durably."""

        input_payload = InputPayload(
            input_type=upload.input_type,
            value=upload.content,
            media_type=upload.media_type,
            file_name=upload.file_name,
            metadata=upload.metadata,
        )
        return self._submit(
            user_id=user_id,
            idempotency_key=idempotency_key,
            input_payload=input_payload,
            preferences=metadata.preferences,
            consent_to_ai_processing=metadata.consent_to_ai_processing,
            learner_age_group=metadata.learner_age_group.value,
            input_mode=upload.input_type,
        )

    def _submit(
        self,
        *,
        user_id: str,
        idempotency_key: str,
        input_payload: InputPayload,
        preferences: JobPreferences,
        consent_to_ai_processing: bool,
        learner_age_group: str,
        input_mode: str,
    ) -> JobRecord:
        """Check cache, construct the canonical request, commit, then wake."""

        logger.info(
            "job.submission_started",
            extra={"user_id": user_id, "input_type": input_mode},
        )
        if not self._readiness.snapshot().accepting_jobs:
            logger.info(
                "job.submission_rejected",
                extra={
                    "user_id": user_id,
                    "input_type": input_mode,
                    "error_code": ErrorCode.SYSTEM_NOT_READY.value,
                },
            )
            raise AppException(
                code=ErrorCode.SYSTEM_NOT_READY,
                detail="The course system is not ready.",
            )

        request_build_failed = False
        try:
            generation_request = GenerationRequest.create(
                schema_version="1.0",
                request_version="generation-request-v1",
                input_payload=input_payload,
                preferences=_package_preferences(preferences),
                provider_consent=consent_to_ai_processing,
                learner_age_group=LearnerAgeGroup(learner_age_group),
                policy_flags=(),
                execution_profile=self._execution_profile,
            )
        except TypeError, ValueError:
            request_build_failed = True
        if request_build_failed:
            logger.info(
                "job.submission_rejected",
                extra={
                    "user_id": user_id,
                    "input_type": input_mode,
                    "error_code": ErrorCode.INVALID_INPUT.value,
                },
            )
            raise AppException(
                code=ErrorCode.INVALID_INPUT,
                detail="The course request is invalid.",
            )

        translated_error: AppException | None = None
        try:
            submitted_job = self._application.submit(
                user_id=user_id,
                idempotency_key=idempotency_key,
                generation_request=generation_request,
                admission_reservation=(
                    self._application.default_admission_reservation()
                ),
            )
        except Exception as error:
            translated_error = translate_txt2crs_exception(error)
        if translated_error is not None:
            logger.info(
                "job.submission_rejected",
                extra={
                    "user_id": user_id,
                    "input_type": input_mode,
                    "error_code": translated_error.code.value,
                },
            )
            raise translated_error from None

        if submitted_job.status not in _TERMINAL_JOB_STATUSES:
            try:
                self._worker.notify_runnable()
            except Exception:
                # The durable queue remains authoritative. A failed in-process
                # hint may add polling latency but cannot turn a committed job
                # into a client-visible failure that encourages duplicates.
                logger.error(
                    "job.worker_notification_failed",
                    extra={"user_id": user_id, "job_id": submitted_job.job_id},
                )

        logger.info(
            "job.submission_completed",
            extra={
                "user_id": user_id,
                "job_id": submitted_job.job_id,
                "input_type": input_mode,
                "revision": submitted_job.revision,
            },
        )
        return submitted_job


def _package_preferences(
    preferences: JobPreferences,
) -> LearningPreferenceIntent:
    """Copy every learner-selected value into the immutable package contract."""

    return LearningPreferenceIntent(
        audience=preferences.audience,
        prior_knowledge=preferences.prior_knowledge,
        learning_goals=preferences.learning_goals,
        level=preferences.level.value,
        language=preferences.language,
    )


__all__ = [
    "SubmissionReadiness",
    "SubmissionWorker",
    "Txt2CrsSubmissionService",
]
