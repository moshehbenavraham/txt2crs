# Security & Compliance Report

**Session ID**: `phase01-session03-input-preferences-and-policy-gate`
**Package**: backend/packages/txt2crs
**Reviewed**: 2026-07-19
**Result**: PASS

## Scope

**Files reviewed** (all 23 package files created or modified by this session):

- `backend/packages/txt2crs/src/txt2crs/generation/__init__.py`
- `backend/packages/txt2crs/src/txt2crs/generation/models.py`
- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`
- `backend/packages/txt2crs/src/txt2crs/generation/preferences.py`
- `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py`
- `backend/packages/txt2crs/src/txt2crs/ingestion/routing_url.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/preparation.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py`
- `backend/packages/txt2crs/src/txt2crs/security/policy.py`
- `backend/packages/txt2crs/tests/factories.py`
- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
- `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py`
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
- `backend/packages/txt2crs/tests/unit/test_content_policy.py`
- `backend/packages/txt2crs/tests/unit/test_generation_preparation.py`
- `backend/packages/txt2crs/tests/unit/test_generation_requests.py`
- `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py`
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py`
- `backend/packages/txt2crs/tests/unit/test_public_package_exports.py`
- `backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py`

**Review method**: Static analysis of the exact package diff and untracked
package files, targeted trust-boundary inspection, dependency-diff inspection,
and the complete credential-free package test suite.

**Review evidence**:

- Command/check: `{ git diff --name-only "$BASE" -- backend/packages/txt2crs; git ls-files --others --exclude-standard backend/packages/txt2crs; } | sort -u`
  - Result: PASS
  - Evidence: The targeted package scope contains 23 modified or new files.
- Command/check: `git diff --name-only "$BASE" -- backend/packages/txt2crs/pyproject.toml backend/uv.lock`
  - Result: PASS
  - Evidence: No package manifest or lockfile changed.
- Command/check: scoped `rg` scans for credential assignments, shell
  execution, raw SQL, debug markers, and logging calls across the 23 files.
  - Result: PASS
  - Evidence: No credential assignment, raw SQL, production shell execution,
    debug call, or logging call exists. The only process API is a fixed-argument
    clean-import regression in `test_public_package_exports.py`.
- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS
  - Evidence: 359 deterministic tests passed, one explicitly credential-gated
    live subscription test skipped, and zero tests failed.
- Targeted inspection: `security/policy.py:46-184`,
  `jobs/preparation.py:33-167`, `jobs/executor.py:78-351`,
  `jobs/public_queries.py:190-425`, and `ingestion/routing_url.py:37-70`.
  - Result: PASS
  - Evidence: Strict inputs, bounded content, two-stage consent/policy gates,
    request/checkpoint identity checks, terminal failure settlement, exact URL
    routing, and public allowlisting are enforced before side effects.

## Security Assessment

### Overall: PASS

| Category | Status | Severity | Details |
|----------|--------|----------|---------|
| Injection (SQLi, CMDi, LDAPi) | PASS | -- | No production query, command, LDAP, template-evaluation, or shell boundary was added. |
| Hardcoded Secrets | PASS | -- | The scoped credential-assignment scan found no embedded key, token, password, or private key. |
| Sensitive Data Exposure | PASS | -- | Safe fixed errors and an explicit public projection keep normalized content, request hashes, policy state, preferences, usage, and provider values private. |
| Insecure Dependencies | PASS | -- | No manifest or lockfile changed in this session. |
| Security Misconfiguration | PASS | -- | No CORS, debug mode, header, deployment, authentication, or configuration surface changed. |
| Database Security | PASS | -- | No SQL or connection configuration changed; durable JSON remains behind the existing tenant-scoped SQLite store. |

### Security Findings

No security findings.

## GDPR Compliance Assessment

### Overall: PASS

**Categories reviewed**: Data Collection & Purpose, Consent Mechanism, Data
Minimization, Right to Erasure, PII in Logs, Third-Party Data Transfers.

### Personal Data Inventory

| Data Element | Source | Storage | Purpose | Retention | Deletion Path |
|-------------|--------|---------|---------|-----------|---------------|
| Submitted source transport and normalized educational content | User submission and selected ingestion adapter | Tenant-scoped SQLite request/checkpoint JSON | Build the requested course and resume without refetching | Generation-job lifetime | Owner-wide purge is the explicit Phase 01 Session 05 lifecycle deliverable |
| Learner age group | User request | Tenant-scoped SQLite request JSON | Apply age-appropriate content policy | Generation-job lifetime | Owner-wide purge is the explicit Phase 01 Session 05 lifecycle deliverable |
| Provider consent | User request | Tenant-scoped SQLite request JSON | Prove provider processing is authorized before ingestion/provider work | Generation-job lifetime | Owner-wide purge is the explicit Phase 01 Session 05 lifecycle deliverable |
| Learning preference intent and resolved preferences | User request plus accepted local course plan | Tenant-scoped SQLite request/checkpoint JSON | Produce and resume the requested learning contract deterministically | Generation-job lifetime | Owner-wide purge is the explicit Phase 01 Session 05 lifecycle deliverable |

### GDPR Findings

No GDPR findings.

- Data collection has the documented course-generation and recovery purpose.
- Consent is checked before ingestion and before any provider-backed pipeline
  can be constructed.
- Exact age is not collected by this boundary; the policy stores only the
  privacy-minimized `LearnerAgeGroup`.
- Public projection and safe errors do not expose normalized source content,
  private policy state, preferences, or request hashes.
- The scoped source contains no logging calls, so this session adds no PII log
  path.
- Provider transfer is consent-gated. This session persists accepted
  preparation before later provider work and does not add a new provider.
- The session specification explicitly assigns owner-wide deletion to Phase 01
  Session 05, satisfying the checklist requirement to document the future
  erasure path while keeping lifecycle work out of this session.

## Recommendations

Complete the owner-wide purge operation in Phase 01 Session 05 and retain
end-to-end tests proving request JSON, checkpoint JSON, artifacts, and
provider-owned state are all deleted for the owner.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (validate)
- **Date**: 2026-07-19
