# Implementation Notes

**Session ID**: `phase02-session01-engine-composition-lifecycle`
**Package**: backend
**Started**: 2026-07-19 19:02
**Last Updated**: 2026-07-19 19:54

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 24 / 24 |
| Estimated Remaining | 0 minutes |
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

### Task T008 - Add Grouped Typed Composition Settings

**Started**: 2026-07-19 19:18
**Completed**: 2026-07-19 19:21
**Duration**: 3 minutes

**Notes**:

- Added finite P0 settings for the exact GPT-5.6 family, managed MCP, inputs,
  retry, run budget, admission, artifacts, and Tavily timeout.
- Empty Tavily dotenv values normalize to `None`; no fake credential is
  created.
- Honored the P0 retention decision by keeping time-based retention out of
  operator settings; the composition layer will use the package maximum until
  coordinated P1 retention exists.

**Files Changed**:

- `backend/app/core/config.py` - Adds typed composition fields and optional
  secret normalization.

**Verification**:

- Command/check: `uv run python -m py_compile app/core/config.py`
  - Result: PASS - Configuration module compiles.
  - Evidence: Command exited zero.
- Command/check: `uv run python -c "from app.core.config import settings; ..."`
  - Result: PASS - Defaults load without a Tavily credential.
  - Evidence: Printed `gpt-5.6 20 True`.
- UI product-surface check: N/A - backend configuration.
- UI craft check: N/A - backend configuration.

**BQC Fixes**:

- Trust boundary enforcement: Every numeric environment input has a Pydantic
  range, and model selection uses an exhaustive literal.
- Error information boundaries: The provider secret uses `SecretStr` and an
  empty placeholder becomes absence.

---

### Task T009 - Add Topology And Cross-Field Validators

**Started**: 2026-07-19 19:21
**Completed**: 2026-07-19 19:23
**Duration**: 2 minutes

**Notes**:

- Restricted the research MCP to numeric loopback addresses.
- Rejected retry budgets, research-call totals, preview sizes, and admission
  relationships that cannot admit one finite job.
- Preserved explicit validation messages without echoing secret or path input.

**Files Changed**:

- `backend/app/core/config.py` - Adds loopback and complete-profile validators.

**Verification**:

- Command/check: `uv run pytest tests/core/test_txt2crs_settings.py -q`
  - Result: PASS - 41 settings tests passed.
  - Evidence: Existing path cases plus 22 new composition cases are green.
- Command/check: `uv run ruff check app/core/config.py tests/core/test_txt2crs_settings.py`
  - Result: PASS - No lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- UI product-surface check: N/A - backend configuration validation.
- UI craft check: N/A - backend configuration validation.

**BQC Fixes**:

- Trust boundary enforcement: Cross-field validation prevents individually
  valid environment values from forming an impossible runtime profile.
- External dependency resilience: MCP host and timeout inputs are bounded
  before any listener or provider resource starts.

---

### Task T010 - Build The Detached Execution Profile

**Started**: 2026-07-19 19:23
**Completed**: 2026-07-19 19:25
**Duration**: 2 minutes

**Notes**:

- Added the single shell translation point for immutable retry, input, run,
  model, prompt, policy, and engine-version identity.
- Used only public `txt2crs.jobs` contracts and the package version.
- Corrected the test field name to the existing public
  `passing_percentage` contract.

**Files Changed**:

- `backend/app/services/txt2crs_application.py` - Adds the detached public
  execution-profile builder.
- `backend/tests/services/test_txt2crs_application.py` - Aligns the preference
  assertion with the public contract.

**Verification**:

- Command/check: `uv run ruff check app/services/txt2crs_application.py`
  - Result: PASS - No lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run python -c "... build_execution_profile(settings) ..."`
  - Result: PASS - A strict profile constructs from credential-free defaults.
  - Evidence: Printed `gpt-5.6 20 txt2crs-0.5.0`.
- UI product-surface check: N/A - backend composition service.
- UI craft check: N/A - backend composition service.

**BQC Fixes**:

- Contract alignment: Uses public package models and existing preference field
  names.
- State freshness: Returns a new frozen profile for each composition call.

---

### Task T011 - Translate Storage, Admission, And Real Configuration

**Started**: 2026-07-19 19:25
**Completed**: 2026-07-19 19:31
**Duration**: 6 minutes

**Notes**:

- Added exact public storage, admission, Codex, worker, Tavily, MCP, and
  execution-profile translation.
- Returning `None` for absent/disabled research preserves credential-free
  startup without a synthetic secret.
- Corrected the package public storage contract to honor Phase 00's explicit
  SQLite/artifact paths and same-volume Codex home while keeping every
  boundary confined and non-overlapping.
- Added the package-owned ephemeral worker directory required by the system
  plan; real provider graphs no longer create workers inside persistent state.

**Files Changed**:

- `backend/app/services/txt2crs_application.py` - Adds real public config
  translation.
- `backend/packages/txt2crs/src/txt2crs/application/config.py` - Accepts,
  derives, canonicalizes, and confines explicit storage and worker paths.
- `backend/packages/txt2crs/src/txt2crs/application/factories.py` - Uses the
  exact validated database, artifact, and worker paths.
- `backend/packages/txt2crs/tests/contract/test_application_factories.py` -
  Adds same-volume, escape, overlap, worker, and exact-path tests before code.
- `backend/tests/services/test_txt2crs_application.py` - Requires worker-path
  translation.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/contract/test_application_factories.py -q`
  - Result: PASS - 23 package factory/config tests passed.
  - Evidence: The two initial explicit-path failures and two worker-path
    failures were observed before implementation, then the file passed.
- Command/check: `uv run --package txt2crs ruff check ...`
  - Result: PASS - No findings in package config, factory, or contract tests.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run python -c "... build_real_application_config ..."`
  - Result: PASS - Exact storage, worker, and GPT-5.6 values constructed.
  - Evidence: Printed `jobs.sqlite3 txt2crs-worker gpt-5.6`.
- UI product-surface check: N/A - backend/package composition.
- UI craft check: N/A - backend/package composition.

**BQC Fixes**:

- Resource cleanup: Factory continues to own stores and provider resources;
  only their validated locations changed.
- Trust boundary enforcement: Explicit child paths reject escape, symlinks,
  and overlap before filesystem creation.
- Contract alignment: Package config now matches the deployed backup and
  worker topology.

**Out-of-Scope Files**:

- `backend/packages/txt2crs/...` - Narrow public-contract correction required
  for the backend session to satisfy the already-adopted Phase 00 topology;
  no private engine implementation was imported by the shell.

---

### Task T012 - Define Lifecycle State And Factory Protocols

**Started**: 2026-07-19 19:31
**Completed**: 2026-07-19 19:33
**Duration**: 2 minutes

**Notes**:

- Added an injectable callable protocol that receives only
  `RealApplicationConfig` and returns the public `ApplicationFactory`.
- Added lock-protected facade, started, and configured state for later worker
  and readiness consumers.

**Files Changed**:

- `backend/app/services/txt2crs_application.py` - Adds protocols, production
  factory adapter, lifecycle constructor, and safe state properties.

**Verification**:

- Command/check: `uv run ruff check app/services/txt2crs_application.py`
  - Result: PASS - No lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run mypy app/services/txt2crs_application.py`
  - Result: PASS - Strict types pass after annotating schema version as its
    literal contract.
  - Evidence: mypy reported no issues.
- UI product-surface check: N/A - backend composition service.
- UI craft check: N/A - backend composition service.

**BQC Fixes**:

- Concurrency safety: All shared lifecycle state reads are protected by one
  reentrant lock.
- Contract alignment: Factory injection uses public package protocols only.

---

### Task T013 - Implement Configured And Unconfigured Start

**Started**: 2026-07-19 19:33
**Completed**: 2026-07-19 19:35
**Duration**: 2 minutes

**Notes**:

- Added one lock-protected start transition with duplicate-trigger prevention.
- Missing or disabled Tavily configuration enters a started but unconfigured
  state without invoking a factory.
- State is assigned only after factory success, so construction failure can be
  retried without a stale facade.

**Files Changed**:

- `backend/app/services/txt2crs_application.py` - Adds lifecycle start.

**Verification**:

- Command/check: `uv run python -c "... lifecycle.start(); lifecycle.start() ..."`
  - Result: PASS - Configured lifecycle created exactly one facade.
  - Evidence: Printed `True True 1` for started, configured, factory calls.
- Command/check: `uv run ruff check app/services/txt2crs_application.py`
  - Result: PASS - No lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- UI product-surface check: N/A - backend composition service.
- UI craft check: N/A - backend composition service.

**BQC Fixes**:

- Duplicate action prevention: Repeated start returns without constructing a
  second graph.
- State freshness on re-entry: Failed creation leaves started false and no
  application reference.

---

### Task T014 - Implement Idempotent Close And Failure Cleanup

**Started**: 2026-07-19 19:35
**Completed**: 2026-07-19 19:37
**Duration**: 2 minutes

**Notes**:

- Clears the facade and state flags before package cleanup so a raising close
  cannot be retried accidentally or leave a stale reference.
- Unconfigured and duplicate close operations remain harmless.

**Files Changed**:

- `backend/app/services/txt2crs_application.py` - Adds lifecycle close.

**Verification**:

- Command/check: `uv run pytest tests/services/test_txt2crs_application.py -q -k 'not lifecycle_events'`
  - Result: PASS - 7 tests passed and only the not-yet implemented logging
    case was deselected.
  - Evidence: Normal, duplicate, unconfigured, retry, and raising close cases
    are green.
- Command/check: `uv run mypy app/services/txt2crs_application.py`
  - Result: PASS - Strict types pass.
  - Evidence: mypy reported no issues.
- UI product-surface check: N/A - backend composition service.
- UI craft check: N/A - backend composition service.

**BQC Fixes**:

- Resource cleanup: Owned facade closes exactly once.
- Failure path completeness: Cleanup errors propagate after ownership state is
  made safe.

---

### Task T015 - Add Safe Structured Lifecycle Events

**Started**: 2026-07-19 19:37
**Completed**: 2026-07-19 19:39
**Duration**: 2 minutes

**Notes**:

- Added convention-compliant composition, configuration, and shutdown events.
- Failure events deliberately omit exception objects, config serialization,
  paths, secrets, and provider detail.

**Files Changed**:

- `backend/app/services/txt2crs_application.py` - Adds coarse structured
  lifecycle events and safe state reset on all base-exception paths.

**Verification**:

- Command/check: `uv run pytest tests/services/test_txt2crs_application.py -q`
  - Result: PASS - 8 tests passed.
  - Evidence: Safe-log test confirms event names and rejects secret, path, and
    exception text.
- Command/check: `uv run ruff check app/services/txt2crs_application.py`
  - Result: PASS - No lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- UI product-surface check: N/A - backend structured logs.
- UI craft check: N/A - backend structured logs.

**BQC Fixes**:

- Error information boundaries: Failure logs carry no private exception
  context.
- Failure path completeness: Start and close reset safe state before
  re-raising.

---

### Task T016 - Export The Shell Composition Service

**Started**: 2026-07-19 19:39
**Completed**: 2026-07-19 19:40
**Duration**: 1 minute

**Notes**:

- Documented the shell services boundary and exported only the lifecycle owner.

**Files Changed**:

- `backend/app/services/__init__.py` - Exports
  `Txt2CrsApplicationLifecycle`.

**Verification**:

- Command/check: `uv run python -c "from app.services import ..."`
  - Result: PASS - Public shell service imports.
  - Evidence: Printed `Txt2CrsApplicationLifecycle`.
- Command/check: `uv run ruff check app/services/__init__.py`
  - Result: PASS - No lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- UI product-surface check: N/A - backend module export.
- UI craft check: N/A - backend module export.

---

### Task T017 - Add The Injectable FastAPI Lifespan Owner

**Started**: 2026-07-19 19:40
**Completed**: 2026-07-19 19:43
**Duration**: 3 minutes

**Notes**:

- Added a `create_app` factory and fresh lifecycle construction on every
  lifespan entry.
- Stores only the shell lifecycle on application state and closes it from
  `finally`, including startup failures.

**Files Changed**:

- `backend/app/main.py` - Adds injectable FastAPI and lifecycle factories.

**Verification**:

- Command/check: `uv run pytest tests/test_txt2crs_lifespan.py -q`
  - Result: PASS - 4 lifespan tests passed.
  - Evidence: Configured, unconfigured, sequential, and failed startup cleanup
    cases are green.
- Command/check: `uv run mypy app/main.py`
  - Result: PASS - Strict app-factory types pass.
  - Evidence: mypy reported no issues.
- UI product-surface check: N/A - backend lifecycle.
- UI craft check: N/A - backend lifecycle.

**BQC Fixes**:

- Resource cleanup: FastAPI closes the lifecycle even when start raises.
- State freshness on re-entry: Each lifespan receives a new service.

---

### Task T018 - Preserve Existing Application Assembly

**Started**: 2026-07-19 19:43
**Completed**: 2026-07-19 19:45
**Duration**: 2 minutes

**Notes**:

- Kept the exported global app, telemetry instrumentation, RFC 9457 handlers,
  limiter, CORS, request logging, and router registration inside one factory.
- Existing liveness, health, login, and donor-item behavior remains intact.

**Files Changed**:

- `backend/app/main.py` - Completes reusable application assembly.

**Verification**:

- Command/check: `uv run pytest tests/api/routes/test_utils.py tests/api/routes/test_login.py tests/api/routes/test_items.py -q`
  - Result: PASS - 27 route tests passed.
  - Evidence: Existing health, auth, and item behavior is unchanged; 27
    pre-existing short-test-secret warnings remain.
- Command/check: `uv run python -c "from app.main import app; ..."`
  - Result: PASS - Global app has registered routes, two middleware layers,
    and the limiter.
  - Evidence: Printed `5 2`.
- UI product-surface check: N/A - existing API routes only.
- UI craft check: N/A - backend app assembly.

---

### Task T019 - Document Operator Composition Settings

**Started**: 2026-07-19 19:45
**Completed**: 2026-07-19 19:47
**Duration**: 2 minutes

**Notes**:

- Documented all finite P0 settings and a deliberately blank Tavily secret.
- Kept the research MCP loopback-only and did not add a published port.

**Files Changed**:

- `backend/.env.example` - Adds model, input, retry, run, admission, MCP, and
  provider placeholders.

**Verification**:

- Command/check: `uv run python -c "... composition-set(Settings.model_fields) ..."`
  - Result: PASS - Every documented txt2crs/Tavily name maps to a typed field.
  - Evidence: 41 composition settings documented; zero unknown names.
- UI product-surface check: N/A - operator dotenv reference.
- UI craft check: N/A - operator dotenv reference.

---

### Task T020 - Format And Lint Changed Python

**Started**: 2026-07-19 19:47
**Completed**: 2026-07-19 19:49
**Duration**: 2 minutes

**Notes**:

- Applied each package's Ruff formatter and import sorter.
- Rechecked all changed shell and engine Python files.

**Files Changed**:

- Changed backend and engine Python files - Mechanical Ruff formatting only.

**Verification**:

- Command/check: `uv run ruff check app/... tests/...`
  - Result: PASS - All changed shell files pass Ruff.
  - Evidence: Ruff reported `All checks passed!`.
- Command/check: `uv run --package txt2crs ruff check ...`
  - Result: PASS - All changed engine files pass package Ruff.
  - Evidence: Ruff reported `All checks passed!`.
- UI product-surface check: N/A - formatting task.
- UI craft check: N/A - formatting task.

---

### Task T021 - Run Focused Composition Tests

**Started**: 2026-07-19 19:49
**Completed**: 2026-07-19 19:50
**Duration**: 1 minute

**Notes**:

- Ran the complete tests-first shell slice after implementation and formatting.

**Files Changed**:

- None - verification task only.

**Verification**:

- Command/check: `uv run pytest tests/core/test_txt2crs_settings.py tests/services/test_txt2crs_application.py tests/test_txt2crs_lifespan.py -q`
  - Result: PASS - 53 tests passed.
  - Evidence: Settings, exact translation, lifecycle cleanup, logging, app
    re-entry, and existing-route cases are green.
- UI product-surface check: N/A - backend focused suite.
- UI craft check: N/A - backend focused suite.

---

### Task T022 - Run The Complete Backend Suite

**Started**: 2026-07-19 19:50
**Completed**: 2026-07-19 19:53
**Duration**: 3 minutes

**Notes**:

- The first full-suite run exposed order-dependent `caplog` capture because
  existing app setup replaces root handlers during collection.
- Replaced that assertion with an injected recording logger at the exact
  service boundary; the runtime behavior was unchanged and the full suite then
  passed.

**Files Changed**:

- `backend/tests/services/test_txt2crs_application.py` - Makes safe-event
  assertions independent of global logging handler order.

**Verification**:

- Command/check: `uv run pytest tests/ -q`
  - Result: PASS - 235 backend tests passed.
  - Evidence: Full suite completed in 7.84 seconds with 63 pre-existing
    short-test-secret JWT warnings.
- Command/check: `uv run ruff check tests/services/test_txt2crs_application.py`
  - Result: PASS - Logger-double correction has no lint findings.
  - Evidence: Ruff reported `All checks passed!`.
- UI product-surface check: N/A - backend full suite.
- UI craft check: N/A - backend full suite.

**BQC Fixes**:

- Contract alignment: The test now observes exact logger calls rather than a
  mutable root-handler side effect.

---

### Task T023 - Run Shell And Package Type Checks

**Started**: 2026-07-19 19:53
**Completed**: 2026-07-19 19:54
**Duration**: 1 minute

**Notes**:

- Checked the complete shell app and engine package after the public config
  correction.

**Files Changed**:

- None - verification task only.

**Verification**:

- Command/check: `uv run mypy app`
  - Result: PASS - 36 shell source files pass strict mypy.
  - Evidence: No issues found.
- Command/check: `uv run ty check app`
  - Result: PASS - Shell ty checks pass.
  - Evidence: ty reported `All checks passed!`.
- Command/check: `uv run --package txt2crs mypy`
  - Result: PASS - 136 engine source files pass strict mypy.
  - Evidence: No issues found.
- UI product-surface check: N/A - type verification.
- UI craft check: N/A - type verification.

---

### Task T024 - Verify Encoding, Diff, And Import Boundaries

**Started**: 2026-07-19 19:54
**Completed**: 2026-07-19 19:56
**Duration**: 2 minutes

**Notes**:

- Checked every file changed from the session base for clean patches, ASCII
  content, and text-only file types.
- Re-ran the AST-backed shell import allowlist against this project's private
  PostgreSQL address because host port 5447 belongs to an unrelated container.
- Ran the complete engine suite and the repository backend validation script
  so the narrow public package contract correction is covered beyond its
  focused factory tests.

**Files Changed**:

- None - verification task only.

**Verification**:

- Command/check: `git diff --check 0c779c910445e636db01a7bca284a72532ef57b6`
  plus ASCII and file-type checks over the changed-file list
  - Result: PASS - No whitespace errors, non-ASCII bytes, or non-text files.
  - Evidence: The combined boundary command exited zero with no output.
- Command/check: `uv run pytest tests/services/test_txt2crs_application.py -q -k shell_composition_imports_only_public_txt2crs_boundaries`
  - Result: PASS - 1 import-boundary test passed and 7 unrelated cases were
    deselected.
  - Evidence: Shell composition imports only documented public `txt2crs`
    modules.
- Command/check: `uv run --package txt2crs pytest`
  - Result: PASS - 453 deterministic package tests passed and 1 explicitly
    live-gated Codex case was skipped.
  - Evidence: The full engine package suite completed successfully.
- Command/check: `./scripts/validate-changes.sh backend`
  - Result: PASS - Repository backend validation completed successfully.
  - Evidence: Formatting, linting, typing, package, and shell checks passed;
    the script's standalone database-test step was skipped, while T022
    separately records the complete migrated database-backed suite.
- UI product-surface check: N/A - backend boundary verification.
- UI craft check: N/A - backend boundary verification.

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

- Last completed task: T024
- Next workflow step: `creview`.
- Checkpoint verification: 41 settings tests, 8 service tests, 4 lifespan
  tests, 23 package factory tests, 27 existing route tests, 235 complete shell
  tests, and 453 complete engine tests pass.
- Objective review: Composition owns one public facade, supports safe
  unconfigured startup, honors the deployed storage/worker topology, and adds
  no worker supervisor or system HTTP routes.
- Checkpoint verification: Public exports import; original 19 settings tests
  pass; new focused suite fails only because the planned module is absent.
- Objective review: The tests cover exact config translation, one lifecycle
  owner, credential-free startup, cleanup, route preservation, and safe logs
  without adding worker, readiness API, or learner-job scope.
- Scope check: Work remains inside the backend composition session.
