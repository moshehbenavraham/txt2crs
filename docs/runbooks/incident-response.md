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

Preserve trace IDs from API responses and logs. Request middleware redacts raw
query strings, path parameters, and client IP addresses, but other events can
still contain account identifiers. Treat log exports as personal data and
restrict access.

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

## Stalled Durable Job Or Worker Replacement

1. Preserve the affected response `trace_id`, job status, public `revision`,
   and timestamps. Do not copy learner input, artifact bytes, provider
   payloads, or private paths into the incident record.
2. Check the cached course-system readiness verdict and correlated
   `txt2crs.worker_*` / `txt2crs.execution_*` log events.
3. Confirm that exactly one backend process and serial worker own the private
   SQLite state. Do not add replicas or extra Uvicorn workers.
4. If the process is unhealthy, restart only the backend. A fresh worker
   discovers durable accepted jobs at startup and resumes active jobs from
   their last accepted checkpoint; it does not require the original in-memory
   wake event.
5. Poll `GET /api/v1/jobs/{job_id}` as the authenticated owner. Verify that
   `revision` advances or that a terminal `completed`, `failed`, or
   `cancelled` status is returned. Do not infer progress from elapsed time.
6. A job already at final validation may replay rendering, and one interrupted
   during delivery may republish artifacts. Neither boundary should start new
   provider turns.
7. If the same revision remains stalled after the backend is healthy, stop
   new admission, capture a consistent backup, and escalate with redacted
   correlated logs. Do not edit the engine SQLite database manually.

## Artifact Integrity Or Delivery Failure

A safe `SYSTEM_6002` response from a status projection, manifest read, or
artifact download indicates that private state could not be represented or
verified. Treat repeated failures as P1 because the route deliberately fails
closed.

1. Preserve the response `trace_id`, HTTP status, public job ID, and request
   time. Do not print the artifact, hash, filename, private path, or exception.
2. Check correlated `artifact.*_failed` and engine events. Cleanup events are
   intentionally sparse; do not enable raw exception or request-body logging.
3. Retry the owner-scoped manifest once. A missing/foreign job or artifact
   returns `JOB_7001`; do not use alternate accounts to probe existence.
4. If metadata succeeds but a download fails, stop serving that job's
   artifacts and create a consistent private-state backup before inspection.
   Never replace a stored hash, byte length, or file merely to make the check
   pass.
5. Restarting the backend is safe but must not be treated as an integrity
   repair. Verified completed artifacts should reopen with identical metadata
   and bytes.
6. Restore only from a reviewed, checksum-validated backup. After recovery,
   read the manifest and download representative HTML, PDF, and DOCX outputs
   as the owner; confirm exact `Content-Type`, `Content-Length`,
   `Content-Disposition`, and private/no-store headers.

## Course-System Readiness or Authentication Failure

1. Log in as a superuser and open `/setup`; do not copy provider credentials
   or private diagnostics into an incident report.
2. Confirm whether the cached verdict reports authentication, research,
   storage, worker, model, input, or admission as the blocking category.
3. Verify `TAVILY_API_KEY` is configured only when research should be enabled,
   and restart the backend after changing `.env`.
4. Retry the browser device-login ceremony once no other ceremony is active.
5. If browser setup remains unavailable, run the exact CLI recovery command
   displayed on `/setup` from `backend/packages/txt2crs/`.
6. Recheck `/setup`; do not add backend replicas or extra Uvicorn workers as a
   recovery action.

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
