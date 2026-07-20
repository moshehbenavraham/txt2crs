# Architecture

## System Overview

txt2crs is a three-package FastAPI/React monorepo. The reusable engine owns
education-domain behavior and exposes one framework-independent application
facade; the application shell owns transport and identity. The shell composes
one facade, serial worker, readiness cache, and system-authentication
coordinator for its complete lifespan. The finished application exposes
authenticated, durable learner submission plus owner-scoped status, result,
manifest, and artifact delivery routes. Account deletion performs engine-first
owner erasure. The frontend consumes those generated contracts for public
discovery, strict multimode intake, durable progress, four completed
publications, private artifact transfer, and isolated HTML preview.

```text
React SPA
    |
    | generated OpenAPI client / HTTPS
    v
FastAPI shell
    |-- PostgreSQL: application users
    |-- private state volume: engine SQLite, artifacts, Codex home
    |-- authenticated course submission, result, artifact, and readiness APIs
    |-- superuser setup API
    `-- lifespan-owned course-system services
            |-- public txt2crs application facade
            |-- one serial recovery/execution worker
            |-- side-effect-free cached readiness
            |-- dedicated ChatGPT authentication coordinator
            `-- managed loopback research MCP and Codex runtime
```

The research MCP server is package-owned and loopback-only. The separate admin
MCP server under `backend/app/mcp/` is a disabled-by-default coding/admin
surface; the two boundaries must never be merged.

## Components

| Component | Location | Technology | Current responsibility |
|-----------|----------|------------|------------------------|
| Backend shell | `backend/app/` | FastAPI, SQLModel, PostgreSQL | HTTP, JWT identity, configuration, migrations, facade composition, serial work, cached readiness, system authentication, errors, and observability |
| Education engine | `backend/packages/txt2crs/` | Pydantic, SQLite, Codex, FastMCP | Public application facade/factories, ingestion, research, generation, policy, jobs, recovery, artifacts, owner lifecycle, rendering, and evaluation |
| Frontend | `frontend/` | React 19, Vite, TanStack, Tailwind | Public discovery, authentication, course intake, durable progress/results, private artifact preview/download, users, and superuser system setup |
| Local topology | `docker-compose.yml` | Docker Compose | PostgreSQL, one backend process, frontend, and persistent private state |

## Ownership Boundaries

- Route handlers call the public `txt2crs` boundary; they never reimplement
  generation, research, policy, persistence, validation, or rendering.
- PostgreSQL is authoritative for application users. Tenant-scoped engine
  SQLite is authoritative for generation jobs.
- Engine owner erasure cancels tracked work, removes private artifacts, then
  transactionally deletes SQLite job parents. Both shell account-deletion
  flows call that public operation before deleting the PostgreSQL user.
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

1. The shell translates validated settings once into `RealApplicationConfig`
   and owns one `Txt2CrsApplication` for its lifespan.
2. The facade delegates durable submission, recovery, safe public job and
   artifact reads, readiness/authentication, executor creation, and owner purge
   to package-owned services.
3. Execution persists provider-free ingestion, policy, and preference
   preparation before opening job-scoped Tavily, research MCP, and Codex
   resources.
4. The exact accepted request and checkpoints drive restart recovery; current
   defaults and refetched source content do not reinterpret accepted work.
5. Owner-scoped status reads expose a finite public projection with a durable
   revision. The package performs ownership lookup and public-state coherence
   checks; the shell adds fixed progress copy and transport links.
6. Manifest and byte reads reauthorize through the package separately.
   Metadata is path-free, and the byte context verifies stored size and hash
   before the shell sends headers.
7. The ASGI response owns an already-entered artifact context and closes it
   exactly once after success, disconnect, send/iterator error, or response
   construction failure.

### Durable Recovery And Artifact Replay

1. Submission commits the exact request, execution profile, admission
   reservation, and accepted row before the shell returns `202`.
2. The single serial worker discovers durable accepted work at startup in
   addition to processing in-memory wake events.
3. Each accepted generation stage atomically persists a package checkpoint
   and revision. A replacement builds fresh runtime resources and consumes
   only the provider turns that follow that checkpoint.
4. The final cross-validated bundle is durable before rendering. Rendering
   and delivery are deterministic local operations, so replacements at those
   boundaries do not repeat model or research work.
5. Artifact publication is verified on every manifest and byte read. A
   topology, metadata, size, or hash mismatch fails closed instead of serving
   partial or unverified output.

### Authentication

1. The client posts credentials to `/api/v1/login/access-token`.
2. The backend validates the user and returns a bearer token.
3. The frontend stores the token in `sessionStorage`.
4. Protected requests send `Authorization: Bearer <token>`.
5. Confirmed `401` session invalidation clears state; an authorization `403`
   does not log the user out.

### Learner Browser Flow

1. The public root stores only an explicitly saved, bounded prompt handoff in
   tab-scoped `sessionStorage`; `/create` consumes it once after authentication.
2. The intake schema accepts one active source family, removes inactive
   fields, requires literal provider-processing consent, and delegates only to
   generated JSON or multipart job operations.
3. One canonical idempotency key survives an exact failed transport retry and
   rotates after the draft changes or the server durably accepts it.
4. `/jobs/$jobId` reads the owner-safe revisioned projection, polls only
   non-terminal states, and preserves the latest monotonic snapshot through a
   transient reconnect.
5. A completed job enables one manifest read. The UI exposes only verified
   entries for the four publications and never constructs artifact URLs or
   filesystem paths.
6. HTML transfer is bounded and metadata-verified before separate parsing,
   active-content removal, restrictive preview CSP, an empty iframe sandbox,
   and revocable temporary URL ownership.

### Health

- Backend readiness executes `SELECT 1` against PostgreSQL and returns `503`
  when unavailable.
- Backend liveness proves the HTTP process is responsive.
- Frontend health is served directly by Nginx without loading React.
- Authenticated course-system readiness is served from a bounded cache covering
  engine storage, worker, research, model, input capabilities, and admission.
  Browser polling never performs provider or destructive storage probes.

### Error Contract

Backend failures use RFC 9457 Problem Details with stable application error
codes and trace IDs. Shell errors use `AppException` and
`app.core.constants.ErrorCode`. Missing and foreign job/artifact reads share
the same `JOB_7001` response; projection and artifact-integrity failures map
to the safe `SYSTEM_6002` response.

## Observability and Security

Structured logging, optional OpenTelemetry, rate limiting outside local mode,
private filesystem modes, non-root containers, and redacted request metadata
are implemented. Remote CodeQL remains unavailable while GitHub rejects
Actions jobs before runner assignment; local deterministic security
equivalents are recorded in the cumulative security report.

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
