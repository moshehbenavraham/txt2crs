"""Static contract for every txt2crs port that can bind on the host.

Container-internal ports may repeat ports used by unrelated projects because
Docker isolates them on the project network. This contract covers the host
side of every published mapping plus direct host development and browser-test
listeners, where a collision would prevent txt2crs from starting.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = Path(
    os.getenv("TXT2CRS_REPOSITORY_ROOT", str(DEFAULT_REPOSITORY_ROOT))
)

ROOT_ENVIRONMENT_EXAMPLE = REPOSITORY_ROOT / ".env.example"
COMPOSE_OVERRIDE_FILE = REPOSITORY_ROOT / "docker-compose.override.yml"
TRAEFIK_COMPOSE_FILE = REPOSITORY_ROOT / "docker-compose.traefik.yml"
VITE_CONFIG_FILE = REPOSITORY_ROOT / "frontend" / "vite.config.ts"
PLAYWRIGHT_CONFIG_FILE = REPOSITORY_ROOT / "frontend" / "playwright.config.ts"
JOBS_PLAYWRIGHT_CONFIG_FILE = REPOSITORY_ROOT / "frontend" / "playwright.jobs.config.ts"
BACKEND_CONFIG_FILE = REPOSITORY_ROOT / "backend" / "app" / "core" / "config.py"
BACKEND_ENVIRONMENT_EXAMPLE = REPOSITORY_ROOT / "backend" / ".env.example"
DEVELOPMENT_SCRIPT = REPOSITORY_ROOT / "scripts" / "dev.sh"
PORT_DOCUMENT = REPOSITORY_ROOT / "docs" / "PORTS.md"

COMPOSE_HOST_PORTS = {
    "TRAEFIK_HTTP_PORT": 86,
    "TRAEFIK_HTTPS_PORT": 8443,
    "TRAEFIK_DASHBOARD_PORT": 8102,
    "POSTGRES_PORT": 5450,
    "BACKEND_PORT": 8016,
    "FRONTEND_PORT": 5195,
    "ADMINER_PORT": 8103,
    "MAILCATCHER_SMTP_PORT": 1029,
    "MAILCATCHER_WEB_PORT": 1084,
    "JAEGER_UI_PORT": 16689,
    "OTLP_GRPC_PORT": 4324,
    "OTLP_HTTP_PORT": 4325,
    "PLAYWRIGHT_REPORT_PORT": 9327,
}

DIRECT_HOST_PORTS = {
    "Vite preview": 4177,
    "Vite development": 5196,
    "deterministic Playwright frontend": 5197,
    "deterministic Playwright backend": 8017,
    "research MCP": 8765,
}

ALL_HOST_PORTS = {*COMPOSE_HOST_PORTS.values(), *DIRECT_HOST_PORTS.values()}


def _read_repository_file(path: Path) -> str:
    """Read one authored file using the repository's required encoding."""

    return path.read_text(encoding="ascii")


def _dotenv_assignments(path: Path) -> dict[str, str]:
    """Parse plain dotenv assignments without evaluating shell syntax."""

    assignments: dict[str, str] = {}
    for line in _read_repository_file(path).splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue
        setting_name, separator, setting_value = stripped_line.partition("=")
        if separator:
            assignments[setting_name] = setting_value
    return assignments


def test_registered_host_ports_are_unique_and_valid() -> None:
    """No two txt2crs listeners may compete for one host port."""

    expected_port_count = len(COMPOSE_HOST_PORTS) + len(DIRECT_HOST_PORTS)

    assert len(ALL_HOST_PORTS) == expected_port_count == 18
    assert all(1 <= port <= 65_535 for port in ALL_HOST_PORTS)


def test_root_environment_declares_every_compose_host_port() -> None:
    """Compose host mappings must be visible and configurable in one place."""

    assignments = _dotenv_assignments(ROOT_ENVIRONMENT_EXAMPLE)

    for setting_name, expected_port in COMPOSE_HOST_PORTS.items():
        assert assignments[setting_name] == str(expected_port)


def test_compose_uses_named_host_ports_and_fixed_container_ports() -> None:
    """Only host mappings change; Docker service ports remain conventional."""

    override_text = _read_repository_file(COMPOSE_OVERRIDE_FILE)
    traefik_text = _read_repository_file(TRAEFIK_COMPOSE_FILE)
    expected_override_mappings = {
        "${TRAEFIK_HTTP_PORT?Variable not set}:80",
        "${TRAEFIK_DASHBOARD_PORT?Variable not set}:8080",
        "${POSTGRES_PORT?Variable not set}:5432",
        "${BACKEND_PORT?Variable not set}:8000",
        "${ADMINER_PORT?Variable not set}:8080",
        "${MAILCATCHER_WEB_PORT?Variable not set}:1080",
        "${MAILCATCHER_SMTP_PORT?Variable not set}:1025",
        "${JAEGER_UI_PORT?Variable not set}:16686",
        "${OTLP_GRPC_PORT?Variable not set}:4317",
        "${OTLP_HTTP_PORT?Variable not set}:4318",
        "${FRONTEND_PORT?Variable not set}:80",
        "${PLAYWRIGHT_REPORT_PORT?Variable not set}:9323",
    }

    for expected_mapping in expected_override_mappings:
        assert expected_mapping in override_text

    assert "${TRAEFIK_HTTP_PORT?Variable not set}:80" in traefik_text
    assert "${TRAEFIK_HTTPS_PORT?Variable not set}:443" in traefik_text


def test_direct_host_listeners_use_the_registered_ports_strictly() -> None:
    """Host tools must fail on collisions instead of selecting random fallbacks."""

    vite_text = _read_repository_file(VITE_CONFIG_FILE)
    playwright_text = _read_repository_file(PLAYWRIGHT_CONFIG_FILE)
    jobs_playwright_text = _read_repository_file(JOBS_PLAYWRIGHT_CONFIG_FILE)
    backend_config_text = _read_repository_file(BACKEND_CONFIG_FILE)
    backend_environment_text = _read_repository_file(BACKEND_ENVIRONMENT_EXAMPLE)
    development_script_text = _read_repository_file(DEVELOPMENT_SCRIPT)

    assert re.search(r"server:\s*\{\s*port: 5196,\s*strictPort: true", vite_text)
    assert re.search(r"preview:\s*\{\s*port: 4177,\s*strictPort: true", vite_text)
    assert "http://localhost:5195" in playwright_text
    assert "http://127.0.0.1:8017" in jobs_playwright_text
    assert "http://127.0.0.1:5197" in jobs_playwright_text
    assert "--port 8017" in jobs_playwright_text
    assert "--port 5197 --strictPort" in jobs_playwright_text
    assert 'FRONTEND_HOST: str = "http://localhost:5196"' in backend_config_text
    assert "POSTGRES_PORT: int = 5450" in backend_config_text
    assert "TXT2CRS_RESEARCH_MCP_PORT=8765" in backend_environment_text
    for expected_development_port in (5450, 8016, 5196):
        assert str(expected_development_port) in development_script_text


def test_default_playwright_uses_the_canonical_root_environment() -> None:
    """Stale host-only frontend settings must not redirect the stack journey."""

    playwright_text = _read_repository_file(PLAYWRIGHT_CONFIG_FILE)

    assert 'path.resolve(import.meta.dirname, "../.env")' in playwright_text
    assert 'import "dotenv/config"' not in playwright_text
    assert "BACKEND_PORT" in playwright_text
    assert "process.env.VITE_API_URL =" in playwright_text


def test_repository_port_document_lists_every_host_allocation() -> None:
    """A fresh clone must explain the complete host and container port model."""

    port_document_text = _read_repository_file(PORT_DOCUMENT)
    host_port_section = port_document_text.split("## Host-bound ports", 1)[1].split(
        "## Container-internal ports",
        1,
    )[0]
    documented_host_ports = {
        int(port_match.group(1))
        for port_match in re.finditer(r"(?m)^\| ([0-9]+) \|", host_port_section)
    }

    assert documented_host_ports == ALL_HOST_PORTS
    assert "Container-internal ports" in port_document_text
    assert "Outbound and dynamic ports" in port_document_text
