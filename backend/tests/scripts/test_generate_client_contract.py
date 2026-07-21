"""Static regression tests for deterministic OpenAPI client generation."""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

# The development container mounts only the public inputs required by these
# static checks. Host runs continue to discover the checkout from this file.
DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(
    os.getenv("TXT2CRS_REPOSITORY_ROOT", str(DEFAULT_REPOSITORY_ROOT))
)
GENERATE_CLIENT_SCRIPT = REPOSITORY_ROOT / "scripts" / "generate-client.sh"
VALIDATE_CHANGES_SCRIPT = REPOSITORY_ROOT / "scripts" / "validate-changes.sh"
OPENAPI_DOCUMENT = REPOSITORY_ROOT / "frontend" / "openapi.json"
OPENAPI_GENERATOR_CONFIG = REPOSITORY_ROOT / "frontend" / "openapi-ts.config.ts"
FRONTEND_PACKAGE_JSON = REPOSITORY_ROOT / "frontend" / "package.json"
ASCII_NORMALIZER_SCRIPT = (
    REPOSITORY_ROOT / "frontend" / "scripts" / "normalize-generated-client.mjs"
)
GENERATED_TYPES = REPOSITORY_ROOT / "frontend" / "src" / "client" / "types.gen.ts"
GENERATED_CLIENT_ROOT = REPOSITORY_ROOT / "frontend" / "src" / "client"


@lru_cache(maxsize=1)
def _read_current_openapi_contract() -> dict[str, Any]:
    """Return generated JSON when present, otherwise derive it from FastAPI.

    ``frontend/openapi.json`` is an intentionally ignored generator
    intermediate. Long-lived workspaces usually have it, but a clean checkout
    does not. Backend contract tests must remain reproducible without
    installing Node merely to recreate an equivalent server-owned document.
    The generated TypeScript files are still inspected separately below.
    """

    if OPENAPI_DOCUMENT.is_file():
        openapi_document = json.loads(OPENAPI_DOCUMENT.read_text(encoding="utf-8"))
    else:
        # Import lazily so fast source-shape tests that do not need OpenAPI can
        # still run under the narrow development-container contract.
        from app.main import app  # noqa: PLC0415

        openapi_document = app.openapi()
    if not isinstance(openapi_document, dict):
        raise AssertionError("The current OpenAPI contract must be a JSON object.")
    return openapi_document


def test_generate_client_formats_openapi_document_and_generated_client() -> None:
    """Generation must not leave a formatter failure behind the hook chain."""

    generation_script = GENERATE_CLIENT_SCRIPT.read_text(encoding="utf-8")
    package_scripts = json.loads(FRONTEND_PACKAGE_JSON.read_text(encoding="utf-8"))[
        "scripts"
    ]
    frontend_generation_command = package_scripts["generate-client:codegen"]

    assert os.access(GENERATE_CLIENT_SCRIPT, os.X_OK)
    assert package_scripts["generate-client"] == "../scripts/generate-client.sh"
    assert "BASH_SOURCE[0]" in generation_script
    assert 'cd -- "$REPOSITORY_ROOT"' in generation_script
    assert "npm --prefix frontend run generate-client:codegen" in generation_script
    assert "openapi.json src/client" in frontend_generation_command
    assert "biome check --write" in frontend_generation_command


def test_generate_client_replaces_openapi_document_atomically() -> None:
    """Concurrent contract readers must never observe a truncated JSON file."""

    generation_script = GENERATE_CLIENT_SCRIPT.read_text(encoding="utf-8")

    assert "mktemp" in generation_script
    assert (
        'mv -- "$TEMPORARY_OPENAPI_DOCUMENT" "$OPENAPI_DOCUMENT"' in generation_script
    )
    assert generation_script.index(
        'mv -- "$TEMPORARY_OPENAPI_DOCUMENT" "$OPENAPI_DOCUMENT"'
    ) < generation_script.index("npm --prefix frontend run generate-client:codegen")


def test_generate_client_normalizes_ascii_only_after_biome_parses_output() -> None:
    """A smart apostrophe cannot break the generator's single-quoted source."""

    package_scripts = json.loads(FRONTEND_PACKAGE_JSON.read_text(encoding="utf-8"))[
        "scripts"
    ]
    frontend_generation_command = package_scripts["generate-client:codegen"]
    generator_config = OPENAPI_GENERATOR_CONFIG.read_text(encoding="utf-8")
    ascii_normalizer = ASCII_NORMALIZER_SCRIPT.read_text(encoding="utf-8")

    assert "postProcess: []" in generator_config
    assert "node scripts/normalize-generated-client.mjs" in frontend_generation_command
    assert frontend_generation_command.index(
        "biome check --write"
    ) < frontend_generation_command.index("node scripts/normalize-generated-client.mjs")
    assert "replaceAll" in ascii_normalizer
    assert "\\u2019" in ascii_normalizer
    assert "writeFileSync" in ascii_normalizer


def test_generated_client_uses_repository_ascii_and_lf_conventions() -> None:
    """Upstream documentation copy cannot bypass repository text conventions."""

    generated_files = sorted(
        path for path in GENERATED_CLIENT_ROOT.rglob("*") if path.is_file()
    )

    assert generated_files
    for generated_file in generated_files:
        generated_bytes = generated_file.read_bytes()
        assert generated_bytes.isascii(), generated_file
        assert b"\r" not in generated_bytes, generated_file


def test_fast_validation_includes_repository_workflow_contracts() -> None:
    """CI configuration regressions belong in the credential-free fast gate."""

    validation_script = VALIDATE_CHANGES_SCRIPT.read_text(encoding="utf-8")

    assert "test_quality_workflow_contract.py" in validation_script
    assert "test_security_workflow_contract.py" in validation_script


def test_system_routes_generate_safe_authenticated_contracts() -> None:
    """The generated client exposes only the reviewed cache and challenge."""

    openapi = _read_current_openapi_contract()
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

    openapi = _read_current_openapi_contract()
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

    openapi = _read_current_openapi_contract()
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


def test_job_read_routes_generate_owner_scoped_bounded_contracts() -> None:
    """Status and manifest reads expose strict schemas under bearer auth."""

    openapi = _read_current_openapi_contract()
    status_operation = openapi["paths"]["/api/v1/jobs/{job_id}"]["get"]
    manifest_operation = openapi["paths"]["/api/v1/jobs/{job_id}/artifacts"]["get"]

    assert status_operation["operationId"] == "jobs-read_job"
    assert manifest_operation["operationId"] == "jobs-read_job_artifacts"
    for operation, response_schema_name in (
        (status_operation, "JobStatusPublic"),
        (manifest_operation, "ArtifactManifestPublic"),
    ):
        assert operation["security"] == [{"OAuth2PasswordBearer": []}]
        assert "requestBody" not in operation
        assert operation["responses"]["200"]["content"]["application/json"][
            "schema"
        ] == {"$ref": f"#/components/schemas/{response_schema_name}"}
        path_parameters = [
            parameter
            for parameter in operation["parameters"]
            if parameter["in"] == "path"
        ]
        assert len(path_parameters) == 1
        assert path_parameters[0]["name"] == "job_id"
        assert path_parameters[0]["required"] is True
        assert path_parameters[0]["schema"]["maxLength"] == 128
        assert path_parameters[0]["schema"]["pattern"] == (
            "^[A-Za-z0-9][A-Za-z0-9._:-]*$"
        )
        assert set(operation["responses"]) >= {"200", "401", "404", "422", "500"}

    status_properties = openapi["components"]["schemas"]["JobStatusPublic"][
        "properties"
    ]
    assert set(status_properties) == {
        "schema_version",
        "job_id",
        "status",
        "revision",
        "created_at",
        "updated_at",
        "runtime_activity_at",
        "progress",
        "input",
        "failure",
        "result",
        "artifacts",
    }
    research_properties = openapi["components"]["schemas"]["JobResearchPublic"][
        "properties"
    ]
    assert set(research_properties) == {
        "fetched_source_count",
        "charged_source_units",
        "accepted_source_count",
    }
    assert "etag" not in json.dumps(status_operation).casefold()


def test_artifact_download_generates_format_accurate_auth_contract() -> None:
    """Generated clients reflect text and binary artifacts without ETag."""

    openapi = _read_current_openapi_contract()
    operation = openapi["paths"]["/api/v1/jobs/{job_id}/artifacts/{artifact_id}"]["get"]

    assert operation["operationId"] == "jobs-download_job_artifact"
    assert operation["security"] == [{"OAuth2PasswordBearer": []}]
    assert "requestBody" not in operation
    assert set(operation["responses"]) >= {"200", "401", "404", "422", "500"}
    artifact_content = operation["responses"]["200"]["content"]
    assert artifact_content == {
        # The wildcard fallback gives code generators one honest union for an
        # endpoint whose runtime Content-Type varies by the selected artifact.
        "*/*": {
            "schema": {
                "oneOf": [
                    {"type": "string"},
                    {
                        "type": "string",
                        "contentMediaType": "application/octet-stream",
                    },
                ]
            }
        },
        "text/html": {"schema": {"type": "string"}},
        "text/markdown": {"schema": {"type": "string"}},
        "application/pdf": {
            "schema": {
                "type": "string",
                "contentMediaType": "application/pdf",
            }
        },
        ("application/vnd.openxmlformats-officedocument.wordprocessingml.document"): {
            "schema": {
                "type": "string",
                "contentMediaType": (
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            }
        },
    }
    generated_types = GENERATED_TYPES.read_text(encoding="utf-8")
    assert "200: string | Blob | File" in generated_types
    parameter_by_name = {
        parameter["name"]: parameter
        for parameter in operation["parameters"]
        if parameter["in"] == "path"
    }
    assert set(parameter_by_name) == {"job_id", "artifact_id"}
    for parameter in parameter_by_name.values():
        assert parameter["required"] is True
        assert parameter["schema"]["maxLength"] == 128
        assert parameter["schema"]["pattern"] == ("^[A-Za-z0-9][A-Za-z0-9._:-]*$")
    assert "etag" not in json.dumps(operation).casefold()


def test_generated_contract_contains_no_retired_donor_item_surface() -> None:
    """Source removal must flow through OpenAPI and every generated client file."""

    openapi = _read_current_openapi_contract()
    assert all(not path.startswith("/api/v1/items") for path in openapi["paths"])
    assert {
        "ItemCreate",
        "ItemPublic",
        "ItemUpdate",
        "ItemsPublic",
    }.isdisjoint(openapi["components"]["schemas"])

    generated_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(GENERATED_CLIENT_ROOT.rglob("*"))
        if path.is_file()
    )
    for retired_identifier in (
        '"/api/v1/items/',
        "ItemsService",
        "ApiV1Items",
        "ItemCreate",
        "ItemPublic",
        "ItemUpdate",
        "ItemsPublic",
    ):
        assert retired_identifier not in generated_source


def test_account_delete_contract_documents_retryable_partial_failures() -> None:
    """Both erasure routes must expose their new 500/503 outcomes to clients."""

    openapi = _read_current_openapi_contract()
    for route_path in (
        "/api/v1/users/me",
        "/api/v1/users/{user_id}",
    ):
        responses = openapi["paths"][route_path]["delete"]["responses"]
        assert responses["500"] == {
            "description": (
                "Engine erasure may already be complete; retrying account "
                "deletion is safe."
            ),
            "content": {"application/problem+json": {}},
        }
        assert responses["503"] == {
            "description": (
                "Account deletion is temporarily unavailable. Please retry."
            ),
            "content": {"application/problem+json": {}},
        }
