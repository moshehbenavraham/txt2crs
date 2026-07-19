# Session 01: Engine Composition Lifecycle

**Session ID**: `phase02-session01-engine-composition-lifecycle`
**Package**: backend
**Status**: Not Started
**Estimated Tasks**: ~12-25
**Estimated Duration**: 2-4 hours

---

## Objective

Create one tested FastAPI composition service that translates typed shell
settings into the public engine application configuration, owns the facade for
the application lifespan, and closes it safely on every startup outcome.

---

## Scope

### In Scope (MVP)

- Backend settings and configuration translation for the engine facade.
- Application-scoped composition service and FastAPI lifespan ownership.
- Package-owned reviewed research declaration loading with shell-controlled
  secret, timeout, and disable-only values.
- Test-factory injection without private engine imports.
- Reverse-order cleanup for success, shutdown, and partial-startup failure.

### Out of Scope

- Serial job execution and recovery loops.
- Public readiness or device authentication routes.
- Learner job submission endpoints.
- Frontend setup screens.

---

## Prerequisites

- [ ] Phase 01 public facade and real/test factory contracts are available.
- [ ] Single-process backend topology remains enforced.

---

## Deliverables

1. Tests for settings translation, public-boundary imports, lifespan
   construction, and cleanup.
2. Backend engine composition service under `backend/app/services/`.
3. FastAPI lifespan integration with dependency access for later sessions.
4. Structured startup and shutdown events with safe fields.

---

## Success Criteria

- [ ] One facade is created per FastAPI lifespan from typed settings.
- [ ] Shell code imports no private engine modules or generation internals.
- [ ] Missing external credentials still allow OpenAPI and setup surfaces to
  start in a truthful unconfigured state.
- [ ] Partial startup and normal shutdown close all created resources exactly
  once.
- [ ] Backend unit, type, lint, and focused lifecycle tests pass.
