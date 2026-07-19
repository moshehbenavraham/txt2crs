# Session Specification

**Session ID**: `phase01-session01-durable-requests-and-recovery`
**Phase**: 01 - Engine Application Boundary
**Status**: Implementation Complete
**Created**: 2026-07-19
**Base Commit**: c56fa822e2f5f62d64ea427ae56739fd5c17ce4d
**Package**: backend/packages/txt2crs
**Package Stack**: Python 3.14, Pydantic v2, SQLite

---

## 1. Session Overview

This session replaces hash-only job admission with a strict, versioned
generation request whose complete generation-affecting state is committed
before a job can be returned as accepted. The immutable execution profile
freezes the model, reasoning, engine/prompt/policy versions, retry behavior,
input bounds, and finite run limits that recovery must reuse.

It is the first Phase 01 session because every later public projection,
preparation checkpoint, worker, and facade depends on an exact recoverable
request. The existing SQLite jobs, admissions, checkpoints, and delivery rows
remain the persistence base; this session adds one immutable migration instead
of rewriting released migrations.

The same package boundary will discover the next runnable job in deterministic
recovery-first order. FastAPI and future workers will not query SQLite tables
or reconstruct current defaults themselves.

---

## 2. Objectives

1. Define strict request, preference-intent, age-group, policy-context, retry,
   input-limit, run-limit, and immutable execution-profile contracts.
2. Derive and verify one canonical SHA-256 request hash across every
   generation-affecting value, including exact text or binary input.
3. Atomically persist the request, job row, and admission reservation with
   owner-scoped replay and conflict behavior.
4. Load exact accepted requests and discover runnable work in stable
   recovery-first order after a SQLite process restart.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase00-session01-baseline-container-and-state` - Provides the
  workspace-aware engine install, one-process topology, private persistent
  state root, and green engine baseline.

### Required Tools Or Knowledge

- Existing `SqliteJobStore` transaction, owner query, checkpoint, admission,
  and packaged migration patterns.
- Pydantic v2 strict/frozen contracts and deterministic JSON serialization.
- SQLite `BEGIN IMMEDIATE`, foreign keys, stable `ORDER BY`, and restart
  behavior.

### Environment Requirements

- Run all package commands from `backend/packages/txt2crs/`.
- Python dependencies are available through the backend uv workspace.
- Default tests require no network, Codex login, Tavily key, or shell import.

---

## 4. Scope

### In Scope (MVP)

- A package caller can construct one strict `GenerationRequest` containing
  `InputPayload`, learner preference intent, provider consent, coarse age
  group, server policy flags, immutable execution profile, and contract
  versions.
- A package caller can canonicalize the complete request, preserve arbitrary
  bounded binary bytes through a reversible encoded representation, and
  reject a supplied hash that does not match the request body.
- The job service can submit or replay one request with an owner-scoped
  idempotency key and finite `AdmissionReservation`.
- The SQLite store can atomically write request, job, and reservation rows or
  roll all of them back on quota, serialization, constraint, or transaction
  failure.
- Recovery can load the exact request and latest checkpoint for an authorized
  owner without applying current defaults.
- The internal worker boundary can select one non-terminal job with delivery
  and rendering recovery first, other active recovery next, accepted work
  last, and stable timestamp/job-ID tie breaking.
- Existing job, checkpoint, quota, delivery, executor, and evaluation tests
  are migrated to the complete request contract.

### Out Of Scope (Deferred)

- Public job projections and artifact streaming - Session 02 owns safe query
  surfaces.
- URL/YouTube routing, preference resolution, curriculum shape, and
  post-ingestion policy - Session 03 owns preparation semantics.
- Managed MCP, GPT-5.6 discovery, and notification modes - Session 04 owns
  provider runtime behavior.
- The final public facade, owner purge, FastAPI routes, and worker thread -
  Sessions 05, Phase 02, and Phase 03 own those boundaries.

---

## 5. Technical Approach

### Architecture

Add `txt2crs.jobs.requests` as the strict contract and canonicalization module.
The execution profile uses immutable Pydantic contracts rather than persisting
mutable `RunBudget` or `RetryController` instances. It stores only reviewed
configuration values that later factories can reconstruct exactly.

Canonicalization creates a type-tagged JSON-compatible representation for raw
input (`text` or base64-encoded `bytes`), excludes only the hash field itself,
sorts mapping keys, uses compact separators, and hashes UTF-8 bytes. A
`GenerationRequest` factory computes the hash; model validation recomputes it
so direct deserialization cannot smuggle a mismatched hash. Input byte length
must not exceed the stored execution-profile limit.

Migration `003_generation_requests.sql` adds one owner-linked request-envelope
row per job with schema version, request hash, canonical request JSON, and
timestamp. Released migrations 001 and 002 remain immutable. The existing
`jobs.input_hash` SQL column becomes a compatibility storage column for the
complete canonical request hash; the Python contract exposes the correct
`request_hash` name. The request-envelope row is authoritative for recovery.

`create_or_get_job` opens one `BEGIN IMMEDIATE` transaction, checks existing
owner/key state, compares the full request hash plus the existing reservation,
then inserts the job, request, and admission rows before one commit. Replay
loads and verifies the stored request. A mismatch or any partial failure rolls
the whole transaction back.

The internal runnable query joins jobs to request envelopes and orders known
non-terminal statuses by explicit recovery priority, then `created_at` and
`job_id`. It returns a complete resume object or `None`; callers never receive
a SQLite row or query the store directly.

### Design Patterns

- Strict immutable value object: Persist only validated versioned request and
  execution-profile contracts.
- Canonical content address: Use a labeled SHA-256 hash over a deterministic
  type-preserving request representation.
- Transaction script: Keep job, request, and reservation admission inside one
  explicit SQLite transaction.
- Forward-only packaged migration: Add migration 003 and preserve already
  released SQL resources unchanged.
- Repository boundary: Keep owner checks, row conversion, and runnable
  ordering in `SqliteJobStore`.
- Service boundary: Expose submission, owner recovery, and internal runnable
  discovery through `JobService`.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` | Strict request/profile contracts, canonical representation, hash creation, and validation | ~260 |
| `backend/packages/txt2crs/src/txt2crs/jobs/migrations/003_generation_requests.sql` | Immutable owner-linked request-envelope schema and indexes | ~30 |
| `backend/packages/txt2crs/tests/unit/test_generation_requests.py` | Contract strictness, immutability, canonicalization, binary round-trip, bounds, and tamper tests | ~240 |
| `backend/packages/txt2crs/tests/integration/test_generation_request_store.py` | Atomic persistence, replay/conflict, rollback, restart, ownership, and runnable-order tests | ~320 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/jobs/models.py` | Rename the domain hash meaning and attach the exact request to recovery state | ~15 |
| `backend/packages/txt2crs/src/txt2crs/jobs/store.py` | Register migration 003; persist/load requests; compare full hashes; discover runnable work | ~180 |
| `backend/packages/txt2crs/src/txt2crs/jobs/service.py` | Submit complete requests and expose exact owner/internal recovery | ~45 |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Export the new public request and execution-profile contracts | ~20 |
| `backend/packages/txt2crs/src/txt2crs/jobs/migrations/README_migrations.md` | Document migration 003 and immutable migration rules | ~10 |
| `backend/packages/txt2crs/tests/factories.py` | Add one reusable valid request/profile factory with finite P0-like limits | ~100 |
| `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py` | Replace hash-only submissions and assert migration compatibility | ~70 |
| `backend/packages/txt2crs/tests/integration/test_admission_quotas.py` | Exercise admission through the complete request contract | ~65 |
| `backend/packages/txt2crs/tests/unit/test_job_service.py` | Exercise service submission and recovery with stored requests | ~55 |
| `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` | Update executor setup to submit exact requests | ~35 |
| `backend/packages/txt2crs/tests/unit/test_evaluation_replay.py` | Update durable job fixtures to the renamed request hash | ~10 |

---

## 7. Success Criteria

### Functional Requirements

- [x] Unknown request/profile fields, invalid enums, unsafe bounds, mutable
  profile updates, and mismatched hashes fail strict validation.
- [x] Canonical hashing distinguishes text from bytes and changes for every
  generation-affecting input, preference, policy, version, model, retry, and
  limit field while ignoring mapping insertion order.
- [x] Valid arbitrary binary input round-trips byte-for-byte through SQLite
  after closing and reopening the store.
- [x] New submission commits exactly one job, request, and reservation; exact
  replay creates no rows or quota usage; changed request or reservation fails
  closed.
- [x] A forced failure after transaction start leaves no orphan job, request,
  or admission row.
- [x] Owner-scoped recovery returns the exact request plus last accepted
  checkpoint and gives foreign owners the same not-found result as missing
  jobs.
- [x] Runnable discovery excludes terminal jobs and deterministically prefers
  delivery/rendering recovery, then other active recovery, then accepted work.

### Testing Requirements

- [x] Failing unit and integration tests are written and observed before
  production implementation.
- [x] Focused request/store/service/quota/executor tests pass.
- [x] The full credential-free engine suite passes with the live test still
  explicitly gated.
- [x] Migration 003 is present in the built wheel and a reopened database
  reports migration version 3.

### Non-Functional Requirements

- [x] No shell, provider, network, credential, raw-input logging, or filesystem
  path exposure is introduced.
- [x] Persisted input is bounded by the accepted execution profile and exact
  request serialization is deterministic across process restart.
- [x] All multi-row writes have explicit transaction boundaries and rollback
  behavior.
- [x] Runnable selection has deterministic finite ordering and returns at most
  one job.

### Quality Gates

- [x] All session-authored files are ASCII-encoded.
- [x] Unix LF line endings are preserved.
- [x] Code follows package conventions with complete types, descriptive names,
  and intern-friendly comments around serialization, transactions, and
  recovery ordering.
- [x] Ruff formatting/lint, strict mypy, pytest, and package build pass from
  the engine package root.

---

## 8. Implementation Notes

### Working Assumptions

- The released `jobs.input_hash` SQLite column may store the complete request
  hash while Python renames the semantic field to `request_hash`: migration
  guidance forbids rewriting migration 001, no code outside the store depends
  on the physical column name, and migration 003 provides the authoritative
  request envelope.
- Binary input will use explicit URL-safe base64 inside canonical JSON rather
  than an independent BLOB column: the implementation plan permits bounded
  SQLite TEXT/BLOB storage, type tagging preserves text-versus-bytes meaning,
  and one canonical representation simplifies hash verification and restart
  recovery.
- Runnable work includes `accepted`, `researching`, `drafting`, `validating`,
  `rendering`, and `delivering`: current job states and the recovery contract
  classify all six as non-terminal, with late delivery/rendering states
  receiving the highest priority.

### Conflict Resolutions

- Existing submission compares an input hash and admission reservation, while
  the adopted plan requires idempotency across the entire canonical request.
  The plan is authoritative for the target behavior, so this session replaces
  hash-only service/store submission and updates all package callers rather
  than preserving an unsafe alternate acceptance path.
- The general project convention requires Alembic for application database
  changes, while this session changes engine-owned tenant SQLite. The
  repository database-ownership table and existing migration README assign
  this schema to packaged immutable SQL migrations, so migration 003 is the
  correct artifact and no PostgreSQL Alembic revision is created.

### Key Considerations

- Serialize and validate the complete request before opening the transaction
  when possible, but prove rollback for failures that occur after `BEGIN`.
- Keep request bodies and canonical JSON out of exception messages, repr-based
  logs, and test failure snapshots that could expose learner content.
- The worker-facing runnable query is an internal ownership boundary, not an
  owner-authorized browser query; public projections remain Session 02 scope.
- Existing checkpoints already persist budget counters. This session freezes
  budget limits in the request so later recovery can restore counters against
  the exact accepted ceiling.

### Potential Challenges

- Pydantic arbitrary-byte JSON behavior can be encoding-dependent: use an
  explicit type tag and base64 codec rather than implicit UTF-8 conversion.
- Existing tests call hash-only store/service APIs in 23 locations: migrate
  them through shared factories so no legacy acceptance path survives.
- SQLite test hooks for mid-transaction failure can become production debug
  surfaces: simulate real constraint/quota failures or use a test-only
  connection trigger, never add a production failure flag.
- Store code is already above the preferred module-size range: keep request
  serialization in `jobs.requests` and row-to-contract helpers cohesive.

### Relevant Considerations

- [P00-backend+backend/packages/txt2crs] **One process is mandatory**:
  deterministic runnable selection supports one serial worker and must not
  imply multi-worker leasing.
- [P00-backend+backend/packages/txt2crs] **Private state needs lifecycle
  coverage**: the request envelope remains in the owner-only SQLite state
  volume and cascades with its job.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  all persistence and discovery behavior is public package behavior, never a
  FastAPI table query.
- [P00] **Layer static and runtime contracts**: combine strict contract tests
  with real SQLite migration, transaction, close/reopen, and ordering tests.
- [P00-backend/packages/txt2crs] **Run engine tools from its package root**:
  use the package's independent pytest, Ruff, mypy, and build configuration.

### Behavioral Quality Focus

Checklist active: Yes

Top behavioral risks for this session:

- An idempotency retry with changed preferences or execution limits could
  silently reuse paid work unless every affecting field is hashed.
- A serialization, quota, or constraint failure could leave an accepted job
  without the request required to execute it.
- Restart ordering could starve near-complete delivery work or select terminal
  jobs unless priority and tie breaking are explicit.

---

## 9. Testing Strategy

### Unit Tests

- Validate strict/frozen contracts, enum values, finite positive limits,
  request-size bounds, and canonical hash verification.
- Prove canonical equality across mapping insertion order and inequality
  across text/bytes type, raw value, metadata, preferences, consent, age
  group, policy flags, versions, model/reasoning, retries, and limits.
- Prove arbitrary non-UTF-8 bytes serialize and restore exactly without
  appearing in safe validation error text.

### Integration Tests

- Apply migrations 001-003 to a new database and upgrade an existing
  version-2 database without rewriting prior rows.
- Commit job, request, and admission together; replay exactly; reject changed
  request or reservation; and verify row counts.
- Exercise quota and constraint failures after transaction start and assert
  no partial durable state.
- Close and reopen SQLite, then recover exact text and binary requests,
  execution profiles, checkpoints, and owner boundaries.
- Create jobs in every status with controlled timestamps and assert stable
  runnable priority, tie breaking, and terminal exclusion.

### Runtime Verification

- Build the wheel, inspect it for migration 003, install/import through the uv
  workspace, and run the complete credential-free package suite.

### Edge Cases

- Empty, oversized, non-UTF-8, and text-versus-bytes input values.
- Unknown fields, unsupported contract versions, invalid identifiers, and a
  request hash copied from another otherwise valid request.
- Same idempotency key under different owners, exact replay outside the rolling
  quota, changed reservation, and concurrent duplicate submissions.
- Databases created at version 2, missing/corrupt request rows, foreign-owner
  recovery, equal timestamps, terminal-only queues, and no runnable jobs.

---

## 10. Dependencies

### Other Sessions

- Depends on: `phase00-session01-baseline-container-and-state`
- Depended by: `phase01-session02-safe-queries-and-artifact-access`,
  `phase01-session03-input-preferences-and-policy-gate`,
  `phase01-session04-managed-runtime-and-model-policy`,
  `phase01-session05-public-facade-and-owner-lifecycle`, and every later worker
  or jobs API session

---

## Next Steps

Run the `implement` workflow step to begin implementation.
