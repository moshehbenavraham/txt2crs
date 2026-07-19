# Session 01: Durable Requests and Recovery

**Session ID**: `phase01-session01-durable-requests-and-recovery`
**Package**: backend/packages/txt2crs
**Status**: Complete
**Estimated Tasks**: ~18-24
**Estimated Duration**: 2-4 hours

---

## Objective

Atomically persist a strict immutable generation request and execution profile,
then discover and recover runnable work without reinterpreting accepted input.

---

## Scope

### In Scope (MVP)

- Strict versioned `GenerationRequest`, preference intent, age group, input
  payload, and immutable `ExecutionProfile` contracts.
- Canonical hashing across every generation-affecting field.
- A packaged SQLite migration for request envelopes and schema versions.
- Atomic create/load behavior that durably stores the envelope with a job.
- Owner-scoped idempotency replay and conflict behavior.
- Deterministic next-runnable discovery with recovery work prioritized over
  older accepted work.
- Restart tests that reopen exact request bytes and the stored execution
  profile.

### Out of Scope

- Public job projections and artifact streaming.
- Input routing, preference resolution, and post-ingestion policy.
- FastAPI routes, worker supervision, or frontend behavior.

---

## Prerequisites

- [x] Phase 00 is complete and the engine deterministic baseline passes.
- [x] Existing engine migration and job-store conventions are understood.

---

## Deliverables

1. Strict request, execution-profile, canonicalization, and error contracts.
2. SQLite migration plus transactional request persistence and load APIs.
3. Runnable-job discovery and restart recovery queries.
4. Tests covering replay, conflict, ordering, migration, rollback, and exact
   recovery.

---

## Success Criteria

- [x] A submission is not considered accepted until the complete request,
  profile, job, and reservation state commit atomically.
- [x] The same owner/key/request replays one job, while any changed
  generation-affecting field fails closed.
- [x] Restart recovery loads exact accepted input and profile versions without
  current-default substitution.
- [x] Runnable discovery prioritizes recovery/delivery work and then the
  oldest accepted job deterministically.
- [x] No shell import or provider credential is required by the tests.
