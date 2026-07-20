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
# Replace local placeholder secrets and set TAVILY_API_KEY.
./scripts/start-local.sh
```

The judge-facing assistant performs non-destructive environment, Docker,
Compose, and port preflight checks before it runs the authoritative
`docker compose up --detach --build --wait` command. It starts the complete
application topology:

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

Create one complete owner-only local backup bundle with:

```bash
./scripts/backup-local-state.sh
```

The command briefly stops the backend writer, captures a PostgreSQL
custom-format dump plus all durable private engine state, validates both
archives, and writes SHA-256 checksums. The archive intentionally omits
`codex-home/tmp`, which contains image-specific process-scratch links that
Codex recreates at startup; credentials and other durable Codex state remain
included. Restore requires the explicit confirmation documented in
[Local deployment](local-deploy.md#backup-and-restore). The legacy
`scripts/backup-db.sh` helper covers PostgreSQL only and is not a complete
application backup.

Backups contain learner records, generated artifacts, and Codex credentials.
They are ignored by Git, created with owner-only permissions, and must be
copied to an operator-controlled encrypted location for protection from host
loss. Automated off-host retention and hosted disaster recovery remain
outside the current scope.

## Future Hosting

A future production scope is not assumed. If the owner later chooses to host
txt2crs, that work must begin with explicit requirements and a new ADR covering
data residency, secrets, TLS, domains, backups, rollout, rollback,
observability, cost, and platform choice. No platform is preselected.
