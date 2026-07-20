#!/usr/bin/env python3
"""Command-line entry point for txt2crs release evidence validation.

The validation implementation lives in ``release_contract.py`` so the trust
boundary and its tests remain a cohesive module below the repository's module
size ceiling. Executing this file directly adds its directory to Python's
import path, so the sibling import needs no application installation.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from release_contract import (
    ReleaseEvidenceError,
    _validate_mode_and_tag,
    canonicalize_release_evidence,
    validate_repository_versions,
    write_canonical_release_evidence,
)

# Re-export the programmatic functions because backend contract tests load this
# exact executable module. Local callers therefore exercise the same boundary
# as the hosted workflow instead of importing a private second implementation.
__all__ = [
    "ReleaseEvidenceError",
    "canonicalize_release_evidence",
    "main",
    "validate_repository_versions",
    "write_canonical_release_evidence",
]


def _build_argument_parser() -> argparse.ArgumentParser:
    """Create the finite command surface shared by local and hosted gates."""

    argument_parser = argparse.ArgumentParser(
        description="Validate txt2crs release identity and public evidence.",
    )
    subcommands = argument_parser.add_subparsers(dest="command", required=True)

    repository_parser = subcommands.add_parser(
        "validate-repository",
        help="Validate version surfaces and candidate/final identity.",
    )
    repository_parser.add_argument("--repository-root", type=Path, required=True)
    repository_parser.add_argument("--expected-version", required=True)
    repository_parser.add_argument(
        "--mode",
        choices=("candidate", "final"),
        required=True,
    )
    repository_parser.add_argument("--revision", required=True)
    repository_parser.add_argument("--tag")

    evidence_parser = subcommands.add_parser(
        "validate-evidence",
        help="Validate and optionally rewrite canonical public evidence.",
    )
    evidence_parser.add_argument("--input", type=Path, required=True)
    evidence_parser.add_argument("--output", type=Path)
    evidence_parser.add_argument(
        "--mode",
        choices=("candidate", "final"),
        required=True,
    )
    evidence_parser.add_argument("--revision", required=True)
    evidence_parser.add_argument("--tag")
    return argument_parser


def _require_json_object(value: object) -> Mapping[str, Any]:
    """Reject a top-level non-object before invoking the strict contract."""

    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ReleaseEvidenceError("release evidence must be an object.")
    return value


def _run_cli(arguments: argparse.Namespace) -> None:
    """Execute one validated CLI operation with explicit failure propagation."""

    if arguments.command == "validate-repository":
        version = validate_repository_versions(
            arguments.repository_root.resolve(),
            expected_version=arguments.expected_version,
        )
        _validate_mode_and_tag(
            version=version,
            mode=arguments.mode,
            revision=arguments.revision,
            tag=arguments.tag,
        )
        sys.stdout.write(f"release-version={version}\n")
        return

    input_document = json.loads(arguments.input.read_text(encoding="utf-8"))
    canonical_content = canonicalize_release_evidence(
        _require_json_object(input_document),
        expected_mode=arguments.mode,
        expected_revision=arguments.revision,
        expected_tag=arguments.tag,
    )
    if arguments.output is not None:
        write_canonical_release_evidence(arguments.output, canonical_content)
    sys.stdout.write("release-evidence=valid\n")


def main(raw_arguments: Sequence[str] | None = None) -> int:
    """Return a stable process status without leaking file or provider details."""

    parsed_arguments = _build_argument_parser().parse_args(raw_arguments)
    try:
        _run_cli(parsed_arguments)
    except (
        ReleaseEvidenceError,
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        tomllib.TOMLDecodeError,
    ) as error:
        if isinstance(error, ReleaseEvidenceError):
            safe_message = str(error)
        else:
            safe_message = "A release input could not be read or parsed safely."
        sys.stderr.write(f"release evidence rejected: {safe_message}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
