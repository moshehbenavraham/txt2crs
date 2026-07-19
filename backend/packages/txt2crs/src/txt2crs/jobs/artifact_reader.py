# SPDX-License-Identifier: MIT-0

"""Confined manifest verification and one-descriptor artifact streaming."""

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from stat import S_ISREG
from typing import Any, BinaryIO

from txt2crs.jobs.artifact_queries import (
    _ARTIFACT_NAME_PATTERN,
    _MANIFEST_FILE_NAME,
    _MAXIMUM_MANIFEST_BYTES,
    _SHA256_HEX_PATTERN,
    ARTIFACT_STREAM_CHUNK_BYTES,
    ArtifactIntegrityError,
    ArtifactManifest,
    ArtifactMetadata,
    _canonical_artifact_kind,
    _has_control_characters,
)
from txt2crs.jobs.store import JobNotFoundError
from txt2crs.rendering.artifacts import RenderedArtifact


@dataclass(frozen=True, slots=True)
class _StoredArtifactDescriptor:
    """Validated path-relative metadata retained from the private manifest."""

    artifact_id: str
    file_name: str
    media_type: str
    size_bytes: int
    sha256_hex: str


@dataclass(frozen=True, slots=True)
class _StoredArtifactManifest:
    """Validated private manifest data without any loaded artifact bodies."""

    raw_manifest: dict[str, Any]
    created_at: datetime
    descriptors: tuple[_StoredArtifactDescriptor, ...]


class FilesystemArtifactReader:
    """Read one immutable artifact tree without exposing a private path."""

    def __init__(
        self,
        *,
        root_directory: Path,
        maximum_job_bytes: int,
    ) -> None:
        self._root_directory = root_directory
        self._maximum_job_bytes = maximum_job_bytes

    def job_directory(self, *, user_id: str, job_id: str) -> Path:
        """Return a confined path made only from opaque identifier hashes."""

        owner_directory = self.owner_directory(user_id=user_id)
        job_hash = sha256(job_id.encode("utf-8")).hexdigest()
        return owner_directory / "jobs" / job_hash

    def owner_directory(self, *, user_id: str) -> Path:
        """Return the non-identifying confined directory for one owner."""

        owner_hash = sha256(user_id.encode("utf-8")).hexdigest()
        return self._root_directory / "owners" / owner_hash

    def require_confined_directory(self, directory: Path) -> None:
        """Reject a symlink, non-directory, or path outside the private root."""

        self._require_confined_regular_directory(directory)

    def require_job_directory(self, *, user_id: str, job_id: str) -> Path:
        """Return an existing owner-scoped directory or one safe not-found."""

        job_directory = self.job_directory(user_id=user_id, job_id=job_id)
        if job_directory.is_symlink():
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        if not job_directory.exists():
            raise JobNotFoundError("The requested artifact was not found.")
        self._require_confined_regular_directory(job_directory)
        return job_directory

    def get_manifest(
        self,
        *,
        user_id: str,
        job_id: str,
    ) -> ArtifactManifest:
        """Return verified public metadata without opening artifact bodies."""

        job_directory = self.require_job_directory(
            user_id=user_id,
            job_id=job_id,
        )
        public_manifest: ArtifactManifest | None = None
        try:
            stored_manifest = self.load_verified_manifest(job_directory)
            public_manifest = ArtifactManifest(
                schema_version="1.0",
                job_id=job_id,
                created_at=stored_manifest.created_at,
                artifacts=tuple(
                    self._public_artifact_metadata(descriptor)
                    for descriptor in stored_manifest.descriptors
                ),
            )
        except (OSError, TypeError, ValueError):
            # Raise only after leaving the handler. Pydantic and JSON errors
            # may retain unsafe manifest input in their exception context.
            pass
        if public_manifest is None:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        return public_manifest

    @contextmanager
    def open_artifact(
        self,
        *,
        user_id: str,
        job_id: str,
        artifact_id: str,
    ) -> Iterator[Iterator[bytes]]:
        """Verify, rewind, and stream one artifact from the same descriptor."""

        job_directory = self.require_job_directory(
            user_id=user_id,
            job_id=job_id,
        )
        stored_manifest: _StoredArtifactManifest | None = None
        try:
            stored_manifest = self.load_verified_manifest(job_directory)
        except (OSError, TypeError, ValueError):
            # A topology race can include the private path in an OSError.
            # Translate only after leaving the handler so neither cause nor
            # context retains that path at the public stream boundary.
            pass
        if stored_manifest is None:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        selected_descriptor = next(
            (
                descriptor
                for descriptor in stored_manifest.descriptors
                if descriptor.artifact_id == artifact_id
            ),
            None,
        )
        if selected_descriptor is None:
            raise JobNotFoundError("The requested artifact was not found.")
        # This also rejects a private/debug artifact ID that is present in a
        # structurally valid legacy manifest but is not publicly downloadable.
        public_metadata: ArtifactMetadata | None = None
        try:
            public_metadata = self._public_artifact_metadata(selected_descriptor)
        except (TypeError, ValueError):
            pass
        if public_metadata is None:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )

        artifact_path = job_directory / selected_descriptor.file_name
        open_flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            open_flags |= os.O_NOFOLLOW
        try:
            file_descriptor = os.open(artifact_path, open_flags)
        except OSError:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            ) from None

        try:
            initial_status = os.fstat(file_descriptor)
            if (
                not S_ISREG(initial_status.st_mode)
                or initial_status.st_size != selected_descriptor.size_bytes
                or initial_status.st_size > self._maximum_job_bytes
            ):
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )

            with os.fdopen(file_descriptor, "rb", closefd=False) as input_file:
                observed_hash = sha256()
                observed_bytes = 0
                while True:
                    chunk = input_file.read(ARTIFACT_STREAM_CHUNK_BYTES)
                    if not chunk:
                        break
                    observed_bytes += len(chunk)
                    if observed_bytes > selected_descriptor.size_bytes:
                        raise ArtifactIntegrityError(
                            "Artifact storage failed integrity verification."
                        )
                    observed_hash.update(chunk)
                if (
                    observed_bytes != selected_descriptor.size_bytes
                    or observed_hash.hexdigest() != selected_descriptor.sha256_hex
                ):
                    raise ArtifactIntegrityError(
                        "Artifact storage failed integrity verification."
                    )

                # Recheck the open file, not its pathname. A replacement by
                # another process cannot redirect this descriptor, and a
                # same-inode write between hashing and rewind is detected.
                verified_status = os.fstat(file_descriptor)
                if _file_identity(initial_status) != _file_identity(verified_status):
                    raise ArtifactIntegrityError(
                        "Artifact storage failed integrity verification."
                    )
                input_file.seek(0)
                yield _iter_artifact_chunks(input_file)
        finally:
            os.close(file_descriptor)

    def load_verified_directory(
        self,
        job_directory: Path,
    ) -> tuple[dict[str, Any], dict[str, RenderedArtifact]]:
        """Read every body and reject path, type, size, or hash drift."""

        stored_manifest = self.load_verified_manifest(job_directory)
        restored_artifacts: dict[str, RenderedArtifact] = {}
        for descriptor in stored_manifest.descriptors:
            content = self._read_private_regular_file(
                job_directory / descriptor.file_name,
                maximum_bytes=descriptor.size_bytes,
            )
            if (
                len(content) != descriptor.size_bytes
                or sha256(content).hexdigest() != descriptor.sha256_hex
            ):
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            restored_artifacts[descriptor.artifact_id] = RenderedArtifact(
                file_name=descriptor.file_name,
                media_type=descriptor.media_type,
                content=content,
            )
        return stored_manifest.raw_manifest, restored_artifacts

    def load_verified_manifest(
        self,
        job_directory: Path,
    ) -> _StoredArtifactManifest:
        """Validate metadata and directory topology without opening body files."""

        self._require_confined_regular_directory(job_directory)
        manifest_bytes = self._read_private_regular_file(
            job_directory / _MANIFEST_FILE_NAME,
            maximum_bytes=_MAXIMUM_MANIFEST_BYTES,
        )
        parsed_manifest: object | None = None
        try:
            parsed_manifest = json.loads(manifest_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
        if not isinstance(parsed_manifest, dict):
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )

        schema_version = parsed_manifest.get("schema_version")
        raw_created_at = parsed_manifest.get("created_at")
        retention_days = parsed_manifest.get("retention_days")
        raw_artifacts = parsed_manifest.get("artifacts")
        if (
            schema_version != "1.0"
            or not isinstance(raw_created_at, str)
            or not isinstance(retention_days, int)
            or isinstance(retention_days, bool)
            or retention_days <= 0
            or not isinstance(raw_artifacts, dict)
            or not raw_artifacts
        ):
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )

        created_at: datetime | None = None
        try:
            created_at = datetime.fromisoformat(raw_created_at)
        except ValueError:
            pass
        if created_at is None or created_at.tzinfo is None:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        created_at = created_at.astimezone(UTC)

        descriptors: list[_StoredArtifactDescriptor] = []
        file_names: set[str] = set()
        declared_total_bytes = 0
        if not all(isinstance(artifact_id, str) for artifact_id in raw_artifacts):
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        for artifact_id in sorted(raw_artifacts):
            descriptor = self._validate_stored_descriptor(
                artifact_id=artifact_id,
                raw_descriptor=raw_artifacts[artifact_id],
            )
            if descriptor.file_name in file_names:
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            file_names.add(descriptor.file_name)
            declared_total_bytes += descriptor.size_bytes
            if declared_total_bytes > self._maximum_job_bytes:
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            descriptors.append(descriptor)

        expected_file_names = file_names | {_MANIFEST_FILE_NAME}
        expected_body_sizes = {
            descriptor.file_name: descriptor.size_bytes for descriptor in descriptors
        }
        actual_file_names: set[str] = set()
        for child in job_directory.iterdir():
            # ``is_file`` follows symlinks, so reject them before inspecting
            # the target type. Metadata queries must never open body files.
            child_status = child.stat(follow_symlinks=False)
            if child.is_symlink() or not S_ISREG(child_status.st_mode):
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            if (
                child.name != _MANIFEST_FILE_NAME
                and expected_body_sizes.get(child.name) != child_status.st_size
            ):
                # A metadata-only listing can compare lstat size without
                # opening the body. Content hashing remains the stream/full
                # read boundary so this query never loads artifact bytes.
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            actual_file_names.add(child.name)
        if actual_file_names != expected_file_names:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        return _StoredArtifactManifest(
            raw_manifest=parsed_manifest,
            created_at=created_at,
            descriptors=tuple(descriptors),
        )

    def _validate_stored_descriptor(
        self,
        *,
        artifact_id: object,
        raw_descriptor: object,
    ) -> _StoredArtifactDescriptor:
        """Validate one untrusted JSON descriptor without touching its body."""

        if (
            not isinstance(artifact_id, str)
            or _ARTIFACT_NAME_PATTERN.fullmatch(artifact_id) is None
            or not isinstance(raw_descriptor, dict)
        ):
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        file_name = raw_descriptor.get("file_name")
        media_type = raw_descriptor.get("media_type")
        size_bytes = raw_descriptor.get("size_bytes")
        expected_hash = raw_descriptor.get("sha256")
        if (
            not isinstance(file_name, str)
            or not file_name
            or len(file_name) > 255
            or Path(file_name).name != file_name
            or file_name in {".", "..", _MANIFEST_FILE_NAME}
            or "/" in file_name
            or "\\" in file_name
            or _has_control_characters(file_name)
            or not isinstance(media_type, str)
            or not 3 <= len(media_type) <= 255
            or "/" not in media_type
            or _has_control_characters(media_type)
            or not isinstance(size_bytes, int)
            or isinstance(size_bytes, bool)
            or not 0 <= size_bytes <= self._maximum_job_bytes
            or not isinstance(expected_hash, str)
            or _SHA256_HEX_PATTERN.fullmatch(expected_hash) is None
        ):
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        return _StoredArtifactDescriptor(
            artifact_id=artifact_id,
            file_name=file_name,
            media_type=media_type,
            size_bytes=size_bytes,
            sha256_hex=expected_hash,
        )

    def _public_artifact_metadata(
        self,
        descriptor: _StoredArtifactDescriptor,
    ) -> ArtifactMetadata:
        """Translate a private descriptor through the exact public ID map."""

        public_kind = _canonical_artifact_kind(descriptor.artifact_id)
        if public_kind is None:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        deliverable, artifact_format = public_kind
        return ArtifactMetadata(
            artifact_id=descriptor.artifact_id,
            deliverable=deliverable,
            format=artifact_format,
            safe_file_name=descriptor.file_name,
            media_type=descriptor.media_type,
            size_bytes=descriptor.size_bytes,
            content_hash=f"sha256:{descriptor.sha256_hex}",
        )

    def _require_confined_regular_directory(self, directory: Path) -> None:
        """Reject symlink substitution at any private directory component."""

        if directory.is_symlink() or not directory.is_dir():
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        try:
            resolved_directory = directory.resolve(strict=True)
        except OSError:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            ) from None
        if (
            resolved_directory != directory
            or self._root_directory not in resolved_directory.parents
        ):
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )

    def _read_private_regular_file(
        self,
        path: Path,
        *,
        maximum_bytes: int | None = None,
    ) -> bytes:
        """Read a bounded regular file without following a retained symlink."""

        byte_limit = self._maximum_job_bytes if maximum_bytes is None else maximum_bytes
        maximum_allowed_read = max(
            self._maximum_job_bytes,
            _MAXIMUM_MANIFEST_BYTES,
        )
        if byte_limit < 0 or byte_limit > maximum_allowed_read:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        open_flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            open_flags |= os.O_NOFOLLOW
        try:
            file_descriptor = os.open(path, open_flags)
        except OSError:
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            ) from None
        try:
            file_status = os.fstat(file_descriptor)
            if not S_ISREG(file_status.st_mode):
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            if file_status.st_size > byte_limit:
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            with os.fdopen(file_descriptor, "rb", closefd=False) as input_file:
                content = input_file.read(byte_limit + 1)
            if len(content) > byte_limit:
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            return content
        finally:
            os.close(file_descriptor)


def _file_identity(file_status: os.stat_result) -> tuple[int, int, int, int, int, int]:
    """Return fields that expose replacement, resizing, or in-place mutation."""

    return (
        file_status.st_dev,
        file_status.st_ino,
        file_status.st_mode,
        file_status.st_size,
        file_status.st_mtime_ns,
        file_status.st_ctime_ns,
    )


def _iter_artifact_chunks(input_file: BinaryIO) -> Iterator[bytes]:
    """Yield fixed-size chunks while the store-owned context remains active."""

    while True:
        chunk = input_file.read(ARTIFACT_STREAM_CHUNK_BYTES)
        if not chunk:
            return
        yield chunk
