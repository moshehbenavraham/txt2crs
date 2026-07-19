# Session Specification

**Session ID**: `phase02-session02-serial-worker-supervisor`
**Phase**: 02 - Composition and Readiness
**Status**: Not Started
**Created**: 2026-07-19
**Base Commit**: 183d35c2422571c844f409008f23c6f31457a0d1
**Package**: backend
**Package Stack**: Python 3.14, FastAPI, SQLModel, PostgreSQL, and public txt2crs contracts

---

## 1. Session Overview

This session adds the one in-process serial worker required by the P0 topology.
The worker starts with the configured FastAPI lifespan, immediately discovers
the next durable runnable item through `Txt2CrsApplication.next_runnable()`,
and creates one fresh public `ApplicationExecutor` handle at a time.

The supervisor also publishes a bounded, content-free worker snapshot for the
next readiness session. Polling, explicit nudges, failure recovery, and
shutdown are deterministic and credential-free in tests. A narrow public
engine-contract correction distinguishes process interruption from a user's
terminal cancellation so deployment shutdown leaves checkpointed work
recoverable.

---

## 2. Objectives

1. Recover runnable jobs on startup and through finite two-second polling
   without reading a private engine store.
2. Execute at most one job at a time through a fresh public executor handle
   and close every handle on every outcome.
3. Expose safe worker liveness, busy, capacity, shutdown, and failure state
   without job content, identifiers, provider detail, or paths.
4. Stop discovery before shutdown, allow a bounded drain, then interrupt
   remaining work without recording a user cancellation.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase02-session01-engine-composition-lifecycle` - owns one configured
  public facade for the complete FastAPI lifespan.
- [x] `phase01-session05-public-facade-and-owner-lifecycle` - exposes durable
  runnable discovery and owner/job-bound executor handles.

### Required Tools Or Knowledge

- Python threading primitives, FastAPI lifespan cleanup, pytest, Ruff, mypy,
  and ty.
- Public `txt2crs.application` and `txt2crs.jobs` contracts only.

### Environment Requirements

- Deterministic tests require no Tavily key, Codex login, or network access.
- Full shell tests use the existing isolated PostgreSQL test configuration.

---

## 4. Scope

### In Scope (MVP)

- The application operator gets exactly one worker thread when the facade is
  configured, with startup scanning and periodic durable discovery.
- Durable runnable work is selected by the package facade and executed in its
  package-defined recovery-first order.
- An in-process nudge wakes idle discovery after a future durable submission;
  periodic polling remains authoritative after restart or a missed nudge.
- Each executor is created, executed, interrupted when required, and closed
  inside one worker-owned scope with cleanup on every acquired-resource path.
- Later readiness composition gets one immutable safe snapshot of liveness,
  active work, capacity, shutdown, and bounded failure codes.
- Shutdown rejects new claims, drains within a typed finite timeout, signals
  restart-safe interruption, and reports a safe timeout error.
- Public cancellation state distinguishes owner cancellation from process
  interruption so interrupted non-terminal work remains runnable.

### Out Of Scope (Deferred)

- Learner submit, status, cancellation, and artifact routes - Phase 03 owns
  HTTP job contracts.
- Provider readiness and the shared runtime ownership lock - Session 03 owns
  cached dependency coordination.
- Parallel workers, an external queue, or horizontal backend replicas - these
  conflict with the P0 single-process topology.
- Readiness HTTP routes and operator authentication - Sessions 03 and 04 own
  those surfaces.

---

## 5. Technical Approach

### Architecture

Create `SerialTxt2CrsWorker` under `backend/app/services/`. One daemon thread
uses only the configured `Txt2CrsApplication` facade. Its loop scans
immediately, calls `next_runnable()`, creates an `ApplicationExecutor` from the
returned owner/job identity, and runs it inside a `try/finally`-protected
scope. An event combines the periodic two-second recovery poll with a
latency-only nudge.

FastAPI creates the worker only after the composition lifecycle owns a real
facade, stores the service on application state, and closes the worker before
the facade. Cleanup attempts every acquired resource and preserves the
authoritative failure.

The engine cancellation token gains a public finite reason. Direct
`cancel()` retains the existing user-cancellation default. A public executor
shutdown request uses an interruption reason, and generation failure
settlement leaves that durable job non-terminal for exact checkpoint recovery.

### Design Patterns

- Supervisor thread: one owner serializes discovery and execution.
- Durable queue polling: SQLite through the facade is authoritative; events
  only reduce latency.
- Immutable snapshot: later readiness code consumes bounded state without
  observing private worker objects.
- Reasoned cancellation: user cancellation and process interruption produce
  different durable outcomes.
- Reverse-order cleanup: worker settles before the application facade closes.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/app/services/txt2crs_worker.py` | Serial worker, safe snapshot, polling, nudge, and bounded shutdown | ~350 |
| `backend/tests/services/test_txt2crs_worker.py` | Recovery, seriality, failure, snapshot, nudge, and shutdown tests | ~500 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/app/core/config.py` | Add finite worker poll and shutdown bounds | ~20 |
| `backend/.env.example` | Document worker poll and shutdown configuration | ~4 |
| `backend/app/main.py` | Own the configured worker in FastAPI lifespan order | ~100 |
| `backend/app/services/__init__.py` | Export the shell worker contracts | ~10 |
| `backend/tests/core/test_txt2crs_settings.py` | Prove defaults and invalid bounds | ~20 |
| `backend/tests/test_txt2crs_lifespan.py` | Prove configured/unconfigured startup and cleanup ordering | ~220 |
| `backend/packages/txt2crs/src/txt2crs/ai/runtime.py` | Add explicit cancellation reasons | ~35 |
| `backend/packages/txt2crs/src/txt2crs/application/facade.py` | Add non-blocking restart-safe executor interruption | ~30 |
| `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` | Preserve non-terminal state on process interruption | ~15 |
| `backend/packages/txt2crs/tests/unit/test_runtime.py` | Prove first-writer cancellation reason semantics | ~45 |
| `backend/packages/txt2crs/tests/unit/test_application_facade.py` | Prove shutdown interruption and close behavior | ~65 |
| `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` | Prove interrupted work remains recoverable | ~70 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] Startup discovers runnable work before its first timed wait.
- [ ] Only package facade discovery and public executor handles are used.
- [ ] No more than one executor is active at any time.
- [ ] Executor construction, execution, and cleanup failures never kill the
  supervisor or expose their private text.
- [ ] A nudge wakes idle discovery, while periodic polling recovers missed
  events and process restarts.
- [ ] Shutdown prevents a new claim, allows one finite drain interval, requests
  restart-safe interruption after timeout, and returns a safe error.
- [ ] Process interruption does not turn a durable non-terminal job into a
  terminal user cancellation.
- [ ] Configured FastAPI lifespans own one worker; unconfigured lifespans own
  none; every partial startup and shutdown path attempts reverse cleanup.

### Testing Requirements

- [ ] Unit tests are written before implementation and pass.
- [ ] Focused worker, lifespan, runtime, facade, and executor scenarios pass.
- [ ] Complete backend shell and engine deterministic suites pass.

### Non-Functional Requirements

- [ ] Default poll interval is 2 seconds and every worker duration is finite
  and bounded by typed settings.
- [ ] Snapshot and structured events contain no job ID, owner ID, request
  content, provider data, exception text, credential, or path.
- [ ] The worker uses one thread and cannot restart after terminal close.
- [ ] Cleanup is idempotent and does not mask an earlier startup or request
  failure.

### Quality Gates

- [ ] All files are ASCII-encoded.
- [ ] Unix LF line endings are used.
- [ ] Code follows project conventions and includes intern-friendly comments.
- [ ] Ruff, mypy, ty, and pre-commit checks pass.

---

## 8. Implementation Notes

### Working Assumptions

- The worker exists only when `Txt2CrsApplicationLifecycle.application` is not
  `None`. Session 01 explicitly represents missing credentials as a started,
  unconfigured lifecycle, so creating a synthetic queue owner would make that
  state less truthful.
- The facade's `next_runnable()` ordering is authoritative. The package store
  already orders delivery and rendering recovery before earlier states, then
  by creation time and job ID, so the shell must not duplicate ordering.
- A nudge is a public supervisor method even though submit routes arrive in
  Phase 03. The system plan defines it as latency-only, and adding it now lets
  the worker behavior be complete without moving HTTP scope forward.
- A dedicated `TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS` setting is required.
  The system plan requires every finite default to be typed and requires a
  bounded drain, while no existing setting correctly owns that duration.

### Conflict Resolutions

- The Session 02 stub says shutdown signals active work, while the system plan
  says deployment interruption must not become a user cancellation. The
  current cancellation token has only one boolean and the executor settles
  every observed cancellation as `cancelled`. This session adds an explicit
  process-interruption reason: direct cancellation keeps its terminal user
  meaning, but worker/facade shutdown preserves the last durable non-terminal
  checkpoint for restart.
- The stub names `backend` as the primary package, while the required shutdown
  semantics reveal a public engine-contract gap. The shell must not work
  around that gap, so the narrow engine runtime/facade/executor correction is
  included and independently tested under `backend/packages/txt2crs/`.

### Key Considerations

- The SQLite job store remains the only queue; no PostgreSQL job shadow or
  in-memory accepted-work list is added.
- A failed discovery or executor attempt waits for the finite poll interval
  before retrying the same durable work, preventing a hot failure loop.
- Logs use bounded reason codes only and never interpolate exceptions or
  runnable identities.

### Potential Challenges

- Thread timing can make tests flaky: coordinate tests with `threading.Event`
  barriers and finite waits instead of sleeps.
- Shutdown can race executor acquisition: publish the active handle under one
  lock and re-check the stop signal before execution.
- Cleanup failures can mask execution failures: retain the primary error and
  report secondary cleanup only through safe structured reason codes.

### Relevant Considerations

- [P00-backend+backend/packages/txt2crs] **One process is mandatory**: one
  in-process thread is the complete P0 worker topology.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  discovery, request loading, checkpoint recovery, and execution stay behind
  public package contracts.
- [P01-backend+backend/packages/txt2crs] **Worker recovery uses public
  handles**: the supervisor never imports or queries the package store.
- [P01-backend/packages/txt2crs] **One context owns provider resources**:
  every executor scope unwinds before another job begins.
- [P01-backend/packages/txt2crs] **Do not retain private exception context**:
  worker state and logs use enumerated safe failure codes only.

### Behavioral Quality Focus

Checklist active: Yes
Top behavioral risks for this session:

- Shutdown racing a newly acquired executor and starting work after claims
  should have stopped.
- One failed executor causing a hot retry loop, leaked provider graph, or dead
  worker thread.
- Process shutdown being persisted as a learner-requested cancellation instead
  of a recoverable interruption.

---

## 9. Testing Strategy

### Unit Tests

- Prove finite settings, cancellation-reason first-writer behavior, immutable
  safe snapshots, immediate startup scan, periodic poll, nudge, and state
  transitions.
- Prove executor scopes close after success, creation failure, execution
  failure, and shutdown interruption.

### Integration Tests

- Run a real engine executor to an interruption boundary and verify its job
  remains non-terminal and is returned by `next_runnable()`.
- Exercise configured and unconfigured FastAPI lifespans with recording
  lifecycle/worker factories and exact reverse cleanup order.

### Runtime Verification

- Start an event-coordinated worker with two runnable fakes and prove the
  second executor cannot overlap the first.
- Block one executor past the finite drain bound, close the supervisor, and
  prove it signals interruption, reports only a safe timeout, and later exits.

### Edge Cases

- Repeated start, repeated close, close before start, and nudge after close.
- Discovery failure, executor factory failure, execution failure, and cleanup
  failure.
- Stop requested between discovery, executor creation, and execution.
- Worker thread exits unexpectedly or remains alive past the shutdown bound.

---

## 10. Dependencies

### Other Sessions

- Depends on: `phase02-session01-engine-composition-lifecycle` and
  `phase01-session05-public-facade-and-owner-lifecycle`.
- Depended by: `phase02-session03-cached-readiness-and-observability`,
  `phase02-session04-system-readiness-and-auth-api`, and Phase 03 job routes.

---

## Next Steps

Run the `implement` workflow step to begin implementation.
