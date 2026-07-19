# Session Specification

**Session ID**: `phase02-session03-cached-readiness-and-observability`
**Phase**: 02 - Composition and Readiness
**Status**: Implemented
**Created**: 2026-07-19
**Base Commit**: 73b395b0385dd0af3cb9841c61a38c7c6d153462
**Package**: backend
**Package Stack**: Python 3.14, FastAPI, Pydantic v2, and public txt2crs contracts

---

## 1. Session Overview

This session builds the side-effect boundary behind the future system
readiness endpoint. The `txt2crs` package gains one aggregate, browser-safe
readiness projection for provider authentication/model discovery, managed
research, storage integrity, enabled input capabilities, and admission
capacity. The FastAPI shell caches that projection, combines it with the
serial worker's safe snapshot, and never performs provider or destructive
storage work from a browser read.

A shared runtime-ownership coordinator serializes readiness refresh, future
device authentication, and current job execution. The session also closes the
known privacy finding in request logging and adds one central package
exception translator that emits only stable shell error codes and generic
safe details.

---

## 2. Objectives

1. Expose complete readiness evidence through one public package boundary
   without leaking private stores, adapters, provider payloads, or paths.
2. Refresh readiness at startup and a finite maintenance interval while
   allowing reads to return the last immutable snapshot immediately.
3. Guarantee that provider readiness, device authentication, and job
   execution cannot own a second Codex app-server concurrently.
4. Remove raw route paths, query parameters, and client addresses from shell
   request logs before system and learner routes are added.
5. Translate public engine exceptions to existing or new semantic
   `ErrorCode` values without retaining private exception context.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase02-session01-engine-composition-lifecycle` - owns one configured
  package facade for the FastAPI lifespan.
- [x] `phase02-session02-serial-worker-supervisor` - exposes bounded worker
  liveness and capacity state and one serial executor owner.

### Required Tools Or Knowledge

- Python threading primitives, immutable Pydantic contracts, FastAPI
  middleware, pytest, Ruff, mypy, and ty.
- Public `txt2crs.application`, `txt2crs.ai`, and `txt2crs.jobs` contracts.

### Environment Requirements

- Deterministic tests require no Tavily key, Codex login, MCP listener, or
  network access.
- Full shell tests use the repository's isolated PostgreSQL test database.

---

## 4. Scope

### In Scope (MVP)

- A strict public engine readiness model with coarse states for runtime
  authentication, exact GPT-5.6 discovery, research/MCP, SQLite, artifacts,
  enabled inputs, and admission capacity.
- Package-owned startup/maintenance probes for SQLite migrations and
  write/rollback, atomic artifact write/read/delete, reviewed research
  topology, configured input adapters, and one conservative admission
  reservation.
- A shell runtime-ownership coordinator with finite owner values and
  content-free snapshots.
- A cached readiness coordinator with immediate startup refresh, bounded
  periodic refresh, immutable last-known snapshots, explicit freshness, safe
  warnings/recovery actions, and bounded shutdown.
- Worker acquisition of shared execution ownership for the whole
  executor-handle lifetime.
- Sanitized request lifecycle events and a central public-package exception
  translation helper.
- FastAPI lifespan ownership and reverse cleanup for the readiness coordinator.

### Out Of Scope (Deferred)

- HTTP system readiness and authentication routes - Session 04 owns API
  schemas, authorization, rate limits, and route behavior.
- Starting, polling, or ending the browser device-code ceremony - Session 04.
- Learner job submission, status, cancellation, and artifact delivery - Phase
  03.
- Frontend operator setup - Session 05.
- Hosted telemetry, privacy retention automation, or production deployment.

---

## 5. Technical Approach

### Architecture

Add a package-owned `ApplicationReadiness` contract and inspector composed by
both real and deterministic application factories. The real inspector owns
all destructive/local checks because the shell cannot legally reach into the
SQLite store, artifact store, adapter registry, source policy, or provider
graph. The facade exposes one aggregate operation and retains the current
safe provider method only as a compatibility alias if existing callers
require it.

Add `RuntimeOwnershipCoordinator` under `backend/app/services/`. It uses one
non-reentrant lock and a finite `readiness`, `authentication`, or `execution`
owner. The worker holds `execution` ownership from runnable discovery through
executor cleanup. Readiness refresh uses non-blocking ownership; if execution
or future authentication owns the runtime, it keeps the previous cache
instead of launching another provider graph.

Add `CachedReadinessCoordinator` with a single finite maintenance thread.
Refresh combines the package aggregate with the worker snapshot into an
immutable safe shell model. `snapshot()` performs no I/O beyond taking locks
and reading worker state. Unconfigured startup publishes an explicit
unavailable snapshot without constructing an engine facade.

### Design Patterns

- Package boundary projection: all engine internals collapse into coarse,
  sanitized readiness states before reaching FastAPI.
- Stale-while-busy cache: contention retains the last known safe projection.
- Single runtime owner: readiness, authentication, and execution use one
  process-wide arbitration primitive.
- Immutable snapshot: browser-facing reads cannot mutate cached state or
  trigger refresh.
- Allowlisted observability: structured logs contain method, route name,
  status, duration, finite state, and safe error code only.
- Central exception mapping: known public engine errors become stable
  `AppException` values; unknown failures become generic internal errors.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/application/readiness.py` | Strict aggregate readiness contracts and package-owned probe coordinator | ~280 |
| `backend/packages/txt2crs/tests/unit/test_application_readiness.py` | Aggregate, storage, input, admission, sanitization, and failure tests | ~420 |
| `backend/app/services/txt2crs_runtime.py` | Shared finite runtime ownership coordinator | ~180 |
| `backend/app/services/txt2crs_readiness.py` | Cached shell readiness model, refresh thread, and safe snapshots | ~360 |
| `backend/app/core/txt2crs_errors.py` | Public package exception-to-shell translation | ~180 |
| `backend/tests/services/test_txt2crs_runtime.py` | Exclusivity, contention, release, and safe snapshot tests | ~220 |
| `backend/tests/services/test_txt2crs_readiness.py` | Cache, side-effect, freshness, combination, and lifecycle tests | ~500 |
| `backend/tests/core/test_txt2crs_errors.py` | Stable error mapping and private-context regression tests | ~220 |
| `backend/tests/core/test_middleware.py` | Request-log privacy and route-template event tests | ~180 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/application/facade.py` | Expose aggregate readiness through the public facade | ~30 |
| `backend/packages/txt2crs/src/txt2crs/application/factories.py` | Compose real/deterministic aggregate inspectors from owned resources | ~100 |
| `backend/packages/txt2crs/src/txt2crs/application/__init__.py` | Export safe readiness contracts | ~20 |
| `backend/packages/txt2crs/src/txt2crs/jobs/store.py` | Add internal current-schema and non-mutating admission checks | ~50 |
| `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py` | Add confined atomic maintenance probe | ~60 |
| `backend/app/services/txt2crs_worker.py` | Hold shared execution ownership around each job lifecycle | ~50 |
| `backend/app/services/__init__.py` | Export readiness and runtime services | ~20 |
| `backend/app/core/config.py` | Add finite readiness refresh and shutdown settings | ~20 |
| `backend/app/core/constants.py` | Add semantic system/job engine error codes and mappings | ~30 |
| `backend/app/core/middleware.py` | Replace raw request metadata with allowlisted route-safe events | ~50 |
| `backend/app/main.py` | Own gate and cache after facade, before worker, with reverse cleanup | ~100 |
| `backend/.env.example` | Document readiness timing settings | ~4 |
| Existing focused tests | Update facade, factory, worker, settings, and lifespan expectations | ~350 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] `accepting_jobs` is true only when every required package check passes,
  the worker is alive and not shutting down, runtime ownership is available,
  the snapshot is fresh, and admission has capacity.
- [ ] Unconfigured systems return a stable unavailable snapshot with generic
  setup actions and no credentials, paths, ports, exception text, or provider
  payloads.
- [ ] `snapshot()` never invokes package readiness, provider, MCP, SQLite
  probe, artifact probe, or cache-refresh work.
- [ ] Startup refreshes immediately; later refreshes use one finite interval
  and retain the previous safe snapshot while execution owns the runtime.
- [ ] A running job prevents readiness and future authentication ownership
  until executor cleanup completes.
- [ ] Storage probes leave no durable job, admission, artifact, or temporary
  probe state after success or failure.
- [ ] Enabled inputs truthfully include all required P0 modes only when their
  package adapters and routing support exist.
- [ ] Public engine failures map to stable shell codes; unknown failures are
  generic and retain neither `__cause__` nor `__context__`.
- [ ] Request logs omit raw paths, query strings, client IPs, learner data,
  credential material, and provider details.

### Testing Requirements

- [ ] Tests are written and observed failing before implementation.
- [ ] Focused engine readiness and backend runtime/readiness/logging/error
  tests pass.
- [ ] Complete deterministic backend shell and engine suites pass.

### Non-Functional Requirements

- [ ] Every duration is finite and bounded by typed settings.
- [ ] Snapshots, logs, warnings, and recovery actions are immutable or copied,
  bounded, allowlisted, and sanitized.
- [ ] No shell module imports private package stores, adapters, factories, or
  provider implementations.
- [ ] Cleanup is idempotent, reverse ordered, and cannot mask a primary
  startup or request failure.

### Quality Gates

- [ ] All files are ASCII-encoded with Unix LF line endings.
- [ ] Code includes intern-friendly comments for ownership and side effects.
- [ ] Ruff format/check, strict mypy, ty, and repository pre-commit pass.

---

## 8. Implementation Notes

### Working Assumptions

- A package aggregate readiness inspection is a required public-boundary
  correction. Existing `Txt2CrsApplication.inspect_readiness()` reports only
  the provider runtime and cannot truthfully prove storage, input, research,
  or admission state without forbidden shell access.
- Provider readiness already opens the same managed real graph used by jobs.
  A successful real inspection therefore proves reviewed Tavily policy and
  the exact two-tool loopback MCP contract in addition to auth/model status.
- The readiness admission reservation uses the default execution profile's
  complete input/output token ceiling and the configured per-request research
  ceiling selected for Phase 03 submission. It is a read-only quota check and
  never inserts an admission row.
- A busy serial worker is conservatively not accepting another P0 request in
  this phase. Phase 03 can revisit queue depth only through a recorded
  admission-policy change.

### Conflict Resolutions

- Session 03 is backend-primary, but its required checks expose a package
  contract gap. Implementing storage or admission queries in FastAPI would
  violate the project architecture, so the narrow public aggregate is added
  and tested inside `backend/packages/txt2crs/`.
- The current request middleware logs the raw route path, query string, and
  client address. That conflicts with the security record and becomes unsafe
  before source-bearing routes exist. This session removes those fields and
  uses an allowlisted matched route template/name only after routing.

### Key Considerations

- The cache keeps the last successful or safe failed projection. A skipped
  refresh records contention only through a bounded internal event and does
  not convert old provider data into a new success.
- Subscription quota remains `unknown` whenever the provider SDK cannot
  expose it. Unknown quota is honest and does not become a guessed failure;
  durable admission remains independently authoritative.
- The runtime owner snapshot contains only the finite owner kind and
  availability, never thread names, job IDs, user IDs, or timing internals.

### Potential Challenges

- Startup ordering can race worker recovery with the first provider probe.
  Construct the shared coordinator first, perform the initial bounded refresh,
  then start the worker; close in exact reverse order.
- Storage probes can leave files or SQLite rows on interruption. Use
  rollback/finally and confined random temporary names, and test interrupted
  cleanup.
- Route templates may be unavailable before `call_next`. Log the received
  event with method only, then include an allowlisted matched template or
  route name on completion without ever falling back to the raw path.

### Relevant Considerations

- [P00-backend] **Request logs expose raw request metadata**: remove the
  cumulative privacy blocker in this session.
- [P00-backend+backend/packages/txt2crs] **One process is mandatory**: one
  shared owner gate prevents duplicate app-server instances.
- [P00-backend] **Readiness still needs engine composition**: package checks
  plus worker state create the reusable admission gate.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  storage, provider, input, and admission checks stay package-owned.
- [P01-backend/packages/txt2crs] **Do not retain private exception context**:
  central translation explicitly breaks chained context.

---

## 9. Validation Plan

1. Run focused engine readiness/facade/factory/storage tests.
2. Run focused shell runtime/readiness/settings/middleware/error/lifespan and
   worker tests.
3. Run complete deterministic engine and shell pytest suites.
4. Run Ruff format/check, strict mypy, ty, and repository pre-commit.
5. Search shell imports, structured log fields, and translated exceptions for
   private package access or unsafe data.
6. Verify no dependency, PostgreSQL schema, Alembic migration, frontend, or
   generated-client change was introduced.
