# Implementation Summary

**Session ID**:
`phase03-session03-account-purge-and-donor-retirement`
**Package**: `backend`
**Completed**: 2026-07-20
**Duration**: 1.0 hours

---

## Overview

Session 03 completed the Durable Jobs API phase by joining account deletion
to the public engine owner lifecycle. Both self-service and administrative
deletion now authorize and resolve the target first, call the lifespan-owned
`Txt2CrsApplication.purge_owner()` barrier, and only then commit PostgreSQL
identity deletion. The package remains authoritative for active-executor
cancellation/join, artifact-first cleanup, and transactional engine-state
removal.

Purge failure leaves the user intact and returns a stable, context-free,
retryable Problem Detail. A database failure after successful engine erasure
reports partial progress truthfully, and retry remains safe because public
owner purge is idempotent.

With durable submission, status, result, recovery, and artifact delivery
already accepted, the temporary Item donor domain is now retired from the
HTTP API, SQLModel/CRUD/error contracts, admin MCP, tests/guidance,
documentation, PostgreSQL schema, and generated frontend client.

---

## Deliverables

### Files Created

| File or Area | Purpose | Lines |
|--------------|---------|-------|
| `backend/app/alembic/versions/a7d9c2e4f601_drop_donor_item_table.py` | Destructive donor-table upgrade and exact empty schema-only downgrade | 80 |
| `backend/tests/acceptance/test_account_purge.py` | Real public-facade active-work, cross-store erasure, failure, and retry acceptance | 304 |
| `backend/tests/architecture/test_donor_retirement.py` | Static current-source, documentation, guidance, and public-contract boundary | 162 |
| `backend/tests/mcp/test_admin_mcp_contract.py` | Read-only current-checkout admin MCP and donor-absence contract | 100 |
| Session workflow artifacts | Specification, tasks, implementation notes, review, security, validation, and this summary | 7 files |

### Files Modified

| File or Area | Changes |
|--------------|---------|
| User routes and application dependency | Added engine-first owner purge to both account deletion paths with exact authorization, order, safe errors, logs, and OpenAPI outcomes |
| Shell models, CRUD, routing, constants, and exceptions | Removed retired Item contracts and registered the account-purge failure |
| Administrative MCP | Removed item tools/counts, renamed the server, rooted validation in this checkout, and removed source mutation |
| Backend tests and curated examples | Added route/error/migration/generated boundary coverage and replaced broken donor examples with current user/admin contracts |
| Alembic migration tests | Proved clean and populated upgrades plus exact empty downgrade/re-upgrade schema |
| Generated frontend client | Removed donor paths, operations, services, request/response contracts, and schemas through the repository generator |
| Public documentation | Replaced donor claims with durable jobs, cross-store erasure, retained-copy truth, and schema-only rollback behavior |
| Apex state and Phase 03 PRD | Marked Session 03 and the complete Durable Jobs API phase complete |
| `backend/pyproject.toml` and `backend/uv.lock` | Advanced the backend shell package from 0.3.5 to 0.3.6 |

### Files Deleted

| File | Reason |
|------|--------|
| `backend/app/api/routes/items.py` | Temporary donor HTTP API retired |
| `backend/tests/api/routes/test_items.py` | Donor route no longer exists |
| `backend/tests/models/test_item_models.py` | Donor SQLModel contracts no longer exist |
| `backend/tests/utils/item.py` | Donor test factory no longer exists |
| `docs/items-feature.md` | Obsolete donor feature documentation |

---

## Technical Decisions

1. **Engine-first erasure**: establish the package worker/artifact/job barrier
   before mutating PostgreSQL so a failed purge cannot orphan private learner
   state behind a deleted identity.
2. **Public facade only**: keep cancellation, joins, artifacts, SQLite
   transactions, and idempotency inside `txt2crs`; the route coordinates one
   typed public call.
3. **Finite failure translation**: translate only known public application
   errors, log only pseudonymous user UUID and finite reason, and raise after
   the exception block so private cause/context cannot survive.
4. **Truthful partial progress**: document 500 after engine success and 503
   before PostgreSQL mutation rather than claiming a distributed rollback.
5. **Schema-only downgrade**: recreate the exact final donor schema for the
   preceding application revision without claiming deleted rows can return.
6. **Derivative client ownership**: regenerate OpenAPI/TypeScript twice and
   accept the explicit Phase 04 learner-source dependency instead of adding a
   false Item shim.
7. **Administrative boundary discipline**: preserve user/schema/validation
   tools, remove donor tools, derive the live backend root, and keep validation
   read-only.

---

## Test Results

| Metric | Value |
|--------|-------|
| Engine tests | 470 passed; 1 explicit live test skipped |
| Backend shell and acceptance | 473 passed |
| Complete deterministic passed | 943 |
| Failed | 0 |
| Migration lifecycle | 8 passed; head and no-drift checks passed |
| Review regression slice | 50 passed, followed by 19 final architecture/MCP/generated checks |
| Generated client | Biome-clean; byte-stable SHA-256 `bd4c08f7743ebb7cdfb7544425d61922440a7ec46eda25b8b9cc3a6b165a845b` |
| Static quality | Backend/engine Ruff, format, strict mypy, backend ty, and applicable pre-commit hooks passed |
| Coverage | N/A - authoritative validation commands did not enable coverage |

The full frontend compiler reports exactly 13 missing retired Item exports in
the learner sources explicitly assigned to Phase 04. Session 03 keeps that
dependency visible and adds no stale generated contract.

---

## Review Repairs

Formal code review resolved one High, three Medium, and four Low findings:

1. Rooted admin MCP validation in this checkout and removed Ruff mutation.
2. Added truthful 500/503 account-deletion OpenAPI outcomes and retained-copy
   language.
3. Corrected nonexistent facade/response names in current documentation.
4. Replaced donor backend instructions and curated examples.
5. Made active acceptance-thread/executor cleanup failure-safe.
6. Required timezone-aware historical downgrade schema.
7. Covered safe `ApplicationClosedError` translation.
8. Removed the final nonexistent donor pagination helper from a docstring.

Every code/contract repair has focused regression evidence, and all review
findings are resolved.

---

## Security And Privacy

- Authenticated current-user or superuser authorization and target existence
  always precede engine mutation.
- Public erasure failures contain stable code/detail/trace only and retain no
  private exception cause or context.
- Structured events contain pseudonymous user UUID and finite state/reason;
  they omit email, content, filename, artifact data, provider values, paths,
  exception strings, and database details.
- Successful live erasure removes engine requests, checkpoints, delivery
  rows, artifacts, and active owner work before PostgreSQL identity.
- API/docs explicitly exclude retained logs, backups, and external-provider
  copies from this operation so compliance claims remain truthful.
- No dependency, secret, raw-SQL, shell-injection, debug-default, or MCP
  cross-wiring change was introduced.

---

## Lessons Learned

1. Cross-store erasure must expose partial-progress truth; pretending two
   independent persistence owners share rollback is more dangerous than a
   clear retry contract.
2. Python exception context can leak a private package error even when the
   new message is safe; translate inside the handler but raise afterward with
   `from None`.
3. Destructive migration rollback is compatibility, not data recovery; test
   the exact old schema and document empty-row semantics.
4. Removing a generated API can correctly reveal a sequential frontend
   dependency. A temporary compatibility shim would make the contract less
   truthful and postpone necessary product replacement.
5. Repository instructions and few-shot examples are executable design
   inputs; retiring a domain requires updating them as carefully as runtime
   source.

---

## Future Considerations

Items for Phase 04 and Phase 05:

1. Replace the learner `/items` route, dashboard, components, hook,
   navigation, schemas, types, examples, and Playwright coverage with the
   durable course-job experience.
2. Preserve the account-erasure and private-error regressions when adding the
   learner account UI.
3. Complete log, backup, and external-provider retention/erasure policy before
   the release privacy gate.
4. Run the representative credentialed live proof and capture complete
   Devpost submission evidence after deterministic release validation.

---

## Session Statistics

- **Tasks**: 24 completed
- **Files Created**: 11 including workflow reports and this summary
- **Files Modified**: 35 implementation files before closeout bookkeeping
- **Files Deleted**: 5
- **Tests Added**: 26 test functions plus parameterized cases
- **Blockers**: 0
- **Review findings**: 8 resolved
