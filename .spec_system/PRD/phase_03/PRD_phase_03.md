# PRD Phase 03: Durable Jobs API

**Status**: In Progress
**Sessions**: 3 (reconciled estimate)
**Estimated Duration**: 2-3 days

**Progress**: 2/3 sessions (67%)

---

## Overview

Phase 03 turns the completed engine boundary and FastAPI composition graph into
the complete private learner API. It accepts bounded JSON or multipart input,
returns `202 Accepted` only after the exact request and admission reservation
are durable, exposes safe owner-scoped progress and results, streams
integrity-checked artifacts, proves restart and delivery replay, coordinates
account erasure across both stores, and removes the temporary donor `items`
domain.

The shell continues to own HTTP, authenticated PostgreSQL identity, rate
limits, request framing, and safe error translation. The `txt2crs` package
continues to own canonical requests, idempotency, admission, generation,
recovery, projections, artifact integrity, and owner purge.

---

## Progress Tracker

| Session | Name | Status | Est. Tasks | Validated |
|---------|------|--------|------------|-----------|
| 01 | Durable Job Submission and Admission | Complete | 25 | 2026-07-20 |
| 02 | Owner-Scoped Job Results and Recovery | Complete | 25 | 2026-07-20 |
| 03 | Account Purge and Donor Retirement | Not Started | 24 | - |

---

## Completed Sessions

- Session 01: Durable Job Submission and Admission - completed 2026-07-20.
- Session 02: Owner-Scoped Job Results and Recovery - completed 2026-07-20.

---

## Upcoming Sessions

- Session 03: Account Purge and Donor Retirement

---

## Objectives

1. Validate strict JSON and multipart requests with finite transport,
   metadata, content-type, file-signature, and OOXML expansion bounds.
2. Map authenticated shell identity and typed input to the public engine
   request without reimplementing canonicalization, policy, persistence, or
   admission.
3. Return `202 Accepted` only after the exact request and admission reservation
   are durably committed; duplicate retries return the original job and
   changed requests conflict.
4. Expose bounded public-safe job/result projections, artifact manifests, and
   one integrity-checked artifact stream under owner-scoped missing-or-wrong
   owner `404` semantics.
5. Apply polling-friendly revisions, private/no-store caching, download
   hardening, and deterministic stream cleanup.
6. Prove exact restart at accepted and active checkpoints and replay delivery
   without regenerating accepted model work.
7. Purge engine-owned state before either PostgreSQL user deletion path and
   represent partial failure truthfully.
8. Remove the donor item API, model, CRUD, constants, tests, docs, and
   read-only admin MCP tools after jobs acceptance is green.
9. Drop the item table through Alembic and verify clean/existing upgrades plus
   a supported downgrade/upgrade round trip.
10. Regenerate OpenAPI and the frontend client only through
    `scripts/generate-client.sh`.

---

## Prerequisites

- Phase 02 completed with one lifespan-owned facade, one serial worker, cached
  readiness, safe exception translation, and protected system setup.
- Phase 01 public request, projection, artifact, recovery, and owner-purge
  contracts remain authoritative.
- The backend continues to run as exactly one application process.
- Local Docker Compose remains the only deployment target.

---

## Planning Assumptions And Resolutions

### Working Assumptions

- Shell request schemas may validate HTTP framing and transport bounds, but
  the engine remains authoritative for canonical generation requests,
  ingestion, content policy, idempotency, admission, and durable state.
- Multipart upload validation is streaming and fail-fast. The shell may spool
  bounded bytes for the package input contract, but it does not extract,
  interpret, or sanitize learner content itself.
- Public job polling returns only the package safe projection plus explicit
  HTTP revision/cache metadata. It never serializes a request envelope,
  checkpoint, provider response, prompt, evidence excerpt, filesystem path,
  or token/cost detail.
- Wrong-owner and missing jobs or artifacts are intentionally
  indistinguishable. Artifact streams close on normal completion,
  disconnect, and integrity failure.
- The item table downgrade can recreate the empty donor schema but cannot
  recover intentionally deleted donor rows.

### Conflict Resolutions

- The implementation plan suggests two Phase 03 sessions using historical
  labels S05 and S06. The scope combines three independent risk boundaries:
  request acceptance, private delivery/recovery, and cross-store
  erasure/schema retirement. Two sessions would exceed the Apex Spec 12-25
  task and 2-4 hour limits. Phase 03 therefore uses three sequential session
  identifiers beginning at S01 without changing the work or exit gate.
- Learner cancellation and library/history remain deferred in the master PRD.
  Phase 03 represents existing cancelled/review-required states in safe
  projections but does not add new cancellation or list routes.
- The generated TypeScript client changes in Session 03 as a derivative of
  backend OpenAPI ownership. Product-specific frontend routes remain Phase 04.

---

## Technical Considerations

### Architecture

FastAPI routes depend on the current authenticated user and the existing
lifespan-owned course-system services. Submission performs shell-owned framing
checks, checks the cached readiness gate, calls the public facade once, and
nudges the serial worker only after durable acceptance. Safe reads call public
facade query handles and add HTTP cache/privacy headers without reaching into
SQLite or artifact paths.

Account deletion establishes a worker barrier through the public owner-purge
operation before deleting PostgreSQL identity. If engine purge fails, the
identity remains and the API returns a stable safe error so an operator can
retry without orphaning private engine data.

### Technologies

- FastAPI strict request/response models and `UploadFile`
- Pydantic v2 validation and package-owned request models
- Starlette streaming responses with explicit cleanup
- Existing `txt2crs` facade, projections, artifact handles, and purge contract
- slowapi route limits and local runtime settings
- SQLModel/PostgreSQL plus Alembic migration
- Generated OpenAPI and TypeScript client
- pytest application acceptance fixtures

### Risks

- **Partial transport acceptance**: Bound content length, streaming byte count,
  MIME/signature agreement, and OOXML expansion before durable submission.
- **Duplicate paid work**: Let the package canonical request and idempotency
  contract decide replay versus conflict; never synthesize a shell-only key.
- **Private projection leakage**: Construct strict allowlisted response models
  from public package projections and assert forbidden fields recursively.
- **Artifact lifetime leaks**: Close package streams in response background
  cleanup and on disconnect/error paths.
- **Cross-store orphaning**: Purge engine data first; never delete PostgreSQL
  identity after a failed or incomplete engine purge.
- **Destructive migration**: Require jobs acceptance first, test clean and
  existing upgrades, and document that downgrade restores schema only.
- **Contract drift**: Regenerate both OpenAPI surfaces and run a clean diff
  check after item removal and job route addition.

### Relevant Considerations

- [P00-backend+frontend] **Donor items remain temporary**: Remove them only
  after the replacement job contract and acceptance coverage are green.
- [P01-backend+backend/packages/txt2crs] **HTTP artifact delivery owns
  cleanup**: Phase 03 must close package streams on every response outcome.
- [P01-backend+backend/packages/txt2crs] **Account erasure spans two owners**:
  engine purge must precede PostgreSQL deletion.
- [P02-backend+backend/packages/txt2crs] **Admission and recovery use public
  handles**: routes may not read private engine persistence.
- [P01-backend/packages/txt2crs] **Persist exact accepted identity**: restart
  uses the stored request and execution profile, never current defaults.
- [P01-backend/packages/txt2crs] **Cross-store erasure needs a worker
  barrier**: cancel/wait, delete artifacts, then delete engine parents.
- [P02-backend] **Operational logs use field allowlists**: new route events
  contain only stable IDs, categories, states, status, and timing.
- [P02-backend+frontend] **Authorization and polling follow server state**:
  cached queries and route guards must not create render-time side effects.

---

## Success Criteria

Phase complete when:

- [ ] All 3 sessions completed.
- [ ] Strict JSON and multipart requests reject unknown fields, unsupported
  types, oversize bodies, signature mismatches, and unsafe OOXML expansion
  before provider work.
- [ ] `202 Accepted` occurs only after exact durable commit and contains the
  stable owner-scoped job location.
- [ ] Same-key/same-request retries return the original job; same-key/changed
  request returns a stable `409`.
- [ ] Readiness, signup policy, rate limits, admission, and package errors map
  to registered RFC 9457 shell errors without private context.
- [ ] Status, result, manifest, and artifact routes are owner-scoped,
  projection-safe, private/no-store, and polling friendly.
- [ ] Artifact downloads verify integrity, use safe filenames and nosniff
  headers, expose no path, and close their package stream on every outcome.
- [ ] Restart from accepted and active checkpoints completes from stored
  state, while delivery replay does not repeat accepted model work.
- [ ] Both user deletion routes purge engine state before PostgreSQL identity
  and preserve retryability on purge failure.
- [ ] No item route, model, CRUD helper, error, test, documentation claim,
  generated client operation, or admin MCP tool remains.
- [ ] Alembic handles clean and existing upgrades and a supported
  downgrade/upgrade schema round trip.
- [ ] Backend, engine, generated-client, migration, and application acceptance
  validation remains green.

---

## Dependencies

### Depends On

- Phase 02: Composition and Readiness
- Phase 01: Engine Application Boundary

### Enables

- Phase 04: Learner Experience
