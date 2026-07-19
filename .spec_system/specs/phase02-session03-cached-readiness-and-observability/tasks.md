# Task Checklist

**Session ID**: `phase02-session03-cached-readiness-and-observability`
**Total Tasks**: 25
**Estimated Duration**: 3.5-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0203]` session ref; `TNNN` task ID.

---

## Setup (2 tasks)

- [x] T001 [S0203] Verify Session 01/02 public facade and worker prerequisites
  and record the pre-session baseline (`.spec_system/specs/phase02-session03-cached-readiness-and-observability/spec.md`)
- [x] T002 [S0203] Inspect package-owned provider, storage, artifact, input,
  and admission seams without adding a private shell import
  (`backend/packages/txt2crs/src/txt2crs/application/factories.py`)

---

## Tests-First Foundation (8 tasks)

- [x] T003 [S0203] [P] Write aggregate readiness contract tests for strict
  coarse states, safe bounds, sanitization, GPT-5.6 identity, and deterministic
  behavior (`backend/packages/txt2crs/tests/unit/test_application_readiness.py`)
- [x] T004 [S0203] Write real aggregate inspector tests for provider/research,
  SQLite migration/write rollback, atomic artifact cleanup, inputs, admission,
  and safe partial failure (`backend/packages/txt2crs/tests/unit/test_application_readiness.py`)
- [x] T005 [S0203] [P] Write runtime-owner exclusivity, contention, release,
  repeated close, and content-free snapshot tests
  (`backend/tests/services/test_txt2crs_runtime.py`)
- [x] T006 [S0203] Write readiness cache tests for immediate startup,
  maintenance refresh, stale/contended behavior, worker combination,
  unconfigured recovery, immutability, and bounded close
  (`backend/tests/services/test_txt2crs_readiness.py`)
- [x] T007 [S0203] Write side-effect regressions proving repeated cache reads
  never call the package, provider, MCP, SQLite probe, artifact probe, or
  refresh scheduler (`backend/tests/services/test_txt2crs_readiness.py`)
- [x] T008 [S0203] [P] Write package-exception mapping tests for stable
  `ErrorCode`, status, generic detail, and absent cause/context
  (`backend/tests/core/test_txt2crs_errors.py`)
- [x] T009 [S0203] [P] Write request middleware tests proving logs omit raw
  path, query, client IP, headers, and body while retaining safe method,
  matched route identity, status, and duration
  (`backend/tests/core/test_middleware.py`)
- [x] T010 [S0203] Extend worker, settings, and lifespan tests for shared
  ownership, coordinator ordering, configured/unconfigured state, partial
  startup, and reverse cleanup (`backend/tests/services/test_txt2crs_worker.py`, `backend/tests/core/test_txt2crs_settings.py`, `backend/tests/test_txt2crs_lifespan.py`)

---

## Engine Boundary Implementation (5 tasks)

- [x] T011 [S0203] Define public finite readiness state, check, and aggregate
  contracts with bounded sanitized construction
  (`backend/packages/txt2crs/src/txt2crs/application/readiness.py`)
- [x] T012 [S0203] Add package-internal current-migration, rollback-only
  SQLite writability, conservative admission-capacity, and confined atomic
  artifact probes (`backend/packages/txt2crs/src/txt2crs/jobs/store.py`, `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py`)
- [x] T013 [S0203] Compose deterministic and real aggregate inspectors from
  package-owned resources, configured adapters, provider graph, and default
  reservation (`backend/packages/txt2crs/src/txt2crs/application/factories.py`)
- [x] T014 [S0203] Expose aggregate readiness through the facade and public
  application exports without exposing private collaborators
  (`backend/packages/txt2crs/src/txt2crs/application/facade.py`, `backend/packages/txt2crs/src/txt2crs/application/__init__.py`)
- [x] T015 [S0203] Run focused engine tests and record the package boundary
  evidence (`backend/packages/txt2crs/tests/unit/test_application_readiness.py`)

---

## Shell Implementation (6 tasks)

- [x] T016 [S0203] Implement the finite shared runtime ownership coordinator
  and content-free snapshot (`backend/app/services/txt2crs_runtime.py`)
- [x] T017 [S0203] Hold execution ownership around worker discovery,
  executor execution, and cleanup without retaining job identity in the gate
  (`backend/app/services/txt2crs_worker.py`)
- [x] T018 [S0203] Implement immutable shell readiness models, unconfigured
  setup state, complete acceptance logic, explicit freshness, safe bounds, and
  generic recovery actions (`backend/app/services/txt2crs_readiness.py`)
- [x] T019 [S0203] Implement immediate and periodic non-blocking refresh,
  last-known cache reads, safe structured events, and bounded idempotent close
  (`backend/app/services/txt2crs_readiness.py`)
- [x] T020 [S0203] Add finite readiness settings and wire gate, initial
  readiness, worker, maintenance, and reverse cleanup through FastAPI lifespan
  (`backend/app/core/config.py`, `backend/.env.example`, `backend/app/main.py`, `backend/app/services/__init__.py`)
- [x] T021 [S0203] Add semantic engine/system error codes, central
  context-free package translation, and allowlisted request lifecycle logging
  (`backend/app/core/constants.py`, `backend/app/core/txt2crs_errors.py`, `backend/app/core/middleware.py`)

---

## Testing And Completion (4 tasks)

- [x] T022 [S0203] Run focused engine and shell readiness, ownership, worker,
  settings, middleware, exception, and lifespan tests
- [x] T023 [S0203] Run complete deterministic backend shell and engine suites
  (`backend/tests/`, `backend/packages/txt2crs/tests/`)
- [x] T024 [S0203] Run Ruff format/check, strict mypy, ty, and repository
  pre-commit gates (`backend/pyproject.toml`, `.pre-commit-config.yaml`)
- [x] T025 [S0203] Verify ASCII/LF, safe log fields, public-only shell imports,
  clean probe state, then record exact implementation evidence
  (`.spec_system/specs/phase02-session03-cached-readiness-and-observability/implementation-notes.md`)

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
