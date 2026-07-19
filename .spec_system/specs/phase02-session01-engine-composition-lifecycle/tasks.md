# Task Checklist

**Session ID**: `phase02-session01-engine-composition-lifecycle`
**Total Tasks**: 24
**Estimated Duration**: 3.5-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0201]` session ref; `TNNN` task ID.

---

## Setup (2 tasks)

- [ ] T001 [S0201] Verify the Phase 01 public application exports and record the backend baseline checks (`backend/packages/txt2crs/src/txt2crs/application/__init__.py`, `backend/pyproject.toml`)
- [ ] T002 [S0201] Create the service-test package before adding composition cases (`backend/tests/services/__init__.py`)

---

## Tests First (5 tasks)

- [ ] T003 [S0201] [P] Extend settings tests for exact P0 defaults, bounded overrides, GPT-5.6 rejection, optional Tavily absence, and cleared inherited environment (`backend/tests/core/test_txt2crs_settings.py`)
- [ ] T004 [S0201] [P] Write exact public configuration translation and public-import boundary tests (`backend/tests/services/test_txt2crs_application.py`)
- [ ] T005 [S0201] Add recording-factory tests for configured creation, unconfigured no-op, idempotent close, factory failure, and close failure with cleanup on scope exit for all acquired resources (`backend/tests/services/test_txt2crs_application.py`)
- [ ] T006 [S0201] Write FastAPI lifespan tests for configured, unconfigured, sequential, and partial-startup states while preserving existing route behavior with cleanup on scope exit for all acquired resources (`backend/tests/test_txt2crs_lifespan.py`)
- [ ] T007 [S0201] Run the new focused tests and record the expected pre-implementation failures (`backend/tests/core/test_txt2crs_settings.py`, `backend/tests/services/test_txt2crs_application.py`, `backend/tests/test_txt2crs_lifespan.py`)

---

## Foundation (5 tasks)

- [ ] T008 [S0201] Add grouped typed settings for model, research, MCP, storage retention, retry, input, run, and admission limits (`backend/app/core/config.py`)
- [ ] T009 [S0201] Validate finite ranges, cross-field budgets, GPT-5.6 family values, loopback topology, and optional external secret normalization at settings construction (`backend/app/core/config.py`)
- [ ] T010 [S0201] Implement one detached P0 `ExecutionProfile` builder from the validated shell settings (`backend/app/services/txt2crs_application.py`)
- [ ] T011 [S0201] Implement storage, admission, and real application configuration translation using only public package contracts (`backend/app/services/txt2crs_application.py`)
- [ ] T012 [S0201] Define the coarse configured/unconfigured lifecycle state and injectable public factory protocols (`backend/app/services/txt2crs_application.py`)

---

## Implementation (6 tasks)

- [ ] T013 [S0201] Implement configured facade creation and safe unconfigured startup without a synthetic secret (`backend/app/services/txt2crs_application.py`)
- [ ] T014 [S0201] Implement idempotent lifecycle close and partial-startup cleanup without masking the primary construction failure (`backend/app/services/txt2crs_application.py`)
- [ ] T015 [S0201] Add structured composition startup, unconfigured, completion, shutdown, and failure events with approved coarse fields only (`backend/app/services/txt2crs_application.py`)
- [ ] T016 [S0201] Export the documented shell composition service without exporting engine internals (`backend/app/services/__init__.py`)
- [ ] T017 [S0201] Add an injectable FastAPI lifespan owner that stores only the shell lifecycle service on application state (`backend/app/main.py`)
- [ ] T018 [S0201] Preserve middleware, exception handlers, router registration, telemetry, limiter, and the exported global application while enabling isolated lifespan tests (`backend/app/main.py`)

---

## Operator Configuration (1 task)

- [ ] T019 [S0201] Document every new finite setting and blank Tavily secret without committing credentials (`backend/.env.example`)

---

## Testing And Completion (5 tasks)

- [ ] T020 [S0201] Format and lint the changed backend Python files (`backend/pyproject.toml`)
- [ ] T021 [S0201] Run the focused settings, composition-service, and lifespan tests to green (`backend/tests/core/test_txt2crs_settings.py`, `backend/tests/services/test_txt2crs_application.py`, `backend/tests/test_txt2crs_lifespan.py`)
- [ ] T022 [S0201] Run the complete deterministic backend test suite (`backend/tests/`)
- [ ] T023 [S0201] Run backend mypy and ty checks for the new public-boundary types (`backend/app/`)
- [ ] T024 [S0201] Verify ASCII, Unix LF, diff cleanliness, and no private txt2crs imports in shell code (`backend/app/services/txt2crs_application.py`, `backend/app/main.py`, `backend/tests/services/test_txt2crs_application.py`, `backend/tests/test_txt2crs_lifespan.py`)

---

## Completion Checklist

- [ ] All tasks marked `[x]`
- [ ] All tests and checks passing
- [ ] All files ASCII-encoded with LF line endings
- [ ] implementation-notes.md updated
- [ ] Ready for `creview` (next step in the implement -> creview -> validate sequence)

---

## Next Steps

Run the `implement` workflow step.
