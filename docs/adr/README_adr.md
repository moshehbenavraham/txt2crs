# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for significant
technical decisions in txt2crs.

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [0000](0000-template.md) | ADR Template | - | - |
| [0002](0002-tanstack-router-and-query.md) | TanStack Router and Query | Accepted | 2025-12-21 |
| [0003](0003-structured-json-logging.md) | Structured JSON Logging | Accepted | 2026-01-26 |
| [0004](0004-rfc9457-error-format.md) | RFC 9457 Error Format | Accepted | 2026-01-26 |
| [0005](0005-opentelemetry-distributed-tracing.md) | OpenTelemetry Distributed Tracing | Accepted | 2026-01-27 |
| [0006](0006-mcp-integration.md) | MCP Integration | Accepted | 2026-01-27 |
| [0007](0007-coolify-deployment-platform.md) | Coolify Deployment Platform | Superseded by 0008 | 2026-02-19 |
| [0008](0008-local-only-deployment-scope.md) | Local-Only Deployment Scope | Superseded by 0009 | 2026-07-19 |
| [0009](0009-portable-container-deployment.md) | Portable Container Deployment | Accepted | 2026-08-26 |

## Creating a New ADR

1. Copy `0000-template.md`.
2. Use the next unused four-digit number.
3. Complete every template section.
4. Add the ADR to the index above.
5. Submit the decision for review.

## ADR Format

Each ADR follows this structure:

- **Status**: Proposed, Accepted, Deprecated, or Superseded
- **Context**: What prompted the decision
- **Decision**: What the project chose
- **Consequences**: Trade-offs and resulting constraints

## For AI Agents

Check existing ADRs before proposing an architectural change. If a new
decision conflicts with an accepted ADR, create a new ADR that explicitly
supersedes it instead of rewriting the historical record.

Key decisions documented here:
- **ADR-0002**: TanStack Router and Query
- **ADR-0003**: Structured JSON logging with trace ID correlation
- **ADR-0004**: RFC 9457 Problem Details errors
- **ADR-0005**: Opt-in OpenTelemetry tracing
- **ADR-0006**: Read-only administrative MCP integration
- **ADR-0007**: Historical Coolify decision, superseded
- **ADR-0008**: Historical Build Week local-only decision, superseded
- **ADR-0009**: Portable container deployment contract
