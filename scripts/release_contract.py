"""Validate synchronized release identity and bounded public evidence.

This script deliberately uses only Python's standard library. A release check
must still run in a clean checkout before the application dependencies are
installed, and it must not import the engine or application merely to inspect
repository metadata.

The script validates evidence that a caller already assembled from
authoritative test, build, and owner-scoped application outputs. It never
opens an engine database, reads provider credentials, calls the network, or
renders an artifact. Those boundaries keep release reporting independent from
the product logic it is proving.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import tomllib
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, NoReturn

SEMANTIC_VERSION_PATTERN = re.compile(
    r"^(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-(?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?:[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
GIT_REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SAFE_RELEASE_FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
EMAIL_LIKE_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@"
    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
)
WINDOWS_ABSOLUTE_PATH_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")

EXPECTED_DELIVERABLES = frozenset({"course", "review_pack", "assessment", "answer_key"})
EXPECTED_FORMATS = frozenset({"html", "markdown", "pdf", "docx"})
EXPECTED_INSPECTION_FIELDS = frozenset(
    {
        "alignment",
        "citations",
        "formatting",
        "integrity",
        "private_access",
        "answer_separation",
    }
)
EXPECTED_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "release",
        "distributions",
        "images",
        "evaluation",
        "live_proof",
        "artifacts",
        "known_exceptions",
    }
)
EXPECTED_RELEASE_FIELDS = frozenset({"version", "revision", "mode", "tag"})
EXPECTED_EVALUATION_FIELDS = frozenset(
    {"case_count", "passed_count", "private_case_data_included"}
)
EXPECTED_LIVE_PROOF_FIELDS = frozenset(
    {"model_family", "research_used", "artifact_count", "duration_seconds"}
)
EXPECTED_ARTIFACT_FIELDS = frozenset(
    {"deliverable", "format", "sha256", "bytes", "inspection"}
)
ALLOWED_KNOWN_EXCEPTIONS = frozenset({"remote_codeql_billing"})
MAXIMUM_ARTIFACT_BYTES = 100 * 1024 * 1024
MAXIMUM_LIVE_DURATION_SECONDS = 24 * 60 * 60

ReleaseMode = Literal["candidate", "final"]


class ReleaseEvidenceError(ValueError):
    """A release surface or public evidence document violated its contract."""


def _fail(message: str) -> NoReturn:
    """Raise the one public-safe validation exception used by the script."""

    raise ReleaseEvidenceError(message)


def _require_mapping(value: object, field_name: str) -> Mapping[str, Any]:
    """Return a JSON object or reject the field with a bounded message."""

    if not isinstance(value, Mapping):
        _fail(f"{field_name} must be an object.")
    if not all(isinstance(key, str) for key in value):
        _fail(f"{field_name} contains a non-string field name.")
    return value


def _require_exact_fields(
    value: Mapping[str, Any],
    *,
    expected_fields: frozenset[str],
    field_name: str,
) -> None:
    """Reject missing and extra fields instead of attempting best-effort scrub."""

    observed_fields = frozenset(value)
    if observed_fields != expected_fields:
        _fail(f"{field_name} fields do not match the public contract.")


def _require_string(value: object, field_name: str) -> str:
    """Return a bounded string and reject blank or multiline content."""

    if not isinstance(value, str) or not value or len(value) > 255:
        _fail(f"{field_name} must be a nonempty bounded string.")
    if any(character in value for character in ("\n", "\r", "\x00")):
        _fail(f"{field_name} contains a forbidden control character.")
    return value


def _require_integer(
    value: object,
    field_name: str,
    *,
    minimum: int,
    maximum: int,
) -> int:
    """Validate integer bounds without accepting booleans as numbers."""

    if isinstance(value, bool) or not isinstance(value, int):
        _fail(f"{field_name} must be an integer.")
    if not minimum <= value <= maximum:
        _fail(f"{field_name} is outside its allowed range.")
    return value


def _require_boolean(value: object, field_name: str) -> bool:
    """Validate a real JSON boolean rather than a truthy substitute."""

    if not isinstance(value, bool):
        _fail(f"{field_name} must be a boolean.")
    return value


def _require_sha256(value: object, field_name: str) -> str:
    """Return one lowercase hexadecimal SHA-256 value."""

    digest = _require_string(value, field_name)
    if SHA256_PATTERN.fullmatch(digest) is None:
        _fail(f"{field_name} must be a lowercase SHA-256 value.")
    return digest


def _normalize_semantic_version_for_python(semantic_version: str) -> str:
    """Translate the documented SemVer prerelease spelling to PEP 440."""

    replacements = {
        "-dev.": ".dev",
        "-alpha.": "a",
        "-beta.": "b",
        "-rc.": "rc",
    }
    normalized_version = semantic_version
    for semantic_marker, python_marker in replacements.items():
        normalized_version = normalized_version.replace(
            semantic_marker,
            python_marker,
        )
    return normalized_version


def _read_toml(path: Path) -> Mapping[str, Any]:
    """Read one trusted repository TOML document."""

    with path.open("rb") as toml_stream:
        parsed_document = tomllib.load(toml_stream)
    return _require_mapping(parsed_document, "TOML document")


def validate_repository_versions(
    repository_root: Path,
    *,
    expected_version: str,
) -> str:
    """Require every declared release surface to identify one exact version."""

    if SEMANTIC_VERSION_PATTERN.fullmatch(expected_version) is None:
        _fail("The expected release version is not valid Semantic Versioning.")

    repository_version = (
        repository_root.joinpath("VERSION").read_text(encoding="ascii").strip()
    )
    if repository_version != expected_version:
        _fail("The repository VERSION does not match the expected release.")

    package_document = _read_toml(
        repository_root / "backend" / "packages" / "txt2crs" / "pyproject.toml"
    )
    project_table = _require_mapping(package_document.get("project"), "project")
    package_version = _require_string(project_table.get("version"), "project.version")
    expected_python_version = _normalize_semantic_version_for_python(expected_version)
    if package_version != expected_python_version:
        _fail("The txt2crs package version does not match the release.")

    lock_document = _read_toml(repository_root / "backend" / "uv.lock")
    lock_packages = lock_document.get("package")
    if not isinstance(lock_packages, Sequence) or isinstance(
        lock_packages,
        (str, bytes, bytearray),
    ):
        _fail("The uv lockfile does not contain package records.")
    txt2crs_lock_versions = [
        package_record.get("version")
        for package_record in lock_packages
        if isinstance(package_record, Mapping)
        and package_record.get("name") == "txt2crs"
    ]
    if txt2crs_lock_versions != [expected_python_version]:
        _fail("The uv lockfile txt2crs version does not match the release.")

    versioning_text = repository_root.joinpath("docs", "VERSIONING.md").read_text(
        encoding="utf-8"
    )
    expected_stage_sentence = (
        f"current repository and Python package release is `{expected_version}`"
    )
    if expected_stage_sentence not in versioning_text:
        _fail("The versioning guide does not identify the current release.")

    changelog_text = repository_root.joinpath("docs", "CHANGELOG.md").read_text(
        encoding="utf-8"
    )
    changelog_heading_pattern = re.compile(
        rf"(?m)^## \[{re.escape(expected_version)}\] - [0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}$"
    )
    if changelog_heading_pattern.search(changelog_text) is None:
        _fail("The changelog does not contain the dated release heading.")

    return repository_version


def _validate_release_identity(
    release_value: object,
    *,
    expected_mode: ReleaseMode,
    expected_revision: str,
    expected_tag: str | None,
) -> str:
    """Validate version, revision, and candidate/final tag invariants."""

    release = _require_mapping(release_value, "release")
    _require_exact_fields(
        release,
        expected_fields=EXPECTED_RELEASE_FIELDS,
        field_name="release",
    )
    version = _require_string(release.get("version"), "release.version")
    if SEMANTIC_VERSION_PATTERN.fullmatch(version) is None:
        _fail("release.version is not valid Semantic Versioning.")

    revision = _require_string(release.get("revision"), "release.revision")
    if GIT_REVISION_PATTERN.fullmatch(revision) is None:
        _fail("release.revision must be a lowercase 40-character Git SHA.")
    if revision != expected_revision:
        _fail("release.revision does not match the tested revision.")

    observed_mode = release.get("mode")
    if observed_mode != expected_mode:
        _fail("release.mode does not match the requested validation mode.")
    observed_tag = release.get("tag")
    if expected_mode == "candidate":
        if observed_tag is not None or expected_tag is not None:
            _fail("A release candidate must not have a final tag.")
    else:
        exact_tag = f"v{version}"
        if (
            not isinstance(observed_tag, str)
            or observed_tag != exact_tag
            or expected_tag != exact_tag
        ):
            _fail("The final release tag must exactly match v<version>.")
    return version


def _validate_distribution_hashes(
    distribution_value: object,
    *,
    version: str,
) -> None:
    """Require only the expected wheel and source distribution checksums."""

    distributions = _require_mapping(distribution_value, "distributions")
    expected_filenames = {
        f"txt2crs-{version}-py3-none-any.whl",
        f"txt2crs-{version}.tar.gz",
    }
    if set(distributions) != expected_filenames:
        _fail("distributions must contain the exact wheel and source archive.")
    for filename, digest in distributions.items():
        if SAFE_RELEASE_FILENAME_PATTERN.fullmatch(filename) is None:
            _fail("A distribution filename is unsafe.")
        _require_sha256(digest, f"distributions.{filename}")


def _validate_image_hashes(image_value: object) -> None:
    """Require reviewed backend and frontend image content identifiers."""

    images = _require_mapping(image_value, "images")
    _require_exact_fields(
        images,
        expected_fields=frozenset({"backend", "frontend"}),
        field_name="images",
    )
    _require_sha256(images.get("backend"), "images.backend")
    _require_sha256(images.get("frontend"), "images.frontend")


def _validate_evaluation(evaluation_value: object) -> None:
    """Validate aggregate-only fixed-corpus results."""

    evaluation = _require_mapping(evaluation_value, "evaluation")
    _require_exact_fields(
        evaluation,
        expected_fields=EXPECTED_EVALUATION_FIELDS,
        field_name="evaluation",
    )
    case_count = _require_integer(
        evaluation.get("case_count"),
        "evaluation.case_count",
        minimum=1,
        maximum=10_000,
    )
    passed_count = _require_integer(
        evaluation.get("passed_count"),
        "evaluation.passed_count",
        minimum=0,
        maximum=case_count,
    )
    if passed_count != case_count:
        _fail("The fixed evaluation corpus must pass completely.")
    if _require_boolean(
        evaluation.get("private_case_data_included"),
        "evaluation.private_case_data_included",
    ):
        _fail("Public evidence may not include private evaluation case data.")


def _validate_live_proof(live_proof_value: object) -> None:
    """Validate the bounded facts allowed from the representative live job."""

    live_proof = _require_mapping(live_proof_value, "live_proof")
    _require_exact_fields(
        live_proof,
        expected_fields=EXPECTED_LIVE_PROOF_FIELDS,
        field_name="live_proof",
    )
    if (
        _require_string(
            live_proof.get("model_family"),
            "live_proof.model_family",
        )
        != "gpt-5.6"
    ):
        _fail("The live proof must identify the reviewed GPT-5.6 family.")
    if not _require_boolean(
        live_proof.get("research_used"),
        "live_proof.research_used",
    ):
        _fail("The live proof must confirm research use.")
    if (
        _require_integer(
            live_proof.get("artifact_count"),
            "live_proof.artifact_count",
            minimum=0,
            maximum=16,
        )
        != 16
    ):
        _fail("The live proof must contain exactly sixteen artifacts.")
    _require_integer(
        live_proof.get("duration_seconds"),
        "live_proof.duration_seconds",
        minimum=0,
        maximum=MAXIMUM_LIVE_DURATION_SECONDS,
    )


def _validate_artifacts(artifact_value: object) -> None:
    """Require one fully reviewed record for every deliverable/format pair."""

    if not isinstance(artifact_value, list):
        _fail("artifacts must be a JSON array.")
    if len(artifact_value) != len(EXPECTED_DELIVERABLES) * len(EXPECTED_FORMATS):
        _fail("artifacts must contain exactly sixteen entries.")

    observed_pairs: set[tuple[str, str]] = set()
    for artifact_index, raw_artifact in enumerate(artifact_value):
        artifact = _require_mapping(raw_artifact, f"artifacts[{artifact_index}]")
        _require_exact_fields(
            artifact,
            expected_fields=EXPECTED_ARTIFACT_FIELDS,
            field_name=f"artifacts[{artifact_index}]",
        )
        deliverable = _require_string(
            artifact.get("deliverable"),
            f"artifacts[{artifact_index}].deliverable",
        )
        artifact_format = _require_string(
            artifact.get("format"),
            f"artifacts[{artifact_index}].format",
        )
        artifact_pair = (deliverable, artifact_format)
        if (
            deliverable not in EXPECTED_DELIVERABLES
            or artifact_format not in EXPECTED_FORMATS
            or artifact_pair in observed_pairs
        ):
            _fail("Artifact deliverable/format pairs are incomplete or duplicated.")
        observed_pairs.add(artifact_pair)
        _require_sha256(
            artifact.get("sha256"),
            f"artifacts[{artifact_index}].sha256",
        )
        _require_integer(
            artifact.get("bytes"),
            f"artifacts[{artifact_index}].bytes",
            minimum=1,
            maximum=MAXIMUM_ARTIFACT_BYTES,
        )
        inspection = _require_mapping(
            artifact.get("inspection"),
            f"artifacts[{artifact_index}].inspection",
        )
        _require_exact_fields(
            inspection,
            expected_fields=EXPECTED_INSPECTION_FIELDS,
            field_name=f"artifacts[{artifact_index}].inspection",
        )
        if any(result != "pass" for result in inspection.values()):
            _fail("Every artifact inspection dimension must pass.")

    expected_pairs = {
        (deliverable, artifact_format)
        for deliverable in EXPECTED_DELIVERABLES
        for artifact_format in EXPECTED_FORMATS
    }
    if observed_pairs != expected_pairs:
        _fail("Artifact deliverable/format coverage is incomplete.")


def _validate_known_exceptions(exception_value: object) -> None:
    """Allow only reviewed finite external exceptions in public evidence."""

    if not isinstance(exception_value, list):
        _fail("known_exceptions must be a JSON array.")
    if (
        any(not isinstance(item, str) for item in exception_value)
        or len(exception_value) != len(set(exception_value))
        or not set(exception_value).issubset(ALLOWED_KNOWN_EXCEPTIONS)
    ):
        _fail("known_exceptions contains an unreviewed value.")


def _reject_private_string_values(value: object) -> None:
    """Reject common private value shapes even inside otherwise allowed fields."""

    if isinstance(value, str):
        if (
            EMAIL_LIKE_PATTERN.search(value) is not None
            or value.startswith("/")
            or WINDOWS_ABSOLUTE_PATH_PATTERN.match(value) is not None
            or "://" in value
        ):
            _fail("Public release evidence contains a private value shape.")
        return
    if isinstance(value, Mapping):
        for nested_value in value.values():
            _reject_private_string_values(nested_value)
        return
    if isinstance(value, list):
        for nested_value in value:
            _reject_private_string_values(nested_value)


def canonicalize_release_evidence(
    evidence_document: Mapping[str, Any],
    *,
    expected_mode: ReleaseMode,
    expected_revision: str,
    expected_tag: str | None = None,
) -> bytes:
    """Validate and deterministically serialize one public evidence document."""

    if GIT_REVISION_PATTERN.fullmatch(expected_revision) is None:
        _fail("The expected revision must be a lowercase 40-character Git SHA.")
    evidence = _require_mapping(evidence_document, "release evidence")
    _require_exact_fields(
        evidence,
        expected_fields=EXPECTED_TOP_LEVEL_FIELDS,
        field_name="release evidence",
    )
    if evidence.get("schema_version") != "1.0":
        _fail("schema_version must equal 1.0.")

    version = _validate_release_identity(
        evidence.get("release"),
        expected_mode=expected_mode,
        expected_revision=expected_revision,
        expected_tag=expected_tag,
    )
    _validate_distribution_hashes(evidence.get("distributions"), version=version)
    _validate_image_hashes(evidence.get("images"))
    _validate_evaluation(evidence.get("evaluation"))
    _validate_live_proof(evidence.get("live_proof"))
    _validate_artifacts(evidence.get("artifacts"))
    _validate_known_exceptions(evidence.get("known_exceptions"))
    _reject_private_string_values(evidence)

    try:
        serialized_evidence = json.dumps(
            evidence,
            ensure_ascii=True,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as error:
        raise ReleaseEvidenceError(
            "Release evidence is not finite JSON data."
        ) from error
    return f"{serialized_evidence}\n".encode("ascii")


def write_canonical_release_evidence(output_path: Path, content: bytes) -> None:
    """Atomically replace one caller-selected public evidence file."""

    output_parent = output_path.parent
    if not output_parent.is_dir() or output_path.is_symlink():
        _fail("The release evidence output boundary is unsafe.")

    temporary_file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(temporary_file_descriptor, "wb") as temporary_stream:
            temporary_stream.write(content)
            temporary_stream.flush()
            os.fsync(temporary_stream.fileno())
        temporary_path.chmod(0o644)
        os.replace(temporary_path, output_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _validate_mode_and_tag(
    *,
    version: str,
    mode: ReleaseMode,
    revision: str,
    tag: str | None,
) -> None:
    """Apply identity rules for repository-only workflow validation."""

    if GIT_REVISION_PATTERN.fullmatch(revision) is None:
        _fail("The workflow revision must be a lowercase 40-character Git SHA.")
    if mode == "candidate":
        if tag is not None:
            _fail("Candidate workflow validation must not receive a tag.")
        return
    if tag != f"v{version}":
        _fail("The final workflow tag must exactly match v<version>.")
