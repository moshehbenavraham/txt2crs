# Code Review and Repair Report

**Session ID**:
`phase03-session02-owner-scoped-job-results-and-recovery`
**Package**: backend
**Reviewed**: 2026-07-20
**Base Commit**: `d080c4be2fb11e3fd016ca89d7fd495241961356`
**Scope**: All changes since the base commit (uncommitted work plus
mid-session commits)
**Result**: RESOLVED

## Review Surface

The review covered the complete 28-file implementation surface present before
this report: 21 tracked modifications and 7 untracked files. There were no
staged changes or mid-session commits. This report is a review artifact and is
not counted in that implementation total.

**Files reviewed** (all changes since the base commit):

Tracked modifications:

- `.spec_system/state.json` - tracked-modified
- `backend/app/api/routes/jobs.py` - tracked-modified
- `backend/app/core/txt2crs_errors.py` - tracked-modified
- `backend/app/schemas/jobs.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` -
  tracked-modified
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - tracked-modified
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` -
  tracked-modified
- `backend/tests/acceptance/conftest.py` - tracked-modified
- `backend/tests/core/test_txt2crs_errors.py` - tracked-modified
- `backend/tests/schemas/test_job_schemas.py` - tracked-modified
- `backend/tests/scripts/test_generate_client_contract.py` - tracked-modified
- `docs/ARCHITECTURE.md` - tracked-modified
- `docs/api/README_api.md` - tracked-modified
- `docs/runbooks/incident-response.md` - tracked-modified
- `frontend/src/client/index.ts` - tracked-modified, generated
- `frontend/src/client/schemas.gen.ts` - tracked-modified, generated
- `frontend/src/client/sdk.gen.ts` - tracked-modified, generated
- `frontend/src/client/types.gen.ts` - tracked-modified, generated
- `frontend/src/client/core/pathSerializer.gen.ts` - tracked-modified,
  generated
- `frontend/scripts/generate-client.mjs` - tracked-modified
- `scripts/generate-client.sh` - tracked mode change

Untracked files:

- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/implementation-notes.md`
  - untracked
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/spec.md`
  - untracked
- `.spec_system/specs/phase03-session02-owner-scoped-job-results-and-recovery/tasks.md`
  - untracked
- `backend/app/api/artifact_response.py` - untracked
- `backend/tests/acceptance/test_job_results_and_recovery.py` - untracked
- `backend/tests/api/routes/test_jobs_results.py` - untracked
- `backend/tests/api/test_artifact_response.py` - untracked

**Inventory commands**: `git status --short`,
`git log --oneline "$BASE"..HEAD`, `git diff "$BASE"`,
`git diff --cached "$BASE"`, and
`git ls-files --others --exclude-standard`.

Generated files were reviewed through their source OpenAPI operation,
repository generator, static contract regression, TypeScript compilation, and
two byte-identical regeneration runs. They were not edited manually.

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `backend/app/api/artifact_response.py:49` and
  `backend/app/api/artifact_response.py:112` could either strand an already
  entered package context when local body construction failed or replace the
  authoritative response-construction failure when cleanup also failed. |
  Fix: settle package ownership on both construction paths, make cleanup
  best-effort while a primary failure is active, retain idempotent closure,
  and add regressions for body and response construction with simultaneous
  cleanup failure. | Status: FIXED
- `backend/app/api/routes/jobs.py:105` advertised only
  `application/octet-stream`, while the route sends exact HTML, Markdown, PDF,
  or DOCX media types and the generated Fetch client parses text and binary
  responses differently. The resulting generated return type could not
  truthfully describe runtime data. | Fix: document all four exact media
  types, add a wildcard string-or-file fallback for generators that select one
  content entry, regenerate a `string | Blob | File` response type, and lock
  both OpenAPI and TypeScript output with a static regression. | Status: FIXED

### Low

- `docs/api/README_api.md:72`, `docs/api/README_api.md:211`, and the session
  task/spec handoffs contained contract/workflow drift: five routes were
  followed by "Both routes," delivery replay was described as republishing an
  already-rendered set even though the executor deterministically rerenders
  the validated bundle, and completed session artifacts still instructed an
  earlier workflow step. | Fix: identify both submission routes precisely,
  document deterministic rerender/republication and generated response
  shapes, point tasks to `creview` then `validate`, and point the reviewed
  specification to `validate`. | Status: FIXED
- `scripts/generate-client.sh` was mode `0644` even though repository
  documentation consistently invokes it as `./scripts/generate-client.sh`. |
  Fix: set mode `0755`, add an executable-mode contract assertion, and execute
  the documented command successfully. | Status: FIXED
- `backend/tests/acceptance/test_job_results_and_recovery.py:196` opened
  replacement applications and interruption-path executors without lexical
  context ownership, so an earlier failed assertion could bypass cleanup even
  though the happy path closed the application later. | Fix: use application
  and executor context managers throughout every reopen/interruption path. |
  Status: FIXED
- `backend/tests/api/routes/test_jobs_results.py:269` parameterized "missing"
  and "wrong-owner" but discarded the parameter, so both cases executed the
  same private-detail fixture. | Fix: exercise distinct private absence and
  foreign-owner details while requiring the same context-free public 404. |
  Status: FIXED
- `frontend/src/client/core/pathSerializer.gen.ts:130` retained a smart
  apostrophe from upstream openapi-ts output, violating the session's
  ASCII-only deliverable gate whenever the complete generated client directory
  was validated. | Fix: normalize that known upstream punctuation inside the
  repository generator, assert ASCII/LF across every generated client file,
  and regenerate instead of hand-editing output. | Status: FIXED
- `implementation-notes.md` recorded the final seven task intervals beyond
  the current repository clock, making otherwise valid evidence appear
  future-dated. | Fix: preserve task order while correcting the final
  intervals and last-updated value to the actual completed session window. |
  Status: FIXED

## Assumptions and Deliberate Non-Fixes

- The session specification remains `Status: Not Started` until the Apex
  `validate` workflow performs the authoritative session transition. Task and
  review artifacts are complete, but `creview` does not preempt that state
  change.
- The current Hey API generator selects one content entry when deriving a
  response type. The wildcard fallback is deliberate: it keeps the generated
  union truthful, while the four more-specific entries remain the exact HTTP
  contract. Runtime parsing still follows the actual response `Content-Type`.
- Registered Problem Details statuses/media remain generated as `unknown`
  error bodies because this repository centralizes runtime error handling in
  `handleApiError()`. This session's requirement is the safe status/media
  boundary; introducing a repository-wide generated Problem Details model is
  not required to make these three reads safe.
- `frontend/openapi.json` remains an ignored generator input. Provenance is
  established by `scripts/generate-client.sh`, the static contract test, the
  generated tracked files, frontend compilation, and the repeated aggregate
  SHA-256 check.
- The live Codex subscription acceptance remains an explicit opt-in release
  gate. All session behavior, restart boundaries, and artifact delivery are
  covered by the credential-free deterministic suites.

## Behavior Changes

- A local allocation or Starlette response-construction failure now closes
  an entered artifact context exactly once without allowing a cleanup failure
  to replace the primary error.
- OpenAPI and the generated client now describe format-specific artifact
  delivery as `string | Blob | File`, matching Fetch parsing for text and
  binary responses.
- The documented `./scripts/generate-client.sh` command is directly
  executable.
- Client generation normalizes one upstream documentation apostrophe so the
  complete generated tree satisfies repository ASCII/LF conventions.
- Public documentation now matches submission scope and actual deterministic
  delivery recovery.
- Acceptance behavior is unchanged; only test resource ownership and
  wrong-owner coverage were strengthened.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first construction and OpenAPI regressions | `uv run pytest tests/api/test_artifact_response.py tests/scripts/test_generate_client_contract.py -q` with isolated PostgreSQL | EXPECTED FAIL | 2 failed and 12 passed before repair: cleanup masked the construction failure and OpenAPI still exposed only octet-stream |
| Tests-first entered-body ownership regression | `uv run pytest tests/api/test_artifact_response.py::test_body_construction_failure_releases_the_entered_context -q` with isolated PostgreSQL | EXPECTED FAIL | Context exit count was 0 after local body construction failed |
| Tests-first executable generator regression | `uv run pytest tests/scripts/test_generate_client_contract.py::test_generate_client_formats_openapi_document_and_generated_client -q` with isolated PostgreSQL | EXPECTED FAIL | `os.access(..., os.X_OK)` was false at mode `0644` |
| Tests-first generated encoding regression | `uv run pytest tests/scripts/test_generate_client_contract.py::test_generated_client_uses_repository_ascii_and_lf_conventions -q` with isolated PostgreSQL | EXPECTED FAIL | Upstream `pathSerializer.gen.ts` contained one non-ASCII smart apostrophe |
| Repaired generated contract | `uv run pytest tests/scripts/test_generate_client_contract.py -q` with isolated PostgreSQL | PASS | 8 passed, including executable mode, exact media union, and complete generated-tree ASCII/LF |
| Focused repaired surface | `uv run pytest tests/api/test_artifact_response.py tests/api/routes/test_jobs_results.py tests/scripts/test_generate_client_contract.py tests/acceptance/test_job_results_and_recovery.py -q` with isolated PostgreSQL | PASS | 37 passed; only 15 known test-key warnings |
| Recovery acceptance repair | `uv run pytest tests/acceptance/test_job_results_and_recovery.py -q` with isolated PostgreSQL | PASS | 7 passed with application/executor context ownership |
| Engine tests | `uv run --package txt2crs pytest -q` | PASS | 470 passed; 1 explicit live-subscription test skipped |
| Engine linter/formatter/types | `uv run --package txt2crs ruff check .`; `uv run --package txt2crs ruff format --check .`; `uv run --package txt2crs mypy` | PASS | 138 files formatted; no lint or type issue |
| Backend tests | `uv run pytest tests/ -q` with isolated PostgreSQL | PASS | 474 passed; 102 known test/dependency warnings |
| Backend linter/formatter/types | `uv run ruff check app tests`; `uv run ruff format --check app tests`; `uv run mypy app`; `uv run ty check app` | PASS | 104 files formatted; 48 application files mypy-clean; ty passed |
| Frontend gates | `npm run lint`; `npm run typecheck`; `npm run build` | PASS | 138 files checked; TypeScript passed; 2,204 modules built |
| Generated provenance | Two consecutive `./scripts/generate-client.sh` runs plus sorted OpenAPI/generated-file aggregate SHA-256 | PASS | Both complete generated trees hashed to `a8003a411031043393160813b196af1b6bb859724094a9e71c1bbfe4f81cb213` |
| Repository hooks | `pre-commit run --all-files` and `pre-commit run --files "${untracked_files[@]}"` | PASS | Every configured tracked and explicit-untracked hook passed |
| Encoding hygiene | ASCII-byte and carriage-return scan over all 29 changed files including this report | PASS | No non-ASCII byte or CRLF line ending remains |
| Final diff re-read | `git diff "$BASE"` plus every file from `git ls-files --others --exclude-standard` | PASS | No remaining logic, privacy, resource, generated-provenance, or workflow issue |

## Summary

1. Reviewed the complete 28-file base-to-worktree implementation surface.
2. Found 0 critical, 0 high, 2 medium, and 6 low issues.
3. Resolved all eight findings with focused regressions, contract checks, or
   targeted documentation/workflow corrections.
4. Engine, backend, frontend, generated-client, lint, format, type, build, and
   repository-hook gates pass.
5. No finding was deferred and no blocker remains.

Next command: `validate`
