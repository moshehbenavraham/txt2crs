# Session 02: Serial Worker Supervisor

**Session ID**: `phase02-session02-serial-worker-supervisor`
**Package**: backend
**Status**: Not Started
**Estimated Tasks**: ~12-25
**Estimated Duration**: 2-4 hours

---

## Objective

Implement one tested serial supervisor that recovers runnable engine jobs,
creates one public executor graph per job, and guarantees bounded cancellation
and cleanup through application shutdown.

---

## Scope

### In Scope (MVP)

- Startup recovery and periodic runnable-job discovery through the facade.
- One active job at most with deterministic queue ordering.
- Per-job `ApplicationExecutor` creation, execution, cancellation, and close.
- Worker liveness, active-work, capacity, and shutdown state for readiness.
- Bounded polling and graceful application shutdown behavior.

### Out of Scope

- Learner submission, status, cancellation, and artifact HTTP routes.
- Parallel workers, external queues, or horizontal replicas.
- Readiness provider probes and operator login.

---

## Prerequisites

- [ ] Session 01 composition service owns the public facade.
- [ ] Phase 01 runnable recovery and executor handles remain validated.

---

## Deliverables

1. Tests for recovery, serial execution, retry-safe failures, cancellation,
   and shutdown.
2. Backend serial worker supervisor owned by the application lifespan.
3. Safe worker snapshot used by later readiness composition.
4. Structured worker and execution lifecycle events.

---

## Success Criteria

- [ ] Recovered runnable work is preferred without reading a private store.
- [ ] No more than one executor graph runs at a time.
- [ ] Every executor closes on success, failure, cancellation, and shutdown.
- [ ] Shutdown stops discovery, signals active work, waits within a bound, and
  reports failure safely.
- [ ] Worker state exposes no request content, provider detail, or path.
- [ ] Focused backend tests and static checks pass.
