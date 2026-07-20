# Session Specification

**Session ID**: `phase03-session03-account-purge-and-donor-retirement`
**Phase**: 03 - Durable Jobs API
**Status**: Planned
**Created**: 2026-07-20
**Base Commit**: 341f8497e8f408137f2920286d3cd9f7cd94ae6a
**Package**: backend
**Package Stack**: Python 3.14, FastAPI, SQLModel, PostgreSQL 18, Alembic,
public txt2crs owner lifecycle, pytest, read-only admin MCP, and generated
OpenAPI/TypeScript client artifacts

---

## 1. Session Overview

This session completes Phase 03 by making PostgreSQL account deletion and
engine-owned learner-data erasure one ordered application operation. Both
self-service and superuser deletion call the lifespan-owned public
`Txt2CrsApplication.purge_owner()` boundary before deleting the PostgreSQL
identity. The package operation already cancels and joins matching executors,
removes artifacts first, and transactionally removes owner job state. A purge
failure therefore leaves the PostgreSQL user intact and returns one stable,
retryable, context-free application error.

The session then retires the temporary donor `items` backend after the durable
jobs replacement API and its acceptance coverage are green. A new Alembic
revision drops the table on upgrade and recreates only the final donor schema
on downgrade. Tests prove clean and existing upgrades, intentional donor-row
loss, and a downgrade/upgrade schema round trip without claiming data
recovery.

All item routes, SQLModel contracts, CRUD helpers, shell errors, backend tests,
documentation claims, generated operations, and read-only admin MCP tools are
removed. The research MCP remains package-owned and untouched.

---

## 2. Objectives

1. Purge every owner's engine request, checkpoint, delivery row, artifact,
   and active executor before either PostgreSQL user-deletion path commits.
2. Preserve the PostgreSQL identity when engine purge fails and expose a safe
   registered error that permits an idempotent retry.
3. Remove the donor item API and implementation without changing the public
   engine boundary or connecting the admin and research MCP servers.
4. Drop the item table through a tested Alembic head revision whose downgrade
   restores only the empty final donor schema.
5. Regenerate the OpenAPI and TypeScript client through the repository script
   and prove no generated item operation or schema remains.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase03-session01-durable-job-submission-and-admission` - supplies the
  complete durable replacement write API and admission acceptance coverage.
- [x] `phase03-session02-owner-scoped-job-results-and-recovery` - supplies the
  complete replacement read/delivery API, restart proof, and generated
  contract coverage.
- [x] `phase01-session05-public-facade-and-owner-lifecycle` - supplies the
  idempotent owner purge, artifact-first ordering, transactional SQLite
  deletion, active-executor cancellation, and join barrier.
- [x] `phase02-session01-engine-composition-lifecycle` - supplies the single
  lifespan-owned facade injected into FastAPI routes.

### Required Tools Or Knowledge

- FastAPI dependency injection and RFC 9457 `AppException` translation.
- Public `Txt2CrsApplication.purge_owner()` and `OwnerPurgeError` contracts.
- SQLModel/PostgreSQL transaction behavior and Alembic upgrade/downgrade
  authoring.
- Generated OpenAPI/client ownership through `scripts/generate-client.sh`.
- FastMCP read-only administrative tool registration.

### Environment Requirements

- Backend and migration tests use the isolated PostgreSQL 18 instance on host
  port 55433, never the unrelated PostgreSQL service on port 5447.
- Engine tests remain credential-free, network-free, and tenant-scoped to
  temporary SQLite/filesystem roots.
- OpenAPI generation must not start providers, workers, listeners, or
  lifespan resources.
- Migration tests create and destroy uniquely named disposable PostgreSQL
  databases through the configured administrative connection.

---

## 4. Scope

### In Scope (MVP)

- Tests-first self-service and superuser account deletion through an injected
  public engine facade.
- Exact owner UUID forwarding, purge-before-delete ordering, and no
  PostgreSQL commit after a purge failure.
- A registered safe retryable error plus bounded structured success/failure
  events containing only pseudonymous user ID and finite reason code.
- Real-facade acceptance proving active owner work settles before purge and
  both engine and PostgreSQL owner state are absent after successful deletion.
- An Alembic revision that drops `item` at head and recreates the complete
  final pre-retirement schema only on downgrade.
- Clean upgrade, existing-database upgrade with donor rows, head downgrade,
  and re-upgrade schema verification.
- Removal of item routes, router registration, SQLModel contracts and
  relationship, CRUD helpers, constants/messages, item-specific exception
  fallback, backend tests/fixtures/utilities, documentation claims, and admin
  MCP item tools/stats.
- Regenerated `frontend/openapi.json` and `frontend/src/client/` with no donor
  path, operation, request, response, or schema.
- Final Phase 03 acceptance and strict shell/package/admin-MCP boundary audit.

### Out Of Scope (Deferred)

- Learner `/items` route, component, hook, dashboard, navigation, Zod, branded
  type, and Playwright removal - Reason: the Phase 03 PRD explicitly limits
  frontend work to generated artifacts; Phase 04 owns product-specific route
  replacement and the learner redesign.
- Full frontend TypeScript/build success immediately after generated donor
  operations disappear - Reason: the deferred Phase 04 learner source still
  imports those removed generated symbols. This known sequential dependency
  is resolved in the next planned phase, not hidden with a hand-written or
  stale client shim.
- Log, backup-bundle, or external-provider erasure automation - Reason:
  retention and backup policy remain a documented release concern.
- Job-specific deletion, retention scheduling, learner cancellation, or job
  history.
- Any import, registration, or runtime connection between the admin MCP and
  the package research MCP.

---

## 5. Technical Approach

### Architecture

Add one private route helper in `users.py` that accepts the injected public
application and target UUID. It emits a bounded `user.engine_purge_started`
event, calls `purge_owner(user_id=str(user_id))`, and translates only
`OwnerPurgeError` or the package's safe public operation failure into a new
registered retryable shell error. It never logs exception text, row counts,
paths, source data, email, or artifact metadata.

Both deletion routes perform all authorization and user-existence checks
before purge, then invoke that helper before `session.delete()` or
`session.commit()`. The superuser path no longer issues an item delete. If the
engine purge succeeds but PostgreSQL commit fails, the engine side is already
idempotently empty and a later retry can finish identity deletion; the API
must not claim atomic rollback across stores.

Remove the Item SQLModel hierarchy and `User.items` relationship so metadata
matches the new head schema. Delete the item router and CRUD/test helpers, and
remove item-specific error ranges and exception dispatch. Keep generic
educational assessment "items" and unrelated collection variables; the audit
targets the donor domain, not ordinary English or engine assessment models.

Create a new Alembic revision after `fe56fa70289e`. Upgrade uses
`op.drop_table("item")`. Downgrade recreates the final donor schema exactly:
UUID primary key, bounded title/description/source URL, text content,
VARCHAR(50) content type, JSON metadata, nullable timezone-aware
`created_at`, non-null owner UUID, named cascade foreign key, and owner index.
Downgrade intentionally creates no donor rows. Runtime migration tests inspect
the schema and verify an existing row is gone after upgrade and remains absent
after downgrade.

Remove admin MCP `list_items`, `get_item`, user `item_count`, and database
`item_count` while preserving user introspection and code-validation tools.
Regenerate the public contract twice through the owning script and assert byte
stability plus complete absence of `/items` operations and Item schemas.

### Design Patterns

- Engine-first erasure: durable private engine state is gone before the shell
  identity can disappear.
- Idempotent compensation: if PostgreSQL fails after engine purge, a repeated
  purge is a safe no-op before the identity deletion is retried.
- Public-boundary injection: route code receives only
  `Txt2CrsApplicationDep`; it never imports an engine store, worker executor,
  checkpoint, or filesystem path.
- Safe error allowlist: translate known public purge failure categories into
  one finite RFC 9457 code without retaining private exception context.
- Schema-only downgrade: restore operational compatibility without pretending
  a destructive donor-row removal is reversible.
- Generated contract ownership: remove source API definitions, then regenerate
  all derivative client files rather than editing them.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/app/alembic/versions/<revision>_drop_donor_item_table.py` | Destructive head upgrade and schema-only donor downgrade | ~90 |
| `backend/tests/acceptance/test_account_purge.py` | Real public-facade cross-store erasure and retry acceptance | ~260 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/app/api/routes/users.py` | Inject public application, coordinate purge before both deletes, remove direct item deletion, add safe events | ~100 |
| `backend/app/models.py` | Remove donor Item models, schemas, aliases, and User relationship | -110 |
| `backend/app/crud.py` | Remove donor Item imports and helper | -80 |
| `backend/app/api/main.py` | Remove item router registration | -2 |
| `backend/app/core/constants.py` | Add account-purge failure code/status and remove item constants/messages | ~10 |
| `backend/app/core/exceptions.py` | Remove item-specific not-found fallback while keeping explicit user handling | -8 |
| `backend/app/mcp/server.py` and `backend/app/mcp/__init__.py` | Remove donor imports/tools/counts and update server description | -150 |
| `backend/tests/api/routes/test_users.py` | Add purge order/failure/retry assertions to both deletion paths | ~180 |
| `backend/tests/migrations/test_migration_safety.py` | Verify clean/existing upgrade and empty downgrade/re-upgrade schema | ~180 |
| `backend/tests/api/routes/test_error_contracts.py` | Protect registered purge failure and donor-code absence | ~30 |
| `backend/tests/scripts/test_generate_client_contract.py` | Protect complete donor absence from OpenAPI/client artifacts | ~60 |
| `frontend/openapi.json` and `frontend/src/client/` | Generated contract without donor items | generated |
| `docs/api/README_api.md`, `docs/database/SCHEMA.md`, `docs/ARCHITECTURE.md`, `backend/README_backend.md`, and `backend/tests/README_backend_tests.md` | Replace donor claims with jobs/account-erasure/migration truth | ~120 |

### Files To Delete

| File/Directory | Reason |
|----------------|--------|
| `backend/app/api/routes/items.py` | Donor HTTP API retired |
| `backend/tests/api/routes/test_items.py` | Donor route behavior no longer exists |
| `backend/tests/models/test_item_models.py` | Donor SQLModel contracts no longer exist |
| `backend/tests/utils/item.py` | Donor test factory no longer exists |
| `docs/items-feature.md` | Donor feature documentation is obsolete |

---

## 7. Success Criteria

### Functional Requirements

- [ ] Both account deletion routes call public owner purge with the target
  UUID before any PostgreSQL delete or commit.
- [ ] Authorization and not-found checks complete before purge, so forbidden
  or absent targets cannot trigger engine mutation.
- [ ] An active owner executor is cancelled and joined before purge returns,
  and no artifact can be recreated after account deletion succeeds.
- [ ] A purge failure returns the registered retryable Problem Detail, logs
  no private exception content, and leaves the PostgreSQL user present.
- [ ] Repeating deletion after a prior engine purge is safe and can complete
  PostgreSQL deletion.
- [ ] A clean database upgrades to head without an item table.
- [ ] An existing head-minus-one database with donor rows upgrades to an
  item-free schema and intentionally loses those rows.
- [ ] Downgrading one revision recreates the exact empty donor schema; upgrading
  again removes it.
- [ ] No donor item route, router, SQLModel, relationship, CRUD helper, error
  code/message, backend test/utility, documentation claim, generated operation
  or schema, or admin MCP tool/count remains.
- [ ] Admin and research MCP boundaries remain separate and import no code
  from each other.

### Testing Requirements

- [ ] Failing deletion, acceptance, migration, error, admin-MCP, and generated
  contract tests are observed before implementation.
- [ ] Focused deletion tests cover self, superuser target, forbidden
  superuser self-delete, missing target, purge success, purge failure, retry,
  and PostgreSQL post-purge failure truth.
- [ ] Migration tests exercise clean upgrade, populated existing upgrade,
  downgrade schema inspection, empty-row semantics, and re-upgrade.
- [ ] Complete engine and backend suites remain green.
- [ ] Client generation is byte-stable and generated artifacts contain no
  donor contract.
- [ ] Relevant frontend formatting/generated-contract checks pass; the known
  learner-source TypeScript dependency is carried directly into Phase 04.

### Non-Functional Requirements

- [ ] Route handlers call only the public facade and contain no engine purge,
  persistence, artifact, or worker implementation.
- [ ] Logs contain no email, source content, filename, artifact hash, path,
  provider value, exception string, or database detail.
- [ ] Error responses preserve neither `__cause__` nor `__context__` from a
  private purge exception.
- [ ] Cross-store order is explicit and documented; no code or docs claim a
  distributed transaction.
- [ ] Destructive migration behavior is documented and downgrade makes no
  donor-row recovery claim.

### Quality Gates

- [ ] All files ASCII-encoded
- [ ] Unix LF line endings
- [ ] Generous intern-friendly comments explain engine-first order,
  idempotent retry, safe logging, and schema-only downgrade
- [ ] Ruff format/check, strict mypy, ty, engine/backend tests, migration
  runtime proof, and relevant generated-client checks pass
- [ ] Repository diff contains no unrelated changes or manually edited
  generated files

---

## 8. Implementation Notes

### Working Assumptions

- The existing public facade already establishes the required worker barrier:
  it holds the application lock, finds owner-bound executor handles, calls
  `close()` to cancel and join them, and only then invokes artifact-first owner
  deletion. The shell should use this operation, not add a second worker API.
- A purge failure is operationally retryable and should map to a 503-class
  registered application code. A 500 would not communicate temporary
  unavailability, while a 4xx would incorrectly blame the caller.
- User UUID is already the package pseudonymous owner ID. It may be logged as
  an operational identifier under the existing allowlist, but email and
  profile data may not.
- The migration downgrade must reproduce the schema at `fe56fa70289e`, not
  merely a minimal table, because a one-revision rollback must leave the
  previous application version operable.
- Historical migrations remain immutable. Removing Item from current
  SQLModel metadata does not permit rewriting the prior revision chain.

### Conflict Resolutions

- The candidate session excludes learner UI removal, while generated Item
  symbols are still imported by the Phase 02 donor dashboard. The explicit
  phase boundary wins: remove only generated artifacts here, record the
  temporary compile dependency, and let Phase 04 remove/replace those product
  sources. Do not preserve a stale generated operation or add a fake local
  client merely to mask the dependency.
- "Reversible migration" means schema reversibility only. The Phase 03 PRD
  explicitly states that intentionally deleted donor rows cannot be restored.
- The global repository contains legitimate educational assessment "items"
  and generic collection variables. The no-item audit applies to the donor
  application domain and its route/model/client/tool documentation, not those
  unrelated meanings.
- Existing admin MCP user tools expose email because that boundary is an
  explicit local read-only administrative surface. This session removes donor
  tools but does not redesign unrelated user introspection.

### Key Considerations

- Complete authorization checks before purge; otherwise an invalid delete
  attempt could erase engine state.
- Do not catch `BaseException` around purge. Translate only expected public
  failure categories and allow process-control exceptions to propagate.
- A successful engine purge followed by PostgreSQL failure is partial
  progress, not rollback. Log a finite shell-deletion failure code and rely on
  idempotent retry.
- SQLAlchemy sessions may autoflush. No user mutation should be staged before
  purge begins.
- Remove relationship access such as admin MCP `len(user.items)` before
  removing the SQLModel relationship.
- Generated artifacts are derivative. Source contract tests must fail first,
  then one repository script owns the complete update.

### Relevant Considerations

- [P01-backend+backend/packages/txt2crs] **Account erasure spans two owners**:
  purge engine state before deleting PostgreSQL identity.
- [P01-backend/packages/txt2crs] **Cross-store erasure needs a worker
  barrier**: use the existing public facade cancellation/join and
  artifact-first deletion.
- [P00-backend+frontend] **Donor items remain temporary**: replacement jobs
  acceptance is now green, so retirement is authorized.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**:
  regenerate rather than hand-edit the client.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  no route may reach private engine persistence.
- [P02-backend] **Operational logs use field allowlists**: emit only stable
  pseudonymous identity and finite state/reason values.

### Behavioral Quality Focus

Checklist active: Yes

Top behavioral risks for this session:

- PostgreSQL identity is deleted even though engine purge failed, orphaning
  private learner state without an authenticated owner.
- Account deletion races an active executor that recreates artifacts after
  purge reports success.
- A destructive migration claims reversibility, silently leaves donor schema
  behind, or makes the previous application version unusable after downgrade.

---

## 9. Testing Strategy

### Unit And Route Tests

- Override `Txt2CrsApplicationDep` with an observable public-boundary fake and
  record purge, session delete, and commit order for self and admin routes.
- Raise `OwnerPurgeError` with deliberately private exception text and assert
  one fixed Problem Detail with no exception chaining or log leakage.
- Simulate a PostgreSQL commit failure after successful purge, assert partial
  truth, then retry against an idempotently empty engine.
- Protect superuser self-delete and missing-user checks from calling purge.
- Assert current error maps contain the new purge code and no Item codes.

### Acceptance Tests

- Build an owner job/artifact through the deterministic public application
  harness, create the matching PostgreSQL user, delete through HTTP, and prove
  both stores no longer expose the owner.
- Block one owner executor, start account deletion, verify purge/deletion has
  not completed, release cancellation-aware execution, and prove no artifact
  recreation.
- Inject a public purge failure, prove the PostgreSQL identity survives, then
  retry successfully.

### Migration Tests

- Upgrade a fresh disposable database directly to head and inspect that only
  the user application table remains.
- Upgrade a fresh database to `fe56fa70289e`, insert a valid user and donor
  item, upgrade to head, and prove the table and row are gone.
- Downgrade head by one revision, inspect every donor column, type,
  nullability, named cascade foreign key, and owner index, and prove zero rows.
- Upgrade again and prove the donor table is removed.

### Contract And Boundary Verification

- Inspect FastAPI OpenAPI before generation for no `/api/v1/items` path or
  Item component.
- Regenerate twice and compare hashes.
- Search generated files for donor path, service, operation, and schema
  identifiers.
- Import and inspect admin MCP registration for no donor tools or stats while
  user and code-validation tools remain available.
- Search shell routes for private engine imports and both MCP trees for
  cross-boundary imports.

---

## 10. Dependencies

### Other Sessions

- Depends on: `phase03-session01-durable-job-submission-and-admission`,
  `phase03-session02-owner-scoped-job-results-and-recovery`,
  `phase01-session05-public-facade-and-owner-lifecycle`, and
  `phase02-session01-engine-composition-lifecycle`.
- Depended by: both Phase 04 learner-experience sessions and both Phase 05
  hardening/submission sessions.

---

## Next Steps

Run `implement` for Phase 03 Session 03.
