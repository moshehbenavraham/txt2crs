# Task Checklist

**Session ID**: `phase02-session02-serial-worker-supervisor`
**Total Tasks**: 25
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[SNNMM]` session ref; `TNNN` task ID.

---

## Setup (2 tasks)

- [x] T001 [S0202] Verify the validated facade prerequisites and capture the
  pre-session baseline (`.spec_system/specs/phase02-session02-serial-worker-supervisor/spec.md`)
- [x] T002 [S0202] Inspect public runnable ordering, executor ownership, and
  FastAPI lifespan seams (`backend/packages/txt2crs/src/txt2crs/application/facade.py`)

---

## Tests-First Foundation (9 tasks)

- [x] T003 [S0202] [P] Write finite poll and shutdown setting regressions,
  including zero and excessive bounds (`backend/tests/core/test_txt2crs_settings.py`)
- [x] T004 [S0202] [P] Write cancellation-reason first-writer and compatibility
  tests (`backend/packages/txt2crs/tests/unit/test_runtime.py`)
- [x] T005 [S0202] Write executor shutdown-interruption tests with no duplicate
  trigger while execution is in flight (`backend/packages/txt2crs/tests/unit/test_application_facade.py`)
- [x] T006 [S0202] Write a real job-executor regression proving process
  interruption remains durable and runnable (`backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`)
- [x] T007 [S0202] [P] Write immediate startup recovery, periodic poll, and
  nudge tests with event barriers (`backend/tests/services/test_txt2crs_worker.py`)
- [x] T008 [S0202] Write serial execution and no-overlap tests for multiple
  facade-selected jobs (`backend/tests/services/test_txt2crs_worker.py`)
- [x] T009 [S0202] Write discovery, creation, execution, and cleanup failure
  tests with bounded retry and safe failure codes (`backend/tests/services/test_txt2crs_worker.py`)
- [x] T010 [S0202] Write snapshot, repeated lifecycle, drain, timeout, and
  restart-safe interruption tests (`backend/tests/services/test_txt2crs_worker.py`)
- [x] T011 [S0202] Write configured, unconfigured, partial-startup, request
  failure, and reverse-cleanup lifespan tests (`backend/tests/test_txt2crs_lifespan.py`)

---

## Implementation (10 tasks)

- [x] T012 [S0202] Add bounded worker poll and shutdown settings
  (`backend/app/core/config.py`)
- [x] T013 [S0202] Document both finite worker settings
  (`backend/.env.example`)
- [x] T014 [S0202] Implement explicit user-cancellation and
  process-interruption reasons (`backend/packages/txt2crs/src/txt2crs/ai/runtime.py`)
- [x] T015 [S0202] Preserve the durable non-terminal checkpoint on process
  interruption (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`)
- [x] T016 [S0202] Add one non-blocking restart-safe executor interruption
  method with idempotent close (`backend/packages/txt2crs/src/txt2crs/application/facade.py`)
- [x] T017 [S0202] Create immutable safe worker status, failure, snapshot, and
  public-facade protocols (`backend/app/services/txt2crs_worker.py`)
- [x] T018 [S0202] Implement immediate durable discovery and one-at-a-time
  executor ownership with cleanup on every scope exit
  (`backend/app/services/txt2crs_worker.py`)
- [x] T019 [S0202] Implement event nudges, finite polling, safe retry reason
  codes, and no private exception retention (`backend/app/services/txt2crs_worker.py`)
- [x] T020 [S0202] Implement stop-before-claim, bounded drain, restart-safe
  interruption, and idempotent terminal close (`backend/app/services/txt2crs_worker.py`)
- [x] T021 [S0202] Wire configured-only worker creation and reverse-order
  cleanup, then export the service (`backend/app/main.py`, `backend/app/services/__init__.py`)

---

## Testing And Completion (4 tasks)

- [x] T022 [S0202] Run focused worker, settings, lifespan, runtime, facade, and
  executor tests (`backend/tests/services/test_txt2crs_worker.py`)
- [x] T023 [S0202] Run complete deterministic backend shell and engine suites
  (`backend/tests/`, `backend/packages/txt2crs/tests/`)
- [x] T024 [S0202] Run Ruff format/check plus strict mypy, ty, and repository
  pre-commit gates (`backend/pyproject.toml`, `.pre-commit-config.yaml`)
- [x] T025 [S0202] Verify ASCII/LF, update task evidence, and record exact
  implementation results (`.spec_system/specs/phase02-session02-serial-worker-supervisor/implementation-notes.md`)

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
