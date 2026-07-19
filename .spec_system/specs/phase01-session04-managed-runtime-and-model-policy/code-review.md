# Code Review and Repair Report

**Session ID**: `phase01-session04-managed-runtime-and-model-policy`
**Package**: `backend/packages/txt2crs`
**Reviewed**: 2026-07-19
**Base Commit**: `118695b4ca97e74b4ca85716d6813581ddb23da6`
**Scope**: All uncommitted changes since the base commit
**Result**: RESOLVED

## Review Surface

**Files reviewed** (all changes since the base commit):

- `.spec_system/PRD/phase_01/PRD_phase_01.md` - tracked-modified
- `.spec_system/PRD/phase_01/session_04_managed_runtime_and_model_policy.md`
  - tracked-modified
- `.spec_system/state.json` - tracked-modified
- `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/spec.md`
  - initially untracked session specification
- `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/tasks.md`
  - initially untracked task checklist
- `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/implementation-notes.md`
  - initially untracked implementation evidence
- `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/code-review.md`
  - review artifact created by this workflow
- `backend/packages/txt2crs/pyproject.toml` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/ai/__init__.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py` -
  tracked-modified
- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py` - initially
  untracked
- `backend/packages/txt2crs/src/txt2crs/ai/model_policy.py` - initially
  untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/004_delivery_notifications.sql`
  - initially untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/notifications.py` - initially
  untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/research/__init__.py` -
  tracked-modified
- `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py` -
  initially untracked
- `backend/packages/txt2crs/src/txt2crs/research/mcp_server.py` -
  tracked-modified
- `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/contract/test_managed_research_mcp.py`
  - initially untracked
- `backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/factories.py` - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_generation_request_store.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/unit/test_delivery_notifications.py`
  - initially untracked
- `backend/packages/txt2crs/tests/unit/test_gpt56_model_policy.py` -
  initially untracked
- `backend/packages/txt2crs/tests/unit/test_job_runtime_resources.py` -
  initially untracked
- `backend/packages/txt2crs/tests/unit/test_job_service.py` -
  tracked-modified
- `backend/packages/txt2crs/tests/unit/test_runtime.py` - tracked-modified
- `backend/uv.lock` - tracked-modified

There were no staged files and no commits after the base commit. Every
initially untracked file was read in full. All such files are ASCII text source,
tests, SQL, or Apex Spec workflow records; no binary or generated artifact
required byte-level review.

**Inventory commands**: `git status --short`,
`git log --oneline "$BASE"..HEAD`, `git diff --stat "$BASE"`,
`git diff --cached --stat "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

- `backend/packages/txt2crs/src/txt2crs/jobs/store.py:125` - Migration 004
  used SQLite `executescript`, whose implicit transaction boundary allowed
  schema changes to survive while the matching migration-version record rolled
  back. A retry could then replay one-time `ALTER TABLE` statements, and
  concurrent constructors could race after observing the same version. Fix:
  acquire a writer lock with `BEGIN IMMEDIATE`, split only complete SQLite
  statements, execute schema changes and version records in one transaction,
  roll back the whole migration set on failure, and close construction-time
  connections on every `BaseException`. Added failed-version-four rollback
  and migration-retry regressions. Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py:139` - Managed
  MCP construction, registry inspection, shutdown timeout, and unexpected
  server-thread exit could expose raw private errors or retain a connectable
  pre-bound listener. Fix: translate ordinary failures into stable typed
  lifecycle errors, retain only a failure boolean instead of a traceback,
  revoke the URL on every exit, and close the owned socket even when a broken
  controller ignores shutdown. Added construction, registry, shutdown, and
  unexpected-exit regressions. Status: FIXED.

### Medium

- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py:41` - An external
  temporary, HTTP, or MCP context manager could raise during `__exit__` and
  replace the primary generation failure. Fix: register safe per-resource
  exits that raise a stable cleanup error only when there is no primary error,
  otherwise annotate and preserve the primary error. The same rule is applied
  to Codex adapter cleanup. Added primary-error and cleanup-only regressions.
  Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py:169` - The managed
  provider pipeline context closed immediately after `generate`, before final
  checkpoint acceptance and result extraction. A lazy provider-backed result
  could therefore be read after its resources were gone. Fix: keep final
  checkpoint validation, rendered artifact access, and usage extraction inside
  the provider context. Added an open-through-extraction regression. Status:
  FIXED.
- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py:204` - The composed
  provider session yielded its runtime without verifying full readiness, so a
  misconfigured or API-key-backed adapter could escape the managed boundary.
  Fix: call the runtime readiness contract after all dependencies are composed
  and before yielding; reject the session with a stable readiness error while
  unwinding every owned resource. Added a not-ready adapter regression.
  Status: FIXED.

### Low

- `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py:373` - The
  loopback check special-cased the hostname `localhost`, even though the
  session contract requires an explicit numeric loopback bind and hostname
  resolution can vary. Fix: accept only numeric IP addresses for which
  `ip_address(...).is_loopback` is true. Added IPv4, IPv6, hostname, wildcard,
  and public-address parameterized coverage. Status: FIXED.

## Assumptions and Deliberate Non-Fixes

- Live GPT-5.6 plus Tavily acceptance remains intentionally gated by
  `TXT2CRS_RUN_LIVE_CODEX=1`, an exact `TXT2CRS_MODEL_ID`, and real
  subscription credentials. The default suite proves the gate and reports one
  explicit skip; it does not claim a credentialed provider run.
- `gpt-5.6` remains the exact configured target. Official OpenAI documentation
  says that identifier aliases `gpt-5.6-sol`, but this implementation does not
  substitute the alias, select another discovered model, or add fallback
  behavior.
- A shutdown timeout cannot forcibly terminate an arbitrary Python thread.
  The safe contract instead revokes publication and closes the owned listener
  immediately; the server thread is daemonized and retains no connectable MCP
  endpoint.
- No shell, database, route, UI, or product surface changed. Application-shell
  review and UI product/craft review are N/A.

## Behavior Changes

- Package SQLite migrations are serialized and atomic with their version
  records, including upgrade failure.
- Each job receives fresh counters and cancellation state, and all provider
  resources unwind in reverse dependency order without masking the primary
  job error.
- Research MCP publishes only a verified, live numeric-loopback endpoint with
  exactly `research_search` and `research_extract`.
- Provider sessions reject non-ready Codex composition before any pipeline can
  use it and remain open through result extraction.
- Every turn uses the exact configured GPT-5.6 identity after exact discovery;
  no nearby alias or fallback is selected.
- Delivery completion persists explicit notification state
  `version=1`, `mode=disabled`, `status=not_applicable` and performs no sink
  call.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Required project analysis | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Active Session 04 and the engine package context resolved. |
| Review base | `git rev-parse 118695b4ca97e74b4ca85716d6813581ddb23da6` | PASS | Exact session base commit exists; no later commit or staged file exists. |
| Tests-first migration review | Failed-version-four rollback regression before repair | EXPECTED FAIL | Schema columns survived even though the version remained 3, proving the atomicity defect. |
| Tests-first provider cleanup review | MCP `__exit__` failure with a primary generation exception before repair | EXPECTED FAIL | The private cleanup exception replaced the primary exception. |
| Tests-first managed MCP review | Construction, registry inspection, timeout, and unexpected-exit regressions before repair | EXPECTED FAIL | Raw exceptions or a still-bound listener violated the managed lifecycle contract. |
| Tests-first executor lifetime review | Provider-open assertion during result extraction before repair | EXPECTED FAIL | The provider context was already closed while extracting returned values. |
| Tests-first readiness review | Not-ready composed runtime before repair | EXPECTED FAIL | The factory yielded the API-key-shaped adapter instead of rejecting it. |
| Tests-first bind review | `localhost` rejection regression before repair | EXPECTED FAIL | A hostname was accepted despite the explicit numeric-loopback contract. |
| Focused repaired tests | Managed MCP, job runtime resources, executor, SQLite migration, model/runtime, and notification suites | PASS | All review regressions and the surrounding focused behavior pass. |
| Full tests | `uv run --package txt2crs pytest -q` | PASS | 402 passed; 1 live credential-gated test skipped. |
| Linter | `uv run --package txt2crs ruff check .` | PASS | All 127 files lint-clean. |
| Formatter | `uv run --package txt2crs ruff format --check .` | PASS | All 127 files formatted. |
| Type checker | `uv run --package txt2crs mypy` | PASS | No issues in 127 source files. |
| Security/privacy inspection | Targeted source and diff scans for credentials, debug markers, non-loopback publication, raw provider details, model fallback, and unbounded lifecycle waits | PASS | No hardcoded secret, fallback, private discovery value, public listener, or unbounded provider wait remains. |
| Final diff check | `git diff --check` plus full diff and untracked-file review | PASS | No whitespace error, unresolved finding, unrelated shell change, staged file, or mid-session commit remains. |

## Summary

1. Reviewed 34 pre-report implementation/workflow files since the base commit
   plus this report: 22 tracked modifications and 12 initially untracked text
   files.
2. Findings: 0 Critical, 2 High, 3 Medium, and 1 Low. All six findings were
   repaired with tests-first regressions.
3. The complete credential-free suite, Ruff format/lint, strict mypy,
   security/privacy inspection, and the final diff check pass.
4. No unresolved finding or review blocker remains.

## Next Command

`validate`
