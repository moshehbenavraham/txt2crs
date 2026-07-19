# Implementation Notes

**Session ID**: `phase03-session01-durable-job-submission-and-admission`
**Package**: backend
**Started**: 2026-07-19 23:21
**Last Updated**: 2026-07-20 00:06

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | Complete - ready for code review |
| Blockers | 0 |

---

## Task Log

### Task T001 - Verify Session Prerequisites

**Started**: 2026-07-19 23:21
**Completed**: 2026-07-19 23:22
**Duration**: 1 minute

**Notes**:
- Verified the active backend session, required tooling, package manifest, and
  isolated PostgreSQL migration state without touching the unrelated database
  already bound to the repository's usual host port.

**Files Changed**:
- `.spec_system/specs/phase03-session01-durable-job-submission-and-admission/implementation-notes.md` - initialized exact task evidence.

**Verification**:
- Command/check: `check-prereqs.sh --json --env --package backend`
  - Result: PASS - spec system, git, jq, uv, package path, and manifest passed.
- Command/check: isolated PostgreSQL `alembic upgrade head`, `current`, and
  `check` on port 55433
  - Result: PASS - revision `fe56fa70289e (head)` with no pending operations.
- UI product-surface check: N/A - setup verification only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T002 - Inspect Boundaries And Record Baseline

**Started**: 2026-07-19 23:22
**Completed**: 2026-07-19 23:22
**Duration**: 1 minute

**Notes**:
- Inspected the public facade/factories, request/admission/policy contracts,
  shell lifespan, readiness/worker dependencies, middleware, rate limiting,
  strict schemas, and generated-client seam.
- Confirmed pre-session focused tests are green before adding tests that must
  fail for the missing submission behavior.

**Files Changed**:
- `.spec_system/specs/phase03-session01-durable-job-submission-and-admission/implementation-notes.md` - recorded baseline evidence.

**Verification**:
- Command/check: engine facade/factory focused pytest
  - Result: PASS - 34 tests passed.
- Command/check: shell settings/errors/middleware/users/system/lifespan pytest
  - Result: PASS - 96 tests passed with 40 existing JWT key-length warnings.
- UI product-surface check: N/A - inspection only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T003 - Add Failing Package Preflight Tests

**Started**: 2026-07-19 23:22
**Completed**: 2026-07-19 23:30
**Duration**: 8 minutes

**Notes**:
- Added facade tests that require package-owned preflight to run before the
  durable job service and prove a refused request never reaches persistence.
- Added a deterministic-factory contract test that requires the public facade
  to expose the factory's finite admission reservation and reject missing
  research consent before any runnable job exists.
- Observed the new tests fail only because the facade constructor and shared
  reservation method do not exist yet, which is the intended tests-first
  boundary for T011.

**Files Changed**:
- `backend/packages/txt2crs/tests/unit/test_application_facade.py` - added
  ordered preflight/submission spies and refusal coverage.
- `backend/packages/txt2crs/tests/contract/test_application_factories.py` -
  added deterministic factory refusal and reservation coverage.

**Verification**:
- Command/check: focused pytest for the three new tests with `--tb=short`
  - Result: EXPECTED FAIL - two constructor failures for the missing
    `preflight_evaluator` argument and one missing
    `default_admission_reservation` method.
- UI product-surface check: N/A - engine contract tests only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T004 - Add Failing Submission Schema Tests

**Started**: 2026-07-19 23:25
**Completed**: 2026-07-19 23:27
**Duration**: 2 minutes

**Notes**:
- Defined tests for all four discriminated JSON inputs, finite text and URL
  bounds, strict unknown-field rejection, normalized unique preferences,
  literal consent, the three reviewed age groups, and upload metadata.
- Protected duplicate-key rejection for untrusted multipart metadata and the
  exact private idempotency-header pattern.
- Defined the frozen allowlisted accepted response, including the stable
  initial revision and relative owner-scoped status location.

**Files Changed**:
- `backend/tests/schemas/test_job_schemas.py` - added the complete red
  transport-contract suite.

**Verification**:
- Command/check: focused schema pytest
  - Result: EXPECTED FAIL during collection because `app.schemas.jobs` has
    not been implemented.
- UI product-surface check: N/A - API schema tests only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T005 - Add Failing Upload Body-Limit Tests

**Started**: 2026-07-19 23:27
**Completed**: 2026-07-19 23:29
**Duration**: 2 minutes

**Notes**:
- Added pure ASGI tests for early declared-length rejection, chunk-by-chunk
  enforcement when the declared length is absent or dishonest, and exact-limit
  success.
- Protected disconnect propagation and proved unrelated routes remain outside
  the upload-specific cap.
- Defined the bounded RFC 9457 response contract for `JOB_7005`.

**Files Changed**:
- `backend/tests/core/test_middleware.py` - added direct ASGI body-limit
  regressions without relying on multipart parser behavior.

**Verification**:
- Command/check: focused middleware pytest
  - Result: EXPECTED FAIL during collection because
    `UploadBodyLimitMiddleware` has not been implemented.
- UI product-surface check: N/A - middleware tests only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T006 - Add Failing Upload Validation Tests

**Started**: 2026-07-19 23:29
**Completed**: 2026-07-19 23:31
**Duration**: 2 minutes

**Notes**:
- Added bounded-read and exact-payload tests for PDF, DOCX, and PPTX, including
  one close on successful context exit.
- Added rejection coverage for byte overflow, unsafe filenames, extension and
  MIME disagreement, invalid magic, corrupt or wrong OOXML structure, archive
  traversal, encryption, macros, active content, entry counts, and expanded
  size.
- Used real PDF metadata to protect corrupt, encrypted, and page-count
  boundaries, plus a cancellation double to prove framework-file cleanup.

**Files Changed**:
- `backend/tests/services/test_txt2crs_uploads.py` - added the complete red
  upload acquisition and transport-validation suite.

**Verification**:
- Command/check: focused upload-service pytest
  - Result: EXPECTED FAIL during collection because
    `app.services.txt2crs_uploads` has not been implemented.
- UI product-surface check: N/A - upload service tests only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T007 - Add Failing Submission Service Tests

**Started**: 2026-07-19 23:31
**Completed**: 2026-07-19 23:34
**Duration**: 3 minutes

**Notes**:
- Defined exact JSON and upload mapping into one immutable package request,
  including YouTube-to-URL routing without duplicating host policy.
- Protected cached-readiness ordering, facade-supplied reservation use,
  context-free package error translation, cancellation, and zero worker
  notification on rejection.
- Proved the post-commit wake event is latency-only: a failed hint cannot
  replace a durable success. Added allowlisted event assertions that exclude
  source text, URL, idempotency key, and request hash.

**Files Changed**:
- `backend/tests/services/test_txt2crs_submission.py` - added the complete red
  shell composition-service suite.

**Verification**:
- Command/check: focused submission-service pytest
  - Result: EXPECTED FAIL during collection because the new job schemas and
    submission service have not been implemented.
- UI product-surface check: N/A - submission service tests only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T008 - Add Failing Authenticated Route Tests

**Started**: 2026-07-19 23:34
**Completed**: 2026-07-19 23:36
**Duration**: 2 minutes

**Notes**:
- Added authorization-ordering, strict JSON/header, and context-free Problem
  Details coverage for the authenticated JSON route.
- Defined the exact `202`, `Location`, private/no-store, pragma, nosniff, and
  referrer-policy contract without exposing the idempotency key.
- Added multipart success, duplicate/extra field, media/size error, service
  skip, and finite-rate-limit cases.

**Files Changed**:
- `backend/tests/api/routes/test_jobs_submission.py` - added the complete red
  authenticated submission route suite.

**Verification**:
- Command/check: focused job-route pytest
  - Result: EXPECTED FAIL during collection because the lifespan-owned
    submission dependency has not been implemented.
- UI product-surface check: N/A - HTTP route tests only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T009 - Add Failing Durable Acceptance Tests

**Started**: 2026-07-19 23:36
**Completed**: 2026-07-19 23:38
**Duration**: 2 minutes

**Notes**:
- Added a credential-free deterministic application harness over production
  SQLite and artifact composition with reusable finite profile/admission data.
- Added close/reopen recovery, replay/conflict, atomic quota, two-owner
  namespace isolation, cross-owner hiding, policy refusal, and no-provider
  resource scenarios.
- Corrected the focused command to use the repository's component PostgreSQL
  variables rather than an unused aggregate URL override.

**Files Changed**:
- `backend/tests/acceptance/conftest.py` - added the reusable deterministic
  durable-state harness.
- `backend/tests/acceptance/test_job_submission.py` - added the complete red
  Phase 03 submission acceptance suite.

**Verification**:
- Command/check: focused acceptance pytest against the isolated PostgreSQL
  container
  - Result: EXPECTED FAIL - all seven cases stop at the missing public
    `default_admission_reservation` facade method.
- UI product-surface check: N/A - durable application acceptance only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T010 - Add Failing Settings, Signup, Error, And OpenAPI Tests

**Started**: 2026-07-19 23:38
**Completed**: 2026-07-19 23:40
**Duration**: 2 minutes

**Notes**:
- Added fail-closed public-signup settings tests: false by default, explicit
  local enablement, and startup rejection when enabled outside local mode.
- Protected disabled-signup ordering before account lookup and adjusted the
  two existing registration cases to explicitly select developer mode.
- Added stable `JOB_7005`-`JOB_7007` status mappings, package policy
  translation, and generated OpenAPI checks for authentication, idempotency
  pattern, discriminated inputs, multipart shape, and allowlisted response.

**Files Changed**:
- `backend/tests/core/test_txt2crs_settings.py` - added signup setting tests.
- `backend/tests/core/test_txt2crs_errors.py` - added job code/status/policy
  translation tests.
- `backend/tests/api/routes/test_users.py` - added explicit enabled/disabled
  signup behavior.
- `backend/tests/scripts/test_generate_client_contract.py` - added generated
  job submission contract checks.

**Verification**:
- Command/check: focused settings/errors/users/client-contract pytest
  - Result: EXPECTED FAIL - 11 new failures for the missing signup setting,
    job error codes/mapping, disabled guard, routes, and generated schemas;
    78 existing cases pass.
- UI product-surface check: N/A - configuration/API contract tests only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T011 - Enforce Package Preflight Before Persistence

**Started**: 2026-07-19 23:40
**Completed**: 2026-07-19 23:41
**Duration**: 1 minute

**Notes**:
- Added a narrow facade preflight protocol and made non-allowed package
  decisions raise the existing safe policy error before `JobService.submit`.
- Kept policy and persistence inside the facade lock so cleanup cannot race
  between the decision and durable write.
- Composed one shared immutable factory reservation into both facade and
  readiness, and exposed it through the open facade for shell submission.

**Files Changed**:
- `backend/packages/txt2crs/src/txt2crs/application/facade.py` - added
  authoritative preflight ordering and reservation access.
- `backend/packages/txt2crs/src/txt2crs/application/factories.py` - composed
  version-matched policy and one shared reservation in both factories.

**Verification**:
- Command/check: complete engine facade and factory contract pytest
  - Result: PASS - 37 tests passed.
- UI product-surface check: N/A - package boundary only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T012 - Export Minimal Submission Contracts

**Started**: 2026-07-19 23:41
**Completed**: 2026-07-19 23:43
**Duration**: 2 minutes

**Notes**:
- Added red import tests before exposing the facade preflight protocol,
  immutable admission reservation, and raw input payload through their
  documented public package namespaces.
- Kept policy implementations, stores, request projection helpers, and
  persistence internals private.

**Files Changed**:
- `backend/packages/txt2crs/tests/unit/test_public_package_exports.py` -
  protected fresh-process imports for the three contracts.
- `backend/packages/txt2crs/src/txt2crs/application/__init__.py` - exported
  the narrow preflight protocol.
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - exported
  reservation and input contracts required by the shell adapter.

**Verification**:
- Command/check: public package export pytest
  - Result: PASS - 4 tests passed.
- Command/check: focused engine Ruff check
  - Result: PASS.
- UI product-surface check: N/A - package exports only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T013 - Add Stable Submission Error Meanings

**Started**: 2026-07-19 23:43
**Completed**: 2026-07-19 23:43
**Duration**: under 1 minute

**Notes**:
- Extended the released job range with payload-too-large, unsupported-media,
  and synchronous policy refusal without renumbering existing system/job codes.
- Added the missing 413 and 415 HTTP constants and context-free package policy
  translation that never copies policy text or reason internals.

**Files Changed**:
- `backend/app/core/constants.py` - added status and stable job-code mappings.
- `backend/app/core/txt2crs_errors.py` - mapped package preflight refusal.

**Verification**:
- Command/check: focused error translation pytest
  - Result: PASS - 3 tests passed.
- Command/check: focused shell Ruff check
  - Result: PASS.
- UI product-surface check: N/A - error boundary only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T014 - Implement Strict Job Transport Schemas

**Started**: 2026-07-19 23:43
**Completed**: 2026-07-19 23:45
**Duration**: 2 minutes

**Notes**:
- Implemented the four discriminated source inputs, finite normalized
  preferences, literal consent, age group, and private idempotency-key type.
- Kept URL validation at shape-only HTTPS syntax and left host, DNS, redirect,
  and retrieval policy to the package.
- Added bounded duplicate-aware multipart JSON parsing and a frozen accepted
  response containing only stable job projection fields.

**Files Changed**:
- `backend/app/schemas/jobs.py` - added strict request, metadata, header, and
  response models.
- `backend/app/schemas/__init__.py` - exported the HTTP-level job schemas.

**Verification**:
- Command/check: focused job-schema pytest
  - Result: PASS - 50 tests passed.
- Command/check: focused Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - generated API schema source only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T015 - Enforce Upload Body Size Before Multipart Parsing

**Started**: 2026-07-19 23:45
**Completed**: 2026-07-19 23:47
**Duration**: 2 minutes

**Notes**:
- Implemented a route-scoped pure ASGI cap that rejects declared overflow
  before downstream work and counts every body frame for absent or dishonest
  lengths.
- Added red-then-green invalid/negative/duplicate `Content-Length` coverage
  with a safe `VALIDATION_4004` response.
- Registered a finite file + metadata + framing allowance inside the outer
  request logger so early failures retain trace correlation.

**Files Changed**:
- `backend/app/core/middleware.py` - added finite pure ASGI ingress enforcement.
- `backend/app/main.py` - registered the exact upload path and bounded total.
- `backend/tests/core/test_middleware.py` - added ambiguous framing cases.

**Verification**:
- Command/check: focused middleware pytest
  - Result: PASS - 10 tests passed.
- Command/check: focused Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - request framing only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T016 - Validate And Own Bounded Uploads

**Started**: 2026-07-19 23:47
**Completed**: 2026-07-19 23:49
**Duration**: 2 minutes

**Notes**:
- Implemented finite 64 KiB reads, exact overflow detection, safe basename,
  extension/MIME/magic agreement, and detached reviewed upload data.
- Added real PDF readability, encryption, and page-count validation plus
  no-extract OOXML central-directory checks for traversal, duplicates,
  encryption, macros/active content, entry counts, expanded bytes, and
  required content types.
- Made the async context the owner of framework cleanup and preserved primary
  validation/cancellation errors if a secondary close attempt fails.

**Files Changed**:
- `backend/app/services/txt2crs_uploads.py` - added bounded transport
  acquisition and PDF/OOXML validation.
- `backend/tests/services/test_txt2crs_uploads.py` - corrected one lint-only
  encoding spelling in the tests-first fixture.

**Verification**:
- Command/check: focused upload-service pytest
  - Result: PASS - 25 tests passed.
- Command/check: focused Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - file transport service only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T017 - Compose Durable Submission In The Shell

**Started**: 2026-07-19 23:49
**Completed**: 2026-07-19 23:51
**Duration**: 2 minutes

**Notes**:
- Implemented JSON and upload mapping into exact public package input,
  preference, age, consent, profile, and reservation contracts.
- Read only cached readiness before construction, translated all facade
  failures through the context-free boundary, and let cancellation propagate.
- Notified the worker only after commit and treated hint failure as added
  latency rather than a false failed submission; logs retain only opaque
  owner/job IDs, input category, revision, and stable error codes.

**Files Changed**:
- `backend/app/services/txt2crs_submission.py` - added the thin shell
  composition adapter.

**Verification**:
- Command/check: focused submission-service pytest
  - Result: PASS - 11 tests passed.
- Command/check: focused Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - application service only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T018 - Add Fail-Closed Lifespan Dependencies

**Started**: 2026-07-19 23:51
**Completed**: 2026-07-19 23:53
**Duration**: 2 minutes

**Notes**:
- Added red-then-green dependency tests for missing, wrong-type, and valid
  lifespan application, worker, and submission state.
- Composed one submission adapter after readiness startup from the exact
  lifespan facade/cache/worker and startup-reviewed execution profile.
- Exported only the shell service and profile builder; dependency access does
  no storage or provider work.

**Files Changed**:
- `backend/tests/api/test_txt2crs_dependencies.py` - added fail-closed
  dependency coverage.
- `backend/app/api/deps.py` - added typed application, worker, and submission
  dependencies.
- `backend/app/services/__init__.py` - exported shell composition contracts.
- `backend/app/main.py` - added lifespan submission composition and cleanup.

**Verification**:
- Command/check: dependency and complete lifespan pytest
  - Result: PASS - 13 tests passed.
- Command/check: focused Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - dependency/lifespan wiring only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T019 - Implement Authenticated JSON Submission

**Started**: 2026-07-19 23:53
**Completed**: 2026-07-19 23:54
**Duration**: 1 minute

**Notes**:
- Added the authenticated strict JSON route with the owner-scoped patterned
  header and one call into the lifespan submission service.
- Returned the frozen 202 projection with `Location`, private/no-store,
  no-cache, nosniff, and no-referrer headers only after durable success.
- Registered the finite endpoint rate while preserving idempotent package
  handling as the duplicate-work authority.

**Files Changed**:
- `backend/app/api/routes/jobs.py` - added JSON submission and shared accepted
  response construction.
- `backend/app/core/rate_limit.py` - added the finite job submission rate.
- `backend/app/api/main.py` - registered the jobs router.

**Verification**:
- Command/check: job-route pytest excluding multipart cases
  - Result: PASS - 8 tests passed and 6 upload cases deselected.
- UI product-surface check: N/A - API route only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T020 - Implement Authenticated Multipart Submission

**Started**: 2026-07-19 23:54
**Completed**: 2026-07-19 23:56
**Duration**: 2 minutes

**Notes**:
- Added exact parsed-form cardinality checks so duplicate metadata/files and
  unknown fields cannot be silently selected or ignored by framework parsing.
- Parsed bounded duplicate-aware metadata, entered the upload owner context,
  and delegated the detached bytes through the same submission service and
  accepted-response path as JSON.
- Closed every parsed file on malformed shape/metadata and let the validator
  own cleanup on every success or transport rejection.

**Files Changed**:
- `backend/app/api/routes/jobs.py` - added strict multipart submission and
  rejection cleanup.

**Verification**:
- Command/check: complete authenticated job-route pytest
  - Result: PASS - 14 tests passed.
- Command/check: focused route Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - API route only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T021 - Register Jobs Router And Finite Rate

**Started**: 2026-07-19 23:53
**Completed**: 2026-07-19 23:56
**Duration**: 3 minutes

**Notes**:
- Registered the jobs router once under the existing API prefix and applied
  the shared `10/minute` submission rate to both write routes.
- Left durable engine admission authoritative for owner quota, replay, and
  paid-work protection.

**Files Changed**:
- `backend/app/api/main.py` - registered the jobs router.
- `backend/app/core/rate_limit.py` - added the finite submission limit.

**Verification**:
- Command/check: complete authenticated job-route pytest
  - Result: PASS - includes the enabled limiter's 11th-request 429 contract.
- Command/check: focused Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - route registration only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T022 - Restrict Public Signup To Local Development

**Started**: 2026-07-19 23:56
**Completed**: 2026-07-19 23:58
**Duration**: 2 minutes

**Notes**:
- Added an explicit false-by-default public-signup setting that can be enabled
  only in the local environment; non-local startup rejects the unsafe
  combination.
- Rejected disabled signup before the route performs an email or database
  lookup, using the shell's structured authorization error contract.
- Kept the root judge/demo example closed while documenting the backend-local
  developer example as open.

**Files Changed**:
- `backend/app/core/config.py` - added and validated the local-only setting.
- `backend/app/api/routes/users.py` - enforced signup mode before persistence.
- `.env.example` - kept judge/demo public signup disabled.
- `backend/.env.example` - enabled the opt-in local developer workflow.
- `backend/tests/core/test_txt2crs_settings.py` - covered defaults and the
  local/non-local environment matrix.
- `backend/tests/api/routes/test_users.py` - covered early disabled rejection.

**Verification**:
- Command/check: focused settings and user-route pytest
  - Result: PASS - 81 tests passed.
- Command/check: focused Ruff and strict mypy
  - Result: PASS.
- UI product-surface check: N/A - configuration and API guard only.
- UI craft check: N/A - no UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T023 - Document And Generate The Submission Contract

**Started**: 2026-07-19 23:58
**Completed**: 2026-07-20 00:01
**Duration**: 3 minutes

**Notes**:
- Documented both authenticated write routes, strict JSON and multipart
  shapes, finite transport/container bounds, stable error codes, cleanup
  ownership, response privacy headers, and durable-commit semantics.
- Documented local-only public signup in the configuration catalog and
  environment behavior matrix.
- Regenerated OpenAPI and the TypeScript client with the repository script.
  Confirmed OpenAPI 3.1's binary `contentMediaType` representation generates
  the intended `Blob | File` client type.

**Files Changed**:
- `docs/api/README_api.md` - added the complete public submission contract.
- `docs/CONFIGURATION.md` - documented the signup setting and examples.
- `docs/environments.md` - documented the local/non-local signup matrix.
- `frontend/src/client/` - regenerated the formatter-owned TypeScript client.
- `backend/tests/scripts/test_generate_client_contract.py` - asserted the
  OpenAPI 3.1 multipart representation and strict job contracts.

**Verification**:
- Command/check: `bash scripts/generate-client.sh`
  - Result: PASS - OpenAPI and 18 generated client files formatted.
- Command/check: generated-client contract pytest
  - Result: PASS - 5 tests passed.
- Command/check: focused Ruff and `git diff --check`
  - Result: PASS.
- UI product-surface check: N/A - generated client and API documentation only.
- UI craft check: N/A - no rendered UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T024 - Run Complete Deterministic Quality Gates

**Started**: 2026-07-20 00:01
**Completed**: 2026-07-20 00:04
**Duration**: 3 minutes

**Notes**:
- Ran the complete reusable-engine and application-shell test suites against
  the isolated migrated PostgreSQL database.
- Replaced one process-global `caplog` dependency with a direct structured
  logger double after the full-suite order exposed that test's handler
  coupling; production behavior was unchanged.
- Applied repository Ruff formatting and passed both Python type checkers.
- Passed frontend Biome, TypeScript, and production-build validation against
  the regenerated client.

**Files Changed**:
- `backend/tests/services/test_txt2crs_submission.py` - made structured-log
  evidence independent of process-global handler order.
- Nine backend session files - formatted mechanically with repository Ruff.

**Verification**:
- Command/check: complete txt2crs package pytest
  - Result: PASS - 467 passed, 1 opt-in live subscription test skipped.
- Command/check: package Ruff check/format and strict mypy
  - Result: PASS - 138 source files type-safe and formatted.
- Command/check: complete backend pytest after formatting
  - Result: PASS - 422 passed.
- Command/check: backend Ruff check/format, strict mypy, and `ty`
  - Result: PASS - 100 files formatted; 47 application files type-safe.
- Command/check: frontend Biome, TypeScript, and Vite production build
  - Result: PASS - 138 files checked and 2,204 modules built.
- UI product-surface check: PASS - existing frontend compiles against the new
  generated job client; this session intentionally adds no visible route.
- UI craft check: N/A - no rendered UI work.

**Out-of-Scope Files**:
- `.spec_system/.../implementation-notes.md` - required Apex session evidence.

### Task T025 - Complete Repository Evidence And Hygiene

**Started**: 2026-07-20 00:04
**Completed**: 2026-07-20 00:06
**Duration**: 2 minutes

**Notes**:
- Ran every pre-commit hook across tracked files and then explicitly across
  untracked session files so new routes, schemas, services, tests, and session
  evidence were not omitted.
- Proved a second OpenAPI/client generation produced the same aggregate
  content hash.
- Rechecked the response, error, and structured-log allowlists plus the
  no-provider/no-worker rejection guarantees through focused route, service,
  acceptance, and generated-contract tests.
- Verified every changed or untracked file is ASCII-encoded with LF endings
  and that the complete diff has no whitespace errors.

**Files Changed**:
- `.spec_system/.../tasks.md` - completed the task and session checklist.
- `.spec_system/.../implementation-notes.md` - recorded final evidence.

**Verification**:
- Command/check: pre-commit on all tracked and all untracked files
  - Result: PASS - large-file, case, TOML/YAML, EOF, whitespace, typo, Ruff,
    mypy, `ty`, Biome, TypeScript, generated-client, and Zizmor hooks passed.
- Command/check: repeat generated-artifact aggregate SHA-256 comparison
  - Result: PASS - identical content hash before and after regeneration.
- Command/check: focused submission security/contract pytest
  - Result: PASS - 37 tests passed.
- Command/check: changed-file ASCII/LF scan and `git diff --check`
  - Result: PASS.
- UI product-surface check: PASS - generated client and production build
  evidence remain green.
- UI craft check: N/A - no rendered UI work.

**Out-of-Scope Files**:
- None.

---

## Checkpoints

### Checkpoint 1 - Environment And Baseline

- Tests: 34 engine and 96 shell focused tests pass.
- Scope: Session objectives remain submission/admission only.
- Next task: T003, package preflight tests.

### Checkpoint 2 - First Tests-First Boundary

- Tests: package preflight, shell request schemas, and pure ASGI body-limit
  tests are written and fail only at their missing implementation seams.
- Scope: Public contracts still exclude owner, filesystem, model, budget,
  provider, and policy implementation details.
- Next task: T006, bounded upload and OOXML transport tests.

### Checkpoint 3 - Transport And Route Tests

- Tests: bounded upload, submission composition, and authenticated JSON/upload
  route contracts are written and observed red at missing modules/dependencies.
- Safety: Every rejection path asserts zero facade or worker work where that
  boundary is observable; cancellation and post-commit wake failure are
  explicit.
- Next task: T009, deterministic durable acceptance fixtures.

### Checkpoint 4 - Tests-First Complete And Package Gate Green

- Tests: all planned red suites exist; facade/factory implementation is green
  across 37 focused engine tests.
- Invariant: every facade submission now evaluates version-matched package
  policy before durable service access and uses a factory-reviewed reservation.
- Next task: T012, minimal public exports for shell composition.

### Checkpoint 5 - Public Contracts Green

- Tests: engine export tests, shell error tests, and all 50 strict job-schema
  tests pass.
- Boundaries: Shell imports only documented preflight/reservation/input
  contracts; URL interpretation and policy remain package-owned.
- Next task: T015, route-scoped pure ASGI upload body cap.

### Checkpoint 6 - Submission Safety Services Green

- Tests: ASGI framing, upload validation, and submission composition pass 10,
  25, and 11 focused cases respectively.
- Ordering: Authentication remains a route concern; service order is cached
  readiness -> canonical request -> package preflight/admission/commit ->
  latency-only worker hint.
- Next task: T018, fail-closed lifespan dependencies.

### Checkpoint 7 - Authenticated Write Surface Green

- Tests: fail-closed dependencies/lifespan pass 13 cases and both HTTP write
  routes pass all 14 auth, validation, header, error, cleanup, and rate cases.
- Surface: The router exposes only POST submission endpoints; Phase 03 Session
  02 still owns job reads and artifacts.
- Next task: T022, explicit local-only public signup mode.

### Checkpoint 8 - Complete Submission Contract Green

- Tests: 467 engine tests and 422 shell tests pass; the sole engine skip is the
  explicitly opt-in live ChatGPT subscription test.
- Contracts: generated TypeScript, OpenAPI 3.1 multipart typing, Python
  formatting/lint/types, and frontend build all pass.
- Next task: T025, repository-wide evidence and hygiene gate.

### Checkpoint 9 - Implementation Ready For Review

- Completion: all 25 tasks and every session checklist item are complete.
- Quality: package, shell, generated client, frontend, repository hooks,
  deterministic generation, and file hygiene are green.
- Next step: run `creview`, address every finding, then run `validate`.

---

## Blockers And Solutions

### Blocker 1: Configured Host Database Belongs To Another Project

**Description**: Port 5447 accepted connections but rejected txt2crs
credentials; repository Compose had no running services.
**Impact**: Initial migration prerequisite check could not use the usual port.
**Resolution**: Started the isolated `txt2crs-phase03-db` PostgreSQL 18.4
container on port 55433 and verified current migrations there.
**Time Lost**: 1 minute
