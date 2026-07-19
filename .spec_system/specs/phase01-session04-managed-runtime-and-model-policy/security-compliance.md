# Security & Compliance Report

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Package**: `backend/packages/txt2crs`
**Reviewed**: 2026-07-19
**Result**: PASS

## Scope

The review covered all 27 package files created or modified since base commit
`118695b4ca97e74b4ca85716d6813581ddb23da6`, plus the workspace lockfile
change. The risk-bearing production surface is:

- `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py`
- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py`
- `backend/packages/txt2crs/src/txt2crs/ai/model_policy.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/004_delivery_notifications.sql`
- `backend/packages/txt2crs/src/txt2crs/jobs/notifications.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py`
- `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py`
- `backend/packages/txt2crs/src/txt2crs/research/mcp_server.py`
- the related public exports, dependency declarations, and tests

**Review method**: Exact package-diff inspection, tests-first review
regressions, dependency-diff inspection, focused lifecycle/migration/model
tests, secret/debug/process scans, distribution inspection, and the complete
credential-free package suite.

## Evidence

- `{ git diff --name-only "$BASE" -- backend/packages/txt2crs; git ls-files
  --others --exclude-standard backend/packages/txt2crs; } | sort -u`
  identified exactly 27 package files.
- Scoped scans found no embedded token, private key, debugger, production
  `print`, dynamic evaluation, shell execution, or caller-controlled process
  invocation.
- Test-only strings such as `secret-platform-key` exercise removal from the
  Codex child environment; they are inert sentinels, not credentials.
- `git diff "$BASE" -- backend/packages/txt2crs/pyproject.toml
  backend/uv.lock` shows only direct declaration of already-resolved Uvicorn.
  No transitive package version changed.
- `uv run --package txt2crs pytest -q` passed 402 tests and skipped the one
  explicitly credential-gated live acceptance test.
- The 94-test focused lifecycle, policy, migration, executor, and live-gate
  selection passed with the same single explicit skip.

## Security Assessment

### Overall: PASS

| Category | Status | Details |
|----------|--------|---------|
| Injection | PASS | The only new SQL is fixed packaged migration text. Runtime values use parameterized SQLite statements. No dynamic command, template, LDAP, or code-evaluation boundary was added. |
| Hardcoded secrets | PASS | No real secret exists in source, tests, config, or workflow artifacts. Live work reads environment configuration only behind its explicit gate. |
| Sensitive-data exposure | PASS | Typed lifecycle/readiness errors omit provider errors, discovered models, port numbers, paths, payloads, credentials, and thread details. Background failures retain only a boolean. |
| Network exposure | PASS | The managed MCP accepts only explicit numeric loopback IPs, pre-binds one owned socket, publishes only after readiness/tool verification, revokes on every exit, and closes the listener on timeouts. |
| Resource ownership | PASS | Temporary storage, HTTP, MCP, and Codex resources close in reverse order. Cleanup cannot mask a primary job error. All waits are finite. |
| Model/provider policy | PASS | Configuration is restricted to four reviewed GPT-5.6 slugs. Exact discovery, requested identity, and result identity are required; no fallback or first-model selection remains. |
| Dependency security | PASS | Uvicorn is a direct bounded dependency because production imports it. The lockfile already contained the resolved dependency; no unrelated dependency changed. |
| Database security | PASS | Migration application is serialized with `BEGIN IMMEDIATE`; schema changes and version records commit or roll back atomically. Notification values are closed enums. |
| Security configuration | PASS | No CORS, auth, debug, hosted MCP, public bind, deployment, or shell configuration changed. |

### Security Findings

No unresolved security findings. The code-review gate repaired the listener
leak/error-translation and migration-atomicity findings before validation.

## GDPR Compliance Assessment

### Overall: PASS

**Categories reviewed**: Data Collection & Purpose, Consent, Data
Minimization, Right to Erasure, PII in Logs, and Third-Party Transfers.

### Personal Data Inventory

| Data Element | Storage/Transfer | Purpose | Retention/Deletion |
|--------------|------------------|---------|--------------------|
| Existing submitted and normalized educational content | Existing tenant-scoped request/checkpoint storage; provider transfer remains consent-gated | Generate and resume the requested course | Existing job lifetime; owner-wide purge remains the explicit Session 05 deliverable |
| Provider/model readiness metadata | Transient in-process adapter/runtime values; only a safe readiness projection escapes | Determine whether the configured subscription runtime can execute | Not newly persisted by this session |
| Temporary worker and HTTP/MCP state | Per-job managed resources | Execute one provider-backed generation attempt | Closed/released on every ordinary exit and partial construction |
| Notification version/mode/status | Tenant-scoped SQLite delivery row | Record that P0 notification is disabled and not applicable | Same delivery-row lifetime; contains no address or message content |

### GDPR Findings

No GDPR findings.

- This session adds no new user-entered field, email address, notification
  destination, or analytics/logging path.
- Disabled notification state is purpose-limited, non-personal, and uses three
  closed values rather than an ambiguous nullable side effect.
- Existing provider consent remains mandatory before provider-backed pipeline
  construction. The managed runtime does not broaden third-party transfer.
- Public readiness and lifecycle errors are data-minimized and omit raw
  provider discovery/error values.
- The scoped production diff adds no logging call, so it introduces no PII log
  path.
- Right-to-erasure composition remains deliberately assigned to Session 05,
  which will purge request, checkpoint, artifact, and provider-owned owner
  state together.

## Recommendation

In Session 05, keep the provider graph behind the managed contexts introduced
here and complete the already-planned idempotent owner-wide purge. Preserve
tests proving purge covers SQLite state, artifacts, and any provider-owned
owner directory.

## Sign-Off

- **Result**: PASS
- **Reviewed by**: AI validation (`validate`)
- **Date**: 2026-07-19
