# Session 05: Public Facade and Owner Lifecycle

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Package**: backend/packages/txt2crs
**Status**: Not Started
**Estimated Tasks**: ~16-22
**Estimated Duration**: 2-4 hours

---

## Objective

Publish the complete shell-needed engine lifecycle through one documented
application facade with real and deterministic factories plus idempotent owner
purge.

---

## Scope

### In Scope (MVP)

- One public `Txt2CrsApplication` boundary for submit, recover, query,
  artifacts, readiness/auth inspection, runnable discovery, executor creation,
  close, and owner purge.
- Typed real and deterministic-test configuration and factory contracts.
- Composition of existing ingestion, policy, store, research, Codex,
  pipeline, renderer, and artifact implementations behind public APIs.
- Idempotent owner purge across request, job, checkpoint, delivery, and
  artifact data.
- Active-owner, partial-failure, retry, and already-purged behavior.
- Public package exports and package-boundary documentation.
- End-to-end deterministic lifecycle tests with no FastAPI imports.

### Out of Scope

- FastAPI settings translation, routes, lifespan, worker thread, and error
  responses.
- PostgreSQL user deletion coordination.
- Frontend client generation or UI behavior.

---

## Prerequisites

- [ ] Sessions 01-04 public contracts and lifecycle behavior are validated.
- [ ] The existing package import and build contract remains green.

---

## Deliverables

1. Public application facade, configuration, and lifecycle protocols.
2. Real and deterministic factory implementations.
3. Idempotent coordinated owner-purge operation.
4. End-to-end deterministic package integration tests.
5. Updated package exports and public documentation.

---

## Success Criteria

- [ ] Every shell-needed operation is available through documented public
  package methods without importing private engine modules.
- [ ] Real and deterministic factories share typed contracts and build fresh
  job-scoped graphs.
- [ ] Owner purge removes all engine-owned records and artifacts, is safe to
  retry, and never reports success after a partial failure.
- [ ] The engine lifecycle executes without FastAPI, PostgreSQL user models,
  network access, or provider credentials in deterministic tests.
- [ ] Ruff, mypy, pytest, package build, and the explicit live-gated
  compatibility check pass for the completed phase.
