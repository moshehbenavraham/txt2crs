# Security & Compliance

> Cumulative security posture and GDPR compliance record. Updated between phases via carryforward.
> **Line budget**: 1000 max | **Last updated**: Phase 05 (2026-07-20)

---

## Current Security Posture

### Overall: AT RISK

| Metric | Value |
|--------|-------|
| Open Findings | 1 |
| Critical/High | 0 |
| Medium/Low | 1 |
| Phases Audited | 6 |
| Last Clean Phase | -- |

Both Phase 05 sessions and the final local infrastructure drill passed with no
unresolved finding. Exact-model live proof used synthetic data, public media
was privacy-reviewed, workflows pass local security analysis, and initialized
Codex state now survives checksum-validated backup and restore without
archiving image-specific scratch links. The cumulative application remains at
risk only because remote CodeQL cannot run while GitHub Actions billing is
disabled.

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

The application minimizes public projections, gates provider transfer on
consent, minimizes normal request/provider/error logging, and coordinates live
engine-state erasure before account deletion. It is not ready for public
personal-data processing because formal legal-basis, third-party-transfer,
retention, log-erasure, backup-erasure, and provider-copy records remain
incomplete.

### Personal Data Inventory

| Data Element | Package | Source | Storage | Purpose | Legal Basis | Retention | Deletion Path | Since |
|-------------|---------|--------|---------|---------|-------------|-----------|---------------|-------|
| Email address | `backend` | Signup, admin, account update | PostgreSQL `user.email` | Authentication and account contact | Contract/user request; formal record pending | Account lifetime; exact policy pending | Coordinated self-service deletion or admin deletion | Imported baseline |
| Optional full name | `backend` | Signup or account update | PostgreSQL `user.full_name` | Account display and administration | Contract/user request; formal record pending | Account lifetime; exact policy pending | Coordinated self-service deletion or admin deletion | Imported baseline |
| Password hash | `backend` | Password setup/reset | PostgreSQL `user.hashed_password` | Authentication | Security necessity | Account lifetime | Coordinated user deletion; replaced on reset | Imported baseline |
| Trace ID, HTTP method, matched route name, status, duration | `backend` | Allowlisted HTTP request metadata | Application logs | Operations and incident correlation | Legitimate interest; assessment pending | Undefined | No documented per-person log erasure path | P02 |
| Optional bounded topic draft | `frontend` | Explicit public landing-page save action | Versioned browser `sessionStorage` envelope | One-time sign-in handoff to the authenticated intake form | User request; formal record pending | Consumed once, cleared on invalid data, or ends with the browser tab/session | `consumeCoursePromptDraft()` or `clearCoursePromptDraft()` | P04 |
| Pseudonymous owner ID | `backend/packages/txt2crs` | Authenticated shell caller | Tenant SQLite; SHA-256 artifact directory derivation | Tenant authorization, quota, recovery, and erasure | Contract/user request; formal record pending | Engine-state lifetime; exact policy pending | Coordinated self-delete calls `purge_owner` first | P01 |
| Submitted input, source metadata, age group, consent, preference intent, and idempotency key | `backend/packages/txt2crs` | Learner generation request | Canonical tenant SQLite request envelope | Course generation, exact restart recovery, and duplicate-safe admission | Contract/user request; provider transfer requires explicit consent | Job lifetime; exact policy pending | Cascades through coordinated `purge_owner` | P01/P03 |
| Normalized content, evidence, resolved preferences, and usage state | `backend/packages/txt2crs` | Ingestion and accepted generation checkpoints | Tenant SQLite checkpoints | Policy, personalization, finite execution, and recovery | Contract/user request; formal record pending | Job lifetime; exact policy pending | Cascades through `purge_owner` | P01 |
| Generated course, review, assessment, and answer-key files | `backend/packages/txt2crs` | Engine output | Owner-only artifact filesystem; temporary revocable browser URLs during authorized use | Authorized preview, download, and recovery | Contract/user request | Artifact lifetime; exact policy pending; browser URLs are revoked on close/unmount | Artifact-first coordinated `purge_owner` | P01/P04 |
| Provider/model runtime state | `backend/packages/txt2crs` | Consented generation execution | Transient HTTP, loopback MCP, Codex, and worker resources | Research and model-backed course generation | Explicit provider consent plus contract; transfer record pending | Job-scoped resources close on exit | Resource cleanup; no durable owner row | P01 |
| Backup copies of application and engine state | root deployment | Operator maintenance action | Owner-only checksum bundle containing PostgreSQL and durable engine/Codex state | Local disaster recovery | Same pending bases as copied records | Local cleanup defaults to seven days; encrypted off-host policy pending | Retention cleanup or explicit secure deletion; no per-owner backup erasure record | P05 |

### Compliance Checklist

| Requirement | Status | Notes |
|------------|--------|-------|
| Data collection has documented purpose | PASS | Account and engine fields have authentication, generation, policy, recovery, and delivery purposes. |
| Consent or other legal basis documented | FAIL | Runtime consent gates exist, but the complete public legal-basis and transfer record is not published. |
| Data minimization verified | PASS | Engine public projections and normal shell request/provider/error logs use reviewed allowlists. |
| Deletion/erasure path exists | PARTIAL | Live engine and PostgreSQL state are coordinated; logs, backups, and any provider copies still need policy and erasure records. |
| No PII in application logs | PASS | Focused regressions reject raw path, query, IP, body/header, recipient, provider-response, and exception content. |
| Third-party transfers documented | PARTIAL | OpenAI/Tavily execution is consent-gated, but the public transfer/privacy record is incomplete. |

---

## Dependency Security

### Current Vulnerabilities

No known vulnerable dependencies. On 2026-07-20, `pip-audit` found none in
locked third-party Python packages and `npm audit --audit-level=high` reported
zero. The local `app` and `txt2crs` workspace distributions were reported
separately as non-index packages.

Additional controls:

- Gitleaks scanned all 78 commits with four exact synthetic/example
  fingerprints and found no leak.
- Pedantic Zizmor and actionlint reported no finding across all ten GitHub
  workflows.
- Every third-party action remains commit-pinned.
- The packaged Codex runtime is lockfile-pinned to `0.144.4`, and the exact
  `gpt-5.6-sol` plus Tavily proof completed with synthetic nonpersonal input.

---

## Resolved Findings

Recently closed items. Compressed after 2 phases.

| ID | Finding | Severity | Resolved | Phase | Resolution |
|----|---------|----------|----------|-------|------------|
| P00-backend-S01 | Raw request metadata can expose personal data | High | 2026-07-19 | P02 | Normal shell request, exception, telemetry, SMTP, and startup events now use bounded allowlists and focused privacy regressions. |
| P00-backend-S03 | Incomplete local backup and restore | Medium | 2026-07-20 | P05 | A Codex-initialized volume exposed image-specific scratch links; backup now omits only `codex-home/tmp`, retains durable state, rejects other symlinks, and passes a destructive two-store restore. |
| P00-backend-S00 | Dynamic non-root volume ownership | High | 2026-07-19 | P00 | Fixed the mount at the image-owned private state root and proved UID 1001 writes and reopens it. |
| P00-S02 | Public edge WAF is not configured | Medium | 2026-07-19 | P00 | Closed as not applicable after ADR-0008 made local Docker the complete project deployment scope. Reassess only after an owner-approved hosted scope change. |

---

## Phase History

| Phase | Sessions | Package Scope | Security | GDPR | Findings Opened | Findings Closed |
|-------|----------|---------------|----------|------|-----------------|-----------------|
| P05 | 2 | Cross-cutting release, live proof, product media, and local infrastructure | Session PASS; cumulative AT RISK | Session N/A; cumulative FAIL | 0 | 0 |
| P04 | 2 | Cross-cutting: 1; `frontend`: 1 | Session PASS; cumulative AT RISK | Session PASS/N/A; cumulative FAIL | 0 | 0 |
| P03 | 3 | `backend`: 3; public engine contracts and generated frontend derivatives | Session PASS; cumulative AT RISK | Session PASS; cumulative FAIL | 0 | 0 |
| P02 | 5 | `backend`: 4; `frontend`: 1; public engine corrections | Session PASS; cumulative AT RISK | Session PASS; cumulative FAIL | 0 | 1 |
| P01 | 5 | `backend/packages/txt2crs`: 5 | Session PASS; cumulative AT RISK | Session PASS; cumulative FAIL | 0 | 1 |

---

## Recommendations

1. Define privacy, legal-basis, provider-transfer, log-retention, engine-state,
   artifact, and backup-retention policy before accepting real learner data.
2. Preserve owner-hidden reads, verified private transfers, bounded inert HTML,
   empty-sandbox isolation, and temporary-URL cleanup during release changes.
3. Pin exact reviewed image IDs and repeat backup/restore after any Codex
   runtime-layout change.
4. Restore GitHub Actions and obtain a clean Security run including CodeQL.

---

*Auto-generated by carryforward. Direct edits allowed but may be overwritten.*
