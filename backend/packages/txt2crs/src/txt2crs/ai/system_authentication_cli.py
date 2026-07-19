# SPDX-License-Identifier: MIT-0

"""Temporary first-run bootstrap for the dedicated txt2crs system account.

This is not a wrapper around an installed Codex CLI. It invokes the package's
SDK-driven device-code service, which in turn launches the Codex app-server
binary already bundled as a Python dependency. The command can disappear once
the same challenge/status methods are wired into the finished FastAPI UI.
"""

import argparse
import os
import webbrowser
from collections.abc import Sequence
from pathlib import Path

from txt2crs.ai.system_authentication import (
    DedicatedSystemAuthenticator,
    SystemAuthenticationError,
    SystemAuthenticationState,
)


def _default_state_directory() -> Path:
    """Return a persistent app-owned directory without requiring configuration."""

    configured_directory = os.getenv("TXT2CRS_SYSTEM_STATE_DIRECTORY")
    if configured_directory:
        return Path(configured_directory).expanduser().resolve()
    return (Path.cwd() / ".txt2crs-system").resolve()


def _build_argument_parser() -> argparse.ArgumentParser:
    """Describe the intentionally small temporary operator interface."""

    argument_parser = argparse.ArgumentParser(
        description=(
            "Connect one dedicated ChatGPT subscription to txt2crs using "
            "the bundled Codex runtime."
        )
    )
    argument_parser.add_argument(
        "--state-directory",
        type=Path,
        default=_default_state_directory(),
        help=(
            "Persistent private application state. Defaults to "
            "./.txt2crs-system or TXT2CRS_SYSTEM_STATE_DIRECTORY."
        ),
    )
    argument_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the verification URL without opening the default browser.",
    )
    return argument_parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Authenticate the dedicated system identity and return a shell exit code."""

    parsed_arguments = _build_argument_parser().parse_args(arguments)
    state_directory = parsed_arguments.state_directory.expanduser().resolve()
    authenticator = DedicatedSystemAuthenticator.create(
        worker_directory=state_directory / "worker",
        codex_home=state_directory / "codex-home",
    )

    current_status = authenticator.current_status(refresh=True)
    if current_status.state is SystemAuthenticationState.authenticated:
        print(current_status.message)
        return 0

    try:
        challenge = authenticator.start_device_code_login()
    except SystemAuthenticationError as authentication_error:
        print(str(authentication_error))
        return 1

    if challenge.verification_url is None or challenge.user_code is None:
        print("ChatGPT authentication did not return a device-code challenge.")
        return 1

    print(f"Open: {challenge.verification_url}")
    print(f"Enter code: {challenge.user_code}")
    if not parsed_arguments.no_browser:
        webbrowser.open(challenge.verification_url, new=2)

    try:
        completed_status = authenticator.wait_for_current_attempt()
    except KeyboardInterrupt:
        authenticator.close()
        print("ChatGPT authentication was cancelled.")
        return 130

    print(completed_status.message)
    return 0 if completed_status.state is SystemAuthenticationState.authenticated else 1


if __name__ == "__main__":
    raise SystemExit(main())
