# Phase 03 Transition Infrastructure Report

**Date:** 2026-07-20
**Result:** PASS
**Selected bundle:** none - validation and repair only
**Platform:** Repository-root Docker Compose
**Scope:** Local-only backend, frontend, PostgreSQL, and private engine state

## Scope Decision

Repository-root Docker Compose remains the complete deployment scope under
ADR-0008. All four infrastructure concerns are configured for that boundary:

- backend and frontend health probes;
- application rate limiting outside explicit local mode;
- complete local PostgreSQL and private engine-state backup/restore;
- manual Compose release, rollback, and health verification.

A hosted WAF, domain, TLS boundary, remote backup store, and deployment
webhook are outside the approved product scope. Adding them requires a future
owner-approved hosting decision and a new ADR; it is not a skipped current
infrastructure item.

## Deployment Topology

| Package | Role | Deploys independently | Local target |
|---------|------|-----------------------|--------------|
| `backend` | FastAPI API, engine host, serial worker | Yes | One non-root backend container |
| `frontend` | Nginx-served React application | Yes | One frontend container |
| `backend/packages/txt2crs` | Reusable engine library | No | Built into the backend image |

Shared infrastructure is PostgreSQL for users plus one private named volume
for tenant SQLite jobs, artifacts, and Codex-managed credentials.

## Repair Applied

Infrastructure validation invoked the deployment commands exactly as
documented and found that `scripts/deploy-smoke-check.sh` and
`scripts/deploy-rollback.sh` were tracked without executable permission. Both
failed before their safety checks could run.

A failing static regression was added first, then both scripts were changed
from Git mode `100644` to `100755`. The regression now passes, the smoke
command executes successfully, and the rollback helper executes its required
precondition check instead of failing with `Permission denied`.

## Evidence Ledger

| Bundle | Component | Package | Validation Target / Command | Result | Fixes Applied | Remaining / Blocker |
|--------|-----------|---------|-----------------------------|--------|---------------|---------------------|
| Health | Backend readiness | `backend` | isolated production container request to `/api/v1/utils/health/` | PASS: status and PostgreSQL healthy, version `0.3.6` | None | None |
| Health | Frontend health | `frontend` | isolated production Nginx `/health` request and image health state | PASS: `{"status":"healthy","service":"frontend"}` | None | None |
| Security | Finite route limits and RFC 9457 response | `backend` | four focused rate-limit tests covering login, jobs, and system auth | PASS: 6 parameterized cases, including 429 | None | None |
| Security | Environment activation policy | `backend` | `test_rate_limiter_enabled_for_non_local_environments` | PASS: disabled only for exact `local` mode | None | None |
| Backup | Complete backup | shared | isolated `txt2crs-infra3` project plus `backup-local-state.sh` | PASS: PostgreSQL and engine state captured | None | None |
| Backup | Hashes and permissions | shared | `sha256sum --check SHA256SUMS`; `stat`; `find` | PASS: 3 hashes; bundle `0700`; all files `0600` | None | None |
| Backup | Destructive restore | shared | mutate both stores, add stale file, run `restore-local-state.sh` | PASS: original database and file restored; stale file absent | None | None |
| Backup | Post-restore service | `backend` | internal readiness request after destructive restore | PASS: healthy | None | None |
| Deploy | Compose production topology | shared | isolated image build plus `up -d --wait backend frontend` | PASS: database, backend, and frontend healthy; backend UID/GID 1001 | None | None |
| Deploy | Smoke helper | shared | `./scripts/deploy-smoke-check.sh` against local backend/frontend health URLs | PASS | Added executable Git mode and regression test | None |
| Deploy | Rollback safety | shared | execute `./scripts/deploy-rollback.sh` without required capture variables | PASS: refused safely with `STACK_NAME is required` | Added executable Git mode | None |
| Contracts | Deployment and backup scripts | `backend/tests/scripts` | focused Ruff plus static contract suite | PASS: 19 | Added direct-execution regression | None |
| Cleanup | Disposable proof resources | root | project container, volume, network, image, and bundle inspection after cleanup | PASS: none remain | None | None |

## Backup And Recovery Result

The proof created an owner-only bundle from a fresh isolated Compose project.
Before backup, PostgreSQL and the engine volume received distinct `original`
markers. Both were changed after backup, and a stale engine file was added.
Restore:

- verified all three SHA-256 entries before destructive work;
- parsed the PostgreSQL and engine archives before replacement;
- restored the database marker to `original`;
- restored the engine marker to `original`;
- removed the stale file; and
- returned the backend to healthy state.

The proof bundle and every isolated container, network, volume, and image tag
were removed after validation.

## Security Boundary

The local development profile intentionally disables rate limiting for test
speed. Focused tests explicitly enabled the limiter and proved that repeated
login, job-submission, and privileged-authentication requests reach the
centralized RFC 9457 `429` contract. Non-local environment defaults keep the
limiter enabled.

There is no public edge in the accepted deployment topology, so a hosted WAF
would be fictitious infrastructure rather than a missing current control.

## Required External Setup

None for the approved local-only deployment target. No new secret, hosted
account, webhook, or platform configuration is required.

## Handoff

`infra -> carryforward` is the required Phase Transition handoff. `documents`
follows `carryforward`; Phase 04 planning begins only after `phasebuild`.

**Next command:** `carryforward`

**Reason:** every infrastructure component in the approved target passes
current health, security, backup/restore, deployment, rollback-safety, and
cleanup validation.
