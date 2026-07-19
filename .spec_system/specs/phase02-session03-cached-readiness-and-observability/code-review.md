# Code Review and Repair Report

**Session ID**: `phase02-session03-cached-readiness-and-observability`
**Package**: backend
**Reviewed**: 2026-07-19
**Base Commit**: `73b395b0385dd0af3cb9841c61a38c7c6d153462`
**Implementation Commit**: `baefc6f`
**Scope**: Complete base-to-implementation diff and retained archive changes
**Result**: RESOLVED

## Review Surface

The exact base-to-head surface was reviewed across:

- Public readiness models, aggregate inspector, facade, factories, and
  application exports.
- SQLite migration/write-rollback and admission probes.
- Confined atomic artifact probe and cleanup.
- Shared runtime ownership, worker acquisition, cache freshness, refresh,
  startup, and shutdown.
- FastAPI settings, lifespan ownership, state exposure, and reverse cleanup.
- Package exception translation and semantic shell error codes.
- Request middleware, exception handlers, telemetry, SMTP, database startup,
  and worker event payloads.
- Focused and complete engine/shell tests.
- Apex session state, planned artifacts, and automatic archive retention.

The review emphasized side-effect boundaries, provider-runtime concurrency,
probe cleanup, finite shutdown, stale-state truthfulness, exception
information boundaries, request metadata, model identity, package layering,
secrets, injection surfaces, and denial-of-service bounds.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `backend/app/core/exception_handlers.py` and
  `backend/app/core/middleware.py` - Normal failure events retained raw
  request paths, response detail, validation payloads, or exception
  tracebacks. A password-recovery path or later source request could place
  personal or credential-bearing data into logs. | Fix: Use static matched
  route names, HTTP method, status, duration, finite error code, and bounded
  validation count only. Incoming trace IDs accept a strict bounded alphabet.
  Added middleware regressions that reject path, query, IP, headers, and body
  content. | Status: FIXED
- `backend/app/core/telemetry.py`, `backend/app/utils.py`, and database startup
  helpers - Telemetry/SMTP failure logs retained raw provider exception or
  response content, recipient identity, host/port detail, or traceback state.
  | Fix: Log only configuration state, timeout, and finite attempt count;
  database readiness failures now emit fixed event names only. Added SMTP and
  telemetry privacy regressions. | Status: FIXED
- `backend/app/services/txt2crs_readiness.py` - A direct refresh call after
  coordinator close could reacquire the gate and restart package/provider
  work during teardown. | Fix: Closed state now rejects refresh before
  ownership or package invocation. Added a post-close no-side-effect
  regression. | Status: FIXED

### Low

- `backend/packages/txt2crs/src/txt2crs/application/readiness.py` - A caller
  could construct an otherwise-ready runtime check with a model identifier
  other than the approved GPT-5.6 model. | Fix: Reuse
  `Gpt56ModelPolicy` during strict readiness-model validation. Added valid and
  invalid model identity tests. | Status: FIXED
- `backend/app/services/txt2crs_readiness.py` - Runtime contention preserved
  the last safe snapshot but labeled the result unavailable instead of
  degraded, hiding that known dependencies may still be healthy while
  execution owns the runtime. | Fix: Busy last-known state is explicitly
  degraded and non-accepting. Added exact state and warning coverage. |
  Status: FIXED

## Assumptions and Deliberate Non-Fixes

- HTTP readiness and authentication routes remain Session 04 scope. This
  session supplies their cached state and ownership boundary but exposes no
  new endpoint.
- Starting and polling device authentication remains Session 04 scope. The
  `authentication` owner is deliberately present now so the route cannot
  introduce a second lock later.
- The real provider and Tavily live proof remains explicitly credential-gated
  for release validation. Deterministic tests verify composition and safe
  projection without network access.
- The host port 5447 collision belongs to an unrelated container. Validation
  used the project's PostgreSQL container private address without mutating
  external state.
- Phase 01 session records moved byte-for-byte into the Apex archive and the
  oldest Phase 00 archive was removed to keep the configured retention cap.
- GDPR review is N/A for new personal-data collection. This session reduces
  existing log processing and adds only coarse, content-free readiness state.

## Behavior Changes

- Browser-facing readiness reads return immediately from immutable cached
  state and cannot launch provider, MCP, database, artifact, or scheduler
  work.
- Readiness, authentication, and job execution have one mutually exclusive
  runtime owner.
- Configured startup refreshes readiness before the worker starts; shutdown
  closes worker, cache, gate, and facade in reverse order.
- Busy, stale, worker-dead, shutting-down, unconfigured, dependency-failed,
  and recovered states are explicit and safe.
- Known public engine exceptions map to stable shell errors without retaining
  their cause, context, or message.
- Normal shell operational logs no longer include raw request/provider/error
  content.

## Security And Compliance Review

| Area | Result | Evidence |
|------|--------|----------|
| Authentication/authorization | N/A | No route or caller-authorization policy changed |
| Input validation | PASS | Readiness timing, trace ID, model identity, enums, and safe text are bounded |
| Injection | PASS | No raw SQL, shell, subprocess, template, deserialization, or dynamic execution surface added |
| Secrets | PASS | Only blank/documented environment names changed; no credential value entered source |
| Data exposure | PASS | Snapshots/events omit identity, request content, paths, queries, client data, provider payloads, exceptions, and credentials |
| Resource safety | PASS | One refresh thread, one worker thread, one runtime owner, non-blocking contention, and bounded shutdown are tested |
| Error handling | PASS | Translation uses semantic codes and generic details and severs exception context |
| Dependencies | PASS | No dependency manifest or lockfile changed |
| Database | PASS | Probes are package-owned, migration-aware, rollback-only or read-only, and leave no persistent probe state |
| GDPR | PASS | Existing log data is minimized; no new personal-data collection, storage, transfer, or retention path |

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first review regressions | Focused middleware, telemetry, SMTP, readiness, and aggregate pytest cases | PASS | Every repaired information-boundary, close-race, busy-state, and model-policy case passes |
| Focused Session 03 tests | Readiness, runtime, worker, settings, middleware, exceptions, lifespan, and aggregate slices | PASS | All focused cases pass |
| Complete shell tests | `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/ -q` | PASS | 273 passed; 63 existing short test-key warnings |
| Complete engine tests | `uv run --package txt2crs pytest -q` | PASS | 464 passed; 1 explicit live test skipped |
| Shell static checks | Ruff, strict mypy, and ty | PASS | All shell checks passed |
| Engine static checks | Ruff, strict mypy, and ty | PASS | All engine checks passed |
| Repository gate | `uv run pre-commit run --all-files` | PASS | Backend, frontend, generated-client, workflow, and format hooks passed |
| Secret/injection scan | Added-line scans and trust-boundary inspection | PASS | No committed secret, execution sink, unsafe query, or private provider payload |
| Encoding/patch integrity | ASCII/LF scan and `git diff --check "$BASE"` | PASS | No encoding, line-ending, or whitespace defect |
| Final diff re-read | Complete base diff plus status/untracked inventory | PASS | No unresolved finding, unrelated edit, debug artifact, or generated drift |

## Summary

1. Reviewed the complete base-to-implementation surface.
2. Found 0 critical, 0 high, 3 medium, and 2 low issues.
3. Repaired all five findings with focused regressions.
4. Complete deterministic suites, static gates, privacy checks, probe cleanup,
   public boundaries, encoding, and diff integrity pass.
5. No code, security, privacy, or workflow blocker remains.

Next command: `validate`
