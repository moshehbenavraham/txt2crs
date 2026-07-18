"""
MCP (Model Context Protocol) server for AI agent tool access.

This module provides an MCP server that exposes database introspection,
code validation, and schema discovery tools to AI agents. The server
enables AI agents to:

- Explore database contents (users, items) with read-only access
- Validate code changes (run linting, type checking, tests)
- Discover API schemas and endpoints
- Access project configuration and structure

Usage:
    Run as a standalone MCP server (stdio transport):
        uv run python -m app.mcp.server

    Or import and use programmatically:
        from app.mcp.server import mcp
        mcp.run(transport="stdio")

Security:
    - All database operations are READ-ONLY
    - Code validation tools run in sandboxed environment
    - No write access to files or database
    - Sensitive fields (passwords, tokens) are never exposed

See Also:
    - docs/adr/0006-mcp-integration.md for architectural decisions
    - https://modelcontextprotocol.io/ for MCP specification
"""

from app.mcp.server import mcp

__all__ = ["mcp"]
