"""Fast static regressions for the backend image and Compose topology."""

import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DOCKERFILE = REPOSITORY_ROOT / "backend" / "Dockerfile"
COMPOSE_FILE = REPOSITORY_ROOT / "docker-compose.yml"
COMPOSE_OVERRIDE_FILE = REPOSITORY_ROOT / "docker-compose.override.yml"
ROOT_ENVIRONMENT_EXAMPLE = REPOSITORY_ROOT / ".env.example"

# Hosted deployment is explicitly outside the project scope. Keeping these
# donor files would silently turn an optional future product decision into an
# active operational dependency, so their absence is part of the local-first
# container contract.
OUT_OF_SCOPE_HOSTED_DEPLOYMENT_FILES = (
    REPOSITORY_ROOT / ".github" / "workflows" / "deploy-coolify.yml",
    REPOSITORY_ROOT / ".github" / "workflows" / "deploy-staging.yml",
    REPOSITORY_ROOT / ".github" / "workflows" / "deploy-production.yml",
    REPOSITORY_ROOT / ".github" / "workflows" / "backup-db.yml",
    REPOSITORY_ROOT / "scripts" / "coolify-deploy.sh",
)


def _read_repository_file(path: Path) -> str:
    """Read one deployment file with an explicit, deterministic encoding."""
    return path.read_text(encoding="utf-8")


def _docker_stage(dockerfile_text: str, stage_name: str) -> str:
    """Return one named Docker stage so assertions cannot pass in another stage."""
    stage_header = f"FROM base AS {stage_name}"
    stage_start = dockerfile_text.index(stage_header)
    next_stage = dockerfile_text.find("\nFROM ", stage_start + len(stage_header))
    if next_stage == -1:
        return dockerfile_text[stage_start:]
    return dockerfile_text[stage_start:next_stage]


def _compose_service(compose_text: str, service_name: str) -> str:
    """Return one top-level Compose service block using its two-space indent."""
    service_match = re.search(
        rf"(?ms)^  {re.escape(service_name)}:\n"
        rf"(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|^[A-Za-z0-9_-]+:\n|\Z)",
        compose_text,
    )
    if service_match is None:
        raise AssertionError(f"Compose service {service_name!r} was not found.")
    return service_match.group(0)


def test_workspace_packages_are_copied_before_first_uv_sync() -> None:
    dockerfile_text = _read_repository_file(BACKEND_DOCKERFILE)

    package_copy_position = dockerfile_text.index("COPY ./packages /app/packages")
    first_sync_position = dockerfile_text.index("uv sync")

    assert package_copy_position < first_sync_position


def test_both_backend_targets_run_one_non_root_process() -> None:
    dockerfile_text = _read_repository_file(BACKEND_DOCKERFILE)

    for stage_name in ("production", "development"):
        stage_text = _docker_stage(dockerfile_text, stage_name)
        assert "USER appuser" in stage_text
        assert re.search(r'CMD \["fastapi", "run", "app/main.py"\]', stage_text)
        assert "--workers" not in stage_text


def test_both_targets_create_owner_only_private_runtime_directories() -> None:
    dockerfile_text = _read_repository_file(BACKEND_DOCKERFILE)

    for stage_name in ("production", "development"):
        stage_text = _docker_stage(dockerfile_text, stage_name)
        assert stage_text.count("useradd --uid 1001") == 1
        assert stage_text.count("groupadd --gid 1001") == 1
        assert stage_text.count("install -d -m 0700") == 1
        assert "/var/lib/txt2crs" in stage_text
        assert "/tmp/txt2crs-worker" in stage_text


def test_compose_passes_engine_paths_to_backend_and_prestart() -> None:
    compose_text = _read_repository_file(COMPOSE_FILE)
    required_environment_names = {
        "TXT2CRS_STATE_ROOT",
        "TXT2CRS_JOB_DB_PATH",
        "TXT2CRS_ARTIFACT_ROOT",
        "TXT2CRS_CODEX_HOME",
        "TXT2CRS_WORKER_ROOT",
    }

    for service_name in ("prestart", "backend"):
        service_text = _compose_service(compose_text, service_name)
        for environment_name in required_environment_names:
            assert environment_name in service_text


def test_compose_uses_database_container_port_for_internal_clients() -> None:
    """Host port mappings must never leak into service-to-service traffic."""

    compose_text = _read_repository_file(COMPOSE_FILE)

    for service_name in ("prestart", "backend"):
        service_text = _compose_service(compose_text, service_name)
        assert "- POSTGRES_SERVER=db" in service_text
        assert "- POSTGRES_PORT=5432" in service_text
        assert "- POSTGRES_PORT=${POSTGRES_PORT}" not in service_text


def test_compose_mounts_one_private_state_volume_separate_from_postgres() -> None:
    compose_text = _read_repository_file(COMPOSE_FILE)
    backend_service = _compose_service(compose_text, "backend")
    database_service = _compose_service(compose_text, "db")

    # The image creates this exact mount point as UID/GID 1001. Allowing
    # Compose to move a fresh named volume to an arbitrary path would make the
    # new directory root-owned and prevent the non-root application from
    # writing its state.
    assert "txt2crs-state:/var/lib/txt2crs" in backend_service
    assert "${TXT2CRS_STATE_ROOT" not in backend_service
    assert "app-db-data:/var/lib/postgresql/data/pgdata" in database_service
    assert re.search(r"(?m)^  txt2crs-state:\s*$", compose_text)
    assert "txt2crs-state" not in database_service
    assert "app-db-data" not in backend_service


def test_research_mcp_port_is_not_published() -> None:
    compose_text = _read_repository_file(COMPOSE_FILE)
    compose_override_text = _read_repository_file(COMPOSE_OVERRIDE_FILE)

    assert "8765:" not in compose_text
    assert "8765:" not in compose_override_text


def test_development_override_keeps_a_single_reload_process() -> None:
    compose_override_text = _read_repository_file(COMPOSE_OVERRIDE_FILE)
    backend_service = _compose_service(compose_override_text, "backend")

    assert "--reload" in backend_service
    assert "--workers" not in backend_service


def test_project_scope_contains_no_active_hosted_deployment_automation() -> None:
    """Local Docker is the only deployment target in the current project scope."""

    unexpected_files = [
        str(path.relative_to(REPOSITORY_ROOT))
        for path in OUT_OF_SCOPE_HOSTED_DEPLOYMENT_FILES
        if path.exists()
    ]

    assert unexpected_files == []


def test_local_environment_example_has_no_coolify_configuration() -> None:
    """The default operator surface must not advertise an out-of-scope host."""

    environment_example_text = _read_repository_file(ROOT_ENVIRONMENT_EXAMPLE)

    assert "COOLIFY" not in environment_example_text.upper()
    assert "APP_UUID" not in environment_example_text
