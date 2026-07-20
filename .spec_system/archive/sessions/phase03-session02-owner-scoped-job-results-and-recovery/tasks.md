# Task Checklist

**Session ID**: `phase03-session02-owner-scoped-job-results-and-recovery`
**Total Tasks**: 25
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-20

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0302]`
session ref; `TNNN` task ID.

---

## Setup And Baseline (2 tasks)

- [x] T001 [S0302] Verify Session 01 completion, public facade/query/stream
  prerequisites, isolated PostgreSQL head, and package/shell focused baseline
  (`backend/packages/txt2crs/src/txt2crs/application/facade.py`,
  `backend/app/api/routes/jobs.py`).
- [x] T002 [S0302] Inspect projection/checkpoint fields, artifact-context
  entry semantics, Starlette disconnect behavior, and current generated
  contract before recording the baseline
  (`backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py`,
  `backend/app/api/artifact_response.py`).

---

## Tests First (7 tasks)

- [x] T003 [S0302] [P] Write failing package projection tests for durable
  revision, nullable pre-plan total, finite post-plan progress, input size,
  resolved result/count leaves, 12-source cap, and explicit truncation without
  private serialization
  (`backend/packages/txt2crs/tests/unit/test_public_job_queries.py`).
- [x] T004 [S0302] [P] Write failing shell response-schema tests for strict
  job/result/failure/source/manifest/artifact mappings, unknown fields, bounds,
  result coherence, and exhaustive enums
  (`backend/tests/schemas/test_job_schemas.py`).
- [x] T005 [S0302] [P] Write failing direct ASGI streaming-response tests for
  successful exhaustion, early disconnect, send failure, iterator failure,
  context-entry failure, and idempotent exact-once cleanup
  (`backend/tests/api/test_artifact_response.py`).
- [x] T006 [S0302] Write failing authenticated route tests for status/result
  revisions, private/no-store/no-ETag headers, uniform missing/wrong-owner
  404s, grouped manifest, safe download headers/body, integrity failures, and
  response-owned cleanup
  (`backend/tests/api/routes/test_jobs_results.py`).
- [x] T007 [S0302] [P] Write failing public-facade acceptance tests for
  completed result/manifest/artifact reads, repeated delivery, two-owner
  isolation, and missing identifiers
  (`backend/tests/acceptance/test_job_results_and_recovery.py`).
- [x] T008 [S0302] Write failing restart acceptance tests for accepted,
  resolved-preference/module, render, and delivery boundaries with exact
  stored identity, remaining-work-only execution, and no repeated model work
  (`backend/tests/acceptance/conftest.py`,
  `backend/tests/acceptance/test_job_results_and_recovery.py`).
- [x] T009 [S0302] [P] Write failing safe exception and generated OpenAPI
  contract tests for the three authenticated GET routes, path bounds, binary
  content, response schemas, and no conditional HTTP contract
  (`backend/tests/core/test_txt2crs_errors.py`,
  `backend/tests/scripts/test_generate_client_contract.py`).

---

## Package And Shell Implementation (11 tasks)

- [x] T010 [S0302] Extend the package public snapshot with revision, nullable
  progress total, finite input size, resolved result/count leaves, 12-source
  bound, and truncation flags while copying only validated private leaves
  (`backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py`).
- [x] T011 [S0302] Export only new public query contracts and keep package
  projection/service integration coherent across close/reopen
  (`backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`,
  `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`).
- [x] T012 [S0302] Implement strict job/progress/input/failure/result/source
  response models and explicit public-package mappers with exhaustive enum and
  nullable-state handling (`backend/app/schemas/jobs.py`).
- [x] T013 [S0302] Implement grouped manifest and artifact metadata response
  models with stable ordering, finite canonical identifiers, and no path/body
  fields (`backend/app/schemas/jobs.py`).
- [x] T014 [S0302] Implement an entered-context artifact body and ASGI
  streaming response that closes exactly once in `finally` across completion,
  disconnect, send/iterator failure, and explicit cleanup
  (`backend/app/api/artifact_response.py`).
- [x] T015 [S0302] Map package projection and integrity failures to
  context-free registered shell errors while preserving the single
  missing/wrong-owner 404 boundary
  (`backend/app/core/txt2crs_errors.py`).
- [x] T016 [S0302] Add the owner-scoped status/result GET route with validated
  path input, explicit mapper, monotonic revision, fixed private headers, and
  no ETag/304 behavior (`backend/app/api/routes/jobs.py`).
- [x] T017 [S0302] Add the owner-scoped manifest GET route with package
  authorization/integrity enforcement, grouped allowlist response, and fixed
  private headers (`backend/app/api/routes/jobs.py`).
- [x] T018 [S0302] Add the owner-scoped artifact GET route that resolves safe
  metadata, enters/verifies the package stream before headers, builds RFC-safe
  attachment/media/length headers, and transfers cleanup to the response
  (`backend/app/api/routes/jobs.py`,
  `backend/app/api/artifact_response.py`).
- [x] T019 [S0302] Expand the deterministic acceptance harness with one
  complete scenario, remaining-turn scenarios, bounded wait helpers, and
  test-only runtime/render/store interruption controls
  (`backend/tests/acceptance/conftest.py`).
- [x] T020 [S0302] Complete accepted/active/render/delivery replacement and
  repeated-delivery acceptance using fresh public facade/worker handles, exact
  durable request/profile/checkpoints, and cleanup for every opened
  application/stream (`backend/tests/acceptance/test_job_results_and_recovery.py`).

---

## Contract, Documentation, And Verification (5 tasks)

- [x] T021 [S0302] Document status/result bounds, revisioned no-store polling,
  owner-hidden 404s, manifest metadata, download headers/cleanup, integrity
  failure, and restart/replay operations, then regenerate the client only
  through the repository script (`backend/tests/scripts/test_generate_client_contract.py`,
  `docs/api/README_api.md`, `docs/ARCHITECTURE.md`,
  `docs/runbooks/incident-response.md`).
- [x] T022 [S0302] Run focused package projection/facade/service and shell
  schema/error/response/route suites; resolve every failure at its owning
  boundary (`backend/packages/txt2crs/tests/`,
  `backend/tests/`).
- [x] T023 [S0302] Run complete engine and backend suites plus Ruff
  check/format, strict mypy, and ty from their owning package roots
  (`backend/packages/txt2crs/pyproject.toml`, `backend/pyproject.toml`).
- [x] T024 [S0302] Regenerate OpenAPI/client twice, prove byte stability, and
  run frontend Biome, TypeScript, and production build without hand-editing
  generated files (`backend/tests/scripts/test_generate_client_contract.py`,
  `frontend/src/client/`).
- [x] T025 [S0302] Run repository pre-commit over tracked and explicit
  untracked files; recheck response/error/log privacy, exact stream cleanup,
  no-provider replay, ASCII/LF, and diff hygiene
  (`backend/app/api/routes/jobs.py`,
  `backend/app/api/artifact_response.py`).

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] implementation-notes.md updated
- [x] Ready for `creview` (next step in the implement -> creview -> validate
  sequence)

---

## Next Steps

Run the `creview` workflow step, then `validate` after every review finding is
resolved.
