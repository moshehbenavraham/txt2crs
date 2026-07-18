# ADR-0007: Coolify Deployment Platform

## Status

Accepted

## Date

2026-02-19

## Context

The project needs a production deployment platform that provides:

1. **Zero-downtime deployments** with health-check-based rollouts
2. **Rollback capability** via a web dashboard
3. **API-driven automation** for CI/CD integration
4. **Self-hosted control** over infrastructure and data
5. **Independent scaling** of backend and frontend applications

The existing deployment workflow (`deploy-production.yml`) relies on a self-hosted runner with Docker Compose, which couples backend and frontend deployments, lacks rollback UI, and requires maintaining runner infrastructure.

## Decision

Use **Coolify** as the production deployment platform with **separate backend and frontend applications** managed independently.

### Architecture

```
GitHub (push/release)
  |
  v
GitHub Actions (trigger only)
  |
  v
Coolify API (/applications/{uuid}/start)
  |
  +-- Backend App (FastAPI, multi-stage Dockerfile, port 8000)
  |     Domain: api.{APP_DOMAIN}
  |     Health check: /api/v1/utils/health/
  |
  +-- Frontend App (React/Nginx, port 80)
        Domain: {APP_DOMAIN}
```

### Deployment Automation

| Component | Purpose |
|-----------|---------|
| `scripts/coolify-deploy.sh` | CLI for first-time setup (`--create`), redeployment, and status checks |
| `.github/workflows/deploy-coolify.yml` | CD workflow triggered by push/release/manual dispatch |

### Backend Dockerfile Changes

The backend Dockerfile is restructured into three stages:

| Stage | Purpose | Used By |
|-------|---------|---------|
| `base` | Shared dependency installation | (intermediate) |
| `development` | Local dev with test packages (default) | `docker compose` |
| `production` | Non-root user, no dev deps, healthcheck | Coolify via `dockerfile_target_build` |

### Environment Management

Coolify manages environment variables per-application with secret encryption. The deploy script sets all required variables via `POST /applications/{uuid}/envs/bulk`, with sensitive values marked `is_secret: true`.

## Consequences

### Positive

- **Zero-downtime deployments**: Coolify health-checks new containers before routing traffic
- **Independent deploys**: Backend and frontend scale and deploy separately
- **Web dashboard**: Rollback, logs, metrics accessible without SSH
- **API-driven**: Full automation via REST API, no self-hosted runners needed
- **Cost predictable**: Fixed server cost vs. variable cloud PaaS pricing
- **Security**: Production containers run as non-root user

### Negative

- **Coolify dependency**: Adds infrastructure dependency on Coolify instance
- **Self-managed infrastructure**: Server and Coolify updates are team responsibility
- **No global edge**: Single-region deployment (use CDN for static assets if needed)

### Neutral

- **GitHub Actions workflow** is lightweight (API trigger only, no build)
- **Existing compose deploy workflows** remain as break-glass fallback paths only (`deploy-staging.yml` / `deploy-production.yml`)

## Alternatives Considered

### Alternative 1: Docker Compose on Self-hosted Runner

Continue using compose-based self-hosted runner workflows as the primary path.

**Rejected because:**
- Coupled backend/frontend deployments
- No rollback UI or deployment history
- Requires maintaining self-hosted runner infrastructure
- No built-in health checks or zero-downtime deploys

### Alternative 2: k3s / Lightweight Kubernetes

Deploy a single-node Kubernetes cluster.

**Rejected because:**
- Significant operational overhead for a small team
- Kubernetes YAML complexity exceeds project needs
- Coolify provides adequate orchestration at lower complexity

### Alternative 3: Kamal (formerly MRSK)

Use Basecamp's Kamal for Docker-based deploys.

**Rejected because:**
- Ruby dependency in a Python/TypeScript project
- No web dashboard for team visibility
- Less mature ecosystem than Coolify
- Manual secrets management

## Implementation Notes

### First-time Setup

```bash
# 1. Configure .env with Coolify credentials
# 2. Run initial setup
./scripts/coolify-deploy.sh --create

# 3. Save output UUIDs to .env
BACKEND_APP_UUID=<from output>
FRONTEND_APP_UUID=<from output>

# 4. Add secrets to GitHub repository settings
# COOLIFY_API_TOKEN, COOLIFY_API_URL, BACKEND_APP_UUID, FRONTEND_APP_UUID
```

### Subsequent Deploys

```bash
# Manual redeploy
./scripts/coolify-deploy.sh

# Check status
./scripts/coolify-deploy.sh --status

# Backend only
./scripts/coolify-deploy.sh --backend-only
```

### GitHub Actions Secrets

| Secret | Description |
|--------|-------------|
| `COOLIFY_API_TOKEN` | API token with deploy permissions |
| `COOLIFY_API_URL` | Coolify API base URL |
| `BACKEND_APP_UUID` | Backend application UUID |
| `FRONTEND_APP_UUID` | Frontend application UUID |

## References

- [Coolify Documentation](https://coolify.io/docs)
- [Coolify API Reference](https://coolify.io/docs/api)
- [ADR-0005: OpenTelemetry Distributed Tracing](./0005-opentelemetry-distributed-tracing.md)
- [ADR-0006: MCP Integration](./0006-mcp-integration.md)
- [Deployment Policy](../deployment-policy.md)
