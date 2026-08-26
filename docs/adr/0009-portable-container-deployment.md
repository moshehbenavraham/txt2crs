# ADR-0009: Portable Container Deployment

## Status

Accepted

## Date

2026-08-26

## Context

The Build Week delivery plan intentionally limited txt2crs to a local Docker
Compose demonstration. That reduced event risk, but the event has ended and
the restriction now prevents ordinary staging and production deployment even
though the application already has production profiles, container images,
health checks, persistent storage, and TLS-aware routing labels.

## Decision

Treat Docker Compose as the complete reference implementation of a portable
container contract, not as the only permitted target.

Local and hosted deployments may use any platform that preserves the checked-in
image, persistence, topology, health, secret, TLS, and authorization contracts.
No vendor is selected by this decision. Platform automation can be added as a
normal operational change and must document its rollback and recovery path.

Public registration and the exact Codex model are operator configuration in all
runtime environments. The product keeps safe defaults and exact model
discovery; it no longer hard-codes event eligibility choices.

## Consequences

### Positive

- Staging and production profiles can represent real deployments.
- Operators can use a hosted container platform without first reversing an
  event-only architecture prohibition.
- The local workflow remains reproducible and continues to exercise the full
  application topology.

### Constraints retained for product safety

- One backend replica remains required while SQLite owns engine jobs and the
  runtime ownership guard is process-local.
- The research MCP remains loopback-only.
- Private state must be persistent, access-controlled, backed up, and restored
  together with PostgreSQL.
- Hosted traffic requires TLS, explicit origins, secret management, health
  probes, and a documented rollback path.

## Supersedes

[ADR-0008](0008-local-only-deployment-scope.md).
