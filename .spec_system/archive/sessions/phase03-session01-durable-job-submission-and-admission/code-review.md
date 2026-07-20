# Code Review and Repair Report

**Session ID**: `phase03-session01-durable-job-submission-and-admission`
**Package**: monorepo
**Reviewed**: 2026-07-20
**Base Commit**: `3dfbd01cf771a67d94b783fdfe269dcb9d357161`
**Implementation Commit**: uncommitted session worktree
**Scope**: Complete base-to-worktree diff plus review repairs
**Result**: RESOLVED

## Review Surface

The review covered the complete 69-file implementation surface present before
this report: 51 tracked modifications and 18 new files. The report itself is a
review artifact and is not counted in that implementation total.

The review emphasized:

- strict authenticated JSON and multipart transport contracts;
- request framing and cumulative body limits;
- bounded PDF and OOXML parsing, archive traversal, active content, and
  decompression limits;
- package-owned preflight, policy, idempotency, and atomic admission;
- shell-to-package mappings and exception translation;
- post-commit worker notification and idempotent terminal replay;
- privacy-safe Problem Details, headers, logs, and generated projections;
- local-only signup, readiness gating, and lifespan dependency ownership;
- acceptance coverage for durable reopen, conflict, quota, and policy paths;
- generated OpenAPI-client provenance and deterministic regeneration; and
- public configuration, API, architecture, onboarding, security, and recovery
  documentation.

### Exact File Inventory

Tracked modifications:

- `.env.example`
- `.spec_system/CONSIDERATIONS.md`
- `.spec_system/PRD/PRD.md`
- `.spec_system/SECURITY-COMPLIANCE.md`
- `.spec_system/audit/audit.md`
- `.spec_system/docs-audit.md`
- `.spec_system/infra/infra.md`
- `.spec_system/pipeline/pipeline.md`
- `.spec_system/specs/phase02-session01-engine-composition-lifecycle/spec.md`
- `.spec_system/specs/phase02-session02-serial-worker-supervisor/spec.md`
- `.spec_system/specs/phase02-session04-system-readiness-and-auth-api/spec.md`
- `.spec_system/specs/phase02-session05-operator-setup-experience/spec.md`
- `.spec_system/specs/phase02-session05-operator-setup-experience/validation.md`
- `.spec_system/state.json`
- `README.md`
- `backend/.env.example`
- `backend/app/api/deps.py`
- `backend/app/api/main.py`
- `backend/app/api/routes/users.py`
- `backend/app/core/config.py`
- `backend/app/core/constants.py`
- `backend/app/core/middleware.py`
- `backend/app/core/rate_limit.py`
- `backend/app/core/txt2crs_errors.py`
- `backend/app/main.py`
- `backend/app/schemas/__init__.py`
- `backend/app/services/__init__.py`
- `backend/packages/txt2crs/src/txt2crs/application/__init__.py`
- `backend/packages/txt2crs/src/txt2crs/application/facade.py`
- `backend/packages/txt2crs/src/txt2crs/application/factories.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`
- `backend/packages/txt2crs/tests/contract/test_application_factories.py`
- `backend/packages/txt2crs/tests/unit/test_application_facade.py`
- `backend/packages/txt2crs/tests/unit/test_public_package_exports.py`
- `backend/tests/api/routes/test_users.py`
- `backend/tests/core/test_middleware.py`
- `backend/tests/core/test_txt2crs_errors.py`
- `backend/tests/core/test_txt2crs_settings.py`
- `backend/tests/scripts/test_generate_client_contract.py`
- `docs/ARCHITECTURE.md`
- `docs/CHANGELOG.md`
- `docs/CONFIGURATION.md`
- `docs/api/README_api.md`
- `docs/environments.md`
- `docs/onboarding.md`
- `docs/runbooks/incident-response.md`
- `frontend/README_frontend.md`
- `frontend/src/client/index.ts`
- `frontend/src/client/schemas.gen.ts`
- `frontend/src/client/sdk.gen.ts`
- `frontend/src/client/types.gen.ts`

New files:

- `.spec_system/PRD/phase_03/PRD_phase_03.md`
- `.spec_system/PRD/phase_03/session_01_durable_job_submission_and_admission.md`
- `.spec_system/PRD/phase_03/session_02_owner_scoped_job_results_and_recovery.md`
- `.spec_system/PRD/phase_03/session_03_account_purge_and_donor_retirement.md`
- `.spec_system/specs/phase03-session01-durable-job-submission-and-admission/implementation-notes.md`
- `.spec_system/specs/phase03-session01-durable-job-submission-and-admission/spec.md`
- `.spec_system/specs/phase03-session01-durable-job-submission-and-admission/tasks.md`
- `backend/app/api/routes/jobs.py`
- `backend/app/schemas/jobs.py`
- `backend/app/services/txt2crs_submission.py`
- `backend/app/services/txt2crs_uploads.py`
- `backend/tests/acceptance/conftest.py`
- `backend/tests/acceptance/test_job_submission.py`
- `backend/tests/api/routes/test_jobs_submission.py`
- `backend/tests/api/test_txt2crs_dependencies.py`
- `backend/tests/schemas/test_job_schemas.py`
- `backend/tests/services/test_txt2crs_submission.py`
- `backend/tests/services/test_txt2crs_uploads.py`

Inventory and provenance were established with `analyze-project.sh --json`,
`git status --short`, `git diff --stat "$BASE"`,
`git diff "$BASE"`, `git ls-files --others --exclude-standard`, and the
repository client-generation script. Every text file in the inventory was
read; generated client files were additionally verified through their source
OpenAPI document, generator, client contract tests, TypeScript build, and
byte-stable regeneration.

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `backend/app/core/middleware.py:93` accepted signed, whitespace-padded, and
  underscore-separated `Content-Length` values because Python's `int` grammar
  is broader than HTTP's decimal grammar. A stricter intermediary could parse
  the same request differently. | Fix: Require a non-empty ASCII digit-only
  byte sequence before conversion. Added regressions for `+10`, ` 10`, and
  `1_0`. | Status: FIXED
- `backend/app/schemas/jobs.py:219` encoded multipart metadata outside the
  parser's safe exception boundary. A direct caller supplying an unpaired
  surrogate received a raw `UnicodeEncodeError` instead of the context-free
  validation result. | Fix: Catch Unicode encoding failures, discard their
  sensitive exception context, and retain the byte-accurate size limit. |
  Status: FIXED
- `backend/app/services/txt2crs_uploads.py:255` rejected `.` and `..` only in
  intermediate OOXML path components, allowing terminal entries such as
  `word/.` and `word/..`. | Fix: Reject terminal dot segments as well and add
  real ZIP regressions for both names. | Status: FIXED
- `backend/app/services/txt2crs_submission.py:215` always sent a worker wake
  hint after an exact replay, including completed, failed, and cancelled
  records. The durable result was correct, but terminal work is not runnable.
  | Fix: Notify only for non-terminal public statuses while preserving
  best-effort post-commit semantics. | Status: FIXED
- `backend/app/api/routes/jobs.py:182` returned the current durable revision
  beside the literal `accepted` status on an exact replay. A completed replay
  could therefore return the internally inconsistent pair
  `accepted`/revision `6`. | Fix: Keep the POST acknowledgement stable at the
  initial accepted revision `0`; the owner-scoped GET endpoint owns current
  state in Session 02. | Status: FIXED

### Low

- `backend/app/api/routes/users.py:412`, `README.md`,
  `docs/ARCHITECTURE.md`, `docs/onboarding.md`, and `docs/CHANGELOG.md` did not
  all describe the implemented state. Signup still claimed unconditional
  public access, while public status documents claimed learner submission
  routes did not exist. | Fix: Document conditional local signup and its 403
  response, update Phase 03 status, and record the submission/security changes
  in the changelog. Regenerate the OpenAPI client. | Status: FIXED
- `backend/tests/acceptance/conftest.py` imported `InputPayload` from the
  private ingestion module even though the session exposes it from the public
  jobs boundary, and `backend/tests/acceptance/test_job_submission.py` typed a
  `JobRecord` helper as `object`. | Fix: Use the public export and exact return
  type. | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- The public API prefix remains `/api/v1`, matching the repository's generated
  contract and existing route topology. Generalizing every pre-existing
  process-global settings reference is outside this session.
- The POST response intentionally acknowledges original admission rather than
  current execution state. Session 02's owner-scoped read contract is the
  authoritative current-state surface.
- ZIP directory entries with a trailing slash remain valid; only empty
  intermediate segments and dot traversal segments are rejected.
- Generated client output was not manually edited. It is accepted only through
  the checked-in generator, source OpenAPI inspection, contract tests,
  TypeScript compilation, and byte-stable second generation.
- Concurrent same-owner idempotent admission is already protected by the
  package acceptance regression
  `test_concurrent_exact_replay_commits_one_durable_request`.
- Live Codex subscription execution remains an explicit credentialed release
  gate and is not required for this credential-free session review.

## Behavior Changes

- Upload request framing now accepts only the HTTP decimal
  `Content-Length` grammar and still counts every actual body chunk.
- Invalid multipart metadata Unicode is translated to the same context-free
  validation result as invalid JSON.
- OOXML archives containing terminal `.` or `..` entries are rejected before
  extraction or package ingestion.
- Exact terminal idempotent replays do not wake the serial worker.
- Every successful POST acknowledgement is stable at
  `status="accepted", revision=0`; current status is intentionally separate.
- OpenAPI now tells clients that signup is a local-only opt-in and can return
  403.
- Public status and architecture documentation now acknowledge the durable
  submission routes while identifying later read, purge, and UI sessions.

## Security and Compliance Review

| Area | Result | Evidence |
|------|--------|----------|
| Authentication/authorization | PASS | Both job routes require `CurrentUser`; unauthenticated malformed bodies are rejected before private validation; signup remains disabled before database lookup |
| Input/output validation | PASS | Strict discriminated schemas, finite metadata, allowlisted 202 projection, exact idempotency-key grammar, and bounded multipart shape are tested |
| Request framing | PASS | Duplicate, malformed, signed, padded, underscored, dishonest, chunked, and oversize body cases are rejected or cumulatively bounded |
| Upload safety | PASS | Filename/MIME/magic agreement, PDF limits, OOXML structure, entry count, expanded bytes, traversal, encryption, macros, and ActiveX are covered |
| Injection | PASS | No shell, SQL, template, HTML, dynamic execution, or unvalidated redirect sink is introduced by the submission surface |
| Secrets and privacy | PASS | Source content, URLs, retry keys, request hashes, provider errors, paths, and upload values are absent from public responses and structured logs |
| Resource safety | PASS | Reads are bounded, framework uploads close on success/failure/cancellation, readiness uses a cache, and worker hints occur only after durable non-terminal results |
| Package ownership | PASS | Routes call the shell adapter, which uses only public `txt2crs` facade/jobs exports; engine logic is not duplicated in the shell |
| Error handling | PASS | Package failures map to `AppException`/`ErrorCode` Problem Details without retaining private exception chains |
| Dependencies | PASS | No new runtime dependency or lockfile change was required |
| Database | PASS | No application schema changed; package admission uses the existing tenant SQLite transaction boundary, so no Alembic migration is needed |
| GDPR | PASS | Owner identity is preserved at the job boundary; this session adds no new public personal-data field or retention policy |

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence |
|-------|-----------------------|--------|----------|
| Tests-first review regressions | Focused shell tests before repairs | EXPECTED FAIL | 8 failed and 109 passed, isolating the five medium defects |
| Focused repaired suite | Same five focused shell files after repairs | PASS | 117 passed |
| Engine suite | `uv run --package txt2crs pytest -q` | PASS | 467 passed, 1 opt-in live test skipped |
| Engine static checks | package Ruff, format, and mypy commands | PASS | 138 files formatted; no lint or type issue |
| Shell suite | `uv run pytest tests/ -q` with isolated PostgreSQL | PASS | 429 passed |
| Shell static checks | Ruff, format, mypy, and ty | PASS | 100 files formatted; 47 application files type-safe |
| Client contract | `pytest tests/scripts/test_generate_client_contract.py -q` | PASS | 5 passed |
| Frontend gates | Biome, TypeScript, and Vite | PASS | 138 files checked; 2,204 modules built |
| Generated provenance | Run `scripts/generate-client.sh` twice and compare aggregate SHA-256 | PASS | Second generation was byte-stable |
| Repository hooks | Pre-commit over all tracked files and the explicit untracked inventory | PASS | Every configured hook passed in both runs |
| Encoding hygiene | ASCII and carriage-return scan over all 70 files including this report | PASS | No non-ASCII byte or CRLF line ending found |
| Patch integrity | Base-to-worktree diff and whitespace review | PASS | No unrelated dependency, migration, or generated-source ownership violation |

## Summary

1. Reviewed the complete 69-file implementation surface.
2. Found 0 critical, 0 high, 5 medium, and 2 low issues.
3. Repaired all seven findings with focused regressions or contract checks.
4. Engine, shell, frontend, generated-client, static, type, and build gates
   pass.
5. No unresolved code, security, privacy, or workflow finding remains.

Next command: `validate`
