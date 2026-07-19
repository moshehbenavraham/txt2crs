# Implementation Notes

**Session ID**: `phase02-session03-cached-readiness-and-observability`
**Package**: backend
**Started**: 2026-07-19 20:21
**Last Updated**: 2026-07-19 21:07

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | 0 minutes |
| Blockers | 0 |

---

## Outcome

The public `txt2crs` application facade now owns one aggregate readiness
inspection. It reduces runtime authentication, exact GPT-5.6 discovery,
managed research topology, current and writable SQLite state, atomic artifact
storage, enabled P0 inputs, and conservative admission capacity into bounded
coarse checks. The shell does not reach through the facade to reconstruct any
provider, store, adapter, policy, or renderer behavior.

FastAPI now owns a stale-while-busy readiness cache and one shared runtime
ownership coordinator. Startup performs one synchronous inspection before the
worker starts. Maintenance refreshes are finite and non-blocking, browser
reads are immutable and side-effect free, and readiness, future device
authentication, and job execution cannot launch overlapping Codex runtimes.

Request, exception, telemetry, SMTP, database-startup, and worker events now
retain only allowlisted route names, methods, status, duration, finite state,
safe codes, and attempt counts. Raw paths, query strings, client addresses,
provider responses, exception strings, tracebacks, and recipient identities
are excluded from normal application logs.

---

## Tests-First Evidence

Implementation began after the focused readiness, runtime-ownership, error
translation, request-logging, worker, settings, and lifespan regressions were
written. Initial collection failed on the deliberately missing public
readiness and shell coordinator contracts. Those failures established the
boundary before implementation.

The host PostgreSQL port remained occupied by an unrelated container. No
container was stopped or modified. Complete shell validation used the
project database at `172.19.0.2:5432`, matching the previously validated
isolated fallback.

---

## Task Log

| Task Range | Result | Evidence |
|------------|--------|----------|
| T001-T002 | Complete | Session prerequisites and public package seams inspected |
| T003-T004 | Complete | Aggregate contract, real probes, sanitization, GPT-5.6, and partial failure tests added |
| T005-T007 | Complete | Runtime exclusivity, cache lifecycle, staleness, contention, and zero-side-effect read tests added |
| T008-T010 | Complete | Error mapping, log privacy, shared worker ownership, settings, and lifespan tests added |
| T011-T015 | Complete | Public readiness models, probes, factories, facade export, and focused engine validation implemented |
| T016-T021 | Complete | Shared owner, cache, worker gate, settings, lifecycle, error codes, translation, and safe observability implemented |
| T022 | Complete | Focused engine and shell readiness/lifecycle tests passed |
| T023 | Complete | 464 engine tests passed with 1 live gate skipped; 273 shell tests passed |
| T024 | Complete | Ruff, mypy, ty, frontend gates, client verification, and Zizmor passed |
| T025 | Complete | Public imports, safe log fields, probe cleanup, ASCII/LF, and diff integrity verified |

---

## Files Created

| File | Purpose |
|------|---------|
| `backend/packages/txt2crs/src/txt2crs/application/readiness.py` | Public finite readiness contracts and aggregate package inspector |
| `backend/packages/txt2crs/tests/unit/test_application_readiness.py` | Aggregate, probe, sanitization, model, input, and admission regressions |
| `backend/app/services/txt2crs_runtime.py` | Shared finite runtime ownership coordinator |
| `backend/app/services/txt2crs_readiness.py` | Immutable cached shell readiness and maintenance lifecycle |
| `backend/app/core/txt2crs_errors.py` | Context-free public package exception translation |
| `backend/tests/services/test_txt2crs_runtime.py` | Ownership exclusivity, contention, close, and snapshot tests |
| `backend/tests/services/test_txt2crs_readiness.py` | Refresh, staleness, busy, recovery, lifecycle, and side-effect tests |
| `backend/tests/core/test_txt2crs_errors.py` | Stable code/status/detail and context-clearing tests |
| `backend/tests/core/test_middleware.py` | Allowlisted request lifecycle logging regressions |

## Files Modified

| File or Area | Change |
|--------------|--------|
| Engine facade, factories, and application exports | Composed and exposed one aggregate readiness method |
| Engine SQLite and artifact stores | Added migration/write-rollback, capacity, and confined atomic probes |
| Engine job exports and narrow typing repairs | Exposed public job errors and corrected strict static-analysis issues |
| Shell worker and service exports | Added shared execution ownership across discovery through cleanup |
| Shell settings and `.env.example` | Added bounded refresh, staleness, and shutdown configuration |
| FastAPI lifespan | Added gate/cache ownership, ordered startup, and reverse cleanup |
| Shell constants and exception translation | Added semantic system and durable-job error codes |
| Middleware, exception handlers, telemetry, SMTP, and startup logging | Removed raw request and provider/error content from normal logs |
| Focused shell and engine tests | Added concurrency, cache, mapping, lifecycle, and privacy coverage |
| `.spec_system/state.json` and session artifacts | Planned and recorded Session 03 |
| `.spec_system/archive/sessions/` | Applied Apex retention by moving Phase 01 records and removing the oldest Phase 00 archive |

---

## Key Implementation Decisions

1. **Readiness belongs to the engine boundary**: Only the package can inspect
   its provider graph, SQLite store, artifact store, adapters, and admission
   policy. The shell receives one safe aggregate.
2. **Reads never probe**: `snapshot()` only reads locked immutable state and
   the worker's safe snapshot. It cannot invoke the provider, MCP, database,
   artifact store, or maintenance scheduler.
3. **One runtime owner**: Readiness, authentication, and execution use finite
   exclusive leases. A busy refresh returns last-known degraded state instead
   of creating another app-server.
4. **Startup is fail-observable, not indefinitely blocking**: Configured
   startup performs one initial refresh before starting the worker; later
   refreshes use a finite daemon thread and bounded shutdown.
5. **Admission is conservative**: The probe reserves the configured token
   ceiling plus the reviewed Tavily allowance without writing a job.
6. **Logs use allowlists**: Normal operational logs carry safe dimensions,
   never raw request locations, provider payloads, exception strings, or
   personal recipient data.
7. **Translation severs private context**: Known public engine errors become
   semantic `AppException` values with generic details, and their cause and
   context are cleared before crossing the shell boundary.

---

## Behavioral Quality Results

- Probe safety: SQLite readiness uses a current-migration check and an
  immediate transaction rolled back after a temporary write/read.
- Artifact safety: The maintenance probe performs staged atomic publish,
  read, delete, and unconditional confined cleanup.
- Runtime safety: Tests prove exclusive finite ownership and no identity or
  provider content in gate snapshots.
- Cache freshness: Stale, busy, worker-dead, shutdown, unconfigured, partial
  failure, and recovered states are explicit.
- Lifecycle safety: Partial startup and normal cleanup close worker,
  readiness, gate, and facade in reverse order without restarting closed work.
- Contract alignment: Shell imports remain limited to reviewed public
  `txt2crs` package exports.
- Model policy: Readiness accepts only the exact configured GPT-5.6 model.

---

## Verification

### Complete Deterministic Suites

- `uv run --package txt2crs pytest -q`
  - PASS: 464 passed; 1 explicit live Codex/Tavily test skipped.
- `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/ -q`
  - PASS: 273 passed; 63 pre-existing short-test-key warnings.

### Static And Repository Gates

- Engine Ruff, strict mypy, and ty: PASS.
- Shell Ruff, strict mypy, and ty: PASS.
- Repository pre-commit: PASS, including frontend Biome/TypeScript, generated
  client verification, and Zizmor.
- `git diff --check`: PASS.
- ASCII and LF verification: PASS.

---

## Deviations And Blockers

- No planned scope was deferred.
- The narrow engine probe implementation and public job-error export were
  required to preserve the package boundary; the shell contains no duplicate
  readiness or storage logic.
- Strict static analysis exposed three existing touched-path typing defects in
  deterministic research, PDF iteration, and metadata return typing. They
  received behavior-preserving corrections.
- The only environment issue was the known unrelated PostgreSQL collision on
  host port 5447. Tests used the project container's private address.
- The credentialed live GPT-5.6/Tavily acceptance test remains intentionally
  gated for release validation.
- Apex retention moved the five completed Phase 01 session directories into
  the archive and removed the oldest Phase 00 archived session. Hash checks
  confirmed the Phase 01 content was unchanged by relocation.

---

## Review Repairs Already Applied

The implementation self-review found and repaired privacy and lifecycle
weaknesses before the formal review checkpoint:

1. Exception handlers no longer log raw paths, response details, validation
   payloads, exception strings, or tracebacks.
2. Telemetry, SMTP, database-startup, and test-startup helpers no longer log
   provider response content, addresses, ports, or raw exceptions.
3. A readiness coordinator cannot refresh or restart provider work after it
   has been closed.
4. Exact GPT-5.6 identity is validated at contract construction, not merely
   assumed by factory composition.
5. Runtime contention is reported as an explicit degraded last-known state.

---

## Next Step

Run `creview` against base commit
`73b395b0385dd0af3cb9841c61a38c7c6d153462`.
