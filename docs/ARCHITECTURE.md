# Architecture

## System Overview

txt2crs is a three-package FastAPI/React monorepo. The reusable engine owns
education-domain behavior and exposes one framework-independent application
facade; the application shell owns transport and identity. The shell does not
yet compose that facade into course-generation routes.

```text
React SPA
    |
    | generated OpenAPI client / HTTPS
    v
FastAPI shell
    |-- PostgreSQL: users and temporary donor items
    |-- private state volume: engine SQLite, artifacts, Codex home
    `-- public txt2crs application facade
            |-- durable requests, recovery, and owner purge
            |-- bounded ingestion, preferences, and two-stage policy
            |-- managed loopback research MCP and Codex runtime
            `-- generation, public projections, rendering, and private delivery
```

The research MCP server is package-owned and loopback-only. The separate admin
MCP server under `backend/app/mcp/` is a disabled-by-default coding/admin
surface; the two boundaries must never be merged.

## Components

| Component | Location | Technology | Current responsibility |
|-----------|----------|------------|------------------------|
| Backend shell | `backend/app/` | FastAPI, SQLModel, PostgreSQL | HTTP, JWT identity, configuration, migrations, health, errors, and observability |
| Education engine | `backend/packages/txt2crs/` | Pydantic, SQLite, Codex, FastMCP | Public application facade/factories, ingestion, research, generation, policy, jobs, recovery, artifacts, owner lifecycle, rendering, and evaluation |
| Frontend | `frontend/` | React 19, Vite, TanStack, Tailwind | Authentication, users, temporary items, and current shell UI |
| Local topology | `docker-compose.yml` | Docker Compose | PostgreSQL, one backend process, frontend, and persistent private state |

## Ownership Boundaries

- Route handlers call the public `txt2crs` boundary; they never reimplement
  generation, research, policy, persistence, validation, or rendering.
- PostgreSQL is authoritative for application users. Tenant-scoped engine
  SQLite is authoritative for generation jobs.
- Engine owner erasure cancels tracked work, removes private artifacts, then
  transactionally deletes SQLite job parents. A future shell account-deletion
  flow must call that public operation before deleting the PostgreSQL user.
- The backend image runs exactly one non-root FastAPI process while the serial
  worker and SQLite topology remain in use.
- `/var/lib/txt2crs` is the image-owned persistent mount containing the job
  database, artifact tree, and isolated Codex home. Worker scratch data stays
  under `/tmp/txt2crs-worker`.
- The generated OpenAPI client is the frontend contract and is changed only by
  `scripts/generate-client.sh`.

## Deployment Topology

Repository-root Docker Compose is the only deployment target in the current
project scope. The backend and frontend remain separate images inside one
local topology; no hosted platform is selected.

| Deployable | Image | Health |
|------------|-------|--------|
| Backend | `backend/Dockerfile` | Readiness: `/api/v1/utils/health/`; liveness: `/api/v1/utils/health-check/` |
| Frontend | `frontend/Dockerfile` | Nginx JSON health: `/health` |

See [deployment policy](deployment-policy.md) for the local source of truth
and [ADR-0008](adr/0008-local-only-deployment-scope.md) for the scope decision.

## Runtime Flows

### Engine Application Boundary

1. The shell will translate validated settings once into
   `RealApplicationConfig` and own one `Txt2CrsApplication` for its lifespan.
2. The facade delegates durable submission, recovery, safe public job and
   artifact reads, readiness/authentication, executor creation, and owner purge
   to package-owned services.
3. Execution persists provider-free ingestion, policy, and preference
   preparation before opening job-scoped Tavily, research MCP, and Codex
   resources.
4. The exact accepted request and checkpoints drive restart recovery; current
   defaults and refetched source content do not reinterpret accepted work.

### Authentication

1. The client posts credentials to `/api/v1/login/access-token`.
2. The backend validates the user and returns a bearer token.
3. The frontend stores the token in `sessionStorage`.
4. Protected requests send `Authorization: Bearer <token>`.
5. Confirmed `401` session invalidation clears state; an authorization `403`
   does not log the user out.

### Health

- Backend readiness executes `SELECT 1` against PostgreSQL and returns `503`
  when unavailable.
- Backend liveness proves the HTTP process is responsive.
- Frontend health is served directly by Nginx without loading React.
- Phase 02 must extend readiness to engine storage, worker, research, model,
  and capability status before generation admission exists.

### Error Contract

Backend failures use RFC 9457 Problem Details with stable application error
codes and trace IDs. Shell errors use `AppException` and
`app.core.constants.ErrorCode`.

## Observability and Security

Structured logging, optional OpenTelemetry, rate limiting outside local mode,
private filesystem modes, and non-root containers are implemented. The
cumulative security record currently flags raw request path/query/IP logging
for remediation before public source submission.

See
[`../.spec_system/SECURITY-COMPLIANCE.md`](../.spec_system/SECURITY-COMPLIANCE.md)
for current findings.

## Decision References

- [ADR index](adr/README_adr.md)
- [Local-only deployment](adr/0008-local-only-deployment-scope.md)
- [Superseded Coolify history](adr/0007-coolify-deployment-platform.md)
- [Structured logging](adr/0003-structured-json-logging.md)
- [RFC 9457 errors](adr/0004-rfc9457-error-format.md)
- [OpenTelemetry](adr/0005-opentelemetry-distributed-tracing.md)
- [MCP boundaries](adr/0006-mcp-integration.md)
