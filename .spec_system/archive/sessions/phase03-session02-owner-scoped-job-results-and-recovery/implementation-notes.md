# Implementation Notes

**Session ID**: `phase03-session02-owner-scoped-job-results-and-recovery`
**Package**: backend
**Started**: 2026-07-20 00:40
**Last Updated**: 2026-07-20 01:52

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | Code review and validation |
| Blockers | 0 |

---

## Task Log

### 2026-07-20 - Session Start

**Environment verified**:
- [x] Apex project and package prerequisites confirmed
- [x] Required tools available
- [x] Directory structure ready
- [x] Isolated PostgreSQL 18 container running on host port 55433
- [x] Alembic revision `fe56fa70289e` is current and is the only head

### Task T001 - Verify Prerequisites And Focused Baseline

**Started**: 2026-07-20 00:40
**Completed**: 2026-07-20 00:41
**Duration**: 1 minute

**Notes**:
- Confirmed Session 01 is complete at base commit
  `d080c4be2fb11e3fd016ca89d7fd495241961356`.
- Confirmed the engine facade/query/stream suites and current shell
  submission/schema/error boundary are green before Session 02 changes.

**Files Changed**:
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded the verified baseline.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T001 complete.

**Verification**:
- Command/check: `bash .spec_system/scripts/check-prereqs.sh --json --env --package backend`
  - Result: PASS - Apex environment and backend package checks passed.
- Command/check: `uv run alembic current && uv run alembic heads` with the isolated PostgreSQL environment
  - Result: PASS - both commands reported `fe56fa70289e (head)`.
- Command/check: `uv run --package txt2crs pytest tests/unit/test_public_job_queries.py tests/integration/test_public_job_query_service.py tests/unit/test_application_facade.py -q`
  - Result: PASS - 28 tests passed.
- Command/check: `uv run pytest tests/api/routes/test_jobs_submission.py tests/core/test_txt2crs_errors.py tests/schemas/test_job_schemas.py -q` with the isolated PostgreSQL environment
  - Result: PASS - 68 tests passed with 16 known dependency warnings.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**Out-of-Scope Files** (files outside declared package):
- `backend/packages/txt2crs/` - the session specification requires public
  engine projection and stream-boundary work consumed by the backend shell.

### Task T002 - Inspect Projection, Stream, ASGI, And Contract Semantics

**Started**: 2026-07-20 00:41
**Completed**: 2026-07-20 00:44
**Duration**: 3 minutes

**Notes**:
- The package projection currently fabricates a 12-unit pre-plan total, caps
  sources at 100, and omits revision, input bytes, resolved preferences,
  result counts, and truncation flags.
- `PipelineCheckpoint` guarantees that `course_plan` and
  `resolved_preferences` arrive together from `design_course` onward.
- The filesystem context verifies size/hash and rewinds one open descriptor
  before yielding; its `finally` closes that descriptor.
- Starlette 1.3 wraps sync iterators but does not close them, and its ASGI 2.4
  send-failure path raises `ClientDisconnect` before background cleanup. The
  API therefore needs response-owned `finally` cleanup.
- The generated contract currently contains only the two job submission POST
  operations; `artifact_response.py` does not yet exist.

**Files Changed**:
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded source-level baseline decisions.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T002 complete.

**Verification**:
- Command/check: targeted `sed`/`rg` inspection of facade, public query,
  checkpoint, artifact reader/store/service, shell schema/route/error, and
  generated-contract test files
  - Result: PASS - ownership and current contract fields matched the session specification.
- Command/check: Python `inspect.getsource` for
  `StreamingResponse.__call__`, `stream_response`, and
  `iterate_in_threadpool`
  - Result: PASS - confirmed send/disconnect behavior and absence of iterator close.
- Command/check: `rg` over `frontend/openapi.json`
  - Result: PASS - only POST `/api/v1/jobs` and `/api/v1/jobs/upload` are present.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**Out-of-Scope Files** (files outside declared package):
- `backend/packages/txt2crs/` - inspected because it owns the public
  projection and verified stream context used by the shell.

### Task T003 - Add Failing Package Projection Tests

**Started**: 2026-07-20 00:44
**Completed**: 2026-07-20 00:46
**Duration**: 2 minutes

**Notes**:
- Added contract expectations for durable revision, exact UTF-8 input size,
  nullable pre-plan totals, resolved course leaves/counts, the 12-source cap,
  and explicit warning/source/conflict truncation.
- Retained the existing private-sentinel assertions so expanding the useful
  projection cannot broaden its trust boundary.

**Files Changed**:
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` - added and
  tightened expanded public projection tests.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded red-test evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T003 complete.

**Verification**:
- Command/check: `uv run --package txt2crs pytest tests/unit/test_public_job_queries.py -q`
  - Result: PASS - red phase observed: 7 expected failures and 9 existing passes.
  - Evidence: failures name missing revision/size/result/truncation fields,
    the 13-source leak, and the fabricated pre-plan total.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Contract alignment: tests now require finite explicit bounds and coherent
  nullable progress before the projection can cross into the shell.
- Error information boundaries: existing private-value absence checks cover
  every newly useful projection branch.

**Out-of-Scope Files** (files outside declared package):
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` - required
  package-owned tests for the shell's public dependency contract.

---

## Next Task

Run Apex `creview`, repair every actionable finding, then run `validate`.

### Task T004 - Add Failing Shell Response-Schema Tests

**Started**: 2026-07-20 00:46
**Completed**: 2026-07-20 00:49
**Duration**: 3 minutes

**Notes**:
- Defined the expected nested status/result/input/progress/artifact response
  shape and fixed safe copy for all nine durable statuses.
- Added strictness, list-bound, private-field rejection, grouped manifest,
  stable ordering, and path/body absence assertions.

**Files Changed**:
- `backend/tests/schemas/test_job_schemas.py` - added read-contract and
  package-to-shell mapper tests.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded red-test evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T004 complete.

**Verification**:
- Command/check: `uv run pytest tests/schemas/test_job_schemas.py -q` with the isolated PostgreSQL environment
  - Result: PASS - red phase observed during collection because
    `ArtifactManifestPublic` and the other new shell contracts do not exist.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Contract alignment: the tests enumerate every package job status and require
  stable shell copy, nested result coherence, and canonical artifact grouping.
- Trust boundary enforcement: unknown checkpoint, evidence, body, and path
  fields are explicitly rejected.

### Task T005 - Add Failing Direct ASGI Stream-Cleanup Tests

**Started**: 2026-07-20 00:49
**Completed**: 2026-07-20 00:52
**Duration**: 3 minutes

**Notes**:
- Added direct ASGI 2.3 and 2.4 coverage for normal exhaustion, receive-side
  disconnect, socket send failure, iterator failure, entry failure, and
  duplicate explicit cleanup.
- Tests require context entry before response construction and exactly one
  context exit across every acquired-resource path.

**Files Changed**:
- `backend/tests/api/test_artifact_response.py` - added response lifecycle tests.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded red-test and checkpoint evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T005 complete.

**Verification**:
- Command/check: `uv run pytest tests/api/test_artifact_response.py -q` with the isolated PostgreSQL environment
  - Result: PASS - red phase observed during collection because the new
    API-owned response module does not exist.
- Checkpoint check: re-read Session 02 objectives and success criteria after
  T003-T005
  - Result: PASS - tests remain limited to public projection, shell mapping,
    and exact stream cleanup; no list/cancel/preview/UI scope was introduced.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Resource cleanup: direct tests cover every ASGI exit path and idempotent
  explicit close.
- Failure path completeness: context-entry failures occur before headers;
  send and iterator failures remain caller-visible after cleanup.

### Task T006 - Add Failing Authenticated Result Route Tests

**Started**: 2026-07-20 00:52
**Completed**: 2026-07-20 00:55
**Duration**: 3 minutes

**Notes**:
- Added status, manifest, and download tests through an overridden public
  facade, including authentication ordering and strict path identifiers.
- Missing and foreign job/manifest/artifact cases assert the same safe
  `JOB_NOT_FOUND`; integrity entry failure asserts a pre-header safe engine
  error.
- Download tests require exact media/length/disposition/privacy headers and
  route-construction cleanup after the context has been entered.

**Files Changed**:
- `backend/tests/api/routes/test_jobs_results.py` - added authenticated read
  and delivery route tests.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded red-test evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T006 complete.

**Verification**:
- Command/check: `uv run pytest tests/api/routes/test_jobs_results.py -q` with the isolated PostgreSQL environment
  - Result: PASS - red phase observed: 15 fixture errors because the package
    input/result projection fields are not implemented.
- UI product-surface check: N/A - API contract only; no UI changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Trust boundary enforcement: authentication and owner IDs are required at
  every facade call; malformed identifiers stop before facade access.
- Error information boundaries: six absence permutations share one detail,
  while integrity detail, path, and hash sentinels remain absent.
- Resource cleanup: a post-entry response-construction failure must close the
  package context once.

### Task T007 - Add Failing Public-Facade Result Acceptance

**Started**: 2026-07-20 00:55
**Completed**: 2026-07-20 00:58
**Duration**: 3 minutes

**Notes**:
- Added one complete public lifecycle asserting the bounded result, all 16
  canonical artifacts, and repeatable verified bytes.
- Added two-owner and missing-identifier isolation for status, manifest, and
  artifact reads, plus close/reopen metadata and byte equality.

**Files Changed**:
- `backend/tests/acceptance/test_job_results_and_recovery.py` - added public
  facade result and delivery acceptance tests.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded red-test evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T007 complete.

**Verification**:
- Command/check: `uv run pytest tests/acceptance/test_job_results_and_recovery.py -q` with the isolated PostgreSQL environment
  - Result: PASS - red phase observed during collection because the complete
    deterministic `DurableResultsHarness` is not implemented.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Trust boundary enforcement: all protected reads pass owner identity into the
  public facade and compare foreign with nonexistent failures.
- Resource cleanup/state freshness: every application and artifact context is
  closed, and reopened reads use fresh facade handles.

### Task T008 - Add Failing Replacement Recovery Acceptance

**Started**: 2026-07-20 00:58
**Completed**: 2026-07-20 01:03
**Duration**: 5 minutes

**Notes**:
- Added serial-worker startup recovery for an accepted job without an
  in-memory wake event.
- Added test-only runtime interruption after `design_course`, renderer
  interruption after the final accepted checkpoint, and filesystem-save
  interruption during delivery.
- Replacement assertions preserve the exact stored request, consume only
  remaining model turns, use no model turn for render/delivery recovery, and
  retain identical repeated artifact bytes.

**Files Changed**:
- `backend/tests/acceptance/test_job_results_and_recovery.py` - added four
  replacement-boundary acceptance tests and bounded worker helper.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded red-test and checkpoint evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T008 complete.

**Verification**:
- Command/check: `uv run pytest tests/acceptance/test_job_results_and_recovery.py -q` with the isolated PostgreSQL environment
  - Result: PASS - red phase remains the missing complete/remainder harness,
    so no production behavior was added before acceptance expectations.
- Checkpoint check: re-read recovery and replay success criteria after T006-T008
  - Result: PASS - accepted, active plan/module, rendering, delivery, owner
    isolation, repeated bytes, and no-model replay are all represented.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- State freshness on re-entry: every boundary closes the first application and
  uses a fresh facade/worker plus exact durable request/checkpoint assertions.
- Duplicate action prevention: replacement stage recordings prove accepted
  model work is not repeated.
- Resource cleanup: every worker, executor owner, application, and stream has
  a bounded `finally` or context exit.

### Task T009 - Add Failing Error And Generated-Contract Tests

**Started**: 2026-07-20 01:03
**Completed**: 2026-07-20 01:06
**Duration**: 3 minutes

**Notes**:
- Added safe translation expectations for public projection and artifact
  integrity errors.
- Added generated OpenAPI expectations for three authenticated GET routes,
  bounded identifiers, strict response schemas, binary content, registered
  errors, and explicit absence of an ETag contract.

**Files Changed**:
- `backend/tests/core/test_txt2crs_errors.py` - added package read/integrity mappings.
- `backend/tests/scripts/test_generate_client_contract.py` - added generated
  status, manifest, and download contract assertions.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded red-test evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T009 complete.

**Verification**:
- Command/check: `uv run pytest tests/core/test_txt2crs_errors.py tests/scripts/test_generate_client_contract.py -q` with the isolated PostgreSQL environment
  - Result: PASS - red phase observed: 3 expected failures and 7 existing passes.
  - Evidence: integrity maps to generic internal today, and generated GET paths
    are absent.
- UI product-surface check: N/A - generated transport contract only.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Error information boundaries: typed integrity/projection failures must map
  to one context-free registered shell error.
- Contract alignment: OpenAPI tests protect auth, path bounds, schema names,
  binary delivery, and the no-conditional-HTTP decision.

### Task T010 - Implement Expanded Package Public Snapshot

**Started**: 2026-07-20 01:06
**Completed**: 2026-07-20 01:12
**Duration**: 6 minutes

**Notes**:
- Added durable revision, exact UTF-8/byte input size, nullable pre-plan
  totals, accepted resolved preference leaves, objective/module counts, and
  explicit truncation.
- Tightened sources to 12 and preserved accurate truncation after
  sanitization/deduplication; added coherence validators for result groups,
  terminal failure, complete progress, and full-page truncation flags.

**Files Changed**:
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` - implemented
  the bounded projection.
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` - formatted
  the tests-first contract.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded implementation evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T010 complete.

**Verification**:
- Command/check: `uv run --package txt2crs pytest tests/unit/test_public_job_queries.py -q`
  - Result: PASS - 16 tests passed.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/public_queries.py tests/unit/test_public_job_queries.py`
  - Result: PASS - no lint findings.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Trust boundary enforcement: all added values are copied from validated
  request/checkpoint leaves inside the package.
- Contract alignment: coherent all-or-none result fields and nullable
  pre-plan progress are enforced by immutable public models.
- Error information boundaries: projection validation still collapses private
  Pydantic/value context into one context-free package error.

**Out-of-Scope Files** (files outside declared package):
- `backend/packages/txt2crs/` - required public engine projection dependency
  defined by the session specification.

### Task T011 - Protect Public Exports And Reopen Coherence

**Started**: 2026-07-20 01:12
**Completed**: 2026-07-20 01:15
**Duration**: 3 minutes

**Notes**:
- The expanded fields live on already-exported immutable contracts, so
  `txt2crs.jobs.__all__` required no new runtime symbol and continues to hide
  the private projection helper.
- Extended the real SQLite/filesystem reopen test to compare durable revision,
  exact input bytes, nullable progress, absent pre-plan result, and false
  truncation flags.

**Files Changed**:
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - extended close/reopen projection assertions.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded integration and checkpoint evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T011 complete.

**Verification**:
- Command/check: `uv run --package txt2crs pytest tests/integration/test_public_job_query_service.py tests/unit/test_public_package_exports.py -q`
  - Result: PASS - 7 tests passed.
- Checkpoint check: `uv run --package txt2crs pytest tests/unit/test_public_job_queries.py tests/integration/test_public_job_query_service.py tests/unit/test_public_package_exports.py -q`
  - Result: PASS - 23 tests passed.
- Command/check: focused package Ruff check
  - Result: PASS - no lint findings.
- Scope check: Session 02 objectives/success criteria re-read
  - Result: PASS - package work is limited to bounded public reads and does not
    introduce shell-owned projection logic or lifecycle scope.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- State freshness on re-entry: the integration test compares projection
  fields only after closing and reopening both authoritative stores.
- Contract alignment: the existing lazy public exports remain sufficient and
  private construction helpers stay unavailable.

**Out-of-Scope Files** (files outside declared package):
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - required public dependency integration test.

### Task T012 - Implement Strict Status And Result Schemas

**Started**: 2026-07-20 01:15
**Completed**: 2026-07-20 01:20
**Duration**: 5 minutes

**Notes**:
- Added strict frozen progress, input, failure, source, result, artifact
  availability, and top-level status response models.
- The mapper uses a total nine-status fixed-copy table, nests package leaves
  explicitly, and derives a manifest URL only when verified artifacts exist.

**Files Changed**:
- `backend/app/schemas/jobs.py` - implemented owner-safe status/result
  contracts and explicit package mapper.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded focused verification.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T012 complete.

**Verification**:
- Command/check: `uv run ruff check app/schemas/jobs.py`
  - Result: PASS - no lint findings.
- Command/check: `uv run mypy app/schemas/jobs.py`
  - Result: PASS - strict type check reported no issues.
- Command/check: `uv run python` focused construction of a complete package
  snapshot and `JobStatusPublic.from_package`
  - Result: PASS - ready copy, coherent result, and manifest URL matched.
- UI product-surface check: N/A - response schemas only.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Contract alignment: response models repeat finite package bounds and reject
  incoherent truncation/progress/availability.
- Error information boundaries: private checkpoint labels never enter the
  response; all progress messages come from a fixed status table.

### Task T013 - Implement Grouped Artifact Manifest Schemas

**Started**: 2026-07-20 01:20
**Completed**: 2026-07-20 01:25
**Duration**: 5 minutes

**Notes**:
- Added strict path-free artifact metadata, canonical deliverable groups, and
  a grouped manifest mapper over the package's verified descriptors.
- Stable download URLs, canonical group/ID order, unique formats, safe
  filename/media checks, finite size, and labeled SHA-256 are enforced.

**Files Changed**:
- `backend/app/schemas/jobs.py` - implemented artifact metadata/group/manifest contracts.
- `backend/tests/schemas/test_job_schemas.py` - corrected the body-absence
  assertion to distinguish a forbidden `content` field from `content_hash`.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded focused evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T013 complete.

**Verification**:
- Command/check: `uv run pytest tests/schemas/test_job_schemas.py -q` with the isolated PostgreSQL environment
  - Result: PASS - 62 tests passed.
- Command/check: `uv run ruff check app/schemas/jobs.py tests/schemas/test_job_schemas.py`
  - Result: PASS - no lint findings.
- Command/check: `uv run mypy app/schemas/jobs.py`
  - Result: PASS - strict type check reported no issues.
- UI product-surface check: N/A - response schemas only.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Contract alignment: package metadata maps to exactly four possible
  deliverables and four unique formats per group.
- Trust boundary enforcement: body/path fields cannot enter the strict
  response and header-adjacent strings reject control characters.

### Task T014 - Implement Response-Owned Artifact Cleanup

**Started**: 2026-07-20 01:25
**Completed**: 2026-07-20 01:30
**Duration**: 5 minutes

**Notes**:
- Added an entered-context iterator with locked idempotent close and an ASGI
  response whose shielded `finally` owns cleanup.
- Construction, success, legacy receive disconnect, modern send failure,
  iterator failure, and duplicate explicit close all settle the same context
  exactly once.
- A primary stream error remains authoritative if cleanup also fails; only a
  fixed safe log event is emitted for that secondary failure.

**Files Changed**:
- `backend/app/api/artifact_response.py` - implemented context ownership and
  streaming response.
- `backend/tests/api/test_artifact_response.py` - applied current annotation/import style.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded lifecycle and checkpoint evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T014 complete.

**Verification**:
- Command/check: `uv run pytest tests/api/test_artifact_response.py -q` with the isolated PostgreSQL environment
  - Result: PASS - 6 tests passed.
- Command/check: focused Ruff and mypy checks for `artifact_response.py`
  - Result: PASS - no lint or type findings.
- Checkpoint check: `uv run pytest tests/schemas/test_job_schemas.py tests/api/test_artifact_response.py -q`
  - Result: PASS - 68 tests passed.
- Scope check: Session 02 delivery objectives re-read
  - Result: PASS - response owns only entered verified streams; integrity,
    authorization, metadata, and storage remain package-owned.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Resource cleanup/concurrency safety: the same lock serializes finite reads
  with exactly-once close, including disconnect races.
- Failure path completeness: entry fails before response creation, while
  post-header errors remain visible after cleanup.

### Task T015 - Map Public Read And Integrity Errors

**Started**: 2026-07-20 01:30
**Completed**: 2026-07-20 01:31
**Duration**: 1 minute

**Notes**:
- Added package projection and integrity errors to the existing context-free
  engine-operation mapping while retaining `JobNotFoundError` as the sole
  owner-hidden 404 boundary.

**Files Changed**:
- `backend/app/core/txt2crs_errors.py` - added typed read/integrity mappings.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded focused evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T015 complete.

**Verification**:
- Command/check: `uv run pytest tests/core/test_txt2crs_errors.py -q`
  - Result: PASS - 3 tests passed.
- Command/check: focused Ruff and mypy checks for `txt2crs_errors.py`
  - Result: PASS - no lint or type findings.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Error information boundaries: package exception messages, paths, hashes, and
  checkpoint detail cannot reach the shell error.

### Task T016 - Add Owner-Scoped Status And Result Route

**Started**: 2026-07-20 01:31
**Completed**: 2026-07-20 01:35
**Duration**: 4 minutes

**Notes**:
- Added authenticated bounded job ID validation, public-facade query,
  explicit schema mapping, registered safe errors, and fixed privacy headers.
- P0 exposes durable revision and `private, no-store` without ETag or 304
  behavior.

**Files Changed**:
- `backend/app/api/routes/jobs.py` - added `GET /jobs/{job_id}` and shared
  private-response/error metadata.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded route evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T016 complete.

**Verification**:
- Command/check: focused status/auth/owner-hidden route selection from
  `tests/api/routes/test_jobs_results.py`
  - Result: PASS - 4 tests passed with known JWT key-length warnings.
- Command/check: focused Ruff and mypy checks for `app/api/routes/jobs.py`
  - Result: PASS - no lint or type findings.
- UI product-surface check: N/A - API route only.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Trust boundary enforcement: the route authenticates, validates the opaque
  path, and authorizes inside `get_public_job`.
- Error information boundaries: only the central translator handles package
  failures, and success copies only `JobStatusPublic`.

### Task T017 - Add Owner-Scoped Manifest Route

**Started**: 2026-07-20 01:35
**Completed**: 2026-07-20 01:38
**Duration**: 3 minutes

**Notes**:
- Added the authenticated manifest GET through package authorization and
  integrity verification, followed by canonical grouped allowlist mapping.
- The route shares the fixed non-cacheable response and registered safe error
  contract with status polling.

**Files Changed**:
- `backend/app/api/routes/jobs.py` - added `GET /jobs/{job_id}/artifacts`.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded route evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T017 complete.

**Verification**:
- Command/check: focused manifest/owner-hidden selection from
  `tests/api/routes/test_jobs_results.py`
  - Result: PASS - 3 tests passed with known JWT key-length warnings.
- Command/check: focused Ruff and mypy checks for `app/api/routes/jobs.py`
  - Result: PASS - no lint or type findings.
- UI product-surface check: N/A - API route only.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Trust boundary enforcement: authorization and manifest integrity are one
  package call using the authenticated owner.
- Contract alignment: only stable grouped metadata leaves the shell mapper.

### Task T018 - Add Verified Artifact Download Route

**Started**: 2026-07-20 01:38
**Completed**: 2026-07-20 01:44
**Duration**: 6 minutes

**Notes**:
- Added canonical metadata lookup, uniform missing-ID handling, package stream
  reauthorization/entry before headers, and response ownership transfer.
- Downloads use exact package media/length, ASCII RFC 5987 attachment
  encoding, private/no-store, no-cache, nosniff, and no-referrer headers.
- A construction failure after entry closes once while preserving the primary
  error and logging only fixed safe copy if cleanup also fails.

**Files Changed**:
- `backend/app/api/routes/jobs.py` - added
  `GET /jobs/{job_id}/artifacts/{artifact_id}` and safe header helpers.
- `backend/tests/api/routes/test_jobs_results.py` - recorded the fixture-only
  manifest dependency explicitly for lint.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded route and checkpoint evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T018 complete.

**Verification**:
- Command/check: `uv run pytest tests/api/routes/test_jobs_results.py -q`
  - Result: PASS - 15 tests passed with 15 known JWT warnings.
- Command/check: focused Ruff and mypy checks for the route
  - Result: PASS - no lint or type findings.
- Checkpoint check: focused error/schema/response/route suites
  - Result: PASS - 86 tests passed with 15 known JWT warnings.
- Scope check: Session 02 HTTP success criteria re-read
  - Result: PASS - three private GETs, one hidden 404, no ETag/304, no preview
    rendering, and no shell access to stores/checkpoints/filesystem paths.
- UI product-surface check: N/A - API route only.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- Resource cleanup: context entry precedes headers and every post-entry route
  or ASGI failure has exactly-one cleanup ownership.
- Trust boundary enforcement: metadata and bytes are independently
  owner-authorized through package calls.
- Error information boundaries: disposition is percent-encoded and logs omit
  filenames, IDs, hashes, exceptions, and paths.

### Task T019 - Build Complete And Remainder Acceptance Harness

**Started**: 2026-07-20 01:44
**Completed**: 2026-07-20 01:46
**Duration**: 2 minutes

**Notes**:
- Added one strict six-turn course scenario with integrity-valid evidence,
  compact stored profile, complete course/review/assessment/answer outputs,
  and 16-artifact rendering.
- Added scenario slicing after accepted stages, a fail-loud local replay
  scenario, optional scenario selection on reopen, and bounded public status
  waits.
- Kept fault injection test-only through the fake runtime, renderer, and
  filesystem-store monkeypatch controls used by the acceptance module.

**Files Changed**:
- `backend/tests/acceptance/conftest.py` - added complete/remainder scenarios,
  exact request/profile, reopen selection, and bounded wait helpers.
- `backend/tests/acceptance/test_job_results_and_recovery.py` - formatted and
  repaired test-only control imports/recording closure.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded harness evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T019 complete.

**Verification**:
- Command/check: focused completed-read/owner/reopen selection from
  `tests/acceptance/test_job_results_and_recovery.py`
  - Result: PASS - 3 tests passed and 4 replacement tests were deselected.
- Command/check: `uv run pytest tests/acceptance/test_job_submission.py -q`
  - Result: PASS - all 7 Session 01 acceptance tests remain green under the
    compact but still finite stored profile.
- Command/check: focused acceptance Ruff check
  - Result: PASS - no lint findings.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- State freshness on re-entry: every harness open creates fresh provider and
  facade state over the same exact durable directory.
- External dependency resilience: all scenarios remain credential-free,
  network-free, and bounded by finite worker polling.
- Contract alignment: the request goal/profile, course plan, assessment item
  count, and six outputs are mutually validated.

**Out-of-Scope Files** (files outside declared package):
- `backend/packages/txt2crs` test-only imports supply deterministic
  evidence/fault controls; production shell code still uses only public
  application/jobs boundaries.

### Task T020 - Prove Replacement And Repeated-Delivery Acceptance

**Started**: 2026-07-20 01:46
**Completed**: 2026-07-20 01:47
**Duration**: 1 minute

**Notes**:
- Exercised accepted-job discovery after process replacement, resumption after
  the durable `design_course` checkpoint, deterministic render replay, and
  delivery replay after the first filesystem save.
- Verified owner/missing-job indistinguishability, identical metadata and
  bytes after reopen, and repeatable bytes from the verified stream boundary.
- Corrected the fault-injection assertions to distinguish runtime request
  stage names from durable checkpoint stage names; the test now interrupts
  immediately before the first module provider turn and proves only remaining
  turns execute after replacement.

**Files Changed**:
- `backend/tests/acceptance/test_job_results_and_recovery.py` - completed the
  seven-scenario private-result and restart/replay acceptance matrix.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded acceptance evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T020 complete.

**Verification**:
- Command/check: `uv run pytest tests/acceptance/test_job_results_and_recovery.py -q` with the isolated PostgreSQL environment
  - Result: PASS - all 7 recovery, ownership, reopen, and delivery tests passed.
- Command/check: focused acceptance Ruff check and format check
  - Result: PASS - both acceptance files are lint-clean and already formatted.
- UI product-surface check: N/A - no UI files changed.
- UI craft check: N/A - no UI files changed.

**BQC Fixes**:
- State freshness on re-entry: each replacement uses a fresh facade, executor
  or worker over the same durable job directory.
- External dependency resilience: all failure points are deterministic,
  bounded, credential-free, and network-free.
- Resource cleanup: every application, worker, executor context, and opened
  artifact stream is closed on success and failure.

### Task T021 - Document Contracts And Regenerate The Frontend Client

**Started**: 2026-07-20 01:47
**Completed**: 2026-07-20 01:48
**Duration**: 1 minute

**Notes**:
- Documented bounded revision polling, complete-or-null results, uniform
  owner-hidden 404s, canonical manifest metadata, pre-header verification,
  exactly-once stream cleanup, and safe integrity failures.
- Documented accepted/active/render/delivery replacement behavior and the
  operator response for stalled jobs or artifact-integrity incidents.
- Regenerated OpenAPI-derived TypeScript types, schemas, and SDK methods only
  through `scripts/generate-client.sh`; no generated file was hand-edited.

**Files Changed**:
- `docs/api/README_api.md` - documented all owner-scoped status, manifest,
  download, bounds, headers, errors, and replay semantics.
- `docs/ARCHITECTURE.md` - recorded package/shell read ownership and durable
  checkpoint/render/delivery recovery flow.
- `docs/runbooks/incident-response.md` - added stalled-job and artifact
  integrity/delivery procedures.
- `backend/app/api/routes/jobs.py` - kept the OpenAPI description free of an
  advertised conditional-validator header.
- `backend/tests/scripts/test_generate_client_contract.py` - verifies the
  three generated read/download operations and bounded binary contract.
- `frontend/src/client/` - generator-created schemas, types, SDK, and exports.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded contract evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T021 complete.

**Verification**:
- Command/check: `bash scripts/generate-client.sh`
  - Result: PASS - OpenAPI export, SDK generation, and Biome formatting
    completed through the repository script.
- Command/check: `uv run pytest tests/scripts/test_generate_client_contract.py -q` with the isolated PostgreSQL environment
  - Result: PASS - all 7 static generation-contract tests passed.
- Command/check: generated SDK symbol inspection
  - Result: PASS - `readJob`, `readJobArtifacts`, and
    `downloadJobArtifact` are present with their generated response models.
- Command/check: `git diff --check`
  - Result: PASS - no whitespace errors.
- UI product-surface check: N/A - generated client only; no rendered UI changed.
- UI craft check: N/A - generated client only; no rendered UI changed.

**BQC Fixes**:
- Contract alignment: documentation, OpenAPI, generator tests, and generated
  client use the same bounded identifiers and response schemas.
- Error information boundaries: operator and client guidance explicitly
  forbids leaking source values, bytes, hashes, filenames, paths, or private
  exceptions.
- Resource cleanup: download documentation matches response-owned
  exactly-once context closure for every ASGI exit.

### Task T022 - Run Focused Engine And Shell Verification

**Started**: 2026-07-20 01:48
**Completed**: 2026-07-20 01:49
**Duration**: 1 minute

**Notes**:
- Verified the package projection/query service, public application facade,
  and filesystem artifact store together.
- Verified shell schema mapping, error translation, entered-body ASGI
  cleanup, owner-scoped routes, replacement acceptance, and generated
  OpenAPI contracts together.
- Applied Ruff's formatter to one static generator-contract test; no
  production behavior changed.

**Files Changed**:
- `backend/tests/scripts/test_generate_client_contract.py` - formatter-only
  normalization after the contract additions.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded focused verification.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T022 complete.

**Verification**:
- Command/check: focused engine public-query/facade/artifact-store tests
  - Result: PASS - 49 tests passed.
- Command/check: focused shell schema/error/ASGI/route/acceptance/generator tests
  - Result: PASS - 100 tests passed with 15 known short-test-key warnings.
- Command/check: focused engine Ruff and strict mypy
  - Result: PASS - Ruff clean and no issues across 138 engine source files.
- Command/check: focused shell Ruff check/format, strict mypy, and ty
  - Result: PASS - all 11 focused files are formatted; shell typing is clean
    across 48 source files.
- UI product-surface check: N/A - no rendered UI files changed.
- UI craft check: N/A - no rendered UI files changed.

**Checkpoint (T019-T022)**:
- Acceptance recovery matrix: PASS - 7/7 scenarios.
- Static OpenAPI generation contract: PASS - 7/7 tests.
- Focused engine/shell suites: PASS - 149 tests total.
- Focused lint/format/type gates: PASS.

**BQC Fixes**:
- Contract alignment: package, transport, acceptance, and generated-client
  contracts pass in one focused checkpoint.
- State freshness on re-entry: replacement acceptance remains green alongside
  facade and durable-store tests.
- Resource cleanup: direct ASGI and real facade stream tests both pass.

### Task T023 - Run Complete Engine And Backend Gates

**Started**: 2026-07-20 01:49
**Completed**: 2026-07-20 01:50
**Duration**: 1 minute

**Notes**:
- Ran both owning Python package gates in parallel without changing their
  configuration roots.
- Preserved the isolated PostgreSQL 18 environment for the complete shell
  suite; the engine suite remained credential-free and used package-owned
  local test state.

**Files Changed**:
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded full-suite evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T023 complete.

**Verification**:
- Command/check: complete engine pytest suite
  - Result: PASS - 470 tests passed and the explicitly opt-in live Codex test
    was skipped.
- Command/check: engine Ruff check/format and strict mypy
  - Result: PASS - 138 files are formatted and typed with no issues.
- Command/check: complete backend pytest suite with isolated PostgreSQL
  - Result: PASS - 471 tests passed with 102 known dependency/test-key
    warnings.
- Command/check: backend Ruff check/format, strict mypy, and ty
  - Result: PASS - 104 files are formatted; all 48 app source files are clean
    under both type checkers.
- UI product-surface check: N/A - Python verification only.
- UI craft check: N/A - Python verification only.

**BQC Fixes**:
- Regression control: every engine and shell test passes under its owning
  project configuration.
- Contract alignment: no focused-only configuration masks failures in the
  complete suites.

### Task T024 - Prove Generator Stability And Frontend Health

**Started**: 2026-07-20 01:50
**Completed**: 2026-07-20 01:51
**Duration**: 1 minute

**Notes**:
- Ran the repository generator twice from identical source and hashed the
  OpenAPI document plus every generated client file after each run.
- Confirmed identical aggregate SHA-256 output, then ran all frontend static
  and production-build gates without touching generated files manually.

**Files Changed**:
- `frontend/src/client/` - deterministic output from the repository generator.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded stability/build evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - marked T024 complete.

**Verification**:
- Command/check: two consecutive `bash scripts/generate-client.sh` runs
  - Result: PASS - aggregate generated-contract SHA-256 remained
    `464822fd2bf462e0446b35c44112ef04754a684c52541e112e9ee492916f7428`.
- Command/check: `npm --prefix frontend run lint`
  - Result: PASS - 138 files checked with no fixes.
- Command/check: `npm --prefix frontend run typecheck`
  - Result: PASS - build TypeScript configuration has no errors.
- Command/check: `npm --prefix frontend run build`
  - Result: PASS - 2,204 modules transformed and the Vite production bundle
    completed.
- UI product-surface check: N/A - generated API client only.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:
- Generation determinism: repeated OpenAPI/client generation is byte-stable.
- Contract alignment: the generated client compiles in both no-emit and
  production-build configurations.

### Task T025 - Run Repository Hooks And Final Boundary Audits

**Started**: 2026-07-20 01:51
**Completed**: 2026-07-20 01:52
**Duration**: 1 minute

**Notes**:
- Ran the complete hook chain over every tracked file and again over every
  explicit untracked file so new response/test/spec files could not bypass
  repository automation.
- Rechecked safe logging/error translation, entered-context ownership,
  no-provider render/delivery replay, changed-file encoding, line endings, and
  diff whitespace.
- Re-ran the direct ASGI response, real authenticated routes, and recovery
  acceptance matrix after the hook chain.

**Files Changed**:
- `docs/api/README_api.md` - replaced non-ASCII punctuation found by the
  explicit changed-file encoding audit.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md` - recorded final implementation evidence.
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md` - completed T025 and the implementation checklist.

**Verification**:
- Command/check: `pre-commit run --all-files`
  - Result: PASS - every hook passed, including Ruff, mypy, ty, Biome,
    TypeScript, client generation, and Zizmor.
- Command/check: `pre-commit run --files <every explicit untracked file>`
  - Result: PASS - all applicable hooks passed for new files.
- Command/check: explicit changed/untracked ASCII and CRLF byte audit
  - Result: PASS - all 25 files are ASCII encoded with LF line endings.
- Command/check: static error/log privacy and stream-cleanup/no-provider-replay inspection
  - Result: PASS - no private exception/detail logging patterns; entered
    context and shielded exactly-once cleanup are present; render/delivery
    tests use a fail-loud runtime scenario.
- Command/check: `git diff --check`
  - Result: PASS - no whitespace errors.
- Command/check: direct response/route/recovery suite
  - Result: PASS - 28 tests passed with 15 known short-test-key warnings.
- UI product-surface check: N/A - API-only implementation.
- UI craft check: N/A - no rendered UI changed.

**Checkpoint (T023-T025)**:
- Complete engine: PASS - 470 passed, 1 opt-in live test skipped.
- Complete backend: PASS - 471 passed.
- Frontend lint/typecheck/build: PASS.
- Repository hooks, explicit new-file hooks, encoding, privacy, cleanup,
  replay, and diff hygiene: PASS.

**BQC Fixes**:
- Error information boundaries: static and behavioral checks confirm only
  safe fixed error/log output crosses the shell.
- Resource cleanup: direct ASGI tests and source inspection cover every
  entered-context exit.
- State freshness on re-entry: render and delivery replacement remain
  provider-free under fresh application handles.
