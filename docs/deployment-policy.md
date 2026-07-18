# Deployment Policy

## Scope

This policy defines the deployment source of truth for `python-react-boilerplate` and the allowed use of fallback deployment paths.

## Source of Truth

- **Primary deployment path**: Coolify.
- **Authoritative automation**: `.github/workflows/deploy-coolify.yml`.
- **Architecture decision**: `docs/adr/0007-coolify-deployment-platform.md`.

Use this path for normal staging and production releases.

## Legacy Fallback Workflows

- `.github/workflows/deploy-staging.yml`
- `.github/workflows/deploy-production.yml`

These workflows are retained as **break-glass fallback** for incidents where Coolify automation is unavailable or degraded.

### Required controls when using fallback workflows

1. Log incident context and approver in the incident ticket.
2. Run smoke checks and rollback steps defined in `docs/runbooks/incident-response.md`.
3. Open follow-up remediation tasks to restore primary-path operation.

## Deployment Governance

- Changes to deployment routing or primary-path ownership require an ADR update.
- Runbook commands and workflow references must be kept in sync whenever deploy scripts/workflows change.
- Release verification must include readiness (`/api/v1/utils/health/`) and liveness (`/api/v1/utils/health-check/`) checks.
