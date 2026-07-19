# Deployment Policy

## Scope

txt2crs is local-first and local-only for the current project scope.
Repository-root Docker Compose is the sole deployment source of truth.

This policy is established by
[ADR-0008](adr/0008-local-only-deployment-scope.md), which supersedes the
donor-era hosted-platform decision.

## Authoritative Path

```bash
cp .env.example .env
# Replace local placeholder secrets.
docker compose up --detach --build --wait
```

The command starts the complete application topology:

- PostgreSQL with persistent application data;
- one non-root FastAPI process hosting the reusable engine;
- one Nginx-served React frontend;
- one private engine-state volume for SQLite jobs, artifacts, and Codex
  credentials.

There is no active staging, hosted production, or platform-specific deployment
workflow in scope. GitHub Actions validates source and containers; it does not
deploy an environment.

## Health Contract

Docker Compose waits for:

| Service | Probe | Meaning |
|---------|-------|---------|
| Backend | `/api/v1/utils/health/` | FastAPI is responsive and PostgreSQL is healthy |
| Frontend | `/health` | Nginx returns `{"status":"healthy","service":"frontend"}` |

The backend also exposes liveness at
`/api/v1/utils/health-check/`. Health checks run inside their containers and
do not require a browser.

## Data Safety

`docker compose down` preserves named volumes. Do not add `--volumes` unless
the operator explicitly intends to delete:

- PostgreSQL users and application records;
- engine job state and rendered artifacts;
- the locally isolated Codex credential store.

The repository provides a PostgreSQL dump helper, but a complete backup must
also protect private engine state while no writer is active. Off-host backup
and hosted disaster recovery are outside the current scope.

## Future Hosting

A future production scope is not assumed. If the owner later chooses to host
txt2crs, that work must begin with explicit requirements and a new ADR covering
data residency, secrets, TLS, domains, backups, rollout, rollback,
observability, cost, and platform choice. No platform is preselected.
