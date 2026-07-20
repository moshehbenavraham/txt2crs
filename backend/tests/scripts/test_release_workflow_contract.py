"""Static safety and identity contracts for release validation."""

import os
import re
from pathlib import Path

DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(
    os.getenv("TXT2CRS_REPOSITORY_ROOT", str(DEFAULT_REPOSITORY_ROOT))
)
RELEASE_WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "release.yml"


def _release_workflow_text() -> str:
    """Read the release workflow through the same narrow mounted contract."""

    return RELEASE_WORKFLOW.read_text(encoding="utf-8")


def test_release_workflow_uses_the_shared_identity_validator() -> None:
    """Hosted and local release checks may not maintain divergent version rules."""

    workflow_text = _release_workflow_text()

    assert "scripts/release_evidence.py validate-repository" in workflow_text
    assert "--expected-version" in workflow_text
    assert "--revision" in workflow_text
    assert "--mode" in workflow_text
    assert "--tag" in workflow_text
    assert "GITHUB_REF_TYPE" in workflow_text
    assert "GITHUB_REF_NAME" in workflow_text


def test_release_workflow_is_read_only_and_never_publishes_or_deploys() -> None:
    """The release job builds evidence but performs no external mutation."""

    workflow_text = _release_workflow_text()

    assert "permissions: {}" in workflow_text
    assert "contents: read" in workflow_text
    assert "pull_request_target:" not in workflow_text
    for forbidden_command in (
        "docker push",
        "gh release",
        "npm publish",
        "uv publish",
        "twine upload",
        "kubectl",
        "terraform apply",
    ):
        assert forbidden_command not in workflow_text


def test_release_workflow_pins_every_action_to_an_exact_commit() -> None:
    """Release builds execute only immutable third-party action revisions."""

    workflow_text = _release_workflow_text()
    action_references = re.findall(r"(?m)^\s*uses:\s*[^@\s]+@([^\s#]+)", workflow_text)

    assert action_references
    assert all(
        re.fullmatch(r"[0-9a-f]{40}", reference) for reference in action_references
    )


def test_release_workflow_builds_and_retains_only_reviewed_artifacts() -> None:
    """The final tag rebuilds both products and uploads bounded release outputs."""

    workflow_text = _release_workflow_text()

    assert "uv build --package txt2crs" in workflow_text
    assert 'docker build --tag "txt2crs-backend:${GITHUB_SHA}" backend' in workflow_text
    assert "txt2crs-frontend:${GITHUB_SHA}" in workflow_text
    assert "backend/dist/" in workflow_text
    assert "release/SHA256SUMS" in workflow_text
    assert "release/image-inspection.json" in workflow_text
    assert "retention-days: 14" in workflow_text
    assert "if-no-files-found: error" in workflow_text
