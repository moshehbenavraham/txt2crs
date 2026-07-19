# PRD Phase 02: Composition and Readiness

**Status**: In Progress
**Sessions**: 5 (initial estimate)
**Estimated Duration**: 3-5 days

**Progress**: 1/5 sessions (20%)

---

## Overview

Phase 02 composes the completed public `txt2crs` engine boundary into one
FastAPI-owned application lifecycle. It adds a serial worker supervisor,
truthful cached readiness, safe operator authentication endpoints, and the
operator setup experience without exposing engine internals or starting
provider work from browser polling.

---

## Progress Tracker

| Session | Name | Status | Est. Tasks | Validated |
|---------|------|--------|------------|-----------|
| 01 | Engine Composition Lifecycle | Complete | 24 | 2026-07-19 |
| 02 | Serial Worker Supervisor | Not Started | ~12-25 | - |
| 03 | Cached Readiness and Observability | Not Started | ~12-25 | - |
| 04 | System Readiness and Auth API | Not Started | ~12-25 | - |
| 05 | Operator Setup Experience | Not Started | ~12-25 | - |

---

## Completed Sessions

- Session 01: Engine Composition Lifecycle - completed 2026-07-19

---

## Upcoming Sessions

- Session 02: Serial Worker Supervisor

---

## Objectives

1. Translate shell settings into one package-owned application configuration
   and own the resulting facade for the complete FastAPI lifespan.
2. Recover and execute runnable work through one serial supervisor using only
   public facade handles and deterministic cleanup.
3. Maintain a bounded safe readiness snapshot for authentication, GPT-5.6,
   research, storage, worker, input capability, and admission checks.
4. Expose authenticated readiness and superuser-only device authentication
   routes with structured error translation.
5. Give operators an accessible setup screen with safe status, device-code
   guidance, and documented CLI recovery.

---

## Prerequisites

- Phase 01 completed and its public facade, configuration, recovery, managed
  provider lifecycle, and owner lifecycle contracts validated.
- The backend continues to run as exactly one application process.
- Local Docker Compose remains the only deployment target.

---

## Planning Assumptions And Resolutions

### Working Assumptions

- The public engine facade and real/test factory contracts completed in Phase
  01 are sufficient for shell composition. The Phase 01 validation evidence
  proves the lifecycle without private imports, so Phase 02 can keep engine
  changes limited to independently tested public-contract corrections.
- Browser readiness reads a cached snapshot and never performs destructive
  storage probes, starts MCP, or invokes Codex synchronously. The system plan
  requires bounded startup/maintenance probes and shared runtime ownership, so
  the application can expose truthful status without duplicating a runtime.
- Phase 02 defines admission readiness but does not add learner job routes.
  The roadmap assigns durable submit, status, and artifact HTTP contracts to
  Phase 03, so this phase only supplies the reusable readiness gate they need.

### Conflict Resolutions

- The master PRD listed Phase 02 as one session, while the implementation plan
  combines five independently testable objectives across backend lifecycle,
  worker execution, readiness, privileged API, and frontend setup. A single
  session could not satisfy the 12-25 task and 2-4 hour contract. Phase 02 is
  therefore split into five ordered sessions, and the master PRD session count
  is reconciled to five.
- The implementation plan's historical suggested label says `S04 -
  composition and readiness`, but Phase 02 has no existing session artifacts
  and state tracking identifies it as the next phase. The phase uses
  sequential Phase 02 session identifiers beginning at S01 so project state
  and session discovery remain unambiguous.

---

## Technical Considerations

### Architecture

FastAPI owns configuration translation, HTTP authorization, exception
translation, lifecycle, and presentation-safe caching. The `txt2crs` package
continues to own generation, research, validation, persistence, rendering,
provider construction, and managed MCP behavior. One application-level
runtime lock serializes readiness refresh, device authentication, and job
execution.

The application lifespan must construct resources in dependency order and
close them in reverse order. The worker recovers runnable jobs through the
facade, requests a fresh executor per job, and guarantees cleanup for success,
failure, cancellation, and shutdown.

### Technologies

- FastAPI lifespan and dependency injection
- Pydantic v2 settings and strict API schemas
- Public `txt2crs` application facade and factory protocols
- Python threading or task supervision with bounded shutdown
- TanStack Query, Zod, shadcn/Radix, and React 19

### Risks

- **Duplicate runtime ownership**: Enforce the existing single-process
  topology and one shared ownership lock for worker, readiness, and login.
- **Private data in logs or errors**: Sanitize request logging, use bounded
  safe projections, and translate package errors through `AppException` and
  `ErrorCode`.
- **Readiness side effects**: Refresh on startup and a bounded maintenance
  schedule; serve browser requests from the last safe snapshot.
- **Shutdown leaks**: Test partial-startup failure and reverse-order cleanup
  for worker, authenticator, MCP, Codex, HTTP, and temporary resources.
- **Operator-only ceremony exposure**: Require current superuser
  authorization and return only browser-safe device login state.

### Relevant Considerations

- [P00-backend] **Request logs expose raw request metadata**: Session 03
  removes raw path, query, and client-IP exposure before new system endpoints
  become public.
- [P00-backend+backend/packages/txt2crs] **One process is mandatory**: The
  lifecycle and supervisor preserve exactly one in-process serial worker.
- [P00-backend] **Readiness still needs engine composition**: Sessions 01-04
  translate the facade snapshots into truthful admission and operator state.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  Shell services call only public facade and factory contracts.
- [P01-backend+backend/packages/txt2crs] **Worker recovery uses public
  handles**: Session 02 recovers runnable jobs and uses
  `ApplicationExecutor` for cancellation and shutdown.
- [P01-backend/packages/txt2crs] **One context owns provider resources**:
  Composition and supervision preserve dependency-order entry and reverse
  cleanup.
- [P01-backend/packages/txt2crs] **Do not retain private exception context**:
  Session 03 tests safe exception translation without private causes or
  contexts.

---

## Success Criteria

Phase complete when:

- [ ] All 5 sessions completed.
- [ ] Unconfigured readiness is truthful, bounded, safe, and side-effect free.
- [ ] Configured readiness validates dedicated authentication, discovered
  GPT-5.6, research, storage, worker health, enabled inputs, and admission.
- [ ] The serial worker recovers runnable jobs, executes one job at a time,
  and closes every per-job resource.
- [ ] A superuser can complete device-code setup through the browser while
  non-superusers cannot access the ceremony.
- [ ] Shutdown and partial startup failures close all application-owned child
  resources.
- [ ] Readiness-dependent admission fails with `SYSTEM_NOT_READY` when any
  required dependency is unavailable.
- [ ] Shell logs and error responses contain no raw personal, learner,
  provider, credential, or filesystem data.
- [ ] Backend and frontend deterministic validation remains green.

---

## Dependencies

### Depends On

- Phase 01: Engine Application Boundary

### Enables

- Phase 03: Durable Jobs API
