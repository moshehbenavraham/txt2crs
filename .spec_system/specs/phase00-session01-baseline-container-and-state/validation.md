# Validation Report

**Session ID**: `phase00-session01-baseline-container-and-state`
**Package**: cross-cutting (`backend-shell`, `txt2crs-engine`, `frontend`)
**Validated**: 2026-07-19
**Result**: PASS

## Validation Summary

| Check | Status | Notes |
|-------|--------|-------|
| Code Review | PASS | `code-review.md` exists, covers the base-commit surface, and has `Result: RESOLVED` |
| Tasks Complete | PASS | 21/21 tasks |
| Files Exist | PASS | 25/25 declared deliverables exist and are non-empty |
| ASCII Encoding | PASS | All 46 review-surface files are ASCII with LF endings |
| Tests Passing | PASS | 421 passed, 0 failed, 1 explicitly live-gated skip |
| Database/Schema Alignment | N/A | No model, CRUD, Alembic, or persisted-data-shape change |
| Success Criteria | PASS | All functional, testing, non-functional, and quality criteria met |
| Conventions | PASS | Naming, structure, comments, testing, and package boundaries spot-checked |
| Security & GDPR | PASS | Security PASS; GDPR N/A because no personal-data behavior changed |
| Behavioral Quality | PASS | No trust-boundary, cleanup, concurrency, failure-path, or contract violation |
| UI Product Surface | PASS | Desktop/mobile login surfaces contain product content and no diagnostics |

**Overall**: PASS

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Project state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Active cross-cutting Phase 00 session found with review artifacts |
| Code review | `sed -n 's/^\*\*Result\*\*: *//p' code-review.md` plus scope inspection | PASS | Exact result `RESOLVED`; 46-file base-commit scope recorded |
| Task completion | `rg -c '^- \[[x ]\] T[0-9]+' tasks.md` and completed-task count | PASS | 21 total, 21 complete, 0 open |
| Deliverables | `test -s` loop over the 25 files declared in `spec.md` | PASS | 25 present and non-empty |
| ASCII/LF | `validate_ascii` over `git diff --name-only "$BASE"` plus untracked files; `git diff --check "$BASE"` | PASS | 46 files clean; no CRLF or whitespace error |
| Repository gate | `./scripts/validate-changes.sh --json` | PASS | 9/9 lint, format, type, focused backend, engine, and frontend steps passed |
| Backend tests | Temporary PostgreSQL 18.4, `uv run alembic upgrade head`, and `uv run pytest tests/ -q` | PASS | All migrations applied; 180 passed; temporary container removed |
| Engine tests | `cd backend/packages/txt2crs && uv run --package txt2crs pytest -q` | PASS | 223 passed; 1 live credential gate skipped by design |
| Frontend tests | `cd frontend && npm run test:unit && npm run build` | PASS | 5 files / 18 tests passed; optimized build completed |
| Database/schema | `git diff --name-only "$BASE" -- backend/app/models.py backend/app/crud.py backend/app/alembic backend/alembic.ini` | N/A | 0 DB-layer files changed; migration apply still passed |
| Success criteria | `spec.md` criteria inspection plus test/runtime evidence below | PASS | Every listed criterion mapped to current evidence |
| Conventions | `.spec_system/CONVENTIONS.md`, nested `AGENTS.md`, Ruff, Biome, mypy, TypeScript, and ShellCheck inspection | PASS | No review-surface violation |
| Security/GDPR | `security-compliance.md`, secret scan, `npm audit --json`, path tests, Compose and image inspection | PASS | 0 open security issues; GDPR N/A |
| Behavioral quality | Targeted inspection of five high-risk deliverables plus focused/runtime tests | PASS | No violation in trust, cleanup, concurrency, failure, or contract priorities |
| UI product surface | Playwright at 1440x900 and 390x844 plus screenshot inspection | PASS | `Log in \| txt2crs`; no devtools, overlay, console problem, or interaction failure |

## 1. Code Review Gate

### Status: PASS

**Report**: `code-review.md`

**Result**: RESOLVED

**Issues**: None. The report resolves every finding across all changes since
base commit `c26350a3f60f9b841762ad7ccbf52f65c2bdcbce`.

## 2. Task Completion

### Status: PASS

**Tasks**: 21/21 complete

**Incomplete tasks**: None

## 3. Deliverables Verification

### Status: PASS

| File | Found | Status |
|------|-------|--------|
| `backend/tests/core/test_txt2crs_settings.py` | Yes | PASS |
| `backend/tests/scripts/test_container_contract.py` | Yes | PASS |
| `frontend/src/lib/branding.ts` | Yes | PASS |
| `frontend/src/lib/branding.test.ts` | Yes | PASS |
| `scripts/verify-production-baseline.sh` | Yes | PASS |
| `implementation-notes.md` | Yes | PASS |
| `backend/Dockerfile` | Yes | PASS |
| `backend/app/core/config.py` | Yes | PASS |
| `.env.example` | Yes | PASS |
| `backend/.env.example` | Yes | PASS |
| `docker-compose.yml` | Yes | PASS |
| `docker-compose.override.yml` | Yes | PASS |
| `scripts/validate-changes.sh` | Yes | PASS |
| `frontend/index.html` | Yes | PASS |
| `frontend/src/components/Common/Logo.tsx` | Yes | PASS |
| `frontend/src/components/Common/Footer.tsx` | Yes | PASS |
| `frontend/src/routes/login.tsx` | Yes | PASS |
| `frontend/src/routes/signup.tsx` | Yes | PASS |
| `frontend/src/routes/recover-password.tsx` | Yes | PASS |
| `frontend/src/routes/reset-password.tsx` | Yes | PASS |
| `frontend/src/routes/_layout/index.tsx` | Yes | PASS |
| `frontend/src/routes/_layout/items.tsx` | Yes | PASS |
| `frontend/src/routes/_layout/settings.tsx` | Yes | PASS |
| `frontend/src/routes/_layout/admin.tsx` | Yes | PASS |
| `frontend/src/routes/_layout/forbidden.tsx` | Yes | PASS |

**Missing deliverables**: None

## 4. ASCII Encoding Check

### Status: PASS

| Files | Encoding | Line Endings | Status |
|-------|----------|--------------|--------|
| All 25 declared deliverables | ASCII | LF | PASS |
| All 21 additional review/workflow files | ASCII | LF | PASS |

**Encoding issues**: None

## 5. Test Results

### Status: PASS

| Metric | Value |
|--------|-------|
| Total Tests | 422 collected |
| Passed | 421 |
| Failed | 0 |
| Skipped | 1 live credential gate |
| Coverage | N/A - coverage is not part of the configured Phase 00 gate |

**Failed tests**: None

Additional runtime checks passed for both production and development image
targets, non-root UID 1001, the one-process command, private modes, engine
import, and replacement-container state reopen.

## 6. Database/Schema Alignment

### Status: N/A

**Evidence**: The base-commit diff contains no change under
`backend/app/models.py`, `backend/app/crud.py`, `backend/app/alembic/`, or
`backend/alembic.ini`. This session configures the engine SQLite path but does
not introduce a database, table, column, index, seed, or persisted-data-shape
change. As an additional compatibility check, all existing Alembic migrations
applied to PostgreSQL 18.4 before the 180-test backend suite.

**Issues found**: None

## 7. Success Criteria

From `spec.md`:

**Functional requirements**:

- [x] Production and development targets install and import `txt2crs`.
- [x] Both image targets declare one non-root FastAPI process.
- [x] Persistent defaults resolve below `/var/lib/txt2crs`; unsafe overrides
  fail validation.
- [x] Compose mounts one state volume independently from PostgreSQL.
- [x] UID 1001 writes and reopens a private marker from a replacement
  container.
- [x] Existing login, signup, user, and item behavior passes in the full
  backend suite.

**Testing requirements**:

- [x] Settings and container contracts were recorded failing-first and now
  pass 19 and 7 tests respectively.
- [x] Shared branding has three focused tests and passes in the 18-test
  frontend suite.
- [x] Engine, backend, frontend, Compose, production, and development image
  checks pass.

**Non-functional requirements and quality gates**:

- [x] State is owner-only and runtime UID is non-zero.
- [x] Deterministic build, import, configuration, and tests require no Codex
  or Tavily credential.
- [x] Research MCP port 8765 is not published.
- [x] Session-authored files are ASCII/LF and `git diff --check` is clean.
- [x] Non-obvious path and deployment constraints have intern-facing comments.
- [x] Rendered user-facing metadata and surfaces contain product content only.

## 8. Conventions Compliance

### Status: PASS

**Categories spot-checked**: Python/TypeScript naming, root and package file
structure, shell cleanup/error behavior, explanatory comments, failing-first
tests, uv/npm lock synchronization, and shell/engine/frontend package
boundaries.

**Convention violations**: None. No generated client file or DB migration was
edited, shell routes do not duplicate engine logic, and all configured
review-surface lint, format, and type checks pass.

## 9. Security & GDPR Compliance

### Status: PASS

**Full report**: See `security-compliance.md`.

| Area | Status | Findings |
|------|--------|----------|
| Security | PASS | 0 open issues |
| GDPR | N/A | No personal-data behavior introduced or changed |

**Critical violations**: None

## 10. Behavioral Quality Spot-Check

### Status: PASS

**Checklist applied**: Yes

**Files spot-checked**:

- `backend/app/core/config.py`
- `backend/Dockerfile`
- `docker-compose.yml`
- `scripts/verify-production-baseline.sh`
- `frontend/src/routes/__root.tsx`

**Categories spot-checked**: trust-boundary validation, resource ownership and
cleanup, single-process concurrency, failure-path cleanup, configuration/image
contract alignment, and product-surface discipline.

**Violations found**: None. The code-review mount ownership and test-isolation
findings were fixed before validation.

**Fixes applied during validation**: None

## 11. UI Product-Surface Spot-Check

### Status: PASS

**Surfaces inspected**: `/login` at 1440x900 and 390x844 through local
Playwright, including title, heading, form, footer, password-reveal
interaction, console/page errors, Vite overlay, and diagnostic text.

**Diagnostics found in primary UI**: None. Both viewports reported
`Log in | txt2crs`, a visible `Welcome back` heading and sign-in control, no
TanStack/query/router diagnostic text, no Vite overlay, and no console or page
error. The password control changed from `type=password` to `type=text`.

**Allowed debug/admin surfaces**: None in the inspected primary surface.

**Fixes applied during validation**: None

## Validation Result

### PASS

All workflow, task, deliverable, encoding, test, schema, success-criteria,
convention, security, behavioral, and rendered UI gates pass.

### Unresolved Failures And Blockers

None

## Next Steps

Next command: `updateprd`
