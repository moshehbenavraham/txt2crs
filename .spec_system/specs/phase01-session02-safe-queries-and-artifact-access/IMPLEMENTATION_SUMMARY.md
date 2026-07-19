# Implementation Summary

**Session ID**: `phase01-session02-safe-queries-and-artifact-access`
**Package**: backend/packages/txt2crs
**Completed**: 2026-07-19
**Duration**: 1.7 hours

---

## Overview

Added the owner-safe read boundary the application shell needs for durable
generation jobs and rendered artifacts. Authorized callers can now obtain a
bounded public job snapshot, inspect a canonical path-free artifact manifest,
and stream one stable artifact ID in fixed chunks without receiving a
filesystem path or private engine state.

The implementation preserves whole-bundle recovery while separating public
artifact contracts, metadata/body verification, and atomic storage lifecycle.
It also adds deterministic in-memory behavior and real SQLite/filesystem
restart coverage so the final facade can compose established package methods.

---

## Deliverables

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` | Strict public job contracts, bounded allowlist projection, and safe URL/failure handling | 517 |
| `backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py` | Canonical artifact metadata contracts and shared pre-write validation | 245 |
| `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py` | Confined manifest verification, full recovery, and same-descriptor streaming | 516 |
| `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` | Public allowlist, bounds, privacy, URL, failure, and malformed-state coverage | 376 |
| `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py` | Real SQLite/filesystem owner, restart, manifest, stream, and integrity coverage | 308 |

Session planning, review, security, validation, and summary artifacts were also
created in the Session 02 specification directory.

### Files Modified

| File | Changes |
|------|---------|
| `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py` | Delegated verified reads, bounded manifest writes, and retained atomic save/delete/retention behavior |
| `backend/packages/txt2crs/src/txt2crs/jobs/service.py` | Added artifact protocol reads, deterministic manifests/streams, and owner-safe query methods |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Exported supported public job and artifact contracts |
| `backend/packages/txt2crs/tests/factories.py` | Added a reusable structurally valid cumulative checkpoint fixture |
| `backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py` | Added metadata-only, stream, mutation, cleanup, privacy, and compatibility tests |
| `backend/packages/txt2crs/tests/unit/test_job_service.py` | Added deterministic store, availability, atomicity, and owner-query tests |

---

## Technical Decisions

1. **Construct public allowlists instead of filtering private serialization**:
   New frozen Pydantic models copy only reviewed fields and never serialize a
   request, checkpoint, evidence excerpt, provider record, token count, or
   path.
2. **Separate metadata from body reads**: Manifest queries open only the
   bounded manifest and compare descriptor metadata/topology with non-following
   stats; content hashing remains on full or selected-body reads.
3. **Stream one verified descriptor**: The reader opens with `O_NOFOLLOW`,
   validates type/size/hash, restats identity, rewinds the same descriptor, and
   yields 64 KiB chunks under deterministic context cleanup.
4. **Use exact stable artifact IDs**: Only the renderer's sixteen
   deliverable/format keys become public. Private legacy/debug artifacts remain
   recoverable but fail closed at public projection.
5. **Keep missing and unauthorized states indistinguishable**: Durable state
   authorizes job snapshots; owner/job hashes authorize bytes; all missing
   owner/job/artifact-ID paths share one safe not-found boundary.

---

## Test Results

| Metric | Value |
|--------|-------|
| Total Collected | 304 |
| Passed | 303 |
| Failed | 0 |
| Explicit Live Gate Skipped | 1 |
| Coverage | Not collected by the configured session command |

Ruff formatting/lint, strict mypy, repository engine validation, wheel/sdist
build, archive inspection, ASCII/LF checks, security/GDPR review, and
behavioral-quality review also pass.

---

## Lessons Learned

1. A metadata-only manifest can still verify confinement, regular-file type,
   exact topology, and current size without opening or loading every body.
2. Writer and reader bounds must share validation; otherwise a successful save
   can create immediately unreadable state.
3. Context-free public errors must be raised after leaving exception handlers
   when the original exception can retain a private path or payload.
4. Durable request hashes and pipeline checkpoint hashes identify different
   contracts; Session 03 must bridge resolved preferences rather than equating
   those hashes.

---

## Future Considerations

1. Session 03 must resolve learning preferences and enforce post-ingestion
   policy before research or provider work.
2. Phase 03 must translate safe artifact metadata into private/no-store,
   nosniff, attachment responses and close streams on disconnect.
3. Session 05 must compose these operations into the public facade and prove
   idempotent owner-wide request/checkpoint/artifact purge.

---

## Session Statistics

- **Tasks**: 22 completed
- **Files Created**: 5 implementation/test files
- **Files Modified**: 6 implementation/test files
- **Tests Added**: 27 named scenarios
- **Review Findings Resolved**: 7
- **Blockers**: 0
