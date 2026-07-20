"""Contracts for the local read-only administrative MCP boundary."""

import asyncio
import inspect
from pathlib import Path
from typing import Any

import pytest

from app.core.config import settings
from app.mcp import server


def _registered_tool_names() -> set[str]:
    """Read tool names through FastMCP's public asynchronous API."""

    return {tool.name for tool in asyncio.run(server.mcp.list_tools())}


def test_admin_mcp_keeps_user_validation_and_schema_tools_without_items() -> None:
    """Donor retirement must not remove the remaining local admin utilities."""

    assert _registered_tool_names() == {
        "list_users",
        "get_user_by_email",
        "get_database_stats",
        "run_ruff_check",
        "run_mypy_check",
        "run_tests",
        "run_full_validation",
        "get_api_endpoints",
        "get_project_info",
    }


def test_admin_mcp_user_and_database_results_have_no_item_counts() -> None:
    """Read-only user/database introspection no longer references donor rows."""

    superuser = server.get_user_by_email(settings.FIRST_SUPERUSER)
    assert superuser is not None
    assert set(superuser) == {
        "id",
        "email",
        "full_name",
        "is_active",
        "is_superuser",
    }

    database_stats = server.get_database_stats()
    assert set(database_stats) == {
        "user_count",
        "active_user_count",
        "superuser_count",
        "database_url",
    }


def test_admin_mcp_imports_neither_donor_model_nor_research_boundary() -> None:
    """The shell admin server and engine research MCP remain disjoint."""

    module_source = inspect.getsource(server)
    assert "from app.models import Item" not in module_source
    assert "list_items" not in module_source
    assert "get_item" not in module_source
    assert "txt2crs.research" not in module_source
    assert "research_mcp" not in module_source


def test_admin_mcp_validation_tools_target_this_backend_without_file_writes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Retained validation tools must operate here and preserve read-only scope."""

    command_calls: list[tuple[list[str], str | None]] = []

    def record_command(
        command: list[str],
        cwd: str | None = None,
    ) -> dict[str, Any]:
        command_calls.append((command, cwd))
        return {
            "success": True,
            "returncode": 0,
            "stdout": "",
            "stderr": "",
        }

    monkeypatch.setattr(server, "_run_command", record_command)
    assert server.run_ruff_check()["success"] is True
    assert server.run_mypy_check()["success"] is True
    assert server.run_tests()["success"] is True
    assert server.run_full_validation()["overall_success"] is True

    expected_backend_root = str(Path(server.__file__).resolve().parents[2])
    assert command_calls
    assert {cwd for _, cwd in command_calls} == {expected_backend_root}
    assert all("--fix" not in command for command, _ in command_calls)
    assert list(inspect.signature(server.run_ruff_check).parameters) == []
    assert "python-react-boilerplate" not in inspect.getsource(server)
