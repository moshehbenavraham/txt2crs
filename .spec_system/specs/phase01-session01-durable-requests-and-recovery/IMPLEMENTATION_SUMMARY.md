# Implementation Summary

**Session ID**: `phase01-session01-durable-requests-and-recovery`
**Package**: backend/packages/txt2crs
**Completed**: 2026-07-19
**Duration**: 1.1 hours

---

## Overview

Replaced hash-only job admission with a strict, versioned, complete generation
request and immutable execution profile. New work now commits its job,
canonical request envelope, and admission reservation atomically; exact
idempotent replay is free, any changed request or reservation fails closed,
and restart recovery reuses the accepted request without applying current
defaults.

The session also added deterministic recovery-first runnable discovery,
owner-safe atomic resume snapshots, finite metadata/input/token bounds, safe
error translation, version-2 SQLite upgrade behavior, and concurrent replay
coverage. All behavior remains inside the reusable `txt2crs` package.

---

## Deliverables

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` | Strict request/profile contracts, normalized canonical identity, bounds, and codecs | 539 |
| `backend/packages/txt2crs/src/txt2crs/jobs/request_store.py` | Cohesive request-envelope SQL and integrity restoration | 114 |
| `backend/packages/txt2crs/src/txt2crs/jobs/migrations/003_generation_requests.sql` | Owner-linked durable request-envelope schema | 14 |
| `backend/packages/txt2crs/tests/unit/test_generation_requests.py` | Contract, normalization, privacy, bounds, mutation, and hash coverage | 340 |
| `backend/packages/txt2crs/tests/integration/test_generation_request_store.py` | Atomicity, replay, concurrency, owner, upgrade, restart, and runnable coverage | 596 |

Session planning, review, security, validation, and summary artifacts were also
created under `.spec_system/PRD/phase_01/` and the session directory.

### Files Modified

| File | Changes |
|------|---------|
| `backend/packages/txt2crs/src/txt2crs/jobs/models.py` | Correct request-hash meaning, submission identity, status rules, and exact resume state |
| `backend/packages/txt2crs/src/txt2crs/jobs/quota.py` | Cohesive parameterized rolling-admission calculation |
| `backend/packages/txt2crs/src/txt2crs/jobs/store.py` | Migration registration, atomic admission, owner recovery, snapshot, and runnable discovery |
| `backend/packages/txt2crs/src/txt2crs/jobs/service.py` | Complete-request submission and store-owned recovery APIs |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Public request/profile contract exports |
| `backend/packages/txt2crs/src/txt2crs/jobs/migrations/README_migrations.md` | Migration 003 and forward-only recovery semantics |
| `backend/packages/txt2crs/tests/factories.py` | Shared request/profile/reservation fixtures |
| `backend/packages/txt2crs/tests/integration/test_admission_quotas.py` | Reservation/profile-aligned quota tests |
| `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` | Executor fixtures use exact stored requests and consent |
| `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py` | Complete request and schema-version coverage |
| `backend/packages/txt2crs/tests/unit/test_job_service.py` | Exact request and atomic resume boundary coverage |

---

## Technical Decisions

1. **Preserve the released physical `jobs.input_hash` column**: Migration 001
   remains immutable; Python exposes `request_hash`, and migration 003 is the
   authoritative complete request envelope.
2. **Use one type-tagged canonical JSON envelope**: Text and arbitrary bytes
   cannot collide, URL-safe base64 preserves binary values, and one artifact
   supports deterministic hash/restart verification.
3. **Validate before hashing or writing**: A private hashless identity applies
   normalization, version, preference, input, metadata, and profile checks
   before canonical work; submission owner/key checks occur before `BEGIN`.
4. **Require reservation coverage**: A new job cannot reserve fewer model
   tokens than its immutable execution profile can spend.
5. **Keep recovery one-process atomic**: Owner resume and worker discovery
   hold the process-local store lock across job, request, and checkpoint reads,
   matching the approved serial-worker architecture.

---

## Test Results

| Metric | Value |
|--------|-------|
| Tests Collected | 275 |
| Passed | 274 |
| Failed | 0 |
| Explicit Live Gate Skipped | 1 |
| Coverage | Not collected by the configured session command |

Ruff format/lint, strict mypy, package build, wheel/sdist content inspection,
SQLite migration/schema checks, security/GDPR review, concurrent replay, and
ASCII/LF checks also pass.

---

## Lessons Learned

1. Canonical identity must be derived from the normalized validated snapshot,
   not raw factory arguments or separately re-read mutable state.
2. `frozen=True` does not deep-freeze an older nested Pydantic model; detached
   copying plus hash revalidation provides the required durable integrity.
3. Resource admission is safe only when the reservation is checked against the
   execution ceiling that recovery will actually restore.
4. Safe outer error text is insufficient if a sensitive Pydantic error remains
   attached through `__cause__` or `__context__`.

---

## Future Considerations

Items for future sessions:

1. Session 02 should build allowlisted public job projections and owner-safe
   manifest/single-artifact reads on this exact recovery boundary.
2. Session 03 must enforce provider consent and content policy before new job
   admission and checkpoint prepared input/preferences.
3. Session 04 must verify that the managed runtime can execute each persisted
   model/profile without fallback.
4. Session 05 must expose the final facade and idempotent owner purge for
   request, job, checkpoint, delivery, and artifact data.

---

## Session Statistics

- **Tasks**: 23 completed
- **Implementation Files Created**: 5
- **Implementation Files Modified**: 11
- **Tests Added**: 51
- **Code Review Findings Resolved**: 10
- **Environment Blockers Resolved**: 2
