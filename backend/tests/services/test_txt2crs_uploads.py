"""Tests for bounded PDF and OOXML upload acquisition."""

import asyncio
import struct
import zipfile
from io import BytesIO
from typing import cast

import fitz  # type: ignore[import-untyped]
import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.core.constants import ErrorCode
from app.core.exceptions import AppException
from app.services.txt2crs_uploads import (
    UploadValidationLimits,
    validated_course_upload,
)

DOCX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
PPTX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.presentation"
)


class RecordingUploadFile(UploadFile):
    """Record bounded reads and closure without changing UploadFile behavior."""

    def __init__(
        self,
        content: bytes,
        *,
        filename: str,
        content_type: str,
    ) -> None:
        super().__init__(
            file=BytesIO(content),
            filename=filename,
            headers=Headers({"content-type": content_type}),
        )
        self.read_sizes: list[int] = []
        self.close_calls = 0

    async def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return await super().read(size)

    async def close(self) -> None:
        self.close_calls += 1
        await super().close()


class CancellingUploadFile(RecordingUploadFile):
    """Simulate client-task cancellation after one successful bounded read."""

    async def read(self, size: int = -1) -> bytes:
        if self.read_sizes:
            raise asyncio.CancelledError
        return await super().read(size)


def _limits(**changes: int) -> UploadValidationLimits:
    """Return small limits that make every boundary inexpensive to test."""

    values = {
        "maximum_file_bytes": 256_000,
        "maximum_pdf_pages": 3,
        "maximum_archive_entries": 20,
        "maximum_expanded_bytes": 20_000,
    }
    values.update(changes)
    return UploadValidationLimits(**values)


def _pdf(*page_texts: str, encrypted: bool = False) -> bytes:
    """Build a finite in-memory PDF fixture with real page metadata."""

    document = fitz.open()
    for page_text in page_texts:
        page = document.new_page()
        page.insert_text((72, 72), page_text)
    if encrypted:
        pdf_bytes = document.tobytes(
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw="owner",
            user_pw="learner",
        )
    else:
        pdf_bytes = document.tobytes()
    document.close()
    return cast(bytes, pdf_bytes)


def _office_archive(
    *,
    kind: str = "docx",
    extra_entries: dict[str, bytes] | None = None,
) -> bytes:
    """Build the minimum reviewed DOCX or PPTX ZIP structure."""

    if kind == "docx":
        main_part_name = "word/document.xml"
        main_content_type = DOCX_MEDIA_TYPE
    else:
        main_part_name = "ppt/presentation.xml"
        main_content_type = PPTX_MEDIA_TYPE
    content_types = (
        '<?xml version="1.0"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        f'<Override PartName="/{main_part_name}" '
        f'ContentType="{main_content_type}"/>'
        "</Types>"
    ).encode()
    archive_buffer = BytesIO()
    with zipfile.ZipFile(
        archive_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr(main_part_name, b"<document>course</document>")
        for entry_name, entry_content in (extra_entries or {}).items():
            archive.writestr(entry_name, entry_content)
    return archive_buffer.getvalue()


def _mark_first_zip_entry_encrypted(archive_bytes: bytes) -> bytes:
    """Set ZIP encryption flags in local and central headers for rejection."""

    mutated = bytearray(archive_bytes)
    local_header = mutated.find(b"PK\x03\x04")
    central_header = mutated.find(b"PK\x01\x02")
    assert local_header >= 0 and central_header >= 0
    local_flags = struct.unpack_from("<H", mutated, local_header + 6)[0]
    central_flags = struct.unpack_from("<H", mutated, central_header + 8)[0]
    struct.pack_into("<H", mutated, local_header + 6, local_flags | 0x1)
    struct.pack_into("<H", mutated, central_header + 8, central_flags | 0x1)
    return bytes(mutated)


async def _capture_payload(
    upload: UploadFile,
    *,
    limits: UploadValidationLimits,
) -> tuple[str, bytes, str, str | None, dict[str, object]]:
    """Enter the validator and detach the fields needed after cleanup."""

    async with validated_course_upload(upload, limits=limits) as payload:
        assert isinstance(payload.value, bytes)
        return (
            payload.input_type,
            payload.value,
            payload.media_type,
            payload.file_name,
            payload.metadata,
        )


@pytest.mark.parametrize(
    ("filename", "media_type", "content", "expected_input_type"),
    [
        ("course.pdf", "application/pdf", _pdf("Page one"), "pdf"),
        ("course.docx", DOCX_MEDIA_TYPE, _office_archive(), "document"),
        (
            "course.pptx",
            PPTX_MEDIA_TYPE,
            _office_archive(kind="pptx"),
            "slides",
        ),
    ],
)
def test_validated_upload_returns_exact_bounded_package_payload_and_closes(
    filename: str,
    media_type: str,
    content: bytes,
    expected_input_type: str,
) -> None:
    upload = RecordingUploadFile(
        content,
        filename=filename,
        content_type=media_type,
    )

    input_type, value, result_media_type, file_name, metadata = asyncio.run(
        _capture_payload(upload, limits=_limits())
    )

    assert input_type == expected_input_type
    assert value == content
    assert result_media_type == media_type
    assert file_name == filename
    assert metadata == {"size_bytes": len(content)}
    assert upload.read_sizes
    assert -1 not in upload.read_sizes
    assert all(0 < read_size <= 65_536 for read_size in upload.read_sizes)
    assert upload.close_calls == 1
    assert upload.file.closed


def test_upload_rejects_actual_bytes_over_limit_and_closes() -> None:
    upload = RecordingUploadFile(
        _pdf("Too large") + b"x" * 100,
        filename="course.pdf",
        content_type="application/pdf",
    )

    with pytest.raises(AppException) as captured_error:
        asyncio.run(_capture_payload(upload, limits=_limits(maximum_file_bytes=10)))

    assert captured_error.value.code is ErrorCode.JOB_PAYLOAD_TOO_LARGE
    assert upload.close_calls == 1
    assert upload.file.closed


@pytest.mark.parametrize(
    ("filename", "media_type", "content"),
    [
        ("../course.pdf", "application/pdf", _pdf("Unsafe")),
        (r"C:\private\course.pdf", "application/pdf", _pdf("Unsafe")),
        ("course\x00.pdf", "application/pdf", _pdf("Unsafe")),
        ("course.txt", "application/pdf", _pdf("Mismatch")),
        ("course.PDF", "text/plain", _pdf("Mismatch")),
        ("course.docm", DOCX_MEDIA_TYPE, _office_archive()),
        ("course.docx", PPTX_MEDIA_TYPE, _office_archive()),
    ],
)
def test_upload_rejects_unsafe_filename_extension_or_mime(
    filename: str,
    media_type: str,
    content: bytes,
) -> None:
    upload = RecordingUploadFile(
        content,
        filename=filename,
        content_type=media_type,
    )

    with pytest.raises(AppException) as captured_error:
        asyncio.run(_capture_payload(upload, limits=_limits()))

    assert captured_error.value.code is ErrorCode.JOB_UNSUPPORTED_MEDIA
    assert upload.file.closed


@pytest.mark.parametrize(
    ("filename", "media_type", "content"),
    [
        ("fake.pdf", "application/pdf", b"not-pdf"),
        ("fake.docx", DOCX_MEDIA_TYPE, b"not-zip"),
        ("fake.pptx", PPTX_MEDIA_TYPE, _office_archive()),
        ("fake.docx", DOCX_MEDIA_TYPE, _office_archive(kind="pptx")),
        ("corrupt.docx", DOCX_MEDIA_TYPE, b"PK\x03\x04corrupt"),
    ],
)
def test_upload_rejects_magic_or_ooxml_structure_mismatch(
    filename: str,
    media_type: str,
    content: bytes,
) -> None:
    upload = RecordingUploadFile(
        content,
        filename=filename,
        content_type=media_type,
    )

    with pytest.raises(AppException) as captured_error:
        asyncio.run(_capture_payload(upload, limits=_limits()))

    assert captured_error.value.code is ErrorCode.JOB_UNSUPPORTED_MEDIA
    assert upload.file.closed


@pytest.mark.parametrize(
    "content",
    [
        _office_archive(extra_entries={"../escape.xml": b"private"}),
        _office_archive(extra_entries={"/absolute.xml": b"private"}),
        _office_archive(extra_entries={r"word\..\escape.xml": b"private"}),
        _office_archive(extra_entries={"word/.": b"private"}),
        _office_archive(extra_entries={"word/..": b"private"}),
        _office_archive(extra_entries={"word/vbaProject.bin": b"macro"}),
        _office_archive(extra_entries={"word/activeX/control.xml": b"active"}),
        _mark_first_zip_entry_encrypted(_office_archive()),
    ],
)
def test_upload_rejects_traversal_active_content_and_encryption(
    content: bytes,
) -> None:
    upload = RecordingUploadFile(
        content,
        filename="course.docx",
        content_type=DOCX_MEDIA_TYPE,
    )

    with pytest.raises(AppException) as captured_error:
        asyncio.run(_capture_payload(upload, limits=_limits()))

    assert captured_error.value.code is ErrorCode.JOB_UNSUPPORTED_MEDIA
    assert upload.file.closed


def test_upload_rejects_excessive_archive_entries_and_expanded_bytes() -> None:
    many_entries = {f"word/item-{entry_index}.xml": b"x" for entry_index in range(5)}
    expanded_entry = {"word/large.xml": b"x" * 500}

    for content, limits in (
        (
            _office_archive(extra_entries=many_entries),
            _limits(maximum_archive_entries=4),
        ),
        (
            _office_archive(extra_entries=expanded_entry),
            _limits(maximum_expanded_bytes=200),
        ),
    ):
        upload = RecordingUploadFile(
            content,
            filename="course.docx",
            content_type=DOCX_MEDIA_TYPE,
        )
        with pytest.raises(AppException) as captured_error:
            asyncio.run(_capture_payload(upload, limits=limits))
        assert captured_error.value.code is ErrorCode.JOB_UNSUPPORTED_MEDIA
        assert upload.file.closed


def test_upload_rejects_corrupt_encrypted_and_excessive_page_pdf() -> None:
    for content, limits in (
        (b"%PDF-1.7\ncorrupt", _limits()),
        (_pdf("Secret", encrypted=True), _limits()),
        (_pdf("One", "Two", "Three", "Four"), _limits(maximum_pdf_pages=3)),
    ):
        upload = RecordingUploadFile(
            content,
            filename="course.pdf",
            content_type="application/pdf",
        )
        with pytest.raises(AppException) as captured_error:
            asyncio.run(_capture_payload(upload, limits=limits))
        assert captured_error.value.code is ErrorCode.JOB_UNSUPPORTED_MEDIA
        assert upload.file.closed


def test_upload_closes_framework_file_when_read_is_cancelled() -> None:
    upload = CancellingUploadFile(
        b"x" * 70_000,
        filename="course.pdf",
        content_type="application/pdf",
    )

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(_capture_payload(upload, limits=_limits()))

    assert upload.close_calls == 1
    assert upload.file.closed
