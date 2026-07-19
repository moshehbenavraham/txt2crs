# Phase Transition Infrastructure Report

**Date:** 2026-07-19
**Result:** PASS
**Selected bundle:** Health
**Platform:** Repository-root Docker Compose
**Scope:** Local-only backend-shell and frontend topology

## Scope Decision

Local Docker is the complete deployment scope for txt2crs. The inherited
hosted-platform assumption was incorrect and has been superseded by ADR-0008.
The repository does not carry or require hosted deployment credentials,
domains, workflows, or production probes.

## Detection

The repository is a monorepo with two local images. The FastAPI shell hosts the
reusable `txt2crs` engine, so the engine does not need an independent service
probe. The React frontend ships as a separate Nginx image. PostgreSQL and the
private engine-state volume are shared backend infrastructure.

The backend already exposed readiness and liveness endpoints and its image
declared a readiness probe. The frontend served normal routes but had neither
a machine-readable endpoint nor an image health check. Health was therefore
the highest incomplete infrastructure bundle.

## Changes

1. Added Nginx `GET /health`, returning
   `{"status":"healthy","service":"frontend"}` without loading React.
2. Added an internal Docker health check with a 30-second interval.
3. Corrected the frontend Dockerfile's self-referential `VITE_API_URL` build
   argument after BuildKit identified it during validation.
4. Documented both local health paths and destructive-volume warnings.
5. Added static regressions that reject active hosted deployment automation
   and platform-specific variables.
6. Removed inherited hosted deployment workflows and platform tooling.

## Evidence Ledger

| Bundle | Component | Package | Validation target / command | Result | Fixes applied |
|--------|-----------|---------|-----------------------------|--------|---------------|
| Health | Nginx endpoint contract | frontend | `npx vitest run src/lib/securityHeaders.test.ts` | PASS: 5 | Added endpoint, image check, build-argument, and local policy regressions |
| Health | Production-like image build | frontend | `docker build --build-arg VITE_API_URL=http://backend:8000 frontend` | PASS, no BuildKit warnings | Removed undefined build-argument self-default |
| Health | Frontend image probe | frontend | Docker health plus `curl -f http://127.0.0.1:15184/health` | PASS: healthy JSON | Added Docker `HEALTHCHECK` |
| Health | Backend readiness | backend-shell | `curl -f http://127.0.0.1:18013/api/v1/utils/health/` in isolated Compose | PASS: application and PostgreSQL healthy, version 0.3.3 | None |
| Health | Full local topology | root | Isolated `docker compose ... up --detach --build --wait backend frontend` | PASS: database, backend, and frontend healthy | Frontend now participates in `--wait` |
| Scope | Hosted automation absence | backend-shell | `test_container_contract.py` | PASS after inherited deployment files and variables were removed | Added permanent local-only contract |
| Cleanup | Isolated resources | root | Matching `docker compose down --volumes --remove-orphans` and resource filters | PASS: no audit containers or volumes remain | None |

## Remaining Infrastructure Work

No hosted infrastructure work belongs to the current project scope. Local
backup and restore validation remains incomplete because the existing
PostgreSQL helper does not also cover private engine state. That is a data
recovery concern, not a reason to add a hosted platform.

## Handoff

`infra -> carryforward` is the required Phase Transition handoff. `documents`
follows `carryforward`; the next implementation session is not planned until
`phasebuild` creates the next phase.

**Next command:** `carryforward`
