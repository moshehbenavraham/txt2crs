# Security & Compliance Report

**Session ID**: `phase01-session02-safe-queries-and-artifact-access`
**Package**: backend/packages/txt2crs
**Reviewed**: 2026-07-19
**Result**: PASS

## Scope

**Files reviewed** (session deliverables plus every file changed since the
recorded base commit):

- `.spec_system/PRD/phase_01/*.md`, `.spec_system/state.json`, and the current
  session records - workflow scope, evidence, and status
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - public contracts
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py` - allowlisted
  artifact metadata and private pre-write validation
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py` - confined
  metadata reads, content integrity, and context-managed streaming
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py` - atomic
  private filesystem lifecycle
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` - bounded
  private-to-public job projection
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py` - owner-safe query
  application boundary and deterministic artifact store
- `backend/packages/txt2crs/tests/factories.py` - cumulative private-state
  fixture
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - real SQLite/filesystem ownership and restart coverage
- `backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py`,
  `test_job_service.py`, and `test_public_job_queries.py` - integrity,
  privacy, cleanup, bounds, and safe-error regressions

**Review method**: Static inspection of the complete base-relative session
surface, targeted security-checklist and behavioral-checklist review,
dependency/schema diffs, secret/log scans, package tests, package build, and
owner/privacy regression tests.

**Review evidence**:

- Command/check: `git diff --name-only "$BASE"` plus
  `git ls-files --others --exclude-standard`
  - Result: PASS - 18 pre-validation files defined the complete review
    surface; no staged-only or mid-session commit escaped the inventory.
  - Evidence: `code-review.md` records every file and has `Result: RESOLVED`.
- Command/check: secret and output scan over the five changed production
  modules using `rg` for OpenAI/Bearer credential shapes and
  `print(`, `logger.`, or `logging.`
  - Result: PASS - no secret literal, raw-input log, print, or logging side
    channel exists in the session production code.
  - Evidence: Public privacy tests assert exact JSON keys and private
    sentinels; filesystem-race errors assert empty cause/context.
- Command/check: `git diff --name-only "$BASE" --
  backend/packages/txt2crs/pyproject.toml backend/uv.lock
  frontend/package.json frontend/package-lock.json`
  - Result: N/A - the command returned no dependency manifest or lockfile.
  - Evidence: This session introduced no dependency to audit.
- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS - 303 tests passed and only the explicit credential-gated
    live Codex test skipped.
  - Evidence: Owner isolation, missing-resource ambiguity, traversal,
    symlinks, mutation, bounded reads, descriptor cleanup, and public
    redaction all have named passing tests.

## Security Assessment

### Overall: PASS

| Category | Status | Severity | Details |
|----------|--------|----------|---------|
| Injection (SQLi, CMDi, LDAPi) | PASS | -- | No SQL, command, LDAP, template execution, or shell interpolation was added. File names/media types reject control characters before storage or public use. |
| Hardcoded Secrets | PASS | -- | No credential, API key, token, password, connection string, or provider secret was added. Test-only privacy sentinels are synthetic. |
| Sensitive Data Exposure | PASS | -- | Public objects are constructed from explicit allowlists. Raw input, evidence excerpts, private IDs/accounting, paths, descriptors, and checkpoint JSON do not cross the package boundary or enter errors/logs. |
| Insecure Dependencies | PASS | -- | No dependency or lockfile changed. |
| Security Misconfiguration | PASS | -- | No CORS, debug, network listener, deployment setting, response header, or permission default changed. Private files/directories retain owner-only modes. |
| Database Security | PASS | -- | No schema/query change exists. Durable owner authorization precedes status availability, and artifact paths use owner/job hashes with indistinguishable not-found behavior. |

### Security Findings

No unresolved security finding remains. The preceding `creview` gate found and
fixed:

- a private filesystem path that an `OSError` race could retain;
- CR/LF and other control characters in supposedly safe file/media metadata;
- stale body sizes in metadata-only manifests;
- a writer/reader manifest-bound mismatch;
- partial deterministic-store state after clock failure;
- contradictory failed/cancelled public state; and
- secret-shaped canonical URL paths.

Every repair has a tests-first regression and is recorded as `FIXED` in
`code-review.md`.

## GDPR Compliance Assessment

### Overall: PASS

**Categories reviewed**: Data Collection & Purpose, Consent Mechanism, Data
Minimization, Right to Erasure, PII in Logs, Third-Party Data Transfers.

### Personal Data Inventory

| Data Element | Source | Storage | Purpose | Retention | Deletion Path |
|-------------|--------|---------|---------|-----------|---------------|
| Pseudonymous owner ID | Authenticated shell caller in later composition | Durable job SQLite; only a SHA-256 owner hash is used in artifact paths | Tenant authorization and private artifact lookup | Existing engine-state lifetime | Existing per-job artifact delete; Session 05 owner-wide purge remains specified |
| Generated course, review, assessment, and answer-key bytes | Accepted engine output | Owner-only filesystem artifact tree | Authorized preview/download and deterministic recovery | Configured artifact retention period | Per-job delete and retention purge; Session 05 owner-wide purge |
| Public-safe source title/URL/publisher/retrieval date | Accepted evidence metadata | Existing checkpoint; copied only into bounded public snapshots | Bibliography and learner source attribution | Existing checkpoint lifetime | Session 05 owner purge |
| Raw learner input, normalized text, evidence excerpts, and provider/accounting data | Existing durable request/checkpoint | Existing private SQLite checkpoint boundary | Generation and recovery only | Existing engine-state lifetime | Session 05 owner purge; never copied by this session's public projection |

### GDPR Findings

No GDPR finding remains within this session's scope.

- This session adds no new personal-data collection, consent decision, or
  third-party transfer.
- Public projection applies data minimization through explicit bounded
  allowlists and safe redaction; private input/evidence/provider values stay
  excluded.
- No PII, learner content, URL credential, private path, or artifact byte is
  logged.
- Per-job deletion and retention remain intact. The already planned Session 05
  owner-wide purge is the complete account-erasure path.

## Recommendations

- Phase 03 should still encode the reviewed safe file name with a robust
  `Content-Disposition` helper and apply the planned private/no-store and
  nosniff headers.
- Session 05 should finish and test idempotent owner-wide purge across SQLite
  requests/checkpoints/delivery state and filesystem artifacts.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (`validate`)
- **Date**: 2026-07-19
