# Architecture

## System Overview

`python-react-boilerplate` is a FastAPI + React monorepo with JWT auth, role-based access control, and user-owned item CRUD.

```
React SPA (TanStack Router/Query)
        |
        | HTTPS / REST
        v
FastAPI API (auth, users, items, utils)
        |
        v
PostgreSQL (SQLModel/Alembic)
```

## Deployment Topology

- **Primary deployment path (source of truth)**: Coolify, defined by ADR-0007 and `.github/workflows/deploy-coolify.yml`.
- **Legacy fallback path**: `.github/workflows/deploy-staging.yml` and `.github/workflows/deploy-production.yml` remain break-glass options for incident response only.
- **Policy reference**: see `docs/deployment-policy.md`.

## Backend Architecture (`backend/app`)

| Area | Path | Responsibility |
|---|---|---|
| API routing | `api/main.py`, `api/routes/` | Route registration and endpoint handlers |
| Auth dependencies | `api/deps.py`, `core/security.py` | Bearer token validation and role checks |
| Domain/data layer | `models.py`, `crud.py` | SQLModel entities and persistence logic |
| Runtime config | `core/config.py` | Environment policy, fail-closed defaults, pool tuning |
| Error contract | `core/exceptions.py`, `core/exception_handlers.py` | RFC 9457 Problem Details responses |
| Observability | `core/logging.py`, `core/telemetry.py` | Structured logs + optional OpenTelemetry |

## Frontend Architecture (`frontend/src`)

| Area | Path | Responsibility |
|---|---|---|
| App bootstrap | `main.tsx` | Query client, global error handling, router setup |
| Routing | `routes/` | File-based route tree and guard layout |
| Auth/session | `hooks/useAuth.ts`, `lib/session.ts` | Login/logout, token/session lifecycle, cache reset |
| API integration | `client/` (generated), component hooks | Typed SDK calls and mutation/query orchestration |
| Validation | `lib/schemas/` | Centralized Zod schemas aligned to backend constraints |

## Runtime Flows

### Authentication and Session Flow

1. Client calls `POST /api/v1/login/access-token`.
2. Backend validates credentials and returns an access token.
3. Frontend stores token in **session storage** (`sessionStorage`), with one-time migration cleanup for legacy `localStorage` tokens.
4. Authenticated requests include `Authorization: Bearer <token>`.
5. Frontend clears auth state only on confirmed authn invalidation (`401` and stale `/users/me` session lookup), not on generic `403` authorization failures.

### Health and Probes

- Readiness endpoint: `GET /api/v1/utils/health/` (returns `503` when dependencies are unhealthy).
- Liveness endpoint: `GET /api/v1/utils/health-check/`.
- Deployment smoke checks and operational runbooks should treat readiness and liveness distinctly.

### Error Contract

Backend negative-path responses are normalized to RFC 9457 Problem Details (`application/problem+json`) with stable semantic fields:

- `type`
- `status`
- `code`
- `trace_id`
- `detail`

## Observability and Versioning

- Structured JSON logs include trace correlation metadata.
- OpenTelemetry is opt-in via `OTEL_ENABLED`.
- `service.version` is derived from backend package metadata at runtime (project version source of truth), preventing drift from `backend/pyproject.toml`.

## Decision References

- ADR index: `docs/adr/README.md`
- Deployment decision: `docs/adr/0007-coolify-deployment-platform.md`
- Tracing decision: `docs/adr/0005-opentelemetry-distributed-tracing.md`
