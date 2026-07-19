# ADR-0007: Coolify Deployment Platform

## Status

Superseded by [ADR-0008](0008-local-only-deployment-scope.md)

## Date

2026-02-19

## Historical Context

The imported application shell previously selected Coolify for separate
hosted backend and frontend applications. That donor-era choice included a
platform API workflow, a provisioning script, application UUIDs, domains, and
platform-managed environment variables.

## Historical Decision

Use Coolify as the shell's hosted production platform.

## Supersession

On 2026-07-19, the txt2crs owner explicitly established repository-root Docker
Compose as the only deployment target in the project scope. The hosted
workflow, provisioning script, scheduled remote operations workflows, and
platform-specific example variables were removed.

This ADR remains only to preserve why those inherited files once existed. It
does not authorize or recommend a hosted target. Any future hosting choice
requires explicit owner approval, fresh requirements, and a new ADR.

## Current Decision

See [ADR-0008](0008-local-only-deployment-scope.md) and the
[deployment policy](../deployment-policy.md).
