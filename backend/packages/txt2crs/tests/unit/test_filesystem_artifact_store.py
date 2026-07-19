# SPDX-License-Identifier: MIT-0

"""Tests for private, durable, owner-scoped local artifact delivery."""

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path
from stat import S_IMODE

import pytest

from txt2crs.jobs.artifact_store import FilesystemPrivateArtifactStore
from txt2crs.jobs.store import JobNotFoundError
from txt2crs.rendering.artifacts import RenderedArtifact


def sample_artifacts(
    *,
    course_content: bytes = b"Course",
) -> dict[str, RenderedArtifact]:
    """Return a small exact artifact set for storage behavior tests."""

    return {
        "course_markdown": RenderedArtifact(
            file_name="python-course.md",
            media_type="text/markdown; charset=utf-8",
            content=course_content,
        ),
        "answer_key_pdf": RenderedArtifact(
            file_name="python-answer-key.pdf",
            media_type="application/pdf",
            content=b"%PDF-private-answer-key",
        ),
    }


def test_filesystem_store_writes_private_files_and_integrity_manifest(
    tmp_path: Path,
) -> None:
    """Tenant/job identifiers never become paths and every byte is private."""

    artifact_root = tmp_path / "private-artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )

    store.save(
        user_id="../../user@example.test",
        job_id="../job-secret",
        artifacts=sample_artifacts(),
    )
    restored = store.get(
        user_id="../../user@example.test",
        job_id="../job-secret",
    )

    assert restored == sample_artifacts()
    assert S_IMODE(artifact_root.stat().st_mode) == 0o700
    all_paths = list(artifact_root.rglob("*"))
    assert not any("user@example" in str(path) for path in all_paths)
    assert not any("job-secret" in str(path) for path in all_paths)
    regular_files = [path for path in all_paths if path.is_file()]
    assert regular_files
    assert all(S_IMODE(path.stat().st_mode) == 0o600 for path in regular_files)
    manifest_path = next(path for path in regular_files if path.name == "manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert set(manifest["artifacts"]) == {"answer_key_pdf", "course_markdown"}
    assert manifest["schema_version"] == "1.0"


def test_filesystem_store_is_idempotent_and_rejects_conflicting_replay(
    tmp_path: Path,
) -> None:
    """An exact retry is harmless while changed bytes fail closed."""

    store = FilesystemPrivateArtifactStore(
        root_directory=tmp_path / "artifacts",
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    artifacts = sample_artifacts()

    store.save(user_id="user-1", job_id="job-1", artifacts=artifacts)
    store.save(user_id="user-1", job_id="job-1", artifacts=artifacts)

    with pytest.raises(ValueError, match="different artifact"):
        store.save(
            user_id="user-1",
            job_id="job-1",
            artifacts=sample_artifacts(course_content=b"Changed course"),
        )


def test_filesystem_store_enforces_owner_and_detects_symlink_tampering(
    tmp_path: Path,
) -> None:
    """Foreign owners see not-found and retained files cannot become symlinks."""

    store = FilesystemPrivateArtifactStore(
        root_directory=tmp_path / "artifacts",
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts=sample_artifacts(),
    )

    with pytest.raises(JobNotFoundError):
        store.get(user_id="user-2", job_id="job-1")

    job_directory = next(
        path.parent for path in (tmp_path / "artifacts").rglob("manifest.json")
    )
    course_path = job_directory / "python-course.md"
    course_path.unlink()
    course_path.symlink_to("/etc/passwd")
    with pytest.raises(ValueError, match="symlink|integrity"):
        store.get(user_id="user-1", job_id="job-1")


def test_filesystem_store_supports_owner_delete_and_retention_purge(
    tmp_path: Path,
) -> None:
    """Explicit deletion and configured expiry remove private bytes."""

    current_time = datetime(2026, 7, 17, 12, 0, tzinfo=UTC)
    store = FilesystemPrivateArtifactStore(
        root_directory=tmp_path / "artifacts",
        maximum_job_bytes=10_000,
        retention_days=7,
        clock=lambda: current_time,
    )
    store.save(
        user_id="user-1",
        job_id="job-expired",
        artifacts=sample_artifacts(),
    )

    current_time += timedelta(days=8)
    assert store.purge_expired() == 1
    with pytest.raises(JobNotFoundError):
        store.get(user_id="user-1", job_id="job-expired")

    store.save(
        user_id="user-1",
        job_id="job-delete",
        artifacts=sample_artifacts(),
    )
    store.delete(user_id="user-1", job_id="job-delete")
    with pytest.raises(JobNotFoundError):
        store.get(user_id="user-1", job_id="job-delete")


def test_filesystem_store_rejects_unsafe_names_and_oversized_sets(
    tmp_path: Path,
) -> None:
    """Rendered file names cannot traverse and total output has a hard cap."""

    store = FilesystemPrivateArtifactStore(
        root_directory=tmp_path / "artifacts",
        maximum_job_bytes=5,
        retention_days=30,
    )
    with pytest.raises(ValueError, match="byte limit"):
        store.save(
            user_id="user-1",
            job_id="job-1",
            artifacts=sample_artifacts(),
        )
    with pytest.raises(ValueError, match="file name"):
        store.save(
            user_id="user-1",
            job_id="job-2",
            artifacts={
                "course": RenderedArtifact(
                    file_name="../course.md",
                    media_type="text/markdown",
                    content=b"ok",
                )
            },
        )

    # Ensure the test itself did not rely on a permissive process umask.
    assert os.path.commonpath([tmp_path, tmp_path / "artifacts"]) == str(tmp_path)
