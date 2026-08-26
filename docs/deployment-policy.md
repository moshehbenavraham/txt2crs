# Deployment Policy

## Scope

txt2crs is container-first and deployment-platform neutral.
Docker Compose is the reference deployment source of truth for a complete installation, not a
restriction to one laptop or one vendor. The same backend and frontend images
may run on a hosted container platform when its configuration preserves the
runtime, security, persistence, and health contracts below.

This policy is established by
[ADR-0009](adr/0009-portable-container-deployment.md), which supersedes the
Build Week local-only decision in
[ADR-0008](adr/0008-local-only-deployment-scope.md).

## Reference Path

```bash
cp .env.example .env
# Replace placeholder secrets and set TAVILY_API_KEY when research is enabled.
./scripts/start-local.sh
```

The helper performs non-destructive environment, Docker, Compose, and port
preflight checks, starts PostgreSQL, and reconciles a preserved local volume's
role password with `.env` without deleting records. It then runs the reference
`docker compose up --detach --build --wait` topology:

- PostgreSQL with persistent application data;
- one non-root FastAPI process hosting the reusable engine;
- one Nginx-served React frontend; and
- one private engine-state volume for SQLite jobs, artifacts, and Codex
  credentials.

## Portable Deployment Contract

A local or hosted deployment must preserve these requirements:

- build the backend and frontend from their checked-in Dockerfiles;
- provide PostgreSQL 18 and durable storage for `/var/lib/txt2crs`;
- keep exactly one backend replica while the engine job store is SQLite and
  runtime ownership is process-local;
- keep the research MCP listener private on loopback;
- inject secrets through environment or platform secret storage, never images;
- configure `DOMAIN`, `FRONTEND_HOST`, and `BACKEND_CORS_ORIGINS` for the real
  public origins;
- terminate TLS before authenticated traffic reaches the application;
- preserve private/no-store artifact delivery and owner authorization; and
- use the health endpoints below for rollout and recovery decisions.

The repository intentionally does not select a hosting vendor. Operators may
add platform-specific deployment automation without an architecture waiver as
long as it implements this contract and documents backup, rollout, rollback,
TLS, domain, observability, and secret-management choices.

## Health Contract

| Service | Probe | Meaning |
|---------|-------|---------|
| Backend | `/api/v1/utils/health/` | FastAPI is responsive and PostgreSQL is healthy |
| Frontend | `/health` | Nginx returns `{"status":"healthy","service":"frontend"}` |

The backend also exposes liveness at `/api/v1/utils/health-check/`. Health
checks do not require a browser or provider credentials.

## Registration Policy

Public signup is available in local, staging, and production profiles and is
enabled in the reference configuration. Set both `ENABLE_PUBLIC_SIGNUP=false`
and `VITE_ENABLE_PUBLIC_SIGNUP=false` for an invite-only installation. The
backend setting is always authoritative.

## Data Safety

`docker compose down` preserves named volumes. Do not add `--volumes` unless
the operator explicitly intends to delete PostgreSQL records, engine job
state, rendered artifacts, and the isolated Codex credential store.

Create a complete owner-only local backup bundle with:

```bash
./scripts/backup-local-state.sh
```

The command captures PostgreSQL plus all durable private engine state and
writes SHA-256 checksums. Hosted operators must provide an equivalent encrypted
off-host backup and restore process before accepting production learner data.
See [local deployment](local-deploy.md#backup-and-restore) for the reference
bundle contract.
