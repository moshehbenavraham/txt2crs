# Implementation Notes

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Package**: backend/packages/txt2crs
**Started**: 2026-07-19 15:50 IDT
**Last Updated**: 2026-07-19 17:24 IDT

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 24 / 24 |
| Estimated Remaining | 3-4 hours |
| Blockers | 0 |

---

## Task Log

### 2026-07-19 - Session Start

**Environment verified**:

- [x] Apex Spec analyzer identifies the active Session 04 directory.
- [x] Package prerequisites pass for `backend/packages/txt2crs`.
- [x] Session 03 is completed and the clean base commit is
  `118695b4ca97e74b4ca85716d6813581ddb23da6`.
- [x] Engine SQLite uses package-owned migrations; this session will add
  migration 004 for delivery notification state.

---

### Task T001 - Verify The Existing Managed-Runtime Baseline

**Started**: 2026-07-19 15:50 IDT
**Completed**: 2026-07-19 15:51 IDT
**Duration**: 1 minute

**Notes**:

- Confirmed the active package and environment using the repository-local Apex
  Spec scripts.
- Proved the existing FastMCP application, official adapter, subscription
  runtime, budgets, delivery service/store, executor, and credential gate are
  green before production edits.
- Verified current official OpenAI guidance: `gpt-5.6` aliases
  `gpt-5.6-sol`, while Codex app-server `model/list` is the entitlement
  discovery boundary. The explicit project target therefore remains
  `gpt-5.6`; documentation examples never create a fallback.

**Files Changed**:

- `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/implementation-notes.md`
  - Recorded environment, official-guidance, and baseline evidence.

**Verification**:

- Command/check: `bash .spec_system/scripts/analyze-project.sh --json`
  - Result: PASS - Session 04 and its package-scoped spec/tasks were
    recognized.
- Command/check: `bash .spec_system/scripts/check-prereqs.sh --json --env --package backend/packages/txt2crs`
  - Result: PASS - All required environment and package checks passed; the
    generic database detector does not inspect package-owned SQLite
    migrations, which are covered by engine integration tests.
- Command/check: `uv run --package txt2crs pytest -q tests/contract/test_research_mcp_server.py tests/contract/test_official_codex_adapter.py tests/unit/test_runtime.py tests/unit/test_budgets.py tests/unit/test_job_service.py tests/integration/test_sqlite_job_store.py tests/integration/test_generation_job_executor.py tests/acceptance/test_live_codex_subscription.py`
  - Result: PASS - 55 tests passed and the one live Codex subscription test
    remained explicitly skipped behind `TXT2CRS_RUN_LIVE_CODEX=1`.
- Official documentation check:
  `https://developers.openai.com/api/docs/guides/latest-model.md` and
  `https://learn.chatgpt.com/docs/app-server#models`.
  - Result: PASS - The configured target and exact app-server discovery
    contract match the planned implementation.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**: None; this task established the unchanged behavioral baseline.

---

### Task T002 - Add Failing Managed Research MCP Lifecycle Tests

**Started**: 2026-07-19 15:51 IDT
**Completed**: 2026-07-19 15:55 IDT
**Duration**: 4 minutes

**Notes**:

- Defined one real ephemeral loopback listener scenario and deterministic
  controller fakes for bind, startup, timeout, tool-registry, and shutdown
  failures.
- Required the managed URL to exist only inside the ready context and required
  repeated cleanup to be safe.

**Files Changed**:

- `backend/packages/txt2crs/tests/contract/test_managed_research_mcp.py` -
  Added the managed listener contract suite.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/contract/test_managed_research_mcp.py`
  - Result: EXPECTED FAIL - Collection reports only the intentionally missing
    `txt2crs.research.managed_mcp` production module.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Resource cleanup: tests require the listener thread and socket to close after
  success and every partial failure.
- Trust boundary: non-loopback bind and tool-registry drift fail before a URL
  can reach provider composition.

---

### Task T003 - Add Failing GPT-5.6 Model Policy And Runtime Tests

**Started**: 2026-07-19 15:55 IDT
**Completed**: 2026-07-19 15:59 IDT
**Duration**: 4 minutes

**Notes**:

- Defined the exact alias/family configuration and discovery contract.
- Moved active runtime and SDK-adapter fixtures to GPT-5.6 and added
  no-fallback plus adapter-result substitution scenarios.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_gpt56_model_policy.py` - Added
  configuration, discovery, turn, result, and safe-error scenarios.
- `backend/packages/txt2crs/tests/unit/test_runtime.py` - Required one
  configured model policy for readiness and turns.
- `backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py` -
  Updated active SDK-shaped fixtures to GPT-5.6.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_gpt56_model_policy.py tests/unit/test_runtime.py tests/contract/test_official_codex_adapter.py`
  - Result: EXPECTED FAIL - Collection identifies only the planned missing
    `txt2crs.ai.model_policy` contract.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Contract alignment: discovery can prove only the exact configured model and
  cannot select a nearby or first-returned value.
- Information boundary: policy failures may name the reviewed configured
  family but never echo discovered provider values.

---

### Task T004 - Add Failing Fresh Job-Resource And Provider Cleanup Tests

**Started**: 2026-07-19 15:59 IDT
**Completed**: 2026-07-19 16:03 IDT
**Duration**: 4 minutes

**Notes**:

- Defined fresh budget/cancellation construction from the stored execution
  profile.
- Recording contexts require temporary, HTTP, MCP, and Codex resources to
  unwind in exact reverse order after normal, partial, failed, cancelled, and
  shutdown exits.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_job_runtime_resources.py` - Added
  fresh-state and provider ownership tests.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_job_runtime_resources.py`
  - Result: EXPECTED FAIL - Collection reports only the planned missing
    `txt2crs.ai.job_runtime` production module.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- State freshness: one job's reserved turn and cancellation do not affect the
  next factory result.
- Resource cleanup: every caller exit reason produces the same reverse close
  order, including partial construction.

---

## Next Task

Run `updateprd` for the validated Session 04 implementation.

---

### Task T005 - Add Failing Notification And Migration Tests

**Started**: 2026-07-19 16:03 IDT
**Completed**: 2026-07-19 16:10 IDT
**Duration**: 7 minutes

**Notes**:

- Replaced the test-only notification sink expectation with explicit
  `disabled` / `not_applicable` policy and durable state contracts.
- Required exact completion replay, provider-free failure behavior, version-3
  delivery backfill, and a second reopen that skips migration 004 rather than
  replaying its `ALTER TABLE` statements.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_delivery_notifications.py` -
  Added strict, immutable, closed-enum notification contracts.
- `backend/packages/txt2crs/tests/unit/test_job_service.py` - Removed sink
  semantics and required one durable disabled notification state.
- `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py` -
  Required migration 004 on fresh and upgraded databases.
- `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`
  - Advanced the expected packaged schema version.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_delivery_notifications.py tests/unit/test_job_service.py tests/integration/test_sqlite_job_store.py tests/integration/test_generation_request_store.py`
  - Result: EXPECTED FAIL - Collection identifies only the planned missing
    `txt2crs.jobs.notifications` contract.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Recovery correctness: released version-3 delivery rows must become explicit
  versioned disabled state.
- Side-effect boundary: no notification provider or nullable delivery branch
  remains available to the application service.

---

### Task T006 - Add Failing Managed-Pipeline Executor Tests

**Started**: 2026-07-19 16:10 IDT
**Completed**: 2026-07-19 16:17 IDT
**Duration**: 7 minutes

**Notes**:

- Changed the executor doubles from eager `create()` values to `open()`
  contexts that record entry and exit.
- Added explicit managed cleanup scenarios for normal completion, factory
  startup failure, model-generation failure, cancellation, and provider-free
  delivery recovery.

**Files Changed**:

- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
  - Required lazy context ownership and reverse-boundary cleanup.

**Verification**:

- Command/check: `python -m py_compile tests/integration/test_generation_job_executor.py`
  - Result: PASS - The rewritten context doubles and tests compile.
- Command/check: `uv run --package txt2crs pytest -q tests/integration/test_generation_job_executor.py`
  - Result: EXPECTED FAIL - Collection stops at the already-planned missing
    notification contract before the old eager factory can satisfy the suite.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Provider ownership: a yielded graph is always closed before the executor
  propagates success, failure, or cancellation.
- Recovery isolation: `rendering` and `delivering` restarts never call
  `pipeline_factory.open()`.

---

### Task T007 - Rewrite The Exact GPT-5.6 Managed-MCP Live Gate

**Started**: 2026-07-19 16:17 IDT
**Completed**: 2026-07-19 16:21 IDT
**Duration**: 4 minutes

**Notes**:

- Removed the acceptance test's free-port race, hand-built Uvicorn thread, and
  GPT-5.4/first-discovered fallback.
- The gate now uses `TXT2CRS_MODEL_ID` with the reviewed GPT-5.6 default,
  managed MCP ownership, exact runtime policy, one schema result, and exactly
  one completed `research_search` event.

**Files Changed**:

- `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`
  - Aligned the external compatibility proof with the shipping lifecycle and
  model policy.

**Verification**:

- Command/check: `python -m py_compile tests/acceptance/test_live_codex_subscription.py`
  - Result: PASS - The rewritten gated test compiles.
- Command/check: all 11 Session 04 focused suites.
  - Result: EXPECTED FAIL - Collection reports only the four planned missing
    modules: managed MCP, GPT-5.6 policy, job runtime, and notification state.
- Live external check: NOT RUN - Remains explicitly gated by
  `TXT2CRS_RUN_LIVE_CODEX=1` and real owner credentials.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Race removal: the test no longer probes and releases a port before server
  bind.
- Configuration integrity: blank, old, nearby, or undiscovered models cannot
  fall through to an arbitrary provider-returned entry.

---

### Task T008 - Implement The Immutable GPT-5.6 Model Policy

**Started**: 2026-07-19 16:21 IDT
**Completed**: 2026-07-19 16:24 IDT
**Duration**: 3 minutes

**Notes**:

- Added the exact four-slug reviewed family with `gpt-5.6` as the product
  default.
- Kept configured selection, entitlement discovery, turn identity, and result
  identity as separate checks with one context-free public error vocabulary.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/ai/model_policy.py` - Added immutable
  GPT-5.6 policy and exact checks.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_gpt56_model_policy.py`
  - Result: PASS - 13 tests passed.
- Command/check: Ruff on implementation and focused tests.
  - Result: PASS.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- No fallback: discovery order and sibling aliases cannot alter the configured
  model.
- Error hygiene: discovered values remain absent from policy exceptions and
  exception causes.

---

### Task T009 - Implement Notification Contracts And Migration 004

**Started**: 2026-07-19 16:24 IDT
**Completed**: 2026-07-19 16:28 IDT
**Duration**: 4 minutes

**Notes**:

- Added closed one-value mode/status enums and immutable versioned policy/state
  contracts.
- Added a new migration resource that appends checked non-null columns and
  explicitly backfills released delivery rows without editing migrations
  001-003.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/notifications.py` - Added explicit
  disabled policy and not-applicable state.
- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/004_delivery_notifications.sql`
  - Added the one-way delivery-state schema upgrade.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_delivery_notifications.py`
  - Result: PASS - 3 tests passed.
- Command/check: Ruff on notification implementation and tests.
  - Result: PASS.
- SQLite upgrade/reopen verification: PENDING T017 - The store intentionally
  does not register or read migration 004 until its nullable outbox API is
  replaced atomically.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Durable meaning: every stored delivery will carry a version, mode, and
  status with no nullable branch.
- Released-schema safety: earlier migration resources remain byte-for-byte
  unchanged.

---

### Task T010 - Implement Fresh Per-Job Runtime Resources

**Started**: 2026-07-19 16:28 IDT
**Completed**: 2026-07-19 16:32 IDT
**Duration**: 4 minutes

**Notes**:

- Added immutable attempt-resource and provider-session value contracts.
- Mapped every stored run-limit field explicitly into a new `RunBudget`, and
  created a new cancellation token on every factory call.
- Added the ordered provider-session owner in the same module; its complete
  lifecycle verification remains assigned to T014 after runtime policy wiring.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py` - Added fresh job
  state plus the managed provider-session contracts.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_job_runtime_resources.py -k fresh`
  - Result: PASS - 1 test passed and 5 lifecycle cases were deliberately
    deselected.
- Command/check: Ruff on runtime-resource implementation and tests.
  - Result: PASS.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Cross-job isolation: mutable counters and cancellation state cannot be
  reused by a later job.
- Schema drift defense: request limits flow through an explicit reviewed
  mapping rather than an unbounded model dump.

---

### Task T011 - Implement The Managed Research MCP Lifecycle

**Started**: 2026-07-19 16:32 IDT
**Completed**: 2026-07-19 16:42 IDT
**Duration**: 10 minutes

**Notes**:

- Added caller-thread loopback bind, pre-bound Uvicorn startup, bounded
  readiness polling, background error containment, URL publication only after
  actual FastMCP registry verification, and finite idempotent close.
- Added a synchronous actual-registry view to the application without trusting
  its static documentation tuple.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py` - Added the
  listener state machine and typed lifecycle errors.
- `backend/packages/txt2crs/src/txt2crs/research/mcp_server.py` - Added actual
  FastMCP tool-registry inspection.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/contract/test_managed_research_mcp.py tests/contract/test_research_mcp_server.py`
  - Result: PASS - 10 tests passed, including the real ephemeral listener.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Bind race: port reservation stays owned continuously from the calling thread
  through Uvicorn shutdown.
- Capability drift: the URL is never published unless the live FastMCP
  registry contains exactly the two reviewed research tools.
- Failure hygiene: raw background errors are retained privately and translated
  into bounded package exceptions.

---

### Task T012 - Align Shared Factories With Canonical Policies

**Started**: 2026-07-19 16:42 IDT
**Completed**: 2026-07-19 16:46 IDT
**Duration**: 4 minutes

**Notes**:

- Replaced the shared profile's repeated model string with the production
  default constant.
- Added narrow shared factories for canonical policy, fresh job attempt state,
  and the disabled notification policy; executor context doubles remain local
  because their lifecycle assertions are test-specific.

**Files Changed**:

- `backend/packages/txt2crs/tests/factories.py` - Aligned reusable composition
  values with production contracts.

**Verification**:

- Command/check: Ruff on `tests/factories.py`.
  - Result: PASS.
- Command/check: focused request/policy/notification/resource factory tests.
  - Result: PASS - 42 tests passed and 19 unrelated cases were deselected.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Fixture drift: shared model configuration can no longer diverge from the
  reviewed production default.
- Scope control: managed pipeline test doubles were not promoted into an
  unrelated generic factory module.

---

### Task T013 - Finalize Real Uvicorn Packaging And Lifecycle

**Started**: 2026-07-19 16:46 IDT
**Completed**: 2026-07-19 16:49 IDT
**Duration**: 3 minutes

**Notes**:

- Declared Uvicorn as a direct engine dependency because the engine imports
  and owns its ASGI server lifecycle.
- Regenerated the workspace lock without changing the already-resolved
  Uvicorn version.

**Files Changed**:

- `backend/packages/txt2crs/pyproject.toml` - Added the direct Uvicorn runtime
  dependency.
- `backend/uv.lock` - Recorded the engine's direct dependency edge.

**Verification**:

- Command/check: `uv lock`.
  - Result: PASS - 154 packages resolved.
- Command/check: real managed-MCP contract suite.
  - Result: PASS - 7 tests passed.
- Command/check: Ruff on managed MCP implementation and tests.
  - Result: PASS.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Packaging correctness: the wheel no longer depends on Uvicorn arriving only
  as an unrelated transitive dependency.

---

### Tasks T014-T015 - Complete Provider Ownership And Runtime Model Policy

**Started**: 2026-07-19 16:49 IDT
**Completed**: 2026-07-19 16:54 IDT
**Duration**: 5 minutes

**Notes**:

- Completed the `ExitStack` owner that enters temporary, HTTP, MCP, and Codex
  resources in dependency order and exits Codex, MCP, HTTP, and temporary
  resources in exact reverse order.
- Applied the configured model policy to readiness, per-turn discovery, and
  post-adapter result identity, translating failures into the existing safe
  runtime policy boundary.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py` - Completed managed
  provider-session composition.
- `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py` - Enforced exact
  configured GPT-5.6 identity at every runtime boundary.

**Verification**:

- Command/check: combined runtime, job-resource, and official adapter tests.
  - Result: PASS - 21 tests passed.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Partial construction: a failed Codex adapter still unwinds MCP, HTTP, and
  temporary resources.
- Turn substitution: adapter output cannot report an older or sibling model.
- Readiness privacy: unavailable discovery never echoes provider-returned
  values.

---

### Tasks T016-T017 - Manage Pipelines And Persist Notification State

**Started**: 2026-07-19 16:54 IDT
**Completed**: 2026-07-19 17:02 IDT
**Duration**: 8 minutes

**Notes**:

- Replaced the executor's eager pipeline value with a context-managed provider
  graph opened only after durable preparation.
- Registered migration 004 with skip-before-execute semantics, replaced
  nullable timestamp decisions with exact notification state reads/writes, and
  removed the notification sink from the application service.
- Completed replays now verify the existing payload hash and policy state
  without repeating artifact or provider work.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` - Added managed lazy
  pipeline ownership.
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - Added migration 004
  registration, one-time migration application, and explicit delivery state.
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py` - Removed sink calls
  and persisted policy-derived state.

**Verification**:

- Command/check: notification/service/SQLite/request persistence suites.
  - Result: PASS - 36 tests passed.
- Command/check: generation-job executor suite.
  - Result: PASS - 10 tests passed.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Migration replay: non-idempotent column additions are skipped after their
  recorded application.
- Completion semantics: no nullable field or provider call can block a
  completed job.
- Provider-free recovery: local rendering/delivery restart never opens the
  managed provider graph.

---

### Tasks T018-T019 - Finalize Public Contracts And Compatibility Gate

**Started**: 2026-07-19 17:02 IDT
**Completed**: 2026-07-19 17:07 IDT
**Duration**: 5 minutes

**Notes**:

- Exported the supported managed lifecycle, model-policy, job-runtime, and
  notification contracts without exposing internal controller details.
- Replaced the last read-only query test sink with the explicit disabled
  policy.
- Kept the pinned Codex SDK/CLI and protocol fixtures unchanged because the
  credential-free adapter contracts remain compatible and the external live
  gate has not demonstrated a pin incompatibility.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/ai/__init__.py`,
  `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`, and
  `backend/packages/txt2crs/src/txt2crs/research/__init__.py` - Added supported
  package exports.
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - Updated application composition.
- `backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py` and
  `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`
  - Aligned active and gated fixtures with GPT-5.6.

**Verification**:

- Command/check: public query plus supported contract suites.
  - Result: PASS - 28 tests passed.
- Command/check: package-boundary import smoke.
  - Result: PASS - Managed server, GPT-5.6 policy, job resources, and disabled
    notification policy import from their supported packages.
- Command/check: Ruff on package exports and query composition.
  - Result: PASS.
- External live gate: NOT RUN - Owner credentials and
  `TXT2CRS_RUN_LIVE_CODEX=1` were not supplied.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Public surface: controller protocols and implementation-only helpers remain
  internal.
- Dependency discipline: SDK and protocol pins change only after an explicit
  real-runtime incompatibility, not from documentation inference.

---

### Task T020 - Pass Every Focused Session 04 Suite

**Started**: 2026-07-19 17:07 IDT
**Completed**: 2026-07-19 17:08 IDT
**Duration**: 1 minute

**Notes**:

- Ran all lifecycle, policy, durability, application-service, executor,
  adapter, and gated compatibility cases in one process.
- No cross-module repairs were required after the implementation tasks.

**Verification**:

- Command/check: all 13 focused Session 04 test files.
  - Result: PASS - 96 tests passed; the one real subscription acceptance
    remained explicitly skipped.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**: None; the combined gate confirmed the individual boundaries
compose without regression.

---

### Task T021 - Pass The Complete Credential-Free Engine Suite

**Started**: 2026-07-19 17:08 IDT
**Completed**: 2026-07-19 17:09 IDT
**Duration**: 1 minute

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q`.
  - Result: PASS - 392 tests passed; the one real subscription acceptance
    remained explicitly gated.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**: None; no existing engine behavior regressed.

---

### Task T022 - Pass Formatting, Lint, And Strict Mypy

**Started**: 2026-07-19 17:09 IDT
**Completed**: 2026-07-19 17:13 IDT
**Duration**: 4 minutes

**Notes**:

- Applied Ruff formatting to six session files.
- Replaced static literal-only field annotations with exact runtime validators
  where tests and persisted strings deliberately cross dynamic boundaries.
- Cast the concrete Uvicorn controller only at its narrow protocol adapter and
  declared the context manager's non-suppressing `Literal[False]` result.

**Verification**:

- Command/check: `uv run --package txt2crs ruff format --check .`.
  - Result: PASS - 127 files already formatted.
- Command/check: `uv run --package txt2crs ruff check .`.
  - Result: PASS.
- Command/check: `uv run --package txt2crs mypy`.
  - Result: PASS - no issues in 127 source files.
- Post-repair focused regression:
  - Result: PASS - 30 policy, notification, migration, and listener tests
    passed.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Persisted parsing: database strings now enter the notification contract
  through explicit model validation.
- Protocol containment: Uvicorn's wider concrete signature is adapted once
  without weakening the testable lifecycle protocol.

---

### Task T023 - Verify Distributions, Migration, And Repository Checks

**Started**: 2026-07-19 17:13 IDT
**Completed**: 2026-07-19 17:14 IDT
**Duration**: 1 minute

**Verification**:

- Migration verification:
  - Result: PASS - Fresh version 4, version-3 backfill, exact read, close, and
    second reopen all pass in the SQLite integration suite.
- Command/check: build isolated sdist and wheel.
  - Result: PASS - `txt2crs-0.3.6.tar.gz` and
    `txt2crs-0.3.6-py3-none-any.whl` built successfully.
- Distribution member inspection:
  - Result: PASS - Both artifacts contain `job_runtime.py`,
    `model_policy.py`, `notifications.py`,
    `004_delivery_notifications.sql`, and `managed_mcp.py`.
- Command/check: `bash scripts/validate-changes.sh engine --json`.
  - Result: PASS - lint, strict mypy, and 392-test engine steps all passed.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Shipping completeness: runtime code and the required migration are present
  in both supported distribution formats.

---

### Task T024 - Complete The Final Session Audit

**Started**: 2026-07-19 17:14 IDT
**Completed**: 2026-07-19 17:24 IDT
**Duration**: 10 minutes

**Notes**:

- Audited every tracked/untracked session file for ASCII, LF, whitespace,
  finite waits, fallback/sink remnants, and package scope.
- Added two tests-first audit regressions: provider cleanup cannot replace a
  primary generation failure, and a controller that exits immediately after
  setting `started` cannot publish a stale URL.
- Adapter-close failure now produces a safe cleanup error only when no primary
  error exists; otherwise it adds a safe note and preserves reverse cleanup.
- Listener readiness now requires a live stabilization interval, and any
  unexpected controller exit revokes the published URL.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py` and
  `backend/packages/txt2crs/tests/unit/test_job_runtime_resources.py` -
  Preserved primary errors across cleanup.
- `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py` and
  `backend/packages/txt2crs/tests/contract/test_managed_research_mcp.py` -
  Rejected transient/dead readiness.

**Verification**:

- Tests-first audit regressions:
  - Result: EXPECTED FAIL - Each regression first reproduced its lifecycle
    defect before the production repair.
- Focused repaired lifecycle suites:
  - Result: PASS - 7 provider-resource tests and 8 managed-listener tests.
- Final complete suite:
  - Result: PASS - 394 tests passed; one real subscription test remained
    explicitly gated.
- Final static checks:
  - Result: PASS - Ruff and strict mypy remain clean across 127 files.
- `git diff --check`, ASCII scan, CRLF scan, removed-fallback/sink scan:
  - Result: PASS - No whitespace, encoding, line-ending, production fallback,
    or removed notification API finding.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Primary-error preservation: cleanup diagnostics no longer hide the job
  failure that initiated stack unwinding.
- Readiness integrity: a transient started flag cannot make a dead endpoint
  provider-visible.

---

## Session Completion

- Tasks: 24 / 24 complete
- Focused tests: 98 passed, 1 externally gated
- Full tests: 394 passed, 1 externally gated
- Ruff format/lint: PASS
- Strict mypy: PASS
- Wheel/sdist inspection: PASS
- Repository engine validation: PASS
- Blockers: 0

---

## Code Review

**Completed**: 2026-07-19

- Reviewed every changed and initially untracked file since base commit
  `118695b4ca97e74b4ca85716d6813581ddb23da6`.
- Added tests-first regressions and repaired six findings: atomic migrations,
  primary-error-preserving cleanup, managed listener cleanup/error
  translation, provider-context lifetime, composed-runtime readiness, and
  numeric-loopback enforcement.
- Final review evidence is 402 passed, 1 intentionally gated live skip, plus
  clean Ruff formatting/lint and strict mypy.
- Review result: `RESOLVED`.

---

## Validation

**Completed**: 2026-07-19

- Verified 28/28 specified deliverables and 23/23 success criteria.
- Re-ran 402 passing tests with one explicit credential-gated live skip,
  94 focused runtime/migration tests with the same gate, and clean lock, Ruff,
  mypy, package build/archive, migration, security/GDPR, and repository engine
  checks.
- Validation result: `PASS`; no unresolved failure or blocker remains.

---

## Release Preparation

**Completed**: 2026-07-19

- Selected `0.4.0` because this session adds supported public engine features
  and intentionally changes pre-1.0 runtime/factory contracts.
- Synchronized `VERSION`, package metadata, `backend/uv.lock`, and
  `docs/VERSIONING.md`.
- Archived the prior `0.3.5` and `0.3.6` entries into
  `docs/archive/CHANGELOG_20260719.md` and recorded the new release in the
  active changelog.
- Final release rerun: 402 passed, 1 explicit live skip; clean Ruff and mypy;
  synchronized lock; and inspected `txt2crs-0.4.0` wheel/sdist.
