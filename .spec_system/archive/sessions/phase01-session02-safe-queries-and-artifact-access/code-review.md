# Code Review and Repair Report

**Session ID**: `phase01-session02-safe-queries-and-artifact-access`
**Package**: backend/packages/txt2crs
**Reviewed**: 2026-07-19
**Base Commit**: 2944662447bcea279705e3b06fba17216267e72d
**Scope**: All changes since the base commit (uncommitted work plus mid-session commits)
**Result**: RESOLVED

## Review Surface

**Files reviewed** (all changes since the base commit):

- `.spec_system/PRD/phase_01/PRD_phase_01.md` - tracked-modified
- `.spec_system/PRD/phase_01/session_02_safe_queries_and_artifact_access.md` - tracked-modified
- `.spec_system/state.json` - tracked-modified
- `.spec_system/specs/phase01-session02-safe-queries-and-artifact-access/code-review.md` - untracked review report
- `.spec_system/specs/phase01-session02-safe-queries-and-artifact-access/implementation-notes.md` - untracked
- `.spec_system/specs/phase01-session02-safe-queries-and-artifact-access/spec.md` - untracked
- `.spec_system/specs/phase01-session02-safe-queries-and-artifact-access/tasks.md` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py` - tracked-modified
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` - untracked
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py` - tracked-modified
- `backend/packages/txt2crs/tests/factories.py` - tracked-modified
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py` - untracked
- `backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py` - tracked-modified
- `backend/packages/txt2crs/tests/unit/test_job_service.py` - tracked-modified
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` - untracked

There are no staged files and no mid-session commits. Every untracked file is
ASCII text authored for this session; there are no binary or generated
artifacts in the review surface.

**Inventory commands**: `git status --short`,
`git log --oneline 2944662447bcea279705e3b06fba17216267e72d..HEAD`,
`git diff 2944662447bcea279705e3b06fba17216267e72d`,
`git diff --cached 2944662447bcea279705e3b06fba17216267e72d`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py:131` -
  `open_artifact` calls manifest/topology loading outside the context-free
  public error translation used by `get_manifest`; an `OSError` race can
  include the private hashed path in the exception. | Fix: translate manifest
  setup failures only after leaving the exception handler, preserving the
  context-free package integrity error | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py:89` -
  Public `safe_file_name` validation and both writers allow ASCII control
  characters, including CR/LF. Phase 03 must be able to encode this reviewed
  value into `Content-Disposition` without inheriting header-injection input.
  | Fix: centralize pre-write private metadata validation and reject C0, DEL,
  and C1 controls in file names/media types at public, real-store,
  deterministic-store, and retained-manifest boundaries | Status: FIXED

### Medium

- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py:280` -
  Metadata-only manifest reads verify body file type and topology but do not
  compare each regular file's current size with its declared size, so stale
  availability metadata can be returned after truncation or replacement. |
  Fix: compare every non-following body `stat` size to its validated
  descriptor without opening body content | Status: FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py:219` - The
  writer does not enforce the reader's media-type constraints or bounded
  manifest size. `save` can succeed and publish a set that `get`,
  `get_manifest`, and `open_artifact` reject immediately. | Fix: validate
  media/file/content metadata before writes, serialize the manifest once,
  reject it above 128 KiB, and only then create the staging tree | Status:
  FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py:118` - The new
  in-memory creation timestamp is written after the artifact dictionary. A
  failing clock leaves partial state, and an exact retry returns early without
  ever creating readable manifest metadata. Empty sets are also accepted even
  though the real store rejects them. | Fix: validate/copy first, obtain an
  aware timestamp before either map mutation, then publish both maps under one
  lock; reject empty/unsafe sets through the shared writer validator | Status:
  FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py:340` - A failed
  job with private failure code `cancelled` is projected with a cancellation
  message even though its public status remains `failed`. | Fix: accept the
  cancellation code only for authoritative durable `cancelled` status and
  collapse the contradictory failed case to `generation_failed` | Status:
  FIXED
- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py:411` - Query
  strings and URL credentials are removed, but a credential-shaped token in a
  canonical URL path is still reflected into public JSON. | Fix: decode and
  inspect the path for controls/whitespace and secret redaction, omitting the
  entire link if it is not safe to reproduce unchanged | Status: FIXED

### Low

No findings.

## Assumptions and Deliberate Non-Fixes

- Manifest listing remains metadata-only and must not hash or load artifact
  bodies. The safe interpretation of "integrity-checked manifest" is to
  validate the bounded signed-by-construction manifest, exact topology, file
  type, and current file size. Content hashing remains the stream/full-bundle
  boundary because implementation-plan section 5.4 explicitly places the
  open/hash/rewind sequence on single-artifact reads.
- The durable `GenerationRequest.request_hash` and cumulative
  `PipelineCheckpoint.request_hash` are deliberately not compared here.
  Targeted inspection of `jobs/requests.py::_derive_request_hash` and
  `generation/pipeline.py::_derive_pipeline_request_hash` proves they hash
  different contracts: the former includes policy/execution identity, while
  the latter includes raw input plus resolved pipeline preferences. Session 03
  owns that deterministic preference bridge, so equating the hashes in this
  session would reject valid recovered jobs.
- Noncanonical private/debug artifacts remain compatible with private
  whole-bundle recovery. Public manifest projection still fails closed when
  any stored identifier is outside the exact renderer map; this behavior is
  explicitly covered by the session compatibility test.

## Behavior Changes

- Artifact writes now reject control-bearing names/media, non-byte content,
  empty sets, and manifests above the reader's 128 KiB ceiling before
  publishing state.
- Metadata listing now fails integrity when a body's current size differs from
  its descriptor, while still opening only `manifest.json`.
- Stream setup filesystem races now become context-free
  `ArtifactIntegrityError` values with no private path.
- Failed jobs cannot present a cancellation reason unless durable status is
  actually `cancelled`.
- Secret-shaped URL paths are omitted from public source summaries.

## Security and Privacy Spot Check

- Injection: PASS - file-name/media control characters are rejected before
  storage or public metadata; no SQL, shell, or dynamic query surface changed.
- Authentication/authorization: PASS - exact owner hash scoping and the common
  missing/wrong-owner error remain covered by unit and real-store integration
  tests.
- Sensitive exposure: PASS - public projection stays allowlisted; filesystem
  races and malformed checkpoint/manifest failures are context-free; no
  request, evidence, provider, usage, descriptor, or private path is logged.
- Dependencies/configuration/database: N/A - no dependency, runtime
  configuration, PostgreSQL, or engine SQLite schema change exists.
- GDPR/data minimization: PASS for this package boundary - no new personal
  data collection or third-party transfer was added; public output copies only
  bounded reviewed fields and the existing owner deletion path is unchanged.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Deterministic state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Session 02 is active; base commit exists; engine is the declared package. |
| Review inventory | Base-relative Git inventory commands listed above | PASS | 17 pre-report files plus this report reviewed; no staged files or mid-session commits. |
| Tests-first red gate | `uv run --package txt2crs pytest -q tests/unit/test_public_job_queries.py tests/unit/test_filesystem_artifact_store.py tests/unit/test_job_service.py` plus the three control-character cases | PASS | Nine intended behavioral failures were observed first; all three control-character cases then failed before their production repair. |
| Focused tests | `uv run --package txt2crs pytest -q tests/unit/test_public_job_queries.py tests/unit/test_filesystem_artifact_store.py tests/unit/test_job_service.py tests/integration/test_public_job_query_service.py` | PASS | 41 query, storage, service, and real SQLite/filesystem tests passed. |
| Full tests | `uv run --package txt2crs pytest -q` | PASS | 303 passed; the one explicit live Codex subscription test remained gated and skipped. |
| Repository bundle | `bash scripts/validate-changes.sh engine` | PASS | Engine Ruff, mypy, and pytest bundle passed. |
| Linter | `uv run --package txt2crs ruff check .` | PASS | All 112 package files passed. |
| Formatter | `uv run --package txt2crs ruff format --check .` | PASS | All 112 package files were already formatted. |
| Type checker | `uv run --package txt2crs mypy` | PASS | Strict mypy reported no issues in 112 source files. |
| Build | `uv build --package txt2crs --out-dir "$build_directory"` and `unzip -l "$build_directory"/*.whl` | PASS | 0.3.4 wheel/sdist built; artifact query/reader/store, public query, and service modules are in the wheel. |
| Security/privacy scan | Security checklist plus targeted production `rg` inspection | PASS | No logging/printing side channel, secret, dependency, schema, SQL, or shell change; owner/privacy regressions pass. |
| ASCII/LF/whitespace | `git diff --check "$BASE"`, `rg -nP '[^\x00-\x7F]'`, `rg -nU '\r'`, and `file` across the review inventory | PASS | All 18 review files are ASCII text with LF endings and no whitespace errors. |
| Final diff re-read | `git diff "$BASE"` plus full reads of every untracked source/test/session file | PASS | All seven findings are fixed; no debug artifact, unfinished task, or new issue remains. |

## Summary

All 18 review-surface files were inventoried and read against base commit
`2944662`. Findings were 0 critical, 2 high, 5 medium, and 0 low; all seven
were repaired with tests. The full 303-test engine suite, Ruff, strict mypy,
package build, repository engine validation, ASCII/LF audit, and targeted
security/privacy review pass. Nothing was deferred and no blocker remains.
