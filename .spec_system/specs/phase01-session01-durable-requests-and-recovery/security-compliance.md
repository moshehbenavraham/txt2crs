# Security & Compliance Report

**Session ID**: `phase01-session01-durable-requests-and-recovery`
**Package**: backend/packages/txt2crs
**Reviewed**: 2026-07-19
**Result**: PASS

## Scope

**Files reviewed** (session deliverables and all other files changed since the
base commit):

- `.spec_system/PRD/PRD.md` and `.spec_system/state.json` - workflow state
- `.spec_system/PRD/phase_01/*.md` - phase/session scope and security boundaries
- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/*.md` -
  requirements, task evidence, review, and validation records
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - public exports
- `backend/packages/txt2crs/src/txt2crs/jobs/models.py` - job and identity contracts
- `backend/packages/txt2crs/src/txt2crs/jobs/quota.py` - parameterized quota reads
- `backend/packages/txt2crs/src/txt2crs/jobs/request_store.py` - request-envelope SQL
- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` - private request contract
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py` - owner/service boundary
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - transactions and owner reads
- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/003_generation_requests.sql`
  and `README_migrations.md` - versioned SQLite schema
- `backend/packages/txt2crs/tests/factories.py` - bounded deterministic fixtures
- `backend/packages/txt2crs/tests/integration/test_admission_quotas.py` - quota tests
- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` -
  consent/provider boundary tests
- `backend/packages/txt2crs/tests/integration/test_generation_request_store.py` -
  ownership, rollback, corruption, and privacy tests
- `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py` -
  migration/tenant tests
- `backend/packages/txt2crs/tests/unit/test_generation_requests.py` -
  strictness, bounds, mutation, and safe-error tests
- `backend/packages/txt2crs/tests/unit/test_job_service.py` - owner and snapshot tests

**Review method**: Static analysis of all 30 final changed files, targeted security
checklist inspection, migration/schema execution, privacy/error regression
tests, secret/log scans, and dependency-diff inspection.

**Review evidence**:

- Command/check: `git diff --name-only "$BASE"` plus
  `git ls-files --others --exclude-standard`
  - Result: PASS - 30 final session files defined the complete validation scope.
  - Evidence: No mid-session commit or staged-only file existed outside that
    inventory.
- Command/check: changed-file regex scan for API keys, passwords, OpenAI key
  formats, logging calls, debug prints, CR characters, and non-ASCII bytes
  - Result: PASS - no credential, raw-input log, debug output, CR, or non-ASCII
    match was found.
  - Evidence: All 30 files report `us-ascii`; request/store production files
    contain no logger or print call.
- Command/check: `git diff --name-only "$BASE" -- backend/pyproject.toml
  backend/uv.lock frontend/package.json frontend/package-lock.json`
  - Result: N/A - no dependency manifest or lockfile changed.
  - Evidence: The command returned no files, so this session introduced no
    dependency to audit.
- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS - 274 deterministic tests passed; one credential-gated live
    provider test skipped by its explicit environment gate.
  - Evidence: Ownership, exact replay, concurrent duplicate submission,
    rollback, corruption, consent rejection, and safe exception-context tests
    are included.

## Security Assessment

### Overall: PASS

| Category | Status | Severity | Details |
|----------|--------|----------|---------|
| Injection (SQLi, CMDi, LDAPi) | PASS | -- | All runtime SQL uses placeholders; migration SQL is static; no shell, LDAP, or command construction was added. |
| Hardcoded Secrets | PASS | -- | No credentials, tokens, API keys, passwords, or connection strings were added. |
| Sensitive Data Exposure | PASS | -- | Raw input stays in owner-private SQLite; public errors suppress validation cause/context; no input, request JSON, path, provider payload, or credential is logged. |
| Insecure Dependencies | PASS | -- | No manifest or lockfile changed. |
| Security Misconfiguration | PASS | -- | No CORS, debug mode, headers, deployment settings, or network listener changed. |
| Database Security | PASS | -- | Owner filters and parameterized queries guard reads; `BEGIN IMMEDIATE` and rollback guard writes; request rows cascade with jobs; finite raw/metadata/token bounds apply before acceptance. |

### Security Findings

No unresolved security findings. The preceding `creview` gate found and fixed:

- sensitive validation error cause/context retention;
- non-finite, non-exact, and unbounded metadata;
- token reservations smaller than executable run limits; and
- invalid owner/idempotency values committing before validation.

Each repair has a targeted regression test and is recorded in
`code-review.md`.

## GDPR Compliance Assessment

### Overall: PASS

**Categories reviewed**: Data Collection & Purpose, Consent Mechanism, Data
Minimization, Right to Erasure, PII in Logs, Third-Party Data Transfers.

### Personal Data Inventory

| Data Element | Source | Storage | Purpose | Retention | Deletion Path |
|-------------|--------|---------|---------|-----------|---------------|
| Pseudonymous owner ID | Authenticated shell caller in later composition | `jobs`, `generation_requests`, and `job_admissions` in private engine SQLite | Tenant authorization, idempotency, quota, and recovery | Engine-state lifetime pending the documented retention policy | Session 05 owner purge; request/admission rows already cascade with the job |
| Raw text or bounded binary input | Learner request | Type-tagged canonical JSON in `generation_requests.request_json` | Generate and exactly recover the requested course | Engine-state lifetime pending owner purge | Session 05 owner purge plus `ON DELETE CASCADE` |
| File display metadata and normalized request metadata | Learner transport/request | `generation_requests.request_json` | Correct ingestion routing and exact recovery | Same as the request | Session 05 owner purge plus cascade |
| Audience, prior knowledge, learning goals, language, and level intent | Learner request | `generation_requests.request_json` | Course personalization | Same as the request | Session 05 owner purge plus cascade |
| Coarse age group and provider consent | Learner request | `generation_requests.request_json` | Policy enforcement without collecting a birth date | Same as the request | Session 05 owner purge plus cascade |

### GDPR Findings

No GDPR findings within this session's scope.

- Data collection has the documented course-generation and recovery purpose.
- Age is minimized to `minor`, `adult`, or `not_provided`; no birth date is
  collected.
- Provider consent is stored as policy context. This session adds no provider
  transfer, and the existing executor test proves false consent reaches no
  model or research work. Session 03 owns the earlier submission preflight.
- No PII or learner content enters logs or package-facing errors.
- No new third-party sharing, analytics, email, or network behavior exists.
- Right-to-erasure implementation is an explicit Session 05 deliverable; the
  new schema already provides job-cascade deletion semantics.

## Recommendations

- Session 03 must enforce provider consent and content policy before new job
  admission, as already specified.
- Session 05 must complete and test idempotent owner purge across SQLite and
  artifact storage.
- The later application/privacy documentation should set an operator-visible
  retention period for private engine state.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (`validate`)
- **Date**: 2026-07-19
