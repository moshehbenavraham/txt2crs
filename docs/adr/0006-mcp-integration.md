# ADR-0006: Model Context Protocol (MCP) Integration

## Status

Accepted

## Date

2026-01-27

## Context

AI coding assistants (Claude Code, Cursor, GitHub Copilot, etc.) need structured access to project resources to provide accurate code generation and assistance. The current approach relies on:

1. Reading source files through file system access
2. Parsing documentation (AGENTS.md, ADRs)
3. Running commands via shell access

This approach has limitations:

- **No database visibility**: AI agents cannot see actual data or schema state
- **Unstructured validation output**: Linting and testing results require parsing
- **No programmatic introspection**: Schema discovery requires reading source files
- **Security concerns**: Shell access provides broad system permissions

The Model Context Protocol (MCP) has emerged as the industry standard for connecting AI agents to tools and data sources, with backing from Anthropic, OpenAI, Google, and Microsoft. MCP provides:

- Standardized tool discovery and invocation
- Structured input/output for all operations
- Built-in security through tool-level permissions
- Transport flexibility (stdio, HTTP/SSE, WebSocket)

## Decision

Implement an MCP server for this codebase that exposes:

### Database Introspection Tools (Read-Only)

| Tool | Purpose |
|------|---------|
| `list_users` | Paginated user listing with public fields |
| `get_user_by_email` | User lookup by email |
| `list_items` | Paginated item listing with optional filtering |
| `get_item` | Full item details by ID |
| `get_database_stats` | Table counts and statistics |

### Code Validation Tools

| Tool | Purpose |
|------|---------|
| `run_ruff_check` | Linting with optional auto-fix |
| `run_mypy_check` | Strict type checking |
| `run_tests` | Pytest with marker filtering |
| `run_full_validation` | Complete validation suite |

### Schema Discovery Tools

| Tool | Purpose |
|------|---------|
| `get_api_endpoints` | List all API routes and methods |
| `get_project_info` | Non-sensitive configuration info |

### Security Constraints

1. **Read-only database access**: No CREATE, UPDATE, or DELETE operations
2. **No sensitive data exposure**: Password hashes, tokens never returned
3. **Sandboxed command execution**: Only predefined validation commands
4. **Configuration-controlled**: Can be disabled via `MCP_ENABLED=false`

### Implementation

Using the official `mcp` Python SDK with FastMCP:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name="python-react-boilerplate",
    version="1.0.0",
)

@mcp.tool()
def list_users(skip: int = 0, limit: int = 20) -> dict:
    """List users in the database."""
    # Implementation
```

### Transport

The server uses stdio transport for Claude Code integration:

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "python-react-boilerplate": {
      "command": "uv",
      "args": ["--directory", "/path/to/backend", "run", "python", "-m", "app.mcp.server"]
    }
  }
}
```

## Consequences

### Positive

- **Structured data access**: AI agents can query database directly with proper schemas
- **Reduced hallucination**: Agents see actual data instead of guessing from code
- **Standardized validation**: JSON output from linting/testing enables automated iteration
- **Better tool selection**: Docstrings guide agents to correct tools
- **Security isolation**: Read-only access prevents accidental mutations
- **Industry standard**: Compatible with all major AI coding tools

### Negative

- **Additional dependency**: `mcp>=1.28.1,<2.0.0` added to requirements
- **Maintenance overhead**: Tools need updating when models change
- **Database connection required**: MCP server needs DB access for introspection
- **Local development only**: Production MCP access requires additional security

### Neutral

- **Separate process**: MCP server runs independently from FastAPI app
- **stdio transport**: Requires process management by the AI tool

## Alternatives Considered

### Alternative 1: HTTP-based custom API

Create a separate REST API endpoint for AI agent access.

**Rejected because:**
- Not standardized; each AI tool would need custom integration
- Requires authentication handling
- Duplicates existing API functionality

### Alternative 2: Direct database access via MCP database tools

Use existing MCP database connectors like `mcp-server-postgres`.

**Rejected because:**
- Exposes raw SQL access (security risk)
- No filtering of sensitive fields
- No custom validation tools
- Less control over returned data structure

### Alternative 3: File-based introspection only

Only expose file reading and schema parsing tools.

**Rejected because:**
- Cannot see actual database state
- Requires parsing unstructured outputs
- Limited debugging capability

## Implementation Notes

### File Structure

```
backend/app/mcp/
├── __init__.py      # Package init, exports mcp server
└── server.py        # FastMCP server with all tools
```

### Running the Server

```bash
# Standalone (for testing)
cd backend && uv run python -m app.mcp.server

# Via Claude Code configuration
# Add to ~/.config/claude-code/settings.json or claude_desktop_config.json
```

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `MCP_ENABLED` | `true` | Enable/disable MCP server |
| `MCP_DB_READ_ONLY` | `true` | Enforce read-only database access |

## References

- [Model Context Protocol Official](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Impact on 2025 - Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/generative-ai/model-context-protocol-mcp-impact-2025)
- [ADR-0005: OpenTelemetry Distributed Tracing](./0005-opentelemetry-distributed-tracing.md)
