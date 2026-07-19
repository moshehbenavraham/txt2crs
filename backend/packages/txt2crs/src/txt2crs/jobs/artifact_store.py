# SPDX-License-Identifier: MIT-0

"""Atomic private filesystem storage for rendered learner artifacts."""

import json
import os
import shutil
import tempfile
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from txt2crs.domain.models import Identifier
from txt2crs.jobs.artifact_queries import (
    _MANIFEST_FILE_NAME,
    _MAXIMUM_MANIFEST_BYTES,
    ARTIFACT_STREAM_CHUNK_BYTES,
    ArtifactDeliverable,
    ArtifactFormat,
    ArtifactIntegrityError,
    ArtifactManifest,
    ArtifactMetadata,
    _validate_private_rendered_artifact_metadata,
)
from txt2crs.jobs.artifact_reader import FilesystemArtifactReader
from txt2crs.rendering.artifacts import RenderedArtifact


class FilesystemPrivateArtifactStore:
    """Persist immutable artifact sets under non-identifying private paths.

    Raw user and job identifiers never become directory names. Their hashes
    provide stable owner scoping without leaking email addresses or allowing
    path traversal. Each complete job directory appears atomically only after
    every artifact and the integrity manifest have been written.

    Read-side manifest, topology, and descriptor verification lives in the
    cohesive ``FilesystemArtifactReader``. This class owns atomic writes,
    deletion, retention, and directory lifecycle.
    """

    def __init__(
        self,
        *,
        root_directory: Path,
        maximum_job_bytes: int,
        retention_days: int,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if maximum_job_bytes <= 0:
            raise ValueError("maximum_job_bytes must be positive.")
        if retention_days <= 0:
            raise ValueError("retention_days must be positive.")
        if root_directory.is_symlink():
            raise ValueError("Artifact root cannot be a symlink.")
        root_directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        root_directory.chmod(0o700)
        self._root_directory = root_directory.resolve(strict=True)
        self._maximum_job_bytes = maximum_job_bytes
        self._retention_days = retention_days
        self._clock = clock or (lambda: datetime.now(UTC))
        self._reader = FilesystemArtifactReader(
            root_directory=self._root_directory,
            maximum_job_bytes=maximum_job_bytes,
        )

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Atomically persist one exact private artifact set."""

        manifest_artifacts = self._validate_and_describe_artifacts(artifacts)
        job_directory = self._reader.job_directory(
            user_id=user_id,
            job_id=job_id,
        )
        if job_directory.exists():
            existing_manifest, _existing_artifacts = (
                self._reader.load_verified_directory(job_directory)
            )
            if existing_manifest["artifacts"] != manifest_artifacts:
                raise ValueError(
                    "A different artifact set already exists for this job."
                )
            return
        if job_directory.is_symlink():
            raise ValueError("Private job directory cannot be a symlink.")

        manifest = {
            "schema_version": "1.0",
            "created_at": self._now().isoformat(),
            "retention_days": self._retention_days,
            "artifacts": manifest_artifacts,
        }
        manifest_bytes = json.dumps(
            manifest,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        if len(manifest_bytes) > _MAXIMUM_MANIFEST_BYTES:
            raise ValueError("Artifact manifest exceeds the configured byte limit.")

        job_parent = job_directory.parent
        self._ensure_private_directory(job_parent.parent.parent)
        self._ensure_private_directory(job_parent.parent)
        self._ensure_private_directory(job_parent)
        temporary_directory = Path(
            tempfile.mkdtemp(prefix=".txt2crs-stage-", dir=job_parent)
        )
        temporary_directory.chmod(0o700)
        try:
            for artifact_name, artifact in sorted(artifacts.items()):
                # The manifest has already validated that this file name is a
                # basename and is unique inside the artifact set.
                self._write_private_file(
                    temporary_directory / artifact.file_name,
                    artifact.content,
                )
                if artifact_name not in manifest_artifacts:
                    raise AssertionError("Artifact manifest drifted during write.")
            self._write_private_file(
                temporary_directory / _MANIFEST_FILE_NAME,
                manifest_bytes,
            )
            try:
                temporary_directory.rename(job_directory)
            except OSError as publish_error:
                # A competing worker may have published the same set first.
                # Verify it exactly; never overwrite a completed directory.
                if not job_directory.exists():
                    raise
                existing_manifest, _existing_artifacts = (
                    self._reader.load_verified_directory(job_directory)
                )
                if existing_manifest["artifacts"] != manifest_artifacts:
                    raise ValueError(
                        "A different artifact set already exists for this job."
                    ) from publish_error
        finally:
            if temporary_directory.exists():
                shutil.rmtree(temporary_directory)

    def probe_readiness(self) -> bool:
        """
        Atomically write, read, and remove a confined maintenance probe.

        This deliberately avoids owner/job directory naming so no durable
        learner-shaped state is created. The surrounding readiness cache runs
        it only at startup and a bounded maintenance interval.
        """

        temporary_directory: Path | None = None
        try:
            temporary_directory = Path(
                tempfile.mkdtemp(
                    prefix=".txt2crs-readiness-",
                    dir=self._root_directory,
                )
            )
            temporary_directory.chmod(0o700)
            staged_path = temporary_directory / "probe.staged"
            published_path = temporary_directory / "probe.ready"
            probe_content = b"txt2crs-readiness-v1"
            self._write_private_file(staged_path, probe_content)
            staged_path.replace(published_path)
            if published_path.read_bytes() != probe_content:
                return False
            published_path.unlink()
            return True
        except Exception:
            return False
        finally:
            if temporary_directory is not None and temporary_directory.exists():
                shutil.rmtree(temporary_directory)

    def get(
        self,
        *,
        user_id: str,
        job_id: str,
    ) -> dict[str, RenderedArtifact]:
        """Return verified bytes only for the exact owner and job."""

        job_directory = self._reader.require_job_directory(
            user_id=user_id,
            job_id=job_id,
        )
        _manifest, artifacts = self._reader.load_verified_directory(job_directory)
        return artifacts

    def get_manifest(
        self,
        *,
        user_id: str,
        job_id: str,
    ) -> ArtifactManifest:
        """Return verified public metadata without opening artifact bodies."""

        return self._reader.get_manifest(user_id=user_id, job_id=job_id)

    def open_artifact(
        self,
        *,
        user_id: str,
        job_id: str,
        artifact_id: str,
    ) -> AbstractContextManager[Iterator[bytes]]:
        """Return one reader-owned verified artifact context."""

        return self._reader.open_artifact(
            user_id=user_id,
            job_id=job_id,
            artifact_id=artifact_id,
        )

    def delete(self, *, user_id: str, job_id: str) -> None:
        """Delete one owner-authorized job artifact directory."""

        job_directory = self._reader.require_job_directory(
            user_id=user_id,
            job_id=job_id,
        )
        shutil.rmtree(job_directory)
        self._prune_empty_parent_directories(job_directory.parent)

    def purge_owner(self, *, user_id: str) -> int:
        """Idempotently delete one confined hashed owner artifact tree."""

        normalized_user_id: str | None = None
        try:
            normalized_user_id = TypeAdapter(Identifier).validate_python(user_id)
        except ValidationError:
            pass
        if normalized_user_id is None:
            raise ValueError("The owner identity is invalid.")

        owner_directory = self._reader.owner_directory(user_id=normalized_user_id)
        if owner_directory.is_symlink():
            raise ArtifactIntegrityError(
                "Artifact storage failed integrity verification."
            )
        if not owner_directory.exists():
            return 0
        self._reader.require_confined_directory(owner_directory)
        jobs_directory = owner_directory / "jobs"
        deleted_job_count = 0
        if jobs_directory.exists():
            if jobs_directory.is_symlink():
                raise ArtifactIntegrityError(
                    "Artifact storage failed integrity verification."
                )
            self._reader.require_confined_directory(jobs_directory)
            for job_directory in jobs_directory.iterdir():
                if job_directory.is_symlink() or not job_directory.is_dir():
                    raise ArtifactIntegrityError(
                        "Artifact storage failed integrity verification."
                    )
                deleted_job_count += 1
        shutil.rmtree(owner_directory)
        self._prune_empty_parent_directories(owner_directory.parent)
        return deleted_job_count

    def purge_expired(self) -> int:
        """Delete verified jobs older than the configured retention window."""

        cutoff = self._now() - timedelta(days=self._retention_days)
        owners_directory = self._root_directory / "owners"
        if not owners_directory.exists():
            return 0
        deleted_count = 0
        for jobs_directory in owners_directory.glob("*/jobs"):
            if jobs_directory.is_symlink() or not jobs_directory.is_dir():
                continue
            for job_directory in list(jobs_directory.iterdir()):
                if job_directory.is_symlink() or not job_directory.is_dir():
                    continue
                manifest, _artifacts = self._reader.load_verified_directory(
                    job_directory
                )
                created_at = datetime.fromisoformat(str(manifest["created_at"]))
                if created_at <= cutoff:
                    shutil.rmtree(job_directory)
                    deleted_count += 1
            self._prune_empty_parent_directories(jobs_directory)
        return deleted_count

    def _validate_and_describe_artifacts(
        self,
        artifacts: dict[str, RenderedArtifact],
    ) -> dict[str, dict[str, str | int]]:
        """Validate names and bounds, then derive the immutable manifest."""

        _validate_private_rendered_artifact_metadata(artifacts)
        total_bytes = sum(len(artifact.content) for artifact in artifacts.values())
        if total_bytes > self._maximum_job_bytes:
            raise ValueError("Rendered artifacts exceed the configured byte limit.")

        manifest_artifacts: dict[str, dict[str, str | int]] = {}
        for artifact_name, artifact in sorted(artifacts.items()):
            manifest_artifacts[artifact_name] = {
                "file_name": artifact.file_name,
                "media_type": artifact.media_type,
                "size_bytes": len(artifact.content),
                "sha256": sha256(artifact.content).hexdigest(),
            }
        return manifest_artifacts

    def _ensure_private_directory(self, directory: Path) -> None:
        """Create one store-owned directory and forbid symlink substitution."""

        if directory.is_symlink():
            raise ValueError("Private artifact directory cannot be a symlink.")
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        directory.chmod(0o700)
        resolved_directory = directory.resolve(strict=True)
        if (
            resolved_directory != self._root_directory
            and self._root_directory not in resolved_directory.parents
        ):
            raise ValueError("Private artifact path escaped its configured root.")

    def _write_private_file(self, path: Path, content: bytes) -> None:
        """Create one non-following file with owner-only permissions."""

        open_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            open_flags |= os.O_NOFOLLOW
        file_descriptor = os.open(path, open_flags, 0o600)
        try:
            with os.fdopen(file_descriptor, "wb", closefd=False) as output_file:
                output_file.write(content)
                output_file.flush()
                os.fsync(output_file.fileno())
        finally:
            os.close(file_descriptor)
        path.chmod(0o600)

    def _prune_empty_parent_directories(self, starting_directory: Path) -> None:
        """Remove empty hashed parents without ever crossing the store root."""

        current_directory = starting_directory
        while (
            current_directory != self._root_directory
            and self._root_directory in current_directory.parents
        ):
            try:
                current_directory.rmdir()
            except OSError:
                break
            current_directory = current_directory.parent

    def _now(self) -> datetime:
        """Return an aware timestamp so retention comparisons are unambiguous."""

        current_time = self._clock()
        if current_time.tzinfo is None:
            raise ValueError("Artifact store clock must return a timezone-aware time.")
        return current_time.astimezone(UTC)


__all__ = [
    "ARTIFACT_STREAM_CHUNK_BYTES",
    "ArtifactDeliverable",
    "ArtifactFormat",
    "ArtifactIntegrityError",
    "ArtifactManifest",
    "ArtifactMetadata",
    "FilesystemPrivateArtifactStore",
]
