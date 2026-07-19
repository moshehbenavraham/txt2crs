"""Authenticated durable course-job submission endpoints."""

from typing import Annotated

from fastapi import APIRouter, File, Form, Header, Request, Response, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
from txt2crs.jobs import JobRecord

from app.api.deps import CurrentUser, Txt2CrsSubmissionDep
from app.core.config import settings
from app.core.constants import ErrorCode, HTTPStatusCode
from app.core.exceptions import AppException
from app.core.rate_limit import JOB_SUBMISSION_RATE_LIMIT, limiter
from app.schemas.jobs import (
    IdempotencyKey,
    JobAcceptedPublic,
    JobSubmissionRequest,
    JobUploadMetadata,
    parse_job_upload_metadata,
)
from app.services.txt2crs_uploads import (
    UploadValidationLimits,
    validated_course_upload,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

IdempotencyHeader = Annotated[
    IdempotencyKey,
    Header(
        alias="Idempotency-Key",
        description=(
            "Private owner-scoped retry key. Reuse only when retrying the same "
            "exact course request."
        ),
    ),
]
OOXML_MAXIMUM_ARCHIVE_ENTRIES = 10_000
OOXML_MAXIMUM_EXPANDED_BYTES = 52_428_800


@router.post(
    "",
    response_model=JobAcceptedPublic,
    status_code=HTTPStatusCode.ACCEPTED,
    summary="Submit a text or URL course job",
    description=(
        "Validates one prompt, pasted text, URL, or YouTube intent and returns "
        "only after package policy, admission, and durable commit succeed."
    ),
)
@limiter.limit(JOB_SUBMISSION_RATE_LIMIT)
def submit_job(
    request: Request,  # noqa: ARG001 - required by slowapi
    response: Response,
    current_user: CurrentUser,
    submission: Txt2CrsSubmissionDep,
    job_request: JobSubmissionRequest,
    idempotency_key: IdempotencyHeader,
) -> JobAcceptedPublic:
    """Authenticate, delegate one strict JSON request, and acknowledge commit."""

    submitted_job = submission.submit_json(
        user_id=str(current_user.id),
        idempotency_key=idempotency_key,
        request=job_request,
    )
    return _accepted_response(submitted_job, response=response)


@router.post(
    "/upload",
    response_model=JobAcceptedPublic,
    status_code=HTTPStatusCode.ACCEPTED,
    summary="Submit a document course job",
    description=(
        "Accepts exactly one strict metadata object and one bounded PDF, DOCX, "
        "or PPTX file, then returns only after durable package commit."
    ),
)
@limiter.limit(JOB_SUBMISSION_RATE_LIMIT)
async def submit_job_upload(
    request: Request,  # required by slowapi and exact multipart inspection
    response: Response,
    current_user: CurrentUser,
    submission: Txt2CrsSubmissionDep,
    idempotency_key: IdempotencyHeader,
    metadata: Annotated[
        str,
        Form(
            min_length=2,
            max_length=262_144,
            description="Strict JSON course preferences, consent, and age group.",
        ),
    ],
    file: Annotated[
        UploadFile,
        File(description="One bounded PDF, DOCX, or PPTX source."),
    ],
) -> JobAcceptedPublic:
    """Validate exact multipart cardinality, own cleanup, and submit bytes."""

    parsed_form = await request.form()
    form_items = list(parsed_form.multi_items())
    metadata_values = [value for key, value in form_items if key == "metadata"]
    file_values = [value for key, value in form_items if key == "file"]
    form_uploads = [
        value for _key, value in form_items if isinstance(value, StarletteUploadFile)
    ]
    has_exact_shape = (
        len(form_items) == 2
        and len(metadata_values) == 1
        and isinstance(metadata_values[0], str)
        and metadata_values[0] == metadata
        and len(file_values) == 1
        and isinstance(file_values[0], StarletteUploadFile)
        and file_values[0] is file
    )
    if not has_exact_shape:
        await _close_uploads_without_masking(form_uploads)
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            detail="Multipart submission must contain one metadata field and file.",
        )

    parsed_metadata: JobUploadMetadata | None = None
    try:
        parsed_metadata = parse_job_upload_metadata(
            metadata,
            maximum_metadata_bytes=settings.TXT2CRS_MAX_METADATA_BYTES,
        )
    except ValueError:
        # Leave the parser's scope before raising so learner JSON is not
        # retained as exception context.
        pass
    if parsed_metadata is None:
        await _close_uploads_without_masking([file])
        raise AppException(
            code=ErrorCode.VALIDATION_ERROR,
            detail="Upload metadata is invalid.",
        )

    async with validated_course_upload(
        file,
        limits=UploadValidationLimits(
            maximum_file_bytes=settings.TXT2CRS_MAX_INPUT_BYTES,
            maximum_pdf_pages=settings.TXT2CRS_MAX_PDF_PAGES,
            maximum_archive_entries=OOXML_MAXIMUM_ARCHIVE_ENTRIES,
            maximum_expanded_bytes=OOXML_MAXIMUM_EXPANDED_BYTES,
        ),
    ) as validated_upload:
        submitted_job = submission.submit_upload(
            user_id=str(current_user.id),
            idempotency_key=idempotency_key,
            metadata=parsed_metadata,
            upload=validated_upload,
        )
    return _accepted_response(submitted_job, response=response)


async def _close_uploads_without_masking(
    uploads: list[StarletteUploadFile],
) -> None:
    """Best-effort close every parsed upload while preserving validation errors."""

    for upload in uploads:
        try:
            await upload.close()
        except BaseException:
            # The route is already rejecting malformed multipart shape. A
            # secondary close failure must not replace that safe public result.
            continue


def _accepted_response(
    submitted_job: JobRecord,
    *,
    response: Response,
) -> JobAcceptedPublic:
    """Set shared privacy headers and build one allowlisted durable projection."""

    job_id = submitted_job.job_id
    status_url = f"/api/v1/jobs/{job_id}"
    response.headers["Location"] = status_url
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return JobAcceptedPublic(
        schema_version="1.0",
        job_id=job_id,
        status="accepted",
        # POST acknowledges the original durable admission. Exact idempotent
        # replays keep this response stable even if the job has since advanced;
        # the owner-scoped GET route introduced next exposes current status.
        revision=0,
        status_url=status_url,
    )


__all__ = ["router"]
