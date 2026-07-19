# SPDX-License-Identifier: MIT-0

"""Atomic private filesystem storage for rendered learner artifacts."""

import json
import os
import re
import shutil
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from stat import S_ISREG
from typing import Any

from txt2crs.jobs.store import JobNotFoundError
from txt2crs.rendering.artifacts import RenderedArtifact

_ARTIFACT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_MANIFEST_FILE_NAME = "manifest.json"


class FilesystemPrivateArtifactStore:
    """Persist immutable artifact sets under non-identifying private paths.

    Raw user and job identifiers never become directory names. Their hashes
    provide stable owner scoping without leaking email addresses or allowing
    path traversal. Each complete job directory appears atomically only after
    every artifact and the integrity manifest have been written.
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

    def save(
        self,
        *,
        user_id: str,
        job_id: str,
        artifacts: dict[str, RenderedArtifact],
    ) -> None:
        """Atomically persist one exact private artifact set."""

        manifest_artifacts = self._validate_and_describe_artifacts(artifacts)
        job_directory = self._job_directory(user_id=user_id, job_id=job_id)
        if job_directory.exists():
            existing_manifest, _existing_artifacts = self._load_verified_directory(
                job_directory
            )
            if existing_manifest["artifacts"] != manifest_artifacts:
                raise ValueError(
                    "A different artifact set already exists for this job."
                )
            return
        if job_directory.is_symlink():
            raise ValueError("Private job directory cannot be a symlink.")

        job_parent = job_directory.parent
        self._ensure_private_directory(job_parent.parent.parent)
        self._ensure_private_directory(job_parent.parent)
        self._ensure_private_directory(job_parent)
        temporary_directory = Path(
            tempfile.mkdtemp(prefix=".txt2crs-stage-", dir=job_parent)
        )
        temporary_directory.chmod(0o700)
        manifest = {
            "schema_version": "1.0",
            "created_at": self._now().isoformat(),
            "retention_days": self._retention_days,
            "artifacts": manifest_artifacts,
        }
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
            manifest_bytes = json.dumps(
                manifest,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
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
                existing_manifest, _existing_artifacts = self._load_verified_directory(
                    job_directory
                )
                if existing_manifest["artifacts"] != manifest_artifacts:
                    raise ValueError(
                        "A different artifact set already exists for this job."
                    ) from publish_error
        finally:
            if temporary_directory.exists():
                shutil.rmtree(temporary_directory)

    def get(
        self,
        *,
        user_id: str,
        job_id: str,
    ) -> dict[str, RenderedArtifact]:
        """Return verified bytes only for the exact owner and job."""

        job_directory = self._job_directory(user_id=user_id, job_id=job_id)
        if not job_directory.exists():
            raise JobNotFoundError("The requested artifacts were not found.")
        if job_directory.is_symlink():
            raise ValueError("Private job directory symlink failed integrity.")
        _manifest, artifacts = self._load_verified_directory(job_directory)
        return artifacts

    def delete(self, *, user_id: str, job_id: str) -> None:
        """Delete one owner-authorized job artifact directory."""

        job_directory = self._job_directory(user_id=user_id, job_id=job_id)
        if not job_directory.exists():
            raise JobNotFoundError("The requested artifacts were not found.")
        if job_directory.is_symlink():
            raise ValueError("Private job directory symlink failed integrity.")
        shutil.rmtree(job_directory)
        self._prune_empty_parent_directories(job_directory.parent)

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
                manifest, _artifacts = self._load_verified_directory(job_directory)
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

        if not artifacts:
            raise ValueError("At least one rendered artifact is required.")
        total_bytes = sum(len(artifact.content) for artifact in artifacts.values())
        if total_bytes > self._maximum_job_bytes:
            raise ValueError("Rendered artifacts exceed the configured byte limit.")

        file_names: set[str] = set()
        manifest_artifacts: dict[str, dict[str, str | int]] = {}
        for artifact_name, artifact in sorted(artifacts.items()):
            if _ARTIFACT_NAME_PATTERN.fullmatch(artifact_name) is None:
                raise ValueError("Artifact name is not a safe identifier.")
            file_name = artifact.file_name
            if (
                not file_name
                or len(file_name) > 255
                or file_name in {".", "..", _MANIFEST_FILE_NAME}
                or Path(file_name).name != file_name
                or "/" in file_name
                or "\\" in file_name
            ):
                raise ValueError("Rendered artifact file name is unsafe.")
            if file_name in file_names:
                raise ValueError("Rendered artifact file names must be unique.")
            file_names.add(file_name)
            manifest_artifacts[artifact_name] = {
                "file_name": file_name,
                "media_type": artifact.media_type,
                "size_bytes": len(artifact.content),
                "sha256": sha256(artifact.content).hexdigest(),
            }
        return manifest_artifacts

    def _load_verified_directory(
        self,
        job_directory: Path,
    ) -> tuple[dict[str, Any], dict[str, RenderedArtifact]]:
        """Read one manifest and reject any path, type, size, or hash drift."""

        manifest_path = job_directory / _MANIFEST_FILE_NAME
        manifest_bytes = self._read_private_regular_file(manifest_path)
        try:
            manifest = json.loads(manifest_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as manifest_error:
            raise ValueError("Artifact manifest failed integrity.") from manifest_error
        if (
            not isinstance(manifest, dict)
            or manifest.get("schema_version") != "1.0"
            or not isinstance(manifest.get("artifacts"), dict)
            or not isinstance(manifest.get("created_at"), str)
        ):
            raise ValueError("Artifact manifest failed integrity.")

        described_artifacts = manifest["artifacts"]
        expected_file_names = {_MANIFEST_FILE_NAME}
        restored_artifacts: dict[str, RenderedArtifact] = {}
        total_bytes = 0
        for artifact_name, raw_description in described_artifacts.items():
            if not isinstance(artifact_name, str) or not isinstance(
                raw_description, dict
            ):
                raise ValueError("Artifact manifest failed integrity.")
            file_name = raw_description.get("file_name")
            media_type = raw_description.get("media_type")
            size_bytes = raw_description.get("size_bytes")
            expected_hash = raw_description.get("sha256")
            if (
                not isinstance(file_name, str)
                or Path(file_name).name != file_name
                or not isinstance(media_type, str)
                or not isinstance(size_bytes, int)
                or size_bytes < 0
                or not isinstance(expected_hash, str)
            ):
                raise ValueError("Artifact manifest failed integrity.")
            content = self._read_private_regular_file(job_directory / file_name)
            if (
                len(content) != size_bytes
                or sha256(content).hexdigest() != expected_hash
            ):
                raise ValueError("Artifact file failed integrity.")
            total_bytes += len(content)
            expected_file_names.add(file_name)
            restored_artifacts[artifact_name] = RenderedArtifact(
                file_name=file_name,
                media_type=media_type,
                content=content,
            )
        if total_bytes > self._maximum_job_bytes:
            raise ValueError("Stored artifacts exceed the configured byte limit.")
        actual_file_names = {
            child.name
            for child in job_directory.iterdir()
            if child.is_file() or child.is_symlink()
        }
        if actual_file_names != expected_file_names:
            raise ValueError("Artifact directory failed manifest integrity.")
        return manifest, restored_artifacts

    def _job_directory(self, *, user_id: str, job_id: str) -> Path:
        """Return a confined path made only from opaque identifier hashes."""

        owner_hash = sha256(user_id.encode("utf-8")).hexdigest()
        job_hash = sha256(job_id.encode("utf-8")).hexdigest()
        return self._root_directory / "owners" / owner_hash / "jobs" / job_hash

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

    def _read_private_regular_file(self, path: Path) -> bytes:
        """Read a bounded regular file without following a retained symlink."""

        open_flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            open_flags |= os.O_NOFOLLOW
        try:
            file_descriptor = os.open(path, open_flags)
        except OSError as file_open_error:
            raise ValueError(
                "Artifact file symlink or type failed integrity."
            ) from file_open_error
        try:
            file_status = os.fstat(file_descriptor)
            if not S_ISREG(file_status.st_mode):
                raise ValueError("Artifact file type failed integrity.")
            if file_status.st_size > self._maximum_job_bytes:
                raise ValueError("Stored artifact exceeds the configured byte limit.")
            with os.fdopen(file_descriptor, "rb", closefd=False) as input_file:
                content = input_file.read(self._maximum_job_bytes + 1)
            if len(content) > self._maximum_job_bytes:
                raise ValueError("Stored artifact exceeds the configured byte limit.")
            return content
        finally:
            os.close(file_descriptor)

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
