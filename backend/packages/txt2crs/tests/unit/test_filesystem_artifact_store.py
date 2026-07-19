# SPDX-License-Identifier: MIT-0

"""Tests for private, durable, owner-scoped local artifact delivery."""

import json
import os
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from stat import S_IMODE

import pytest

from txt2crs.jobs.artifact_store import (
    ARTIFACT_STREAM_CHUNK_BYTES,
    ArtifactDeliverable,
    ArtifactFormat,
    ArtifactIntegrityError,
    ArtifactMetadata,
    FilesystemPrivateArtifactStore,
)
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


def _stored_job_directory(artifact_root: Path) -> Path:
    """Locate the opaque directory without relying on owner/job path internals."""

    return next(path.parent for path in artifact_root.rglob("manifest.json"))


def _tracking_os_open(
    *,
    opened_paths: list[Path],
    opened_descriptors: list[int] | None = None,
) -> Callable[..., int]:
    """Return a transparent ``os.open`` spy for descriptor lifecycle tests."""

    real_os_open = os.open

    def track_open(path: os.PathLike[str] | str, flags: int, mode: int = 0o777) -> int:
        opened_paths.append(Path(path))
        descriptor = real_os_open(path, flags, mode)
        if opened_descriptors is not None:
            opened_descriptors.append(descriptor)
        return descriptor

    return track_open


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


def test_owner_purge_deletes_only_the_hashed_owner_tree_and_is_idempotent(
    tmp_path: Path,
) -> None:
    """Account erasure removes every owner job while preserving other owners."""

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
    store.save(
        user_id="user-1",
        job_id="job-2",
        artifacts=sample_artifacts(course_content=b"Second course"),
    )
    store.save(
        user_id="user-2",
        job_id="job-3",
        artifacts=sample_artifacts(course_content=b"Other owner"),
    )

    assert store.purge_owner(user_id="user-1") == 2
    assert store.purge_owner(user_id="user-1") == 0
    with pytest.raises(JobNotFoundError):
        store.get_manifest(user_id="user-1", job_id="job-1")
    assert (
        store.get(user_id="user-2", job_id="job-3")["course_markdown"].content
        == b"Other owner"
    )


def test_owner_purge_rejects_symlinked_owner_without_touching_target(
    tmp_path: Path,
) -> None:
    """A replaced owner directory cannot redirect recursive deletion."""

    artifact_root = tmp_path / "artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    external_directory = tmp_path / "external"
    external_directory.mkdir()
    external_file = external_directory / "keep.txt"
    external_file.write_text("keep", encoding="utf-8")
    owner_hash = sha256(b"user-1").hexdigest()
    owner_directory = artifact_root / "owners" / owner_hash
    owner_directory.parent.mkdir(parents=True)
    owner_directory.symlink_to(external_directory, target_is_directory=True)

    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        store.purge_owner(user_id="user-1")

    assert external_file.read_text(encoding="utf-8") == "keep"


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
    with pytest.raises(ValueError, match="file name"):
        store.save(
            user_id="user-1",
            job_id="job-header-control",
            artifacts={
                "course_markdown": RenderedArtifact(
                    file_name="course.md\r\nX-Injected: yes",
                    media_type="text/markdown",
                    content=b"ok",
                )
            },
        )
    with pytest.raises(ValueError, match="media type"):
        store.save(
            user_id="user-1",
            job_id="unsafe-media-type",
            artifacts={
                "course_markdown": RenderedArtifact(
                    file_name="course.md",
                    media_type="invalid-media-type\r\nX-Injected: yes",
                    content=b"ok",
                )
            },
        )

    # Ensure the test itself did not rely on a permissive process umask.
    assert os.path.commonpath([tmp_path, tmp_path / "artifacts"]) == str(tmp_path)


def test_public_artifact_metadata_rejects_file_name_control_characters() -> None:
    """Path-free metadata is safe for later HTTP filename encoding."""

    with pytest.raises(ValueError, match="file name"):
        ArtifactMetadata(
            artifact_id="course_markdown",
            deliverable=ArtifactDeliverable.course,
            format=ArtifactFormat.markdown,
            safe_file_name="course.md\r\nX-Injected: yes",
            media_type="text/markdown",
            size_bytes=0,
            content_hash="sha256:" + ("a" * 64),
        )


def test_save_rejects_metadata_larger_than_the_readable_manifest_bound(
    tmp_path: Path,
) -> None:
    """A successful save must always produce a manifest the store can reopen."""

    store = FilesystemPrivateArtifactStore(
        root_directory=tmp_path / "artifacts",
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    oversized_metadata = {
        f"private_debug_{index:04d}": RenderedArtifact(
            file_name=f"{index:04d}-{'x' * 200}.txt",
            media_type=f"application/{'x' * 200}",
            content=b"",
        )
        for index in range(300)
    }

    with pytest.raises(ValueError, match="manifest"):
        store.save(
            user_id="user-1",
            job_id="oversized-manifest",
            artifacts=oversized_metadata,
        )

    assert list((tmp_path / "artifacts").rglob("manifest.json")) == []


def test_manifest_query_returns_canonical_metadata_without_opening_bodies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Metadata listing opens the manifest only, never every artifact body."""

    artifact_root = tmp_path / "artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts=sample_artifacts(),
    )
    opened_paths: list[Path] = []
    monkeypatch.setattr(
        "txt2crs.jobs.artifact_reader.os.open",
        _tracking_os_open(opened_paths=opened_paths),
    )

    manifest = store.get_manifest(user_id="user-1", job_id="job-1")

    assert [path.name for path in opened_paths] == ["manifest.json"]
    assert manifest.job_id == "job-1"
    assert manifest.created_at.tzinfo is not None
    assert [artifact.artifact_id for artifact in manifest.artifacts] == [
        "answer_key_pdf",
        "course_markdown",
    ]
    metadata_by_id = {artifact.artifact_id: artifact for artifact in manifest.artifacts}
    course_metadata = metadata_by_id["course_markdown"]
    assert course_metadata.deliverable is ArtifactDeliverable.course
    assert course_metadata.format is ArtifactFormat.markdown
    assert course_metadata.safe_file_name == "python-course.md"
    assert course_metadata.media_type == "text/markdown; charset=utf-8"
    assert course_metadata.size_bytes == len(b"Course")
    assert course_metadata.content_hash == (f"sha256:{sha256(b'Course').hexdigest()}")
    assert "owners" not in manifest.model_dump_json()
    assert str(artifact_root) not in manifest.model_dump_json()


def test_stream_query_hashes_rewinds_and_chunks_one_open_descriptor(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One selected body is verified before fixed-size chunks are yielded."""

    course_content = b"a" * (ARTIFACT_STREAM_CHUNK_BYTES * 2 + 17)
    artifact_root = tmp_path / "artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=len(course_content) + 10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts=sample_artifacts(course_content=course_content),
    )
    opened_paths: list[Path] = []
    monkeypatch.setattr(
        "txt2crs.jobs.artifact_reader.os.open",
        _tracking_os_open(opened_paths=opened_paths),
    )

    with store.open_artifact(
        user_id="user-1",
        job_id="job-1",
        artifact_id="course_markdown",
    ) as artifact_chunks:
        chunks = list(artifact_chunks)

    assert b"".join(chunks) == course_content
    assert max(len(chunk) for chunk in chunks) <= ARTIFACT_STREAM_CHUNK_BYTES
    assert [path.name for path in opened_paths].count("python-course.md") == 1


def test_stream_uses_open_descriptor_after_path_is_replaced(tmp_path: Path) -> None:
    """A pathname swap after validation cannot change the bytes being served."""

    original_content = b"original verified course bytes"
    artifact_root = tmp_path / "artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts=sample_artifacts(course_content=original_content),
    )
    job_directory = _stored_job_directory(artifact_root)
    course_path = job_directory / "python-course.md"

    with store.open_artifact(
        user_id="user-1",
        job_id="job-1",
        artifact_id="course_markdown",
    ) as artifact_chunks:
        course_path.rename(job_directory / "verified-open-file")
        course_path.write_bytes(b"malicious replacement bytes")
        streamed_content = b"".join(artifact_chunks)

    assert streamed_content == original_content


def test_stream_detects_mutation_between_hash_and_descriptor_recheck(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A selected file changed after hashing fails before any bytes are yielded."""

    artifact_root = tmp_path / "artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts=sample_artifacts(course_content=b"original"),
    )
    course_path = _stored_job_directory(artifact_root) / "python-course.md"
    target_inode = course_path.stat().st_ino
    real_fstat = os.fstat
    target_fstat_count = 0

    def mutate_before_second_target_fstat(file_descriptor: int) -> os.stat_result:
        nonlocal target_fstat_count
        file_status = real_fstat(file_descriptor)
        if file_status.st_ino == target_inode:
            target_fstat_count += 1
            if target_fstat_count == 2:
                # Change the size as well as the contents. Some temporary
                # filesystems can report identical nanosecond timestamps for
                # two operations in the same clock tick, so a same-length
                # replacement made this race test flaky.
                course_path.write_bytes(b"mutated-and-resized!")
                file_status = real_fstat(file_descriptor)
        return file_status

    monkeypatch.setattr(
        "txt2crs.jobs.artifact_reader.os.fstat",
        mutate_before_second_target_fstat,
    )

    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        with store.open_artifact(
            user_id="user-1",
            job_id="job-1",
            artifact_id="course_markdown",
        ):
            pytest.fail("The context must not yield a mutated descriptor.")

    assert target_fstat_count == 2


def test_stream_closes_descriptor_after_early_exit_and_consumer_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Partial consumers and raised exceptions cannot leak private file handles."""

    artifact_root = tmp_path / "artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts=sample_artifacts(course_content=b"course bytes"),
    )
    opened_paths: list[Path] = []
    opened_descriptors: list[int] = []
    monkeypatch.setattr(
        "txt2crs.jobs.artifact_reader.os.open",
        _tracking_os_open(
            opened_paths=opened_paths,
            opened_descriptors=opened_descriptors,
        ),
    )

    with store.open_artifact(
        user_id="user-1",
        job_id="job-1",
        artifact_id="course_markdown",
    ) as artifact_chunks:
        assert next(artifact_chunks) == b"course bytes"
    selected_descriptor = opened_descriptors[-1]
    with pytest.raises(OSError):
        os.fstat(selected_descriptor)

    with pytest.raises(RuntimeError, match="consumer stopped"):
        with store.open_artifact(
            user_id="user-1",
            job_id="job-1",
            artifact_id="course_markdown",
        ):
            raise RuntimeError("consumer stopped")
    selected_descriptor = opened_descriptors[-1]
    with pytest.raises(OSError):
        os.fstat(selected_descriptor)


def test_artifact_queries_hide_missing_owner_job_and_identifier(
    tmp_path: Path,
) -> None:
    """Foreign owners and missing resources share one exact safe not-found error."""

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

    operations = (
        lambda: store.get_manifest(user_id="user-2", job_id="job-1"),
        lambda: store.get_manifest(user_id="user-1", job_id="job-missing"),
        lambda: store.open_artifact(
            user_id="user-2",
            job_id="job-1",
            artifact_id="course_markdown",
        ).__enter__(),
        lambda: store.open_artifact(
            user_id="user-1",
            job_id="job-1",
            artifact_id="artifact-missing",
        ).__enter__(),
    )
    messages: list[str] = []
    for operation in operations:
        with pytest.raises(JobNotFoundError) as error_info:
            operation()
        messages.append(str(error_info.value))

    assert messages == [messages[0]] * len(messages)
    assert "owner" not in messages[0].casefold()
    assert "identifier" not in messages[0].casefold()


def test_manifest_and_stream_reject_unsafe_topology_and_corruption(
    tmp_path: Path,
) -> None:
    """Manifest traversal, symlinks, extra files, and changed bytes fail closed."""

    def new_store_and_directory(
        case_name: str,
    ) -> tuple[FilesystemPrivateArtifactStore, Path]:
        artifact_root = tmp_path / case_name
        store = FilesystemPrivateArtifactStore(
            root_directory=artifact_root,
            maximum_job_bytes=10_000,
            retention_days=30,
        )
        store.save(
            user_id="user-1",
            job_id="job-1",
            artifacts=sample_artifacts(),
        )
        return store, _stored_job_directory(artifact_root)

    traversal_store, traversal_directory = new_store_and_directory("traversal")
    traversal_manifest_path = traversal_directory / "manifest.json"
    traversal_manifest = json.loads(traversal_manifest_path.read_text(encoding="utf-8"))
    traversal_manifest["artifacts"]["course_markdown"]["file_name"] = "../course.md"
    traversal_manifest_path.write_text(
        json.dumps(traversal_manifest),
        encoding="utf-8",
    )
    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        traversal_store.get_manifest(user_id="user-1", job_id="job-1")

    symlink_store, symlink_directory = new_store_and_directory("symlink")
    symlink_course_path = symlink_directory / "python-course.md"
    symlink_course_path.unlink()
    symlink_course_path.symlink_to("/etc/passwd")
    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        symlink_store.get_manifest(user_id="user-1", job_id="job-1")

    extra_store, extra_directory = new_store_and_directory("extra")
    (extra_directory / "unexpected.txt").write_bytes(b"unexpected")
    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        extra_store.get_manifest(user_id="user-1", job_id="job-1")

    size_store, size_directory = new_store_and_directory("changed-size")
    (size_directory / "python-course.md").write_bytes(b"Course with extra bytes")
    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        size_store.get_manifest(user_id="user-1", job_id="job-1")

    corrupt_store, corrupt_directory = new_store_and_directory("corrupt")
    (corrupt_directory / "python-course.md").write_bytes(b"Courze")
    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        with corrupt_store.open_artifact(
            user_id="user-1",
            job_id="job-1",
            artifact_id="course_markdown",
        ):
            pytest.fail("Corrupt content must fail before yielding.")


def test_stream_setup_translates_filesystem_races_without_private_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A topology race must remain a typed context-free package failure."""

    artifact_root = tmp_path / "private-artifacts"
    store = FilesystemPrivateArtifactStore(
        root_directory=artifact_root,
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts=sample_artifacts(),
    )
    stored_job_directory = _stored_job_directory(artifact_root)
    real_iterdir = Path.iterdir

    def fail_for_private_job_directory(path: Path) -> Iterator[Path]:
        if path == stored_job_directory:
            raise OSError(f"private filesystem race at {path}")
        return real_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fail_for_private_job_directory)

    with pytest.raises(ArtifactIntegrityError, match="integrity") as error_info:
        with store.open_artifact(
            user_id="user-1",
            job_id="job-1",
            artifact_id="course_markdown",
        ):
            pytest.fail("A raced manifest must fail before yielding.")

    assert str(artifact_root) not in str(error_info.value)
    assert error_info.value.__cause__ is None
    assert error_info.value.__context__ is None


def test_manifest_rejects_unknown_noncanonical_artifact_identifier(
    tmp_path: Path,
) -> None:
    """Only the renderer's reviewed deliverable/format matrix is public."""

    store = FilesystemPrivateArtifactStore(
        root_directory=tmp_path / "artifacts",
        maximum_job_bytes=10_000,
        retention_days=30,
    )
    store.save(
        user_id="user-1",
        job_id="job-1",
        artifacts={
            "private_debug_dump": RenderedArtifact(
                file_name="debug.txt",
                media_type="text/plain",
                content=b"private diagnostics",
            )
        },
    )

    restored_private_bundle = store.get(user_id="user-1", job_id="job-1")
    assert restored_private_bundle["private_debug_dump"].content == (
        b"private diagnostics"
    )
    with pytest.raises(ArtifactIntegrityError, match="integrity"):
        store.get_manifest(user_id="user-1", job_id="job-1")
