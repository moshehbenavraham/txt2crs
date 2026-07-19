"""Static safety contracts for the repository security workflow."""

import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SECURITY_WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "security.yml"
GITLEAKS_IGNORE_FILE = REPOSITORY_ROOT / ".gitleaksignore"


def test_security_workflow_covers_the_mixed_stack_without_write_defaults() -> None:
    """The security bundle scans source, history, and both dependency trees."""

    workflow_text = SECURITY_WORKFLOW.read_text(encoding="utf-8")

    assert "permissions: {}" in workflow_text
    assert "pull_request_target:" not in workflow_text
    assert "secret-scan:" in workflow_text
    assert "codeql:" in workflow_text
    assert "dependency-review:" in workflow_text
    assert "dependency-audit:" in workflow_text
    assert 'language: ["python", "javascript-typescript"]' in workflow_text
    assert "pip-audit --progress-spinner=off" in workflow_text
    assert "npm audit --audit-level=high" in workflow_text


def test_security_workflow_pins_every_third_party_action_to_a_commit() -> None:
    """Immutable action references prevent tag replacement attacks."""

    workflow_text = SECURITY_WORKFLOW.read_text(encoding="utf-8")
    action_references = re.findall(r"(?m)^\s*uses:\s*[^@\s]+@([^\s#]+)", workflow_text)

    assert action_references
    assert all(
        re.fullmatch(r"[0-9a-f]{40}", reference) for reference in action_references
    )


def test_gitleaks_exceptions_are_fingerprint_scoped_and_explained() -> None:
    """Known synthetic fixtures may not turn into broad path/rule exclusions."""

    ignore_file_lines = GITLEAKS_IGNORE_FILE.read_text(encoding="utf-8").splitlines()
    reason_comments = [line for line in ignore_file_lines if line.startswith("#")]
    fingerprints = [
        line for line in ignore_file_lines if line and not line.startswith("#")
    ]

    assert len(reason_comments) >= 2
    assert len(fingerprints) == 4
    for fingerprint in fingerprints:
        commit_sha, path, rule_id, line_number = fingerprint.split(":")
        assert re.fullmatch(r"[0-9a-f]{40}", commit_sha)
        assert path.startswith("backend/")
        assert rule_id in {"generic-api-key", "jwt"}
        assert line_number.isdigit()
