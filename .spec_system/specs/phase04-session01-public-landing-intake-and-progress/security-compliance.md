# Security & Compliance Report

**Session ID**: `phase04-session01-public-landing-intake-and-progress`
**Package**: cross-cutting (`backend`, `backend/packages/txt2crs`, `frontend`)
**Reviewed**: 2026-07-20
**Result**: PASS

## Scope

**Files reviewed**:

- All 45 declared deliverables from `spec.md` - public/auth routes, intake,
  progress, validation, submission, polling, deterministic test composition,
  browser journeys, Compose/build configuration, generated route ownership,
  and current documentation
- `frontend/src/components/Landing/`, `CourseIntake/`, and `CourseProgress/` -
  personal-data, consent, safe-copy, and product-surface boundaries
- `frontend/src/lib/course-draft.ts`, `schemas/fields.ts`, and
  `schemas/job.ts` - bounded browser persistence and trust-boundary validation
- `frontend/src/hooks/useCourseSubmission.ts` and progress `queries.ts` -
  generated-client transport, idempotency, owner reads, retry, and safe errors
- `backend/tests/browser/` and `frontend/playwright.jobs.config.ts` -
  test-only isolation, environment inputs, state ownership, and cleanup
- Session-created/modified documentation and configuration - public settings,
  third-party processing claims, retention caveats, and secret guidance

**Review method**: Targeted static review of session-created/modified files,
final deterministic tests, browser/resource inspection, and dependency-delta
inspection using the Apex security/GDPR checklist.

**Review evidence**:

- Command/check: high-confidence secret-pattern scan over all active
  changed/new files
  - Result: PASS
  - Evidence: 0 files matched AWS, OpenAI, GitHub, or private-key patterns.
- Command/check:
  `git diff --name-only "$BASE" -- backend/pyproject.toml backend/uv.lock frontend/package.json frontend/package-lock.json`
  - Result: N/A
  - Evidence: 0 dependency manifest or lockfile changes; no new dependency
    advisory surface was introduced.
- Command/check: production/test boundary search plus
  `test_production_route_graph_has_no_browser_fixture_controls`
  - Result: PASS
  - Evidence: 0 test-only imports or fixture flags in `backend/app` or
    `frontend/src`; production OpenAPI has no `/__test__` path.
- Command/check: touched-feature searches for `dangerouslySetInnerHTML`,
  `eval`, direct `fetch`/Axios, course-source `localStorage` writes, debug
  statements, private paths, tokens, provider payloads, and stack traces
  - Result: PASS
  - Evidence: every reviewed count was 0.
- Command/check: final complete/failed isolated Playwright scenarios plus
  PostgreSQL `/tmp`/process inspection
  - Result: PASS
  - Evidence: each scenario passed 15 tests with 1 intentional skip; afterward
    there were 0 browser users, 0 temporary browser roots, and 0 test server
    listeners.
- Command/check: `git diff --check "$BASE"`, ASCII/CR scans, generated-client
  reproduction, and repository hooks over every changed/explicit new file
  - Result: PASS
  - Evidence: no source-hygiene, generated-contract, static-analysis, or hook
    violation.

## Security Assessment

### Overall: PASS

| Category | Status | Severity | Details |
|----------|--------|----------|---------|
| Injection (SQLi, CMDi, LDAPi) | PASS | -- | Session application code uses centralized Zod and generated services. No raw SQL, shell interpolation, dynamic evaluation, or HTML injection was introduced. Test server commands are fixed strings and variable values are passed through environment maps. |
| Hardcoded Secrets | PASS | -- | No secret pattern is present. `VITE_*` values are documented as public. The finite `Browser-only-123!` value is a non-production disposable test credential for a unique user removed by teardown, not a deployed secret. |
| Sensitive Data Exposure | PASS | -- | Source bodies are absent from URLs, logs, query keys, errors, and localStorage. Upload preview reads metadata only. Public errors remain bounded and owner reads use the authenticated generated endpoint. |
| Insecure Dependencies | N/A | -- | No Python or JavaScript manifest/lockfile changed. |
| Security Misconfiguration | PASS | -- | Public signup defaults false and is display-only; backend authorization remains authoritative. The deterministic app requires an explicit test flag, private fresh state, and has no production route. Remote fonts were removed to preserve the restrictive CSP. |
| Database Security | PASS | -- | No DB schema/query code changed. Browser users are created through normal APIs and deleted through the account-purge API; test residue count is zero. |

### Security Findings

No unresolved security findings. The code-review path-ownership, cleanup, and
warning-boundary findings were repaired before validation and have focused
regressions.

## GDPR Compliance Assessment

### Overall: PASS

**Categories reviewed**: Data Collection & Purpose, Consent Mechanism, Data
Minimization, Right to Erasure, PII in Logs, Third-Party Data Transfers.

### Personal Data Inventory

| Data Element | Source | Storage | Purpose | Retention | Deletion Path |
|-------------|--------|---------|---------|-----------|---------------|
| Optional bounded topic draft | Learner on public `/` | Browser `sessionStorage` in one versioned envelope | Carry the learner's explicit draft through sign-in | Consumed once at `/create`, cleared on invalid data, or ends with the browser tab/session | `consumeCoursePromptDraft()` and `clearCoursePromptDraft()` |
| Course source and learning intent | Learner at `/create` | Form memory, then owner-scoped server/engine job state after exact consent | Generate the requested course package | Governed by the configured installation and providers; the UI makes no broader retention promise | Existing authenticated `DELETE /api/v1/users/me` purges owner engine state and identity |
| Coarse learner age group | Learner at `/create` | Owner-scoped job request | Apply age-aware language and safeguards | Same as the owner job | Existing account deletion path |
| Authentication email/token | Existing auth flow | PostgreSQL email plus existing session-scoped browser token handling | Authenticate and authorize private routes | Existing account/session lifecycle | Existing logout and authenticated account deletion |

### GDPR Findings

No GDPR findings.

- Data collection has a product purpose and optional fields remain optional.
- Age is minimized to `minor`, `adult`, or `not_provided`; no birth date is
  collected.
- The topic handoff occurs only after an explicit save action and stays in
  tab-scoped browser storage. AI/research processing requires literal boolean
  `true` before submission.
- Landing/intake copy states that configured AI/research services may process
  the source after consent without promising unsupported provider privacy,
  retention, regulation, or compliance guarantees.
- Source/intent/age content is excluded from application logs, query keys,
  learner errors, and test reports.
- Existing coordinated account erasure remains the deletion path and is also
  exercised by browser teardown.

## Recommendations

- Session 02 should preserve the same owner-only and bounded-copy rules when
  it adds result, source/conflict, manifest, preview, and download surfaces.
- Deployment-specific privacy/retention language should remain operator-owned;
  do not turn this implementation report into a regulatory guarantee.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (`validate`)
- **Date**: 2026-07-20
