# Task Checklist

**Session ID**: `phase03-session01-durable-job-submission-and-admission`
**Total Tasks**: 25
**Estimated Duration**: 3.5-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0301]`
session ref; `TNNN` task ID.

---

## Setup (2 tasks)

- [x] T001 [S0301] Verify Phase 02 facade, worker, readiness, errors, rate
  limits, strict-schema, multipart, and generated-client prerequisites
  (`.spec_system/specs/phase03-session01-durable-job-submission-and-admission/spec.md`)
- [x] T002 [S0301] Inspect public request/policy/admission and shell
  lifespan/dependency seams, then record the failing-test baseline
  (`backend/packages/txt2crs/src/txt2crs/application/facade.py`)

---

## Tests-First Foundation (8 tasks)

- [x] T003 [S0301] [P] Write engine facade/factory tests proving preflight
  happens before persistence and refusal calls the job service zero times
  (`backend/packages/txt2crs/tests/unit/test_application_facade.py`,
  `backend/packages/txt2crs/tests/contract/test_application_factories.py`)
- [x] T004 [S0301] [P] Write strict JSON, multipart metadata,
  preference/consent/age, idempotency, URL, bounds, and accepted-response tests
  (`backend/tests/schemas/test_job_schemas.py`)
- [x] T005 [S0301] Write pure ASGI declared/chunked body-limit, disconnect,
  unrelated-route, and RFC 9457 regression tests
  (`backend/tests/core/test_middleware.py`)
- [x] T006 [S0301] [P] Write bounded upload, filename, MIME, magic,
  PDF/ZIP/OOXML, traversal, encryption, macro, entry, expansion, and cleanup
  tests (`backend/tests/services/test_txt2crs_uploads.py`)
- [x] T007 [S0301] Write submission mapping, readiness, package-error,
  idempotency, admission, post-commit nudge, and safe-log tests
  (`backend/tests/services/test_txt2crs_submission.py`)
- [x] T008 [S0301] Write authenticated JSON/upload route tests for unknown
  data, authorization ordering, 202/Location/privacy headers, Problem Details,
  cleanup, and finite rate limits
  (`backend/tests/api/routes/test_jobs_submission.py`)
- [x] T009 [S0301] Build reusable deterministic acceptance fixtures and write
  durable commit/reopen, replay/conflict, quota, two-owner, policy, and
  no-provider-work scenarios
  (`backend/tests/acceptance/conftest.py`,
  `backend/tests/acceptance/test_job_submission.py`)
- [x] T010 [S0301] [P] Extend settings, signup, error translation, and OpenAPI
  contract tests for the local switch, new job errors, both submission routes,
  header pattern, and generated schemas
  (`backend/tests/core/test_txt2crs_settings.py`,
  `backend/tests/api/routes/test_users.py`,
  `backend/tests/core/test_txt2crs_errors.py`,
  `backend/tests/scripts/test_generate_client_contract.py`)

---

## Implementation (12 tasks)

- [x] T011 [S0301] Add package-owned preflight and shared finite admission
  reservation to public facade/factory composition without exposing policy
  internals
  (`backend/packages/txt2crs/src/txt2crs/application/facade.py`,
  `backend/packages/txt2crs/src/txt2crs/application/factories.py`)
- [x] T012 [S0301] Export only shell-needed preflight/reservation contracts and
  preserve public package import boundaries
  (`backend/packages/txt2crs/src/txt2crs/application/__init__.py`,
  `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`)
- [x] T013 [S0301] Add payload-too-large, unsupported-media, and policy job
  error meanings plus context-free package translation while preserving
  released system/job ranges
  (`backend/app/core/constants.py`, `backend/app/core/txt2crs_errors.py`)
- [x] T014 [S0301] Implement strict job input, preferences, metadata,
  idempotency-header, and accepted-job public models with exhaustive enum
  handling (`backend/app/schemas/jobs.py`)
- [x] T015 [S0301] Implement the route-scoped pure ASGI multipart body cap with
  schema-validated limits and explicit RFC 9457 error mapping on every
  declared/chunked failure (`backend/app/core/middleware.py`,
  `backend/app/main.py`)
- [x] T016 [S0301] Implement bounded upload acquisition and safe PDF/OOXML
  transport validation with cleanup on scope exit for all acquired
  files/archive resources (`backend/app/services/txt2crs_uploads.py`)
- [x] T017 [S0301] Implement package request/profile/reservation mapping,
  readiness refusal, facade submission, and post-commit worker nudge with
  idempotency protection and explicit failure mapping
  (`backend/app/services/txt2crs_submission.py`)
- [x] T018 [S0301] Add fail-closed dependencies for lifespan application,
  readiness, worker, and submission service without provider work at import
  time (`backend/app/api/deps.py`, `backend/app/services/__init__.py`)
- [x] T019 [S0301] Implement authenticated JSON submission with authorization
  at the boundary, finite rate limiting, duplicate-trigger protection, safe
  headers, and allowlisted events (`backend/app/api/routes/jobs.py`)
- [x] T020 [S0301] Implement authenticated multipart submission with strict
  metadata/file shape, bounded cleanup on every outcome, shared service
  semantics, and safe headers (`backend/app/api/routes/jobs.py`)
- [x] T021 [S0301] Register the jobs router and add the finite submission rate
  without changing serial-worker or system-route ownership
  (`backend/app/api/main.py`, `backend/app/core/rate_limit.py`)
- [x] T022 [S0301] Add the explicit local-only public-signup setting, enforce
  disabled/restricted handling before database reads, and update developer and
  judge/demo examples (`backend/app/core/config.py`,
  `backend/app/api/routes/users.py`, `backend/.env.example`, `.env.example`)

---

## Testing And Completion (3 tasks)

- [x] T023 [S0301] Document submission routes, input/error bounds, cleanup,
  privacy headers, and signup mode, then regenerate and format OpenAPI plus the
  TypeScript client (`docs/api/README_api.md`, `docs/CONFIGURATION.md`,
  `docs/environments.md`, `scripts/generate-client.sh`)
- [x] T024 [S0301] Run focused and complete deterministic engine/backend tests,
  Ruff format/check, strict mypy, ty, generated-client contract, and frontend
  Biome/TypeScript checks (`backend/packages/txt2crs/tests/`, `backend/tests/`,
  `frontend/`)
- [x] T025 [S0301] Run repository pre-commit; verify request/error/log
  allowlists, no provider work on rejection, clean generated state, ASCII/LF,
  and exact evidence; update implementation notes
  (`.spec_system/specs/phase03-session01-durable-job-submission-and-admission/implementation-notes.md`)

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

Run the `creview` workflow step.
