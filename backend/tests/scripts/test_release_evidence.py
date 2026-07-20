"""Tests for deterministic, public-safe release candidate evidence."""

import importlib.util
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType

import pytest

DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
RELEASE_EVIDENCE_SCRIPT = DEFAULT_REPOSITORY_ROOT / "scripts" / "release_evidence.py"
DELIVERABLES = ("course", "review_pack", "assessment", "answer_key")
FORMATS = ("html", "markdown", "pdf", "docx")


def _load_release_evidence_module() -> ModuleType:
    """Load the repository script without turning ``scripts`` into a package."""

    module_specification = importlib.util.spec_from_file_location(
        "release_evidence",
        RELEASE_EVIDENCE_SCRIPT,
    )
    if module_specification is None or module_specification.loader is None:
        raise AssertionError("The release evidence module could not be loaded.")
    release_evidence_module = importlib.util.module_from_spec(module_specification)
    script_directory = str(RELEASE_EVIDENCE_SCRIPT.parent)
    sys.path.insert(0, script_directory)
    try:
        module_specification.loader.exec_module(release_evidence_module)
    finally:
        sys.path.remove(script_directory)
    return release_evidence_module


@pytest.fixture
def release_evidence_module() -> ModuleType:
    """Return the release module after its tests have defined the contract."""

    return _load_release_evidence_module()


@pytest.fixture
def synchronized_repository(tmp_path: Path) -> Path:
    """Create the smallest repository tree containing every version surface."""

    (tmp_path / "backend" / "packages" / "txt2crs").mkdir(parents=True)
    (tmp_path / "docs").mkdir()
    (tmp_path / "VERSION").write_text("1.0.0\n", encoding="ascii")
    (tmp_path / "backend" / "packages" / "txt2crs" / "pyproject.toml").write_text(
        '[project]\nname = "txt2crs"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "backend" / "uv.lock").write_text(
        'version = 1\n\n[[package]]\nname = "txt2crs"\nversion = "1.0.0"\n',
        encoding="utf-8",
    )
    (tmp_path / "docs" / "VERSIONING.md").write_text(
        "The current repository and Python package release is `1.0.0`.\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "CHANGELOG.md").write_text(
        "## [1.0.0] - 2026-07-20\n",
        encoding="utf-8",
    )
    return tmp_path


def _artifact_entries() -> Iterator[dict[str, object]]:
    """Yield one completely reviewed public record per deliverable and format."""

    for deliverable_index, deliverable in enumerate(DELIVERABLES):
        for format_index, artifact_format in enumerate(FORMATS):
            unique_hash_value = format(
                1 + (deliverable_index * len(FORMATS)) + format_index,
                "064x",
            )
            yield {
                "deliverable": deliverable,
                "format": artifact_format,
                "sha256": unique_hash_value,
                "bytes": 1_000 + deliverable_index * 100 + format_index,
                "inspection": {
                    "alignment": "pass",
                    "citations": "pass",
                    "formatting": "pass",
                    "integrity": "pass",
                    "private_access": "pass",
                    "answer_separation": "pass",
                },
            }


def valid_candidate_document() -> dict[str, object]:
    """Return a complete synthetic candidate evidence document."""

    return {
        "schema_version": "1.0",
        "release": {
            "version": "1.0.0",
            "revision": "a" * 40,
            "mode": "candidate",
            "tag": None,
        },
        "distributions": {
            "txt2crs-1.0.0-py3-none-any.whl": "b" * 64,
            "txt2crs-1.0.0.tar.gz": "c" * 64,
        },
        "images": {
            "backend": "d" * 64,
            "frontend": "e" * 64,
        },
        "evaluation": {
            "case_count": 13,
            "passed_count": 13,
            "private_case_data_included": False,
        },
        "live_proof": {
            "model_family": "gpt-5.6",
            "research_used": True,
            "artifact_count": 16,
            "duration_seconds": 120,
        },
        "artifacts": list(_artifact_entries()),
        "known_exceptions": ["remote_codeql_billing"],
    }


def test_synchronized_repository_version_surfaces_pass(
    release_evidence_module: ModuleType,
    synchronized_repository: Path,
) -> None:
    """Every declared release surface must identify the stable candidate."""

    observed_version = release_evidence_module.validate_repository_versions(
        synchronized_repository,
        expected_version="1.0.0",
    )

    assert observed_version == "1.0.0"


@pytest.mark.parametrize(
    ("relative_path", "old_text", "new_text"),
    [
        ("VERSION", "1.0.0", "1.0.1"),
        (
            "backend/packages/txt2crs/pyproject.toml",
            'version = "1.0.0"',
            'version = "0.7.0"',
        ),
        (
            "backend/uv.lock",
            'version = "1.0.0"',
            'version = "0.7.0"',
        ),
        ("docs/VERSIONING.md", "`1.0.0`", "`0.7.0`"),
        ("docs/CHANGELOG.md", "[1.0.0]", "[0.7.0]"),
    ],
)
def test_any_version_surface_drift_fails_closed(
    release_evidence_module: ModuleType,
    synchronized_repository: Path,
    relative_path: str,
    old_text: str,
    new_text: str,
) -> None:
    """No release surface may silently disagree with the requested version."""

    drifted_path = synchronized_repository / relative_path
    drifted_path.write_text(
        drifted_path.read_text(encoding="utf-8").replace(old_text, new_text),
        encoding="utf-8",
    )

    with pytest.raises(release_evidence_module.ReleaseEvidenceError):
        release_evidence_module.validate_repository_versions(
            synchronized_repository,
            expected_version="1.0.0",
        )


def test_candidate_evidence_is_canonical_and_byte_stable(
    release_evidence_module: ModuleType,
) -> None:
    """Equivalent evidence must serialize identically for repeatable hashing."""

    candidate_document = valid_candidate_document()

    first_serialization = release_evidence_module.canonicalize_release_evidence(
        candidate_document,
        expected_mode="candidate",
        expected_revision="a" * 40,
    )
    reordered_document = dict(reversed(list(candidate_document.items())))
    second_serialization = release_evidence_module.canonicalize_release_evidence(
        reordered_document,
        expected_mode="candidate",
        expected_revision="a" * 40,
    )

    assert first_serialization == second_serialization
    assert first_serialization.endswith(b"\n")
    assert json.loads(first_serialization) == candidate_document


def test_candidate_rejects_a_tag_and_final_requires_the_exact_tag(
    release_evidence_module: ModuleType,
) -> None:
    """A candidate is untagged; final mode accepts only ``v<version>``."""

    candidate_document = valid_candidate_document()
    tagged_candidate = json.loads(json.dumps(candidate_document))
    tagged_candidate["release"]["tag"] = "v1.0.0"
    with pytest.raises(release_evidence_module.ReleaseEvidenceError):
        release_evidence_module.canonicalize_release_evidence(
            tagged_candidate,
            expected_mode="candidate",
            expected_revision="a" * 40,
        )

    final_document = json.loads(json.dumps(candidate_document))
    final_document["release"]["mode"] = "final"
    final_document["release"]["tag"] = "v1.0.0"
    release_evidence_module.canonicalize_release_evidence(
        final_document,
        expected_mode="final",
        expected_revision="a" * 40,
        expected_tag="v1.0.0",
    )

    final_document["release"]["tag"] = "v0.7.0"
    with pytest.raises(release_evidence_module.ReleaseEvidenceError):
        release_evidence_module.canonicalize_release_evidence(
            final_document,
            expected_mode="final",
            expected_revision="a" * 40,
            expected_tag="v1.0.0",
        )


def test_evidence_requires_exactly_four_deliverables_by_four_formats(
    release_evidence_module: ModuleType,
) -> None:
    """Missing, duplicate, or unexpected artifact pairs invalidate the proof."""

    incomplete_document = valid_candidate_document()
    incomplete_document["artifacts"] = incomplete_document["artifacts"][:-1]
    with pytest.raises(release_evidence_module.ReleaseEvidenceError):
        release_evidence_module.canonicalize_release_evidence(
            incomplete_document,
            expected_mode="candidate",
            expected_revision="a" * 40,
        )

    duplicate_document = valid_candidate_document()
    duplicate_document["artifacts"][-1] = duplicate_document["artifacts"][0]
    with pytest.raises(release_evidence_module.ReleaseEvidenceError):
        release_evidence_module.canonicalize_release_evidence(
            duplicate_document,
            expected_mode="candidate",
            expected_revision="a" * 40,
        )


@pytest.mark.parametrize(
    ("mutation_key", "mutation_value"),
    [
        ("credential", "example-secret-value"),
        ("email", "learner@example.com"),
        ("prompt", "private course input"),
        ("provider_payload", {"raw": "private"}),
        ("token_count", 1234),
        ("filesystem_path", "/home/operator/private-artifact.pdf"),
        ("artifact_body", "complete private publication"),
        ("private_url", "https://private.example/artifact"),
    ],
)
def test_evidence_rejects_private_or_provider_fields_at_any_depth(
    release_evidence_module: ModuleType,
    mutation_key: str,
    mutation_value: object,
) -> None:
    """Public evidence uses an allowlist instead of attempting best-effort scrub."""

    unsafe_document = valid_candidate_document()
    unsafe_document["live_proof"][mutation_key] = mutation_value

    with pytest.raises(release_evidence_module.ReleaseEvidenceError):
        release_evidence_module.canonicalize_release_evidence(
            unsafe_document,
            expected_mode="candidate",
            expected_revision="a" * 40,
        )


@pytest.mark.parametrize(
    "field_mutation",
    [
        ("artifacts", 0, "sha256", "not-a-hash"),
        ("artifacts", 0, "bytes", 0),
        ("artifacts", 0, "inspection", {"alignment": "pass"}),
        ("live_proof", None, "duration_seconds", -1),
        ("evaluation", None, "passed_count", 14),
    ],
)
def test_evidence_rejects_malformed_hashes_bounds_and_incomplete_reviews(
    release_evidence_module: ModuleType,
    field_mutation: tuple[str, int | None, str, object],
) -> None:
    """The ledger must be complete and finite before it can be public."""

    section_name, list_index, field_name, field_value = field_mutation
    malformed_document = valid_candidate_document()
    section = malformed_document[section_name]
    if list_index is None:
        section[field_name] = field_value
    else:
        section[list_index][field_name] = field_value

    with pytest.raises(release_evidence_module.ReleaseEvidenceError):
        release_evidence_module.canonicalize_release_evidence(
            malformed_document,
            expected_mode="candidate",
            expected_revision="a" * 40,
        )
