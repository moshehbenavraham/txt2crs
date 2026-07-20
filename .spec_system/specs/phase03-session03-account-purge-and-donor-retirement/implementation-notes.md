# Implementation Notes

**Session ID**: `phase03-session03-account-purge-and-donor-retirement`
**Package**: backend
**Started**: 2026-07-20 02:01
**Last Updated**: 2026-07-20 02:56

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 24 / 24 |
| Estimated Remaining | review and validation |
| Blockers | 0 |

---

## Task Log

### 2026-07-20 - Session Start

**Environment verified**:
- [x] Apex project/session state and backend package prerequisites confirmed
- [x] uv, jq, Git, Alembic, PostgreSQL 18, and repository tooling available
- [x] Isolated PostgreSQL is running on host port 55433
- [x] Alembic is current at `fe56fa70289e`

---

### Task T001 - Verify erasure, migration, and replacement-job baseline

**Started**: 2026-07-20 02:01
**Completed**: 2026-07-20 02:03
**Duration**: 2 minutes

**Notes**:
- Confirmed both Phase 03 replacement sessions are completed in deterministic
  project state and the public facade already cancels and joins matching owner
  executors before owner lifecycle purge.
- Confirmed the isolated database is healthy and current without accessing the
  unrelated service on host port 5447.

**Files Changed**:
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded baseline evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T001 complete

**Verification**:
- Command/check: `bash .spec_system/scripts/analyze-project.sh --json`
  - Result: PASS - active session resolved with 13 completed prerequisites.
- Command/check: `cd backend && ... uv run alembic current && uv run pytest tests/api/routes/test_users.py tests/migrations/test_migration_safety.py -q`
  - Result: PASS - head `fe56fa70289e`; 34 tests passed.
- Command/check: `cd backend/packages/txt2crs && uv run --package txt2crs pytest tests/unit/test_application_facade.py -q`
  - Result: PASS - 12 facade tests passed, including owner barrier coverage.
- UI product-surface check: N/A - backend session baseline only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Trust boundary/concurrency: verified existing facade barrier before planning
  any shell behavior; no duplicate worker-side purge API will be introduced.

---

## Checkpoint

**Next task**: T003 - write failing self-delete purge-order and retry tests.

---

### Task T002 - Inventory the donor domain and derivative contract

**Started**: 2026-07-20 02:03
**Completed**: 2026-07-20 02:05
**Duration**: 2 minutes

**Notes**:
- Located the donor HTTP router, six SQLModel contracts/aliases, user
  relationship, CRUD helper, three error codes/messages, exception-handler
  fallback, test cleanup, route/model suites, utility, five current
  documentation surfaces, four generated contract files, and four admin MCP
  exposures.
- Classified historical Alembic revisions as immutable and current learner
  `/items` sources as the explicit Phase 04 dependency. Engine assessment
  items and generic collection variables are unrelated and stay.

**Files Changed**:
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded the bounded inventory
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T002 complete

**Verification**:
- Command/check: targeted `rg` over `backend/app`, `backend/tests`, `docs`,
  `frontend/openapi.json`, and `frontend/src/client`
  - Result: PASS - every donor-owned source and derivative reference is
    assigned to T010/T014-T019; `exception_handlers.py` was added to the
    implementation inventory.
- Command/check: `rg` comparison against `backend/packages/txt2crs`
  assessment models and frontend non-generated sources
  - Result: PASS - unrelated assessment vocabulary excluded; deferred learner
    imports recorded without broadening Phase 03.
- UI product-surface check: N/A - inventory only; learner UI is unchanged.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Contract alignment: expanded the removal inventory to include the central
  unknown-resource exception mapper, avoiding a stale Item fallback.

---

### Task T003 - Write failing self-delete purge and retry tests

**Started**: 2026-07-20 02:05
**Completed**: 2026-07-20 02:07
**Duration**: 2 minutes

**Notes**:
- Added a public-boundary fake and dependency override with deterministic
  cleanup, plus exact purge/delete/commit ordering instrumentation.
- Added safe-failure identity retention, private-message rejection, retry, and
  superuser self-delete no-purge coverage.

**Files Changed**:
- `backend/tests/api/routes/test_users.py` - added self-delete purge contract tests and focused helpers
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded red-test evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T003 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/api/routes/test_users.py -q`
  - Result: PASS (tests-first gate) - suite reached 30 passing and four
    expected failures; self-delete showed no facade purge and deleted the user
    instead of returning the specified 503.
- UI product-surface check: N/A - API tests only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Mutation safety/failure completeness: test requires idempotent retry and
  proves authorization completes before any engine mutation.

---

### Task T004 - Write failing superuser target purge and retry tests

**Started**: 2026-07-20 02:07
**Completed**: 2026-07-20 02:08
**Duration**: 1 minute

**Notes**:
- Required the target UUID, not acting administrator UUID, at the package
  boundary and fixed the observable order as purge, SQLModel delete, commit.
- Protected missing-target and administrator self-delete paths from invoking
  owner purge, and added failure retention plus repeated-purge retry.

**Files Changed**:
- `backend/tests/api/routes/test_users.py` - added admin deletion ordering, authorization, failure, and retry tests
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded red-test evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T004 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/api/routes/test_users.py -q`
  - Result: PASS (tests-first gate) - admin cases fail specifically because the
    current route never calls the injected facade and deletes the identity
    after the configured purge failure.
- UI product-surface check: N/A - API tests only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Trust boundary: target existence and self-authorization must precede the
  erasure mutation; focused assertions now prevent regression.

---

### Task T005 - Write failing real-facade cross-store acceptance

**Started**: 2026-07-20 02:08
**Completed**: 2026-07-20 02:10
**Duration**: 2 minutes

**Notes**:
- Added a real deterministic facade behind the HTTP dependency, with one
  completed artifact-bearing job and one blocked active executor for the same
  PostgreSQL owner.
- Added real artifact-store purge failure, identity/job retention, safe 503,
  and restored retry coverage.

**Files Changed**:
- `backend/tests/acceptance/test_account_purge.py` - added real facade, active barrier, artifact erasure, failure, and retry acceptance
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded red-test evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T005 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/acceptance/test_account_purge.py -q`
  - Result: PASS (tests-first gate) - both tests fail at the intended boundary:
    HTTP deletion neither cancels the active facade executor nor retains the
    identity after real artifact purge failure.
- UI product-surface check: N/A - backend acceptance only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Resource cleanup/concurrency: finite events, joins, dependency cleanup, and
  application close protect every success/failure assertion from dangling
  threads or facade resources.

---

## Checkpoint - Tests-First Erasure Boundary

- Baseline and five planning/test tasks are complete.
- New red tests prove the current deletion routes violate ordered purge,
  failure retention, active-executor waiting, and cross-store erasure.
- Scope remains Phase 03 backend/migration/generated artifacts; learner UI is
  untouched.

**Next task**: T006 - add failing safe error and structured-log contracts.

---

### Task T006 - Write failing purge error and log allowlist tests

**Started**: 2026-07-20 02:10
**Completed**: 2026-07-20 02:12
**Duration**: 2 minutes

**Notes**:
- Required `USER_2007` to map owner purge failure to 503 with one fixed detail,
  no cause/context, and no private error content.
- Required removal of the Item error namespace/content constants and bounded
  failure logs containing only pseudonymous user ID and a finite reason code.

**Files Changed**:
- `backend/tests/core/test_txt2crs_errors.py` - added registered purge and retired-error contract tests
- `backend/tests/api/routes/test_users.py` - added failure-event allowlist/privacy assertions
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded red-test evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T006 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/core/test_txt2crs_errors.py tests/api/routes/test_users.py -q`
  - Result: PASS (tests-first gate) - 32 tests pass and the new contracts fail
    because `USER_PURGE_FAILED` is unregistered, Item codes remain, and routes
    emit no purge event.
- UI product-surface check: N/A - error/log contract only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Error information boundary: hostile email/path/provider strings are now
  explicit negative assertions for exception response, chaining, and logs.

**Next task**: T007 - write destructive migration round-trip tests.

---

### Task T007 - Write failing destructive migration round-trip tests

**Started**: 2026-07-20 02:12
**Completed**: 2026-07-20 02:14
**Duration**: 2 minutes

**Notes**:
- Split current-head absence, complete pre-retirement schema, historical
  downgrade, and row-count assertions so destructive semantics are explicit.
- Added fresh, populated existing, empty schema downgrade, re-upgrade, and
  static revision-shape coverage against disposable PostgreSQL databases.

**Files Changed**:
- `backend/tests/migrations/test_migration_safety.py` - added retirement migration and runtime schema/row tests
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded red-test evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T007 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/migrations/test_migration_safety.py -q`
  - Result: PASS (tests-first gate) - four historical tests pass; four new
    tests fail because revision `a7d9c2e4f601` does not exist and current head
    still contains `item`.
- UI product-surface check: N/A - PostgreSQL migration tests only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- State freshness/contract alignment: every runtime case creates a unique
  database and inspects actual PostgreSQL schema rather than trusting metadata
  or a prior test's state.

**Next task**: T008 - write failing admin MCP donor-absence contracts.

---

### Task T008 - Write failing admin MCP donor-absence contracts

**Started**: 2026-07-20 02:14
**Completed**: 2026-07-20 02:16
**Duration**: 2 minutes

**Notes**:
- Defined the exact nine retained read-only user, validation, and schema tools
  through FastMCP's public tool-list API.
- Required removal of donor tool registration, model import, per-user count,
  database count, and any research MCP crossing.

**Files Changed**:
- `backend/tests/mcp/test_admin_mcp_contract.py` - added tool, payload, import, and boundary contracts
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded red-test evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T008 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/mcp/test_admin_mcp_contract.py -q`
  - Result: PASS (tests-first gate) - all three tests fail on the current
    `list_items`/`get_item` registrations, Item import, and item counts.
- UI product-surface check: N/A - local admin MCP only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Contract alignment/trust boundary: tests preserve the exact local read-only
  tool set and explicitly reject research-boundary imports.

**Next task**: T009 - write donor-absence source and generated-contract tests.

---

### Task T009 - Write failing donor source and generated-contract tests

**Started**: 2026-07-20 02:16
**Completed**: 2026-07-20 02:18
**Duration**: 2 minutes

**Notes**:
- Added static runtime/model/router/CRUD/error/file/document checks restricted
  to the donor domain and current operational docs.
- Added OpenAPI and all-generated-file checks for donor paths, service,
  operation, request/response, and schema identifiers.

**Files Changed**:
- `backend/tests/architecture/test_donor_retirement.py` - added complete current-source and docs retirement contract
- `backend/tests/scripts/test_generate_client_contract.py` - added derivative OpenAPI/client absence contract
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded red-test evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T009 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/architecture/test_donor_retirement.py tests/scripts/test_generate_client_contract.py -q`
  - Result: PASS (tests-first gate) - eight existing contract tests pass; four
    new tests fail on present donor files/models/docs/OpenAPI.
- UI product-surface check: N/A - generated artifacts and static source only.
- UI craft check: N/A - no learner source changed.

**BQC Fixes**:
- Contract alignment: derivative checks read every generated file, preventing
  a stale service/type export after OpenAPI source removal.

---

## Checkpoint - Complete Red Test Layer

- All seven tests-first tasks are complete and fail at their intended current
  behavior.
- PostgreSQL migration cases are isolated and cleaned up; HTTP/facade thread
  cases use finite joins and cleanup.
- Next implementation begins with the outward error contract before route
  mutation code.

**Next task**: T010 - implement registered purge failure and remove donor
error/content constants.

---

### Task T010 - Register purge failure and remove donor error constants

**Started**: 2026-07-20 02:18
**Completed**: 2026-07-20 02:21
**Duration**: 3 minutes

**Notes**:
- Added `USER_2007` with fixed retry detail and 503 mapping; owner purge now
  translates before the generic engine-operation branch.
- Removed Item error codes/messages/content enum, Item legacy HTTP mapping,
  and Item-specific not-found dispatch while retaining user behavior.

**Files Changed**:
- `backend/app/core/constants.py` - registered purge error and removed donor constants
- `backend/app/core/exceptions.py` - reduced current not-found helper to user-owned resources
- `backend/app/core/exception_handlers.py` - removed legacy Item HTTP mapping
- `backend/app/core/txt2crs_errors.py` - safely translated public `OwnerPurgeError`
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded implementation evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T010 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/core/test_txt2crs_errors.py -q`
  - Result: PASS - 5 tests passed, including private-content and no-chain
    assertions.
- Command/check: `cd backend && uv run ruff check app/core/constants.py app/core/exceptions.py app/core/exception_handlers.py app/core/txt2crs_errors.py`
  - Result: PASS - all checks passed.
- UI product-surface check: N/A - error boundary only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Failure completeness/error boundary: owner purge is a caller-visible
  retryable 503 and never copies package exception text.

**Next task**: T011 - implement the shared public-facade purge helper and safe
events.

---

### Task T011 - Implement public-facade purge helper and safe events

**Started**: 2026-07-20 02:21
**Completed**: 2026-07-20 02:23
**Duration**: 2 minutes

**Notes**:
- Added one helper that calls only `Txt2CrsApplication.purge_owner` and emits
  started/completed/failed events with pseudonymous UUID and finite reason.
- Translates only public owner/readiness failures, then raises outside the
  `except` block so private package context is not attached.

**Files Changed**:
- `backend/app/api/routes/users.py` - added the shared engine-first erasure helper
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded helper evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T011 complete

**Verification**:
- Command/check: `cd backend && uv run ruff check app/api/routes/users.py --fix && uv run ruff format app/api/routes/users.py`
  - Result: PASS - imports normalized and file formatted.
- Command/check: `cd backend && ... uv run pytest tests/core/test_txt2crs_errors.py -q`
  - Result: PASS - 5 safe translation tests passed.
- UI product-surface check: N/A - private route helper only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Error boundary/resource concurrency: helper delegates the complete
  cancellation/join/artifact/store lifecycle to the locked public facade and
  does not catch process-control exceptions.

**Next task**: T012 - call the helper before self-service PostgreSQL deletion.

---

### Task T012 - Integrate engine-first self-service deletion

**Started**: 2026-07-20 02:23
**Completed**: 2026-07-20 02:26
**Duration**: 3 minutes

**Notes**:
- Injected the lifespan public application and called purge only after
  superuser self-delete authorization but before SQLModel mutation.
- Added post-purge PostgreSQL commit-failure/retry proof and updated the
  existing success test to provide an explicit available facade.

**Files Changed**:
- `backend/app/api/routes/users.py` - added application dependency and ordered self purge
- `backend/tests/api/routes/test_users.py` - added partial-progress retry test and explicit success dependency
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded route evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T012 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/api/routes/test_users.py -q -k 'delete_user_me'`
  - Result: PASS - 5 self-delete tests passed, including purge failure, DB
    failure after purge, retry, ordering, and superuser denial.
- Command/check: Ruff check/fix and format over route and test files
  - Result: PASS - one import ordering fix applied; files formatted.
- UI product-surface check: N/A - authenticated API mutation only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Mutation safety/failure completeness: a database failure after successful
  purge returns failure, retains identity through rollback, and repeats the
  idempotent purge on retry.

**Next task**: T013 - integrate engine-first superuser target deletion and
remove direct donor-row deletion.

---

### Task T013 - Integrate engine-first superuser target deletion

**Started**: 2026-07-20 02:26
**Completed**: 2026-07-20 02:28
**Duration**: 2 minutes

**Notes**:
- Added the public application dependency and target purge after existence and
  administrator self-delete checks but before SQLModel deletion.
- Removed the direct Item delete query/import and documented complete
  engine-owned course-state purge.

**Files Changed**:
- `backend/app/api/routes/users.py` - ordered admin purge and removed donor delete
- `backend/tests/api/routes/test_users.py` - supplied explicit facade to existing admin success test
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded admin route evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T013 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/api/routes/test_users.py -q`
  - Result: PASS - all 35 user route tests passed.
- Command/check: Ruff check/fix and format over route and tests
  - Result: PASS - all checks passed; both files formatted.
- UI product-surface check: N/A - administrator API mutation only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Trust boundary/mutation safety: missing, unauthorized, and self targets
  cannot trigger engine purge; exact target UUID is asserted before DB commit.

---

## Checkpoint - Ordered Erasure Implemented

- Both deletion routes now use one public facade helper before PostgreSQL
  mutation.
- Self/admin unit routes, retry behavior, safe translation, and logging
  contracts are green.
- Next risky operation is the destructive Alembic revision; runtime tests are
  already red and isolated.

**Next task**: T014 - add the donor table retirement migration.

---

### Task T014 - Add donor table retirement migration

**Started**: 2026-07-20 02:28
**Completed**: 2026-07-20 02:30
**Duration**: 2 minutes

**Notes**:
- Added head `a7d9c2e4f601` with one-table destructive upgrade and a complete
  schema-only downgrade including UUIDs, bounds, JSON/text/timezone types,
  named cascade foreign key, primary key, and owner index.
- Documented irreversible donor-row loss in module and downgrade comments.

**Files Changed**:
- `backend/app/alembic/versions/a7d9c2e4f601_drop_donor_item_table.py` - added upgrade/downgrade
- `backend/tests/migrations/test_migration_safety.py` - formatted completed runtime/static proof
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded migration evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T014 complete

**Verification**:
- Command/check: `cd backend && ... uv run pytest tests/migrations/test_migration_safety.py -q`
  - Result: PASS - 8 tests passed across fresh, populated, downgrade,
    re-upgrade, and historical migration paths.
- Command/check: Ruff check/fix and format over migration and safety tests
  - Result: PASS - all checks passed; test file formatted.
- UI product-surface check: N/A - schema migration only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Contract alignment/state freshness: live disposable PostgreSQL inspection
  proves both schema shapes and zero-row downgrade semantics.

**Next task**: T015 - remove current Item metadata, CRUD, router, and module.

---

### Task T015 - Remove current Item metadata, CRUD, and router

**Started**: 2026-07-20 02:30
**Completed**: 2026-07-20 02:33
**Duration**: 3 minutes

**Notes**:
- Removed seven donor model/type contracts, `User.items`, CRUD helper/import,
  HTTP router registration/module, and stale dependency documentation.
- Historical migrations remain unchanged; admin MCP references remain
  intentionally isolated for T017.

**Files Changed**:
- `backend/app/models.py` - removed donor metadata and relationship
- `backend/app/crud.py` - removed donor helper and documentation
- `backend/app/api/main.py` - removed donor router
- `backend/app/api/deps.py` - replaced donor usage example
- `backend/app/api/routes/items.py` - deleted donor HTTP module
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded removal evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T015 complete

**Verification**:
- Command/check: isolated-env Python import inspection of `app.models` and
  `app.main.app.routes`
  - Result: PASS - all seven donor symbols and every `/api/v1/items` route are
    absent.
- Command/check: Ruff check and format over changed application files
  - Result: PASS - all checks passed; CRUD file formatted.
- UI product-surface check: N/A - backend source removal only.
- UI craft check: N/A - learner route is Phase 04 and unchanged.

**BQC Fixes**:
- Contract alignment: SQLModel metadata now matches the item-free Alembic
  head; no shell router can expose a table that no longer exists.

**Next task**: T016 - remove donor tests/utilities and update shared fixtures.

---

### Task T016 - Remove donor tests/utilities and update shared fixtures

**Started**: 2026-07-20 02:33
**Completed**: 2026-07-20 02:34
**Duration**: 1 minute

**Notes**:
- Deleted donor route/model suites and their item factory, removed Item from
  the session fixture cleanup, and converted the central not-found contract
  proof to the surviving user resource.
- Applied head `a7d9c2e4f601` to the isolated Phase 03 PostgreSQL database
  before running the shared-fixture-backed regression slice.

**Files Changed**:
- `backend/tests/api/routes/test_items.py` - deleted obsolete donor route suite
- `backend/tests/models/test_item_models.py` - deleted obsolete donor model suite
- `backend/tests/utils/item.py` - deleted obsolete donor factory
- `backend/tests/conftest.py` - removed donor cleanup dependency
- `backend/tests/api/routes/test_error_contracts.py` - retained semantic 404 proof through users
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded removal evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T016 complete

**Verification**:
- Command/check: isolated `uv run alembic upgrade head && uv run alembic current`
  - Result: PASS - isolated database advanced from `fe56fa70289e` to
    `a7d9c2e4f601 (head)`.
- Command/check: focused user/error/translation/migration pytest slice
  - Result: PASS - 54 tests passed.
- UI product-surface check: N/A - obsolete backend tests only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Contract alignment: the surviving not-found test now exercises a real
  current resource instead of preserving a donor endpoint solely for coverage.

**Next task**: T017 - retire donor capabilities from the admin MCP.

---

### Task T017 - Retire donor capabilities from the admin MCP

**Started**: 2026-07-20 02:34
**Completed**: 2026-07-20 02:35
**Duration**: 1 minute

**Notes**:
- Removed donor imports, UUID parsing, list/read tools, user item counts, and
  database item counts from the local read-only administrative MCP.
- Renamed the server identity/example to `txt2crs-admin` and kept its nine
  user, validation, schema, and project tools disjoint from engine research.

**Files Changed**:
- `backend/app/mcp/server.py` - removed donor tools/data and updated server identity
- `backend/app/mcp/__init__.py` - replaced donor capability description
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded MCP evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T017 complete

**Verification**:
- Command/check: isolated `uv run pytest tests/mcp/test_admin_mcp_contract.py -q`
  - Result: PASS - 3 contract tests passed.
- Command/check: Ruff lint and format check over admin MCP and tests
  - Result: PASS - all checks passed; all files formatted.
- UI product-surface check: N/A - local developer MCP only.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Boundary integrity: exact tool-set and source-level assertions prove the
  admin MCP neither retains donor capabilities nor imports research MCP code.

**Next task**: T018 - replace current donor documentation with job/erasure truth.

---

### Task T018 - Replace donor documentation with job/erasure truth

**Started**: 2026-07-20 02:35
**Completed**: 2026-07-20 02:39
**Duration**: 4 minutes

**Notes**:
- Deleted the obsolete scaffold feature guide and updated backend, API,
  architecture, test, ADR, and dashboard-contract claims to the current job
  API and engine-first account-erasure behavior.
- Rebuilt the database schema guide around its actual two-store boundary:
  PostgreSQL users plus package-owned tenant SQLite, including retry semantics
  and the schema-only truth of the destructive migration downgrade.

**Files Changed**:
- `docs/items-feature.md` - deleted obsolete donor guide
- `backend/README_backend.md` - documented job routes and ordered erasure
- `backend/tests/README_backend_tests.md` - documented current coverage
- `docs/api/README_api.md` - removed donor endpoints and documented purge failures
- `docs/database/SCHEMA.md` - replaced stale schema with current two-store truth
- `docs/ARCHITECTURE.md` - updated topology and completed owner erasure
- `docs/adr/0004-rfc9457-error-format.md` - updated active error namespaces
- `docs/dashboard-design.md` - retired generated donor contract claims
- `backend/tests/architecture/test_donor_retirement.py` - corrected source-fragment assertion and formatted
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded documentation evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T018 complete

**Verification**:
- Command/check: isolated architecture retirement suite
  - Result: PASS - 3 tests passed.
- Command/check: targeted retired-contract search across current documentation
  - Result: PASS - no donor route/schema/generated-type claims remain.
- Command/check: `git diff --check` over changed documentation
  - Result: PASS - no whitespace errors.
- UI product-surface check: N/A - documentation only; Phase 04 owns learner UI.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:
- Contract alignment: current docs no longer describe deleted routes/tables,
  and downgrade language cannot be mistaken for deleted-row recovery.

**Next task**: T019 - regenerate the OpenAPI and TypeScript client.

---

### Task T019 - Regenerate OpenAPI and the TypeScript client

**Started**: 2026-07-20 02:39
**Completed**: 2026-07-20 02:41
**Duration**: 2 minutes

**Notes**:
- Ran only the repository generation script against the isolated head schema;
  OpenAPI and Hey API outputs now derive from the donor-free FastAPI routes.
- Biome formatting remained owned by the generation workflow. The existing
  learner source dependency is intentionally left for Phase 04 rather than
  hidden behind a handwritten generated-client shim.

**Files Changed**:
- `frontend/openapi.json` - regenerated donor-free API schema
- `frontend/src/client/` - regenerated TypeScript operations and schemas
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded generation evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T019 complete

**Verification**:
- Command/check: isolated `bash scripts/generate-client.sh`
  - Result: PASS - OpenAPI export, Hey API generation, and Biome write completed.
- Command/check: generated-client contract suite
  - Result: PASS - 9 tests passed.
- Command/check: generated-source retired-identifier search
  - Result: PASS - no donor path, service, operation, request, response, or
    schema remains.
- UI product-surface check: dependency intentionally deferred to Phase 04.
- UI craft check: N/A - generated contracts only.

**BQC Fixes**:
- Derivative integrity: the contract was regenerated from live application
  source; no manual generated edit or compatibility shim was introduced.

**Next task**: T020 - run the complete focused Phase 03 gate.

---

### Task T020 - Run the focused Phase 03 gate

**Started**: 2026-07-20 02:41
**Completed**: 2026-07-20 02:42
**Duration**: 1 minute

**Notes**:
- Exercised every session-owned boundary together against the isolated
  PostgreSQL head, including the real facade's active-executor barrier and
  artifact-failure retry acceptance paths.

**Files Changed**:
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded focused gate
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T020 complete

**Verification**:
- Command/check: focused users, real purge acceptance, migrations, translation,
  admin MCP, architecture, and generated-contract pytest selection
  - Result: PASS - 65 tests passed.
- UI product-surface check: N/A - backend/contract phase gate.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Integrated confidence: route-level fakes and real package behavior agree on
  ordering, retryability, owner isolation, and donor absence.

**Next task**: T021 - exercise the migration through live CLI transitions.

---

### Task T021 - Exercise live migration transitions

**Started**: 2026-07-20 02:42
**Completed**: 2026-07-20 02:45
**Duration**: 3 minutes

**Notes**:
- Used only isolated PostgreSQL port 55433. Downgrade recreated all nine
  historical columns, primary key, cascade owner foreign key, and owner index
  with zero rows.
- Added a disposable owner and donor row, upgraded to prove destructive table
  removal while preserving the user, removed the probe user, then completed a
  second downgrade/re-upgrade cycle to prove schema-only empty restoration.

**Files Changed**:
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded live schema evidence
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T021 complete

**Verification**:
- Command/check: Alembic downgrade to `fe56fa70289e` plus information-schema,
  index, and constraint inspection
  - Result: PASS - exact prior shape restored with row count zero.
- Command/check: insert one disposable donor row then `alembic upgrade head`
  - Result: PASS - donor table absent, probe user retained until explicit cleanup.
- Command/check: `alembic downgrade -1`, empty-row query, head re-upgrade,
  `alembic current`, and final table query
  - Result: PASS - empty downgrade; final `a7d9c2e4f601 (head)` with no donor
    relation and one current application table.
- UI product-surface check: N/A - isolated database verification.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Migration truth: live populated destruction and empty downgrade evidence
  match the revision documentation; no claim of row recovery remains.

**Next task**: T022 - run complete engine/backend quality gates.

---

### Task T022 - Run complete engine/backend quality gates

**Started**: 2026-07-20 02:45
**Completed**: 2026-07-20 02:48
**Duration**: 3 minutes

**Notes**:
- Ran package-owned suites and static tools from their correct roots in
  parallel. The first backend format check identified two new test files;
  Ruff formatted them and the full backend quality chain then passed.

**Files Changed**:
- `backend/tests/acceptance/test_account_purge.py` - Ruff formatting only
- `backend/tests/scripts/test_generate_client_contract.py` - Ruff formatting only
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded full gates
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T022 complete

**Verification**:
- Command/check: complete backend suite against isolated PostgreSQL
  - Result: PASS - 468 tests passed.
- Command/check: complete engine suite
  - Result: PASS - 470 tests passed, 1 live-subscription test skipped by its
    explicit opt-in contract.
- Command/check: engine Ruff check/format and mypy
  - Result: PASS - 138 files formatted; strict types clean.
- Command/check: backend Ruff check/format, strict mypy, and ty
  - Result: PASS - 103 files formatted; 47 typed source files clean; ty clean.
- UI product-surface check: N/A - backend/engine quality gates.
- UI craft check: N/A - no UI changed.

**BQC Fixes**:
- Quality ownership: every suite and formatter used its package-local
  configuration, avoiding the workspace exclusion mismatch.

**Next task**: T023 - prove deterministic generation and record Phase 04 dependency.

---

### Task T023 - Prove deterministic generation and record Phase 04 dependency

**Started**: 2026-07-20 02:48
**Completed**: 2026-07-20 02:51
**Duration**: 3 minutes

**Notes**:
- Regenerated the complete OpenAPI/client output twice and obtained the same
  aggregate SHA-256:
  `da9115c8b5d1d878f20c5e90273af71b33464dd29f6160f7724129016fc6b16f`.
- Generated artifacts pass their regression and Biome gates.
- The expected Phase 04 dependency is explicit: current learner sources
  `Dashboard/LibraryPreview.tsx`, `Dashboard/queries.ts`, six files under
  `components/Items/`, `hooks/useSaveToItems.ts`, and
  `routes/_layout/items.tsx` still import retired `ItemPublic`, `ItemCreate`,
  or `ItemsService`. TypeScript reports 13 `TS2305` errors. Phase 04 must
  remove/replace those product sources; Phase 03 intentionally adds no stale
  generated shim.

**Files Changed**:
- `frontend/openapi.json` and `frontend/src/client/` - deterministically regenerated
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - recorded hash and exact dependency
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - marked T023/dependency complete

**Verification**:
- Command/check: two isolated generation runs plus aggregate SHA-256 comparison
  - Result: PASS - byte-stable matching hashes.
- Command/check: generated-contract pytest suite
  - Result: PASS - 9 tests passed.
- Command/check: read-only Biome check over OpenAPI and generated client
  - Result: PASS - 18 files checked with no fixes.
- Command/check: `npm run typecheck`
  - Result: EXPECTED DEPENDENCY - 13 missing-export errors only in the
    explicitly deferred learner sources listed above.
- UI product-surface check: deferred source dependency is bounded and handed
  directly to Phase 04.
- UI craft check: N/A - no product UI changed.

**BQC Fixes**:
- Derivative integrity/sequencing: repeatable generation is proven without
  falsifying the contract to keep obsolete learner code compiling.

**Next task**: T024 - run final repository hygiene and boundary audits.

---

### Task T024 - Run final repository hygiene and boundary audits

**Started**: 2026-07-20 02:51
**Completed**: 2026-07-20 02:56
**Duration**: 5 minutes

**Notes**:
- Ran every repository hook with only `typescript-frontend` skipped for the
  explicitly documented Phase 04 dependency. Client generation used isolated
  PostgreSQL port 55433 and remained stable.
- Enumerated all seven intentional untracked files, re-read both mutation
  paths and their failure/retry proofs, and searched current source/generated
  artifacts for donor and cross-MCP references.
- Normalized the touched dashboard design guide's pre-existing Unicode
  punctuation and box drawing to repository ASCII conventions, then verified
  all 36 changed/untracked files use ASCII and LF.

**Files Changed**:
- `docs/dashboard-design.md` - mechanically normalized touched documentation to ASCII
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md` - completed audit record
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md` - completed task/checklist

**Verification**:
- Command/check: `SKIP=typescript-frontend ... pre-commit run --all-files`
  - Result: PASS - every executed hook passed, including Ruff, mypy, ty,
    Biome, generation, typos, YAML/TOML, whitespace, and zizmor.
- Command/check: explicit changed/untracked ASCII, CRLF, and `git diff --check`
  audit
  - Result: PASS - 36 files ASCII/LF; no whitespace failures.
- Command/check: source inspection/search for purge order, retry/privacy
  assertions, generated donor symbols, and admin/research MCP cross-wiring
  - Result: PASS - purge precedes both SQL deletes; only finite log fields and
    context-free errors remain; generated/current application source is donor
    free; MCP boundaries remain disjoint.
- Command/check: final real-purge, architecture, and admin-MCP regression slice
  - Result: PASS - 8 tests passed.
- UI product-surface check: the only excluded frontend gate is bounded to the
  recorded Phase 04 replacement sources.
- UI craft check: N/A - no learner UI implementation in this session.

**BQC Fixes**:
- Delivery hygiene: no untracked implementation file, private error detail,
  stale generated contract, migration ambiguity, or encoding exception is
  hidden from review.

---

## Session Implementation Complete

- 24 / 24 tasks completed.
- Backend and engine suites and all applicable static gates pass.
- The isolated database is at `a7d9c2e4f601 (head)`.
- The one sequential dependency is explicit and intentionally belongs to
  Phase 04: learner source still imports removed generated donor symbols.

**Next workflow step**: `creview`.
