"""Regression tests for the judge-facing local startup command.

The startup script is intentionally tested with a fake Docker executable. This
keeps the suite credential-free and prevents a unit test from changing the
developer's real containers, images, networks, or volumes.
"""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(
    os.getenv("TXT2CRS_REPOSITORY_ROOT", str(DEFAULT_REPOSITORY_ROOT))
)
START_LOCAL_SCRIPT = REPOSITORY_ROOT / "scripts" / "start-local.sh"
LEGACY_DEPLOY_SCRIPT = REPOSITORY_ROOT / "scripts" / "deploy-local-clean.sh"
ROOT_ENVIRONMENT_EXAMPLE = REPOSITORY_ROOT / ".env.example"
BACKEND_ENVIRONMENT_EXAMPLE = REPOSITORY_ROOT / "backend" / ".env.example"
FRONTEND_ENVIRONMENT_EXAMPLE = REPOSITORY_ROOT / "frontend" / ".env.example"

VALID_ENVIRONMENT = """\
DOCKER_IMAGE_BACKEND=txt2crs-backend
DOCKER_IMAGE_FRONTEND=txt2crs-frontend
TAG=latest
DOMAIN=localhost
STACK_NAME=txt2crs
TRAEFIK_HTTP_PORT=86
TRAEFIK_HTTPS_PORT=8443
TRAEFIK_DASHBOARD_PORT=8102
POSTGRES_PORT=5450
BACKEND_PORT=8016
FRONTEND_PORT=5195
ADMINER_PORT=8103
MAILCATCHER_SMTP_PORT=1029
MAILCATCHER_WEB_PORT=1084
JAEGER_UI_PORT=16689
OTLP_GRPC_PORT=4324
OTLP_HTTP_PORT=4325
PLAYWRIGHT_REPORT_PORT=9327
FRONTEND_HOST=http://localhost:5195
ENVIRONMENT=local
PROJECT_NAME=txt2crs
TXT2CRS_MODEL_ID=gpt-5.6-sol
TXT2CRS_RESEARCH_ENABLED=true
TAVILY_API_KEY=test-tavily-key
SECRET_KEY=0123456789abcdef0123456789abcdef
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=test-superuser-password
POSTGRES_DB=app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=test-database-password
"""

FAKE_DOCKER_SCRIPT = """\
#!/usr/bin/env bash
set -eu

printf '%s\\n' "$*" >> "$FAKE_DOCKER_LOG"

case " $* " in
    *" compose version "*)
        printf '%s\\n' "Docker Compose version v2.test"
        ;;
    *" info "*)
        ;;
    *" config --quiet "*)
        if [ "${FAKE_DOCKER_MODE:-success}" = "config-failure" ]; then
            printf '%s\\n' "fake compose configuration failure" >&2
            exit 1
        fi
        ;;
    *" config "*)
        if [ "${FAKE_DOCKER_MODE:-success}" = "port-conflict" ] ||
            [ "${FAKE_DOCKER_MODE:-success}" = "own-port" ]; then
            cat <<'EOF'
services:
  frontend:
    ports:
      - mode: ingress
        target: 80
        published: "5195"
EOF
        fi
        ;;
    *" ps -q "*)
        if [ "${FAKE_DOCKER_MODE:-success}" = "own-port" ]; then
            printf '%s\\n' "current-full-container-id"
        fi
        ;;
    *" ps --no-trunc --format "*)
        if [ "${FAKE_DOCKER_MODE:-success}" = "port-conflict" ]; then
            printf '%s\\n' \
                "other-id|another-project-frontend-1|0.0.0.0:5195->80/tcp"
        elif [ "${FAKE_DOCKER_MODE:-success}" = "own-port" ]; then
            printf '%s\\n' \
                "current-full-container-id|txt2crs-frontend-1|0.0.0.0:5195->80/tcp"
        fi
        ;;
    *" up "*)
        if [ "${FAKE_DOCKER_MODE:-success}" = "up-failure" ]; then
            printf '%s\\n' "fake compose startup failure" >&2
            exit 1
        fi
        printf '%s\\n' "fake stack started"
        ;;
    *" ps --all "*)
        printf '%s\\n' "frontend running healthy"
        printf '%s\\n' "backend running healthy"
        printf '%s\\n' "db running healthy"
        ;;
    *" logs "*)
        printf '%s\\n' "fake bounded diagnostics"
        ;;
    *" down "*)
        printf '%s\\n' "fake stack stopped"
        ;;
esac
"""


def _make_test_project(
    temporary_path: Path,
    *,
    environment_text: str | None = VALID_ENVIRONMENT,
) -> tuple[Path, Path, dict[str, str]]:
    """Create a minimal checkout and a fake Docker command for one script run."""

    project_root = temporary_path / "txt2crs"
    scripts_directory = project_root / "scripts"
    fake_binary_directory = temporary_path / "bin"
    scripts_directory.mkdir(parents=True)
    fake_binary_directory.mkdir()

    shutil.copy2(START_LOCAL_SCRIPT, scripts_directory / "start-local.sh")
    (project_root / ".env.example").write_text(
        VALID_ENVIRONMENT,
        encoding="ascii",
    )
    (project_root / "docker-compose.yml").write_text(
        "services: {}\n",
        encoding="ascii",
    )
    if environment_text is not None:
        (project_root / ".env").write_text(environment_text, encoding="ascii")

    fake_docker = fake_binary_directory / "docker"
    fake_docker.write_text(FAKE_DOCKER_SCRIPT, encoding="ascii")
    fake_docker.chmod(fake_docker.stat().st_mode | stat.S_IXUSR)

    fake_docker_log = temporary_path / "docker.log"
    process_environment = os.environ.copy()
    process_environment.update(
        {
            "FAKE_DOCKER_LOG": str(fake_docker_log),
            "NO_COLOR": "1",
            "PATH": f"{fake_binary_directory}:{process_environment['PATH']}",
        }
    )
    return project_root, fake_docker_log, process_environment


def _run_start_script(
    project_root: Path,
    process_environment: dict[str, str],
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    """Run the copied startup script and capture its complete terminal output."""

    return subprocess.run(
        ["bash", str(project_root / "scripts" / "start-local.sh"), *arguments],
        cwd="/",
        env=process_environment,
        check=False,
        capture_output=True,
        text=True,
    )


def test_startup_script_is_executable_ascii_and_uses_lf() -> None:
    """The advertised command must run directly in ordinary ASCII terminals."""

    script_bytes = START_LOCAL_SCRIPT.read_bytes()

    assert START_LOCAL_SCRIPT.stat().st_mode & stat.S_IXUSR
    assert script_bytes.isascii()
    assert b"\r" not in script_bytes


def test_environment_examples_explain_roles_and_cross_link_each_other() -> None:
    """Every template must direct judges and host developers to the right file."""

    expected_header_markers = {
        ROOT_ENVIRONMENT_EXAMPLE: (
            "CANONICAL JUDGE AND DOCKER CONFIGURATION",
            "backend/.env.example",
            "frontend/.env.example",
        ),
        BACKEND_ENVIRONMENT_EXAMPLE: (
            "HOST-ONLY BACKEND DEVELOPMENT",
            "../.env.example",
            "../frontend/.env.example",
        ),
        FRONTEND_ENVIRONMENT_EXAMPLE: (
            "HOST-ONLY FRONTEND DEVELOPMENT",
            "../.env.example",
            "../backend/.env.example",
        ),
    }

    for environment_template, required_markers in expected_header_markers.items():
        template_bytes = environment_template.read_bytes()
        concise_header = b"\n".join(template_bytes.splitlines()[:18]).decode("ascii")

        assert template_bytes.isascii(), environment_template
        assert b"\r" not in template_bytes, environment_template
        for required_marker in required_markers:
            assert required_marker in concise_header, (
                environment_template,
                required_marker,
            )


def test_missing_environment_aborts_before_docker_with_copy_instructions(
    tmp_path: Path,
) -> None:
    """A fresh clone must explain configuration before probing host tools."""

    project_root, fake_docker_log, process_environment = _make_test_project(
        tmp_path,
        environment_text=None,
    )

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr

    assert result.returncode == 2
    assert "CONFIGURATION REQUIRED" in combined_output
    assert "cp .env.example .env" in combined_output
    assert "SECRET_KEY" in combined_output
    assert "POSTGRES_PASSWORD" in combined_output
    assert "FIRST_SUPERUSER_PASSWORD" in combined_output
    assert "TAVILY_API_KEY" in combined_output
    assert not fake_docker_log.exists()


def test_placeholder_secrets_fail_without_printing_environment_values(
    tmp_path: Path,
) -> None:
    """Default placeholders must fail closed without leaking configured values."""

    environment_text = VALID_ENVIRONMENT.replace(
        "SECRET_KEY=0123456789abcdef0123456789abcdef",
        "SECRET_KEY=changethis",
    ).replace(
        "TAVILY_API_KEY=test-tavily-key",
        "TAVILY_API_KEY=",
    )
    project_root, fake_docker_log, process_environment = _make_test_project(
        tmp_path,
        environment_text=environment_text,
    )

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr

    assert result.returncode == 2
    assert "SECRET_KEY" in combined_output
    assert "TAVILY_API_KEY" in combined_output
    assert "changethis" not in combined_output
    assert not fake_docker_log.exists()


def test_last_duplicate_environment_assignment_matches_compose_semantics(
    tmp_path: Path,
) -> None:
    """Validation must inspect the same final assignment that Compose will use."""

    environment_text = f"{VALID_ENVIRONMENT}\nSECRET_KEY=changethis\n"
    project_root, fake_docker_log, process_environment = _make_test_project(
        tmp_path,
        environment_text=environment_text,
    )

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr

    assert result.returncode == 2
    assert "SECRET_KEY" in combined_output
    assert "changethis" not in combined_output
    assert not fake_docker_log.exists()


def test_default_start_validates_compose_builds_waits_and_prints_next_steps(
    tmp_path: Path,
) -> None:
    """The happy path must use the repository's authoritative Compose command."""

    project_root, fake_docker_log, process_environment = _make_test_project(tmp_path)

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr
    docker_commands = fake_docker_log.read_text(encoding="ascii")

    assert result.returncode == 0, combined_output
    assert "config --quiet" in docker_commands
    assert "up --detach --build --wait" in docker_commands
    assert "TXT2CRS IS READY" in combined_output
    assert "http://localhost:5195" in combined_output
    assert "http://localhost:8016/docs" in combined_output
    assert "http://localhost:5195/setup" in combined_output
    assert "FIRST_SUPERUSER_PASSWORD" in combined_output


def test_no_build_status_and_stop_modes_remain_non_destructive(tmp_path: Path) -> None:
    """Useful repeat operations must never prune images or delete volumes."""

    project_root, fake_docker_log, process_environment = _make_test_project(tmp_path)

    no_build_result = _run_start_script(
        project_root,
        process_environment,
        "--no-build",
    )
    status_result = _run_start_script(project_root, process_environment, "--status")
    stop_result = _run_start_script(project_root, process_environment, "--stop")
    docker_commands = fake_docker_log.read_text(encoding="ascii")

    assert no_build_result.returncode == 0
    assert status_result.returncode == 0
    assert stop_result.returncode == 0
    assert "up --detach --wait" in docker_commands
    assert "down --remove-orphans" in docker_commands
    assert "prune" not in docker_commands
    assert "--volumes" not in docker_commands
    assert "down --remove-orphans --volumes" not in docker_commands


def test_foreign_port_conflict_aborts_before_compose_start(tmp_path: Path) -> None:
    """A conflicting local project should be named before a long image build."""

    project_root, fake_docker_log, process_environment = _make_test_project(tmp_path)
    process_environment["FAKE_DOCKER_MODE"] = "port-conflict"

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr
    docker_commands = fake_docker_log.read_text(encoding="ascii")

    assert result.returncode == 3
    assert "PORT CONFLICT" in combined_output
    assert "5195" in combined_output
    assert "another-project-frontend-1" in combined_output
    assert " up " not in f" {docker_commands} "


def test_current_project_port_is_allowed_for_idempotent_restart(tmp_path: Path) -> None:
    """A repeated startup must recognize its own full Docker container IDs."""

    project_root, fake_docker_log, process_environment = _make_test_project(tmp_path)
    process_environment["FAKE_DOCKER_MODE"] = "own-port"

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr
    docker_commands = fake_docker_log.read_text(encoding="ascii")

    assert result.returncode == 0, combined_output
    assert "PORT CONFLICT" not in combined_output
    assert "up --detach --build --wait" in docker_commands


def test_duplicate_host_ports_abort_before_docker(tmp_path: Path) -> None:
    """The checked-in allocation cannot contain an internal host collision."""

    environment_text = VALID_ENVIRONMENT.replace(
        "BACKEND_PORT=8016",
        "BACKEND_PORT=5195",
    )
    project_root, fake_docker_log, process_environment = _make_test_project(
        tmp_path,
        environment_text=environment_text,
    )

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr

    assert result.returncode == 2
    assert "BACKEND_PORT" in combined_output
    assert "FRONTEND_PORT" in combined_output
    assert "must use unique host ports" in combined_output
    assert not fake_docker_log.exists()


def test_start_failure_prints_bounded_diagnostics(tmp_path: Path) -> None:
    """A failed deployment must leave the judge with immediate recovery evidence."""

    project_root, fake_docker_log, process_environment = _make_test_project(tmp_path)
    process_environment["FAKE_DOCKER_MODE"] = "up-failure"

    result = _run_start_script(project_root, process_environment)
    combined_output = result.stdout + result.stderr
    docker_commands = fake_docker_log.read_text(encoding="ascii")

    assert result.returncode == 1
    assert "DEPLOYMENT FAILED" in combined_output
    assert "fake bounded diagnostics" in combined_output
    assert "ps --all" in docker_commands
    assert "logs --no-color --tail 80 db prestart backend frontend" in docker_commands


def test_legacy_deploy_command_is_a_safe_compatibility_wrapper() -> None:
    """The donor-era command must delegate instead of pruning global Docker state."""

    legacy_script_text = LEGACY_DEPLOY_SCRIPT.read_text(encoding="utf-8")

    assert "start-local.sh" in legacy_script_text
    assert "exec" in legacy_script_text
    assert "docker builder prune" not in legacy_script_text
    assert "python-react-boilerplate" not in legacy_script_text
    assert "--volumes" not in legacy_script_text
