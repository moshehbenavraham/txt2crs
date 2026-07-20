# Session 03: Account Purge and Donor Retirement

**Session ID**: `phase03-session03-account-purge-and-donor-retirement`
**Package**: backend
**Status**: Complete
**Estimated Tasks**: 24
**Estimated Duration**: 2-4 hours

---

## Objective

Complete Phase 03 by coordinating engine purge before PostgreSQL account
deletion, then remove the temporary donor item domain and regenerate the
application contract from a verified Alembic schema transition.

---

## Scope

### In Scope (MVP)

- Tests for both self-service and superuser user-deletion paths.
- Public owner purge before PostgreSQL deletion with retryable partial-failure
  behavior and safe structured events.
- Item-table drop migration with clean/existing upgrade and supported
  downgrade/upgrade schema verification.
- Removal of item routes, models, CRUD helpers, constants/errors, tests,
  documentation, frontend generated operations, and read-only admin MCP item
  tools.
- OpenAPI and frontend client regeneration through the repository script.
- Final Phase 03 acceptance and boundary audit.

### Out of Scope

- Log or backup-bundle erasure automation.
- Job-specific deletion or retention scheduling.
- Learner UI route/component removal beyond generated client artifacts.
- Any connection between the admin MCP and research MCP.

---

## Prerequisites

- [ ] Sessions 01 and 02 job acceptance/read/delivery coverage is green.
- [x] Engine `purge_owner` is idempotent and establishes the required worker
  barrier.

---

## Deliverables

1. Tests proving engine purge precedes PostgreSQL deletion and a failed purge
   preserves the user for safe retry.
2. User-deletion integration through the public application boundary.
3. Alembic migration that drops and schema-only recreates the donor item
   table.
4. Complete donor item code, API, documentation, test, and admin-tool removal.
5. Regenerated OpenAPI/client artifacts and final Phase 03 validation record.

---

## Success Criteria

- [ ] Both account deletion routes purge all engine-owned owner state before
  PostgreSQL identity deletion.
- [ ] Purge failure returns a registered safe error and leaves the user
  present for idempotent retry.
- [ ] Clean and existing databases upgrade to an item-free schema.
- [ ] A supported downgrade/upgrade round trip recreates then removes the
  empty schema without claiming deleted donor-row recovery.
- [ ] Repository and generated artifacts contain no item route, model, CRUD
  helper, error code, test, docs claim, client operation, or admin MCP tool.
- [ ] Admin and research MCP boundaries remain separate.
- [ ] Backend, engine, acceptance, migration, generated-client, type, lint,
  and relevant frontend checks pass.
