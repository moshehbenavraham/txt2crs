# Code Review and Repair Report

**Session ID**: `phase02-session02-serial-worker-supervisor`
**Package**: backend
**Reviewed**: 2026-07-19
**Base Commit**: `183d35c2422571c844f409008f23c6f31457a0d1`
**Scope**: All changes since the base commit, including the implementation
checkpoint and review repairs
**Result**: RESOLVED

## Review Surface

The exact base-to-head diff was reviewed across:

- Apex session planning, task, implementation, state, and archive records.
- `backend/app/core/config.py` and `backend/.env.example`.
- `backend/app/main.py` and `backend/app/services/__init__.py`.
- `backend/app/services/txt2crs_worker.py`.
- `backend/tests/core/test_txt2crs_settings.py`.
- `backend/tests/services/test_txt2crs_worker.py`.
- `backend/tests/test_txt2crs_lifespan.py`.
- `backend/packages/txt2crs/src/txt2crs/ai/runtime.py`.
- `backend/packages/txt2crs/src/txt2crs/application/facade.py`.
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`.
- Engine runtime, facade, and generation-executor tests.

The review emphasized thread races, stop-before-claim behavior, bounded
shutdown, restart semantics, cleanup ordering, error masking, public package
boundaries, safe structured events, secrets, personal data, injection
surfaces, and denial-of-service bounds.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `backend/app/services/txt2crs_worker.py:171` - The supervisor stored its
  thread object before calling `Thread.start()`, but a real thread-creation
  failure left that unstarted object in `_thread`. Snapshot then called
  `is_alive()` and partial-startup cleanup attempted `join()` on an object
  that never started, leaving inconsistent state and a secondary cleanup
  failure. | Fix: Reset `_thread` and status synchronously when start fails,
  retain only the safe `worker_crashed` code, use best-effort bounded logging,
  and preserve the original start exception. Added a regression with a
  failing thread factory and repeated close. | Status: FIXED
- `backend/app/services/txt2crs_worker.py:340` - The session deliverables
  required structured worker and execution lifecycle events, but the
  implementation emitted only worker start/shutdown/failure events. Operators
  could not distinguish an idle worker from a handle that started and then
  completed or failed. | Fix: Emit `txt2crs.execution_started`,
  `txt2crs.execution_completed`, `txt2crs.execution_failed`, and
  `txt2crs.execution_cleanup_failed` with bounded reason codes only. Added
  success/failure event regressions that reject job identity, fake provider
  names, paths, and exception text. | Status: FIXED

### Low

No findings.

## Assumptions and Deliberate Non-Fixes

- Provider/authentication readiness gating and the shared runtime ownership
  lock remain Session 03 scope. Session 02 supplies the serial worker and safe
  snapshot required by that coordinator; it does not create a shell-side
  provider probe or inspect private checkpoints.
- The worker intentionally keeps `last_failure_code` as historical safe
  context after a later success. Session 03 must derive current acceptance
  from liveness, active capacity, configured dependencies, and snapshot
  freshness rather than treating this field as a permanent failure latch.
- The engine package files are a narrow public-contract correction required by
  the system plan's rule that deployment shutdown cannot become a learner
  cancellation. The shell still imports no private engine module or store.
- Phase 00 session artifacts moved to the archive because `plansession`
  retains only the current and previous phases. Their content is byte-for-byte
  unchanged.
- The existing raw request-metadata logging security finding is unchanged and
  remains assigned to Session 03 before new system routes become public.
- GDPR review is N/A for new collection or persistence. The worker transiently
  passes existing pseudonymous owner/job identifiers through the public
  facade but never logs, serializes, or adds storage for them.

## Behavior Changes

- Failed operating-system thread creation now returns the supervisor to a
  safely closable stopped state while preserving the original exception.
- Every executor attempt now has bounded start and terminal lifecycle events.
- Event payloads contain only fixed event names and finite reason codes; they
  exclude runnable identity and exception content.

## Security And Compliance Review

| Area | Result | Evidence |
|------|--------|----------|
| Authentication/authorization | N/A | No route or identity policy changed; the worker receives the already-authorized durable owner identity from the package |
| Input validation | PASS | New finite settings reject zero and excessive poll/shutdown durations |
| Injection | PASS | No SQL, shell, subprocess, template, deserialization, or dynamic execution surface added |
| Secrets | PASS | Only empty/documented environment names changed; no key, token, password, or credential value entered source |
| Data exposure | PASS | Snapshot and events omit job ID, owner ID, request data, provider detail, exceptions, and paths |
| Resource safety | PASS | One thread, one active handle, finite polling, stop-before-claim, reverse cleanup, and bounded drain are tested |
| Error handling | PASS | Worker errors use enums and safe text; cleanup never replaces an earlier startup/request error |
| Dependencies | PASS | No dependency or lockfile change |
| Database | N/A | No PostgreSQL/Alembic or engine SQLite schema/query change |
| GDPR | N/A | No new personal-data collection, storage, transfer, retention, or deletion path |

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first review regressions | Focused pytest `-k 'failed_thread_start or emits_bounded_execution'` | PASS | All 3 cases failed before repair, then passed after state reset and execution events |
| Focused Session 02 tests | `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/services/test_txt2crs_worker.py tests/test_txt2crs_lifespan.py tests/core/test_txt2crs_settings.py -q` | PASS | 62 tests passed |
| Complete shell tests | `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/ -q` | PASS | 255 tests passed; 63 existing short test-key warnings |
| Complete engine tests | `uv run --package txt2crs pytest -q` | PASS | 458 tests passed; 1 explicit live Codex/Tavily test skipped |
| Shell linter/type checks | `uv run ruff check app tests && uv run mypy app && uv run ty check app` | PASS | Ruff, strict mypy, and ty passed |
| Engine linter/type checks | `uv run --package txt2crs ruff check . && uv run --package txt2crs mypy` | PASS | Ruff and strict mypy passed |
| Secret/injection scan | Added-line scans for private-key markers, credential prefixes, dynamic execution, subprocesses, shell execution, and raw SQL | PASS | No committed secret, execution sink, or query surface found |
| Encoding/patch integrity | `git diff --check "$BASE"` plus ASCII scan over changed files | PASS | No whitespace or non-ASCII error |
| Final diff re-read | Complete `git diff "$BASE"` and untracked-file inventory | PASS | No unresolved finding, unrelated edit, debug artifact, or generated drift |

## Summary

1. Reviewed the complete base-to-head session surface.
2. Found 0 critical, 0 high, 2 medium, and 0 low issues.
3. Repaired both medium findings with regressions that failed first.
4. Full shell and engine suites, static checks, security spot-checks, encoding,
   and diff integrity pass.
5. No code, security, privacy, or workflow blocker remains.

Next command: `validate`
