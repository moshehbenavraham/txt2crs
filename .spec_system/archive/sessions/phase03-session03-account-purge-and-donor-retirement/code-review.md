# Code Review and Repair Report

**Session ID**:
`phase03-session03-account-purge-and-donor-retirement`
**Package**: backend
**Reviewed**: 2026-07-20
**Base Commit**: `341f8497e8f408137f2920286d3cd9f7cd94ae6a`
**Scope**: All changes since the base commit (uncommitted work plus
mid-session commits)
**Result**: RESOLVED

## Review Surface

The review covered the complete 47-file implementation surface present before
this report: 40 tracked changes and 7 untracked files. There were no staged
changes or mid-session commits. This report is a review artifact and is not
counted in that implementation total.

**Files reviewed** (all changes since the base commit):

Tracked modifications and deletions:

- `.spec_system/state.json` - tracked-modified
- `backend/AGENTS.md` - tracked-modified
- `backend/README_backend.md` - tracked-modified
- `backend/app/api/deps.py` - tracked-modified
- `backend/app/api/main.py` - tracked-modified
- `backend/app/api/routes/items.py` - tracked-deleted
- `backend/app/api/routes/users.py` - tracked-modified
- `backend/app/core/constants.py` - tracked-modified
- `backend/app/core/exception_handlers.py` - tracked-modified
- `backend/app/core/exceptions.py` - tracked-modified
- `backend/app/core/txt2crs_errors.py` - tracked-modified
- `backend/app/crud.py` - tracked-modified
- `backend/app/mcp/__init__.py` - tracked-modified
- `backend/app/mcp/server.py` - tracked-modified
- `backend/app/models.py` - tracked-modified
- `backend/tests/README_backend_tests.md` - tracked-modified
- `backend/tests/api/routes/test_error_contracts.py` - tracked-modified
- `backend/tests/api/routes/test_items.py` - tracked-deleted
- `backend/tests/api/routes/test_users.py` - tracked-modified
- `backend/tests/conftest.py` - tracked-modified
- `backend/tests/core/test_txt2crs_errors.py` - tracked-modified
- `backend/tests/migrations/test_migration_safety.py` - tracked-modified
- `backend/tests/models/test_item_models.py` - tracked-deleted
- `backend/tests/scripts/test_generate_client_contract.py` - tracked-modified
- `backend/tests/utils/item.py` - tracked-deleted
- `docs/ARCHITECTURE.md` - tracked-modified
- `docs/adr/0004-rfc9457-error-format.md` - tracked-modified
- `docs/api/README_api.md` - tracked-modified
- `docs/dashboard-design.md` - tracked-modified
- `docs/database/SCHEMA.md` - tracked-modified
- `docs/items-feature.md` - tracked-deleted
- `examples/backend/api/authenticated_endpoint.py` - tracked-modified
- `examples/backend/api/error_handling.py` - tracked-modified
- `examples/backend/crud/paginated_list.py` - tracked-modified
- `examples/backend/crud/update_partial.py` - tracked-modified
- `examples/backend/testing/unit_test_crud.py` - tracked-modified
- `frontend/src/client/index.ts` - tracked-modified, generated
- `frontend/src/client/schemas.gen.ts` - tracked-modified, generated
- `frontend/src/client/sdk.gen.ts` - tracked-modified, generated
- `frontend/src/client/types.gen.ts` - tracked-modified, generated

Untracked files:

- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/implementation-notes.md`
  - untracked
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/spec.md`
  - untracked
- `.spec_system/specs/phase03-session03-account-purge-and-donor-retirement/tasks.md`
  - untracked
- `backend/app/alembic/versions/a7d9c2e4f601_drop_donor_item_table.py`
  - untracked
- `backend/tests/acceptance/test_account_purge.py` - untracked
- `backend/tests/architecture/test_donor_retirement.py` - untracked
- `backend/tests/mcp/test_admin_mcp_contract.py` - untracked

**Inventory commands**: `git status --short`,
`git log --oneline "$BASE"..HEAD`, `git diff "$BASE"`,
`git diff --cached "$BASE"`, and
`git ls-files --others --exclude-standard`.

Generated files were reviewed through their source OpenAPI operations,
repository generator, static contract regressions, Biome formatting, donor
symbol searches, and two byte-identical regeneration runs. They were not
edited manually.

## Findings by Severity

### Critical

No findings.

### High

- `backend/app/mcp/server.py:40` and `backend/app/mcp/server.py:218` retained
  validation commands rooted at another checkout and allowed
  `run_ruff_check(fix=True)` to mutate source through an administrative MCP
  documented as read-only. | Fix: derive the actual backend root from the
  module, route every validation command through it, remove the mutation
  parameter and `--fix`, and add a command-capture regression at
  `backend/tests/mcp/test_admin_mcp_contract.py:89`. | Status: FIXED

### Medium

- `backend/app/api/routes/users.py:75`, both delete decorators, and the
  generated contract omitted the retryable post-purge database failure and
  purge-unavailable outcomes. Their copy also implied broader erasure than
  the operation performs. | Fix: document Problem Details 500 and 503
  responses, state partial-failure retry behavior, explicitly exclude retained
  logs and backups, regenerate the client, and lock both operations at
  `backend/tests/scripts/test_generate_client_contract.py:289`. | Status:
  FIXED
- `docs/database/SCHEMA.md:56` and `docs/dashboard-design.md:744` named a
  nonexistent purge method and response model, so copied examples could not
  work against the public package/API. | Fix: name
  `Txt2CrsApplication.purge_owner(...)` and `JobStatusPublic`, clarify
  application defaults versus database server defaults, and add static
  contract assertions. | Status: FIXED
- `backend/AGENTS.md:168` and five curated backend examples still taught the
  deleted donor model, route, CRUD, and error contracts. Those repository
  instructions would have generated broken new code after donor retirement. |
  Fix: replace the examples with current user/profile/admin contracts, preserve
  authorization-before-lookup and safe logging guidance, and compile, lint,
  test, and statically guard the examples at
  `backend/tests/architecture/test_donor_retirement.py:113`. | Status: FIXED

### Low

- `backend/tests/acceptance/test_account_purge.py:181` could join a thread
  that had never started and could leave an active executor alive when an
  earlier assertion failed, masking the useful failure. | Fix: track thread
  starts, close a live executor first, join only started threads, and always
  close the application. | Status: FIXED
- `backend/tests/migrations/test_migration_safety.py:123` inspected the
  recreated donor table but did not require its historical `created_at`
  column to remain timezone-aware. | Fix: assert the exact timezone flag in
  the downgrade schema contract and rerun the PostgreSQL migration tests. |
  Status: FIXED
- `backend/tests/api/routes/test_users.py:753` did not exercise the public
  `ApplicationClosedError` translation branch. | Fix: add a facade double and
  regression proving safe `SYSTEM_6001`/503 output, retained identity, finite
  `application_closed` logging, and absence of private exception context. |
  Status: FIXED
- `backend/app/core/constants.py:192` still taught a nonexistent
  `get_items()` pagination helper after the donor domain was removed. | Fix:
  replace it with a domain-neutral page-size calculation and extend the
  donor-retirement source regression. | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- The session specification remains `Status: Not Started` until the Apex
  `validate` workflow performs the authoritative transition. Completed tasks
  and this review do not preempt that workflow.
- The learner `/items` route, dashboard, components, hook, navigation, Zod,
  branded types, frontend examples, and Playwright work remain unchanged by
  explicit Session 03 scope. Phase 04 owns their replacement. The resulting
  13 `TS2305` missing-export errors are recorded rather than hidden behind a
  stale generated `Item` shim.
- Historical Alembic revisions retain donor names because migration history
  is immutable. The new head removes the donor table and its downgrade
  recreates the exact preceding empty schema; it cannot recover deleted rows.
- Historical dashboard blueprints remain in the design guide for Phase 04 to
  replace. Current API truth in that guide no longer claims donor aggregates
  or nonexistent job response contracts.
- Retained logs, backup bundles, and external-provider copies are outside this
  erasure operation. Public API and database documentation now say so
  explicitly.
- The admin MCP and loopback research MCP remain separate boundaries. No
  import, registration, tool, or runtime connection was introduced between
  them.

## Behavior Changes

- Self-service and administrative account deletion purge engine-owned owner
  state through the public facade before committing PostgreSQL identity
  deletion.
- Purge failures leave the user intact and return a context-free `USER_2007`
  503; a closed application returns the existing safe lifecycle error.
- A database failure after successful purge reports partial progress
  truthfully, and the idempotent operation is safe to retry.
- OpenAPI and the generated client now expose both 500 and 503 deletion
  outcomes and describe the actual live-data erasure boundary.
- The donor Item route, SQLModel/CRUD/error contracts, admin-MCP tools,
  current backend tests/guidance, documentation claims, and generated client
  symbols are removed.
- Alembic head drops the donor table; downgrade recreates its exact prior
  empty schema for application rollback compatibility.
- Administrative MCP validation now targets this checkout and cannot request
  Ruff source mutation.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first admin MCP review regression | Focused `test_admin_mcp_validation_tools_target_this_backend_without_file_writes` before repair | EXPECTED FAIL | Captured validation cwd pointed to the retired `python-react-boilerplate` checkout |
| Tests-first account OpenAPI regression | Focused `test_account_delete_contract_documents_retryable_partial_failures` before repair | EXPECTED FAIL | Generated response map raised `KeyError: '500'` |
| Tests-first current-doc regression | Focused `test_current_documentation_names_real_public_erasure_and_job_contracts` before repair | EXPECTED FAIL | Documentation named `purge_owner_data` and `JobPublic`, neither of which exists |
| Tests-first guidance regression | Focused `test_backend_agent_guidance_and_examples_use_current_shell_contracts` before repair | EXPECTED FAIL | Backend instructions and examples imported retired Item contracts |
| Tests-first final donor-docstring regression | Focused donor source test before repair | EXPECTED FAIL | `get_items(` remained in `backend/app/core/constants.py` |
| Repaired review surface | Focused route, acceptance, migration, architecture, MCP, and generated-contract suites with isolated PostgreSQL | PASS | 50 tests passed before the final docstring repair; the final architecture/MCP/generated slice then passed 19 tests |
| Migration lifecycle | Clean head upgrade, populated donor upgrade, one-revision downgrade inspection, and re-upgrade on disposable PostgreSQL `127.0.0.1:55433` | PASS | Head `a7d9c2e4f601`; populated donor rows removed; downgrade restored the exact empty prior schema including timezone-aware `created_at`; re-upgrade returned to head |
| Real facade erasure acceptance | `uv run pytest tests/acceptance/test_account_purge.py -q` with isolated PostgreSQL | PASS | Active work settled before identity deletion, artifacts/jobs disappeared, failure retained identity, and retry completed |
| Backend tests | `uv run pytest tests/ -q` with isolated PostgreSQL | PASS | 473 passed; 102 known test/dependency warnings |
| Engine tests | `uv run --package txt2crs pytest -q` | PASS | 470 passed; 1 explicit live-subscription test skipped |
| Backend linter/formatter/types | Ruff check and format over `app`, `tests`, and `examples/backend`; strict mypy; ty | PASS | 109 files formatted; 47 application files mypy-clean; Ruff and ty passed |
| Engine linter/formatter/types | Package Ruff check and format; strict mypy | PASS | 138 files formatted; no lint or type issue |
| Generated provenance | Two consecutive isolated `scripts/generate-client.sh` runs plus aggregate SHA-256 | PASS | Both complete generated trees hashed to `bd4c08f7743ebb7cdfb7544425d61922440a7ec46eda25b8b9cc3a6b165a845b` |
| Generated frontend formatting | Read-only Biome check over `frontend/openapi.json` and `frontend/src/client` | PASS | 18 files checked with no fixes |
| Deferred frontend dependency | `npm run typecheck` | EXPECTED DEPENDENCY | Exactly 13 `TS2305` errors, all in the explicitly deferred learner Item sources owned by Phase 04 |
| Repository hooks | `SKIP=typescript-frontend pre-commit run` with isolated PostgreSQL | PASS | Every applicable hook passed; only the explicitly deferred frontend typecheck hook was skipped |
| Encoding and whitespace | ASCII-byte, carriage-return, and `git diff --check` scan over the complete changed/untracked surface | PASS | No non-ASCII byte, CRLF, or whitespace error remains |
| Security and boundary inspection | Secret/private-detail, donor-symbol, purge-order, generated-contract, and admin/research MCP cross-wiring searches | PASS | Current backend/generated sources are donor-free; logs and public errors remain bounded; MCP boundaries are disjoint |
| Final diff re-read | `git diff "$BASE"` plus every file from `git ls-files --others --exclude-standard` | PASS | No remaining correctness, privacy, migration, resource, documentation, or generated-provenance issue |

## Summary

1. Reviewed the complete 47-file base-to-worktree implementation surface.
2. Found 0 critical, 1 high, 3 medium, and 4 low issues.
3. Resolved all eight findings with focused regressions and targeted repairs.
4. Backend, engine, migration, generated-client, lint, format, type, security,
   and repository-hook gates pass within the Session 03 scope.
5. The only expected dependency is the explicitly deferred Phase 04 learner
   source replacement; no review finding or Session 03 blocker remains.

Next command: `validate`
