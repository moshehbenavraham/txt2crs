# Code Review and Repair Report

**Session ID**: `phase02-session04-system-readiness-and-auth-api`
**Package**: backend
**Reviewed**: 2026-07-19
**Base Commit**: `470b2609dc9701c9eae28a5db8cfe30c1f2faef8`
**Implementation Commit**: `ffc97da`
**Scope**: Complete base-to-implementation diff plus review repairs
**Result**: RESOLVED

## Review Surface

The exact base-to-head surface was reviewed across:

- Public package authentication exports and their import boundary.
- Lifespan construction, startup, app-state exposure, and reverse cleanup.
- Shared runtime ownership across readiness, execution, and authentication.
- Initial persisted-account refresh and the finite cache monitor.
- Strict readiness and authentication response projections.
- Authentication, superuser authorization, rate limits, and RFC 9457 routes.
- Semantic package-error translation and exception-chain removal.
- Generated OpenAPI/TypeScript contracts and public API documentation.
- Focused and complete engine/shell tests.
- Apex planning, implementation, review, and state records.

The review emphasized authentication authorization, cache-only GET behavior,
lease lifetime, startup/shutdown races, partial-startup behavior, URL/code
allowlists, provider-detail isolation, bounded resources, generated-client
ownership, and package/shell separation.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `backend/app/main.py` - Authentication cleanup originally ran before the
  readiness coordinator stopped. Releasing an active authentication lease
  could therefore allow the still-live readiness thread to acquire the
  provider runtime before facade cleanup cancelled the package ceremony. |
  Fix: Start authentication before readiness and the worker; close the worker
  and readiness before authentication, the gate, and the facade. A lifespan
  regression protects the complete order. | Status: FIXED
- `backend/app/api/routes/system.py` - Raising a translated `AppException`
  inside the package-error handler let Python retain the private provider
  exception as `__context__`, even with `raise ... from None`. | Fix: Save the
  translated safe error and raise it only after leaving the `except` scope.
  Error tests verify the public response and cleared exception chain. |
  Status: FIXED

### Low

- `backend/app/services/txt2crs_authentication.py` - A direct call to
  `start_authentication()` before lifecycle `start()` could acquire and retain
  the authentication lease without a monitor thread to observe terminal
  completion. | Fix: Reject pre-lifecycle calls before package or gate access.
  A regression verifies no package call and an immediately available runtime.
  | Status: FIXED
- `backend/app/services/txt2crs_authentication.py` - If another runtime owner
  prevented the initial persisted-account refresh, the default cache remained
  `signed_out`, which falsely implied a confirmed account state. | Fix:
  Publish a challenge-free `failed` snapshot with a generic temporary-
  unavailability message. A contention regression verifies no package call
  and the exact safe state. | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- Device-auth logout remains the documented P1 follow-up.
- Learner job and artifact routes remain Phase 04 scope.
- The browser setup experience remains Session 05 scope.
- The pinned Codex SDK does not expose device-code expiry, so the API does not
  invent a deadline.
- GET status performs no credential refresh. Persisted-account refresh remains
  a single lifecycle action so browser polling cannot start provider work.
- The host port 5447 collision belongs to an unrelated container. Validation
  uses the project's PostgreSQL container private address without changing
  the other container.
- The exact GPT-5.6/Tavily live proof remains credential-gated for release
  validation.

## Behavior Changes

- Any active authenticated user can read a detached coarse readiness cache.
- Only an active superuser can start or inspect a device-code ceremony.
- Device start retains one authentication lease until terminal state,
  package failure, or lifecycle close.
- Repeated waiting/authenticated starts replay safe cached state.
- Readiness and authentication GETs do not invoke package, provider,
  credential, storage, or runtime-gate work.
- Unconfigured, busy, closed, and package failures map to stable RFC 9457
  errors without private exception detail.
- Responses expose only reviewed readiness fields or finite auth state, the
  validated OpenAI URL, bounded user code, and safe message.

## Security And Compliance Review

| Area | Result | Evidence |
|------|--------|----------|
| Authentication/authorization | PASS | Readiness requires an active user; both auth routes require a current superuser before service access |
| Input/output validation | PASS | Frozen extra-forbid responses enforce finite enums, bounded collections/text/code, aware time, reviewed model/input values, and the approved OpenAI HTTPS host |
| Injection | PASS | No raw SQL, shell, subprocess, template, unsafe deserialization, redirect, or dynamic execution surface was added |
| Secrets | PASS | No OAuth token, account identity, key, provider payload, path, port, or credential value enters the response or logs |
| Data exposure | PASS | Route projections use explicit allowlists; translated errors sever cause/context and use generic details |
| Resource safety | PASS | One monitor, one retained lease, non-blocking contention, finite polling/shutdown, and idempotent cleanup are tested |
| Error handling | PASS | Semantic error codes and RFC 9457 handlers cover unavailable, busy, package-failed, unauthorized, and rate-limited paths |
| Dependencies | PASS | No dependency manifest, package lock, or third-party version changed |
| Database | PASS | No application schema, query, migration, or engine persistence behavior changed |
| GDPR | PASS | No new personal-data field, durable processing purpose, transfer, retention, or erasure path was introduced |

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first review regressions | Focused authentication service and lifespan/error cases | PASS | Cleanup order, detached errors, pre-start rejection, and busy-initial state are protected |
| Focused authentication service | `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/services/test_txt2crs_authentication.py -q` | PASS | 9 passed |
| Shell static checks | Ruff, strict mypy, and ty | PASS | All shell checks passed |
| Added-line security scan | Diff scan plus manual trust-boundary inspection | PASS | No secret assignment, command execution, unsafe query, or private provider projection |
| Dependency/schema inventory | Base-to-head filename and manifest inspection | PASS | No dependency or Alembic change |
| Patch integrity | `git diff --check "$BASE"` | PASS | No whitespace defect |
| Complete validation | Session `validate` matrix | PASS | 760 deterministic tests, static/frontend/client gates, pre-commit, ASCII/LF, and diff integrity passed |

## Summary

1. Reviewed the complete base-to-implementation surface.
2. Found 0 critical, 0 high, 2 medium, and 2 low issues.
3. Repaired all four findings with focused regressions.
4. Focused tests and shell static gates pass.
5. No unresolved code, security, privacy, or workflow finding remains.

Next command: `validate`
