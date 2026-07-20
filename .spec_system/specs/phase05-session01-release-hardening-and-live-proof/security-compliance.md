# Security & Compliance Report

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Package**: null (cross-cutting monorepo)
**Reviewed**: 2026-07-20
**Result**: PASS

## Scope

**Files reviewed** (session changes only):

- 339 generated Codex protocol-fixture paths, including the pinned `0.144.4`
  fixture index and retained compatibility schema.
- 29 txt2crs engine source, package, documentation, and test paths covering
  authentication, exact-model policy, provider schemas, research, bounded
  generation repair, rendering, evaluation, and live acceptance.
- 22 backend shell paths covering configuration, readiness, serial worker
  startup, generated schemas, production email templates, and tests.
- 8 frontend paths covering generated model contracts, client generation,
  setup presentation tests, and Playwright setup.
- 17 root release, environment-example, workflow, version, changelog, release
  evidence, and script paths.
- 9 active Apex/PRD paths and 21 exact archive renames.

The complete base-to-HEAD inventory contains 445 changed paths. One path is a
deleted compatibility fixture; all 444 current regular files were included in
the current-file ASCII/LF and secret-diff scans.

**Review method**: Targeted static analysis of the complete session diff,
strict evidence validation, focused trust-boundary tests, full engine/backend/
frontend suites, dependency audits, workflow and shell analysis, exact-head
distribution/image inspection, and privacy-pattern scanning.

**Review evidence**:

- Command/check: `git diff "$BASE" HEAD | gitleaks stdin --redact --no-banner`
  - Result: PASS - about 1.14 MB of session diff scanned with no leak.
- Command/check: strict public-release risky-value `rg` scan plus
  `python scripts/release_evidence.py validate-evidence`
  - Result: PASS - no email, absolute path, credential assignment, private URL,
    prompt, provider payload, or artifact body is present; the canonical
    evidence hash is
    `43e811fc58efdce308b33d74112ab3a5969bca6fa3585e9a347643f6d052bbbd`.
- Command/check: `uv run --with pip-audit pip-audit` and
  `npm audit --audit-level=high`
  - Result: PASS - no known Python vulnerability and zero npm vulnerabilities;
    local `app` and `txt2crs` packages are correctly reported as non-PyPI.
- Command/check: `actionlint .github/workflows/*.yml`,
  `uv run --project backend zizmor --pedantic .github/workflows`, `bash -n`,
  and `shellcheck`
  - Result: PASS - all ten workflows and both changed shell helpers pass.
- Command/check: focused release/workflow/auth helper contracts
  - Result: PASS - 33 tests cover exact fields, redaction, candidate/final
    identity, pinned read-only workflow behavior, fixed auth state, and
    argument forwarding.
- Command/check: exact-head full suites
  - Result: PASS - engine 489 passed with 2 explicit live skips, backend 517
    passed on migrated PostgreSQL 18, frontend 132 passed, and all lint/type/
    build gates passed.

## Security Assessment

### Overall: PASS

| Category | Status | Severity | Details |
|----------|--------|----------|---------|
| Injection (SQLi, CMDi, LDAPi) | PASS | -- | No changed runtime path adds raw SQL, LDAP, `shell=True`, `eval`, or string-built command execution. The auth helper quotes forwarded arguments and fixes the credential directory before `exec`. |
| Hardcoded Secrets | PASS | -- | Gitleaks found no secret in the complete diff. Environment examples contain names/placeholders only, and tracked evidence contains no credential-shaped value. |
| Sensitive Data Exposure | PASS | -- | Public evidence is exact-field allowlisted and recursively rejects email, URL, and absolute-path shapes. Provider errors, prompts, account details, raw artifacts, and local paths remain behind typed private boundaries. |
| Insecure Dependencies | PASS | -- | Python and npm audits found no known vulnerability. The Codex SDK/CLI change is lockfile-pinned to `0.144.4` with a generated protocol fixture and contract tests. |
| Security Misconfiguration | PASS | -- | Workflows are read-only/pinned/nonpublishing; production images are labeled, health-checked, and backend runs non-root; the auth helper enforces owner-only state; exact model selection fails closed. |

The backend suite emits an expected warning for the deliberately short local
test signing key. Non-local configuration tests require production-strength
secrets, and this session did not weaken that boundary.

### Security Findings

No unresolved security findings.

The review repaired three high security/release findings before validation:
the authentication state-directory override, missing production email
templates caused by Docker context filtering, and an invalid bare model
default. Current regression and exact-head image evidence covers all three.

## GDPR Compliance Assessment

### Overall: N/A

This session introduced no new production collection, consent decision,
personal-data field, retention rule, logging field, third-party transfer, or
deletion behavior. The representative provider run used a synthetic,
nonpersonal education topic through the existing explicit provider-processing
consent boundary. Existing owner authorization and purge behavior remain
unchanged and are covered by full engine/backend/browser tests.

**Categories reviewed**: Data Collection & Purpose, Consent Mechanism, Data
Minimization, Right to Erasure, PII in Logs, Third-Party Data Transfers.

### Personal Data Inventory

No personal data was collected or processed by new production behavior in this
session. Local browser tests create disposable synthetic accounts and delete
them through the existing owner purge path.

### GDPR Findings

No GDPR findings.

## Recommendations

- Session 02 must rebuild distributions and images from its exact final
  tracked commit and must not reuse historical candidate build hashes.
- Keep `remote_codeql_billing` as the sole reviewed external exception until a
  hosted CodeQL job actually runs.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (`validate`)
- **Date**: 2026-07-20
