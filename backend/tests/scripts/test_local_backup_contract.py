"""Backup/restore contracts for PostgreSQL plus private engine state."""

import importlib.util
import io
import os
import tarfile
from pathlib import Path
from types import ModuleType

import pytest

# Repository-level scripts are mounted read-only at /workspace for tests that
# run inside the development backend container. Host runs discover the same
# checkout relative to this file.
DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(
    os.getenv("TXT2CRS_REPOSITORY_ROOT", str(DEFAULT_REPOSITORY_ROOT))
)
BACKUP_SCRIPT = REPOSITORY_ROOT / "scripts" / "backup-local-state.sh"
RESTORE_SCRIPT = REPOSITORY_ROOT / "scripts" / "restore-local-state.sh"
ARCHIVE_HELPER = REPOSITORY_ROOT / "scripts" / "local_state_archive.py"
ROOT_GITIGNORE = REPOSITORY_ROOT / ".gitignore"


def _load_archive_helper() -> ModuleType:
    """Load the repository helper without making scripts an application package."""

    module_spec = importlib.util.spec_from_file_location(
        "local_state_archive",
        ARCHIVE_HELPER,
    )
    if module_spec is None or module_spec.loader is None:
        raise AssertionError("Could not load local-state archive helper.")

    archive_helper = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(archive_helper)
    return archive_helper


def test_archive_helper_round_trips_regular_owner_state(tmp_path: Path) -> None:
    """Restore replaces stale state while preserving nested bytes and modes."""

    archive_helper = _load_archive_helper()
    source_directory = tmp_path / "source"
    nested_directory = source_directory / "artifacts" / "job-1"
    nested_directory.mkdir(parents=True)
    nested_directory.chmod(0o700)
    artifact_file = nested_directory / "course.zip"
    artifact_file.write_bytes(b"course archive bytes")
    artifact_file.chmod(0o600)
    (source_directory / "jobs.sqlite3").write_bytes(b"sqlite fixture")

    archive_path = tmp_path / "engine-state.tar.gz"
    archive_helper.create_state_archive(source_directory, archive_path)
    archive_helper.validate_state_archive(archive_path)

    restore_directory = tmp_path / "restored"
    restore_directory.mkdir()
    (restore_directory / "stale.txt").write_text("remove me", encoding="utf-8")

    archive_helper.restore_state_archive(archive_path, restore_directory)

    assert not (restore_directory / "stale.txt").exists()
    restored_artifact = restore_directory / "artifacts" / "job-1" / "course.zip"
    assert restored_artifact.read_bytes() == b"course archive bytes"
    assert restored_artifact.stat().st_mode & 0o777 == 0o600
    assert (restore_directory / "jobs.sqlite3").read_bytes() == b"sqlite fixture"


def test_archive_helper_rejects_symlinked_source_state(tmp_path: Path) -> None:
    """A backup must not follow a link out of the private state boundary."""

    archive_helper = _load_archive_helper()
    source_directory = tmp_path / "source"
    source_directory.mkdir()
    outside_file = tmp_path / "outside-secret"
    outside_file.write_text("must not be archived", encoding="utf-8")
    (source_directory / "escaped").symlink_to(outside_file)

    with pytest.raises(ValueError, match="symbolic link"):
        archive_helper.create_state_archive(
            source_directory,
            tmp_path / "engine-state.tar.gz",
        )


def test_archive_helper_validates_before_replacing_destination(tmp_path: Path) -> None:
    """A traversal member fails closed without deleting current engine state."""

    archive_helper = _load_archive_helper()
    malicious_archive = tmp_path / "malicious.tar.gz"
    malicious_payload = b"escape"
    malicious_member = tarfile.TarInfo(name="../escaped.txt")
    malicious_member.size = len(malicious_payload)
    with tarfile.open(malicious_archive, mode="w:gz") as archive:
        archive.addfile(malicious_member, io.BytesIO(malicious_payload))

    restore_directory = tmp_path / "restore"
    restore_directory.mkdir()
    current_state = restore_directory / "jobs.sqlite3"
    current_state.write_bytes(b"current-state")

    with pytest.raises(ValueError, match="unsafe path"):
        archive_helper.restore_state_archive(malicious_archive, restore_directory)

    assert current_state.read_bytes() == b"current-state"
    assert not (tmp_path / "escaped.txt").exists()


def test_backup_script_covers_both_persistent_stores_and_integrity() -> None:
    """One maintenance backup must quiesce and capture both data boundaries."""

    backup_script_text = BACKUP_SCRIPT.read_text(encoding="utf-8")

    assert "docker compose" in backup_script_text
    assert "stop backend" in backup_script_text
    assert 'Destination "/var/lib/txt2crs"' in backup_script_text
    assert "pg_dump" in backup_script_text
    assert "--format=custom" in backup_script_text
    assert "local_state_archive.py" in backup_script_text
    assert "create" in backup_script_text
    assert "validate" in backup_script_text
    assert "sha256sum" in backup_script_text
    # The archive container runs as root to read owner-only credentials.  It
    # must return the resulting 0600 file to the invoking host user before the
    # host-side checksum and later off-host copy can read it.
    assert "id -u" in backup_script_text
    assert "id -g" in backup_script_text
    assert "chown" in backup_script_text
    assert "BACKUP_RETENTION_DAYS" in backup_script_text
    assert "umask 077" in backup_script_text


def test_restore_script_fails_closed_before_destructive_replacement() -> None:
    """Checksums and archive validation must precede database or volume clearing."""

    restore_script_text = RESTORE_SCRIPT.read_text(encoding="utf-8")

    confirmation_position = restore_script_text.index("TXT2CRS_RESTORE_CONFIRM")
    checksum_position = restore_script_text.index("sha256sum --check")
    archive_validation_position = restore_script_text.index("local_state_archive.py")
    database_replacement_position = restore_script_text.index("dropdb")
    state_replacement_position = restore_script_text.index(" restore ")

    assert confirmation_position < checksum_position
    assert checksum_position < database_replacement_position
    assert archive_validation_position < database_replacement_position
    assert archive_validation_position < state_replacement_position
    assert "stop backend" in restore_script_text
    assert "pg_restore" in restore_script_text
    assert 'Destination "/var/lib/txt2crs"' in restore_script_text


def test_default_backup_directory_is_never_committed() -> None:
    """Backups contain credentials and learner data, so Git must ignore them."""

    gitignore_text = ROOT_GITIGNORE.read_text(encoding="utf-8")

    assert "/backups/" in gitignore_text
