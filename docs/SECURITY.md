# Security Policy

## Supported Version

Only the current repository version in [`../VERSION`](../VERSION) is supported.

## Reporting a Vulnerability

Do not send txt2crs reports to the upstream boilerplate maintainer and do not
open a public issue containing exploit details, credentials, personal data, or
private generated content.

Use a private GitHub Security Advisory when that repository feature is
available. Otherwise, coordinate privately with the repository owner and share
only the minimum reproduction material needed; never put exploit details in a
public issue.

This missing organizational contact is tracked in
[`../.spec_system/docs-audit.md`](../.spec_system/docs-audit.md).

## Include in a Private Report

- A concise impact statement
- Affected revision, route, or component
- Minimal reproduction steps
- Whether credentials or personal data may be exposed
- Suggested remediation, if known

Never include real secrets or learner content when a synthetic reproduction is
sufficient.

## Current Posture

The cumulative security and GDPR record is
[`../.spec_system/SECURITY-COMPLIANCE.md`](../.spec_system/SECURITY-COMPLIANCE.md).
It is the source of truth for open findings, dependency audits, personal-data
inventory, and remediation priorities.

Repository controls include:

- Non-root containers and owner-only engine state
- Rate limiting outside local development
- RFC 9457 errors without stack traces
- Gitleaks history scanning and dependency audits
- Commit-pinned GitHub Actions plus Zizmor checks
- Credential-free deterministic validation
- Owner-only, checksum-validated PostgreSQL and engine-state backups

Local and hosted deployments must preserve the same security contract. Do not
claim that real learner data is ready for unrestricted use while logging,
private reporting, and privacy-policy findings remain. Backup bundles
themselves contain learner data and Codex credentials, so keep them encrypted
and access controlled.
