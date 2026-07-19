# Implementation Summary

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Package**: `backend/packages/txt2crs`
**Completed**: 2026-07-19
**Duration**: 1.6 hours

---

## Overview

Session 04 established one bounded provider lifecycle for future real
generation graphs. The engine can now own a verified loopback research MCP
server, compose and clean up temporary/HTTP/MCP/Codex resources in dependency
order, enforce exact GPT-5.6 entitlement and result identity without fallback,
create fresh per-job budget/cancellation state, and persist an explicit
disabled notification outcome independently from course completion.

## Deliverables

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `src/txt2crs/research/managed_mcp.py` | Pre-bound loopback server ownership, readiness, tool verification, and cleanup | 379 |
| `src/txt2crs/ai/model_policy.py` | Immutable four-slug GPT-5.6 policy and exact identity gates | 89 |
| `src/txt2crs/ai/job_runtime.py` | Fresh job state and ordered managed provider session | 219 |
| `src/txt2crs/jobs/notifications.py` | Versioned disabled/not-applicable notification contracts | 90 |
| `src/txt2crs/jobs/migrations/004_delivery_notifications.sql` | Durable notification-state upgrade and backfill | 23 |
| `tests/contract/test_managed_research_mcp.py` | Real and deterministic listener lifecycle coverage | 374 |
| `tests/unit/test_gpt56_model_policy.py` | Configuration/discovery/turn/result policy coverage | 103 |
| `tests/unit/test_job_runtime_resources.py` | Fresh state, readiness, cleanup order, and primary-error coverage | 344 |
| `tests/unit/test_delivery_notifications.py` | Strict notification policy/state coverage | 72 |

Paths in the table are relative to `backend/packages/txt2crs`.

### Files Modified

| Area | Changes |
|------|---------|
| Runtime and exports | Bound `CodexSubscriptionRuntime` to the model policy and exposed only supported AI/research/job contracts |
| Research MCP | Added actual FastMCP registry inspection and managed publication semantics |
| Executor | Replaced eager pipeline creation with an owned context kept open through result extraction |
| Delivery service/store | Removed notification-sink behavior, persisted exact notification state, and made migrations atomic |
| Tests/factories/live gate | Migrated fixtures to GPT-5.6, managed MCP, fresh resources, explicit disabled notifications, and exact live configuration |
| Dependencies | Declared directly imported Uvicorn and synchronized `backend/uv.lock` |

## Technical Decisions

1. **Pre-bind before threading**: Address conflicts are deterministic, and one
   object owns the only listener descriptor.
2. **Readiness is publishability**: A URL exists only while the Uvicorn thread
   is alive and the real FastMCP registry equals the reviewed two-tool tuple.
3. **Discovery proves; it never chooses**: The exact configured GPT-5.6 slug
   must be discovered before readiness and every turn and must match the
   adapter result.
4. **Provider ownership is one context**: Fresh mutable state and an
   `ExitStack` make cleanup order explicit and prevent cleanup failures from
   hiding the generation error.
5. **Migration and version are one write**: `BEGIN IMMEDIATE` serializes
   constructors, and each schema change commits atomically with its migration
   record.
6. **Disabled is durable state**: P0 delivery stores
   `1 / disabled / not_applicable`; it never infers behavior from null or calls
   a notification provider.

## Test Results

| Metric | Value |
|--------|-------|
| Tests Collected | 403 |
| Passed | 402 |
| Explicitly Gated | 1 live GPT-5.6/Tavily subscription test |
| Failed | 0 |
| Focused Runtime/Migration Selection | 94 passed, 1 gated |

Ruff format/lint, strict mypy, lock validation, fresh/upgrade/failure SQLite
migration verification, wheel/sdist build and member inspection, and the
repository engine validation command also passed.

## Code Review Repairs

The formal review resolved six findings:

1. Made SQLite schema/version migration application atomic and serialized.
2. Closed/revoked the managed listener on construction, registry, timeout, and
   unexpected-thread failures while exposing only typed safe errors.
3. Preserved primary generation errors when external context cleanup fails.
4. Kept provider resources open through final checkpoint and result
   extraction.
5. Rejected a composed runtime before yield when it is not ready.
6. Restricted managed listener configuration to explicit numeric loopback IPs.

## Lessons Learned

1. SQLite `executescript` is not suitable when migration statements and their
   version record must share an existing explicit transaction.
2. A server's `started` flag needs a live-thread stabilization check before an
   endpoint becomes provider-visible.
3. Exit stacks need safe adapters around third-party context managers, not
   only around explicitly closeable clients.
4. A managed factory must own validation and result extraction as well as the
   central provider call.
5. Exact provider policy needs three checks: discovery, requested identity,
   and returned identity.

## Future Considerations

1. Session 05 should compose the real and deterministic application factories
   exclusively from these managed boundaries.
2. Session 05 must implement idempotent owner-wide purge across SQLite
   requests/checkpoints/delivery rows, artifacts, and provider-owned state.
3. Phase 02 should map the package readiness projection into shell lifespan
   and routes without recreating discovery or resource ownership.
4. Phase 05 should run and preserve the explicit credentialed GPT-5.6 plus one
   Tavily research-call acceptance proof.

## Session Statistics

- **Tasks**: 24 completed
- **Files Created**: 9
- **Files Modified**: 19
- **Test Functions Added**: 33 plus parameterized cases
- **Code Review Findings**: 6 resolved
- **Success Criteria**: 23/23
- **Blockers**: 0
