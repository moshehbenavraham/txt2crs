# Code Review and Repair Report

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Package**: Cross-cutting monorepo (`backend`, `backend/packages/txt2crs`,
`frontend`, release tooling, and session documentation)
**Reviewed**: 2026-07-20
**Base Commit**: `875808005a011a6a23538fa903805d0719463ccd`
**Scope**: All changes since the base commit, including twelve mid-session
commits and uncommitted review repairs
**Result**: RESOLVED

## Review Surface

The pre-report inventory contained 444 changed paths, 18,767 insertions, and
1,415 deletions. This report is the 445th changed path. No changed file was
binary and no untracked input existed before this report was created.

Files reviewed:

- 339 Codex protocol-fixture paths: all 337 files in
  `backend/packages/txt2crs/docs/fixtures/codex_app_server_0.144.4/`, the
  fixture index, and the retained older compatibility schema. The fixture is
  generated from pinned `openai-codex`/CLI `0.144.4`; its 337-file aggregate
  manifest hash is
  `3ea892bc0080b15e1a17d716a4c9124429190446049ec41f5161ec19577a93e8`.
- 21 unchanged, 100-percent Git renames from the three completed Phase 03
  session directories into `.spec_system/archive/sessions/`.
- 9 active Apex/PRD state paths under `.spec_system/PRD/`,
  `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/`,
  `.spec_system/state.json`, and this report.
- 13 root/release/configuration paths: `.env.example`, `.gitignore`,
  `.github/workflows/release.yml`, `README.md`, `VERSION`,
  `docs/CHANGELOG.md`, `docs/CONFIGURATION.md`, `docs/VERSIONING.md`,
  `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md`, and all four
  `docs/release/` deliverables.
- 29 engine package paths: package metadata/docs, AI/runtime/application/
  generation/research/rendering source, acceptance/contract/integration/unit
  tests, and `backend/uv.lock`.
- 22 backend shell paths: `.dockerignore`, `.env.example`, three tracked email
  templates, configuration/schema/readiness/worker source, and API/browser/
  core/schema/script/service/support tests.
- 8 frontend paths: generator configuration/scripts, package scripts,
  generated schemas/types, setup presentation test, and Playwright setup test.
- 4 root scripts: authentication helper, client generator, release contract,
  and release evidence CLI.

Inventory commands:

- `bash .spec_system/scripts/analyze-project.sh --json`
- `git status --short`
- `git log --oneline 875808005a011a6a23538fa903805d0719463ccd..HEAD`
- `git diff 875808005a011a6a23538fa903805d0719463ccd`
- `git diff --cached 875808005a011a6a23538fa903805d0719463ccd`
- `git ls-files --others --exclude-standard`
- `git diff --name-status 875808005a011a6a23538fa903805d0719463ccd`
- `git diff --numstat 875808005a011a6a23538fa903805d0719463ccd`

## Findings by Severity

### Critical

No critical findings.

### High

- `scripts/auth-codex.sh:22` - Caller arguments followed the helper-owned
  `--state-directory`, so a repeated option could redirect credentials outside
  the owner-only repository state boundary. Fix: reject both split and
  equals-form overrides before invoking `uv`; both forms have regression
  coverage. Status: FIXED.
- `backend/.dockerignore:14` - Recursive `**/build` excluded the tracked
  `app/email-templates/build/*.html` runtime assets from production images.
  Fix: re-include only that exact directory and its HTML files; static
  contracts and a real production image prove all three templates ship.
  Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/ai/model_policy.py:14`,
  `backend/app/core/config.py:312` - Bare `gpt-5.6` was treated as an exact
  model and remained the application default even though the packaged
  app-server catalog does not expose it. Fix: default to exact
  `gpt-5.6-sol`, accept only Sol/Terra/Luna exact IDs, align environment/docs/
  public OpenAPI/generated client/test fixtures, and explicitly reject the
  bare family label. Status: FIXED.

### Medium

- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py:1007` -
  Duplicate block IDs collapsed into a dictionary and bypassed module-draft
  validation, later causing an unbounded canonical-course validation failure.
  Fix: detect duplicate IDs before dictionary construction and raise the safe
  local repair code `module_block_id_duplicate`. Status: FIXED.
- `backend/packages/txt2crs/src/txt2crs/rendering/artifacts.py:735` - One label
  dictionary mixed objective, section, flashcard, and exercise namespaces, so
  schema-valid cross-namespace ID collisions overwrote headings. Fix: use
  namespace-specific heading maps and preserve all distinct labels for
  free-form references. Status: FIXED.
- `frontend/package.json:17`, `scripts/generate-client.sh:5` - The documented
  public `npm run generate-client` path bypassed formatting/ASCII normalization
  and the wrapper depended on the caller's working directory. Fix: delegate
  the public command to the root wrapper, resolve paths with `BASH_SOURCE[0]`,
  and keep codegen/format/normalization in one internal command. Status: FIXED.
- `.github/workflows/release.yml:125` - Hosted backend/frontend release builds
  omitted the OCI version and revision labels required by the release
  specification and local proof. Fix: label both images with repository
  version and `${GITHUB_SHA}`. Status: FIXED.
- `scripts/generate-client.sh:13` - The wrapper redirected directly into
  `frontend/openapi.json`; a concurrent contract reader observed the file
  after truncation and before JSON completion. Fix: write a same-directory
  temporary document, atomically rename it, and clean failed temporary output.
  The entire 73-test script suite now passes while generation runs
  concurrently. Status: FIXED.
- `backend/app/services/txt2crs_worker.py:211` - `Thread.start()` returned
  before the worker published its first idle/active snapshot, allowing an
  immediate healthy submission to receive `SYSTEM_6001`/503. Fix: add a
  finite startup barrier using the existing lifecycle timeout and return only
  after an operational state is visible. Status: FIXED.

### Low

- `backend/packages/txt2crs/pyproject.toml:17` - Stable package `1.0.0` still
  advertised the Pre-Alpha classifier. Fix: use
  `Development Status :: 5 - Production/Stable` with metadata regression
  coverage. Status: FIXED.
- `README.md:125` - A manual quick-start edit claimed the credential-free fast
  gate performed live research/LLM execution. Fix: retain the useful Tavily
  and short authentication instructions while separating live-provider gates
  from the credential-free command. Status: FIXED.
- `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/tasks.md:206`
  - The completed task list still told the next agent to rerun `implement`.
  Fix: advance the handoff through `creview` and now to `validate`. Status:
  FIXED.
- `backend/packages/txt2crs/docs/HERMES_MINIMUM_CODE_PULL_EVALUATION.md`,
  `backend/packages/txt2crs/src/txt2crs/rendering/artifacts.py`,
  `backend/packages/txt2crs/tests/unit/test_rendering.py` - The validation
  changed-file scan found Unicode bytes that predated the session but remained
  in three session-touched files. Fix: normalize donor-document punctuation to
  ASCII and express the renderer's em dash plus Hebrew test data with ASCII
  `\u` escapes, preserving runtime output. Status: FIXED.

## Assumptions and Deliberate Non-Fixes

- Candidate evidence remains tied to exact tested revision
  `a80700863e99cdd34bed757873d969236cdf36fa`. The review did not rewrite its
  revision or hashes to claim that later repairs received the already-complete
  paid live run. Exact Sol was explicitly selected for that run. Session 02
  must rebuild and revalidate its final tracked commit before creating
  `v1.0.0`.
- Bare `gpt-5.6` remains only where it truthfully means a model family in the
  public candidate ledger/validator, or where a negative test proves the bare
  value is rejected. It is not retained as a selectable exact model.
- The stable-only release validator's prerelease filename normalization was
  not broadened because this session validates exact stable `1.0.0`; changing
  unrelated prerelease behavior would exceed the review surface.
- Phase/session status remains planned/not-started until Apex `validate` and
  `updateprd` own the state transition. The code review does not predeclare a
  successful validation.
- The authentication/model decision used only repository behavior and the
  operator-provided local `/home/aiwithapex/projects/hermes` and
  `/home/aiwithapex/projects/aios` sources. No web or OpenAI documentation was
  used.

## Behavior Changes

- Invalid provider module drafts with duplicate block IDs receive one bounded
  local repair instead of failing later during canonical assembly.
- Review headings remain correct when valid identifiers collide across domain
  namespaces.
- Application defaults, readiness, durable execution profiles, public API
  types, and operator examples use exact `gpt-5.6-sol`; bare `gpt-5.6` fails
  closed as an exact selection.
- The auth helper cannot redirect its credential state; generated-client
  writes are caller-location independent and atomic; production images include
  email templates and hosted images carry release labels.
- Worker startup exposes readiness only after the serial worker is
  operational, eliminating the immediate first-submission 503 race.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Model source evidence | Focused `rg`/`sed` inspection of local Hermes and AIOS model catalogs and delivery plan | PASS | Exact Sol/Terra/Luna IDs; Sol is the reviewed baseline; bare text is family matching only |
| Packaged model discovery | Readiness-only `OfficialCodexSdkAdapter.list_model_ids()` membership probe using the dedicated state | PASS | ChatGPT mode; five catalog entries; bare false; Sol/Terra/Luna true; no model turn |
| Model red/green | Engine model-policy test plus backend settings/schema tests | PASS | RED: 2 engine and 3 backend failures; GREEN: 13 engine and 56 backend tests |
| Duplicate-ID and rendering red/green | Focused generation/rendering regressions | PASS | Three initial failures across duplicate ID, label collision, and metadata; targeted tests pass after repair |
| Auth boundary red/green | `pytest ...test_authentication_script_rejects_state_directory_overrides` | PASS | Both split and equals forms failed before repair and pass after repair |
| Docker context red/green | Focused container contract plus real `docker build --target production` | PASS | Static failure repaired; final image contains three nonempty email templates, non-root user, package 1.0.0, command, and healthcheck |
| Workflow labels red/green | `uv run pytest --confcutdir=tests/scripts tests/scripts/test_release_workflow_contract.py -q` | PASS | Five release workflow contracts, including two-image OCI labels |
| Client generation | Concurrent `tests/scripts` run and `npm run generate-client` | PASS | 73 script contracts passed while five client files regenerated; no truncated JSON |
| Worker startup red/green | Gated start regression, exact browser submission, and full backend suite | PASS | RED immediate 503 and deterministic start-barrier failure; GREEN regression and browser test; 517 backend tests |
| Engine formatter/linter/types/tests | `ruff format --check .`, `ruff check .`, `mypy`, `pytest -q` from engine root | PASS | 138 files formatted; lint/types clean; 489 passed, 2 explicit live skips |
| Backend migrations/formatter/linter/types/tests | Fresh PostgreSQL 18, `alembic upgrade head`, Ruff, mypy, `pytest tests -q` | PASS | All migrations; 111 files formatted; lint/types clean; 517 passed, 1 dependency deprecation warning |
| Frontend tests/lint/types/build | `npm run test:unit`, `npm run lint`, `npm run typecheck`, `npm run build` | PASS | 132 tests; 158 Biome files; 2,215 modules built |
| Repository fast gate | `./scripts/validate-changes.sh --json` | PASS | 9 of 9 backend, engine, and frontend checks |
| Shell checks | `bash -n` and `shellcheck` for auth/client scripts | PASS | Both scripts clean |
| Hooks | `pre-commit run --all-files` | PASS | All 15 hooks passed after one mechanical Ruff format |
| Candidate identity | Repository/evidence validators, canonical regeneration, `cmp`, `sha256sum` | PASS | Exact `a807008...`; canonical hash `43e811...bbbd`; byte-identical |
| Secret/diff/tag hygiene | `git diff --check`, redacted Gitleaks stdin scan of base diff, untracked/tag/resource inspections | PASS | No leak, whitespace error, untracked input, `v1.0.0` tag, temporary database, or temporary image |
| Text conventions | Current-file ASCII/CRLF scan over the complete base diff plus focused renderer test | PASS | All 444 current regular changed paths are ASCII/LF; one path is a deleted compatibility fixture; 21 renderer tests preserve Unicode behavior through ASCII `\\u` escapes |
| Final diff re-read | `git diff "$BASE"` plus generated-fixture provenance and untracked inventory | PASS | All 445 final paths reviewed; no unresolved finding or debug artifact |

## Security and Behavioral Review

- Trust boundaries: exact model allowlist, auth state ownership, owner-private
  artifact behavior, safe provider error codes, and release evidence allowlist
  remain fail closed.
- Resource/concurrency safety: the worker startup barrier, atomic generator,
  bounded repair path, reverse-order lifecycle cleanup, and temporary resource
  removal have direct evidence.
- Sensitive data: no credential, provider payload, prompt, raw live artifact,
  email/account identifier, or private absolute state path was added to public
  evidence. The Gitleaks scan covers the entire diff from the session base.
- GDPR: no new personal-data collection or sharing was introduced by review
  repairs. Existing consent, minimization, owner access, and purge behavior
  remain unchanged.
- Product surface: no new user-facing diagnostics or developer scaffolding was
  added. The frontend changes are generated model typing and test fixtures.

## Summary

1. Reviewed all 444 implementation paths since the exact base plus this report,
   including 12 commits, 339 protocol-fixture paths, 21 archive moves, and 84
   other source/test/config/docs paths.
2. Resolved 0 critical, 3 high, 6 medium, and 4 low findings; every code or
   tooling correction has a regression or exact static/runtime proof.
3. Preserved the exact historical live candidate identity instead of
   relabeling later repairs; Session 02 owns final immutable rebuild/tag proof.
4. Full engine, backend, frontend, repository, hook, release, image, security,
   and text-convention evidence is green. Remaining blockers: none.

Summary:
- Reviewed all changes since base commit `8758080` (445 final paths)
- Findings: 0 critical, 3 high, 6 medium, 4 low; all resolved
- Evidence: full engine/backend/frontend suites, migrations, image inspection,
  release/canonical checks, concurrent codegen, hooks, Gitleaks, and final diff
- Remaining blockers: none

Next command: `validate`
Reason: all changes since the base commit have been reviewed, repaired, and
verified; the session is ready for the validation gate.
