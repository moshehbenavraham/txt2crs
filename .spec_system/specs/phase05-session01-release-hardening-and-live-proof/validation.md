# Validation Report

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Package**: null (cross-cutting monorepo)
**Validated**: 2026-07-20
**Result**: PASS

## Validation Summary

| Check | Status | Notes |
|-------|--------|-------|
| Code Review | PASS | `code-review.md` is `RESOLVED` and covers all 445 paths since the exact base, including the validation follow-up repair. |
| Tasks Complete | PASS | 25/25 implementation tasks are checked. |
| Files Exist | PASS | 18/18 specified deliverables exist and are non-empty. |
| ASCII Encoding | PASS | All 18 deliverables and all 444 current regular changed files are ASCII with LF endings; one changed path is intentionally deleted. |
| Tests Passing | PASS | Engine 489, backend 517, frontend 132, and both 16-test deterministic browser scenarios pass; only explicit live/opposite-scenario skips remain. |
| Database/Schema Alignment | N/A | No persisted data shape or migration changed; a fresh PostgreSQL 18 migration apply reaches Alembic head. |
| Success Criteria | PASS | Release, deterministic, production, live-proof, privacy, evidence, and Session 02 handoff criteria have direct evidence. |
| Conventions | PASS | Naming, package boundaries, comments, typed errors, tests-first repairs, generated-client ownership, resource cleanup, and module size comply. |
| Security & GDPR | PASS | Security passes with no unresolved finding; GDPR is N/A because no new personal-data handling was introduced. |
| Behavioral Quality | PASS | Five highest-risk application/tool files have no priority violation. |
| UI Product Surface | PASS | No production UI component changed; current build and deterministic learner journeys remain free of banned diagnostics. |

**Overall**: PASS

## Evidence Ledger

Every row names the exact command or targeted inspection used.

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Project state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Phase 5, current Session 01, monorepo true, cross-cutting package context, and both Phase 05 sessions discovered. |
| Code review | `code-review.md` inspection plus `git diff "$BASE" HEAD` inventory | PASS | Result is exactly `RESOLVED`; 0 critical, 3 high, 6 medium, and 4 low findings are all fixed. |
| Task completion | `rg` count over task IDs in `tasks.md` | PASS | 25/25 task IDs are `[x]`; no task is incomplete. |
| Deliverables | explicit 18-path `test -f`/`test -s` loop from the `spec.md` tables | PASS | 18/18 files exist and are non-empty. |
| ASCII/LF | `file`, `LC_ALL=C grep '[^[:print:][:space:]]'`, and `grep $'\r'` over deliverables and all base-to-HEAD current files | PASS | 18/18 deliverables and 444/444 current regular changed paths are ASCII/LF; the one absent path is a deleted old fixture. |
| Engine suite | `cd backend/packages/txt2crs && uv run --package txt2crs pytest -q && ... ruff format --check . && ... ruff check . && ... mypy` | PASS | 489 passed, 2 explicit live skips, 138 files formatted, lint clean, and strict mypy clean for 138 source files. |
| Backend suite | fresh PostgreSQL 18 plus `cd backend && uv run alembic upgrade head && uv run pytest tests/ -q && uv run ruff ... && uv run mypy app` with isolated settings | PASS | Alembic reached `a7d9c2e4f601` head; 517 passed; 111 files formatted; lint clean; strict mypy clean for 47 source files. |
| Frontend suite | `cd frontend && npm run test:unit && npm run lint && npm run typecheck && npm run build` | PASS | 20 files/132 tests, 158 Biome files, strict TypeScript, and 2,215 production modules pass. |
| Repository gate | `./scripts/validate-changes.sh --json` | PASS | 9/9 backend, engine, and frontend steps pass after the validation repair. |
| Browser acceptance | `TXT2CRS_BROWSER_SCENARIO=complete` and `failed` with `npx playwright test --config=playwright.jobs.config.ts` | PASS | Each scenario passes 16 tests with one explicit opposite-scenario skip; setup, submission, refresh, publications, failure recovery, accessibility, and owner cleanup pass. |
| Focused trust boundaries | 33 release/workflow/auth tests, 6 runtime/auth/pipeline tests, and 1 worker startup test | PASS | Exact evidence fields, redaction, fixed credential state, schema fallback, bounded repair, and operational startup barrier pass. |
| Database/schema | `git diff --name-only "$BASE" HEAD -- backend/app/models.py backend/app/alembic backend/packages/txt2crs/src/txt2crs/persistence backend/packages/txt2crs/src/txt2crs/storage` plus fresh migration apply | N/A | No persisted-shape artifact changed; the existing migration chain applies cleanly to fresh PostgreSQL 18. |
| Release identity | `python scripts/release_evidence.py validate-repository ... --mode candidate --revision a807...` | PASS | Version surfaces are synchronized at `1.0.0`; candidate mode is tag-free and `v1.0.0` remains absent. |
| Public evidence | `validate-evidence` to a temporary file, `cmp`, and `sha256sum` | PASS | Sixteen unique pairs and six PASS dimensions validate; canonical bytes match hash `43e811...bbbd`. |
| Historical live proof | candidate JSON, artifact ledger, implementation notes, and focused live acceptance result inspection | PASS | Exact Sol, real Tavily, 258 seconds, 6 sources/excerpts/usages, 9 checkpoints, 4 publications, and 16 inspected private artifacts are recorded without raw bodies. |
| Exact-head distributions | `uv build --package txt2crs` to a temporary directory plus wheel/tar metadata inspection | PASS | At `72afd23`, wheel `447e85e...98071` and sdist `976b023...01c4` identify `1.0.0` and include license, package README, and metadata. |
| Exact-head images | labeled production `docker build` for backend/frontend plus `docker image inspect` and transient runtime checks | PASS | At `72afd23`, backend `f66a049...e5b0` is non-root, one-process, healthy, package `1.0.0`, and contains all three email templates; frontend `e7b0d08...b7ea` contains the built app and healthcheck. |
| Dependency security | `uv run --with pip-audit pip-audit` and `npm audit --audit-level=high` | PASS | No known Python vulnerability and zero npm vulnerabilities; local packages are expected non-PyPI skips. |
| Workflow/shell security | `actionlint`, `zizmor --pedantic`, `bash -n`, and `shellcheck` | PASS | All ten workflows and both changed helpers pass; Zizmor's normal offline-mode notice is non-failing. |
| Secret/privacy scan | full-diff redacted Gitleaks scan plus public-release risky-pattern scan | PASS | No secret or private public-evidence value found. |
| Success criteria | `spec.md` criteria cross-referenced with every evidence row above | PASS | All release, deterministic/production, live, and handoff criteria are proven at their declared historical or exact-head boundary. |
| Conventions | targeted inspection against `.spec_system/CONVENTIONS.md` | PASS | Engine/shell/frontend ownership, typed boundaries, descriptive naming, intern-oriented comments, tests-first history, and cleanup comply. |
| Behavioral quality | priority checklist applied to `release_contract.py`, `codex_runtime.py`, `system_authentication.py`, `pipeline.py`, and `txt2crs_worker.py` | PASS | Trust validation, cleanup, mutation/concurrency safety, failure paths, and contracts are explicit and tested. |
| UI product surface | UI checklist plus current frontend build and deterministic learner journeys | PASS | No normal product route shows debug labels, readiness badges, package/version labels, viewport readouts, or scaffolding. |
| Resource/diff hygiene | resource removal checks, `ss` for validation ports, `git diff --check`, and `git status --short` | PASS | Disposable databases, images, browser state, and listeners are removed; diff hygiene passes. |

## 1. Code Review Gate

### Status: PASS

**Report**: `code-review.md`

**Result**: RESOLVED

**Issues**: None. The report covers the complete base-to-HEAD session surface.
Its final follow-up records the validation-discovered Unicode source issue as
the fourth low finding and proves the ASCII-preserving repair.

## 2. Task Completion

### Status: PASS

**Tasks**: 25/25 complete

**Incomplete tasks**: None

## 3. Deliverables Verification

### Status: PASS

| File | Found | Status |
|------|-------|--------|
| `scripts/release_evidence.py` | Yes | PASS |
| `backend/tests/scripts/test_release_evidence.py` | Yes | PASS |
| `backend/tests/scripts/test_release_workflow_contract.py` | Yes | PASS |
| `docs/release/README_release.md` | Yes | PASS |
| `docs/release/RELEASE_CANDIDATE_1_0_0.json` | Yes | PASS |
| `docs/release/ARTIFACT_INSPECTION_1_0_0.md` | Yes | PASS |
| `docs/release/DETERMINISTIC_SAMPLE_1_0_0.md` | Yes | PASS |
| `.github/workflows/release.yml` | Yes | PASS |
| `.gitignore` | Yes | PASS |
| `VERSION` | Yes | PASS |
| `backend/packages/txt2crs/pyproject.toml` | Yes | PASS |
| `backend/uv.lock` | Yes | PASS |
| `docs/VERSIONING.md` | Yes | PASS |
| `docs/CHANGELOG.md` | Yes | PASS |
| `backend/packages/txt2crs/tests/acceptance/README_acceptance.md` | Yes | PASS |
| `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` | Yes | PASS |
| `.spec_system/PRD/PRD.md` | Yes | PASS |
| `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md` | Yes | PASS |

**Missing deliverables**: None

The session is intentionally cross-cutting (`Package: null`), so these
repo-root, engine, shell, and workflow paths are all within declared scope.

## 4. ASCII Encoding Check

### Status: PASS

| Scope | Encoding | Line Endings | Status |
|-------|----------|--------------|--------|
| 18 specified deliverables | ASCII | LF | PASS |
| 444 current regular base-to-HEAD changed files | ASCII | LF | PASS |
| 1 deleted compatibility fixture | N/A | N/A | PASS |

**Encoding issues**: None. Validation repaired three base-existing Unicode
representations in session-touched files. Runtime em-dash and Hebrew behavior
is preserved through ASCII `\u` escapes; 21 focused rendering tests pass.

## 5. Test Results

### Status: PASS

| Suite | Passed | Failed | Skipped |
|-------|--------|--------|---------|
| Engine pytest | 489 | 0 | 2 explicit live gates |
| Backend pytest | 517 | 0 | 0 |
| Frontend Vitest | 132 | 0 | 0 |
| Completed deterministic Playwright | 16 | 0 | 1 opposite scenario |
| Failed deterministic Playwright | 16 | 0 | 1 opposite scenario |

**Coverage**: Not collected; the session specification defines functional,
scenario, security, and release evidence rather than a numeric threshold.

**Failed tests**: None

The backend warnings are known local test-key and third-party deprecation
notices. Non-local secret-strength tests pass, and no warning represents a
failed product contract.

## 6. Database/Schema Alignment

### Status: N/A

**Evidence**: The targeted base-to-HEAD diff contains no PostgreSQL model,
Alembic migration, engine persistence schema, or store-shape change. A fresh
PostgreSQL 18 database nevertheless applied every migration and reported
`a7d9c2e4f601 (head)` before the full backend suite.

**Issues found**: None

## 7. Success Criteria

From `spec.md`:

### Release Contract

- [x] Tests-first negative cases cover version drift, malformed hashes,
      artifact-count drift, incomplete inspection, unsafe fields,
      nondeterminism, candidate tags, and mismatched final tags.
- [x] Repository/package/lock/docs/changelog, exact-head distributions, both
      exact-head images, and bounded candidate evidence identify `1.0.0`.
- [x] The release workflow is pinned, read-only, nonpublishing,
      local-deployment-only, and calls the shared validator.

### Deterministic And Production Proof

- [x] Engine, backend, frontend, generated contracts, evaluation, acceptance,
      browser, hook, security, distribution, and documentation gates pass.
- [x] Exact-head images have healthchecks; backend runs as `appuser` with one
      FastAPI process and all required email templates.
- [x] The recorded isolated replacement proof preserves PostgreSQL identity,
      engine private state, and verified private artifacts.

### Live Proof

- [x] One canonical synthetic job used exact `gpt-5.6-sol` without fallback
      and real Tavily research before drafting.
- [x] All four publications and all sixteen format pairs pass alignment,
      citation, formatting, integrity, private-access, and answer-separation
      review.
- [x] Public evidence and the complete session diff contain no credential,
      prompt, provider payload, raw artifact body, private identifier, or
      public local path.

### Handoff

- [x] Deterministic sample and canonical live ledger are reproducible and
      judge-safe.
- [x] Implementation notes record exact historical live revision/evidence,
      current reviewed deterministic proof, external CodeQL exception, and
      cleanup.
- [x] Session 02 has an explicit final-link/build/health/replacement/tag/push
      revalidation list and remains the sole owner of `v1.0.0`.

The public candidate ledger remains an honest historical record of the paid
live run at `a807008...`; it is not relabeled as if later review repairs
received that provider execution. Exact-head deterministic builds at
`72afd23...` pass. Session 02 must rebuild its final tracked commit and record
new build hashes before tagging.

## 8. Conventions Compliance

### Status: PASS

**Categories spot-checked**: naming, package/file structure, error handling,
comments, tests-first implementation, generated-client ownership, database
conventions, resource cleanup, and logging.

**Convention violations**: None. Runtime orchestration stays in the engine,
the shell consumes the public facade, generated frontend files come from the
authoritative wrapper, errors remain bounded/typed, and comments explain
security and lifecycle decisions for a first-year intern.

## 9. Security & GDPR Compliance

### Status: PASS

**Full report**: See `security-compliance.md` in this session directory.

| Area | Status | Findings |
|------|--------|----------|
| Security | PASS | 0 unresolved issues |
| GDPR | N/A | No new production personal-data handling |

**Critical violations**: None

## 10. Behavioral Quality Spot-Check

### Status: PASS

**Checklist applied**: Yes

**Files spot-checked**:

- `scripts/release_contract.py`
- `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py`
- `backend/packages/txt2crs/src/txt2crs/ai/system_authentication.py`
- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`
- `backend/app/services/txt2crs_worker.py`

**Categories spot-checked**: trust boundaries, resource cleanup, mutation and
concurrency safety, failure paths, external dependency bounds, and contract
alignment.

**Violations found**: None. Release evidence rejects unknown/private fields;
provider schemas retain local Pydantic validation; auth clients close across
all paths; pipeline repairs are budgeted and finite; the worker startup wait
is bounded and publishes an operational snapshot before accepting work.

**Fixes applied during validation**: Re-encoded three session-touched files as
ASCII without changing runtime Unicode output. The review report records and
resolves this low finding.

## 11. UI Product-Surface Spot-Check

### Status: PASS

**Surfaces inspected**: Current production frontend build plus deterministic
public landing, intake, progress, results, missing/foreign job, failed job,
mobile, keyboard, contrast, and cleanup journeys.

**Diagnostics found in primary UI**: None

**Allowed debug/admin surfaces**: Existing separate administrator and
operator-setup routes only; this session added no debug surface.

**Fixes applied during validation**: None

## Validation Result

### PASS

All workflow, task, deliverable, encoding, test, schema-scope, release,
production, live-proof, security/privacy, behavioral, and product-surface
checks pass.

### Unresolved Failures And Blockers

None

The hosted CodeQL billing rejection is a documented low external exception,
not a hidden passing claim. It does not block this locally validated session.

## Next Steps

Next command: `updateprd`

Reason: every validation check passed and the session is ready to be marked
complete.
