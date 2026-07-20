# Code Review and Repair Report

**Session ID**:
`phase04-session01-public-landing-intake-and-progress`
**Package**: backend + frontend
**Reviewed**: 2026-07-20
**Base Commit**: `08297e317683ad6cf608e4d9333bfbb819955ef7`
**Scope**: All changes since the base commit, including every untracked file
**Result**: RESOLVED

## Review Surface

The review covered the complete 141-path implementation surface present before
this report: 73 tracked deltas and 68 untracked files. The validation
follow-up expanded that surface to 144 paths: 76 tracked deltas and the same
68 implementation files. `HEAD` remained the base commit, so there were no
mid-session commits or staged-only changes. Workflow reports are not counted
in that implementation total.

Five completed Phase 02 session directories were moved from active specs to
the session archive. For each directory below, all seven named files were
inventoried as one tracked deletion plus one untracked archive destination:
`IMPLEMENTATION_SUMMARY.md`, `code-review.md`, `implementation-notes.md`,
`security-compliance.md`, `spec.md`, `tasks.md`, and `validation.md`.

- `phase02-session01-engine-composition-lifecycle`
- `phase02-session02-serial-worker-supervisor`
- `phase02-session03-cached-readiness-and-observability`
- `phase02-session04-system-readiness-and-auth-api`
- `phase02-session05-operator-setup-experience`

The 35 archive destinations under `.spec_system/archive/sessions/` were
compared individually with `git show "$BASE:$source" | cmp`; all 35 were
byte-identical and zero mismatches were found.

**Other tracked modifications and deletions reviewed**:

- `.spec_system/state.json` - modified
- `backend/app/main.py` - modified
- `backend/tests/acceptance/conftest.py` - modified
- `docker-compose.override.yml` - modified
- `docker-compose.yml` - modified
- `docs/CHANGELOG.md` - modified
- `docs/dashboard-design.md` - modified
- `docs/onboarding.md` - modified
- `examples/frontend/hooks/use_mutation_with_toast.ts` - modified
- `examples/frontend/hooks/use_query_with_suspense.ts` - modified
- `frontend/.env.example` - modified
- `frontend/AGENTS.md` - modified
- `frontend/Dockerfile` - modified
- `frontend/README_frontend.md` - modified
- `frontend/index.html` - modified
- `frontend/src/components/Common/Footer.tsx` - modified
- `frontend/src/components/Common/NotFound.tsx` - modified
- `frontend/src/components/Sidebar/AppSidebar.tsx` - modified
- `frontend/src/components/Sidebar/Main.tsx` - modified
- `frontend/src/components/ui/badge.tsx` - modified
- `frontend/src/components/ui/button.tsx` - modified
- `frontend/src/hooks/useAuth.ts` - modified
- `frontend/src/index.css` - modified
- `frontend/src/lib/schemas/fields.ts` - modified
- `frontend/src/lib/schemas/index.ts` - modified
- `frontend/src/lib/types/branded.ts` - modified
- `frontend/src/lib/types/index.ts` - modified
- `frontend/src/routeTree.gen.ts` - modified, generated
- `frontend/src/routes/_layout.tsx` - modified
- `frontend/src/routes/_layout/forbidden.tsx` - modified
- `frontend/src/routes/_layout/index.tsx` - deleted
- `frontend/src/routes/login.tsx` - modified
- `frontend/src/routes/recover-password.tsx` - modified
- `frontend/src/routes/reset-password.tsx` - modified
- `frontend/src/routes/signup.tsx` - modified
- `frontend/src/vite-env.d.ts` - modified
- `frontend/tests/auth.setup.ts` - modified
- `frontend/tests/config.ts` - modified
- `frontend/tests/dashboard.spec.ts` - modified
- `frontend/tests/login.spec.ts` - modified
- `frontend/tests/utils/user.ts` - modified

**Other untracked files reviewed**:

- `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/implementation-notes.md`
- `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/spec.md`
- `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/tasks.md`
- `backend/tests/browser/__init__.py`
- `backend/tests/browser/deterministic_app.py`
- `backend/tests/browser/test_deterministic_app.py`
- `backend/tests/support/__init__.py`
- `backend/tests/support/deterministic_course.py`
- `frontend/playwright.jobs.config.ts`
- `frontend/src/components/CourseIntake/CourseIntakeForm.tsx`
- `frontend/src/components/CourseIntake/InputModeField.tsx`
- `frontend/src/components/CourseIntake/LearningIntentFields.tsx`
- `frontend/src/components/CourseIntake/SourcePreview.tsx`
- `frontend/src/components/CourseProgress/CourseProgressPage.tsx`
- `frontend/src/components/CourseProgress/presentation.test.ts`
- `frontend/src/components/CourseProgress/presentation.ts`
- `frontend/src/components/CourseProgress/queries.test.ts`
- `frontend/src/components/CourseProgress/queries.ts`
- `frontend/src/components/Landing/LandingPage.tsx`
- `frontend/src/hooks/useCourseSubmission.test.tsx`
- `frontend/src/hooks/useCourseSubmission.ts`
- `frontend/src/lib/course-draft.test.ts`
- `frontend/src/lib/course-draft.ts`
- `frontend/src/lib/public-config.test.ts`
- `frontend/src/lib/public-config.ts`
- `frontend/src/lib/schemas/job.test.ts`
- `frontend/src/lib/schemas/job.ts`
- `frontend/src/lib/types/branded.test.ts`
- `frontend/src/routes/_layout/create.tsx`
- `frontend/src/routes/_layout/jobs.$jobId.tsx`
- `frontend/src/routes/index.tsx`
- `frontend/tests/auth.teardown.ts`
- `frontend/tests/course-journey.spec.ts`

**Inventory commands**: `git status --short`,
`git log --oneline "$BASE"..HEAD`, `git diff "$BASE"`,
`git diff --cached "$BASE"`, `git ls-files --others --exclude-standard`,
`git diff --check "$BASE"`, and the byte-identity loop described above.

Generated OpenAPI/client files had no base-to-worktree delta.
`frontend/src/routeTree.gen.ts` was reviewed through source route ownership,
TanStack regeneration during Vite, TypeScript, Biome, and the production
build; it was not hand edited.

## Findings by Severity

### Critical

No findings.

### High

- `frontend/src/lib/course-draft.ts` had a bounded session-only prompt consumer,
  but the public landing had no prompt producer. The required public -> login
  -> `/create` handoff was therefore unreachable. | Fix: add the strictly
  validated `CourseTopicHandoff` at
  `frontend/src/components/Landing/LandingPage.tsx:324`, retain direct sign-in,
  surface safe storage failure, and prove one-time consumption in
  `frontend/tests/course-journey.spec.ts:258`. | Status: FIXED
- `frontend/playwright.jobs.config.ts` and
  `backend/tests/browser/deterministic_app.py` derived a shared
  `/tmp/browser-worker`, reused/chmodded an environment-selected state
  directory, persisted auth state in the repository, and left browser-created
  PostgreSQL users behind. Concurrent or failed runs could collide with or
  mutate state they did not own. | Fix: allocate one private run root with
  sibling state/worker/auth paths, reject pre-existing and symlink-parent
  state paths, keep one inherited root/email across Playwright workers, add a
  teardown project using the real account-purge API, and delete foreign users
  in `finally`. Regression coverage is at
  `backend/tests/browser/test_deterministic_app.py:76`,
  `frontend/tests/auth.teardown.ts:47`, and
  `frontend/tests/course-journey.spec.ts:697`. | Status: FIXED

### Medium

- `snapshot.input.extraction_warnings` and `warnings_truncated` were never
  rendered, despite being part of the generated owner response and the
  session contract. | Fix: add a pure warning presentation, a separate warning
  region at `frontend/src/components/CourseProgress/CourseProgressPage.tsx:186`,
  unit coverage, and browser coverage at
  `frontend/tests/course-journey.spec.ts:563`. | Status: FIXED
- The browser suite covered prompt execution and PDF metadata but did not prove
  the generated request shape for text, URL, YouTube, DOCX, or PPTX; it also
  lacked rendered warning, cancellation, and reconnecting checks. | Fix: add
  isolated generated-client interception for all seven source families at
  `frontend/tests/course-journey.spec.ts:441` and owner-status projections for
  warning/reconnection and cancellation without creating irrelevant backend
  jobs. | Status: FIXED
- Rendered QA at the required 320px minimum found the non-wrapping public
  handoff button forcing 51 pixels of document-level horizontal overflow with
  a maximum-length draft. | Fix: allow the primary label to wrap while
  retaining a 48px minimum action height, and lock the maximum-draft case at
  `frontend/tests/course-journey.spec.ts:285`. | Status: FIXED
- Validation's rendered WCAG audit found low-contrast footer text in both
  themes (1.30 and 3.06 ratios) plus dark-theme primary captions and actions
  between 4.14 and 4.37, below the 4.5:1 normal-text requirement. | Fix: add a
  browser-computed light/dark contrast audit, give dark primary fills a
  charcoal foreground and luminous green surface, keep primary links/captions
  bright, and replace the low-opacity footer separator with a decorative rule.
  The test failed before the repair and passes at
  `frontend/tests/course-journey.spec.ts:306`. | Status: FIXED

### Low

- Truncated-warning copy claimed additional notes were available in the job
  record even though the public response exposes only the bounded list and
  truncation flag. Repeated warning strings could also create duplicate React
  keys. | Fix: say additional notes were omitted and combine response order
  with note text for stable sibling keys at
  `frontend/src/components/CourseProgress/CourseProgressPage.tsx:193`. |
  Status: FIXED
- `docs/dashboard-design.md` still named removed remote fonts, described a
  nonexistent validation summary, and claimed every rail row rendered the
  current server message. A stale route comment also pointed to a completed
  implementation task. | Fix: document the local type roles, actual
  first-invalid-control focus, adjacent current-update panel, tab-scoped topic
  handoff, and remove the stale task marker. | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- The specification remains `Status: Not Started` until the Apex `validate`
  workflow performs the authoritative status transition. Completed tasks and
  this review do not preempt that workflow.
- Session 01 intentionally stops at a truthful completed-job handoff. Full
  result, source/conflict, manifest, artifact preview, and download
  composition remain Session 02 scope.
- `VITE_ENABLE_PUBLIC_SIGNUP` remains display-only public build data. The
  backend setting and signup route remain authoritative; no frontend flag is
  treated as access control.
- The deterministic facade performs one real prompt execution path. Other
  source-family browser checks stop at the generated-client boundary to avoid
  irrelevant durable jobs; existing backend route/upload acceptance covers
  strict server validation and package delegation.
- The known short local JWT key and one upstream HTTPX raw-body deprecation
  warning are test-environment warnings, not product behavior introduced by
  this session.
- Historical Phase 02 session content is not rewritten. Its 35 exact files are
  moved into the documented archive location byte-for-byte.

## Behavior Changes

- Signed-out `/` now explains the one-source-to-four-publications product and
  can preserve one valid bounded topic in tab-scoped session storage through
  sign-in.
- Authenticated learners use `/create` for strict prompt, text, URL, YouTube,
  PDF, DOCX, or PPTX intake, explicit AI/research consent, and canonical
  single-flight submission.
- Accepted jobs navigate to private `/jobs/$jobId`, poll revisioned owner state
  with visibility-aware cadence/backoff, stop at terminal state, render
  bounded extraction notes, and preserve uniform missing/foreign recovery.
- Public signup actions follow explicit build visibility while backend
  authorization remains authoritative.
- Deterministic Playwright runs own and remove their engine, worker, auth, and
  database test state without adding a production fixture route.
- The learner interface uses local/system typography compatible with the
  restrictive production content security policy.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Tests-first state ownership regression | Focused backend browser tests before repair | EXPECTED FAIL | 1 failed, 4 passed; a pre-existing state directory was accepted instead of rejected |
| Tests-first warning presentation regression | Focused Vitest before repair | EXPECTED FAIL | `getInputWarningsPresentation` did not exist and the warning assertion failed with a TypeError |
| Tests-first public handoff/resource cleanup | Added Playwright handoff and teardown stories before fixture/UI repair | EXPECTED FAIL | Public page had no topic field; run-owned auth/user cleanup was absent |
| Tests-first minimum-width regression | Isolated Playwright `--grep '320px minimum'` before repair | EXPECTED FAIL | Expected no overflow; received 51 pixels |
| Minimum-width repair | Same isolated focused Playwright command after repair | PASS | Setup, 320px maximum-draft story, and teardown all passed |
| Tests-first WCAG contrast regression | Isolated Playwright `--grep 'WCAG AA text contrast'` before repair | EXPECTED FAIL | Light theme reported the 1.30 separator and 3.06 footer text ratios; manual dark audit also found primary text/action ratios from 4.14 to 4.37 |
| WCAG contrast repair | Same isolated focused Playwright command after repair | PASS | Setup, rendered light/dark text audit, and teardown all passed with no failing visible text |
| Archive provenance | Base-deletion to archive-destination `git show | cmp` loop | PASS | 35 files checked; 0 mismatches |
| Backend shell tests | `uv run pytest tests/ -q` with retained isolated PostgreSQL | PASS | 479 passed; 106 reviewed dependency/test-key warnings |
| Engine tests | `uv run --package txt2crs pytest -q` | PASS | 470 passed; 1 explicit live-subscription test skipped |
| Backend static gates | Ruff check/format, mypy, and ty from `backend/` | PASS | 108 files formatted; 47 application files mypy-clean; Ruff and ty clean |
| Engine static gates | Package Ruff check/format and strict mypy | PASS | 138 files formatted and type-clean |
| Frontend unit/static/build | Vitest, Biome, TypeScript, and production build | PASS | 97 assertions; 141 files checked; 2,202 modules built |
| Generated provenance | `scripts/generate-client.sh` plus base diff | PASS | OpenAPI and generated client reproduced with zero delta |
| Isolated complete journey | `TXT2CRS_BROWSER_SCENARIO=complete` dedicated config | PASS | 15 passed; 1 failure-only terminal story skipped |
| Isolated failed journey | `TXT2CRS_BROWSER_SCENARIO=failed` dedicated config | PASS | 15 passed; 1 complete-only story skipped |
| Broad production browser regression | Isolated Phase 04 Compose project during T024 | PASS | 66 passed; 7 intentionally skipped before review repairs; changed paths were rerun in both final isolated scenarios |
| Rendered learner QA | Desktop/mobile light/dark, 200% layout equivalent, 320px max draft, keyboard/reduced motion | PASS | Zero overflow after repair, zero layout shift, visible focus, 48px action, no remote resources or console/page/request failures |
| Static security inspection | Secret, test-boundary, eval/render, storage, transport, debug, private-copy, and generated-drift searches | PASS | All reviewed counts were zero |
| Resource cleanup | PostgreSQL pattern count, `/tmp` roots, and process listener inspection | PASS | 0 browser users, 0 browser roots, and 0 deterministic backend/Vite listeners after both scenarios |
| Repository hooks | `pre-commit run --files` over every changed and explicit new file | PASS | All applicable file, Ruff, mypy, ty, Biome, TypeScript, generated-client, and security hooks passed |
| Encoding and whitespace | ASCII-byte, carriage-return, and `git diff --check` scans | PASS | Active-session text is ASCII/LF with no whitespace error |
| Final diff re-read | Full base diff plus all 68 untracked files | PASS | No unresolved correctness, privacy, resource, responsive, documentation, or provenance issue |

## Summary

1. Reviewed the complete 144-path base-to-worktree implementation surface,
   including the validation follow-up.
2. Found 0 critical, 2 high, 4 medium, and 2 low issues.
3. Resolved all eight findings with focused regressions and bounded repairs.
4. Backend, engine, frontend, generated-client, browser, rendered,
   security/resource, and repository-hook gates pass.
5. No review blocker or deferred Session 01 defect remains.

Next command: `validate`
