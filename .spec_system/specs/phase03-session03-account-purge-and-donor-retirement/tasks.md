# Task Checklist

**Session ID**: `phase03-session03-account-purge-and-donor-retirement`
**Total Tasks**: 24
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-20

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0303]`
session ref; `TNNN` task ID.

---

## Setup And Baseline (2 tasks)

- [x] T001 [S0303] Verify Sessions 01/02 replacement-job acceptance, the
  public facade owner barrier, isolated PostgreSQL head, and focused
  user-deletion/migration baselines
  (`backend/app/api/routes/users.py`,
  `backend/packages/txt2crs/src/txt2crs/application/facade.py`,
  `backend/tests/migrations/test_migration_safety.py`).
- [x] T002 [S0303] Inventory every donor route/model/relationship/CRUD/error,
  backend test/fixture, documentation claim, generated operation/schema, and
  admin MCP tool/count while distinguishing unrelated assessment items and
  deferred learner UI
  (`backend/app/`, `backend/tests/`, `docs/`, `frontend/src/client/`).

---

## Tests First (7 tasks)

- [x] T003 [S0303] Write failing self-delete route tests for exact target UUID,
  authorization-before-purge, purge-before-session-delete/commit, successful
  response, safe purge failure with retained user, and idempotent retry
  (`backend/tests/api/routes/test_users.py`).
- [x] T004 [S0303] [P] Write failing superuser-delete route tests for target
  existence/self-delete checks before purge, exact target UUID, ordered purge
  and PostgreSQL delete, retained user on purge failure, and retry after prior
  engine success (`backend/tests/api/routes/test_users.py`).
- [x] T005 [S0303] Write failing real-facade acceptance for cross-store owner
  erasure, active executor cancellation/join before identity commit, no
  artifact recreation, purge-failure retention, and successful retry
  (`backend/tests/acceptance/test_account_purge.py`).
- [x] T006 [S0303] [P] Write failing error/log tests for one registered
  retryable purge code, fixed safe detail, no exception chaining/private
  content, bounded structured event fields, and complete Item error removal
  (`backend/tests/api/routes/test_error_contracts.py`,
  `backend/tests/core/`).
- [x] T007 [S0303] Write failing migration tests for fresh head upgrade,
  populated `fe56fa70289e` upgrade, intentional donor-row loss, exact empty
  one-revision downgrade schema, and re-upgrade removal
  (`backend/tests/migrations/test_migration_safety.py`).
- [x] T008 [S0303] [P] Write failing admin MCP contract tests requiring user
  and validation tools while rejecting donor imports, tools, user item counts,
  and database item stats (`backend/tests/mcp/`).
- [x] T009 [S0303] [P] Write failing OpenAPI/generated-contract and source
  inventory tests requiring no donor path, operation, service, schema, model,
  CRUD helper, registered error, backend test, or documentation claim
  (`backend/tests/scripts/test_generate_client_contract.py`,
  `backend/tests/architecture/`).

---

## Erasure And Donor Retirement Implementation (10 tasks)

- [x] T010 [S0303] Add the registered retryable account-purge failure
  code/status/detail and remove Item error codes, messages, content-type
  constants, and item-specific not-found fallback
  (`backend/app/core/constants.py`, `backend/app/core/exceptions.py`).
- [x] T011 [S0303] Implement one private engine-purge route helper using only
  `Txt2CrsApplicationDep`, exact target UUID, known public exception
  translation, bounded structured events, and no private exception context
  (`backend/app/api/routes/users.py`).
- [x] T012 [S0303] Integrate engine-first purge into self-service deletion
  before any PostgreSQL delete/commit while preserving superuser self-delete
  protection and truthful post-purge database-failure behavior
  (`backend/app/api/routes/users.py`).
- [x] T013 [S0303] Integrate engine-first purge into superuser target deletion,
  remove the explicit Item delete statement, and preserve not-found/self
  authorization before mutation (`backend/app/api/routes/users.py`).
- [x] T014 [S0303] Add the immutable Alembic head revision that drops `item`
  and recreates the exact final empty donor schema on downgrade with comments
  documenting irreversible row loss
  (`backend/app/alembic/versions/<revision>_drop_donor_item_table.py`).
- [x] T015 [S0303] Remove Item SQLModel/request/response contracts,
  `User.items`, item imports, CRUD helpers, HTTP router registration, and the
  donor route module after replacement acceptance remains green
  (`backend/app/models.py`, `backend/app/crud.py`, `backend/app/api/main.py`,
  `backend/app/api/routes/items.py`).
- [x] T016 [S0303] Remove obsolete donor route/model tests and test utilities,
  then update shared fixtures and assertions to use user/job factories without
  weakening authentication, deletion, or database coverage
  (`backend/tests/api/routes/test_items.py`,
  `backend/tests/models/test_item_models.py`, `backend/tests/utils/item.py`,
  `backend/tests/conftest.py`).
- [x] T017 [S0303] Remove admin MCP Item imports, list/read tools,
  per-user/database item counts, and donor descriptions while preserving its
  read-only user/schema/validation boundary and complete separation from the
  research MCP (`backend/app/mcp/server.py`, `backend/app/mcp/__init__.py`).
- [x] T018 [S0303] Remove obsolete donor documentation and replace current
  backend/API/database/architecture/test claims with durable jobs,
  engine-first account erasure, and schema-only downgrade truth
  (`docs/items-feature.md`, `backend/README_backend.md`,
  `docs/api/README_api.md`, `docs/database/SCHEMA.md`,
  `docs/ARCHITECTURE.md`, `backend/tests/README_backend_tests.md`).
- [x] T019 [S0303] Regenerate OpenAPI and the TypeScript client only through
  `scripts/generate-client.sh`, preserving formatter ownership and proving no
  generated donor path, service, operation, request/response, or schema
  (`frontend/openapi.json`, `frontend/src/client/`).

---

## Verification And Phase Gate (5 tasks)

- [x] T020 [S0303] Run focused user deletion, account-purge acceptance,
  migration, error, admin-MCP, architecture, and generated-contract suites;
  resolve every failure at its owning boundary (`backend/tests/`).
- [x] T021 [S0303] Run clean/populated disposable PostgreSQL upgrade plus
  head-minus-one downgrade/head re-upgrade commands and record exact schema
  evidence without touching port 5447
  (`backend/app/alembic/versions/`, `backend/tests/migrations/`).
- [x] T022 [S0303] Run complete engine and backend suites plus engine/backend
  Ruff format/check, strict mypy, and backend ty from their owning package
  roots (`backend/packages/txt2crs/pyproject.toml`,
  `backend/pyproject.toml`).
- [x] T023 [S0303] Regenerate the client twice, prove byte stability, run
  generated-artifact/Biome checks, and record the intentional Phase 04
  learner-source TypeScript dependency without adding a stale or hand-written
  Item client shim (`scripts/generate-client.sh`, `frontend/src/client/`).
- [x] T024 [S0303] Run relevant repository hooks and explicit untracked-file
  checks; re-audit purge order/retry, log/error privacy, migration downgrade
  truth, donor absence, MCP separation, ASCII/LF, and diff hygiene before
  handing the completed Phase 03 session to review (`backend/`, `docs/`,
  `frontend/src/client/`).

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All session-scoped tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] implementation-notes.md updated
- [x] Known Phase 04 frontend source dependency recorded
- [x] Ready for `creview` (next step in the implement -> creview -> validate
  sequence)

---

## Next Steps

Run the `creview` workflow step, then `validate` after every review finding is
resolved.
