"""Authenticated durable course-job submission endpoints."""

from typing import Annotated, Any
from urllib.parse import quote

from fastapi import (
    APIRouter,
    File,
    Form,
    Header,
    Path,
    Query,
    Request,
    Response,
    UploadFile,
)
from starlette.datastructures import UploadFile as StarletteUploadFile
from txt2crs.jobs import JobRecord

from app.api.artifact_response import (
    ArtifactStreamingResponse,
    EnteredArtifactBody,
)
from app.api.deps import (
    CurrentUser,
    Txt2CrsApplicationDep,
    Txt2CrsSubmissionDep,
)
from app.core.config import settings
from app.core.constants import ContentTypes, ErrorCode, HTTPStatusCode, Pagination
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.core.rate_limit import JOB_SUBMISSION_RATE_LIMIT, limiter
from app.core.txt2crs_errors import translate_txt2crs_exception
from app.schemas.jobs import (
    ArtifactManifestPublic,
    IdempotencyKey,
    JobAcceptedPublic,
    JobIdentifier,
    JobLibraryPublic,
    JobStatusPublic,
    JobSubmissionRequest,
    JobUploadMetadata,
    parse_job_upload_metadata,
)
from app.services.txt2crs_uploads import (
    UploadValidationLimits,
    validated_course_upload,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = get_logger(__name__)

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
MARKDOWN_MEDIA_TYPE = "text/markdown"
PDF_MEDIA_TYPE = "application/pdf"
DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
JobPathIdentifier = Annotated[
    JobIdentifier,
    Path(
        description="Opaque owner-scoped durable course job identifier.",
    ),
]
ArtifactPathIdentifier = Annotated[
    JobIdentifier,
    Path(
        description="Stable canonical artifact identifier.",
    ),
]
JobListLimit = Annotated[
    int,
    Query(
        ge=1,
        le=50,
        description="Maximum owner-scoped course jobs returned in this page.",
    ),
]
JobListCursor = Annotated[
    str | None,
    Query(
        min_length=1,
        max_length=512,
        description="Opaque newest-first continuation returned by this endpoint.",
    ),
]
_PRIVATE_RESPONSE_HEADERS = {
    "Cache-Control": "private, no-store",
    "Pragma": "no-cache",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}
_PRIVATE_READ_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    HTTPStatusCode.UNAUTHORIZED: {
        "description": "Authentication is required.",
        "content": {ContentTypes.PROBLEM_JSON: {}},
    },
    HTTPStatusCode.NOT_FOUND: {
        "description": "The owner-scoped course job was not found.",
        "content": {ContentTypes.PROBLEM_JSON: {}},
    },
    HTTPStatusCode.UNPROCESSABLE_ENTITY: {
        "description": "A path identifier is invalid.",
        "content": {ContentTypes.PROBLEM_JSON: {}},
    },
    HTTPStatusCode.INTERNAL_SERVER_ERROR: {
        "description": "The course result could not be read safely.",
        "content": {ContentTypes.PROBLEM_JSON: {}},
    },
}
_PRIVATE_LIST_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    status: response
    for status, response in _PRIVATE_READ_ERROR_RESPONSES.items()
    if status != HTTPStatusCode.NOT_FOUND
}
_ARTIFACT_DOWNLOAD_RESPONSES: dict[int | str, dict[str, Any]] = {
    **_PRIVATE_READ_ERROR_RESPONSES,
    HTTPStatusCode.OK: {
        "description": "Verified private artifact bytes.",
        "content": {
            # OpenAPI models text responses as strings and file formats through
            # JSON Schema's contentMediaType keyword. The wildcard fallback
            # preserves an honest string-or-file union in generators that pick
            # only one content entry for a status code. The four exact entries
            # document every media type emitted by the deterministic renderer.
            "*/*": {
                "schema": {
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "string",
                            "contentMediaType": "application/octet-stream",
                        },
                    ]
                }
            },
            ContentTypes.TEXT_HTML: {"schema": {"type": "string"}},
            MARKDOWN_MEDIA_TYPE: {"schema": {"type": "string"}},
            PDF_MEDIA_TYPE: {
                "schema": {
                    "type": "string",
                    "contentMediaType": PDF_MEDIA_TYPE,
                }
            },
            DOCX_MEDIA_TYPE: {
                "schema": {
                    "type": "string",
                    "contentMediaType": DOCX_MEDIA_TYPE,
                }
            },
        },
    },
}


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


@router.get(
    "",
    response_model=JobLibraryPublic,
    status_code=HTTPStatusCode.OK,
    summary="List retained course jobs",
    description=(
        "Returns one stable newest-first owner page. The opaque continuation "
        "can be replayed to recover older retained jobs without exposing "
        "engine persistence details."
    ),
    responses=_PRIVATE_LIST_ERROR_RESPONSES,
)
def list_jobs(
    response: Response,
    current_user: CurrentUser,
    application: Txt2CrsApplicationDep,
    limit: JobListLimit = Pagination.DEFAULT_LIMIT,
    cursor: JobListCursor = None,
) -> JobLibraryPublic:
    """Delegate the owner collection to the package facade and map its page."""

    try:
        package_page = application.list_public_jobs(
            user_id=str(current_user.id),
            page_size=limit,
            cursor=cursor,
        )
        public_page = JobLibraryPublic.from_package(package_page)
    except Exception as package_error:
        raise translate_txt2crs_exception(package_error) from None

    _set_private_response_headers(response)
    return public_page


@router.get(
    "/{job_id}",
    response_model=JobStatusPublic,
    status_code=HTTPStatusCode.OK,
    summary="Read current course job status and result",
    description=(
        "Returns one revisioned owner-scoped allowlist. Responses are private "
        "and non-cacheable; P0 does not implement conditional cache validators."
    ),
    responses=_PRIVATE_READ_ERROR_RESPONSES,
)
def read_job(
    job_id: JobPathIdentifier,
    response: Response,
    current_user: CurrentUser,
    application: Txt2CrsApplicationDep,
) -> JobStatusPublic:
    """Read through the package facade and map only its public snapshot."""

    try:
        public_snapshot = application.get_public_job(
            job_id=job_id,
            user_id=str(current_user.id),
        )
        public_response = JobStatusPublic.from_package(public_snapshot)
    except Exception as package_error:
        raise translate_txt2crs_exception(package_error) from None

    _set_private_response_headers(response)
    return public_response


@router.get(
    "/{job_id}/artifacts",
    response_model=ArtifactManifestPublic,
    status_code=HTTPStatusCode.OK,
    summary="Read the verified course artifact manifest",
    description=(
        "Returns owner-scoped path-free metadata grouped by educational "
        "deliverable after package integrity verification."
    ),
    responses=_PRIVATE_READ_ERROR_RESPONSES,
)
def read_job_artifacts(
    job_id: JobPathIdentifier,
    response: Response,
    current_user: CurrentUser,
    application: Txt2CrsApplicationDep,
) -> ArtifactManifestPublic:
    """Authorize and verify the manifest inside the package boundary."""

    try:
        package_manifest = application.get_artifact_manifest(
            job_id=job_id,
            user_id=str(current_user.id),
        )
        public_manifest = ArtifactManifestPublic.from_package(package_manifest)
    except Exception as package_error:
        raise translate_txt2crs_exception(package_error) from None

    _set_private_response_headers(response)
    return public_manifest


@router.get(
    "/{job_id}/artifacts/{artifact_id}",
    response_class=Response,
    status_code=HTTPStatusCode.OK,
    summary="Download one verified course artifact",
    description=(
        "Reauthorizes and verifies one canonical artifact before headers, then "
        "streams its existing private descriptor without buffering."
    ),
    responses=_ARTIFACT_DOWNLOAD_RESPONSES,
)
def download_job_artifact(
    job_id: JobPathIdentifier,
    artifact_id: ArtifactPathIdentifier,
    current_user: CurrentUser,
    application: Txt2CrsApplicationDep,
) -> ArtifactStreamingResponse:
    """Enter one verified package stream and transfer cleanup to its response."""

    user_id = str(current_user.id)
    try:
        package_manifest = application.get_artifact_manifest(
            job_id=job_id,
            user_id=user_id,
        )
    except Exception as package_error:
        raise translate_txt2crs_exception(package_error) from None

    selected_artifact = next(
        (
            artifact
            for artifact in package_manifest.artifacts
            if artifact.artifact_id == artifact_id
        ),
        None,
    )
    if selected_artifact is None:
        # Missing IDs use the same job-level code and copy as missing/foreign
        # jobs. The response cannot become an artifact-existence oracle.
        raise AppException(
            code=ErrorCode.JOB_NOT_FOUND,
            detail="The requested course job was not found.",
        )

    try:
        package_context = application.open_artifact(
            job_id=job_id,
            user_id=user_id,
            artifact_id=artifact_id,
        )
        entered_body = EnteredArtifactBody.enter(package_context)
    except Exception as package_error:
        raise translate_txt2crs_exception(package_error) from None

    response_headers = {
        **_PRIVATE_RESPONSE_HEADERS,
        "Content-Type": selected_artifact.media_type,
        "Content-Length": str(selected_artifact.size_bytes),
        "Content-Disposition": _attachment_disposition(
            selected_artifact.safe_file_name
        ),
    }
    try:
        return ArtifactStreamingResponse(
            entered_body,
            headers=response_headers,
        )
    except BaseException:
        # A monkeypatch, future response option, or allocation failure can
        # occur after context entry but before ASGI takes ownership.
        _close_after_response_construction_failure(entered_body)
        raise


def _attachment_disposition(file_name: str) -> str:
    """Encode every file name as an ASCII RFC 5987 attachment parameter."""

    encoded_file_name = quote(file_name, safe="")
    return f"attachment; filename*=utf-8''{encoded_file_name}"


def _close_after_response_construction_failure(body: EnteredArtifactBody) -> None:
    """Preserve the construction error while settling entered stream ownership."""

    try:
        body.close()
    except BaseException:
        # The active construction error remains authoritative. Log no
        # filename, artifact identifier, hash, exception, or private path.
        try:
            logger.error("artifact.response_cleanup_failed")
        except BaseException:
            return


def _set_private_response_headers(response: Response) -> None:
    """Apply the fixed privacy policy shared by result and manifest JSON."""

    for header_name, header_value in _PRIVATE_RESPONSE_HEADERS.items():
        response.headers[header_name] = header_value


__all__ = ["router"]
