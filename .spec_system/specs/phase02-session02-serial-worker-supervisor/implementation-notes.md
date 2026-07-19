# Implementation Notes

**Session ID**: `phase02-session02-serial-worker-supervisor`
**Package**: backend
**Started**: 2026-07-19 20:05
**Last Updated**: 2026-07-19 20:17

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | 0 minutes |
| Blockers | 0 |

---

## Outcome

The FastAPI lifespan now owns exactly one serial generation worker whenever
the public `txt2crs` facade is configured. The thread scans durable runnable
work immediately, uses the package's recovery-first ordering, executes one
fresh public handle at a time, and polls every two seconds even when no
in-process nudge arrives.

The worker exposes only an immutable lifecycle snapshot. It records bounded
failure codes without exception text, job identity, owner identity, provider
detail, or paths. Shutdown stops new claims, allows a finite drain, and then
signals a restart-safe interruption before reporting a bounded error.

The public engine cancellation contract now distinguishes direct user
cancellation from application shutdown. The first reason wins. An interrupted
provider path leaves the accepted durable job and latest checkpoint
non-terminal, so the next process discovers and resumes it instead of showing
a false learner cancellation.

---

## Tests-First Evidence

Implementation began only after the new focused tests were written.

| Boundary | Pre-implementation result | Expected missing contract |
|----------|---------------------------|---------------------------|
| Engine runtime/facade/executor | Collection failed | `CancellationReason` and restart-safe executor interruption |
| Shell worker/lifespan/settings | Collection failed | `txt2crs_worker.py` and `Txt2CrsWorkerFactory` |

The initial shell execution then reached the repository session fixture but
connected to an unrelated PostgreSQL instance already occupying host port
5447. No container was stopped. Focused and complete shell validation used
the project database at `172.19.0.2:5432`, matching the prior validated local
fallback.

---

## Task Log

| Task | Result | Evidence |
|------|--------|----------|
| T001 | Complete | Session 01 and Phase 01 public-facade validation artifacts confirmed |
| T002 | Complete | Facade, resume state, deterministic store ordering, and lifespan seams inspected |
| T003 | Complete | Poll default 2, shutdown default 30, zero/upper bounds tested |
| T004 | Complete | User and shutdown reason first-writer tests added |
| T005 | Complete | Non-blocking executor shutdown request and join tests added |
| T006 | Complete | Real SQLite executor interruption remains `researching` and runnable |
| T007 | Complete | Immediate scan, timed poll, and nudge tests use event barriers |
| T008 | Complete | Two queued executors prove maximum active count is one |
| T009 | Complete | Discovery, creation, execution, and cleanup failures remain retryable and safe |
| T010 | Complete | Snapshot, repeated close, pre-start close, drain, and timeout covered |
| T011 | Complete | Configured/unconfigured and exceptional FastAPI cleanup order covered |
| T012 | Complete | Typed poll and shutdown fields added to shell settings |
| T013 | Complete | Both finite settings documented in `.env.example` |
| T014 | Complete | Thread-safe cancellation reasons implemented with immutable first cause |
| T015 | Complete | Application shutdown skips terminal cancellation settlement |
| T016 | Complete | `ApplicationExecutor.request_shutdown()` added as a public non-blocking signal |
| T017 | Complete | Safe status, failure, snapshot, and structural facade protocols created |
| T018 | Complete | Durable discovery and one-at-a-time executor ownership implemented |
| T019 | Complete | Latency-only nudge, polling, safe retry codes, and best-effort logging implemented |
| T020 | Complete | Stop-before-claim, bounded drain, timeout interruption, and repeated close implemented |
| T021 | Complete | Worker construction and reverse cleanup wired into FastAPI lifespan |
| T022 | Complete | 34 focused engine and 59 focused shell tests passed |
| T023 | Complete | 458 engine tests passed, 1 live-gated; 252 shell tests passed |
| T024 | Complete | Ruff, mypy, ty, frontend gates, client generation, and Zizmor passed |
| T025 | Complete | ASCII/LF, diff integrity, task evidence, and implementation notes completed |

---

## Files Created

| File | Purpose |
|------|---------|
| `backend/app/services/txt2crs_worker.py` | Serial discovery, execution, safe snapshot, nudge, and bounded shutdown |
| `backend/tests/services/test_txt2crs_worker.py` | Event-coordinated worker concurrency and failure regressions |

## Files Modified

| File or Area | Change |
|--------------|--------|
| `backend/app/core/config.py` and `backend/.env.example` | Added finite poll and shutdown settings |
| `backend/app/main.py` and `backend/app/services/__init__.py` | Added configured-only worker ownership and exports |
| `backend/tests/core/test_txt2crs_settings.py` | Added exact defaults and invalid bounds |
| `backend/tests/test_txt2crs_lifespan.py` | Added worker factory, startup, ordering, and cleanup coverage |
| `backend/packages/txt2crs/src/txt2crs/ai/runtime.py` | Added authoritative cancellation reasons |
| `backend/packages/txt2crs/src/txt2crs/application/facade.py` | Added restart-safe executor interruption |
| `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` | Preserved non-terminal state on process interruption |
| Engine runtime, facade, and executor tests | Added reason, interruption, and recovery regressions |
| `.spec_system/state.json` and session artifacts | Planned and recorded Session 02 |
| `.spec_system/archive/sessions/phase00-session01-baseline-container-and-state/` | Archived specs older than the current and previous phase |

---

## Key Implementation Decisions

1. **The durable database remains the queue**: The shell stores no accepted
   job list and performs no ordering. `next_runnable()` remains authoritative.
2. **Nudges are disposable**: `notify_runnable()` only wakes an idle event;
   startup scanning and periodic polling recover every missed event.
3. **One handle owns one attempt**: The worker publishes one active executor,
   runs it, and closes it before another discovery can execute.
4. **Failures carry codes, not objects**: Snapshots retain only a
   `WorkerFailureCode`; exceptions are neither serialized nor attached.
5. **Shutdown is not user cancellation**: A direct token `cancel()` keeps its
   existing user meaning. Facade and worker cleanup use the separate
   `application_shutdown` reason, which the durable executor leaves runnable.
6. **Cleanup is reverse ordered**: FastAPI closes the worker before the facade
   and still attempts facade cleanup when worker cleanup fails.

---

## Behavioral Quality Results

- Scoped lifecycle: Every created executor receives one close attempt on
  success, failure, stop races, and shutdown timeout.
- Duplicate-trigger prevention: Repeated start cannot create another thread;
  repeated close is safe; a closed worker cannot restart.
- Failure states: Discovery, creation, execution, cleanup, crash, and shutdown
  timeout have explicit finite codes.
- Retry behavior: Failed attempts wait for the configured poll interval and
  do not hot-loop.
- Concurrency: Event barriers prove the second executor cannot overlap the
  first and cannot start after shutdown begins.
- State freshness: Snapshots are rebuilt under the supervisor lock and contain
  no runnable identity.
- Contract alignment: Tests use public facade behavior and an AST allowlist
  rejects private `txt2crs` imports.

---

## Verification

### Focused Tests

- `uv run --package txt2crs pytest packages/txt2crs/tests/unit/test_runtime.py packages/txt2crs/tests/unit/test_application_facade.py packages/txt2crs/tests/integration/test_generation_job_executor.py -q`
  - PASS: 34 tests.
- `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/services/test_txt2crs_worker.py tests/test_txt2crs_lifespan.py tests/core/test_txt2crs_settings.py -q`
  - PASS: 59 tests.

### Complete Deterministic Suites

- `uv run --package txt2crs pytest -q`
  - PASS: 458 passed; 1 explicit live Codex/Tavily test skipped.
- `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/ -q`
  - PASS: 252 passed; 63 pre-existing short-test-key warnings.

### Static And Repository Gates

- Engine Ruff and strict mypy: PASS.
- Shell Ruff, strict mypy, and ty: PASS.
- Repository pre-commit: PASS, including frontend Biome/TypeScript, generated
  client verification, and Zizmor.
- `git diff --check`: PASS.
- ASCII and LF verification: PASS.

---

## Deviations And Blockers

- No scope was deferred.
- The planned engine public-contract correction was required and completed;
  the shell contains no cancellation or persistence workaround.
- The only environment issue was the known unrelated PostgreSQL collision on
  host port 5447. The project container remained running and tests used its
  private Docker address.
- The credentialed live GPT-5.6/Tavily acceptance test remains intentionally
  gated for release validation.

---

## Code Review Repairs

Formal base-to-head review found and fixed two Medium issues:

1. A `Thread.start()` failure now clears the unstarted thread reference and
   leaves partial-startup cleanup idempotent.
2. Every executor attempt now emits bounded structured start and terminal
   lifecycle events without identity or exception content.

The three review regressions failed before repair and now pass. The updated
focused shell set passes 62 tests, and the complete shell suite passes 255
tests with the same 63 pre-existing short-test-key warnings. The complete
engine suite remains 458 passed with one explicit live gate skipped.

---

## Next Step

Run `creview` against base commit
`183d35c2422571c844f409008f23c6f31457a0d1`.
