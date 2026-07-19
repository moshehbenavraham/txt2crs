# Validation Report

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Package**: `backend/packages/txt2crs`
**Validated**: 2026-07-19
**Result**: PASS

## Validation Summary

| Check | Status | Notes |
|-------|--------|-------|
| Code Review | PASS | `code-review.md` is `RESOLVED`; all 9 findings are repaired |
| Tasks Complete | PASS | 24/24 tasks |
| Files Exist | PASS | 18/18 applicable specified deliverables plus 1 required supporting reader change; 3 conditional export files were not needed |
| ASCII Encoding | PASS | Every changed/untracked session file is ASCII with Unix LF and a final newline |
| Tests Passing | PASS | 444 passed, 1 explicitly gated live test skipped, 0 failed |
| Focused Session Tests | PASS | 79 facade/factory/purge/store/artifact/executor/import tests |
| Database Alignment | PASS | No schema change; owner deletion uses existing cascades and verified atomic transactions |
| Distribution | PASS | Wheel/sdist ship all 5 application modules and updated documentation |
| Success Criteria | PASS | 23/23 functional, testing, non-functional, and quality criteria |
| Static/Repository Gates | PASS | Lock, Ruff format/lint, strict mypy, build, and repository engine validation |
| Security & GDPR | PASS | No unresolved finding; complete retry-safe active-owner erasure is present |
| UI Product Surface | N/A | No FastAPI shell, frontend, generated client, or UI file changed |

**Overall**: PASS

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence |
|-------|-----------------------|--------|----------|
| Project state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Session 05 is active in Phase 01 and its workflow directory resolves. |
| Prerequisites | `bash .spec_system/scripts/check-prereqs.sh --json --env --package backend/packages/txt2crs` | PASS | Environment and package registration pass; generic migration-tool warnings are N/A for package-owned SQLite SQL. |
| Code review | Exact result parse and report inspection | PASS | Review is `RESOLVED`; 0 Critical, 2 High, 4 Medium, and 3 Low findings were fixed. |
| Task completion | Checkbox count in `tasks.md` | PASS | 24 complete, 24 total, 0 incomplete. |
| Deliverables | Explicit existence and non-empty inspection | PASS | All 9 created and 9 applicable modified deliverables exist; artifact-reader support exists; conditional jobs/ingestion/security export edits were unnecessary because the public factory keeps private imports internal. |
| ASCII/LF | Non-ASCII, CR, and final-byte scans | PASS | No non-ASCII byte, CRLF line, or missing final newline exists in the session surface. |
| Focused behavior | Session owner, facade, factory, lifecycle, SQLite, filesystem, executor, and public-import selection | PASS | 79 passed. |
| Full suite | `uv run --package txt2crs pytest -q` | PASS | 444 passed, 1 explicit live skip in 10.11 seconds. |
| Lock | `cd backend && uv lock --check` | PASS | 154 packages resolve from the synchronized lock. |
| Format/lint | Ruff format and `ruff check .` | PASS | All reviewed source/tests are formatted and lint-clean. |
| Types | `uv run --package txt2crs mypy` | PASS | No issues in 136 source files. |
| Owner deletion | Real SQLite and filesystem tests | PASS | Active/terminal rows, five-table cascade, other-owner preservation, commit/delete failures, symlink confinement, partial failure, retry, and repeated purge pass. |
| Public lifecycle | `tests/integration/test_application_lifecycle.py` | PASS | Public factory submits, discovers, executes, queries, reads 16 artifacts, recovers, purges twice, and closes without network/credentials. |
| Package build | Isolated `uv build --package txt2crs --out-dir <temp>` | PASS | `txt2crs-0.4.0` wheel and sdist built successfully. |
| Archive inspection | Exact tar/unzip member and wheel metadata inspection | PASS | All five application modules ship; README ships in sdist and its facade/factory guidance is in wheel metadata. |
| Repository validation | `bash scripts/validate-changes.sh engine --json` | PASS | Engine lint, strict typecheck, and tests all pass. |
| Security/privacy | Exact diff, secret/process/log/host/path/model scans and `security-compliance.md` | PASS | No secret, public listener, raw path, model fallback, dynamic execution, new PII log, or false purge success remains. |
| Final diff | `git diff --check` and whole-surface inspection | PASS | No whitespace error, staged file, scope leak, or unresolved validation issue remains. |

## Deliverable Alignment

### Status: PASS

Created application configuration, facade, factories, owner lifecycle, public
exports, and all four specified test modules are non-empty and exercised.
Modified store/service/artifact behavior, root lazy exports, canonical
fixtures, SQLite/filesystem/import tests, and README guidance are present.

The planned `jobs/__init__.py`, `ingestion/__init__.py`, and
`security/__init__.py` edits were explicitly conditional ("if needed"). They
are not needed: `txt2crs.application` is the supported shell boundary, while
its factory implementation may compose package-private concrete modules
without widening subsystem exports. `artifact_reader.py` received the small
supporting confined-owner path operation required by filesystem purge.

No application database schema changed, so no Alembic migration is required.
Package SQLite deletion relies on the already-released foreign-key schema and
is verified against real databases.

## Success Criteria

### Functional Requirements: 10/10

- [x] Every shell-needed operation is available through documented public
  `txt2crs.application` methods; lazy root facade/factory discovery also works.
- [x] Submit, recovery, runnable discovery, public snapshot, manifest, and
  single-artifact stream delegate to existing owner-safe authorities.
- [x] Authentication and readiness return existing strict browser-safe
  contracts.
- [x] Every executor is owner/job-bound, one-shot, cancelable, wait-closeable,
  and owns fresh budget/cancellation state.
- [x] The real factory composes enabled ingestion, content policy, SQLite,
  filesystem, Tavily, managed MCP, exact GPT-5.6 Codex, pipeline, renderer,
  readiness, and authentication implementations.
- [x] The deterministic factory shares the public protocol and copies fresh
  credential-free provider/budget/cancellation state for each job.
- [x] The public deterministic lifecycle produces and reads exactly 16
  artifacts and completes recovery, repeated purge, and close.
- [x] Owner purge deletes artifacts plus all jobs, requests, admissions,
  checkpoints, and deliveries, including active statuses.
- [x] Artifact/database/commit/count failures never return success; retries
  and already-purged owners are safe.
- [x] Executor/application close is synchronized and idempotent; later
  mutation/execution through a closed reference raises the stable closed
  error.

### Testing Requirements: 6/6

- [x] Initial collection/import/config failures and every review repair were
  observed failing before production fixes.
- [x] Real SQLite/filesystem coverage proves cascades, confinement, active
  deletion, partial failure, retry, and repeated purge.
- [x] Recording composition proves fresh budgets/cancellation and no provider
  startup during submit/query/executor creation/purge.
- [x] Deterministic integration imports the supported application boundary
  and uses no FastAPI, PostgreSQL, external network, or credential.
- [x] The complete credential-free suite passes; the real GPT-5.6/Tavily test
  remains explicitly gated by `TXT2CRS_RUN_LIVE_CODEX=1`.
- [x] Wheel and sdist contain the complete application package and public
  documentation.

### Non-Functional Requirements: 4/4

- [x] Public contracts/errors expose no owner hash, request content, SQL,
  private path, secret, discovered model list, or internal component type.
- [x] Configuration is strict/immutable, validates finite values, absolute
  non-symlinked separate private roots, numeric loopback, canonical scenario
  JSON, exact GPT-5.6, and secret masking.
- [x] Purge and close are synchronized, finite under the configured provider
  timeouts, idempotent, and never claim cross-store atomicity.
- [x] No shell, application PostgreSQL, frontend, hosted deployment, SMTP, or
  new provider entered the package session.

### Quality Gates: 3/3

- [x] All session files are ASCII with Unix LF and final newlines.
- [x] Complete types, descriptive names, and intern-oriented comments explain
  delegation, freshness, laziness, ownership, purge ordering, and recovery.
- [x] Ruff, strict mypy, pytest, build/archive inspection, repository engine
  validation, formal code review, and security validation pass.

## Conventions Compliance

### Status: PASS

- Reusable composition and lifecycle logic lives only in
  `backend/packages/txt2crs`; no shell route duplicates engine behavior.
- Tests were authored and observed failing before the initial implementation
  and before every formal-review repair.
- Public return values are strict package contracts rather than `Any`.
- SQLite statements are fixed and parameterized; no schema change or
  application Alembic requirement exists.
- Secret values remain in `SecretStr`/provider-owned boundaries and are absent
  from serialized configuration and public errors.
- README manual assembly guidance was replaced by the supported public factory
  and facade workflow.

## Security & GDPR Compliance

### Status: PASS

See `security-compliance.md`. The engine now provides complete active-owner
erasure for its SQLite and filesystem state, without claiming deletion of the
future shell's PostgreSQL account row or operator-owned provider credentials.
No new personal field, analytics, or logging path was introduced.

## Behavioral Quality Spot-Check

### Status: PASS

Reviewed application configuration/facade/factories/owner lifecycle, SQLite
purge, artifact confinement, and the public deterministic lifecycle for empty,
invalid, repeated, concurrent, partial-failure, restart, and cleanup behavior.
All review findings were repaired before validation; validation found no
additional repository-fixable defect.

## UI Product-Surface Spot-Check

### Status: N/A

No FastAPI route, React component, generated API client, CSS, or rendered
product surface changed.

## Validation Result

### PASS

All workflow gates, 24 tasks, 18 applicable specified deliverables, 23 success
criteria, full/focused tests, static checks, real persistence failure paths,
distributions, security/GDPR checks, and repository validation pass.

### Unresolved Failures And Blockers

None.

## Next Steps

Next command: `updateprd`
