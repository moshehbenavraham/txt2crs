# Implementation Notes

**Session ID**: `phase02-session01-engine-composition-lifecycle`
**Package**: backend
**Started**: 2026-07-19 19:02
**Last Updated**: 2026-07-19 19:18

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 7 / 24 |
| Estimated Remaining | 2.5 hours |
| Blockers | 0 |

---

## Task Log

### 2026-07-19 - Session Start

**Environment verified**:

- [x] Apex Spec prerequisites and backend package context confirmed
- [x] uv, Python, git, jq, and repository scripts available
- [x] Phase 01 public application exports import successfully
- [x] Local PostgreSQL started, credentials aligned with the development
  environment, and migrations advanced to head

---

### Task T001 - Verify Public Exports And Backend Baseline

**Started**: 2026-07-19 19:02
**Completed**: 2026-07-19 19:04
**Duration**: 2 minutes

**Notes**:

- Confirmed the three public Phase 01 composition types import from
  `txt2crs.application`.
- Resolved an occupied host port without stopping the unrelated container by
  starting the project database on its private Docker network.
- Aligned the project-local PostgreSQL role with `.env`, applied all Alembic
  migrations, and reran the focused baseline.

**Files Changed**:

- None - environment and public-contract verification only.

**Verification**:

- Command/check: `uv run python -c "from txt2crs.application import ..."`
  - Result: PASS - `RealApplicationConfig`, `RealApplicationFactory`, and
    `Txt2CrsApplication` imported.
  - Evidence: All three class names printed from the installed workspace.
- Command/check: `uv run alembic upgrade head`
  - Result: PASS - All seven application revisions applied.
  - Evidence: Alembic advanced through revision `fe56fa70289e`.
- Command/check: `uv run pytest tests/core/test_txt2crs_settings.py -q`
  - Result: PASS - 19 tests passed in 0.19 seconds.
  - Evidence: Focused settings baseline is green against the migrated project
    database.
- UI product-surface check: N/A - backend composition session.
- UI craft check: N/A - backend composition session.

---

### Task T002 - Create The Service-Test Package

**Started**: 2026-07-19 19:05
**Completed**: 2026-07-19 19:05
**Duration**: 1 minute

**Notes**:

- Added the package marker before introducing composition-service tests.

**Files Changed**:

- `backend/tests/services/__init__.py` - Documents the service-test boundary.

**Verification**:

- Command/check: `test -f backend/tests/services/__init__.py`
  - Result: PASS - The package marker exists.
  - Evidence: File contains one ASCII module docstring.
- UI product-surface check: N/A - backend test structure.
- UI craft check: N/A - backend test structure.

---

### Task T003 - Add Finite Composition Settings Tests

**Started**: 2026-07-19 19:05
**Completed**: 2026-07-19 19:08
**Duration**: 3 minutes

**Notes**:

- Added exact conservative P0 defaults for model, MCP, input, retry, run, and
  admission configuration.
- Added invalid-bound, non-loopback host, cross-budget, optional secret, and
  inherited-environment isolation scenarios.
- Kept P0 time-based artifact retention out of operator settings because the
  implementation plan explicitly defers that setting to P1.

**Files Changed**:

- `backend/tests/core/test_txt2crs_settings.py` - Adds the complete
  composition-settings contract.

**Verification**:

- Command/check: `uv run ruff check tests/core/test_txt2crs_settings.py`
  - Result: PASS - No lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run python -m py_compile tests/core/test_txt2crs_settings.py`
  - Result: PASS - Test module compiles before implementation exists.
  - Evidence: Command exited zero.
- UI product-surface check: N/A - backend settings tests.
- UI craft check: N/A - backend settings tests.

---

### Task T004 - Add Public Configuration Translation Tests

**Started**: 2026-07-19 19:08
**Completed**: 2026-07-19 19:11
**Duration**: 3 minutes

**Notes**:

- Specified exact immutable execution, storage, admission, provider, and MCP
  translation through public `txt2crs` contracts.
- Added an AST import allowlist so shell code cannot drift into private engine
  modules.
- The tests expose a Phase 01 contract mismatch: the package storage config
  currently cannot accept the already-adopted explicit SQLite/artifact paths
  or the nested same-volume Codex home. The implementation will correct that
  public package contract tests-first and record the cross-package files.

**Files Changed**:

- `backend/tests/services/test_txt2crs_application.py` - Defines exact shell
  translation and import-boundary behavior.

**Verification**:

- Command/check: `uv run ruff check tests/services/test_txt2crs_application.py`
  - Result: PASS - Import sorting fixed and no findings remain.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run python -m py_compile tests/services/test_txt2crs_application.py`
  - Result: PASS - Test module syntax is valid.
  - Evidence: Command exited zero.
- UI product-surface check: N/A - backend service tests.
- UI craft check: N/A - backend service tests.

---

### Task T005 - Add Factory And Cleanup Lifecycle Tests

**Started**: 2026-07-19 19:11
**Completed**: 2026-07-19 19:14
**Duration**: 3 minutes

**Notes**:

- Added recording application/factory doubles without constructing real
  provider resources.
- Covered duplicate start, idempotent close, absent configuration, retry after
  creation failure, cleanup failure, and log information boundaries.
- BQC drove explicit state reset after failure and reference clearing before a
  close that may raise.

**Files Changed**:

- `backend/tests/services/test_txt2crs_application.py` - Adds lifecycle,
  cleanup, retry, and safe-log scenarios.

**Verification**:

- Command/check: `uv run ruff check tests/services/test_txt2crs_application.py`
  - Result: PASS - No lint findings after import normalization.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run python -m py_compile tests/services/test_txt2crs_application.py`
  - Result: PASS - Test module syntax is valid.
  - Evidence: Command exited zero.
- UI product-surface check: N/A - backend lifecycle tests.
- UI craft check: N/A - backend lifecycle tests.

**BQC Fixes**:

- Resource cleanup: Tests require one close for normal and exceptional paths.
- Duplicate action prevention: Tests require duplicate start/close to be
  idempotent.
- State freshness on re-entry: Tests require retry after a failed start.
- Error information boundaries: Tests reject secret, path, and exception text
  in structured events.

---

### Task T006 - Add FastAPI Lifespan Integration Tests

**Started**: 2026-07-19 19:14
**Completed**: 2026-07-19 19:17
**Duration**: 3 minutes

**Notes**:

- Added configured and unconfigured lifespan ownership cases.
- Added sequential TestClient cycles to reject stale global lifecycle reuse.
- Added partial-startup cleanup and existing OpenAPI/liveness regression
  coverage.

**Files Changed**:

- `backend/tests/test_txt2crs_lifespan.py` - Defines application factory,
  lifespan ownership, route preservation, and cleanup behavior.

**Verification**:

- Command/check: `uv run ruff check tests/test_txt2crs_lifespan.py`
  - Result: PASS - No lint findings after import normalization.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run python -m py_compile tests/test_txt2crs_lifespan.py`
  - Result: PASS - Test module syntax is valid.
  - Evidence: Command exited zero.
- UI product-surface check: N/A - API liveness/OpenAPI regression only.
- UI craft check: N/A - backend lifespan tests.

**BQC Fixes**:

- Resource cleanup: Startup failure must still close the partial service.
- State freshness on re-entry: Sequential lifespans must receive distinct
  service objects.
- Contract alignment: Existing OpenAPI and liveness endpoints must remain
  available in both configured states.

---

### Task T007 - Record The Tests-First Red State

**Started**: 2026-07-19 19:17
**Completed**: 2026-07-19 19:18
**Duration**: 1 minute

**Notes**:

- Ran all three focused files together after writing the tests and before
  changing application code.
- Collection failed only on the intentionally absent composition module;
  production implementation has not begun.

**Files Changed**:

- None - verification task only.

**Verification**:

- Command/check: `uv run pytest tests/core/test_txt2crs_settings.py tests/services/test_txt2crs_application.py tests/test_txt2crs_lifespan.py -q`
  - Result: PASS - The required pre-implementation failure was observed.
  - Evidence: pytest stopped with two `ModuleNotFoundError` collection errors
    for `app.services.txt2crs_application`.
- UI product-surface check: N/A - backend tests-first checkpoint.
- UI craft check: N/A - backend tests-first checkpoint.

---

## Blockers & Solutions

### Blocker 1: Local PostgreSQL Port And State Drift

**Description**: Port 5447 belonged to an unrelated running project, and the
txt2crs volume required password alignment plus schema migrations.
**Impact**: T001 baseline pytest could not initialize the session fixture.
**Resolution**: Preserved the unrelated container, started txt2crs PostgreSQL
on its private Docker network, aligned the local role, and ran Alembic to head.
**Time Lost**: 2 minutes.

---

## Design Decisions

No implementation design decision recorded yet.

---

## Checkpoint

- Last completed task: T007
- Next task: T008 - add grouped typed composition settings.
- Checkpoint verification: Public exports import; original 19 settings tests
  pass; new focused suite fails only because the planned module is absent.
- Objective review: The tests cover exact config translation, one lifecycle
  owner, credential-free startup, cleanup, route preservation, and safe logs
  without adding worker, readiness API, or learner-job scope.
- Scope check: Work remains inside the backend composition session.
