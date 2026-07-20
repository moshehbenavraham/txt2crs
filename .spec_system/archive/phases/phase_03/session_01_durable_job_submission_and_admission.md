# Session 01: Durable Job Submission and Admission

**Session ID**: `phase03-session01-durable-job-submission-and-admission`
**Package**: backend
**Status**: Complete
**Estimated Tasks**: 25
**Estimated Duration**: 2-4 hours

---

## Objective

Add the tests-first authenticated submission boundary for strict JSON and
multipart learner inputs, bounded streaming validation, cached readiness,
public-facade idempotency/admission, and durable `202 Accepted` semantics.

---

## Scope

### In Scope (MVP)

- Application acceptance fixtures using the real deterministic engine facade.
- Strict topic/text/URL/YouTube JSON input and document multipart metadata.
- Content-length and streaming byte bounds, content type, file signature, and
  bounded ZIP/OOXML structure validation.
- Owner-scoped idempotency key validation and canonical package mapping.
- Cached readiness, admission, rate-limit, and local public-signup policy.
- Durable submission response, location, revision, privacy headers, and worker
  nudge after commit.
- Stable RFC 9457 error translation using registered `ErrorCode` values.

### Out of Scope

- Job status, results, manifests, or artifact downloads.
- Learner cancellation, job library, or job deletion.
- Account deletion coordination or donor item removal.
- Product-specific frontend intake.

---

## Prerequisites

- [x] Phase 02 composition, readiness cache, worker, and exception translation
  are complete.
- [x] Phase 01 durable request, canonical idempotency, and admission contracts
  are available through the public facade.

---

## Deliverables

1. Tests for strict JSON/multipart parsing, all transport bounds, and forbidden
   provider work on rejection.
2. Tests for same-request replay, changed-request conflict, concurrent
   duplicate transport, readiness failure, admission failure, rate limits,
   and signup policy.
3. Typed submission request/response schemas and transport helpers.
4. Authenticated submit route using only public course-system services.
5. Structured allowlisted submission events and API documentation.

---

## Success Criteria

- [ ] Unknown fields and unsupported input combinations are rejected before
  facade submission.
- [ ] Oversize, mismatched, corrupt, or expansion-unsafe uploads fail before
  research or Codex resources open.
- [ ] `202` is returned only after exact request and reservation persistence.
- [ ] Same key and canonical request returns the original job without another
  reservation; a changed request returns `409`.
- [ ] System-not-ready and admission refusal create no job.
- [ ] Submission responses contain only safe stable identity, state, revision,
  and route information with private/no-store headers.
- [ ] Focused acceptance, route, schema, type, lint, and generated-contract
  checks pass.
