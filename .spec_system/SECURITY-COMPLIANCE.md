# Security & Compliance

> Cumulative security posture and GDPR compliance record. Updated between phases via carryforward.
> **Line budget**: 1000 max | **Last updated**: Phase 00 (2026-07-19)

---

## Current Security Posture

### Overall: AT RISK

| Metric | Value |
|--------|-------|
| Open Findings | 3 |
| Critical/High | 1 |
| Medium/Low | 2 |
| Phases Audited | 1 |
| Last Clean Phase | -- |

The Phase 00 implementation surface passed its scoped review. The cumulative
application remains at risk because pre-existing request logging can expose
personal data and complete local recovery controls are not yet proven.

---

## Open Findings

Active security or GDPR issues requiring attention. Ordered by severity.

### Critical / High

- **[P00-backend-S01] Raw request metadata can expose personal data**
  - Severity: High
  - File: `backend/app/core/middleware.py`
  - Description: Request logs contain the raw path, query string, and client
    IP. Password-recovery paths can include an email address, and future query
    parameters may contain tokens or source references.
  - Remediation: Log a bounded route template and approved fields only,
    redact sensitive values, minimize IP handling, and document log retention.
  - Status: Open
  - Opened: P00 (2026-07-19)

### Medium / Low

- **[P00-backend-S03] Persistent data has no proven complete backup and restore**
  - Severity: Medium
  - File: `scripts/backup-db.sh`
  - Description: PostgreSQL dump commands and retention cleanup exist, but no
    complete local restore has been verified. The private engine state volume
    is not included in that backup path.
  - Remediation: Back up both persistence owners while writers are stopped,
    restore into disposable local targets, and document recovery objectives.
  - Status: Open
  - Opened: P00 (2026-07-19)

- **[P00-S04] Remote security analysis cannot execute**
  - Severity: Low
  - File: `.github/workflows/security.yml`
  - Description: GitHub Actions billing rejects every job before scheduling.
    Gitleaks and dependency audits pass locally, but CodeQL is remote-only.
  - Remediation: Restore Actions billing, run Security successfully, review
    CodeQL/dependency-review results, and remove the skipped-workflow entries.
  - Status: Open
  - Opened: P00 (2026-07-19)

---

## GDPR Compliance Status

### Overall: NON-COMPLIANT

The Phase 00 changes add no new personal-data collection. The cumulative
baseline is not ready for public processing because request logs are not
data-minimized and legal-basis, consent, and retention records are incomplete.

### Personal Data Inventory

| Data Element | Package | Source | Storage | Purpose | Legal Basis | Retention | Deletion Path | Since |
|-------------|---------|--------|---------|---------|-------------|-----------|---------------|-------|
| Email address | `backend` | Signup, admin, account update | PostgreSQL `user.email` | Authentication and account contact | Contract/user request; formal record pending | Account lifetime; exact policy pending | Self-service or admin user deletion | Imported baseline |
| Optional full name | `backend` | Signup or account update | PostgreSQL `user.full_name` | Account display and administration | Contract/user request; formal record pending | Account lifetime; exact policy pending | Self-service or admin user deletion | Imported baseline |
| Password hash | `backend` | Password setup/reset | PostgreSQL `user.hashed_password` | Authentication | Security necessity | Account lifetime | User deletion; replaced on reset | Imported baseline |
| Client IP, trace ID, path, query | `backend` | HTTP request metadata | Structured application logs | Operations and incident correlation | Legitimate interest; assessment pending | Undefined | No documented per-person log erasure path | Imported baseline |

### Compliance Checklist

| Requirement | Status | Notes |
|------------|--------|-------|
| Data collection has documented purpose | PASS | Account fields support authentication and administration. |
| Consent or other legal basis documented | FAIL | No complete public privacy/legal-basis record exists. |
| Data minimization verified | FAIL | Raw paths, queries, and client IPs are logged. |
| Deletion/erasure path exists | PARTIAL | Account rows can be deleted; log and future artifact erasure are incomplete. |
| No PII in application logs | FAIL | Recovery-route email and client metadata can enter logs. |
| Third-party transfers documented | N/A | Phase 00 does not expose engine source/provider submission through the shell. |

---

## Dependency Security

### Current Vulnerabilities

No known vulnerable dependencies. On 2026-07-19, `pip-audit` reported none
for locked third-party Python packages and `npm audit --audit-level=high`
reported zero. The two local Python workspace packages were correctly skipped
as non-index distributions.

Additional controls:

- Gitleaks 8.30.1 scanned all 14 commits with four exact synthetic/example
  fingerprints and found no leaks.
- Zizmor reported no findings across all GitHub workflows.
- Every third-party action in the new Security workflow is commit-pinned.

---

## Resolved Findings

Recently closed items. Compressed after 2 phases.

| ID | Finding | Severity | Resolved | Phase | Resolution |
|----|---------|----------|----------|-------|------------|
| P00-backend-S00 | Dynamic non-root volume ownership | High | 2026-07-19 | P00 | Fixed the mount at the image-owned private state root and proved UID 1001 writes and reopens it. |
| P00-S02 | Public edge WAF is not configured | Medium | 2026-07-19 | P00 | Closed as not applicable after ADR-0008 made local Docker the complete project deployment scope. Reassess only after an owner-approved hosted scope change. |

---

## Phase History

| Phase | Sessions | Package Scope | Security | GDPR | Findings Opened | Findings Closed |
|-------|----------|---------------|----------|------|-----------------|-----------------|
| P00 | 1 | Cross-cutting: backend, engine, frontend | Session PASS; cumulative AT RISK | Session N/A; cumulative FAIL | 4 | 2 |

---

## Recommendations

1. Sanitize request logging before adding source-submission endpoints.
2. Define privacy, legal-basis, log-retention, and erasure policy before the
   release workflow accepts real learner content.
3. Restore GitHub Actions and obtain a clean Security run, including CodeQL.
4. Add backup and local restore coverage for PostgreSQL and the
   engine state volume.

---

*Auto-generated by carryforward. Direct edits allowed but may be overwritten.*
