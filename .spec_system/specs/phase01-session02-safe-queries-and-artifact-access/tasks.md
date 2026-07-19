# Task Checklist

**Session ID**: `phase01-session02-safe-queries-and-artifact-access`
**Total Tasks**: 22
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[SNNMM]` session ref; `TNNN` task ID.

---

## Setup And Tests First (5 tasks)

- [x] T001 [S0102] Run the JSON analyzer, full engine baseline, and focused existing progress/artifact/service tests before production edits (`.spec_system/scripts/analyze-project.sh`, `backend/packages/txt2crs/tests/unit/test_progress_projection.py`, `backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py`, `backend/packages/txt2crs/tests/unit/test_job_service.py`)
- [x] T002 [S0102] Write failing public snapshot allowlist, progress, warning/source/conflict bounds, URL/failure sanitization, malformed-checkpoint, and privacy tests (`backend/packages/txt2crs/tests/unit/test_public_job_queries.py`)
- [x] T003 [S0102] Write failing metadata-only manifest, stable-ID mapping, one-descriptor stream, chunk-bound, symlink, mutation, corruption, byte-limit, not-found, cleanup, and whole-bundle compatibility tests with authorization enforced at the private byte boundary (`backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py`)
- [x] T004 [S0102] Write failing real-SQLite service snapshot/manifest/stream/restart tests for correct owner, foreign owner, missing job, missing artifact set, and missing artifact ID with indistinguishable error mapping (`backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`)
- [x] T005 [S0102] Run the new focused suites and record their expected pre-implementation failures (`backend/packages/txt2crs/tests/unit/test_public_job_queries.py`, `backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py`, `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`)

---

## Foundation (4 tasks)

- [x] T006 [S0102] Implement strict public snapshot, progress, input, source, failure, artifact-availability, and projection-error contracts (`backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py`)
- [x] T007 [S0102] Implement strict artifact deliverable/format/metadata/manifest contracts plus the exact canonical renderer artifact-ID map (`backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py`)
- [x] T008 [S0102] [P] Add a reusable complete cumulative checkpoint fixture containing representative safe and private values (`backend/packages/txt2crs/tests/factories.py`)
- [x] T009 [S0102] Expand the private artifact protocol with typed manifest and context-managed stream operations, including cleanup on scope exit for every acquired stream (`backend/packages/txt2crs/src/txt2crs/jobs/service.py`)

---

## Implementation (7 tasks)

- [x] T010 [S0102] Project coherent resume state into bounded status/timestamps, accepted-stage units, safe input display, warnings, course title, source summaries, conflict summaries, failures, and artifact availability without serializing private state (`backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py`)
- [x] T011 [S0102] Split filesystem manifest validation from whole-body restore so metadata queries verify safe descriptors and exact directory topology without loading artifact bodies (`backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py`, `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py`)
- [x] T012 [S0102] Implement owner-scoped single-artifact streaming that opens once, rejects symlinks/non-regular files, enforces size, hashes and restats bounded bytes, rewinds the same descriptor, yields fixed chunks, and always closes (`backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py`, `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py`)
- [x] T013 [S0102] Preserve existing full-bundle get/save/delete/retention behavior through the shared verified manifest helpers and fail closed on unsafe legacy metadata (`backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py`)
- [x] T014 [S0102] Implement matching in-memory manifest/stream operations with canonical metadata, owner isolation, immutable copies, and deterministic context cleanup (`backend/packages/txt2crs/src/txt2crs/jobs/service.py`)
- [x] T015 [S0102] Add service methods for owner-authorized public snapshots, manifests, and artifact streams; authorize durable jobs before availability probes and preserve integrity errors (`backend/packages/txt2crs/src/txt2crs/jobs/service.py`)
- [x] T016 [S0102] Export supported public snapshot and artifact query contracts while keeping projection/storage helpers private (`backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`)

---

## Testing And Completion (6 tasks)

- [x] T017 [S0102] Run and repair public projection tests until every allowlist, bound, safe-failure, and privacy scenario passes (`backend/packages/txt2crs/tests/unit/test_public_job_queries.py`)
- [x] T018 [S0102] Run and repair artifact-store tests until metadata-only reads, stable IDs, confinement, same-descriptor integrity, bounded chunks, cleanup, and existing full-bundle behavior pass (`backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py`)
- [x] T019 [S0102] Run and repair service unit/integration tests until owner authorization, restart, unavailable artifacts, and indistinguishable not-found behavior pass (`backend/packages/txt2crs/tests/unit/test_job_service.py`, `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`)
- [x] T020 [S0102] Run the complete credential-free engine suite and repair every session-caused regression (`backend/packages/txt2crs/pyproject.toml`)
- [x] T021 [S0102] Run Ruff formatting/lint and strict mypy from the engine package root and repair all findings (`backend/packages/txt2crs/pyproject.toml`)
- [x] T022 [S0102] Build the package, verify public query modules ship, audit session files for ASCII/LF, update task evidence, and confirm no request, checkpoint, provider, token, artifact byte, descriptor, or path entered public output/errors (`backend/packages/txt2crs/pyproject.toml`, `.spec_system/specs/phase01-session02-safe-queries-and-artifact-access/implementation-notes.md`, `.spec_system/specs/phase01-session02-safe-queries-and-artifact-access/tasks.md`)

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
