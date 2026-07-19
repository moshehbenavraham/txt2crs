# Session 04: Managed Runtime and Model Policy

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Package**: backend/packages/txt2crs
**Status**: Not Started
**Estimated Tasks**: ~18-24
**Estimated Duration**: 2-4 hours

---

## Objective

Provide one bounded managed research and Codex runtime lifecycle that enforces
GPT-5.6 selection, fresh per-job limits, and non-blocking disabled
notification semantics.

---

## Scope

### In Scope (MVP)

- Managed loopback research MCP start, readiness, exact two-tool verification,
  stop, and join behavior.
- Typed bind, startup, timeout, and shutdown failures.
- Ordered research MCP, Codex app-server, HTTP, and temporary resource cleanup.
- GPT-5.6 family configuration, model discovery, and no-fallback enforcement.
- One schema-constrained live turn and allowlisted MCP tool-call compatibility
  gate.
- Fresh cancellation and run-budget state for every executor graph.
- Versioned notification mode/status with P0 `disabled` and
  `not_applicable` completion behavior.
- Success, failure, cancellation, and shutdown lifecycle tests.

### Out of Scope

- Browser device-code authentication routes and cached application readiness.
- SMTP, email outbox delivery, or P1 notification retries.
- FastAPI lifespan and serial worker supervision.

---

## Prerequisites

- [ ] Session 03 preparation gate proves that providers start only after
  accepted policy.
- [ ] The existing Codex protocol fixtures and two-tool research declaration
  are understood.

---

## Deliverables

1. Managed research MCP lifecycle and typed lifecycle errors.
2. GPT-5.6 discovery and exact-selection model policy.
3. Fresh per-job runtime resource and budget factories.
4. Disabled notification completion semantics.
5. Deterministic lifecycle tests and an explicit credential-gated live test.

---

## Success Criteria

- [ ] The research MCP URL becomes available only after exactly two tools are
  ready and the listener always closes.
- [ ] Configured GPT-5.6 absence makes the runtime unavailable; no older or
  first-discovered model is selected.
- [ ] Each executor graph receives fresh budget and cancellation state.
- [ ] Disabled notification records `not_applicable` and cannot block a
  completed delivery.
- [ ] Success, failure, cancellation, and shutdown leave no child process,
  HTTP client, temporary worker resource, or loopback listener.
