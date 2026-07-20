# Phase 05 Transition Infrastructure Report

**Date:** 2026-07-20
**Base revision:** `8f598900b99ff88135fde453d3fccf93c019ab0e`
**Result:** PASS
**Selected bundle:** none - validation and repair only
**Deployment target:** isolated repository-root Docker Compose

## Detection And Topology

`bash .spec_system/scripts/analyze-project.sh --json` reported a mixed
Python/TypeScript monorepo with all eighteen sessions and Phases 00 through 05
complete. The repository has three registered packages:

- `backend-shell` is a deployable FastAPI API and engine host;
- `frontend` is a deployable Nginx static application; and
- `txt2crs-engine` is a reusable library built into the backend rather than an
  independently deployed service.

PostgreSQL and the private `txt2crs-state` volume are shared durable
infrastructure. ADR-0008 defines repository-root Docker Compose as the complete
deployment scope, so there is no hosted environment, public edge, WAF,
platform webhook, or deferred production target.

All four infrastructure bundles were already configured. This run validated
each bundle against fresh disposable resources and repaired one real backup
failure found only after the Codex runtime had initialized its private home.

## Isolated Target

The main validation target used:

- Compose project `txt2crs-phase05-infra`;
- reviewed backend image
  `sha256:9b503211b88d815e865545da595ef41a29a7d2f1abacfce4014b70144af80b4e`;
- reviewed frontend image
  `sha256:176e1fda3ded30ab070641d2d7a30c8aaab48d1bcf22c7ad562e8b5e23f143d9`;
- isolated Compose-prefixed PostgreSQL and private-state volumes; and
- no published host ports.

The mutable local `latest` tags initially resolved to older images, so they
were rejected as evidence. The stack was recreated with the exact reviewed
image IDs before any bundle was accepted. Every disposable container, network,
volume, and temporary backup was removed after validation; unrelated running
projects were not modified.

## Health Bundle

The backend container probe and an in-container request to
`/api/v1/utils/health/` both passed. The response reported HTTP 200,
`status=healthy`, and `database=healthy`. Its `0.3.6` version is the FastAPI
shell's intentionally independent implementation version; the declared
repository and engine release remains `1.0.0` as required by the adopted Phase
05 release-surface policy.

The frontend container probe and a request over the isolated backend network
to `/health` both passed with:

```json
{"service":"frontend","status":"healthy"}
```

PostgreSQL, prestart migrations, the backend, and the frontend reached their
authored production states on the exact reviewed images.

## Security Bundle

A second disposable topology used:

- `ENVIRONMENT=production`;
- generated validation-only signing, database, and initial-user values;
- a fresh PostgreSQL 18 database and private engine-state volume;
- public signup and private development routes disabled; and
- research disabled so no provider call or real credential was required.

After migrations and initial data completed, six rapid invalid login requests
returned:

```text
401 401 401 401 401 429
```

The final response was RFC 9457 Problem Details with status `429`, code
`RATE_5001`, title `Rate Limit Exceeded`, and a trace ID. The production server
also emitted the required `rate_limit.request_rejected` structured event.

No WAF is configured because the accepted deployment has no hosted or public
edge. This is an intentional topology fact, not a deferred component.

## Backup Bundle

The first backup attempt exposed an actual release defect. A started Codex
runtime creates absolute executable links under
`codex-home/tmp/arg0/<runtime>/`. Those image-specific process-scratch links
caused the safe archive helper to reject the otherwise valid private-state
volume.

The repair was tests-first:

1. add a failing regression that combines durable `codex-home/auth.json` data
   with the same absolute scratch-link shape;
2. omit only `codex-home/tmp` from durable-state archives;
3. continue rejecting every symlink elsewhere in the state root; and
4. prove archive validation and restore preserve the durable Codex data.

The focused backup suite passed all seven tests, and the complete backend
suite passed all 518 tests at 88% coverage on migrated PostgreSQL 18. The live
drill then inserted one PostgreSQL probe and one private engine-state probe and
ran:

```text
BACKUP_RETENTION_DAYS=7 ./scripts/backup-local-state.sh <isolated-directory>
```

The bundle directory was mode `0700`; `postgres.dump`,
`engine-state.tar.gz`, `manifest.json`, and `SHA256SUMS` were mode `0600`.
The PostgreSQL catalog, safe-tar validator, and every recorded SHA-256 digest
passed.

After both probes were deliberately deleted, the drill ran:

```text
TXT2CRS_RESTORE_CONFIRM=replace-local-state \
  ./scripts/restore-local-state.sh <verified-bundle>
```

Restore recovered exactly:

- PostgreSQL: `database-roundtrip-ok`; and
- private engine state: `engine-roundtrip-ok`.

The PostgreSQL container identity and `txt2crs-state` volume name remained
unchanged, and both application health endpoints passed after restore.

## Deploy And Rollback Bundle

The deploy test performed a real application-tier transition:

1. replace the reviewed images with backend
   `sha256:c9933b7091617355fa271833bc9a40ec5dde79c18fa29727bdf1f80c30dd03b2`
   and frontend
   `sha256:a37f5471fad43754486e192bed261b0c90df3157c3ab0630a6c36a43783798ca`;
2. verify the replacement containers used those exact IDs and retained a
   private-state probe;
3. run `scripts/deploy-rollback.sh` with the reviewed image IDs; and
4. wait for and inspect both post-rollback health states.

The rollback restored the exact reviewed backend and frontend IDs. PostgreSQL
kept the same container, the engine kept the same named volume, the synthetic
private-state probe survived both transitions, and both health responses
passed. Data rollback remains a separate explicit backup restore operation.

## Evidence Ledger

| Bundle | Component | Package | Validation Target | Command / Check | Result | Fixes Applied | Remaining / Blocker |
|--------|-----------|---------|-------------------|-----------------|--------|---------------|---------------------|
| Detection | Project state | root | repository | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | None | None |
| Health | API readiness | `backend` | exact reviewed image in isolated Compose | container health plus request to `/api/v1/utils/health/` | PASS | Rejected stale mutable `latest` tag and pinned reviewed ID | None |
| Health | Nginx health | `frontend` | exact reviewed image in isolated Compose | container health plus request to `/health` | PASS | Rejected stale mutable `latest` tag and pinned reviewed ID | None |
| Security | Authentication rate limit | `backend` | disposable production-mode topology | six rapid form POSTs to `/api/v1/login/access-token` | PASS: sixth response `429`/`RATE_5001` | Used isolated non-default validation values and fresh PostgreSQL | None |
| Backup | Durable-state bundle | root | initialized isolated Compose state | `backup-local-state.sh` plus permissions, catalog, archive, and checksum checks | PASS after repair | Omit regenerable `codex-home/tmp`; retain fail-closed handling elsewhere | None |
| Backup | Destructive restore drill | root | initialized isolated Compose state | confirmed `restore-local-state.sh`, then exact database and file reads | PASS | None | None |
| Deploy | Image replacement and rollback | root | isolated Compose application tier | alternate-image replacement followed by `deploy-rollback.sh` | PASS | None | None |
| Deploy | Persistence and post-rollback probes | root | isolated Compose application tier | image IDs, DB identity, volume identity, state marker, and health | PASS | None | None |
| Cleanup | Disposable resources | root | local Docker | project down with volumes plus residue queries | PASS | None | None |

## Known Issues

The Skipped Infra registry remains empty. The real local deployment target has
working health, production throttling, complete durable-state backup/restore,
and image rollback. GitHub Actions billing remains a pipeline-only external
condition and does not prevent local operation.

## Handoff

`infra -> carryforward` is the required Phase Transition handoff.
`documents` follows `carryforward`. There is no unfinished phase to create
after documentation reconciliation.

**Next command:** `carryforward`

**Reason:** All four configured bundles pass against the complete deployment
scope, the discovered authenticated-state backup defect is repaired and
regression-tested, and no infrastructure exception or external setup remains.
