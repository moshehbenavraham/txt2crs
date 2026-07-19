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


def test_job_submission_routes_generate_strict_authenticated_contracts() -> None:
    """Both write routes expose one reviewed header and accepted projection."""

    openapi = json.loads(OPENAPI_DOCUMENT.read_text(encoding="utf-8"))
    json_submission = openapi["paths"]["/api/v1/jobs"]["post"]
    upload_submission = openapi["paths"]["/api/v1/jobs/upload"]["post"]

    for operation in (json_submission, upload_submission):
        assert operation["security"] == [{"OAuth2PasswordBearer": []}]
        idempotency_parameters = [
            parameter
            for parameter in operation["parameters"]
            if parameter["name"] == "Idempotency-Key"
        ]
        assert len(idempotency_parameters) == 1
        idempotency_parameter = idempotency_parameters[0]
        assert idempotency_parameter["in"] == "header"
        assert idempotency_parameter["required"] is True
        assert idempotency_parameter["schema"]["pattern"] == (
            "^[A-Za-z0-9._:-]{1,128}$"
        )
        accepted_schema = operation["responses"]["202"]["content"]["application/json"][
            "schema"
        ]
        assert accepted_schema == {"$ref": "#/components/schemas/JobAcceptedPublic"}

    assert json_submission["operationId"] == "jobs-submit_job"
    json_schema_ref = json_submission["requestBody"]["content"]["application/json"][
        "schema"
    ]["$ref"]
    assert json_schema_ref.endswith("/JobSubmissionRequest")

    multipart_content = upload_submission["requestBody"]["content"]
    assert set(multipart_content) == {"multipart/form-data"}
    upload_schema_ref = multipart_content["multipart/form-data"]["schema"]["$ref"]
    upload_schema_name = upload_schema_ref.rsplit("/", maxsplit=1)[-1]
    upload_properties = openapi["components"]["schemas"][upload_schema_name][
        "properties"
    ]
    assert upload_properties["metadata"]["type"] == "string"
    assert upload_properties["file"] == {
        "type": "string",
        # OpenAPI 3.1 represents binary request content with the JSON Schema
        # ``contentMediaType`` keyword. The generated TypeScript type is
        # consequently ``Blob | File`` rather than a plain string.
        "contentMediaType": "application/octet-stream",
        "title": "File",
        "description": "One bounded PDF, DOCX, or PPTX source.",
    }


def test_job_openapi_contains_discriminated_inputs_and_allowlisted_response() -> None:
    """Generated clients retain input discrimination and private-field absence."""

    openapi = json.loads(OPENAPI_DOCUMENT.read_text(encoding="utf-8"))
    schemas = openapi["components"]["schemas"]
    input_schema = schemas["JobSubmissionRequest"]["properties"]["input"]

    assert input_schema["discriminator"]["propertyName"] == "type"
    assert set(input_schema["discriminator"]["mapping"]) == {
        "prompt",
        "text",
        "url",
        "youtube",
    }
    assert set(schemas["JobAcceptedPublic"]["properties"]) == {
        "schema_version",
        "job_id",
        "status",
        "revision",
        "status_url",
    }
    assert "idempotency_key" not in schemas["JobAcceptedPublic"]["properties"]
