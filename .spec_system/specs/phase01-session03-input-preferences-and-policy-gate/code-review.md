# Code Review and Repair Report

**Session ID**: `phase01-session03-input-preferences-and-policy-gate`
**Package**: `backend/packages/txt2crs`
**Reviewed**: 2026-07-19
**Base Commit**: `70ce4599cbf9bd212b226e6328b8763318561d3e`
**Scope**: All changes since the base commit (uncommitted work plus
mid-session commits)
**Result**: RESOLVED

## Review Surface

**Files reviewed** (all changes since the base commit):

- `.spec_system/PRD/phase_01/PRD_phase_01.md` - tracked-modified
- `.spec_system/PRD/phase_01/session_03_input_preferences_and_policy_gate.md`
  - tracked-modified
- `.spec_system/state.json` - tracked-modified
- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/spec.md`
  - untracked session specification
- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/tasks.md`
  - untracked task checklist
- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/implementation-notes.md`
  - untracked implementation evidence
- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/code-review.md`
  - untracked review artifact created by this workflow
- `backend/packages/txt2crs/src/txt2crs/generation/__init__.py` -
  tracked-modified
- `backend/packages/txt2crs/src/txt2crs/generation/models.py` -
  tracked-modified
- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py` -
  tracked-modified
- `backend/packages/txt2crs/src/txt2crs/generation/preferences.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py` -
  tracked-modified
- `backend/packages/txt2crs/src/txt2crs/ingestion/routing_url.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/preparation.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` -
  tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/security/policy.py` - tracked-modified
- `backend/packages/txt2crs/tests/factories.py` - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py` -
  tracked-modified
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/unit/test_content_policy.py` -
  tracked-modified
- `backend/packages/txt2crs/tests/unit/test_generation_preparation.py` -
  untracked
- `backend/packages/txt2crs/tests/unit/test_generation_requests.py` -
  tracked-modified
- `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py`
  - untracked
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` -
  tracked-modified
- `backend/packages/txt2crs/tests/unit/test_public_package_exports.py` -
  untracked
- `backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py` -
  untracked

There were no staged files and no mid-session commits after the base commit.
Every untracked file was read in full. All untracked files are UTF-8/ASCII text
source, tests, or Apex Spec workflow records; no binary/generated artifact
required byte-level review.

**Inventory commands**: `git status --short`,
`git log --oneline "$BASE"..HEAD`, `git diff --stat "$BASE"`,
`git diff --cached --stat "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py:173` - A
  checkpoint labeled as an early stage could contain later artifacts, allowing
  resume to skip required generation and local acceptance gates. Fix: added
  stage-specific forbidden-artifact validation and a tampered
  `design_course` regression. Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py:309` - Rendering and
  delivery parsed a final pipeline checkpoint without binding its row or
  request hash to the stored job request, so a structurally valid transplanted
  bundle could be delivered. Fix: centralized row/stage/sequence/request
  validation and added a real-SQLite foreign-checkpoint delivery regression.
  Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py:169` - Ordinary lazy
  pipeline-factory exceptions occurred outside failure settlement, leaving the
  prepared job runnable and eligible for a provider-startup hot loop. Fix:
  moved construction, generation, final-checkpoint acceptance, and result
  extraction under one settlement boundary while preserving `SystemExit`
  replacement behavior. Added a terminal factory-failure regression. Status:
  FIXED.

### Medium

- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py:226` and
  `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py:303` - Direct
  projection accepted mismatched job/request identities and preparation or
  pipeline checkpoints from another request. Fix: fail closed on both identity
  boundaries and retain the context-free public projection error. Added job
  and checkpoint mismatch privacy regressions. Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/ingestion/routing_url.py:48` - The
  injected normalizer annotation was trusted at runtime; bytes output caused an
  `AttributeError` and could reach the unvalidated `model_copy` path. Fix:
  require a string before host parsing or child selection and add a zero-call
  adapter regression. Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/generation/models.py:27` - Concrete
  preferences capped derived learning goals at 12 while the stored
  `CurriculumShapeLimits` and `CoursePlan` contracts permit up to 100
  objectives. A locally valid custom profile could therefore fail after plan
  acceptance. Fix: align derived concrete goals to the 100-objective contract
  and add a 13-objective resolver regression. Status: FIXED.

### Low

- `backend/packages/txt2crs/tests/unit/test_generation_preparation.py:169` -
  The production adapter-output type and normalized-character gates existed
  but neither failure branch was exercised, despite the task evidence claiming
  bounded adapter validation. Fix: added wrong-input-type and stored-limit
  regressions. Status: FIXED.
- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/implementation-notes.md:6`
  and `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/tasks.md:70`
  - Session metadata still reported 15/24 tasks and pointed back to
  `implement`. Fix: synchronized progress and changed the handoff to
  `validate` after resolved review. Status: FIXED.

## Assumptions and Deliberate Non-Fixes

- The first post-repair full-suite invocation intermittently failed
  `test_stream_detects_mutation_between_hash_and_descriptor_recheck`, a file
  unchanged since the base commit. The exact targeted test immediately passed,
  and the complete suite then passed with 359 tests. No unrelated artifact
  reader or test change was made because the failure was not reproducible and
  no session diff touched that behavior.
- Live Codex subscription acceptance remains intentionally gated by
  `TXT2CRS_RUN_LIVE_CODEX=1`; credentialed provider execution is outside this
  session and the default suite reports the explicit skip.
- No UI files or product surfaces changed. UI product-surface and craft review
  are N/A.

## Behavior Changes

- Invalid or future-filled checkpoint artifacts now fail before resume.
- Final delivery and public projection now reject any job, request, row, or
  checkpoint identity mismatch.
- Ordinary provider-graph construction failures settle the job as
  `generation_failed`; abrupt process replacement still remains resumable.
- URL router normalizer implementations must return a string.
- Concrete derived preferences can carry every objective permitted by the
  stored curriculum contract.
- Preparation output type and normalized-size behavior is unchanged but now
  regression-covered.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Required project analysis | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Active Session 03 and monorepo context resolved. |
| Review base | `git rev-parse 70ce4599cbf9bd212b226e6328b8763318561d3e` | PASS | Exact spec base commit exists. |
| Tests-first review regressions | `uv run --package txt2crs pytest -q tests/unit/test_routing_url_ingestion.py tests/unit/test_learning_preference_resolution.py tests/unit/test_generation_preparation.py tests/integration/test_generation_pipeline.py tests/integration/test_generation_job_executor.py tests/unit/test_public_job_queries.py` | EXPECTED FAIL | 6 failures isolated the router, goal bound, checkpoint stage, factory settlement, delivery identity, and projection identity defects; 58 passed. |
| Focused repaired tests | Same six-file pytest command after repairs | PASS | 64 passed. |
| Full tests | `uv run --package txt2crs pytest -q` | PASS | Final rerun: 359 passed, 1 live credential-gated test skipped. |
| Intermittent full-test audit | `uv run --package txt2crs pytest -q tests/unit/test_filesystem_artifact_store.py::test_stream_detects_mutation_between_hash_and_descriptor_recheck -vv` | PASS | The one unchanged test that failed on the first full run passed immediately in isolation; the full rerun also passed. |
| Linter | `uv run --package txt2crs ruff check .` | PASS | All 119 files lint-clean. |
| Formatter | `uv run --package txt2crs ruff format --check .` | PASS | All 119 files formatted. |
| Type checker | `uv run --package txt2crs mypy` | PASS | No issues in 119 source files. |
| Security/privacy inspection | Targeted `rg` scan for debug markers, secrets, removed caller inputs, and private public-projection fields, plus sentinel projection tests | PASS | No hardcoded secret, debug artifact, caller-supplied execution value, or private preparation/provider field crosses the reviewed boundary. No dependency, SQL, auth, or logging change occurred. |
| ASCII/LF audit | Shell loop over `git diff --name-only` plus `git ls-files --others --exclude-standard` using non-ASCII and carriage-return scans | PASS | 29 pre-report files: zero non-ASCII, zero CRLF, zero missing final newlines. |
| Final diff re-read | `git diff "$BASE"`, `git diff --cached "$BASE"`, and full reads of every untracked text file | PASS | All changed hunks mapped to T001-T024; no unresolved finding, debug artifact, incomplete task, staged file, or mid-session commit remains. |

## Summary

1. Reviewed 29 implementation/workflow files since base commit plus this review
   report; the surface contains 19 tracked modifications and 10 initially
   untracked text files.
2. Findings: 0 Critical, 3 High, 3 Medium, and 2 Low. All eight findings were
   repaired and regression-tested.
3. The only deliberate non-fix is a non-reproducible failure in an unchanged
   filesystem-artifact test; its targeted rerun and the complete rerun passed.
4. Focused tests, the full credential-free suite, Ruff format/lint, strict
   mypy, privacy/security inspection, and the final diff re-read all pass.

## Next Command

`validate`
