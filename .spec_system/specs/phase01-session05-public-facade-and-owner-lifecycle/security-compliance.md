# Security & Compliance Report

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Package**: `backend/packages/txt2crs`
**Reviewed**: 2026-07-19
**Result**: PASS

## Scope

The assessment covered all package production, test, documentation, and Apex
workflow changes since base commit
`2e2c022265d802e127893fb9d328a4e0ba60211e`. The risk-bearing production
surface is:

- `src/txt2crs/application/config.py`
- `src/txt2crs/application/facade.py`
- `src/txt2crs/application/factories.py`
- `src/txt2crs/application/owner_lifecycle.py`
- `src/txt2crs/jobs/artifact_reader.py`
- `src/txt2crs/jobs/artifact_store.py`
- `src/txt2crs/jobs/service.py`
- `src/txt2crs/jobs/store.py`
- the supported package exports and assembly documentation

Review methods included exact diff/untracked-file inspection, tests-first
security regressions, static and secret scans, SQLite failure injection,
filesystem symlink/confinement tests, package archive inspection, 444
credential-free tests, and the repository engine validation gate.

## Security Assessment

### Overall: PASS

| Category | Status | Details |
|----------|--------|---------|
| Authentication boundary | PASS | The facade delegates only to `DedicatedSystemAuthenticator` and returns its browser-safe snapshot. `CODEX_HOME` is explicit, separate from engine state, and cannot traverse an existing symlink. |
| Authorization/tenant isolation | PASS | The facade binds executor creation, recovery, public query, manifest, stream, and purge operations to the supplied owner. Durable queries include `user_id`; artifact paths use SHA-256 owner/job directories rather than raw identifiers. The shell remains responsible for establishing the authenticated owner. |
| Right-to-erasure race safety | PASS | Purge cancels and waits for tracked owner executors, removes the confined artifact tree first, then deletes owner job parents in one SQLite transaction. It cannot report success on artifact, database, commit, or rowcount failure, and retries are idempotent. |
| SQL injection/transaction integrity | PASS | Owner values use SQLite parameters. `BEGIN IMMEDIATE` serializes deletion, foreign keys cascade child rows, commit failures roll back, and the deleted parent count is verified before success. |
| Filesystem confinement | PASS | User/job names never enter paths. Absolute application roots reject symlink ancestry and credential/state overlap. Owner purge rejects symlinked/non-directory topology, confines resolved directories to the private root, and does not follow an external symlink target. |
| Network/SSRF | PASS | Managed research MCP configuration accepts only explicit numeric loopback addresses. Tavily uses one fixed HTTPS origin, bounded timeouts/document sizes, and the existing public-URL normalization/DNS/redirect defenses. No hosted/public MCP path was added. |
| Provider/model policy | PASS | Real composition uses the exact reviewed GPT-5.6 model policy and reviewed Tavily source declaration. Provider construction is lazy; budget, cancellation, retry, guardrail, HTTP research client, MCP, temporary worker, Codex adapter, coordinator, and pipeline state are job-scoped. No fallback or first-discovered selection exists. |
| Secrets | PASS | Tavily is a `SecretStr`, never serialized in clear text, and remains in the application-owned provider process. Codex child construction retains the existing API-key stripping. Scans found no embedded token or private key. Test-only strings are inert sentinels. |
| Error/data exposure | PASS | Public close, closed-state, owner-purge, readiness, and construction paths use context-free messages. They omit paths, SQL, request content, owner hashes, provider errors, discovered models, and secrets. |
| Resource ownership/DoS | PASS | Config limits are finite; construction unwinds partial store/HTTP/auth resources; executor/application close is idempotent and synchronized; completed executor graphs are weakly tracked rather than retained indefinitely. |
| Dynamic execution/dependencies | PASS | No caller-controlled shell/process invocation, code evaluation, new dependency, debug mode, or production print/log path was introduced. Subprocess use is limited to clean-process import tests. |

### Security Findings

No unresolved security finding remains. Formal review repaired the
active-executor erasure race, SQLite commit/count integrity, admitted-call
close race, private-root ambiguity, and early MCP-host validation before this
assessment.

## GDPR Assessment

### Overall: PASS

**Categories reviewed**: collection and purpose, consent, minimization,
third-party transfer, storage limitation, right to erasure, and PII in logs.

### Personal Data Inventory

| Data Element | Storage/Transfer | Purpose | Retention/Deletion |
|--------------|------------------|---------|--------------------|
| Owner identifier | Tenant-scoped SQLite rows; one-way SHA-256 directory derivation | Authorize and group the owner's jobs/artifacts | Every engine row and hashed owner artifact tree is removed by `purge_owner` |
| Submitted educational input/preferences | Exact SQLite request envelope and accepted checkpoints; consent-gated transfer to ingestion/research/model providers as required | Generate and resume the requested course | Cascades with owner jobs; generated artifacts are deleted first |
| Generated course/review/test/answer-key files | Private owner/job filesystem tree | Deliver requested learning materials | Owner purge removes the complete tree; repeat deletion is safe |
| Usage and delivery state | Tenant-scoped checkpoint/delivery rows | Resume finite budgets and prove idempotent disabled delivery | Cascades through parent job deletion |
| Dedicated system authentication challenge/account state | In-memory safe snapshots plus Codex-managed credentials in separate operator-controlled `CODEX_HOME` | Connect the configured system ChatGPT subscription | Logout/close use the existing authentication boundary; this is system state, not learner-owned data |
| Tavily secret/provider runtime state | In-memory config and fixed-origin HTTPS request only | Authorized URL extraction and course research | Not persisted in job/artifact storage; job-scoped research resources close after use |

### GDPR Findings

No GDPR finding remains.

- Collection is purpose-limited to course generation, recovery, delivery, and
  finite usage accounting already declared by the request contract.
- Existing content policy evaluates provider consent before remote URL
  ingestion or model/research work. Deterministic composition transfers
  nothing externally.
- Public responses remain data-minimized: path-free job snapshots, manifest
  metadata, one verified artifact stream, safe readiness/auth snapshots, and
  deletion counts.
- The session adds no analytics, email, address, demographic field, or logging
  call. No new PII log path exists.
- Owner deletion covers active and terminal jobs, exact request envelopes,
  admissions, checkpoints, delivery rows, and private artifacts. The future
  shell must coordinate its PostgreSQL user/account deletion separately, as
  explicitly scoped for Phase 04.
- The operator-controlled Codex identity and Tavily credential are not owner
  data and are intentionally outside owner purge.

## Compliance Evidence

- SQLite cascade, rollback, commit-rejection, rowcount, retry, and already
  purged tests pass.
- Filesystem hashed-owner, other-owner preservation, idempotency, and symlink
  target tests pass.
- Active executor cancellation/wait and facade close synchronization tests
  pass.
- Config rejects unknown fields, mutation, relative/symlinked/overlapping
  private roots, unsafe MCP hosts, invalid deterministic JSON, empty secrets,
  and non-GPT-5.6 model configuration.
- Scoped scans found no hardcoded credential, private key, dynamic execution,
  production subprocess, public listener, debug marker, or new logging call.
- Full suite: 444 passed, 1 explicitly credential-gated live test skipped.
- Ruff, strict mypy, lock validation, isolated wheel/sdist inspection, and the
  repository engine gate pass.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (`validate`)
- **Date**: 2026-07-19
