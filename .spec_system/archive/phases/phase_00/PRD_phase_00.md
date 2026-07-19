# PRD Phase 00: Application Baseline

**Status**: Complete
**Sessions**: 1 (initial estimate)
**Estimated Duration**: 1 day

**Progress**: 1/1 sessions (100%)

---

## Overview

Turn the imported FastAPI/React shell into a truthful and reproducible base
for composing the reusable `txt2crs` engine. This phase corrects the
production image workspace install, enforces the single-process P0 topology,
adds typed private engine-state paths and persistent storage, and preserves
the existing shell smoke paths until the durable jobs API is ready to replace
the donor `items` domain.

---

## Progress Tracker

| Session | Name | Status | Est. Tasks | Validated |
|---------|------|--------|------------|-----------|
| 01 | Baseline Container and State | Complete | 21 | 2026-07-19 |

---

## Completed Sessions

- Session 01: Baseline Container and State - completed 2026-07-19

---

## Upcoming Sessions

None - Phase 00 is complete.

---

## Objectives

1. Make the production backend image install and import the workspace-owned
   `txt2crs` package reliably.
2. Enforce one non-root FastAPI process and one writable persistent private
   state root for the P0 runtime.
3. Add typed engine settings and regression coverage while keeping the
   existing backend, engine, frontend, and Compose checks green.

---

## Prerequisites

- The imported FastAPI/React shell and workspace-owned `txt2crs` package are
  present.
- The adopted input-to-course implementation plan remains the scope authority.

---

## Planning Assumptions And Resolutions

### Working Assumptions

- Phase 00 fits one implementation session: the adopted plan explicitly
  suggests S01 and confines the work to container installation, topology,
  private state, typed settings, truthful defaults, and regression checks.
- The donor `items` domain remains temporarily: the adopted plan requires its
  removal only after durable jobs acceptance coverage exists in Phase 03.

### Conflict Resolutions

- The master PRD labeled Phase 00 "In Progress" while state tracking reported
  zero sessions and `not_started`. The existing shell is partially imported,
  but no structured Phase 00 session has begun, so phase tracking uses
  "Not Started" until Session 01 starts. The master PRD and state tracking are
  reconciled to that interpretation.

---

## Technical Considerations

### Architecture

- The backend shell owns configuration, lifecycle, HTTP, and identity.
- The engine package remains reusable and must be installed from the uv
  workspace rather than copied or reimplemented in the shell.
- Private engine SQLite state, artifacts, and `CODEX_HOME` live below one
  confined application-owned root mounted from a persistent volume.

### Technologies

- Python 3.14, uv workspace, FastAPI, Pydantic settings, and pytest
- Docker Compose, a multi-stage backend image, and a non-root runtime user
- React 19 and TypeScript smoke validation for renamed public defaults

### Risks

- Workspace install order can produce a host-only success: build and import
  the production image as a regression gate.
- Multiple Uvicorn workers can duplicate the serial engine worker: assert the
  exact one-process container command.
- Misconfigured paths can escape the private root: validate resolved child
  paths and prove the non-root runtime can write and reopen state.

---

## Success Criteria

Phase complete when:

- [x] Session 01 is completed and validated.
- [x] Host and production-container imports of `txt2crs` work.
- [x] The backend image runs one non-root FastAPI worker.
- [x] A non-root process can write and reopen the persistent private state
  volume.
- [x] Typed engine settings reject unsafe or inconsistent private paths.
- [x] Login, signup, and current item smoke coverage still pass.
- [x] Engine, backend, frontend, Compose configuration, and production-image
  validation are green.

---

## Dependencies

### Depends On

- Imported FastAPI/React application shell
- Reusable `backend/packages/txt2crs` workspace package

### Enables

- Phase 01: Engine Application Boundary
