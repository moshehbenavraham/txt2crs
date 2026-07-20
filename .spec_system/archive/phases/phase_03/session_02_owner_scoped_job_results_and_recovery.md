# Session 02: Owner-Scoped Job Results and Recovery

**Session ID**: `phase03-session02-owner-scoped-job-results-and-recovery`
**Package**: backend
**Status**: Complete
**Estimated Tasks**: 25
**Estimated Duration**: 2-4 hours

---

## Objective

Expose the complete private read and delivery lifecycle for one accepted job
and prove that backend restart and delivery replay preserve exact accepted
work without leaking internal state or regenerating model output.

---

## Scope

### In Scope (MVP)

- Owner-scoped status and completed-result projections.
- Owner-scoped artifact manifest and one-artifact download.
- Uniform missing/wrong-owner `404` behavior across every route.
- Polling revisions, terminal-state semantics, private/no-store headers, and
  conditional response behavior supported by the public projection.
- Safe content disposition, nosniff, integrity failures, bounded streaming,
  disconnect cleanup, and package-stream closure.
- Acceptance tests for two owners, refresh/poll behavior, provider-safe
  failures, restart at accepted and active checkpoints, and delivery replay.

### Out of Scope

- Job list/history, cancellation endpoint, or per-job deletion.
- HTML preview sandboxing in the browser.
- Account deletion or item-domain retirement.
- Frontend progress and results screens.

---

## Prerequisites

- [ ] Session 01 durably accepts owner-scoped jobs.
- [x] Phase 01 exposes safe projections, manifest/artifact handles, recovery,
  and exact checkpoint semantics.

---

## Deliverables

1. Route and acceptance tests for status, results, manifest, downloads,
   ownership, headers, and stream cleanup.
2. Restart fixtures covering accepted, preference/pipeline checkpoint, render,
   and delivery boundaries.
3. Strict public response schemas derived only from package projections.
4. Authenticated job/result/artifact routes using public facade handles.
5. Updated API documentation and generated-contract assertions.

---

## Success Criteria

- [ ] Job polling is monotonic, bounded, revisioned, and stops meaningfully at
  terminal state without exposing request/checkpoint/provider data.
- [ ] Completed results include only safe deliverable, source-summary, and
  conflict-disclosure fields.
- [ ] Wrong-owner and missing resources are indistinguishable `404` responses.
- [ ] Manifests expose stable artifact identifiers and metadata but no
  filesystem path.
- [ ] Downloads verify integrity, use safe filenames and headers, and close
  package streams on success, disconnect, and failure.
- [ ] Restart uses stored request/profile/checkpoints and delivery replay does
  not regenerate accepted model work.
- [ ] Focused acceptance, route, schema, type, lint, and generated-contract
  checks pass.
