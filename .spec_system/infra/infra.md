# Phase 02 Transition Infrastructure Report

**Date:** 2026-07-19
**Result:** PASS
**Selected bundle:** none - validation only
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
webhook are not part of the approved product scope. Adding them would violate
ADR-0008 and requires a future owner-approved hosting decision and new ADR.
No skipped-infrastructure entry is therefore appropriate.

## Deployment Topology

| Package | Role | Deploys independently | Local target |
|---------|------|-----------------------|--------------|
| `backend` | FastAPI API, engine host, serial worker | Yes | One non-root backend container |
| `frontend` | Nginx-served React application | Yes | One frontend container |
| `backend/packages/txt2crs` | Reusable engine library | No | Built into the backend image |

Shared infrastructure is PostgreSQL for users plus one private named volume
for tenant SQLite jobs, artifacts, and Codex-managed credentials.

## Evidence Ledger

| Bundle | Component | Package | Validation target / command | Result | Fixes Applied | Remaining / Blocker |
|--------|-----------|---------|-----------------------------|--------|---------------|---------------------|
| Health | Backend readiness | `backend` | isolated container request to `/api/v1/utils/health/` | PASS: `healthy`, PostgreSQL ready | None | None |
| Health | Frontend health | `frontend` | isolated container `curl http://127.0.0.1/health` | PASS: `healthy` | None | None |
| Security | Finite route limits and RFC 9457 response | `backend` | focused login/system rapid-request tests | PASS: 2 | None | None |
| Security | Environment activation policy | `backend` | complete shell suite security-default tests | PASS: enabled outside explicit `local` | None | None |
| Backup | Complete backup | shared | isolated `txt2crs_infra` project plus `backup-local-state.sh` | PASS: PostgreSQL and engine state captured | None | None |
| Backup | Hashes and permissions | shared | `sha256sum --check SHA256SUMS`; `stat`; `find` | PASS: 3 hashes; bundle `0700`; all files `0600` | None | None |
| Backup | Destructive restore | shared | mutate both stores, add stale file, run `restore-local-state.sh` | PASS: original database and file restored; stale file absent | None | None |
| Backup | Post-restore service | shared | backend and frontend internal health requests | PASS: both healthy | None | None |
| Deploy | Compose topology | shared | `docker compose config --quiet` and isolated `up -d --wait backend frontend` | PASS: one healthy backend and frontend | None | None |
| Cleanup | Disposable proof resources | root | Compose project container, volume, and network inspection after `down -v` | PASS: none remain | None | None |

## Backup And Recovery Result

The proof created one owner-only bundle from a fresh isolated project. Before
backup, PostgreSQL and the engine volume received distinct `original` markers.
Both were changed after backup, and a stale engine file was added. Restore:

- verified all three SHA-256 entries before destructive work;
- parsed the PostgreSQL and engine archives before replacement;
- restored the database marker to `original`;
- restored the engine marker to `original`;
- removed the stale file; and
- returned both deployable services to healthy state.

The proof bundle and every isolated container, network, volume, and temporary
file were removed after validation.

## Security Boundary

The local development profile intentionally disables rate limiting for test
speed. Focused tests explicitly enable the limiter and proved that repeated
login and privileged authentication requests return the centralized RFC 9457
`429` contract. Non-local environment defaults keep the limiter enabled.

There is no public edge in the accepted deployment topology, so a hosted WAF
would be fictitious infrastructure rather than a missing current control.

## Handoff

`infra -> carryforward` is the required Phase Transition handoff. `documents`
follows `carryforward`; Phase 03 planning begins only after `phasebuild`.

**Next command:** `carryforward`
**Reason:** every infrastructure component in the approved local-only target
passes current health, security, backup/restore, and cleanup validation.
