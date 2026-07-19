"""Bounded acquisition and transport validation for course source uploads.

This shell service validates only HTTP/file-container facts. It does not
extract learner text or decide whether source content is suitable; those
behaviors remain inside the reusable ``txt2crs`` package.
"""

import zipfile
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
from typing import Literal, NoReturn

import fitz  # type: ignore[import-untyped]
from fastapi import UploadFile

from app.core.constants import ErrorCode
from app.core.exceptions import AppException

UPLOAD_READ_CHUNK_BYTES = 65_536
MAXIMUM_SAFE_FILENAME_CHARACTERS = 255
MAXIMUM_ARCHIVE_ENTRY_NAME_CHARACTERS = 1_000

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
PPTX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
)
_DOCX_MAIN_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
)
_PPTX_MAIN_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
)
CourseUploadInputType = Literal["pdf", "document", "slides"]

_UPLOAD_TYPES: dict[str, tuple[str, CourseUploadInputType]] = {
    ".pdf": ("application/pdf", "pdf"),
    ".docx": (DOCX_MEDIA_TYPE, "document"),
    ".pptx": (PPTX_MEDIA_TYPE, "slides"),
}


@dataclass(frozen=True, slots=True)
class UploadValidationLimits:
    """Finite resource ceilings applied before package persistence."""

    maximum_file_bytes: int
    maximum_pdf_pages: int
    maximum_archive_entries: int
    maximum_expanded_bytes: int

    def __post_init__(self) -> None:
        """Reject ineffective or accidentally unbounded limits."""

        if self.maximum_file_bytes <= 0:
            raise ValueError("Maximum upload bytes must be positive.")
        if self.maximum_pdf_pages <= 0:
            raise ValueError("Maximum PDF pages must be positive.")
        if self.maximum_archive_entries <= 0:
            raise ValueError("Maximum archive entries must be positive.")
        if self.maximum_expanded_bytes <= 0:
            raise ValueError("Maximum expanded bytes must be positive.")


@dataclass(frozen=True, slots=True)
class ValidatedCourseUpload:
    """Detached exact upload bytes after transport validation succeeds."""

    input_type: CourseUploadInputType
    content: bytes
    media_type: str
    file_name: str
    size_bytes: int

    @property
    def value(self) -> bytes:
        """Match the public package input's exact byte-value terminology."""

        return self.content

    @property
    def metadata(self) -> dict[str, object]:
        """Return a fresh allowlisted metadata mapping for request hashing."""

        return {"size_bytes": self.size_bytes}


@asynccontextmanager
async def validated_course_upload(
    upload: UploadFile,
    *,
    limits: UploadValidationLimits,
) -> AsyncIterator[ValidatedCourseUpload]:
    """Yield one detached validated upload and always close framework state."""

    primary_error: BaseException | None = None
    try:
        filename, media_type, input_type = _validate_filename_and_media(upload)
        content = await _read_bounded_upload(upload, limits=limits)
        if input_type == "pdf":
            _validate_pdf(content, maximum_pages=limits.maximum_pdf_pages)
        else:
            _validate_ooxml(
                content,
                input_type=input_type,
                maximum_entries=limits.maximum_archive_entries,
                maximum_expanded_bytes=limits.maximum_expanded_bytes,
            )
        yield ValidatedCourseUpload(
            input_type=input_type,
            content=content,
            media_type=media_type,
            file_name=filename,
            size_bytes=len(content),
        )
    except BaseException as error:
        primary_error = error
        raise
    finally:
        try:
            await upload.close()
        except BaseException:
            # A close failure matters when it is the only failure. If request
            # validation or cancellation already failed, preserve that primary
            # result after still attempting cleanup exactly once.
            if primary_error is None:
                raise


def _validate_filename_and_media(
    upload: UploadFile,
) -> tuple[str, str, CourseUploadInputType]:
    """Require one safe basename whose extension and MIME agree exactly."""

    filename = upload.filename
    media_type = upload.content_type
    if (
        not isinstance(filename, str)
        or not filename
        or len(filename) > MAXIMUM_SAFE_FILENAME_CHARACTERS
        or filename != filename.strip()
        or filename in {".", ".."}
        or "/" in filename
        or "\\" in filename
        or any(ord(character) < 32 or ord(character) == 127 for character in filename)
        or not isinstance(media_type, str)
    ):
        _raise_unsupported_media()

    extension = PurePosixPath(filename).suffix.casefold()
    reviewed_type = _UPLOAD_TYPES.get(extension)
    if reviewed_type is None or media_type != reviewed_type[0]:
        _raise_unsupported_media()
    return filename, media_type, reviewed_type[1]


async def _read_bounded_upload(
    upload: UploadFile,
    *,
    limits: UploadValidationLimits,
) -> bytes:
    """Read only finite chunks and stop after the first byte over the cap."""

    if upload.size is not None and upload.size > limits.maximum_file_bytes:
        _raise_payload_too_large()

    chunks: list[bytes] = []
    total_bytes = 0
    while True:
        chunk = await upload.read(UPLOAD_READ_CHUNK_BYTES)
        if not chunk:
            break
        total_bytes += len(chunk)
        if total_bytes > limits.maximum_file_bytes:
            _raise_payload_too_large()
        chunks.append(chunk)
    return b"".join(chunks)


def _validate_pdf(content: bytes, *, maximum_pages: int) -> None:
    """Check PDF magic, readability, encryption, and the finite page count."""

    if not content.startswith(b"%PDF-"):
        _raise_unsupported_media()

    pdf_document: fitz.Document | None = None
    parsing_failed = False
    try:
        pdf_document = fitz.open(stream=content, filetype="pdf")
    except Exception:
        parsing_failed = True
    if parsing_failed or pdf_document is None:
        _raise_unsupported_media()

    try:
        if pdf_document.needs_pass or pdf_document.page_count > maximum_pages:
            _raise_unsupported_media()
    finally:
        pdf_document.close()


def _validate_ooxml(
    content: bytes,
    *,
    input_type: CourseUploadInputType,
    maximum_entries: int,
    maximum_expanded_bytes: int,
) -> None:
    """Inspect finite ZIP metadata and required OOXML structure without extract."""

    if not content.startswith(b"PK\x03\x04"):
        _raise_unsupported_media()

    archive_failed = False
    try:
        with zipfile.ZipFile(BytesIO(content), mode="r") as archive:
            _inspect_ooxml_archive(
                archive,
                input_type=input_type,
                maximum_entries=maximum_entries,
                maximum_expanded_bytes=maximum_expanded_bytes,
            )
    except AppException:
        raise
    except Exception:
        # CRC, central-directory, decompression, and unsupported ZIP feature
        # errors all become the same content-free media rejection.
        archive_failed = True
    if archive_failed:
        _raise_unsupported_media()


def _inspect_ooxml_archive(
    archive: zipfile.ZipFile,
    *,
    input_type: CourseUploadInputType,
    maximum_entries: int,
    maximum_expanded_bytes: int,
) -> None:
    """Validate central-directory metadata before reading one bounded marker."""

    entries = archive.infolist()
    if not entries or len(entries) > maximum_entries:
        _raise_unsupported_media()

    seen_names: set[str] = set()
    total_expanded_bytes = 0
    for entry in entries:
        entry_name = entry.filename
        normalized_name = entry_name.casefold()
        path_parts = entry_name.split("/")
        if (
            not entry_name
            or len(entry_name) > MAXIMUM_ARCHIVE_ENTRY_NAME_CHARACTERS
            or entry_name in seen_names
            or "\\" in entry_name
            or entry_name.startswith("/")
            or any(part in {"", ".", ".."} for part in path_parts[:-1])
            or path_parts[-1] in {".", ".."}
            or entry.flag_bits & 0x1
            or _is_active_ooxml_entry(normalized_name)
        ):
            _raise_unsupported_media()
        seen_names.add(entry_name)
        total_expanded_bytes += entry.file_size
        if total_expanded_bytes > maximum_expanded_bytes:
            _raise_unsupported_media()

    required_main_part, accepted_main_content_types = {
        "document": (
            "word/document.xml",
            frozenset({DOCX_MEDIA_TYPE, _DOCX_MAIN_CONTENT_TYPE}),
        ),
        "slides": (
            "ppt/presentation.xml",
            frozenset({PPTX_MEDIA_TYPE, _PPTX_MAIN_CONTENT_TYPE}),
        ),
    }[input_type]
    if "[Content_Types].xml" not in seen_names or required_main_part not in seen_names:
        _raise_unsupported_media()

    content_types = archive.read("[Content_Types].xml")
    if not any(
        content_type.encode("ascii") in content_types
        for content_type in accepted_main_content_types
    ):
        _raise_unsupported_media()


def _is_active_ooxml_entry(normalized_name: str) -> bool:
    """Return whether an OOXML member can contain active or embedded content."""

    return (
        normalized_name.endswith("/vbaproject.bin")
        or "/activex/" in f"/{normalized_name}"
        or "/embeddings/" in f"/{normalized_name}"
        or normalized_name.startswith("customui/")
        or "/externallinks/" in f"/{normalized_name}"
    )


def _raise_payload_too_large() -> NoReturn:
    """Raise one safe stable overflow error."""

    raise AppException(
        code=ErrorCode.JOB_PAYLOAD_TOO_LARGE,
        detail="The uploaded file exceeds the configured limit.",
    )


def _raise_unsupported_media() -> NoReturn:
    """Raise one safe error for all unreviewed or invalid file containers."""

    raise AppException(
        code=ErrorCode.JOB_UNSUPPORTED_MEDIA,
        detail="The uploaded file type or structure is unsupported.",
    )


__all__ = [
    "DOCX_MEDIA_TYPE",
    "PPTX_MEDIA_TYPE",
    "UploadValidationLimits",
    "ValidatedCourseUpload",
    "validated_course_upload",
]
