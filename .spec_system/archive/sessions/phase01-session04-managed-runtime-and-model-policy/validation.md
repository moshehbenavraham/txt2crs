# Validation Report

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Package**: `backend/packages/txt2crs`
**Validated**: 2026-07-19
**Result**: PASS

## Validation Summary

| Check | Status | Notes |
|-------|--------|-------|
| Code Review | PASS | `code-review.md` is `RESOLVED`; all 6 findings are repaired |
| Tasks Complete | PASS | 24/24 tasks |
| Files Exist | PASS | 28/28 specified deliverables are non-empty |
| ASCII Encoding | PASS | 28/28 deliverables are ASCII with Unix LF and final newlines |
| Tests Passing | PASS | 402 passed, 1 explicitly gated live test skipped, 0 failed |
| Focused Runtime/Migration Tests | PASS | 94 passed, 1 explicitly gated live test skipped |
| Database/Schema Alignment | PASS | Fresh/upgrade/failure/reopen migration 004 paths pass atomically |
| Distribution | PASS | Wheel and sdist contain all 5 new shipping modules/migration |
| Success Criteria | PASS | 23/23 functional, testing, non-functional, and quality criteria |
| Static/Repository Gates | PASS | Lock, Ruff format/lint, strict mypy, and repository engine validation |
| Security & GDPR | PASS | No unresolved finding; Session 05 erasure path retained |
| UI Product Surface | N/A | No application shell or frontend file changed |

**Overall**: PASS

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Project state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Session 04 is active in Phase 01 and resolves to the engine package. |
| Prerequisites | `bash .spec_system/scripts/check-prereqs.sh --json --env --package backend/packages/txt2crs` | PASS | Environment and registered package pass. The generic migration-tool warning is N/A because the engine owns versioned SQLite SQL resources verified below. |
| Code review | Exact result parse plus review inventory | PASS | Review result is `RESOLVED`; 0 Critical, 2 High, 3 Medium, and 1 Low finding were fixed. |
| Task completion | Task-checkbox count in `tasks.md` | PASS | 24 complete, 24 total, 0 incomplete. |
| Deliverables | Explicit non-empty/scope loop over section 6 paths | PASS | 28/28 exist: 27 package files plus the synchronized workspace lockfile. |
| ASCII/LF | Byte, carriage-return, and final-newline scans over all 28 deliverables | PASS | Zero non-ASCII bytes, CRLF files, or missing final newlines. |
| Focused behavior | `uv run --package txt2crs pytest -q` over managed MCP, model/runtime, job resources, notifications/service, SQLite/request stores, executor, and live gate | PASS | 94 passed, 1 explicit live skip. |
| Full suite | `uv run --package txt2crs pytest -q` | PASS | 402 passed, 1 explicit live skip in 10.31 seconds. |
| Lock | `uv lock --check` | PASS | 154 packages resolve with a synchronized lock. |
| Format/lint | `uv run --package txt2crs ruff format --check .`; `uv run --package txt2crs ruff check .` | PASS | 127 files formatted; all checks pass. |
| Types | `uv run --package txt2crs mypy` | PASS | No issues in 127 source files. |
| Migration 004 | Real SQLite tests in the focused selection | PASS | Fresh schema, upgrade from version 3 with delivery data, exact backfill, reopen, failed migration rollback, and retry behavior pass. |
| Package build | `uv build --package txt2crs --out-dir <temp>` | PASS | Final release rerun built the `txt2crs-0.4.0` wheel and sdist successfully. |
| Archive inspection | Exact member lookup in wheel and sdist | PASS | `job_runtime.py`, `model_policy.py`, `notifications.py`, migration 004, and `managed_mcp.py` exist in both archives. |
| Repository validation | `bash scripts/validate-changes.sh engine --json` | PASS | Engine lint, strict typecheck, and tests all pass. |
| Security/privacy | Exact diff, secret/debug/process/model/bind scans, trust-boundary inspection, and `security-compliance.md` | PASS | No secret, public listener, model fallback, raw provider value, unbounded wait, unsafe dynamic execution, or PII log path remains. |
| Final diff | `git diff --check` and complete changed/untracked-file review | PASS | No whitespace error, scope leak, staged file, or unresolved validation issue. |

## Database And Migration Alignment

### Status: PASS

Migration `004_delivery_notifications.sql` is a package-owned SQLite migration,
not an application PostgreSQL/Alembic change. It adds explicit notification
version, mode, and status columns and backfills every old delivery row as
`1 / disabled / not_applicable`.

The migration runner now acquires the SQLite writer lock before reading
versions and executes complete migration statements plus version records
inside one transaction. A failed version-four migration leaves both schema and
version unchanged, so reopening can safely retry. Released migrations 001-003
were not rewritten.

## Success Criteria

### Functional Requirements: 10/10

- [x] Managed research MCP accepts only explicit numeric loopback binds and
  publishes only a live server with the exact two-tool registry.
- [x] Bind, startup, readiness timeout, registry, and shutdown failures use
  typed context-free package errors.
- [x] Successful, partially failed, unexpectedly stopped, timed-out, and
  repeatedly closed lifecycles revoke their URL and close the listener.
- [x] Provider resources close Codex, MCP, HTTP, then temporary storage across
  success, partial construction, runtime failure, cancellation, and shutdown.
- [x] Every job-runtime request creates distinct pristine budget and
  cancellation instances from its stored execution profile.
- [x] Executor provider contexts open only after accepted preparation is
  durable and stay open through final checkpoint/result extraction.
- [x] `gpt-5.6` is the default and configuration accepts exactly the four
  reviewed GPT-5.6 slugs.
- [x] Readiness and every turn require exact discovery, request, and adapter
  result identities; older, first-discovered, and substituted models fail.
- [x] Completion persists notification version 1, disabled mode, and
  not-applicable status without any notification sink.
- [x] Exact completion replay is idempotent and cannot change notification
  policy/state.

### Testing Requirements: 6/6

- [x] Tests-first failures are recorded for lifecycle, model policy, fresh
  resources, notification/migration, executor cleanup, and live gating.
- [x] A real loopback test proves connectivity only inside the ready context.
- [x] Recording contexts prove exact cleanup order for all required exits.
- [x] Real SQLite tests cover fresh and version-3 delivery-row upgrades.
- [x] The complete credential-free suite passes and the credentialed live test
  remains explicitly gated.
- [x] Both distribution formats contain all new runtime modules and migration.

### Non-Functional Requirements: 4/4

- [x] Public readiness/lifecycle errors omit provider error, credential,
  discovered list, port, path, payload, and thread internals.
- [x] Startup/shutdown waits are finite and repeated cleanup is safe.
- [x] The listener is numeric-loopback-only and Codex child construction still
  strips OpenAI, Codex, and Tavily API keys.
- [x] No FastAPI, frontend, SMTP, owner-purge, serial-worker, or hosted
  deployment behavior entered the session.

### Quality Gates: 3/3

- [x] All 28 deliverables are ASCII with Unix LF and final newlines.
- [x] Strict types, descriptive names, and intern-oriented comments explain
  ownership, publication, discovery, cleanup, freshness, and notification
  durability.
- [x] Ruff, mypy, pytest, migration verification, build/archive inspection,
  and repository engine validation pass.

## Conventions Compliance

### Status: PASS

- Reusable provider lifecycle/model/notification logic stays inside
  `backend/packages/txt2crs`; no shell route duplicates it.
- New Python contracts are fully typed, use descriptive names, and include
  comments at the ownership and trust boundaries.
- Stable package exceptions do not expose private provider details.
- Tests were authored and observed failing before production code and before
  every code-review repair.
- SQLite changes use the package migration directory; application Alembic and
  PostgreSQL are untouched.
- Uvicorn is declared directly because production imports it, and the
  workspace lock is synchronized.

## Security & GDPR Compliance

### Status: PASS

See `security-compliance.md`. No unresolved security or GDPR finding remains.
The existing consent boundary is preserved; no new personal field or logging
path was added; Session 05 remains responsible for owner-wide erasure.

## Behavioral Quality Spot-Check

### Status: PASS

**Files checked**:

- `research/managed_mcp.py`
- `ai/job_runtime.py`
- `ai/model_policy.py`
- `jobs/executor.py`
- `jobs/store.py`
- `jobs/service.py`

Trust boundaries, ownership, mutation freshness, failure paths, concurrency,
and stored-contract alignment pass. Validation required no additional repair
after the formal code-review fixes.

## UI Product-Surface Spot-Check

### Status: N/A

No FastAPI shell, route, React, generated client, CSS, or rendered product
surface changed.

## Validation Result

### PASS

All workflow gates, 28 deliverables, 23 success criteria, tests, static checks,
atomic migration paths, package archives, security/GDPR checks, and repository
engine validation pass. No repository-fixable issue remains.

### Unresolved Failures And Blockers

None.

## Next Steps

Next command: `updateprd`
