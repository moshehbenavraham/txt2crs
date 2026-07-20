# Phase 04 Transition Infrastructure Report

**Date:** 2026-07-20
**Base revision:** `dac60fea7b5209022fce3b393f1fbb29663e57b7`
**Result:** PASS
**Selected bundle:** none - validation only
**Deployment target:** isolated repository-root Docker Compose

## Detection And Topology

`bash .spec_system/scripts/analyze-project.sh --json` reported a mixed
Python/TypeScript monorepo with three registered packages, Phase 04 complete,
and no active session. Repository-root Docker Compose is the accepted and
complete deployment target under ADR-0008; there is no hosted environment,
public edge, remote deployment credential, or platform webhook in scope.

The deployable units are the FastAPI backend shell, which hosts the reusable
engine, and the Nginx frontend. PostgreSQL and the private `txt2crs-state`
volume are shared durable infrastructure. The engine library has no
independent deployment surface.

All four infrastructure bundles already existed. This run adopted Security
and Deploy explicitly into `.spec_system/CONVENTIONS.md`, clarified the
seven-day default backup retention, and validated every configured component
against an isolated instance of the actual deployment target.

## Isolated Target

The validation target used:

- Compose project `txt2crs-phase04-pipeline`;
- backend image `txt2crs-phase04-pipeline-backend:dac60fe`;
- frontend image `txt2crs-phase04-pipeline-frontend:dac60fe`;
- isolated Compose-prefixed PostgreSQL and private-state volumes;
- no published host ports.

The backend and frontend ran as production images. PostgreSQL, migrations,
prestart, the API, and Nginx all reached their authored healthy states.

## Health Bundle

The backend container probe reached
`/api/v1/utils/health/`, returned HTTP 200 with `status=healthy`, and proved
PostgreSQL connectivity. The frontend container probe reached `/health` and
returned stable JSON with `status=healthy` and `service=frontend`. Both
containers remained healthy after backup, restore, and rollback recreation.

## Security Bundle

A standalone backend used `ENVIRONMENT=production`, an isolated state root,
the isolated validation PostgreSQL service, disabled research, and no private
development routes. Six rapid invalid login requests returned:

```text
401 401 401 401 401 429
```

The sixth response was an RFC 9457 Problem Details object with
`RATE_5001`, title `Rate Limit Exceeded`, HTTP status 429, and a trace ID. The
server logged `rate_limit.request_rejected` and shut down gracefully.

No WAF is configured because ADR-0008 deliberately excludes a hosted or public
edge. This is not a deferred production check: local Docker is the complete
deployment scope, and the API's non-local protection was validated directly.

## Backup Bundle

The complete recovery drill inserted one PostgreSQL probe and one private
engine-state probe, then ran:

```text
BACKUP_RETENTION_DAYS=7 ./scripts/backup-local-state.sh <isolated-directory>
```

The generated bundle directory was mode `0700`; its PostgreSQL dump,
engine-state archive, manifest, and checksum list were mode `0600`.
`pg_restore --list`, archive validation, and all SHA-256 checks passed.

After the probes were deliberately removed, the drill ran:

```text
TXT2CRS_RESTORE_CONFIRM=replace-local-state \
  ./scripts/restore-local-state.sh <verified-bundle>
```

The restore recreated the application database, replaced the private state
atomically, restarted the backend, and recovered exactly:

- PostgreSQL: `database-roundtrip-ok`;
- private engine state: `engine-roundtrip-ok`.

The probes were then removed, and the backend, frontend, and PostgreSQL all
remained healthy. The first isolated backup invocation accidentally inherited
the developer Compose override; the target was recovered without data loss,
and the successful drill pinned `COMPOSE_FILE` to the base production Compose
file. No repository defect or exception remained.

## Deploy And Rollback Bundle

Local deployment is intentionally manual. The documented rollback helper was
executed with the reviewed current backend and frontend image IDs:

```text
BACKEND_PREV_IMAGE_ID=<reviewed-id> \
FRONTEND_PREV_IMAGE_ID=<reviewed-id> \
STACK_NAME=txt2crs-phase04-pipeline \
./scripts/deploy-rollback.sh
```

It retagged the reviewed images, reran prestart, and recreated only the
application tier. The backend and frontend returned to healthy, the backend
and frontend containers used the exact supplied image IDs, PostgreSQL kept the
same container, and the backend retained
`txt2crs-phase04-pipeline_txt2crs-state`. API and frontend health responses
passed again after rollback.

The tag/manual GitHub release workflow validates release artifacts but never
deploys, matching the local-only policy. Data rollback remains a separate,
explicit, checksum-validated restore operation.

## Evidence Ledger

| Bundle | Component | Package | Validation Target | Command / Check | Result | Fixes Applied | Remaining / Blocker |
|--------|-----------|---------|-------------------|-----------------|--------|---------------|---------------------|
| Detection | Project state | root | repository | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | None | None |
| Health | API readiness | `backend` | isolated production Compose | container health plus Python request to `/api/v1/utils/health/` | PASS | None | None |
| Health | Nginx health | `frontend` | isolated production Compose | container health plus backend-network request to `/health` | PASS | None | None |
| Security | Authentication rate limit | `backend` | production-mode Uvicorn on `127.0.0.1:8016` | six rapid form POSTs to `/api/v1/login/access-token` | PASS: sixth response 429 | Supplied isolated production-safe configuration | None |
| Backup | Complete durable-state bundle | root | isolated production Compose | `BACKUP_RETENTION_DAYS=7 ./scripts/backup-local-state.sh <isolated-directory>` | PASS | Pinned base Compose file after the first command inherited the dev override | None |
| Backup | Destructive restore drill | root | isolated production Compose | confirmed `restore-local-state.sh`, then database and file sanity checks | PASS | None | None |
| Deploy | Image rollback | root | isolated production Compose | `scripts/deploy-rollback.sh` with reviewed image IDs | PASS | None | None |
| Deploy | Persistence and post-rollback probes | root | isolated production Compose | image-ID, DB-container, state-volume, API, and frontend checks | PASS | Corrected a diagnostic command because the minimal Nginx image intentionally has no `wget` | None |

## Known Issues

The Skipped Infra registry remains empty. The target is the real repository
deployment scope, all configured components passed, and no external setup is
required. GitHub Actions billing remains a pipeline-only external condition
and does not prevent local deployment, backup, restore, or rollback.

## Handoff

`infra -> carryforward` is the required Phase Transition handoff.
`documents` follows `carryforward`; session planning resumes only after
`phasebuild` creates Phase 05.

**Next command:** `carryforward`

**Reason:** Health, Security, Backup, and Deploy all pass against the complete
local deployment target with no infrastructure exception or external setup
remaining.
