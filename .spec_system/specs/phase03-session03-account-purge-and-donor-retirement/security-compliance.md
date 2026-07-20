# Security & Compliance Report

**Session ID**:
`phase03-session03-account-purge-and-donor-retirement`
**Package**: backend
**Reviewed**: 2026-07-20
**Result**: PASS

## Scope

**Files reviewed** (session deliverables and their direct regressions):

- `backend/app/api/routes/users.py` and `backend/app/api/deps.py` - protected
  account-erasure coordination and public application injection
- `backend/app/core/constants.py`,
  `backend/app/core/txt2crs_errors.py`,
  `backend/app/core/exceptions.py`, and
  `backend/app/core/exception_handlers.py` - public error allowlist and donor
  error retirement
- `backend/app/models.py`, `backend/app/crud.py`, and
  `backend/app/api/main.py` - current shell data/route surface after donor
  retirement
- `backend/app/mcp/server.py` and `backend/app/mcp/__init__.py` - local
  read-only administrative boundary
- `backend/app/alembic/versions/a7d9c2e4f601_drop_donor_item_table.py` -
  destructive upgrade and schema-only rollback
- `backend/tests/acceptance/test_account_purge.py`,
  `backend/tests/api/routes/test_users.py`,
  `backend/tests/core/test_txt2crs_errors.py`,
  `backend/tests/migrations/test_migration_safety.py`,
  `backend/tests/mcp/test_admin_mcp_contract.py`,
  `backend/tests/architecture/test_donor_retirement.py`, and generated-contract
  tests - executable privacy, authorization, failure, migration, and boundary
  evidence
- `frontend/openapi.json` and `frontend/src/client/` - generated external API
  contract
- Current backend/API/database/architecture/ADR/test documentation and the
  retired donor documentation deletion - privacy and erasure claims
- The complete base-to-worktree inventory recorded in `code-review.md`,
  including five deleted donor files and the session workflow artifacts

**Review method**: Targeted static analysis of every session-touched file,
authorization/mutation-order inspection, private-detail and secret searches,
dependency-diff inspection, MCP cross-wiring search, deterministic tests, and
isolated PostgreSQL migration validation.

**Review evidence**:

- Command/check: `git diff --name-only
  341f8497e8f408137f2920286d3cd9f7cd94ae6a` plus
  `git ls-files --others --exclude-standard`
  - Result: PASS - review scope matches all tracked changes, deletions, and
    untracked session files.
  - Evidence: `code-review.md` inventories 40 tracked changes and 7 untracked
    implementation files before review artifacts.
- Command/check: hardcoded-secret regular-expression scan over changed
  application, core, MCP, and migration files
  - Result: PASS - no access key, private key, API key, client secret, or
    provider-token pattern matched.
  - Evidence: command printed `HARDCODED_SECRET_PATTERNS=ABSENT`.
- Command/check: targeted inspection/search of
  `backend/app/api/routes/users.py`
  - Result: PASS - current-user/superuser authorization and target existence
    precede purge; purge precedes `session.delete()` and `session.commit()`.
  - Evidence: self-delete order is lines 491-504 and admin-delete order is
    lines 751-766.
- Command/check: `str(error)`, `repr(error)`, email-log, and extra-field
  searches over the erasure/error boundary
  - Result: PASS - public failures and structured events contain no private
    exception string or email.
  - Evidence: only pseudonymous `user_id` and finite `reason_code` fields are
    emitted; command printed `PRIVATE_EXCEPTION_LOGGING=ABSENT`.
- Command/check: dependency manifest/lockfile diff against the base commit
  - Result: PASS - no dependency changed in this session.
  - Evidence: command printed `DEPENDENCY_CHANGES=NONE`.
- Command/check: generated donor scan and cross-MCP import scan
  - Result: PASS - the generated client contains no retired donor contract,
    and neither MCP boundary imports or registers the other.
  - Evidence: command printed `GENERATED_DONOR_CONTRACT=ABSENT` and
    `MCP_CROSS_WIRING=ABSENT`.
- Command/check: full backend and engine deterministic suites
  - Result: PASS - 473 backend and 470 engine tests passed; the only skip is
    the explicitly opt-in live-subscription test.
  - Evidence: no test failure; account-erasure acceptance covers success,
    active-work settlement, failure retention, and retry.
- Command/check: isolated PostgreSQL `alembic current`, `alembic check`, and
  migration test suite on port 55433
  - Result: PASS - head is `a7d9c2e4f601`, no upgrade operation is missing,
    and all 8 migration tests passed.
  - Evidence: clean/populated upgrade and downgrade/re-upgrade behavior match
    the tracked revision.

## Security Assessment

### Overall: PASS

| Category | Status | Severity | Details |
|----------|--------|----------|---------|
| Injection (SQLi, CMDi, LDAPi) | PASS | -- | Route queries use typed SQLModel operations; MCP validation passes argument lists directly to `subprocess.run` without a shell and uses a fixed repository root |
| Hardcoded Secrets | PASS | -- | No credential or private-key pattern in touched runtime/configuration files; PostgreSQL evidence uses process environment only |
| Sensitive Data Exposure | PASS | -- | Public errors are finite and context-free; logs contain only pseudonymous user UUID and finite state/reason fields |
| Insecure Dependencies | PASS | -- | No Python or JavaScript manifest/lockfile changed |
| Security Misconfiguration | PASS | -- | No CORS, debug, authentication, header, or deployment default changed; admin and research MCP boundaries remain disjoint |
| Database Security | PASS | -- | No hardcoded connection string or raw SQL concatenation; migration has upgrade/downgrade and was exercised on disposable PostgreSQL |

### Security Findings

No security findings.

The code-review repair that removed MCP source mutation and the stale external
checkout path is already resolved and regression-protected; it is not an open
validation finding.

## GDPR Compliance Assessment

### Overall: PASS

**Categories reviewed**: Data Collection & Purpose, Consent Mechanism, Data
Minimization, Right to Erasure, PII in Logs, Third-Party Data Transfers.

### Personal Data Inventory

| Data Element | Source | Storage | Purpose | Retention | Deletion Path |
|-------------|--------|---------|---------|-----------|---------------|
| User UUID | Authenticated account or authorized admin target | PostgreSQL `"user"` row; pseudonymous owner key in engine SQLite/artifact paths | Authentication identity, owner isolation, and deterministic erasure target | Until account deletion, subject to separately managed logs/backups | `DELETE /api/v1/users/me` or admin `DELETE /api/v1/users/{user_id}` calls public `purge_owner()` before PostgreSQL deletion |
| Email and profile | Existing account record | PostgreSQL `"user"` table; existing local admin MCP may read it | Login, profile, and authorized local administration | Until account deletion, subject to separately managed logs/backups | PostgreSQL user deletion after successful engine purge |
| Course request/checkpoint/delivery state | Existing learner generation request | Tenant-scoped engine SQLite | Durable course generation and recovery | Until owner purge or later retention policy | Public `Txt2CrsApplication.purge_owner()` transactionally removes owner job state |
| Generated artifacts | Existing learner job output | Private engine artifact tree | Course, review-material, test, and answer-key delivery | Until owner purge or later retention policy | Public owner purge removes artifacts before engine job parents |

This session collects no new personal-data category and introduces no new
consent or third-party transfer. It adds the application right-to-erasure
path across both live persistence owners. Retained logs, backup copies, and
external-provider copies are explicitly not misrepresented as erased by this
operation; their policy and automation remain separate release work.

### GDPR Findings

No GDPR findings.

The account route logs a pseudonymous user UUID because it is the minimum
stable operational identifier required to correlate erasure state. It does
not log email, profile data, source content, filenames, artifact details,
provider values, exception strings, or database details.

## Recommendations

- Complete the Phase 05 retention/privacy release gate for log, backup, and
  external-provider deletion policy; keep the current API copy truthful until
  that separate automation exists.
- Preserve the account-erasure and no-private-detail regressions when Phase 04
  replaces the learner account UI.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (`validate`)
- **Date**: 2026-07-20
