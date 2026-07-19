# Incident Response

Repository-root Docker Compose is the only deployment topology in scope.
Record the incident start time, source revision, symptoms, and operator actions
before changing local state.

## Severity

| Level | Description | Initial response |
|-------|-------------|------------------|
| P0 | Complete outage, data loss, or credential exposure | Immediate |
| P1 | Authentication, generation, or artifact delivery unavailable | Within 1 hour |
| P2 | Degraded non-critical behavior | Within 4 hours |
| P3 | Cosmetic or documentation issue | Next working session |

## First Checks

```bash
docker compose ps
curl --fail http://localhost:8012/api/v1/utils/health/
curl --fail http://localhost:5183/health
docker compose logs --tail=200 backend
docker compose logs --tail=200 frontend
docker compose logs --tail=200 db
```

Preserve trace IDs from API responses and logs. Logs can contain request
paths, query strings, and client IP addresses, so treat exports as personal
data and restrict access.

## Database Readiness Failure

1. Inspect `docker compose ps db` and `docker compose logs db`.
2. Verify the local PostgreSQL values in `.env`.
3. Restart only PostgreSQL: `docker compose restart db`.
4. Re-run backend readiness.
5. Do not delete volumes as a recovery step.

## Frontend Health or Stale Build

1. Check `curl --fail http://localhost:5183/health`.
2. Inspect `docker compose logs frontend`.
3. Regenerate the API client only when backend routes changed:
   `./scripts/generate-client.sh`.
4. Rebuild with
   `docker compose up --detach --build --wait frontend`.

## Authentication Failures

1. Confirm `.env` has a non-placeholder `SECRET_KEY`.
2. Inspect the correlated backend error without copying bearer tokens.
3. Retry with a new browser session after configuration is corrected.
4. Treat an unexpected secret change as a security incident because existing
   JWTs become invalid.

## Migration Failure

With the backend running, inspect status without modifying data:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic history
```

Correct the migration or configuration and rerun
`docker compose exec backend alembic upgrade head`. A downgrade can destroy or
reinterpret data; use it only after reviewing the target migration and
capturing a complete backup with `./scripts/backup-local-state.sh`.

## Private Engine State Failure

The `txt2crs-state` volume contains engine SQLite jobs, artifacts, and the
isolated Codex credential store.

1. Stop admission of new work before repairing state.
2. Inspect backend logs and volume ownership without printing credentials or
   artifact contents.
3. Keep exactly one backend process and one serial generation worker.
4. Never copy the SQLite database while it is being written.
5. Never use `docker compose down --volumes` as a repair step.

Create a consistent backup before invasive repair:

```bash
./scripts/backup-local-state.sh
```

When recovery requires replacement of both PostgreSQL and private engine
state, use a reviewed bundle:

```bash
TXT2CRS_RESTORE_CONFIRM=replace-local-state \
  ./scripts/restore-local-state.sh \
  ./backups/txt2crs_backup_<UTC timestamp>
```

The restore validates checksums and both archive formats before destructive
replacement, then restarts and waits for a previously running backend. Verify
both health endpoints and inspect correlated logs after recovery.

## Local Rollback

1. Record the current source revision and local image IDs.
2. Stop containers without deleting volumes.
3. Restore the intended source revision through normal version control.
4. Review Alembic compatibility before rebuilding.
5. Run `docker compose up --detach --build --wait`.
6. Verify both health endpoints and the backend version.

`scripts/deploy-rollback.sh` may recreate containers from previously captured
local image IDs, but it does not roll back either database.

## Escalation Gaps

The repository does not yet contain a verified private security-reporting
address or valid CODEOWNERS identity. Those are owner/operator decisions
recorded in
[`../../.spec_system/docs-audit.md`](../../.spec_system/docs-audit.md) and the
[deployment guide](../deployment.md).
