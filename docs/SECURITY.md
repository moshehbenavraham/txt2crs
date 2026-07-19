# Security Policy

## Supported Version

Only the current repository version in [`../VERSION`](../VERSION) is supported
during the hackathon build.

## Reporting a Vulnerability

Do not send txt2crs reports to the upstream boilerplate maintainer and do not
open a public issue containing exploit details, credentials, personal data, or
private generated content.

This private repository does not currently expose a verified project-specific
security mailbox or GitHub private-vulnerability-reporting endpoint. The
repository owner must choose and publish that durable private channel before a
public release. Until then, coordinate privately with the repository owner and
share only the minimum reproduction material needed.

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

The current scope is local-only. Do not claim that real learner data is ready
for unrestricted use while logging, remote-CI, private reporting, and
privacy-policy findings remain. Backup bundles themselves contain learner data
and Codex credentials, so keep them encrypted and access controlled.
