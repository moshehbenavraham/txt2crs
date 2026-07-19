#!/usr/bin/env python3
"""Create, validate, and restore the private txt2crs engine-state archive.

The local deployment keeps job metadata, generated artifacts, and Codex
credentials in one Docker volume.  This helper deliberately accepts only
directories and regular files so a symbolic link cannot make a backup escape
that private volume or make a restore write outside its destination.
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import tarfile
import tempfile
from collections.abc import Sequence
from pathlib import Path, PurePosixPath


def _require_real_directory(directory_path: Path, purpose: str) -> None:
    """Reject missing directories and links before reading or replacing data."""

    if directory_path.is_symlink():
        raise ValueError(f"{purpose} must not be a symbolic link: {directory_path}")
    if not directory_path.is_dir():
        raise ValueError(f"{purpose} must be an existing directory: {directory_path}")


def _validate_source_entry(entry_path: Path) -> None:
    """Allow only real directories and files inside a backup source."""

    entry_mode = entry_path.lstat().st_mode
    if stat.S_ISLNK(entry_mode):
        raise ValueError(f"Backup source contains a symbolic link: {entry_path}")
    if not (stat.S_ISDIR(entry_mode) or stat.S_ISREG(entry_mode)):
        raise ValueError(
            f"Backup source contains an unsupported special file: {entry_path}"
        )


def _normalized_member_path(member_name: str) -> PurePosixPath:
    """Return a safe relative archive path or fail before extraction."""

    member_path = PurePosixPath(member_name)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise ValueError(f"Archive member has an unsafe path: {member_name}")

    # Tar writers commonly represent the archive root as ".".  Remove no-op
    # segments so duplicate spellings such as "./jobs.sqlite3" are compared
    # consistently during validation.
    normalized_parts = tuple(
        path_part for path_part in member_path.parts if path_part not in ("", ".")
    )
    return PurePosixPath(*normalized_parts) if normalized_parts else PurePosixPath(".")


def _validated_archive_members(
    archive: tarfile.TarFile,
) -> list[tuple[tarfile.TarInfo, PurePosixPath]]:
    """Validate every member before a restore is allowed to clear old state."""

    validated_members: list[tuple[tarfile.TarInfo, PurePosixPath]] = []
    seen_paths: set[PurePosixPath] = set()

    for archive_member in archive.getmembers():
        normalized_path = _normalized_member_path(archive_member.name)
        if normalized_path in seen_paths:
            raise ValueError(
                f"Archive contains a duplicate path: {archive_member.name}"
            )
        if not (archive_member.isdir() or archive_member.isreg()):
            raise ValueError(
                "Archive contains an unsupported link or special file: "
                f"{archive_member.name}"
            )

        seen_paths.add(normalized_path)
        validated_members.append((archive_member, normalized_path))

    if not validated_members:
        raise ValueError("Engine-state archive is empty.")
    return validated_members


def create_state_archive(source_directory: Path, archive_path: Path) -> None:
    """Create an owner-only gzip tar archive from a private state directory."""

    source_directory = source_directory.absolute()
    archive_path = archive_path.absolute()
    _require_real_directory(source_directory, "Backup source")
    if archive_path.is_symlink():
        raise ValueError(
            f"Archive destination must not be a symbolic link: {archive_path}"
        )

    archive_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{archive_path.name}.",
        suffix=".tmp",
        dir=archive_path.parent,
    )
    os.close(temporary_file_descriptor)
    temporary_archive_path = Path(temporary_name)

    try:
        # Add one entry at a time after lstat validation.  recursive=False is
        # important: tarfile must never independently follow an unchecked path.
        with tarfile.open(temporary_archive_path, mode="w:gz") as archive:
            _validate_source_entry(source_directory)
            archive.add(source_directory, arcname=".", recursive=False)
            for source_entry in sorted(
                source_directory.rglob("*"),
                key=lambda path: path.relative_to(source_directory).as_posix(),
            ):
                _validate_source_entry(source_entry)
                relative_name = source_entry.relative_to(source_directory).as_posix()
                archive.add(source_entry, arcname=relative_name, recursive=False)

        os.chmod(temporary_archive_path, 0o600)
        validate_state_archive(temporary_archive_path)
        temporary_archive_path.replace(archive_path)
    finally:
        temporary_archive_path.unlink(missing_ok=True)


def validate_state_archive(archive_path: Path) -> None:
    """Read and validate an archive without changing current engine state."""

    archive_path = archive_path.absolute()
    if archive_path.is_symlink() or not archive_path.is_file():
        raise ValueError(f"Engine-state archive must be a regular file: {archive_path}")

    try:
        with tarfile.open(archive_path, mode="r:gz") as archive:
            _validated_archive_members(archive)
    except tarfile.TarError as archive_error:
        raise ValueError(
            f"Engine-state archive is invalid: {archive_path}"
        ) from archive_error


def _remove_existing_destination_children(destination_directory: Path) -> None:
    """Clear only children after the complete incoming archive is validated."""

    for current_child in destination_directory.iterdir():
        if current_child.is_symlink() or current_child.is_file():
            current_child.unlink()
        elif current_child.is_dir():
            shutil.rmtree(current_child)
        else:
            raise ValueError(
                f"Restore destination contains an unsupported entry: {current_child}"
            )


def _restore_recorded_ownership(
    destination_directory: Path,
    validated_members: list[tuple[tarfile.TarInfo, PurePosixPath]],
) -> None:
    """Restore numeric ownership when the maintenance container runs as root."""

    if not hasattr(os, "geteuid") or os.geteuid() != 0:
        return

    # Children come first so the archive root's ownership is applied last.
    for archive_member, normalized_path in reversed(validated_members):
        restored_path = (
            destination_directory
            if normalized_path == PurePosixPath(".")
            else destination_directory.joinpath(*normalized_path.parts)
        )
        os.chown(restored_path, archive_member.uid, archive_member.gid)


def restore_state_archive(archive_path: Path, destination_directory: Path) -> None:
    """Replace destination contents only after validating every archive member."""

    archive_path = archive_path.absolute()
    destination_directory = destination_directory.absolute()
    _require_real_directory(destination_directory, "Restore destination")

    # The first open performs complete validation.  Nothing below this point
    # runs for traversal paths, links, device files, or corrupt archives.
    with tarfile.open(archive_path, mode="r:gz") as archive:
        validated_members = _validated_archive_members(archive)

    _remove_existing_destination_children(destination_directory)

    with tarfile.open(archive_path, mode="r:gz") as archive:
        # Python's data filter adds a second standard-library safety layer.
        archive.extractall(path=destination_directory, filter="data")

    _restore_recorded_ownership(destination_directory, validated_members)


def _build_argument_parser() -> argparse.ArgumentParser:
    """Build the small maintenance CLI used from Docker-backed shell scripts."""

    argument_parser = argparse.ArgumentParser(
        description="Safely archive or restore txt2crs engine state."
    )
    subcommands = argument_parser.add_subparsers(dest="command", required=True)

    create_parser = subcommands.add_parser("create", help="Create a state archive.")
    create_parser.add_argument("source_directory", type=Path)
    create_parser.add_argument("archive_path", type=Path)

    validate_parser = subcommands.add_parser(
        "validate", help="Validate a state archive."
    )
    validate_parser.add_argument("archive_path", type=Path)

    restore_parser = subcommands.add_parser(
        "restore", help="Replace state from a validated archive."
    )
    restore_parser.add_argument("archive_path", type=Path)
    restore_parser.add_argument("destination_directory", type=Path)
    return argument_parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the requested archive operation and return a shell-friendly status."""

    parsed_arguments = _build_argument_parser().parse_args(arguments)
    try:
        if parsed_arguments.command == "create":
            create_state_archive(
                parsed_arguments.source_directory,
                parsed_arguments.archive_path,
            )
        elif parsed_arguments.command == "validate":
            validate_state_archive(parsed_arguments.archive_path)
        else:
            restore_state_archive(
                parsed_arguments.archive_path,
                parsed_arguments.destination_directory,
            )
    except (OSError, ValueError, tarfile.TarError) as maintenance_error:
        sys.stderr.write(f"local-state archive error: {maintenance_error}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
