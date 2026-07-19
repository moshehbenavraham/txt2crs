# Code Review and Repair Report

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Package**: `backend/packages/txt2crs`
**Reviewed**: 2026-07-19
**Base Commit**: `2e2c022265d802e127893fb9d328a4e0ba60211e`
**Scope**: All uncommitted changes since the base commit
**Result**: RESOLVED

## Review Surface

The review covered every tracked modification and initially untracked file
since the recorded base commit:

- Phase/session PRDs, `.spec_system/state.json`, and the Session 05
  specification, tasks, and implementation evidence.
- `README_txt2crs.md` and the root/application package exports.
- All five new application modules: configuration, facade, factories, owner
  lifecycle, and package exports.
- SQLite store, artifact reader/store, and in-memory artifact protocol changes.
- Canonical test factories and all new/modified unit, contract, integration,
  public-import, SQLite, filesystem, and deterministic lifecycle tests.
- This review report.

There were no staged files, no commits after the base commit, and no binary or
generated files in the review surface. All initially untracked files were read
in full. Inventory used `git status --short`, `git log`, tracked/cached diffs,
and `git ls-files --others --exclude-standard`.

## Findings by Severity

### Critical

No findings.

### High

- `src/txt2crs/application/facade.py` - Owner purge could run while an
  owner-bound executor was already delivering. Artifact deletion could finish,
  SQLite deletion could commit, and the still-running executor could then
  recreate the owner artifact directory before its next database operation
  failed. Fix: executor close now requests cancellation and waits for active
  execution to settle; facade purge closes only the target owner's tracked
  handles before artifact-first deletion. Added an active-executor barrier
  regression. Status: FIXED.
- `src/txt2crs/jobs/store.py` - `COMMIT` was outside the purge transaction's
  exception boundary. A commit failure left the deletion visible on the open
  connection and the transaction unusable for retry. The returned count also
  was not checked against actual deleted parent rows, allowing a trigger to
  suppress deletion without preventing success. Fix: commit inside the guarded
  transaction, roll back commit failures, and require delete rowcount to match
  the pre-delete count. Added rejected-commit and suppressed-delete retry
  regressions. Status: FIXED.

### Medium

- `src/txt2crs/application/facade.py` - Methods checked open state and then
  released the lock before delegation, so close could shut SQLite beneath a
  call that had already been admitted. Concurrent duplicate close could also
  return before the first cleanup completed. Fix: serialize the complete
  facade call/cleanup boundary with the application lock and retain
  all-resource cleanup behavior. Added a blocking-submit close regression.
  Status: FIXED.
- `src/txt2crs/application/facade.py` - Strongly retaining every executor
  handle until process shutdown accumulated complete provider/pipeline graphs
  after jobs were done. Fix: use weak handle tracking; a running worker or
  caller remains strongly owned while completed abandoned handles can be
  collected. Added a garbage-collection regression. Status: FIXED.
- `src/txt2crs/application/config.py` - Direct Pydantic construction could
  bypass the deterministic scenario helpers with a non-object turn or invalid
  evidence JSON. Fix: validate, finite-check, and canonicalize both JSON
  fields at the model boundary. Added direct-construction regressions.
  Status: FIXED.
- `src/txt2crs/application/config.py` - Private state and credential roots
  could be nested or traverse an existing parent symlink, and unsafe MCP hosts
  were rejected only when the managed server eventually started. Fix: reject
  symlink ancestry and overlapping private roots, and require an explicit
  numeric loopback address during configuration validation. Added path and
  host regressions. Status: FIXED.

### Low

- `src/txt2crs/application/facade.py` - Authentication and purge method return
  annotations erased strict package contracts to `Any`. Fix: publish exact
  `SystemAuthenticationSnapshot` and `OwnerPurgeResult` types and test the
  annotations. Status: FIXED.
- `src/txt2crs/application/owner_lifecycle.py` - Purge result counts accepted
  negatives, and an invalid structurally typed store value could escape as a
  Pydantic error rather than the stable purge error. Fix: constrain result
  fields and translate every non-integer, boolean, or negative count before
  result construction. Added contract and coordinator regressions.
  Status: FIXED.
- `tests/unit/test_filesystem_artifact_store.py` - The descriptor mutation
  race changed content without changing size; a temporary filesystem could
  report the same timestamp within one clock tick, making the test flaky.
  Fix: make the injected mutation change both content and size. The regression
  passed 20 consecutive isolated runs and the complete suite. Status: FIXED.

## Assumptions and Deliberate Non-Fixes

- The real GPT-5.6 plus Tavily acceptance remains intentionally gated by
  `TXT2CRS_RUN_LIVE_CODEX=1` and real subscription credentials. The default
  suite reports one explicit skip and makes no credentialed-live claim.
- A cancellation wait is bounded by the finite timeouts already enforced on
  the real provider graph. Python cannot forcibly terminate an arbitrary
  external blocking call; the application prevents purge from claiming
  success until the tracked executor actually settles.
- `default_execution_profile` is not treated as an equality requirement for
  recovered jobs. Durable requests intentionally retain their exact accepted
  profile across application restart; the exact configured GPT-5.6 identity
  remains the required invariant.
- The application factory keeps URL-ingestion adapters and their thread-safe
  HTTP client process-scoped. Research HTTP, budget, cancellation, retry,
  guardrail, MCP, temporary worker, Codex adapter, coordinator, and pipeline
  state remain fresh and job-scoped.
- No FastAPI shell, PostgreSQL model, frontend, hosted deployment, SMTP, or
  additional provider entered the session. UI product/craft review is N/A.

## Behavior Changes

- Shells now use one strict public application facade and select a real or
  deterministic factory without assembling private engine modules.
- Every executor is owner/job-bound, one-shot, cancelable, wait-closeable, and
  backed by fresh mutable runtime state.
- Owner purge stops tracked owner work, deletes only the confined hashed owner
  artifact tree, then atomically deletes all owner jobs and cascaded rows.
- Real configuration rejects secret/state aliasing and non-loopback MCP binds
  before construction. Provider resources remain lazy until execution or an
  explicit readiness probe.
- Deterministic composition exercises production persistence, preparation,
  pipeline, rendering, artifact, recovery, and purge behavior while replacing
  only provider outputs.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence |
|-------|-----------------------|--------|----------|
| Review base and inventory | Git base/log/status/diff/untracked inspection | PASS | Exact base exists; no later commit or staged change; all files reviewed. |
| Tests-first commit repair | Rejected SQLite `COMMIT` before repair | EXPECTED FAIL | Deleted row remained invisible on the open transaction and retry was not clean. |
| Tests-first delete-count repair | Trigger-suppressed parent delete before repair | EXPECTED FAIL | Purge returned a success count while the owner job remained. |
| Tests-first close synchronization | Blocking admitted submit before repair | EXPECTED FAIL | Cleanup callback ran while the facade operation was still active. |
| Tests-first active purge repair | Blocking owner executor before repair | EXPECTED FAIL | Purge did not request cancellation and deletion began before execution settled. |
| Tests-first retention repair | Closed executor weak-reference before repair | EXPECTED FAIL | The application retained the complete closed handle graph. |
| Tests-first strict contracts | Direct JSON, path/host, return annotation, and count regressions | EXPECTED FAIL | Invalid values or erased types crossed the public boundary. |
| Focused repaired tests | Session facade/factory/purge/store/artifact/executor/import selection | PASS | 79 passed. |
| Complete engine tests | `uv run --package txt2crs pytest -q` | PASS | 444 passed; 1 credential-gated live test skipped. |
| Formatting and lint | Ruff format plus `ruff check .` | PASS | All reviewed source and tests are formatted/lint-clean. |
| Strict types | `uv run --package txt2crs mypy` | PASS | No issues in 136 source files. |
| Distribution | Isolated `uv build`, tar/unzip/metadata inspection | PASS | Wheel/sdist contain all application modules and updated documentation. |
| Repository engine gate | `bash scripts/validate-changes.sh engine --json` | PASS | Engine lint, typecheck, and tests passed. |
| Security/privacy audit | ASCII/LF, secret, path, fallback/sink, public-host, and error scans | PASS | No secret, raw private path, model fallback, public MCP bind, or partial-success path remains. |
| Final diff | `git diff --check` and whole-diff review | PASS | No whitespace error or unresolved finding remains. |

## Summary

1. Reviewed 25 pre-report implementation/workflow files plus this report:
   13 tracked modifications and 13 initially untracked text files.
2. Findings: 0 Critical, 2 High, 4 Medium, and 3 Low. All findings were
   repaired with tests-first regressions.
3. Focused and complete tests, Ruff, strict mypy, isolated distributions,
   repository validation, and security/privacy inspection pass.
4. No unresolved finding or review blocker remains.

## Next Command

`validate`
