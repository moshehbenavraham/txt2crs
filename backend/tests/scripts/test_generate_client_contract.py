"""Static regression tests for deterministic OpenAPI client generation."""

import json
import os
from pathlib import Path

# The development container mounts only the public inputs required by these
# static checks. Host runs continue to discover the checkout from this file.
DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(
    os.getenv("TXT2CRS_REPOSITORY_ROOT", str(DEFAULT_REPOSITORY_ROOT))
)
GENERATE_CLIENT_SCRIPT = REPOSITORY_ROOT / "scripts" / "generate-client.sh"
VALIDATE_CHANGES_SCRIPT = REPOSITORY_ROOT / "scripts" / "validate-changes.sh"
OPENAPI_DOCUMENT = REPOSITORY_ROOT / "frontend" / "openapi.json"


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


def test_system_routes_generate_safe_authenticated_contracts() -> None:
    """The generated client exposes only the reviewed cache and challenge."""

    openapi = json.loads(OPENAPI_DOCUMENT.read_text(encoding="utf-8"))
    readiness = openapi["paths"]["/api/v1/system/readiness"]["get"]
    auth_start = openapi["paths"]["/api/v1/system/auth/start"]["post"]
    auth_status = openapi["paths"]["/api/v1/system/auth/status"]["get"]

    assert readiness["security"] == [{"OAuth2PasswordBearer": []}]
    assert auth_start["security"] == [{"OAuth2PasswordBearer": []}]
    assert auth_status["security"] == [{"OAuth2PasswordBearer": []}]
    assert "requestBody" not in auth_start
    auth_properties = openapi["components"]["schemas"]["SystemAuthenticationPublic"][
        "properties"
    ]
    assert set(auth_properties) == {
        "state",
        "verification_url",
        "user_code",
        "message",
    }
