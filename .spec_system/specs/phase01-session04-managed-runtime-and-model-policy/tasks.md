# Task Checklist

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Total Tasks**: 24
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[SNNMM]` session ref; `TNNN` task ID.

---

## Setup And Tests First (7 tasks)

- [x] T001 [S0104] Run the Apex Spec analyzer/prerequisites plus existing research MCP, official Codex adapter, runtime, budget, job service/store, executor, and live-gate baselines from the engine package root (`.spec_system/scripts/analyze-project.sh`, `backend/packages/txt2crs/tests/contract/test_research_mcp_server.py`, `backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py`, `backend/packages/txt2crs/tests/unit/test_runtime.py`, `backend/packages/txt2crs/tests/unit/test_budgets.py`, `backend/packages/txt2crs/tests/unit/test_job_service.py`, `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py`, `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`, `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`)
- [x] T002 [S0104] Write failing managed research MCP tests for loopback-only pre-bind, URL publication after readiness, actual two-tool registry verification, real listener reachability, bind/startup/timeout/tool/shutdown errors, idempotent close, and no leaked thread/socket (`backend/packages/txt2crs/tests/contract/test_managed_research_mcp.py`)
- [x] T003 [S0104] Write failing GPT-5.6 policy/runtime tests for the Sol alias default, exact four-slug allowlist, configured-model discovery, no older/first fallback, safe readiness, turn recheck, and adapter-result identity (`backend/packages/txt2crs/tests/unit/test_gpt56_model_policy.py`, `backend/packages/txt2crs/tests/unit/test_runtime.py`, `backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py`)
- [x] T004 [S0104] Write failing job-runtime tests for fresh pristine budgets/cancellation plus managed temporary/HTTP/MCP/Codex construction and exact reverse cleanup on success, construction error, turn error, cancellation, and outer shutdown (`backend/packages/txt2crs/tests/unit/test_job_runtime_resources.py`)
- [x] T005 [S0104] Write failing strict notification and real-SQLite migration tests for `disabled`/`not_applicable`, fresh database version 4, migration-3 backfill, exact replay, and zero sink semantics (`backend/packages/txt2crs/tests/unit/test_delivery_notifications.py`, `backend/packages/txt2crs/tests/unit/test_job_service.py`, `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py`, `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`)
- [x] T006 [S0104] Write failing executor tests proving the lazy pipeline is opened as a managed context only after preparation and closes after success, ordinary generation/factory failure, cancellation, and resumed delivery without provider construction (`backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`)
- [x] T007 [S0104] Rewrite the credential-gated live test expectation for exact `TXT2CRS_MODEL_ID` GPT-5.6, managed MCP, one schema result, and allowlisted tool call; run all new focused suites and record the expected pre-implementation failures (`backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`, `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/implementation-notes.md`)

---

## Foundation (5 tasks)

- [x] T008 [S0104] Implement immutable GPT-5.6 family configuration, default alias, exact discovery selection, and context-free model-policy errors (`backend/packages/txt2crs/src/txt2crs/ai/model_policy.py`)
- [x] T009 [S0104] Implement strict versioned disabled notification policy/state contracts and migration 004 without rewriting released migrations (`backend/packages/txt2crs/src/txt2crs/jobs/notifications.py`, `backend/packages/txt2crs/src/txt2crs/jobs/migrations/004_delivery_notifications.sql`)
- [x] T010 [S0104] Implement fresh `RunBudget`/`CancellationToken` construction from the exact stored run limits and immutable job-runtime resource contracts (`backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py`)
- [x] T011 [S0104] Implement the managed research MCP state machine and typed bind/startup/readiness/tool-contract/shutdown errors around an owned pre-bound loopback socket (`backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py`, `backend/packages/txt2crs/src/txt2crs/research/mcp_server.py`)
- [x] T012 [S0104] Update shared factories for canonical GPT-5.6 policy, fresh job resources, managed pipeline contexts, and disabled notification state (`backend/packages/txt2crs/tests/factories.py`)

---

## Implementation (7 tasks)

- [x] T013 [S0104] Complete real Uvicorn/FastMCP start, bounded readiness, exact registered-tool verification, URL publication, stop/join, socket cleanup, and real loopback regression behavior (`backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py`, `backend/packages/txt2crs/tests/contract/test_managed_research_mcp.py`, `backend/packages/txt2crs/pyproject.toml`, `backend/uv.lock`)
- [x] T014 [S0104] Implement the ordered `ExitStack` provider-session context for temporary worker root, HTTP client, managed MCP, and closeable Codex adapter, preserving primary errors and reversing every partial construction (`backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py`)
- [x] T015 [S0104] Enforce configured GPT-5.6 policy in Codex readiness, immediately before every turn, and on returned adapter identity without exposing discovered/provider-private values (`backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py`)
- [x] T016 [S0104] Change the executor's lazy pipeline factory to a managed context and preserve preparation-first construction, terminal settlement, cancellation, and provider-free delivery restart (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`, `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`)
- [x] T017 [S0104] Persist/read exact notification version/mode/status, remove nullable notification decisions and sink calls, and keep artifact/delivery completion idempotent across restart (`backend/packages/txt2crs/src/txt2crs/jobs/store.py`, `backend/packages/txt2crs/src/txt2crs/jobs/service.py`, `backend/packages/txt2crs/tests/unit/test_job_service.py`)
- [x] T018 [S0104] Export only supported managed lifecycle, model-policy, runtime-resource, and notification contracts from package boundaries and update public-query test composition (`backend/packages/txt2crs/src/txt2crs/research/__init__.py`, `backend/packages/txt2crs/src/txt2crs/ai/__init__.py`, `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`, `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`)
- [x] T019 [S0104] Update active official-adapter fixtures and the explicit live compatibility gate to GPT-5.6 with managed research MCP and no fallback; upgrade pinned SDK/CLI and regenerate protocol fixtures only if the live gate proves incompatibility (`backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py`, `backend/packages/txt2crs/tests/contract/test_codex_protocol_fixture.py`, `backend/packages/txt2crs/tests/fixtures/codex_protocol/`, `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`)

---

## Testing And Completion (5 tasks)

- [x] T020 [S0104] Run and repair all focused managed MCP, GPT-5.6 policy/runtime, job-resource, notification/migration, service, executor, adapter, and gated-live suites until ordering, cleanup, discovery, and durability assertions pass (`backend/packages/txt2crs/tests/contract/test_managed_research_mcp.py`, `backend/packages/txt2crs/tests/unit/test_gpt56_model_policy.py`, `backend/packages/txt2crs/tests/unit/test_job_runtime_resources.py`, `backend/packages/txt2crs/tests/unit/test_delivery_notifications.py`)
- [x] T021 [S0104] Run the complete credential-free engine suite and repair every session-caused regression, leaving the real GPT-5.6/Tavily acceptance explicitly gated (`backend/packages/txt2crs/pyproject.toml`)
- [x] T022 [S0104] Run Ruff formatting/lint and strict mypy from the engine package root and repair all findings (`backend/packages/txt2crs/pyproject.toml`)
- [x] T023 [S0104] Verify migration 004 on fresh/upgrade stores, build wheel/sdist, inspect managed/model/runtime/notification/migration members, and run repository engine validation (`backend/packages/txt2crs/src/txt2crs/jobs/migrations/004_delivery_notifications.sql`, `scripts/validate-changes.sh`)
- [x] T024 [S0104] Audit every session file for ASCII/LF, finite waits, no leaked listener/thread/client/temp resource, no fallback or private readiness/error values, update task evidence and implementation notes, and prepare the session for `creview` (`.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/implementation-notes.md`, `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/tasks.md`)

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] implementation-notes.md updated
- [x] Ready for `creview`

---

## Next Steps

Run `creview` for `phase01-session04-managed-runtime-and-model-policy`.
