# Security & Compliance

> Cumulative security posture and GDPR compliance record. Updated between phases via carryforward.
> **Line budget**: 1000 max | **Last updated**: Phase 02 Session 04 (2026-07-19)

---

## Current Security Posture

### Overall: AT RISK

| Metric | Value |
|--------|-------|
| Open Findings | 1 |
| Critical/High | 0 |
| Medium/Low | 1 |
| Phases Audited | 3 |
| Last Clean Phase | -- |

All five Phase 01 engine sessions and the first four Phase 02 composition
sessions passed their scoped security and GDPR reviews with no unresolved
session finding. Session 03 removed raw request/provider/error content from
normal shell logs, and Session 04 protects cached readiness/device
authentication with active-user/superuser authorization and one finite shared
runtime owner. The cumulative application remains at risk only because remote
CodeQL validation cannot run while GitHub Actions billing is disabled.

---

## Open Findings

Active security or GDPR issues requiring attention. Ordered by severity.

### Critical / High

None.

### Medium / Low

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

The engine minimizes public projections, gates provider transfer on consent,
and implements complete owner erasure for engine-owned state. Phase 02
Session 03 also minimizes normal shell request and provider/error logging. The
cumulative application is not ready for public personal-data processing
because legal-basis, third-party-transfer, retention, and coordinated
shell-erasure records remain incomplete.

### Personal Data Inventory

| Data Element | Package | Source | Storage | Purpose | Legal Basis | Retention | Deletion Path | Since |
|-------------|---------|--------|---------|---------|-------------|-----------|---------------|-------|
| Email address | `backend` | Signup, admin, account update | PostgreSQL `user.email` | Authentication and account contact | Contract/user request; formal record pending | Account lifetime; exact policy pending | Self-service or admin user deletion | Imported baseline |
| Optional full name | `backend` | Signup or account update | PostgreSQL `user.full_name` | Account display and administration | Contract/user request; formal record pending | Account lifetime; exact policy pending | Self-service or admin user deletion | Imported baseline |
| Password hash | `backend` | Password setup/reset | PostgreSQL `user.hashed_password` | Authentication | Security necessity | Account lifetime | User deletion; replaced on reset | Imported baseline |
| Trace ID, HTTP method, matched route name, status, duration | `backend` | Allowlisted HTTP request metadata | Application logs | Operations and incident correlation | Legitimate interest; assessment pending | Undefined | No documented per-person log erasure path | P02 |
| Pseudonymous owner ID | `backend/packages/txt2crs` | Authenticated shell caller | Tenant SQLite; SHA-256 artifact directory derivation | Tenant authorization, quota, recovery, and erasure | Contract/user request; shell record pending | Engine-state lifetime; exact policy pending | `purge_owner`; shell coordination pending | P01 |
| Submitted input, source metadata, age group, consent, and preference intent | `backend/packages/txt2crs` | Learner generation request | Canonical tenant SQLite request envelope | Course generation and exact restart recovery | Contract/user request; provider transfer requires explicit consent | Job lifetime; exact policy pending | Cascades through `purge_owner` | P01 |
| Normalized content, evidence, resolved preferences, and usage state | `backend/packages/txt2crs` | Ingestion and accepted generation checkpoints | Tenant SQLite checkpoints | Policy, personalization, finite execution, and recovery | Contract/user request; formal record pending | Job lifetime; exact policy pending | Cascades through `purge_owner` | P01 |
| Generated course, review, assessment, and answer-key files | `backend/packages/txt2crs` | Engine output | Owner-only artifact filesystem | Authorized preview, download, and recovery | Contract/user request | Artifact lifetime; exact policy pending | Artifact-first `purge_owner` | P01 |
| Provider/model runtime state | `backend/packages/txt2crs` | Consented generation execution | Transient HTTP, loopback MCP, Codex, and worker resources | Research and model-backed course generation | Explicit provider consent plus contract; transfer record pending | Job-scoped resources close on exit | Resource cleanup; no durable owner row | P01 |

### Compliance Checklist

| Requirement | Status | Notes |
|------------|--------|-------|
| Data collection has documented purpose | PASS | Account and engine fields have authentication, generation, policy, recovery, and delivery purposes. |
| Consent or other legal basis documented | FAIL | Runtime consent gates exist, but the complete public legal-basis and transfer record is not published. |
| Data minimization verified | PASS | Engine public projections and normal shell request/provider/error logs use reviewed allowlists. |
| Deletion/erasure path exists | PARTIAL | Engine owner purge is complete; PostgreSQL coordination and log erasure remain incomplete. |
| No PII in application logs | PASS | Focused regressions reject raw path, query, IP, body/header, recipient, provider-response, and exception content. |
| Third-party transfers documented | PARTIAL | OpenAI/Tavily execution is consent-gated, but the public transfer/privacy record is incomplete. |

---

## Dependency Security

### Current Vulnerabilities

No known vulnerable dependencies. On 2026-07-19, `pip-audit` found none in
locked third-party Python packages and `npm audit --audit-level=high` reported
zero. The local `app` and `txt2crs` workspace distributions were correctly
excluded as non-index packages.

Additional controls:

- Gitleaks 8.30.1 scanned all 22 commits with four exact synthetic/example
  fingerprints and found no leak.
- Zizmor reported no finding across any GitHub workflow.
- Every third-party action remains commit-pinned.
- The exact GPT-5.6/Tavily live acceptance test remains credential-gated and
  was not claimed as locally executed.

---

## Resolved Findings

Recently closed items. Compressed after 2 phases.

| ID | Finding | Severity | Resolved | Phase | Resolution |
|----|---------|----------|----------|-------|------------|
| P00-backend-S01 | Raw request metadata can expose personal data | High | 2026-07-19 | P02 | Normal shell request, exception, telemetry, SMTP, and startup events now use bounded allowlists and focused privacy regressions. |
| P00-backend-S03 | Incomplete local backup and restore | Medium | 2026-07-19 | P01 | A live disposable proof restored PostgreSQL and private engine state from one owner-only checksum-validated bundle. |
| P00-backend-S00 | Dynamic non-root volume ownership | High | 2026-07-19 | P00 | Fixed the mount at the image-owned private state root and proved UID 1001 writes and reopens it. |
| P00-S02 | Public edge WAF is not configured | Medium | 2026-07-19 | P00 | Closed as not applicable after ADR-0008 made local Docker the complete project deployment scope. Reassess only after an owner-approved hosted scope change. |

---

## Phase History

| Phase | Sessions | Package Scope | Security | GDPR | Findings Opened | Findings Closed |
|-------|----------|---------------|----------|------|-----------------|-----------------|
| P02 | 4/5 | `backend` shell plus public engine boundary | Session PASS; cumulative AT RISK | Session PASS; cumulative FAIL | 0 | 1 |
| P01 | 5 | `backend/packages/txt2crs`: 5 | Session PASS; cumulative AT RISK | Session PASS; cumulative FAIL | 0 | 1 |
| P00 | 1 | Cross-cutting: backend, engine, frontend | Session PASS; cumulative AT RISK | Session N/A; cumulative FAIL | 4 | 2 |

---

## Recommendations

1. Define privacy, legal-basis, provider-transfer, log-retention, engine-state,
   artifact, and backup-retention policy before accepting real learner data.
2. Coordinate engine `purge_owner` with PostgreSQL account deletion and expose
   truthful partial-failure behavior in Phase 04.
3. Run the credentialed GPT-5.6/Tavily acceptance proof before release.
4. Restore GitHub Actions and obtain a clean Security run including CodeQL.

---

*Auto-generated by carryforward. Direct edits allowed but may be overwritten.*
