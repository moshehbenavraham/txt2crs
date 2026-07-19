"""Tests for local, machine-readable error capture.

The Apex phase-transition audit uses this small file-backed capture helper to
leave the most recent development error in a format another agent can inspect.
These tests deliberately use a temporary directory so normal test runs never
write diagnostic artifacts into the repository.
"""

import json
from pathlib import Path

from app.core.logging import write_last_error


def test_write_last_error_creates_private_structured_capture(
    tmp_path: Path,
) -> None:
    """A captured exception keeps the documented JSON shape and permissions."""

    try:
        raise RuntimeError("deliberate audit validation error")
    except RuntimeError as captured_error:
        capture_path = write_last_error(
            captured_error,
            context={"operation": "audit-observability-validation"},
            logs_directory=tmp_path,
        )

    capture_payload = json.loads(capture_path.read_text(encoding="utf-8"))

    assert capture_path.parent == tmp_path
    assert capture_path.name.startswith("last_error_")
    assert capture_path.suffix == ".json"
    assert capture_path.stat().st_mode & 0o777 == 0o600
    assert set(capture_payload) == {
        "timestamp",
        "level",
        "msg",
        "error",
        "context",
    }
    assert capture_payload["level"] == "error"
    assert capture_payload["msg"] == "deliberate audit validation error"
    assert capture_payload["error"]["type"] == "RuntimeError"
    assert capture_payload["error"]["message"] == capture_payload["msg"]
    assert (
        "RuntimeError: deliberate audit validation error"
        in (capture_payload["error"]["stack"])
    )
    assert capture_payload["context"] == {"operation": "audit-observability-validation"}


def test_write_last_error_creates_owner_only_logs_directory(
    tmp_path: Path,
) -> None:
    """A missing diagnostic directory is created without group/world access."""

    logs_directory = tmp_path / "logs"

    write_last_error(ValueError("capture me"), logs_directory=logs_directory)

    assert logs_directory.is_dir()
    assert logs_directory.stat().st_mode & 0o777 == 0o700
