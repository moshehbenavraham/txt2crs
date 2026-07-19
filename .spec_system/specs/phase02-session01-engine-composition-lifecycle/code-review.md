# Code Review and Repair Report

**Session ID**: `phase02-session01-engine-composition-lifecycle`
**Package**: backend
**Reviewed**: 2026-07-19
**Base Commit**: `0c779c910445e636db01a7bca284a72532ef57b6`
**Scope**: All changes since the base commit (uncommitted work plus
mid-session commits)
**Result**: RESOLVED

## Review Surface

**Files reviewed** (all changes since the base commit):

- `.spec_system/specs/phase02-session01-engine-composition-lifecycle/code-review.md`
  - Review artifact created and reread during this command.
- `.spec_system/specs/phase02-session01-engine-composition-lifecycle/implementation-notes.md`
  - Mid-session implementation evidence.
- `.spec_system/specs/phase02-session01-engine-composition-lifecycle/spec.md`
  - Mid-session session specification.
- `.spec_system/specs/phase02-session01-engine-composition-lifecycle/tasks.md`
  - Mid-session completed task checklist.
- `.spec_system/state.json` - Mid-session workflow state.
- `backend/.env.example` - Operator composition settings.
- `backend/app/core/config.py` - Typed shell settings and cross-field
  validation.
- `backend/app/main.py` - FastAPI application factory and lifespan ownership.
- `backend/app/services/__init__.py` - Shell service export.
- `backend/app/services/txt2crs_application.py` - Public package translation
  and facade lifecycle.
- `backend/packages/txt2crs/src/txt2crs/application/config.py` - Public
  storage and worker configuration correction.
- `backend/packages/txt2crs/src/txt2crs/application/factories.py` - Exact
  storage and ephemeral worker path use.
- `backend/packages/txt2crs/tests/contract/test_application_factories.py` -
  Package configuration and factory regressions.
- `backend/tests/core/test_txt2crs_settings.py` - Shell setting regressions.
- `backend/tests/services/__init__.py` - Service-test package marker.
- `backend/tests/services/test_txt2crs_application.py` - Translation and
  lifecycle regressions.
- `backend/tests/test_txt2crs_lifespan.py` - FastAPI lifespan regressions.

No unrelated untracked files or binary/generated artifacts were present.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

- `backend/app/services/txt2crs_application.py:264` - A failure after
  `ApplicationFactory.create()` returned a facade reset the shell reference
  without closing the acquired facade. A logging-handler failure on the
  completion event demonstrated the leak, and a cleanup failure could also
  replace the primary startup exception. | Fix: Clear ownership first, attempt
  acquired-facade cleanup exactly once, emit safe best-effort failure events,
  and preserve the primary exception. Added the late-start regression in
  `backend/tests/services/test_txt2crs_application.py`. | Status: FIXED
- `backend/app/services/txt2crs_application.py:302` - The
  `shutdown_started` log ran before package cleanup and could raise before
  `application.close()`; the `shutdown_failed` logger could separately mask
  the authoritative package cleanup error. | Fix: Retain any pre-cleanup
  observer error while cleanup proceeds, surface it only after successful
  cleanup, and make error logging best-effort while a primary exception is in
  flight. Added both shutdown regressions in
  `backend/tests/services/test_txt2crs_application.py`. | Status: FIXED

### Medium

- `backend/packages/txt2crs/src/txt2crs/application/factories.py:530` - The
  dedicated authentication Codex app-server still received a working
  directory below persistent engine state even though this session introduced
  the configured ephemeral worker root. That directory would be included in
  whole-state backups and violated the reviewed Codex cwd topology. | Fix:
  Place authentication cwd at
  `RealApplicationConfig.worker_directory / "authentication"` and extend the
  real-factory cleanup test to assert the exact path. | Status: FIXED

### Low

No findings.

## Assumptions and Deliberate Non-Fixes

- Session specification status and success-criteria checkboxes remain owned by
  the later `updateprd` workflow step. The current `tasks.md` and
  `implementation-notes.md` correctly hand off to `creview`, so changing PRD
  completion state during this review would cross workflow responsibilities.
- The three engine package files are retained in this backend-primary session.
  Targeted inspection of the Phase 00 topology, the current session
  implementation notes, and the public shell import allowlist shows that they
  are the narrow public-contract correction required to honor exact SQLite,
  artifact, Codex-home, and worker paths. The shell still imports no private
  engine implementation.
- GDPR review is N/A. This session adds application composition and
  configuration only; it collects no new personal data and logs only coarse
  lifecycle state.

## Behavior Changes

- A facade returned during startup is now closed exactly once when a later
  startup operation fails, without replacing the original failure if cleanup
  or its observer also fails.
- Shutdown now always attempts facade cleanup even when the start-of-shutdown
  logger fails, while package cleanup errors remain authoritative.
- Dedicated system authentication now uses the configured ephemeral worker
  root instead of durable engine state for its Codex working directory.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first startup cleanup | `POSTGRES_SERVER="$TXT2CRS_DB_ADDRESS" POSTGRES_PORT=5432 uv run pytest tests/services/test_txt2crs_application.py -q -k late_start_failure` | PASS | Regression failed before repair because `close_calls` was 0, then passed after repair. |
| Tests-first authentication cwd | `uv run --package txt2crs pytest packages/txt2crs/tests/contract/test_application_factories.py -q -k authentication_build_fails` | PASS | Regression first observed durable `state/authentication-worker`, then passed with ephemeral `worker/authentication`. |
| Tests-first shutdown cleanup | `POSTGRES_SERVER="$TXT2CRS_DB_ADDRESS" POSTGRES_PORT=5432 uv run pytest tests/services/test_txt2crs_application.py -q -k 'shutdown_logging_failure or shutdown_failure_log'` | PASS | Both regressions failed before repair, then passed after cleanup ordering and primary-error preservation were corrected. |
| Complete shell tests | `POSTGRES_SERVER="$TXT2CRS_DB_ADDRESS" POSTGRES_PORT=5432 uv run pytest tests/ -q` from `backend/` | PASS | 238 tests passed; 63 existing short test-secret warnings. |
| Complete engine tests | `uv run --package txt2crs pytest` from `backend/packages/txt2crs/` | PASS | 453 deterministic tests passed; 1 explicitly credential-gated live Codex test skipped. |
| Shell linter | `uv run ruff check app tests` from `backend/` | PASS | Ruff reported all checks passed. |
| Engine linter | `uv run --package txt2crs ruff check .` from the engine package | PASS | Ruff reported all checks passed. |
| Shell formatter | `uv run ruff format --check app tests` from `backend/` | PASS | 74 files already formatted. |
| Engine formatter | `uv run --package txt2crs ruff format --check .` from the engine package | PASS | One review-test drift was formatted; all 136 files then passed. |
| Shell type checkers | `uv run mypy app && uv run ty check app` from `backend/` | PASS | 36 mypy source files and the complete ty app check passed. |
| Engine type checker | `uv run --package txt2crs mypy` from the engine package | PASS | 136 source files passed strict mypy. |
| Security and privacy spot-check | Targeted review of the complete base-to-head diff plus added-line scans for private-key markers, credential prefixes, dynamic execution, subprocesses, shell execution, and raw SQL | PASS | No committed secret, injection surface, dependency change, new PII collection, or private failure detail found. |
| Encoding and patch integrity | `git diff --check "$BASE"` plus ASCII scan over `git diff --name-only "$BASE"` | PASS | No whitespace error or non-ASCII content. |
| Final diff re-read | `git diff "$BASE"` plus `git ls-files --others --exclude-standard` | PASS | All 17 files were reread; no unresolved finding, debug artifact, unrelated edit, or untracked file remains. |

## Summary

1. Reviewed all 17 files in the deterministic base-to-head surface, including
   three mid-session commits and the final review artifact.
2. Found 0 critical, 2 high, 1 medium, and 0 low issues; all three findings
   were repaired with tests that failed before their corresponding fixes.
3. Deliberately left only workflow-owned PRD status updates for `updateprd`;
   no code or security finding remains.
4. Complete shell and engine tests, Ruff formatting/linting, mypy, ty,
   encoding, security spot-checks, and the final diff inspection pass.

Next command: `validate`
