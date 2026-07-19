# Session 01: Baseline Container and State

**Session ID**: `phase00-session01-baseline-container-and-state`
**Packages**: backend-shell, txt2crs-engine, frontend
**Status**: Complete
**Estimated Tasks**: ~12-25
**Estimated Duration**: 2-4 hours

---

## Objective

Establish a production-reproducible application baseline that installs the
workspace engine, runs one non-root backend process, and safely persists all
private engine state under typed configuration.

---

## Scope

### In Scope (MVP)

- Write failing regression tests before changing production configuration.
- Correct backend Docker workspace copy and `uv sync` ordering.
- Assert one Uvicorn process and a non-root runtime user.
- Add a confined private state root plus SQLite, artifact, and `CODEX_HOME`
  child settings.
- Wire one persistent application-state volume through Docker Compose.
- Rename remaining boilerplate runtime or public UI defaults that contradict
  the txt2crs product identity.
- Preserve current authentication and donor-item smoke behavior.
- Validate the engine, backend, frontend, Compose configuration, and
  production image.

### Out of Scope

- Engine request envelopes, recovery queries, projections, artifacts, policy,
  or runtime factories owned by Phase 01.
- Composition root, readiness, device-code setup, or worker supervision owned
  by Phase 02.
- Jobs routes, donor-item removal, or database migration owned by Phase 03.
- Learner workflow redesign owned by Phase 04.

---

## Prerequisites

- [x] Root, backend, and frontend agent guidance has been reviewed.
- [x] Current production image, Compose, settings, and test behavior has been
  inspected before writing the regression tests.

---

## Deliverables

1. Test-backed backend image installation and single-process topology.
2. Typed, path-confined private engine settings with persistent Compose
   storage.
3. Truthful txt2crs runtime/UI defaults without removing the donor domain.
4. Green baseline validation evidence recorded in the session artifacts.

---

## Success Criteria

- [x] Production image code can import `txt2crs`.
- [x] Container configuration proves one non-root FastAPI process.
- [x] Private engine state survives reopen through the mounted volume.
- [x] Unsafe private-state path configuration fails closed.
- [x] Existing shell authentication and item smoke behavior remains green.
- [x] Required engine, backend, frontend, Compose, and image checks pass.
