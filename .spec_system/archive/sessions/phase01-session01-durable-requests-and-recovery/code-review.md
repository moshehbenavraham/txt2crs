# Code Review and Repair Report

**Session ID**: `phase01-session01-durable-requests-and-recovery`
**Package**: backend/packages/txt2crs
**Reviewed**: 2026-07-19
**Base Commit**: c56fa822e2f5f62d64ea427ae56739fd5c17ce4d
**Scope**: All changes since the base commit (uncommitted work plus mid-session commits)
**Result**: RESOLVED

## Review Surface

**Files reviewed** (all changes since the base commit):

- `.spec_system/PRD/PRD.md` - tracked-modified
- `.spec_system/state.json` - tracked-modified
- `.spec_system/PRD/phase_01/PRD_phase_01.md` - untracked
- `.spec_system/PRD/phase_01/session_01_durable_requests_and_recovery.md` - untracked
- `.spec_system/PRD/phase_01/session_02_safe_queries_and_artifact_access.md` - untracked
- `.spec_system/PRD/phase_01/session_03_input_preferences_and_policy_gate.md` - untracked
- `.spec_system/PRD/phase_01/session_04_managed_runtime_and_model_policy.md` - untracked
- `.spec_system/PRD/phase_01/session_05_public_facade_and_owner_lifecycle.md` - untracked
- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/spec.md` - untracked
- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/tasks.md` - untracked
- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/implementation-notes.md` - untracked
- `.spec_system/specs/phase01-session01-durable-requests-and-recovery/code-review.md` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/README_migrations.md` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/migrations/003_generation_requests.sql` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/models.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/quota.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/request_store.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - tracked-modified
- `backend/packages/txt2crs/tests/factories.py` - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_admission_quotas.py` - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_generation_request_store.py` - untracked
- `backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py` - tracked-modified
- `backend/packages/txt2crs/tests/unit/test_generation_requests.py` - untracked
- `backend/packages/txt2crs/tests/unit/test_job_service.py` - tracked-modified

No mid-session commits, staged files, generated files, or binary files were
present. Ignored wheel and source-distribution build outputs were inspected
during implementation but are not part of the Git review surface.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py:168` - Arbitrary
  `InputPayload.metadata` can be silently normalized (`NaN` and infinity
  become `null`), change type during JSON conversion, escape the input byte
  budget, or raise a provider-specific serialization exception. That breaks
  exact recovery and the stable safe-error contract. | Fix: add explicit
  finite-JSON validation and copying, a profile-owned metadata byte ceiling,
  single-snapshot serialization, and exact round-trip/mutation tests before
  canonical persistence. | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/request_store.py:78` - The safe
  compatibility error explicitly chains the underlying Pydantic/JSON error.
  A traceback can therefore reveal the canonical request and learner input
  even though the outer message is safe. | Fix: suppress the sensitive
  cause and context at both repository and package boundaries, hide input in
  frozen-contract validation strings, and test the formatted traceback plus
  exception object. | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py:219` - A caller can
  reserve fewer input/output tokens than the immutable run profile can spend,
  bypassing the admission quota's worst-case resource accounting. | Fix:
  reject under-reserved new work inside the transaction, align shared
  fixtures, and retain exact-replay conflict ordering. | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py:159` - Owner and
  idempotency identifiers were written before `JobRecord` validation. Invalid
  values could commit three durable rows and then fail while constructing the
  return value; strip-normalized values could become unreadable. | Fix:
  normalize and validate a private submission identity before serialization
  or `BEGIN`, with context-free typed errors and zero-row tests. | Status:
  FIXED

### Medium

- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py:221` - The convenience
  factory hashes caller values before Pydantic normalizes and validates them.
  Valid strip-normalized identifiers therefore fail with a false hash
  mismatch, and oversized input is encoded before the cheap byte-limit
  rejection. | Fix: validate a private hashless request identity first, then
  hash the normalized snapshot. | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py:30` - Audience, prior
  knowledge, learning-goal count, and per-goal lengths exceeded the
  authoritative P0 transport limits. | Fix: use the plan's 500/2,000/10 and
  3-500 constraints with parameterized boundary tests. | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py:34` - Any identifier
  was accepted as `request_version`, so recovery could treat an unsupported
  future contract as current. | Fix: constrain the version to the one
  implemented literal and test future-version rejection. | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py:343` - Service resume and
  worker discovery assembled job, request, and checkpoint across separate
  lock acquisitions, allowing one-process writer interleaving. | Fix: add one
  lock-scoped store snapshot and make both callers delegate to it. | Status:
  FIXED

### Low

- `backend/packages/txt2crs/src/txt2crs/jobs/store.py:53` - The idempotency
  conflict docstring still says "different input" even though the key now
  protects the complete request. | Fix: update the boundary documentation. |
  Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py` - Review repairs pushed
  the persistence module to 693 lines, above the repository's rough cohesion
  range. | Fix: extract request-envelope SQL and integrity restoration into
  the 114-line `request_store.py` helper while leaving transaction and public
  error ownership in `SqliteJobStore`; the store returned to 664 cohesive
  lines without changing behavior. | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- The released physical `jobs.input_hash` column remains unchanged. Migration
  001 is immutable, migration 003 is authoritative, and all Python callers now
  expose `request_hash`; renaming the old column would create upgrade risk
  without changing behavior.
- `InputPayload` is an older mutable nested contract. The accepted request is
  copied through normalized validation, and serialization recomputes the hash
  before every write, so post-construction mutation fails closed. Replacing
  the shared ingestion contract or inventing a parallel payload type would be
  outside this session and is unnecessary for durable integrity.
- Runnable discovery does not lease work because Phase 00 explicitly fixes
  the deployment to one process and one serial worker. The query remains
  deterministic and bounded; multi-worker leasing would expand the approved
  architecture.
- A migrated version-2 active job without a request envelope fails closed
  rather than being skipped. This matches the exact-recovery requirement and
  prevents a replacement worker from silently substituting current defaults.
- `provider_consent=False` remains representable in the immutable request.
  Session 03 owns the provider-free submission preflight that prevents such a
  request from becoming a new job; this session must persist the full policy
  context and existing executor coverage still fails it before provider work.
- The request contains private learner data by product requirement. It remains
  confined to owner-private SQLite with no logging or response projection;
  Session 05 explicitly owns idempotent owner erasure across engine state.

## Behavior Changes

- Metadata must now be finite JSON and fit the execution profile's persisted
  metadata-byte ceiling; tuples, sets, dates, arbitrary objects, cycles,
  `NaN`, and infinity fail safely instead of being coerced.
- Request creation normalizes and validates before hashing; serialization
  uses one detached snapshot and rejects any later nested payload mutation
  with a context-free safe error.
- P0 preference and request-version limits now match the authoritative plan.
- New jobs must validate/normalize owner and idempotency identifiers and must
  reserve at least the execution profile's input/output token ceilings.
- Resume and runnable discovery now return one process-local lock-scoped
  job/request/checkpoint snapshot.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Deterministic state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Phase 01 Session 01 located; monorepo package is `backend/packages/txt2crs`. |
| Scope inventory | `git status --short`; `git log --oneline "$BASE"..HEAD`; `git diff --stat "$BASE"`; `git diff --cached --stat "$BASE"`; `git ls-files --others --exclude-standard` | PASS | 28 final files found, no commits or staged changes. |
| Source-of-truth read | Full reads of `CONVENTIONS.md`, `CONSIDERATIONS.md`, session `spec.md`, `tasks.md`, and `implementation-notes.md` | PASS | All 23 implementation tasks map to concrete changed files and evidence. |
| Test-first finding proof | Targeted pytest commands for metadata/error cases, P0 preference bounds, unsupported version, atomic resume delegation, token under-reservation, and invalid identities | PASS | Observed 8, 5, 1, 1, 1, and 3 expected failures respectively before production repairs. |
| Focused repaired behavior | `uv run --package txt2crs pytest -q tests/unit/test_generation_requests.py tests/integration/test_generation_request_store.py`; focused store/quota/service/executor command | PASS | 50 request tests and 36 cross-store/service tests passed. |
| Concurrent replay stability | Ten runs of `uv run --package txt2crs pytest -q tests/integration/test_generation_request_store.py::test_concurrent_exact_replay_commits_one_durable_request` | PASS | 10/10 runs committed exactly one job/request/admission set. |
| Full tests | `uv run --package txt2crs pytest -q` | PASS | 274 passed; only the explicit `TXT2CRS_RUN_LIVE_CODEX=1` acceptance test skipped. |
| Linter | `uv run --package txt2crs ruff check .` | PASS | All 107 engine source/test files passed. |
| Formatter | `uv run --package txt2crs ruff format --check .` | PASS | All 107 files already formatted. |
| Type checker | `uv run --package txt2crs mypy` | PASS | Strict mypy reported no issues in 107 source files. |
| Package build | `uv build --package txt2crs`; `unzip -l` and `tar -tzf` filtered inspections | PASS | Wheel and sdist contain `requests.py`, `request_store.py`, and migration 003. |
| Security checklist | Targeted inspection against `security-compliance-checklist.md`; changed-file secret/log search | PASS | Parameterized SQL only; no new dependencies, secrets, raw-input logs, shell calls, paths, or public payload exposure. Erasure remains explicit Session 05 scope. |
| Encoding/whitespace | 28-file PCRE non-ASCII scan, CR scan, `file --mime-encoding`, and `git diff --check "$BASE"` | PASS | All 28 files are US-ASCII/LF with no whitespace errors. |
| Final diff re-read | `git diff "$BASE"` plus full reads of every untracked text file | PASS | All 28 files re-read; no unresolved finding, debug artifact, or unrelated edit remains. |

## Summary

1. Reviewed all 28 changed or untracked files since the exact base commit,
   including all session planning/evidence artifacts and every production/test
   hunk.
2. Found four high, four medium, and two low issues; every finding is fixed
   with targeted regression coverage or a behavior-preserving extraction.
3. Recorded six evidence-backed deliberate non-fixes/scope decisions that
   preserve the released schema, one-process topology, ingestion/policy
   boundaries, and planned erasure lifecycle.
4. Full tests, Ruff format/lint, strict mypy, package build/archive inspection,
   security checks, ASCII/LF checks, and final diff re-read all pass.
