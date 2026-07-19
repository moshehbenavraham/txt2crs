# Task Checklist

**Session ID**: `phase02-session04-system-readiness-and-auth-api`
**Total Tasks**: 25
**Estimated Duration**: 3.5-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0204]` session ref; `TNNN` task ID.

---

## Setup (2 tasks)

- [x] T001 [S0204] Verify Sessions 01-03 lifecycle, worker, cache, runtime,
  public facade, error, and authorization prerequisites
  (`.spec_system/specs/phase02-session04-system-readiness-and-auth-api/spec.md`)
- [x] T002 [S0204] Inspect package authentication state/completion, slowapi,
  RFC 9457, API schema, app-state dependency, and generated-client seams
  (`backend/packages/txt2crs/src/txt2crs/ai/system_authentication.py`)

---

## Tests-First Foundation (9 tasks)

- [x] T003 [S0204] [P] Write public export tests for safe authentication state,
  snapshot, and error contracts
  (`backend/packages/txt2crs/tests/unit/test_public_package_exports.py`)
- [x] T004 [S0204] [P] Write exact monitor/shutdown settings defaults and
  invalid-bound tests (`backend/tests/core/test_txt2crs_settings.py`)
- [x] T005 [S0204] Write coordinator initial refresh, immutable snapshot,
  start, waiting replay, authenticated replay, and no-overlap tests
  (`backend/tests/services/test_txt2crs_authentication.py`)
- [x] T006 [S0204] Write terminal release, package failure, thread failure,
  repeated close, active close, and safe event regressions
  (`backend/tests/services/test_txt2crs_authentication.py`)
- [x] T007 [S0204] [P] Write strict readiness and device-auth schema allowlist,
  bounds, URL/code, cross-state, timezone, and unknown-field tests
  (`backend/tests/schemas/test_system_schemas.py`)
- [x] T008 [S0204] Write authenticated readiness route tests proving exact
  projection and zero coordinator refresh/package side effects
  (`backend/tests/api/routes/test_system.py`)
- [x] T009 [S0204] Write device-auth route tests for missing/normal/superuser,
  start/status replay, unavailable, busy, package failure, RFC 9457, and rate
  limits (`backend/tests/api/routes/test_system.py`)
- [x] T010 [S0204] Extend lifespan tests for auth construction, initial
  refresh, state exposure, partial startup, and reverse cleanup
  (`backend/tests/test_txt2crs_lifespan.py`)
- [x] T011 [S0204] Add OpenAPI/client contract tests for route IDs, auth,
  response schemas, safe fields, and no request body
  (`backend/tests/scripts/test_generate_client_contract.py`)

---

## Implementation (10 tasks)

- [x] T012 [S0204] Export the facade's safe authentication contracts through
  `txt2crs.application`
  (`backend/packages/txt2crs/src/txt2crs/application/__init__.py`)
- [x] T013 [S0204] Add finite authentication monitor and shutdown settings and
  document both names (`backend/app/core/config.py`, `backend/.env.example`)
- [x] T014 [S0204] Implement immutable cached auth state, protocols, finite
  service errors, and initial persisted-account refresh
  (`backend/app/services/txt2crs_authentication.py`)
- [x] T015 [S0204] Implement replay-safe start, retained runtime lease,
  in-memory status monitor, exact terminal release, and idempotent close
  (`backend/app/services/txt2crs_authentication.py`)
- [x] T016 [S0204] Implement strict readiness/auth HTTP projections and
  state-dependent URL/code validation (`backend/app/schemas/system.py`)
- [x] T017 [S0204] Add fail-closed lifespan service dependencies without
  import-time app-state access (`backend/app/api/deps.py`)
- [x] T018 [S0204] Add/register readiness and auth routes with authentication,
  superuser authorization, finite rate limits, and safe structured events
  (`backend/app/api/routes/system.py`, `backend/app/api/main.py`)
- [x] T019 [S0204] Add `SYSTEM_AUTH_FAILED`, status mapping, and central
  context-free package auth translation
  (`backend/app/core/constants.py`, `backend/app/core/txt2crs_errors.py`)
- [x] T020 [S0204] Wire authentication construction/start/state/cleanup through
  FastAPI lifespan and export the service (`backend/app/main.py`, `backend/app/services/__init__.py`)
- [x] T021 [S0204] Document route safety and CLI recovery, then regenerate and
  format OpenAPI plus the TypeScript client (`scripts/generate-client.sh`)

---

## Testing And Completion (4 tasks)

- [x] T022 [S0204] Run focused engine export and shell service/schema/route/
  dependency/settings/error/lifespan tests
- [x] T023 [S0204] Run complete deterministic backend shell and engine suites
  (`backend/tests/`, `backend/packages/txt2crs/tests/`)
- [x] T024 [S0204] Run client generation, frontend checks, Ruff format/check,
  strict mypy, ty, and repository pre-commit
- [x] T025 [S0204] Verify route/log/error allowlists, cache-only reads, public
  imports, clean generated state, ASCII/LF, then record exact evidence
  (`.spec_system/specs/phase02-session04-system-readiness-and-auth-api/implementation-notes.md`)

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] `implementation-notes.md` updated
- [x] Ready for `creview` (next step in the implement -> creview -> validate sequence)

---

## Next Steps

Run the `implement` workflow step.
