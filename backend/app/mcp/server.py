"""
MCP server exposing tools for AI agent access.

This module implements an MCP server using MCPServer that provides:
- Database introspection tools (read-only)
- Code validation tools (linting, type checking)
- Schema discovery tools (OpenAPI, endpoints)

The server is designed to be run as a standalone process with stdio transport
for integration with AI coding assistants like Claude Code, Cursor, etc.

Example:
    Run the MCP server:
        uv run python -m app.mcp.server

    Configure in claude_desktop_config.json:
        {
            "mcpServers": {
                "txt2crs-admin": {
                    "command": "uv",
                    "args": ["--directory", "/path/to/backend", "run", "python", "-m", "app.mcp.server"]
                }
            }
        }
"""

import subprocess
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from sqlmodel import Session, func, select

from app.core.config import settings
from app.core.db import engine
from app.models import User

# Initialize MCP server
mcp = MCPServer(name="txt2crs-admin")
BACKEND_ROOT = str(Path(__file__).resolve().parents[2])


# =============================================================================
# Database Introspection Tools (Read-Only)
# =============================================================================


@mcp.tool()
def list_users(
    skip: int = 0,
    limit: int = 20,
    include_inactive: bool = False,
) -> dict[str, Any]:
    """
    List users in the database with pagination.

    Returns a paginated list of users with their public information.
    Sensitive fields (password hashes) are never returned.

    Args:
        skip: Number of records to skip for pagination. Defaults to 0.
        limit: Maximum number of users to return. Defaults to 20, max 100.
        include_inactive: If True, includes inactive users. Defaults to False.

    Returns:
        Dictionary with 'users' list and 'total_count' integer.

    Example:
        list_users(skip=0, limit=10)
        # Returns: {"users": [...], "total_count": 42}
    """
    limit = min(limit, 100)  # Cap at 100

    with Session(engine) as session:
        # Build query
        query = select(User)
        if not include_inactive:
            query = query.where(User.is_active == True)  # noqa: E712

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_count = session.exec(count_query).one()

        # Get paginated results
        query = query.offset(skip).limit(limit)
        users = session.exec(query).all()

        return {
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                }
                for user in users
            ],
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
        }


@mcp.tool()
def get_user_by_email(email: str) -> dict[str, Any] | None:
    """
    Get a user by their email address.

    Performs a case-sensitive email lookup and returns public user information.
    Returns None if no user is found with the given email.

    Args:
        email: Email address to search for (case-sensitive).

    Returns:
        User data dictionary if found, None otherwise.

    Example:
        get_user_by_email("admin@example.com")
        # Returns: {"id": "...", "email": "...", "full_name": "...", ...}
    """
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        }


@mcp.tool()
def get_database_stats() -> dict[str, Any]:
    """
    Get database statistics and table information.

    Returns counts and basic statistics for all tables in the database.
    Useful for understanding the current state of the database.

    Returns:
        Dictionary with table names and their record counts.

    Example:
        get_database_stats()
        # Returns: {"user_count": 10, "active_user_count": 9, ...}
    """
    with Session(engine) as session:
        user_count = session.exec(select(func.count()).select_from(User)).one()
        active_user_count = session.exec(
            select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
        ).one()
        superuser_count = session.exec(
            select(func.count()).select_from(User).where(User.is_superuser == True)  # noqa: E712
        ).one()

        # Extract host/db from URI (hide credentials)
        db_uri = settings.SQLALCHEMY_DATABASE_URI
        if db_uri:
            # Convert to string and extract host part (after @)
            uri_str = str(db_uri)
            db_host = uri_str.split("@")[-1] if "@" in uri_str else "configured"
        else:
            db_host = "Not configured"

        return {
            "user_count": user_count,
            "active_user_count": active_user_count,
            "superuser_count": superuser_count,
            "database_url": db_host,
        }


# =============================================================================
# Code Validation Tools
# =============================================================================


def _run_command(cmd: list[str], cwd: str | None = None) -> dict[str, Any]:
    """Run a command and return structured output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Command timed out after 120 seconds",
        }
    except FileNotFoundError as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command not found: {e}",
        }


@mcp.tool()
def run_ruff_check() -> dict[str, Any]:
    """
    Run ruff linting on the backend code.

    Executes a read-only ruff check for style and code quality issues. File
    mutation is intentionally unavailable through the administrative MCP.

    Returns:
        Dictionary with 'success' boolean and 'output' string.

    Example:
        run_ruff_check()
        # Returns: {"success": True, "output": "All checks passed!"}
    """
    cmd = ["uv", "run", "ruff", "check", "app"]
    return _run_command(cmd, cwd=BACKEND_ROOT)


@mcp.tool()
def run_mypy_check() -> dict[str, Any]:
    """
    Run mypy type checking on the backend code.

    Executes mypy in strict mode to verify type annotations.

    Returns:
        Dictionary with 'success' boolean and 'output' string.

    Example:
        run_mypy_check()
        # Returns: {"success": True, "output": "Success: no issues found in 33 source files"}
    """
    cmd = ["uv", "run", "mypy", "app", "--strict"]
    return _run_command(cmd, cwd=BACKEND_ROOT)


@mcp.tool()
def run_tests(
    test_path: str = "tests/",
    verbose: bool = True,
    markers: str | None = None,
) -> dict[str, Any]:
    """
    Run pytest tests on the backend code.

    Executes pytest with configurable options for test selection.

    Args:
        test_path: Path to test directory or specific test file. Defaults to "tests/".
        verbose: If True, run with verbose output. Defaults to True.
        markers: Optional pytest marker expression (e.g., "not integration").

    Returns:
        Dictionary with 'success' boolean and test output.

    Example:
        run_tests()
        # Returns: {"success": True, "output": "...passed..."}

        run_tests(test_path="tests/models/", markers="hypothesis")
        # Returns property-based test results
    """
    cmd = ["uv", "run", "pytest", test_path]
    if verbose:
        cmd.append("-v")
    if markers:
        cmd.extend(["-m", markers])
    cmd.append("--tb=short")

    return _run_command(cmd, cwd=BACKEND_ROOT)


@mcp.tool()
def run_full_validation() -> dict[str, Any]:
    """
    Run complete validation suite (ruff, mypy, tests).

    Executes all validation steps in order and reports aggregate results.
    This is equivalent to running the pre-commit checks.

    Returns:
        Dictionary with results for each validation step and overall success.

    Example:
        run_full_validation()
        # Returns: {"overall_success": True, "ruff": {...}, "mypy": {...}, "tests": {...}}
    """
    results: dict[str, Any] = {
        "overall_success": True,
        "steps": [],
    }

    # Run ruff
    ruff_result = _run_command(["uv", "run", "ruff", "check", "app"], cwd=BACKEND_ROOT)
    results["steps"].append({"name": "ruff", **ruff_result})
    if not ruff_result["success"]:
        results["overall_success"] = False

    # Run ruff format check
    format_result = _run_command(
        ["uv", "run", "ruff", "format", "--check", "app"], cwd=BACKEND_ROOT
    )
    results["steps"].append({"name": "ruff-format", **format_result})
    if not format_result["success"]:
        results["overall_success"] = False

    # Run mypy
    mypy_result = _run_command(
        ["uv", "run", "mypy", "app", "--strict"], cwd=BACKEND_ROOT
    )
    results["steps"].append({"name": "mypy", **mypy_result})
    if not mypy_result["success"]:
        results["overall_success"] = False

    # Run unit tests (without database dependency)
    test_result = _run_command(
        ["uv", "run", "pytest", "tests/models/", "-v", "--tb=short"],
        cwd=BACKEND_ROOT,
    )
    results["steps"].append({"name": "tests-unit", **test_result})
    if not test_result["success"]:
        results["overall_success"] = False

    return results


# =============================================================================
# Schema Discovery Tools
# =============================================================================


@mcp.tool()
def get_api_endpoints() -> dict[str, Any]:
    """
    List all API endpoints with their methods and paths.

    Returns a structured list of all routes registered in the FastAPI application.

    Returns:
        Dictionary with 'endpoints' list containing route information.

    Example:
        get_api_endpoints()
        # Returns: {"endpoints": [{"path": "/api/v1/users/", "methods": ["GET", "POST"], ...}]}
    """
    # Import here to avoid circular imports
    from app.main import app

    endpoints = []
    for route in app.routes:
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)
        if isinstance(path, str) and isinstance(methods, set):
            endpoints.append(
                {
                    "path": path,
                    "methods": sorted(methods),
                    "name": getattr(route, "name", None),
                }
            )

    return {"endpoints": endpoints, "count": len(endpoints)}


@mcp.tool()
def get_project_info() -> dict[str, Any]:
    """
    Get project configuration and environment information.

    Returns non-sensitive configuration values useful for understanding
    the project setup.

    Returns:
        Dictionary with project name, version, environment, and settings.

    Example:
        get_project_info()
        # Returns: {"project_name": "...", "environment": "local", ...}
    """
    return {
        "project_name": settings.PROJECT_NAME,
        "api_version": settings.API_V1_STR,
        "environment": settings.ENVIRONMENT,
        "debug": settings.ENVIRONMENT == "local",
        "cors_origins": settings.all_cors_origins,
        "emails_enabled": settings.emails_enabled,
        "sentry_enabled": bool(settings.SENTRY_DSN),
        "otel_enabled": settings.OTEL_ENABLED,
    }


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> None:
    """Run the MCP server with stdio transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
