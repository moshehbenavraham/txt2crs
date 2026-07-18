# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) that document significant architectural decisions made in this project.

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [0000](0000-template.md) | ADR Template | - | - |
| [0002](0002-tanstack-router-and-query.md) | TanStack Router and Query | Accepted | 2025-12-21 |
| [0003](0003-structured-json-logging.md) | Structured JSON Logging | Accepted | 2026-01-26 |
| [0004](0004-rfc9457-error-format.md) | RFC 9457 Error Format | Accepted | 2026-01-26 |
| [0005](0005-opentelemetry-distributed-tracing.md) | OpenTelemetry Distributed Tracing | Accepted | 2026-01-27 |
| [0006](0006-mcp-integration.md) | MCP Integration | Accepted | 2026-01-27 |
| [0007](0007-coolify-deployment-platform.md) | Coolify Deployment Platform | Accepted | 2026-02-19 |

## Creating a New ADR

1. Copy the template from `0000-template.md`
2. Number it sequentially (e.g., `0005-your-decision.md`)
3. Fill in all sections
4. Add to the index above
5. Submit for review

## ADR Format

Each ADR follows this structure:

- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: What prompted this decision?
- **Decision**: What we chose to do
- **Consequences**: Trade-offs, what this enables, what it prevents

## For AI Agents

When making architectural decisions, check existing ADRs for context. If proposing a change that conflicts with an existing ADR, create a new ADR that supersedes the old one rather than modifying it directly.

Key decisions documented here:
- **ADR-0002**: Frontend uses TanStack Router/Query for type-safe routing and data fetching
- **ADR-0003**: Backend uses structured JSON logging with trace ID correlation
- **ADR-0004**: All API errors follow RFC 9457 Problem Details format
- **ADR-0005**: Backend uses OpenTelemetry for opt-in distributed tracing
- **ADR-0006**: Backend exposes MCP server for AI agent tool access
- **ADR-0007**: Production deployment uses Coolify for self-hosted PaaS
