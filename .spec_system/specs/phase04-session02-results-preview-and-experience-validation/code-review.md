# Code Review and Repair Report

**Session ID**: `phase04-session02-results-preview-and-experience-validation`
**Package**: frontend
**Reviewed**: 2026-07-20
**Base Commit**: `acb55418a22beef91e3349eb9a66f734eb112995`
**Scope**: All changes since the base commit (uncommitted work plus
mid-session commits)
**Result**: RESOLVED

## Review Surface

There were no staged changes and no mid-session commits. The review covered
17 tracked-modified files and 20 untracked files.

**Files reviewed** (all changes since the base commit):

- `.spec_system/state.json` - tracked-modified
- `docker-compose.override.yml` - tracked-modified
- `docker-compose.yml` - tracked-modified
- `docs/CHANGELOG.md` - tracked-modified
- `docs/dashboard-design.md` - tracked-modified
- `docs/onboarding.md` - tracked-modified
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` - tracked-modified
- `frontend/.env.example` - tracked-modified
- `frontend/AGENTS.md` - tracked-modified
- `frontend/Dockerfile` - tracked-modified
- `frontend/README_frontend.md` - tracked-modified
- `frontend/src/components/CourseProgress/CourseProgressPage.tsx` -
  tracked-modified
- `frontend/src/index.css` - tracked-modified
- `frontend/src/lib/public-config.test.ts` - tracked-modified
- `frontend/src/lib/public-config.ts` - tracked-modified
- `frontend/src/vite-env.d.ts` - tracked-modified
- `frontend/tests/course-journey.spec.ts` - tracked-modified
- `.spec_system/specs/phase04-session02-results-preview-and-experience-validation/implementation-notes.md`
  - untracked
- `.spec_system/specs/phase04-session02-results-preview-and-experience-validation/spec.md`
  - untracked
- `.spec_system/specs/phase04-session02-results-preview-and-experience-validation/tasks.md`
  - untracked
- `frontend/src/components/CourseResults/ArtifactActions.tsx` - untracked
- `frontend/src/components/CourseResults/CourseResultsWorkspace.test.tsx` -
  untracked
- `frontend/src/components/CourseResults/CourseResultsWorkspace.tsx` -
  untracked
- `frontend/src/components/CourseResults/HtmlArtifactPreview.tsx` - untracked
- `frontend/src/components/CourseResults/PublicationCard.tsx` - untracked
- `frontend/src/components/CourseResults/ResultDisclosure.tsx` - untracked
- `frontend/src/components/CourseResults/artifact-transfer.test.ts` - untracked
- `frontend/src/components/CourseResults/artifact-transfer.ts` - untracked
- `frontend/src/components/CourseResults/presentation.test.ts` - untracked
- `frontend/src/components/CourseResults/presentation.ts` - untracked
- `frontend/src/components/CourseResults/preview-document.test.ts` - untracked
- `frontend/src/components/CourseResults/preview-document.ts` - untracked
- `frontend/src/components/CourseResults/queries.test.ts` - untracked
- `frontend/src/components/CourseResults/queries.ts` - untracked
- `frontend/src/components/CourseResults/useArtifactTransfer.test.tsx` -
  untracked
- `frontend/src/components/CourseResults/useArtifactTransfer.ts` - untracked
- `frontend/src/components/ui/spinner.tsx` - untracked standard shadcn
  component added through the project CLI

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`, and
`git ls-files --others --exclude-standard`.

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `frontend/src/components/CourseResults/queries.ts:55` - The manifest query
  did not consume TanStack Query's abort signal, so route exit could leave the
  generated-client read running. Fix: accept the query context signal and pass
  it to `JobsService.readJobArtifacts`. The query test now asserts the exact
  signal reaches the generated operation. Status: FIXED.
- `frontend/src/components/CourseResults/queries.ts:34` - A cross-job manifest
  identity failure used a generic `Error`, and the retry classifier treated
  every generic error as transient. Fix: add a fixed
  `ArtifactManifestIntegrityError` and explicitly exclude it from retry. The
  query test proves the mismatch is fixed-copy and non-transient. Status:
  FIXED.
- `frontend/src/components/CourseResults/CourseResultsWorkspace.tsx:130` - A
  completed snapshot with `available=true`, a positive count, and a null
  manifest URL disabled the query but still rendered the pending skeleton
  forever. Fix: use the same complete manifest-advertisement predicate for the
  workspace gate and query enablement. A server-rendered component regression
  test proves the inconsistent state fails visibly without the spinner.
  Status: FIXED.
- `frontend/src/components/CourseResults/presentation.ts:122` - Manifest MIME
  validation used `startsWith`, allowing values such as
  `text/html-malicious` to reach the presentation even though transfer
  verification later rejected them. Fix: compare the normalized MIME base
  exactly to the finite format map. The malformed-manifest unit test proves
  the near-prefix is rejected. Status: FIXED.
- `frontend/src/components/CourseResults/ArtifactActions.tsx:156` and
  `frontend/src/components/CourseResults/HtmlArtifactPreview.tsx:132` -
  alternate-format menu items and the preview close control were below the
  session's 44 px practical target floor. Fix: add a 44 px minimum menu-item
  height and a preview-local 44 px close-control size. The completed browser
  journey polls past the intentional opening transform and measures both
  rendered targets. Status: FIXED.

### Low

- `.spec_system/specs/phase04-session02-results-preview-and-experience-validation/tasks.md:195`
  - The completed checklist still instructed the next agent to run
  `implement`, contradicting its own completed state. Fix: hand off to
  `creview`. Status: FIXED.

## Assumptions and Deliberate Non-Fixes

- The preview CSP deliberately omits `sandbox` and `navigate-to` meta
  directives. Browser inspection showed those directives are unsupported or
  ignored in a meta-delivered policy; the empty iframe `sandbox` attribute,
  URL/active-content stripping, supported CSP directives, and no-referrer
  policy enforce the intended boundary without browser warnings.
- Plain HTTP source references remain navigable because the session
  specification explicitly allows HTTP(S). They receive opener and referrer
  isolation and are never fetched automatically.
- The public preview cap remains a strict positive safe integer rather than
  gaining an unrequested frontend hard maximum. It is operator-selected
  presentation configuration; backend delivery and artifact-size limits remain
  authoritative.

## Behavior Changes

- Manifest reads now abort with their TanStack Query lifecycle.
- Cross-job manifest identity failures no longer retry as connectivity errors.
- Inconsistent completed artifact advertisements show bounded unavailable
  recovery instead of a permanent loading state.
- MIME near-prefixes fail before publication actions render.
- Format menu items and the preview close control meet the 44 px project floor.
- The task record now names `creview` as its next workflow.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first repair gate | `npx vitest run src/components/CourseResults/presentation.test.ts src/components/CourseResults/queries.test.ts src/components/CourseResults/CourseResultsWorkspace.test.tsx` before fixes | PASS | Expected red state: signal, integrity-error export, inconsistent workspace, and exact MIME regressions failed before implementation. |
| Focused repair tests | `npx vitest run src/components/CourseResults/presentation.test.ts src/components/CourseResults/queries.test.ts src/components/CourseResults/CourseResultsWorkspace.test.tsx` | PASS | 3 files and 10 tests passed after repair. |
| Full unit tests | `npm run test:unit` | PASS | 20 files and 132 tests passed. |
| Browser acceptance | `POSTGRES_SERVER=127.0.0.1 POSTGRES_PORT=55433 POSTGRES_USER=postgres POSTGRES_PASSWORD=<isolated-test-password> POSTGRES_DB=app TXT2CRS_BROWSER_SCENARIO=complete npx playwright test --config playwright.jobs.config.ts` | PASS | 16 passed and the one failed-scenario-only story skipped; setup and owner cleanup passed. The report redacts the disposable local fixture password. |
| Linter | `npm run lint` | PASS | Biome checked 157 files with no remaining diagnostics. |
| Formatter | `npx biome check src/components/CourseResults tests/course-journey.spec.ts` | PASS | All repaired source and browser files match deterministic formatting. |
| Type checker | `npm run typecheck` | PASS | Strict build TypeScript emitted no diagnostics. |
| Production build | `npm run build` | PASS | 2,215 modules built; secure preview remains a 4.43 kB lazy chunk. |
| Repository validation | `./scripts/validate-changes.sh --json` | PASS | All 9 backend, engine, and frontend lint, type-check, format, baseline-test, and engine-test steps passed. |
| Changed-file hooks | `pre-commit run --files <all 38 modified and untracked files>` | PASS | Large-file, conflict, TOML/YAML, EOF, whitespace, typo, Biome, and TypeScript hooks passed. |
| Repository hygiene | `git diff --check` plus ASCII/LF, generated-client/OpenAPI, and listener guards | PASS | All 38 current files are clean; no generated contract drift or test listener remains. |
| Security and product-surface review | Targeted read of all CourseResults files plus `rg` for direct fetch, parent HTML insertion, broad iframe tokens, scripts, debug output, and stale markers | PASS | Generated client is the only transport; empty sandbox, no-referrer, bounded transformation, safe copy, and product-only UI remain intact. |
| Final diff re-read | `git diff "$BASE"` plus full reads of every untracked text file | PASS | All 37 pre-report review-surface files were re-read; no unresolved finding, debug artifact, generated-client edit, or out-of-scope implementation remains. |

## Summary

1. Reviewed all 37 files changed or created since base commit
   `acb55418a`, including configuration, documentation, the complete frontend
   result feature, unit tests, and browser acceptance.
2. Found 0 critical, 0 high, 5 medium, and 1 low issue; all are fixed.
3. Recorded three evidence-backed deliberate non-fixes; none is a blocker.
4. Focused red-to-green regressions, all 132 frontend unit tests, the complete
   16-story deterministic browser run, Biome, strict TypeScript, and the
   production build all pass.

Next command: `validate`

Reason: all changes since the base commit have been reviewed and repaired; the
session is ready for the validation gate.
