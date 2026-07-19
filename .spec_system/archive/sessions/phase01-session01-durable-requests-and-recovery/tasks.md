# Task Checklist

**Session ID**: `phase01-session01-durable-requests-and-recovery`
**Total Tasks**: 23
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[SNNMM]` session ref; `TNNN` task ID.

---

## Setup And Tests First (5 tasks)

- [x] T001 [S0101] Run the deterministic analyzer, engine baseline, and focused existing job tests before editing production code (`.spec_system/scripts/analyze-project.sh`, `backend/packages/txt2crs/tests/unit/test_job_service.py`, `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py`, `backend/packages/txt2crs/tests/integration/test_admission_quotas.py`)
- [x] T002 [S0101] Write strict request/profile, canonical-hash, arbitrary-binary, immutability, unknown-field, tamper, and execution-profile input-bound tests (`backend/packages/txt2crs/tests/unit/test_generation_requests.py`)
- [x] T003 [S0101] Write failing atomic create/load/replay/conflict/rollback/owner/restart and version-2-upgrade request-envelope tests (`backend/packages/txt2crs/tests/integration/test_generation_request_store.py`)
- [x] T004 [S0101] Write failing recovery-priority, stable timestamp/job-ID tie-break, terminal-exclusion, and empty-queue discovery tests (`backend/packages/txt2crs/tests/integration/test_generation_request_store.py`)
- [x] T005 [S0101] Run the new focused tests and record their expected pre-implementation failures (`backend/packages/txt2crs/tests/unit/test_generation_requests.py`, `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`)

---

## Foundation (4 tasks)

- [x] T006 [S0101] Implement strict frozen preference-intent, age-group, policy-context, retry, input-limit, run-limit, and execution-profile contracts with finite bounds (`backend/packages/txt2crs/src/txt2crs/jobs/requests.py`)
- [x] T007 [S0101] Implement type-tagged canonical request serialization, URL-safe base64 binary round-trip, SHA-256 creation, and mismatch validation without placing learner input in errors (`backend/packages/txt2crs/src/txt2crs/jobs/requests.py`)
- [x] T008 [S0101] [P] Add reusable valid generation-request and execution-profile factories that keep later tests concise (`backend/packages/txt2crs/tests/factories.py`)
- [x] T009 [S0101] Add immutable migration 003 for owner-linked canonical request envelopes and document the forward-only schema (`backend/packages/txt2crs/src/txt2crs/jobs/migrations/003_generation_requests.sql`, `backend/packages/txt2crs/src/txt2crs/jobs/migrations/README_migrations.md`)

---

## Implementation (8 tasks)

- [x] T010 [S0101] Replace the hash-only Python job meaning with `request_hash` and include the exact accepted request in resume state (`backend/packages/txt2crs/src/txt2crs/jobs/models.py`)
- [x] T011 [S0101] Register migration 003 through an explicit migration-resource map and preserve migrations 001-002 unchanged (`backend/packages/txt2crs/src/txt2crs/jobs/store.py`)
- [x] T012 [S0101] Replace hash-only creation with one transaction that validates and writes the job, request envelope, and admission reservation, with idempotency protection, transaction boundaries, and rollback on failure (`backend/packages/txt2crs/src/txt2crs/jobs/store.py`)
- [x] T013 [S0101] Implement owner-scoped request loading that verifies the persisted hash and exact binary/text round-trip while mapping missing, foreign, or corrupt state to typed safe errors (`backend/packages/txt2crs/src/txt2crs/jobs/store.py`)
- [x] T014 [S0101] Implement bounded next-runnable discovery with explicit recovery priority and deterministic ordering, returning at most one complete resume state (`backend/packages/txt2crs/src/txt2crs/jobs/store.py`)
- [x] T015 [S0101] Update service submission, owner resume, and worker discovery to consume complete request contracts instead of caller hashes (`backend/packages/txt2crs/src/txt2crs/jobs/service.py`)
- [x] T016 [S0101] Export the request/profile boundary and keep internal persistence helpers private (`backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`)
- [x] T017 [S0101] Migrate existing store, quota, service, executor, and evaluation fixtures away from hash-only acceptance without preserving an alternate unsafe path (`backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py`, `backend/packages/txt2crs/tests/integration/test_admission_quotas.py`, `backend/packages/txt2crs/tests/unit/test_job_service.py`, `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`, `backend/packages/txt2crs/tests/unit/test_evaluation_replay.py`)

---

## Testing And Completion (6 tasks)

- [x] T018 [S0101] Run and repair request-contract unit tests until strictness, hashing, binary, bounds, and tamper scenarios pass (`backend/packages/txt2crs/tests/unit/test_generation_requests.py`)
- [x] T019 [S0101] Run and repair SQLite request/store/service/quota/executor tests until atomicity, idempotency, ownership, restart, migration, and ordering scenarios pass (`backend/packages/txt2crs/tests/integration/test_generation_request_store.py`, `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py`, `backend/packages/txt2crs/tests/integration/test_admission_quotas.py`, `backend/packages/txt2crs/tests/unit/test_job_service.py`, `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`)
- [x] T020 [S0101] Run the complete credential-free engine suite and repair every session-caused regression (`backend/packages/txt2crs/pyproject.toml`)
- [x] T021 [S0101] Run Ruff formatting/lint and strict mypy from the engine package root and repair all findings (`backend/packages/txt2crs/pyproject.toml`)
- [x] T022 [S0101] Build the package and verify migration 003 plus the request contracts ship in the wheel (`backend/packages/txt2crs/pyproject.toml`, `backend/packages/txt2crs/src/txt2crs/jobs/migrations/003_generation_requests.sql`)
- [x] T023 [S0101] Audit every session file for ASCII/LF, update implementation evidence task by task, and confirm no raw learner input, provider credential, or filesystem path entered logs or errors (`.spec_system/specs/phase01-session01-durable-requests-and-recovery/implementation-notes.md`, `.spec_system/specs/phase01-session01-durable-requests-and-recovery/tasks.md`)

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] implementation-notes.md updated
- [x] Ready for `creview` (next step in the implement -> creview -> validate sequence)

---

## Next Steps

Run the `creview` workflow step.
