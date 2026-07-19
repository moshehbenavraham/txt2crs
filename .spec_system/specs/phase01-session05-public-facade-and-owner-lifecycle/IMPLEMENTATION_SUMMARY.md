# Implementation Summary

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Package**: `backend/packages/txt2crs`
**Completed**: 2026-07-19
**Duration**: 2.0 hours

---

## Overview

Session 05 published the complete framework-independent engine application
boundary. FastAPI can now compose one strict real or deterministic factory and
use a single facade for durable submission/recovery, runnable discovery,
public job and artifact access, safe readiness/authentication, fresh
owner/job-bound execution, synchronized shutdown, and complete engine owner
erasure.

The real factory owns the existing production SQLite, filesystem, ingestion,
content-policy, Tavily, managed loopback MCP, exact GPT-5.6 Codex, pipeline,
renderer, readiness, and authentication implementations. Provider work remains
lazy and job-scoped. The deterministic factory replaces only provider outputs
while exercising production persistence, preparation, pipeline, rendering,
artifact, recovery, and purge paths.

## Deliverables

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `src/txt2crs/application/__init__.py` | Supported public application exports | 49 |
| `src/txt2crs/application/config.py` | Strict real/deterministic configuration and scenario contracts | 262 |
| `src/txt2crs/application/facade.py` | Public facade and synchronized one-shot executor handle | 408 |
| `src/txt2crs/application/factories.py` | Real and deterministic composition roots | 799 |
| `src/txt2crs/application/owner_lifecycle.py` | Retry-safe artifact-first owner erasure | 141 |
| `tests/unit/test_owner_lifecycle.py` | Purge order, failure, retry, and strict result coverage | 179 |
| `tests/unit/test_application_facade.py` | Delegation, close, concurrency, purge, and retention coverage | 699 |
| `tests/contract/test_application_factories.py` | Config, composition, laziness, freshness, and cleanup contracts | 443 |
| `tests/integration/test_application_lifecycle.py` | Public-only deterministic 16-artifact lifecycle | 91 |

Paths are relative to `backend/packages/txt2crs`.

### Files Modified

| Area | Changes |
|------|---------|
| SQLite store | Added validated atomic owner-parent deletion, cascade/count verification, commit rollback, and retry behavior |
| Artifact reader/store/service | Added confined hashed-owner purge to filesystem/in-memory protocols and implementations |
| Public package exports | Added lazy root facade/factory entrypoints without eager optional/provider imports |
| Test factories and persistence tests | Added canonical deterministic scenario data plus real cascade, symlink, partial-failure, and race coverage |
| Package README | Replaced private manual assembly instructions with supported facade/factory guidance |
| Apex records | Added the complete spec, task, implementation, review, security, validation, and phase tracking evidence |

## Technical Decisions

1. **Facade delegates only**: Existing job, artifact, authentication, readiness,
   executor, and purge authorities retain all domain behavior.
2. **Provider state is lazy and fresh**: Every executor creates new budget,
   cancellation, retry, guardrail, research HTTP, MCP, Codex, coordinator, and
   pipeline state only after accepted preparation.
3. **Erasure stops work first**: Purge cancels and waits for tracked owner
   executors so delivery cannot recreate artifacts after success.
4. **Artifacts precede SQLite**: A filesystem failure preserves durable retry
   identity; a later SQLite failure can retry the idempotent empty artifact
   tree.
5. **Close is a synchronization boundary**: Admitted facade calls complete
   before resource teardown; duplicate close waits and cleanup still attempts
   every owned resource.
6. **Public config fails early**: Unknown fields, mutation, invalid JSON,
   unsafe/overlapping private paths, public MCP hosts, secrets, and unsupported
   model identities are rejected before runtime construction.

## Test Results

| Metric | Value |
|--------|-------|
| Complete tests | 445 collected |
| Passed | 444 |
| Explicitly gated | 1 live GPT-5.6/Tavily acceptance |
| Focused Session 05 selection | 79 passed |
| Ruff | PASS |
| Strict mypy | PASS - 136 source files |
| Wheel/sdist and repository gate | PASS |

## Code Review Repairs

Formal review resolved 2 High, 4 Medium, and 3 Low findings:

1. Prevented active delivery from recreating owner artifacts after purge.
2. Rolled back failed SQLite commits and verified actual deleted parent counts.
3. Serialized admitted facade calls with application cleanup.
4. Replaced process-lifetime strong executor retention with weak tracking.
5. Validated direct deterministic JSON construction.
6. Rejected symlinked/overlapping private roots and unsafe MCP hosts early.
7. Restored exact authentication and purge return annotations.
8. Rejected and safely translated impossible deletion counts.
9. Removed a coarse-filesystem timestamp assumption from one race test.

## Lessons Learned

1. Cross-store erasure needs a worker barrier as well as artifact-first
   ordering; otherwise late delivery can recreate already-purged files.
2. SQLite commit belongs inside the same guarded success boundary as delete,
   and a claimed count should be verified against actual affected rows.
3. An open-state check is not enough for shutdown concurrency; the delegated
   operation and teardown must share one synchronization boundary.
4. Pydantic helper constructors do not replace field-level validation when
   direct public model construction remains supported.

## Future Considerations

1. Phase 02 should translate shell settings exactly once into
   `RealApplicationConfig` and own one facade for the FastAPI lifespan.
2. The serial worker should recover before polling new jobs and use
   `ApplicationExecutor` as its cancellation/shutdown boundary.
3. Phase 03 routes should map package errors to shell `ErrorCode` values
   without importing private engine modules.
4. Phase 04 account deletion must call engine purge before the PostgreSQL user
   transaction and report partial failure truthfully.
5. The credentialed live GPT-5.6/Tavily proof remains required at release.

## Session Statistics

- **Tasks**: 24 completed
- **Implementation/test files created**: 9
- **Tracked files modified before closeout**: 13
- **Test functions added**: 35 plus parameterized cases
- **Code review findings**: 9 resolved
- **Success criteria**: 23/23
- **Blockers**: 0
