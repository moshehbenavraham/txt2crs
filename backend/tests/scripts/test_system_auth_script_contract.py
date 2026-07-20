"""Contracts for the short repository-level ChatGPT authentication helper."""

import os
import stat
import subprocess
from pathlib import Path

DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(
    os.getenv("TXT2CRS_REPOSITORY_ROOT", str(DEFAULT_REPOSITORY_ROOT))
)
AUTHENTICATION_SCRIPT = REPOSITORY_ROOT / "scripts" / "auth-codex.sh"
LIVE_ACCEPTANCE_GUIDE = (
    REPOSITORY_ROOT
    / "backend"
    / "packages"
    / "txt2crs"
    / "tests"
    / "acceptance"
    / "README_acceptance.md"
)


def test_authentication_script_is_directly_executable() -> None:
    """The advertised short command must work without an explicit shell."""

    assert AUTHENTICATION_SCRIPT.is_file()
    assert AUTHENTICATION_SCRIPT.stat().st_mode & stat.S_IXUSR


def test_authentication_script_invokes_the_packaged_cli_from_any_directory(
    tmp_path: Path,
) -> None:
    """The helper must preserve the reviewed package and private state boundary."""

    fake_binary_directory = tmp_path / "bin"
    fake_binary_directory.mkdir()
    captured_working_directory = tmp_path / "working-directory.txt"
    captured_arguments = tmp_path / "arguments.bin"
    fake_uv_binary = fake_binary_directory / "uv"
    fake_uv_binary.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s' "$PWD" >"$TXT2CRS_TEST_CAPTURE_WORKING_DIRECTORY"
printf '%s\\0' "$@" >"$TXT2CRS_TEST_CAPTURE_ARGUMENTS"
""",
        encoding="utf-8",
    )
    fake_uv_binary.chmod(0o700)

    test_environment = dict(os.environ)
    test_environment["PATH"] = (
        f"{fake_binary_directory}{os.pathsep}{test_environment['PATH']}"
    )
    test_environment["TXT2CRS_TEST_CAPTURE_WORKING_DIRECTORY"] = str(
        captured_working_directory
    )
    test_environment["TXT2CRS_TEST_CAPTURE_ARGUMENTS"] = str(captured_arguments)

    subprocess.run(
        [AUTHENTICATION_SCRIPT, "--no-browser"],
        cwd=tmp_path,
        env=test_environment,
        check=True,
        capture_output=True,
        text=True,
    )

    assert captured_working_directory.read_text(encoding="utf-8") == str(
        REPOSITORY_ROOT / "backend"
    )
    assert captured_arguments.read_bytes().split(b"\0")[:-1] == [
        b"run",
        b"--package",
        b"txt2crs",
        b"txt2crs-system-auth",
        b"--state-directory",
        os.fsencode(REPOSITORY_ROOT / ".txt2crs-system"),
        b"--no-browser",
    ]


def test_live_acceptance_guide_uses_the_short_authentication_helper() -> None:
    """Operators should not need to reconstruct the packaged uv command."""

    guide_text = LIVE_ACCEPTANCE_GUIDE.read_text(encoding="utf-8")

    assert "./scripts/auth-codex.sh" in guide_text
    assert "TXT2CRS_MODEL_ID" in guide_text
    assert "TXT2CRS_LIVE_MODEL" not in guide_text
