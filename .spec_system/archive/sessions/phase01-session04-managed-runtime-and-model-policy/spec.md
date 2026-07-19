# Session Specification

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Phase**: 01 - Engine Application Boundary
**Status**: Planned
**Created**: 2026-07-19
**Base Commit**: 118695b4ca97e74b4ca85716d6813581ddb23da6
**Package**: backend/packages/txt2crs
**Package Stack**: Python 3.14, Pydantic v2, SQLite

---

## 1. Session Overview

This session turns the existing blocking research FastMCP application and
closeable Codex adapter into one bounded, testable provider lifecycle. A
managed loopback server will bind explicitly, verify the exact two-tool
contract, become addressable only after readiness, and stop and join on every
exit. A provider-session context will then own cleanup order across the Codex
app-server, research MCP listener, HTTP client, and temporary worker root.

The session also replaces permissive model selection with an explicit GPT-5.6
policy. The configured model must be one reviewed GPT-5.6 family slug and must
appear exactly in Codex app-server discovery. Readiness and every turn fail
closed when that condition is not met; neither an older model nor the first
discovered model is a fallback. The live compatibility test will use the same
policy, one schema-constrained result, and an allowlisted MCP research call.

Finally, the session makes every future executor graph start from fresh mutable
budget and cancellation state, makes the pipeline factory a managed context,
and replaces nullable notification delivery semantics with a strict versioned
P0 `disabled` / `not_applicable` record. These contracts prepare Session 05 to
publish the complete real and deterministic application factories without
reimplementing resource ownership.

---

## 2. Objectives

1. Provide one package-owned managed provider lifecycle with exact research
   tools, explicit GPT-5.6 discovery policy, fresh per-job mutable state, and
   durable non-blocking disabled notification semantics.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase01-session03-input-preferences-and-policy-gate` - Proves accepted
  preparation is durable before a provider-backed pipeline factory can open.
- [x] `phase01-session02-safe-queries-and-artifact-access` - Provides the
  delivery and public projection boundaries that notification changes must
  preserve.

### Required Tools Or Knowledge

- Existing `ResearchMcpApplication`, `ResearchToolService`,
  `OfficialCodexSdkAdapter`, `CodexSubscriptionRuntime`, `RunBudget`,
  `CancellationToken`, `GenerationJobExecutor`, and `JobService`.
- FastMCP streamable HTTP application plus a package-managed Uvicorn server.
- Codex app-server model discovery through the pinned official Python SDK.
- SQLite migration ownership under `txt2crs.jobs.migrations`.

### Environment Requirements

- Run package commands from `backend/packages/txt2crs/`.
- Default tests remain credential-free and external-network-free. A local
  loopback listener test is allowed and must close its descriptor.
- Live Codex/Tavily compatibility remains behind
  `TXT2CRS_RUN_LIVE_CODEX=1`.

---

## 4. Scope

### In Scope (MVP)

- A synchronous `ManagedResearchMcpServer` context that owns one pre-bound
  loopback socket, background server thread, bounded startup wait, exact
  FastMCP registry verification, stop signal, and bounded join.
- Typed and context-free bind, startup, readiness-timeout, tool-contract, and
  shutdown errors.
- A research MCP URL that is unavailable before readiness and after close.
- Idempotent close after a successful start and cleanup after partial startup
  failure.
- One managed provider-session context using deterministic reverse-order
  cleanup: Codex adapter/app-server, research MCP listener, HTTP client, then
  temporary worker directory.
- A fresh `RunBudget` and `CancellationToken` created from the exact stored
  execution profile for every job-runtime resource request.
- A context-managed durable pipeline factory boundary so executor success,
  generation failure, cancellation, and abrupt factory errors release provider
  resources.
- A strict immutable GPT-5.6 model policy whose default is `gpt-5.6` and whose
  reviewed values are exactly `gpt-5.6`, `gpt-5.6-sol`,
  `gpt-5.6-terra`, and `gpt-5.6-luna`.
- Exact configured-model discovery at readiness and immediately before each
  model turn, with adapter-result model identity validation.
- Safe readiness when the configured model is absent, with no discovered model
  list or private provider error exposed.
- One explicit live compatibility test using `TXT2CRS_MODEL_ID` (default
  `gpt-5.6`), managed research MCP, a schema-constrained turn, and one
  allowlisted research tool call.
- Strict versioned delivery-notification contracts with P0
  `mode=disabled` and `status=not_applicable`.
- A package SQLite migration that records notification schema version, mode,
  and status for old and new delivery rows without rewriting released
  migrations.
- Completion that stores artifacts and the disabled notification state, marks
  the job complete, and never calls or requires a notification sink.
- Public package exports for the supported lifecycle, model, runtime-resource,
  and notification contracts.

### Out Of Scope (Deferred)

- Complete real/deterministic ingestion, research, pipeline, executor, and
  public application facade factories - Session 05.
- Owner-wide SQLite/artifact/Codex purge - Session 05.
- FastAPI lifespan, runtime ownership lock, readiness cache, serial worker, and
  device-code routes - Phase 02.
- SMTP/email outbox modes, retries, warnings, and operator UI - P1.
- API-key fallback, non-OpenAI providers, automatic model substitution, or
  model-selection UI.
- Hosted or externally published research MCP endpoints.

---

## 5. Technical Approach

### Architecture

Add `txt2crs.research.managed_mcp`. `ManagedResearchMcpServer` receives one
`ResearchMcpApplication` and reviewed loopback bind settings. It creates and
binds the socket in the calling thread so address conflicts are reported
deterministically before a child thread starts. It passes that already-bound
socket to a Uvicorn server running the FastMCP streamable HTTP ASGI
application. The server URL remains private until both Uvicorn reports started
and the FastMCP registry contains exactly the two ordered reviewed tool names.

The manager stores no secret and exposes no arbitrary ASGI or server
configuration. Startup uses a monotonic deadline and small injected polling
interval. Partial startup calls the same bounded shutdown path. Close requests
server exit, joins the thread, closes the pre-bound socket, clears the public
URL state, and reports a typed shutdown error if the thread remains alive or
the server reports a fatal failure. Repeated close after a clean shutdown is
harmless.

Add `txt2crs.ai.model_policy`. `Gpt56ModelPolicy` is immutable and validates
the configured slug at construction. `require_discovered` accepts only an
exact match in the stable discovered-model tuple and never chooses a value.
`CodexSubscriptionRuntime` owns this policy. Readiness checks the authenticated
ChatGPT account and exact configured model. A turn must request that configured
model, rediscover it, and receive the same model identifier from the adapter
result before its schema output is accepted.

The explicit model target follows the current official OpenAI model guide:
`gpt-5.6` aliases `gpt-5.6-sol`; Sol is the flagship target. The public Codex
Python SDK documentation still demonstrates older slugs, so availability is
never inferred from documentation. App-server discovery through the pinned SDK
is authoritative for the authenticated account. The dependency pins change
only if the credential-gated test proves the pinned SDK/CLI cannot discover or
run the reviewed target.

Add `txt2crs.ai.job_runtime`. `JobRuntimeResourcesFactory.create` converts the
stored `RunExecutionLimits` to a new `RunBudgetLimits`, then constructs a new
`RunBudget` and `CancellationToken`. It must never cache either mutable
instance. A `ManagedProviderSessionFactory` receives narrow context factories
for the temporary worker root, HTTP client, managed research MCP, and Codex
adapter. It uses one `ExitStack`, enters resources in ownership order, and
yields a provider context only after the MCP and Codex runtime are ready.
Reverse exit order guarantees Codex closes before MCP, followed by HTTP and
temporary storage. Construction failure at any point unwinds already-entered
resources.

Strengthen `DurablePipelineFactory` in `jobs.executor` from eager `create` to
an `open` context-manager method. `GenerationJobExecutor` opens it only after
accepted preparation is durable and keeps construction, generation, final
checkpoint acceptance, and result extraction inside the context and terminal
failure settlement. Existing process-replacement behavior remains resumable;
ordinary errors settle safely and release the graph.

Add `txt2crs.jobs.notifications` with immutable
`DeliveryNotificationPolicy` and `DeliveryNotificationState` contracts. The
P0 policy constructor returns only `mode=disabled`; completion derives
`status=not_applicable`. Migration `004_delivery_notifications.sql` adds
version/mode/status columns to the existing delivery row and backfills old
rows as disabled/not-applicable. The legacy nullable timestamp can remain as a
storage-compatibility column but no application decision reads it.

`JobService` receives the explicit disabled policy rather than a sink.
Completion saves artifacts, records the payload hash and exact notification
state idempotently, then marks the job complete. Replays require both the
payload hash and notification state to match. No notification provider call
can delay, fail, or roll back a completed P0 course.

### Design Patterns

- Pre-bound managed listener: bind synchronously, then hand one owned socket to
  the background server.
- Readiness before publication: URL state appears only after server and exact
  tool-contract checks pass.
- Exact selection policy: configuration names the required model; discovery
  proves availability but never chooses a substitute.
- Exit-stack ownership: enter dependencies in use order and close them in
  deterministic reverse order.
- Fresh mutable job state: derive new counters and cancellation from immutable
  stored limits for every graph.
- Versioned disabled side effect: persist `not_applicable` instead of using
  null to imply notification behavior.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py` | Managed loopback bind, readiness, exact tools, stop, join, and typed lifecycle errors | ~300 |
| `backend/packages/txt2crs/src/txt2crs/ai/model_policy.py` | Immutable GPT-5.6 configuration and exact discovery policy | ~120 |
| `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py` | Fresh budget/cancellation resources and ordered provider-session context | ~280 |
| `backend/packages/txt2crs/src/txt2crs/jobs/notifications.py` | Versioned disabled notification policy and durable state | ~140 |
| `backend/packages/txt2crs/src/txt2crs/jobs/migrations/004_delivery_notifications.sql` | Backward-compatible notification version/mode/status columns | ~30 |
| `backend/packages/txt2crs/tests/contract/test_managed_research_mcp.py` | Real loopback and deterministic lifecycle/error coverage | ~320 |
| `backend/packages/txt2crs/tests/unit/test_gpt56_model_policy.py` | Default/family/discovery/no-fallback/runtime identity coverage | ~220 |
| `backend/packages/txt2crs/tests/unit/test_job_runtime_resources.py` | Fresh state and ordered provider cleanup coverage | ~300 |
| `backend/packages/txt2crs/tests/unit/test_delivery_notifications.py` | Strict disabled policy and durable state coverage | ~180 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/pyproject.toml` | Declare the directly imported managed ASGI server dependency if not already direct | ~2 |
| `backend/uv.lock` | Synchronize any direct dependency declaration | generated |
| `backend/packages/txt2crs/src/txt2crs/research/mcp_server.py` | Expose exact registered-tool inspection needed by the manager | ~35 |
| `backend/packages/txt2crs/src/txt2crs/research/__init__.py` | Export supported managed lifecycle contracts | ~30 |
| `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py` | Enforce configured GPT-5.6 policy at readiness/turn/result boundaries | ~100 |
| `backend/packages/txt2crs/src/txt2crs/ai/__init__.py` | Export model and job-runtime contracts | ~30 |
| `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` | Open the lazy pipeline factory as a managed context on every path | ~55 |
| `backend/packages/txt2crs/src/txt2crs/jobs/service.py` | Replace the sink with explicit disabled notification persistence | ~80 |
| `backend/packages/txt2crs/src/txt2crs/jobs/store.py` | Apply migration 004 and persist/read exact notification state | ~120 |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Export notification policy/state contracts | ~25 |
| `backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py` | Move active adapter fixtures to GPT-5.6 and prove exact result identity | ~60 |
| `backend/packages/txt2crs/tests/unit/test_runtime.py` | Exercise configured-model readiness and turn policy | ~100 |
| `backend/packages/txt2crs/tests/unit/test_job_service.py` | Replace sink assertions with disabled/not-applicable durable delivery assertions | ~180 |
| `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py` | Verify migration 004 and reopened delivery state | ~90 |
| `backend/packages/txt2crs/tests/integration/test_generation_request_store.py` | Update current migration-version expectations | ~15 |
| `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` | Prove managed pipeline cleanup after success/failure/cancellation/restart | ~160 |
| `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py` | Compose the explicit disabled notification policy | ~20 |
| `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py` | Use managed MCP and exact configured GPT-5.6 without fallback | ~120 |
| `backend/packages/txt2crs/tests/factories.py` | Supply canonical model policy, runtime resources, and disabled notification fixtures | ~100 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] The managed research MCP binds only an explicit loopback address and
  publishes its URL only after server readiness and exact two-tool
  verification.
- [ ] Bind, startup, readiness timeout, wrong tool registry, and shutdown
  failures use typed context-free package errors.
- [ ] Successful, partially failed, and repeatedly closed MCP lifecycles leave
  no background server thread or listening socket.
- [ ] Provider-session cleanup order is Codex, MCP, HTTP, then temporary worker
  storage on success, construction failure, turn failure, cancellation, and
  outer shutdown.
- [ ] Every job-runtime resource request receives a distinct pristine
  `RunBudget` and `CancellationToken` derived from the stored execution
  profile.
- [ ] The executor enters its provider-backed pipeline through a context
  manager only after accepted preparation is durable and exits it on every
  ordinary path.
- [ ] The configured default is `gpt-5.6`; only the four reviewed GPT-5.6
  family slugs are accepted.
- [ ] Readiness and every real turn require the exact configured model in
  discovery; older, first-discovered, and adapter-result substitutions fail
  closed.
- [ ] P0 completion persists notification schema version, `disabled` mode, and
  `not_applicable` status and performs zero notification-sink calls.
- [ ] Delivery replay remains idempotent and cannot change the stored
  notification policy or state.

### Testing Requirements

- [ ] Failing lifecycle, model-policy, fresh-resource, notification/migration,
  executor-cleanup, and live-gate tests are written and observed before
  production implementation.
- [ ] At least one real loopback test proves the listener accepts connections
  only while the managed context is ready and is closed afterward.
- [ ] Recording contexts prove exact cleanup order for success, construction
  failure, runtime failure, cancellation, and shutdown.
- [ ] Real SQLite tests apply migration 004 to both a fresh database and a
  migration-3 database with an existing delivery row.
- [ ] The complete credential-free engine suite passes and the explicit live
  test remains gated by credentials/configuration.
- [ ] The built wheel and sdist contain the managed MCP, model policy, job
  runtime, notification, and migration modules.

### Non-Functional Requirements

- [ ] No provider error, credential, discovered-model list, port, filesystem
  path, HTTP payload, or thread internals enter public readiness or typed
  lifecycle error messages.
- [ ] Startup and shutdown waits are finite; repeated cleanup is safe; no
  blocking sleep exceeds the configured deadline.
- [ ] The research listener remains loopback-only and the Codex child
  environment still strips OpenAI/Codex/Tavily API keys.
- [ ] No FastAPI, frontend, SMTP, owner-purge, serial-worker, or hosted
  deployment behavior enters this package session.

### Quality Gates

- [ ] All session-authored files are ASCII-encoded with Unix LF endings.
- [ ] Complete types and intern-friendly comments explain socket ownership,
  readiness publication, exact discovery, reverse cleanup, fresh state, and
  durable disabled notification semantics.
- [ ] Ruff format/lint, strict mypy, pytest, migration verification, package
  build, archive inspection, and repository engine validation pass.

---

## 8. Implementation Notes

### Working Assumptions

- Current official OpenAI model guidance says `gpt-5.6` aliases
  `gpt-5.6-sol`. The product requirement explicitly chooses that alias, so the
  default remains `gpt-5.6` even if other GPT-5.6 variants are discovered.
- Official Codex app-server documentation identifies `model/list` as the
  discovery operation. Documentation examples are not entitlement evidence;
  the authenticated SDK result is authoritative.
- The existing pinned Codex SDK already exposes account, model discovery,
  schema turns, cancellation, MCP configuration, and close. Pins change only
  after a failing live compatibility gate demonstrates an actual protocol gap.
- The managed MCP listener may use a local loopback socket in deterministic
  tests. External research/provider calls remain fake except in the explicit
  live test.
- The legacy `notified_at` SQLite column can remain for migration
  compatibility, but new application code must never derive mode or status
  from its nullability.
- Session 05 composes the concrete Tavily/research/pipeline/executor graph.
  Session 04 owns the reusable resource contexts and fresh-state contracts it
  must use.

### Conflict Resolutions

- Existing live acceptance falls back to GPT-5.4 or the first discovered
  model. The master plan and current official GPT-5.6 guidance win; the test
  must require the configured reviewed GPT-5.6 model or fail.
- Existing `ResearchMcpApplication.streamable_http_url` is available before a
  server is running. Readiness correctness wins; only the managed lifecycle
  exposes a usable URL to provider composition.
- Existing `JobService` treats null `notified_at` as pending and calls a sink
  before completion. Explicit P0 disabled semantics win; delivery records
  `not_applicable`, does not call a sink, and completion remains independent
  from email.
- Existing `DurablePipelineFactory.create` has no cleanup boundary. Resource
  ownership wins; the executor opens a context-managed factory after
  preparation and always exits it.

---

## 9. Dependencies

### Depends On

- `phase01-session03-input-preferences-and-policy-gate`
- Existing FastMCP application, official Codex SDK adapter, runtime budgets,
  job service/store, and executor.

### Enables

- `phase01-session05-public-facade-and-owner-lifecycle`
- Phase 02 real engine readiness and executor graph composition.
- Phase 05 explicit representative GPT-5.6 plus research live proof.

---

## 10. Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Background server startup races readiness or leaks a listener | Critical | Pre-bind one owned socket, publish only after dual readiness, and test real connect/close behavior |
| Cleanup error hides the original generation failure | High | Preserve primary exceptions while recording/raising typed cleanup failures only when no earlier failure is active |
| Model policy accepts a nearby or default model | Critical | Exact four-slug configuration allowlist plus exact configured discovery and adapter-result checks |
| SDK pin cannot expose GPT-5.6 | High | Keep deterministic policy green, run the explicit live gate, and upgrade SDK/CLI together only on demonstrated incompatibility |
| Mutable budget or cancellation leaks across jobs | High | Stateless factory construction and identity/counter isolation tests |
| Delivery migration changes existing rows ambiguously | High | Backfill explicit disabled/not-applicable values and test upgrade from migration 3 with a delivery row |
| Removing notification sink breaks restart delivery | Medium | Keep artifact and delivery writes idempotent; verify delivering-state replay with the explicit stored notification state |
| Managed resource abstraction duplicates Session 05 composition | Medium | Keep Session 04 factories provider-resource-only; leave concrete application/executor graph assembly to Session 05 |

---

## 11. References

- `.spec_system/PRD/PRD.md`
- `.spec_system/PRD/phase_01/PRD_phase_01.md`
- `.spec_system/PRD/phase_01/session_04_managed_runtime_and_model_policy.md`
- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/IMPLEMENTATION_SUMMARY.md`
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` sections 4.3, 5.7,
  5.8, 5.10, 7, 10, and 11
- `.spec_system/CONSIDERATIONS.md`
- `.spec_system/SECURITY-COMPLIANCE.md`
- `backend/AGENTS.md`
- `https://developers.openai.com/api/docs/guides/latest-model.md`
- `https://learn.chatgpt.com/docs/codex-sdk#python-library`
- `https://learn.chatgpt.com/docs/app-server#models`
- `backend/packages/txt2crs/src/txt2crs/research/mcp_server.py`
- `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py`
