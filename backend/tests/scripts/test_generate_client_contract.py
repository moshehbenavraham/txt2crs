"""Static regression tests for deterministic OpenAPI client generation."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
GENERATE_CLIENT_SCRIPT = REPOSITORY_ROOT / "scripts" / "generate-client.sh"
VALIDATE_CHANGES_SCRIPT = REPOSITORY_ROOT / "scripts" / "validate-changes.sh"


def test_generate_client_formats_openapi_document_and_generated_client() -> None:
    """Generation must not leave a formatter failure behind the hook chain."""

    generation_script = GENERATE_CLIENT_SCRIPT.read_text(encoding="utf-8")

    assert "openapi.json src/client" in generation_script
    assert "biome check --write" in generation_script


def test_fast_validation_includes_repository_workflow_contracts() -> None:
    """CI configuration regressions belong in the credential-free fast gate."""

    validation_script = VALIDATE_CHANGES_SCRIPT.read_text(encoding="utf-8")

    assert "test_quality_workflow_contract.py" in validation_script
    assert "test_security_workflow_contract.py" in validation_script
