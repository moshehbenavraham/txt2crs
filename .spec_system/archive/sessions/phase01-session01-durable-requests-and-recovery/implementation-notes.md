# Implementation Notes

**Session ID**: `phase01-session01-durable-requests-and-recovery`
**Package**: backend/packages/txt2crs
**Started**: 2026-07-19 12:00 IDT
**Last Updated**: 2026-07-19 12:56 IDT

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 23 / 23 |
| Estimated Remaining | 0 hours |
| Blockers | 0 |

---

## Task Log

### 2026-07-19 - Session Start

**Environment verified**:

- [x] Spec system and active session confirmed by the deterministic analyzer.
- [x] Package registration, directory, manifest, uv, jq, and git available.
- [x] Engine-owned SQLite schema artifact identified as packaged migration 003.
- [x] No PostgreSQL service is required for this engine-only session.

---

### Task T001 - Record The Engine And Job-State Baseline

**Started**: 2026-07-19 12:00 IDT
**Completed**: 2026-07-19 12:00 IDT
**Duration**: 1 minute

**Notes**:

- Confirmed Phase 01 Session 01 and the `backend/packages/txt2crs` package.
- Established the credential-free baseline before production-code edits.

**Files Changed**:

- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/implementation-notes.md` - Recorded prerequisite and baseline evidence.
- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/tasks.md` - Marked T001 complete.

**Verification**:

- Command/check: `bash .spec_system/scripts/analyze-project.sh --json`
  - Result: PASS - Phase 01, active Session 01, package and planning artifacts found.
- Command/check: `bash .spec_system/scripts/check-prereqs.sh --json --env --package backend/packages/txt2crs`
  - Result: PASS - required environment and registered package checks passed.
- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS - 223 passed and 1 explicit live-provider test skipped in 3.91 seconds.
- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_job_service.py tests/integration/test_sqlite_job_store.py tests/integration/test_admission_quotas.py`
  - Result: PASS - 18 focused existing job-state tests passed in 0.82 seconds.
- UI product-surface check: N/A - engine persistence session has no UI.
- UI craft check: N/A - engine persistence session has no UI.

**BQC Fixes**:

- N/A - T001 recorded the unchanged baseline before runtime behavior changes.

---

### Task T002 - Write Failing Generation Request Contract Tests

**Started**: 2026-07-19 12:01 IDT
**Completed**: 2026-07-19 12:03 IDT
**Duration**: 2 minutes

**Notes**:

- Defined the expected strict public contracts before creating production code.
- Covered request/profile drift, mutation, finite limits, input bounds,
  canonical identity, binary persistence, tamper detection, and safe errors.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_generation_requests.py` - Added
  twelve scenario groups plus parameterized boundary cases.

**Verification**:

- Command/check: `uv run python -m py_compile tests/unit/test_generation_requests.py`
  - Result: PASS - the new test module is syntactically valid.
- Command/check: `rg -n '^def test_|^@pytest.mark.parametrize' tests/unit/test_generation_requests.py`
  - Result: PASS - twelve named scenario groups and four parameter tables found.
- UI product-surface check: N/A - engine contract tests have no UI.
- UI craft check: N/A - engine contract tests have no UI.

**BQC Fixes**:

- Trust boundary: tests require unknown-field rejection, hash verification,
  input bounds, and non-echoing integrity errors.
- Contract alignment: tests define one immutable exact request/profile API.

---

### Task T003 - Write Failing Atomic Request Store Tests

**Started**: 2026-07-19 12:03 IDT
**Completed**: 2026-07-19 12:06 IDT
**Duration**: 3 minutes

**Notes**:

- Added real SQLite scenarios for atomic three-row admission, exact replay,
  changed request/reservation conflict, owner isolation, and close/reopen.
- Added migration-2 upgrade, corrupt-state, and trigger-induced rollback tests.

**Files Changed**:

- `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`
  - Added eight request-envelope persistence and recovery scenarios.

**Verification**:

- Command/check: `uv run python -m py_compile tests/integration/test_generation_request_store.py`
  - Result: PASS - the integration test module is syntactically valid.
- Command/check: `rg -n '^def test_' tests/integration/test_generation_request_store.py`
  - Result: PASS - eight named persistence/recovery scenarios found.
- UI product-surface check: N/A - engine SQLite tests have no UI.
- UI craft check: N/A - engine SQLite tests have no UI.

**BQC Fixes**:

- Mutation safety: tests require exact idempotency and full rollback.
- Trust boundary: tests require owner checks and safe corrupt-state errors.
- State freshness: tests close and reopen the store before recovery.

---

### Task T004 - Write Failing Runnable Discovery Tests

**Started**: 2026-07-19 12:06 IDT
**Completed**: 2026-07-19 12:08 IDT
**Duration**: 2 minutes

**Notes**:

- Defined recovery-first priority across every non-terminal state.
- Added deterministic timestamp/job-ID ordering, restart, terminal exclusion,
  empty-queue, and missing-envelope behavior.

**Files Changed**:

- `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`
  - Added four runnable discovery scenarios and controlled-clock helpers.

**Verification**:

- Command/check: `uv run python -m py_compile tests/integration/test_generation_request_store.py`
  - Result: PASS - the expanded integration module is syntactically valid.
- Command/check: `rg -n '^def test_runnable' tests/integration/test_generation_request_store.py`
  - Result: PASS - four named discovery scenarios found.
- UI product-surface check: N/A - engine queue tests have no UI.
- UI craft check: N/A - engine queue tests have no UI.

**BQC Fixes**:

- State freshness: restart behavior revalidates persisted requests.
- Failure path completeness: missing envelopes fail closed instead of being
  silently skipped.
- Concurrency safety: stable bounded ordering prevents ambiguous selection.

---

### Task T005 - Observe The Tests Fail Before Implementation

**Started**: 2026-07-19 12:08 IDT
**Completed**: 2026-07-19 12:09 IDT
**Duration**: 1 minute

**Notes**:

- Ran both new suites before creating any production request module.
- Both stopped at the expected missing-boundary import, proving the tests are
  not passing against the old hash-only implementation.

**Files Changed**:

- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/implementation-notes.md` - Recorded red-test evidence.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_generation_requests.py tests/integration/test_generation_request_store.py`
  - Result: EXPECTED FAIL - two collection errors report `No module named 'txt2crs.jobs.requests'`.
  - Evidence: production request contracts and persistence boundary do not yet exist.
- UI product-surface check: N/A - engine tests have no UI.
- UI craft check: N/A - engine tests have no UI.

**BQC Fixes**:

- N/A - this task established the required tests-first red state.

---

### Task T006 - Implement Strict Frozen Request And Profile Contracts

**Started**: 2026-07-19 12:09 IDT
**Completed**: 2026-07-19 12:12 IDT
**Duration**: 3 minutes

**Notes**:

- Added immutable Pydantic contracts for intent, age, retry, input bounds, run
  limits, execution versions, and the complete request shape.
- Enforced unique goals/flags, coherent retry/research ceilings, non-empty
  input, and the stored input-byte cap.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` - Added strict
  contract classes and cross-field validators.
- `backend/packages/txt2crs/tests/unit/test_generation_requests.py` - Corrected
  retry-count semantics and a lint-only line wrap.

**Verification**:

- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/requests.py tests/unit/test_generation_requests.py`
  - Result: PASS - no lint findings.
- Command/check: direct uv Python import of all seven new contract classes
  - Result: PASS - request contract classes import successfully.
- UI product-surface check: N/A - engine contracts have no UI.
- UI craft check: N/A - engine contracts have no UI.

**BQC Fixes**:

- Trust boundary: unknown fields, invalid enums, incoherent limits, empty
  input, and oversized input fail at model validation.
- Contract alignment: retry attempts and budget retries now share their actual
  existing runtime semantics.

---

### Task T007 - Implement Canonical Serialization And Hash Validation

**Started**: 2026-07-19 12:12 IDT
**Completed**: 2026-07-19 12:15 IDT
**Duration**: 3 minutes

**Notes**:

- Added type-tagged text/byte encoding, canonical ASCII JSON, URL-safe base64,
  SHA-256 creation, deserialization, and recomputed integrity checks.
- Revalidates the hash during model construction and storage serialization so
  nested input mutation cannot persist under a stale identity.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` - Added request
  factory, codecs, canonical serialization, and integrity validation.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_generation_requests.py`
  - Result: PASS - 19 request contract and canonicalization cases passed.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/requests.py tests/unit/test_generation_requests.py`
  - Result: PASS - no lint findings.
- UI product-surface check: N/A - engine serialization has no UI.
- UI craft check: N/A - engine serialization has no UI.

**BQC Fixes**:

- Mutation safety: serialization recomputes identity after construction.
- Error boundary: malformed codecs and hashes use stable messages without
  echoing learner content.
- Contract alignment: text and byte values have distinct reversible encodings.

---

### Task T008 - Centralize Valid Request And Profile Factories

**Started**: 2026-07-19 12:15 IDT
**Completed**: 2026-07-19 12:18 IDT
**Duration**: 3 minutes

**Notes**:

- Added one reusable P0-like execution profile and generation request factory.
- Removed duplicated builders from unit and integration tests while retaining
  explicit override points for every contract area.

**Files Changed**:

- `backend/packages/txt2crs/tests/factories.py` - Added typed profile/request
  factories.
- `backend/packages/txt2crs/tests/unit/test_generation_requests.py` - Reused
  shared factories.
- `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`
  - Reused shared factories and normalized imports.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_generation_requests.py`
  - Result: PASS - 19 tests still pass after deduplication.
- Command/check: `uv run --package txt2crs ruff check tests/factories.py tests/unit/test_generation_requests.py tests/integration/test_generation_request_store.py`
  - Result: PASS - no lint findings after one automatic import sort.
- Command/check: `uv run --package txt2crs mypy tests/factories.py tests/unit/test_generation_requests.py`
  - Result: PASS - strict typing passes for the factory and unit contract tests.
- UI product-surface check: N/A - test factories have no UI.
- UI craft check: N/A - test factories have no UI.

**BQC Fixes**:

- Contract alignment: all new tests now share one complete valid request shape,
  reducing accidental fixture drift.

---

### Task T009 - Add And Document Migration 003

**Started**: 2026-07-19 12:18 IDT
**Completed**: 2026-07-19 12:20 IDT
**Duration**: 2 minutes

**Notes**:

- Added one request envelope per job with owner, schema version, canonical
  hash/JSON, timestamp, foreign-key cascade, and owner lookup index.
- Preserved released migrations 001 and 002 byte-for-byte.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/003_generation_requests.sql`
  - Added the request-envelope schema.
- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/README_migrations.md`
  - Documented migration 003 and exact recovery purpose.

**Verification**:

- Command/check: apply sorted migrations 001-003 to in-memory stdlib SQLite
  and inspect `PRAGMA table_info/index_list`
  - Result: PASS - six required columns and owner/job index verified.
- Command/check: inspect Git diff for migrations 001 and 002
  - Result: PASS - neither released migration is modified.
- UI product-surface check: N/A - engine schema has no UI.
- UI craft check: N/A - engine schema has no UI.

**BQC Fixes**:

- Contract alignment: the schema artifact matches the new durable request
  contract in the same session.
- Failure cleanup: `ON DELETE CASCADE` prevents orphan request envelopes.

---

## Blockers And Solutions

### Blocker 1: SQLite CLI Is Not Installed

**Description**: The optional `sqlite3` shell executable is absent.
**Impact**: The first migration syntax-check command could not run.
**Resolution**: Used Python 3.14's standard `sqlite3` module from the package uv
environment to apply and inspect the exact SQL resources in memory.
**Time Lost**: Less than 1 minute.

---

### Task T010 - Update Job And Resume Contracts

**Started**: 2026-07-19 12:20 IDT
**Completed**: 2026-07-19 12:21 IDT
**Duration**: 1 minute

**Notes**:

- Renamed the Python domain field from source-only `input_hash` to complete
  `request_hash`.
- Made the exact accepted `GenerationRequest` mandatory in every resume state.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/models.py` - Updated job and
  recovery contracts.

**Verification**:

- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/models.py`
  - Result: PASS - no lint findings.
- Command/check: direct runtime inspection of `JobRecord.model_fields` and
  `ResumeState.__annotations__`
  - Result: PASS - `request_hash` and `GenerationRequest` are mandatory.
- UI product-surface check: N/A - engine models have no UI.
- UI craft check: N/A - engine models have no UI.

**BQC Fixes**:

- Contract alignment: recovery cannot represent a job without its exact
  accepted request.

---

### Task T011 - Register Migration 003

**Started**: 2026-07-19 12:21 IDT
**Completed**: 2026-07-19 12:22 IDT
**Duration**: 1 minute

**Notes**:

- Replaced the two-file conditional with an explicit ordered migration map.
- Kept schema version derivation coupled to the highest packaged resource.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - Registered migrations
  001-003 by exact immutable resource name.

**Verification**:

- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/store.py`
  - Result: PASS - no lint findings.
- Command/check: create and close a temporary `SqliteJobStore`
  - Result: PASS - the reopened schema reports migration version 3.
- UI product-surface check: N/A - engine migrations have no UI.
- UI craft check: N/A - engine migrations have no UI.

**BQC Fixes**:

- Contract alignment: store migration version now matches the shipped request
  schema artifact.

---

### Task T012 - Persist Request, Job, And Reservation Atomically

**Started**: 2026-07-19 12:22 IDT
**Completed**: 2026-07-19 12:25 IDT
**Duration**: 3 minutes

**Notes**:

- Removed caller-supplied hashes from store admission and serialize/verify the
  complete request before acquiring the write transaction.
- Inserted job, request envelope, and admission reservation under one
  `BEGIN IMMEDIATE`; exact replay is row-free and conflict-safe.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - Replaced hash-only
  admission with complete request persistence and updated row projection.

**Verification**:

- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/store.py`
  - Result: PASS - no lint findings.
- Command/check: temporary SQLite create/replay/count/trigger-rollback scenario
  - Result: PASS - exact replay retained `(1, 1, 1)` rows and an aborted second
    request left all three counts unchanged.
- UI product-surface check: N/A - engine persistence has no UI.
- UI craft check: N/A - engine persistence has no UI.

**BQC Fixes**:

- Duplicate prevention: owner/key replay compares canonical request and
  reservation without consuming rows or quota.
- Failure cleanup: all three writes share one rollback boundary.
- Concurrency safety: `BEGIN IMMEDIATE` and the process lock protect
  read-check-write admission.

---

### Task T013 - Load And Verify Owner-Scoped Requests

**Started**: 2026-07-19 12:25 IDT
**Completed**: 2026-07-19 12:27 IDT
**Duration**: 2 minutes

**Notes**:

- Added owner-scoped request loading with canonical deserialization and
  three-way schema/hash verification against envelope and job state.
- Added one stable compatibility error for missing, malformed, or mismatched
  accepted state without exposing request content.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - Added
  `JobRequestCompatibilityError` and exact request loading.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/integration/test_generation_request_store.py -k 'not runnable'`
  - Result: PASS - 8 persistence, replay, rollback, ownership, restart,
    upgrade, and corrupt-state tests passed; 4 discovery tests deselected.
- Command/check: Ruff check for the store and request integration tests
  - Result: PASS - no lint findings.
- UI product-surface check: N/A - engine recovery has no UI.
- UI craft check: N/A - engine recovery has no UI.

**BQC Fixes**:

- Trust boundary: authorization is enforced before reading the request row.
- Error boundary: incompatible durable state maps to one safe stable message.
- State freshness: every recovery deserializes and revalidates current durable
  bytes and hashes.

---

### Task T014 - Implement Deterministic Runnable Discovery

**Started**: 2026-07-19 12:27 IDT
**Completed**: 2026-07-19 12:29 IDT
**Duration**: 2 minutes

**Notes**:

- Added a one-row internal worker query ordered by delivery, rendering, other
  active recovery stages, accepted state, timestamp, and job ID.
- Discovery restores and verifies the exact request and latest checkpoint
  before returning a complete resume state.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - Added bounded runnable
  discovery and complete recovery-state construction.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/integration/test_generation_request_store.py`
  - Result: PASS - all 12 request persistence and discovery tests passed.
- Command/check: Ruff check for store and discovery tests
  - Result: PASS - no lint findings.
- UI product-surface check: N/A - engine worker discovery has no UI.
- UI craft check: N/A - engine worker discovery has no UI.

**BQC Fixes**:

- State freshness: selected work is rehydrated and verified at discovery time.
- Failure completeness: incompatible non-terminal requests fail closed.
- Concurrency safety: query is bounded to one stable result under the store
  lock.

---

### Task T015 - Update The Job Service Boundary

**Started**: 2026-07-19 12:29 IDT
**Completed**: 2026-07-19 12:31 IDT
**Duration**: 2 minutes

**Notes**:

- Replaced hash-only service submission with the complete request contract.
- Owner resume now requires the exact request, and worker discovery delegates
  to the store without exposing SQL behavior.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/service.py` - Updated submit,
  resume, and next-runnable methods.

**Verification**:

- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/service.py`
  - Result: PASS - no lint findings.
- Command/check: temporary service submit/resume/next-runnable scenario
  - Result: PASS - owner recovery returned the exact request and discovery
    returned the accepted work item.
- UI product-surface check: N/A - engine service has no UI.
- UI craft check: N/A - engine service has no UI.

**BQC Fixes**:

- Contract alignment: no service acceptance path accepts a caller hash.
- Trust boundary: owner recovery obtains request state through the
  owner-enforcing store method.

---

### Task T016 - Export The Public Request Boundary

**Started**: 2026-07-19 12:31 IDT
**Completed**: 2026-07-19 12:32 IDT
**Duration**: 1 minute

**Notes**:

- Exported the seven public request/profile value contracts from
  `txt2crs.jobs`.
- Kept canonical codecs, row helpers, and SQLite details private.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - Added intentional
  public request/profile exports.

**Verification**:

- Command/check: Ruff check for `src/txt2crs/jobs/__init__.py`
  - Result: PASS - no lint findings.
- Command/check: import all seven contracts from `txt2crs.jobs`
  - Result: PASS - public imports resolve.
- UI product-surface check: N/A - package exports have no UI.
- UI craft check: N/A - package exports have no UI.

**BQC Fixes**:

- Contract alignment: downstream packages have one documented import boundary
  while persistence codecs remain encapsulated.

---

### Task T017 - Migrate Legacy Hash-Only Package Callers

**Started**: 2026-07-19 12:32 IDT
**Completed**: 2026-07-19 12:36 IDT
**Duration**: 4 minutes

**Notes**:

- Updated store, quota, service, and executor tests to submit complete request
  contracts; executor requests now preserve their exact prompt payload.
- Extended the migration contract test to migration 003 and the restart
  expectation to schema version 3.
- Inspected evaluation `input_hash` uses and retained them because they are
  `EvaluationCase` fixture-content hashes, not job-acceptance APIs.

**Files Changed**:

- `backend/packages/txt2crs/tests/factories.py` - Added exact input-payload
  overrides.
- `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py` - Used
  request contracts and schema version 3.
- `backend/packages/txt2crs/tests/integration/test_admission_quotas.py` - Used
  request contracts for every quota path.
- `backend/packages/txt2crs/tests/unit/test_job_service.py` and
  `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
  - Used and verified stored requests.

**Verification**:

- Command/check: focused pytest across store, quota, service, executor, and
  evaluation replay files
  - Result: PASS - 25 tests passed in 3.63 seconds.
- Command/check: focused Ruff check across six migrated test/factory files
  - Result: PASS - no lint findings.
- Command/check: `rg -n 'input_hash=|\.input_hash' src tests --glob '*.py'`
  - Result: PASS - remaining matches belong only to the separate evaluation
    corpus contract; no job store/service call accepts `input_hash`.
- UI product-surface check: N/A - engine tests have no UI.
- UI craft check: N/A - engine tests have no UI.

**BQC Fixes**:

- Contract alignment: every job acceptance fixture now exercises the complete
  request API and exact migration version.
- State freshness: executor restart fixtures persist the actual prompt request
  they later resume.

---

### Task T018 - Pass The Request Contract Unit Suite

**Started**: 2026-07-19 12:36 IDT
**Completed**: 2026-07-19 12:37 IDT
**Duration**: 1 minute

**Notes**:

- Re-ran every strictness, finite-limit, identity, binary, bounds, mutation,
  and tamper scenario against the final contract implementation.

**Files Changed**:

- No production changes were required; the completed contract suite is green.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q tests/unit/test_generation_requests.py`
  - Result: PASS - 19 tests passed in 0.40 seconds.
- UI product-surface check: N/A - engine contracts have no UI.
- UI craft check: N/A - engine contracts have no UI.

**BQC Fixes**:

- N/A - all planned contract boundary behaviors already pass.

---

### Task T019 - Pass The Focused Persistence And Service Gates

**Started**: 2026-07-19 12:37 IDT
**Completed**: 2026-07-19 12:38 IDT
**Duration**: 1 minute

**Notes**:

- Ran request/store, migration, admission, service, and full executor recovery
  scenarios together to catch shared-state or fixture mismatches.

**Files Changed**:

- No changes were required; the combined focused gate is green.

**Verification**:

- Command/check: focused pytest across five request/store/service/executor files
  - Result: PASS - 34 tests passed in 4.25 seconds.
- UI product-surface check: N/A - engine persistence has no UI.
- UI craft check: N/A - engine persistence has no UI.

**BQC Fixes**:

- N/A - atomicity, idempotency, owner checks, restart, migration, ordering, and
  delivery recovery all passed together.

---

### Task T020 - Pass The Complete Engine Test Suite

**Started**: 2026-07-19 12:38 IDT
**Completed**: 2026-07-19 12:39 IDT
**Duration**: 1 minute

**Notes**:

- Ran every engine unit, contract, integration, evaluation, rendering, and
  credential-free acceptance test.

**Files Changed**:

- No changes were required; no session-caused regression remained.

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS - 254 passed and 1 explicit live Codex test skipped in 6.05
    seconds (31 net new passing tests over the 223-test baseline).
- UI product-surface check: N/A - engine test gate has no UI.
- UI craft check: N/A - engine test gate has no UI.

**BQC Fixes**:

- N/A - complete regression evidence is green.

---

### Task T021 - Pass Ruff And Strict Mypy

**Started**: 2026-07-19 12:39 IDT
**Completed**: 2026-07-19 12:41 IDT
**Duration**: 2 minutes

**Notes**:

- The first formatting check identified three session-touched files; formatted
  those exact files and reran every static gate.
- Ruff lint and strict mypy were already clean.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py`,
  `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`,
  and `backend/packages/txt2crs/tests/unit/test_job_service.py` - Ruff-only
  formatting.

**Verification**:

- Command/check: `uv run --package txt2crs ruff format --check .`
  - Result: PASS - all 106 files are formatted.
- Command/check: `uv run --package txt2crs ruff check .`
  - Result: PASS - no lint findings.
- Command/check: `uv run --package txt2crs mypy`
  - Result: PASS - no issues in 106 source files.
- UI product-surface check: N/A - engine static gates have no UI.
- UI craft check: N/A - engine static gates have no UI.

**BQC Fixes**:

- Contract alignment: strict typing covers production and test request shapes.

---

### Task T022 - Build And Inspect Package Artifacts

**Started**: 2026-07-19 12:41 IDT
**Completed**: 2026-07-19 12:43 IDT
**Duration**: 2 minutes

**Notes**:

- Built both source and wheel distributions from the engine package.
- Inspected both archives for the request contract module and immutable
  migration 003.

**Files Changed**:

- `backend/dist/txt2crs-0.3.3.tar.gz` and
  `backend/dist/txt2crs-0.3.3-py3-none-any.whl` - Ignored build artifacts.

**Verification**:

- Command/check: `uv build --package txt2crs`
  - Result: PASS - source and wheel distributions built successfully.
- Command/check: `unzip -l` wheel and `tar -tzf` source distribution
  - Result: PASS - both contain `jobs/requests.py` and
    `jobs/migrations/003_generation_requests.sql`.
- UI product-surface check: N/A - package build has no UI.
- UI craft check: N/A - package build has no UI.

**BQC Fixes**:

- Contract alignment: the runtime wheel ships the code and schema resource
  required to open request-envelope databases.

---

### Blocker 2: Build Output Directory Is Workspace-Relative

**Description**: The first archive-inspection command looked under the package
directory, while uv wrote workspace package artifacts to `backend/dist`.
**Impact**: The initial `find` and `unzip` path checks failed after a successful
build.
**Resolution**: Inspected the exact paths reported by uv under `backend/dist`
and verified both archives.
**Time Lost**: Less than 1 minute.

---

### Task T023 - Complete The Encoding, Privacy, And Evidence Audit

**Started**: 2026-07-19 12:43 IDT
**Completed**: 2026-07-19 12:48 IDT
**Duration**: 5 minutes

**Notes**:

- Audited all 26 tracked/untracked phase and package files for ASCII, LF,
  whitespace, raw-input logging, hash-only acceptance, and package scope.
- The audit found `store.py` at 730 lines, so admission calculations moved to
  `quota.py` and transition rules moved to `models.py`; the store is now 635
  cohesive persistence lines without behavior changes.
- Confirmed remaining `input_hash` matches belong only to the independent
  evaluation-corpus content-address contract.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/quota.py` - Extracted read-only
  rolling quota calculation.
- `backend/packages/txt2crs/src/txt2crs/jobs/models.py` - Centralized job-state
  transition validation.
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - Delegated quota and
  transition responsibilities.
- Session `spec.md`, `tasks.md`, and this note - Finalized implementation
  status, criteria, evidence, and handoff.

**Verification**:

- Command/check: full changed-file ASCII/CR scan plus `git diff --check`
  - Result: PASS - 26 files are ASCII/LF with no whitespace errors.
- Command/check: search new production request/store code for logger, logging,
  and print calls
  - Result: PASS - no raw request logging or debug output exists.
- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS - 254 passed and 1 explicit live-provider skip after the
    cohesion refactor.
- Command/check: Ruff format/lint and strict mypy
  - Result: PASS - 106 files formatted/linted and typed with no findings.
- UI product-surface check: N/A - engine persistence session has no UI.
- UI craft check: N/A - engine persistence session has no UI.

**BQC Fixes**:

- Resource ownership: store close behavior remains explicit and tested.
- Mutation safety: canonical idempotency and transactional rollback pass.
- Trust boundary: request validation, owner reads, and safe errors pass.
- State freshness: restart recovery revalidates exact durable requests.
- Contract alignment: request/profile schema, migration, service, and wheel
  contents agree.

---

## Design Decisions

### Decision 1: Keep The Released Physical Hash Column

**Context**: Migration 001 named the job column `input_hash`, while the new
identity covers the full generation request.
**Options Considered**:

1. Rewrite or rebuild migration 001 - clearer physical name but violates the
   immutable released-migration rule.
2. Preserve the column and expose `request_hash` in Python - keeps upgrade
   compatibility while correcting public semantics.

**Chosen**: Preserve the physical column and expose `request_hash`.
**Rationale**: Migration 003 is the authoritative request envelope, and no
caller sees or depends on the legacy physical name.

### Decision 2: Use One Typed Canonical JSON Envelope

**Context**: Raw input may be text or arbitrary binary bytes.
**Options Considered**:

1. Split metadata JSON and input BLOB - efficient bytes but creates two
   canonical representations and more reconciliation paths.
2. Type-tag text/bytes and base64 binary inside canonical JSON - modest
   storage overhead with one reversible hashable envelope.

**Chosen**: Type-tagged canonical JSON.
**Rationale**: The bounded 20 MiB P0 request remains practical, text and bytes
cannot collide, and recovery validates one exact artifact.

### Decision 3: Extract Cohesive Store Rules

**Context**: Request persistence pushed the existing store beyond the
repository's preferred module range.
**Options Considered**:

1. Leave the 730-line module - least change but ignores an explicit convention.
2. Move quota arithmetic and state transitions to their domain modules - a
   behavior-preserving split with existing coverage.

**Chosen**: Move quota calculation to `quota.py` and transitions to `models.py`.
**Rationale**: `SqliteJobStore` retains transaction/query ownership while
domain rules live with their contracts.

---

## Checkpoint

- Completed: T001-T023 (100%).
- Verification: 254 tests passed, 1 explicit live-provider test skipped, Ruff
  format/lint passed, strict mypy passed, package build passed, migration 003
  ships in both archives, and ASCII/LF/privacy audits passed.
- Scope check: exact durable request and recovery objective unchanged.
- Next command: `creview`.

---

## Code Review And Repair Gate

### 2026-07-19 - Complete Review Since Base Commit

**Scope**:

- Re-read all tracked and untracked changes since
  `c56fa822e2f5f62d64ea427ae56739fd5c17ce4d`.
- Reviewed 28 final files against the session spec, project conventions,
  behavioral checklist, and security/privacy checklist.
- Added regression tests before each observable repair and recorded the full
  finding/evidence ledger in `code-review.md`.

**Resolved findings**:

- Metadata now permits only detached, finite JSON values, has an immutable
  profile-owned byte ceiling, and cannot be silently normalized or leak
  serialization context.
- Request creation validates before hashing and rejects oversized raw input
  before base64 work; persistence serializes one detached snapshot so nested
  mutation cannot race the canonical hash.
- P0 audience, prior-knowledge, learning-goal, and request-version constraints
  now match the authoritative implementation plan.
- Owner/idempotency identifiers validate before any write, and new admission
  reservations must cover the immutable profile's input/output token ceilings.
- Owner resume and internal runnable discovery now rehydrate job, request, and
  checkpoint under one process-local lock scope.
- Request-envelope SQL/integrity helpers moved to `jobs/request_store.py` to
  keep the primary store cohesive after the safety repairs.
- Sensitive compatibility translations contain neither exception cause nor
  exception context; formatted traceback tests preserve learner privacy.

**Verification**:

- Command/check: targeted red tests for metadata, safe errors, normalization,
  preference limits, contract version, reservation coverage, submission
  identity, and atomic resume
  - Result: EXPECTED FAIL before each production repair, then PASS afterward.
- Command/check: run concurrent exact replay ten consecutive times
  - Result: PASS - all ten runs committed one job, one request, and one
    admission row.
- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS - 274 passed and one explicit live-provider acceptance test
    skipped behind `TXT2CRS_RUN_LIVE_CODEX=1`.
- Command/check: Ruff format/lint and strict mypy
  - Result: PASS - all 107 engine files formatted/linted and typed.
- Command/check: `uv build --package txt2crs` plus wheel/sdist archive listings
  - Result: PASS - request contracts, request-store helper, and migration 003
    ship in both archives.
- Command/check: final 28-file ASCII/CR/secret/log scan and
  `git diff --check`
  - Result: PASS - all files are ASCII/LF with no whitespace, credential,
    raw-input logging, or debug artifacts.

**Review checkpoint**:

- Findings: 0 critical, 4 high, 4 medium, 2 low; all resolved.
- Remaining blockers: 0.
- Next command: `validate`.
