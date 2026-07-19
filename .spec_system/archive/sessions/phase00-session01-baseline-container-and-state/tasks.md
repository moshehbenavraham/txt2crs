# Task Checklist

**Session ID**: `phase00-session01-baseline-container-and-state`
**Total Tasks**: 21
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0001]` session ref; `TNNN` task ID.

---

## Setup (3 tasks)

- [x] T001 [S0001] Record the pre-change engine import, Dockerfile, Compose, settings, and branding baseline (`backend/Dockerfile`, `docker-compose.yml`, `backend/app/core/config.py`, `frontend/src/routes/`)
- [x] T002 [S0001] Write failing typed path-default and confinement tests, including relative, escaping, symlink, overlap, and custom-root cases (`backend/tests/core/test_txt2crs_settings.py`)
- [x] T003 [S0001] [P] Write failing install-order, non-root, one-process, state-volume, environment, and unpublished-port contract tests (`backend/tests/scripts/test_container_contract.py`)

---

## Foundation (5 tasks)

- [x] T004 [S0001] Copy workspace packages before the first uv sync in every backend build path (`backend/Dockerfile`)
- [x] T005 [S0001] Create the fixed non-root runtime user and owner-only state/worker directories in both image targets (`backend/Dockerfile`)
- [x] T006 [S0001] Replace four-worker defaults with one explicit FastAPI process while preserving the one-process reload override (`backend/Dockerfile`, `docker-compose.override.yml`)
- [x] T007 [S0001] Add typed txt2crs state, job database, artifact, Codex home, and worker-root fields with custom-root default derivation (`backend/app/core/config.py`)
- [x] T008 [S0001] Enforce normalized absolute paths, persistent-child confinement, distinct boundaries, and symlink rejection at startup (`backend/app/core/config.py`)

---

## Implementation (8 tasks)

- [x] T009 [S0001] Document truthful txt2crs image, stack, project, and filesystem defaults without adding secrets (`.env.example`, `backend/.env.example`)
- [x] T010 [S0001] Pass explicit engine paths to prestart and backend services and mount one named persistent state volume separate from PostgreSQL (`docker-compose.yml`)
- [x] T011 [S0001] Preserve the non-root local backend command and replace the donor OpenTelemetry service-name fallback (`docker-compose.override.yml`)
- [x] T012 [S0001] [P] Write the shared product-name and page-title helper plus failing-first unit coverage (`frontend/src/lib/branding.test.ts`, `frontend/src/lib/branding.ts`)
- [x] T013 [S0001] Replace donor document titles and accessible product naming while preserving existing routes and temporary assets (`frontend/index.html`, `frontend/src/components/Common/Logo.tsx`, `frontend/src/components/Common/Footer.tsx`, `frontend/src/routes/`)
- [x] T014 [S0001] Add deterministic settings and container contract tests to repository validation (`scripts/validate-changes.sh`)
- [x] T015 [S0001] Build a cleanup-safe production runtime smoke for engine import, non-root identity, owner-only state, and volume reopen (`scripts/verify-production-baseline.sh`)
- [x] T016 [S0001] Run focused tests and repair implementation defects without weakening their safety assertions (`backend/tests/core/test_txt2crs_settings.py`, `backend/tests/scripts/test_container_contract.py`, `frontend/src/lib/branding.test.ts`)

---

## Testing (5 tasks)

- [x] T017 [S0001] Run backend Ruff, strict mypy, and deterministic focused pytest checks (`scripts/validate-changes.sh backend`)
- [x] T018 [S0001] [P] Run engine Ruff, mypy, pytest, and package build checks (`backend/packages/txt2crs/pyproject.toml`)
- [x] T019 [S0001] [P] Run frontend Biome, TypeScript, unit tests, and production build checks (`frontend/package.json`)
- [x] T020 [S0001] Render Compose configuration, execute the production-image baseline smoke, and run existing login/signup/item smoke tests when PostgreSQL is available (`docker-compose.yml`, `scripts/verify-production-baseline.sh`, `backend/tests/api/routes/`)
- [x] T021 [S0001] Validate ASCII/LF requirements and record task-by-task decisions plus exact verification evidence (`.spec_system/specs/phase00-session01-baseline-container-and-state/implementation-notes.md`)

---

## Completion Checklist

- [x] All tasks marked `[x]`.
- [x] All tests and checks passing.
- [x] All session-authored files ASCII-encoded with LF line endings.
- [x] `implementation-notes.md` updated.
- [x] Ready for `creview` (next step in the implement -> creview -> validate sequence).
