# Task Checklist

**Session ID**: `phase04-session01-public-landing-intake-and-progress`
**Total Tasks**: 25
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-20

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0401]` session ref; `TNNN` task ID.

---

## Setup (3 tasks)

- [x] T001 [S0401] Verify the clean Phase 03 prerequisites, generated job
  operations, existing auth/setup routes, current browser baseline, and
  isolated PostgreSQL availability; record observed mobile/desktop light/dark
  states without changing user containers
  (`.spec_system/specs/phase04-session01-public-landing-intake-and-progress/implementation-notes.md`,
  `frontend/openapi.json`, `frontend/tests/`).
- [x] T002 [S0401] Write failing lifecycle, durable submit/read, cleanup, and
  production-isolation tests for the credential-free deterministic browser
  application with cleanup on scope exit for every worker, facade, file, and
  temporary resource
  (`backend/tests/browser/test_deterministic_app.py`).
- [x] T003 [S0401] [P] Write failing product-flow tests for public access,
  configured signup, every intake family, duplicate submit, direct/refresh job
  progress, reconnecting, safe terminal states, ownership, mobile, keyboard,
  and reduced motion with product-facing assertions only
  (`frontend/tests/course-journey.spec.ts`,
  `frontend/src/lib/schemas/job.test.ts`,
  `frontend/src/components/CourseProgress/queries.test.ts`).

---

## Foundation (7 tasks)

- [x] T004 [S0401] Move the accepted deterministic profile, request, evidence,
  and complete course scenario into shared typed test support while preserving
  current acceptance imports and provider-free behavior
  (`backend/tests/support/deterministic_course.py`,
  `backend/tests/acceptance/conftest.py`).
- [x] T005 [S0401] Implement the isolated browser FastAPI composition over the
  public deterministic facade, real serial worker, normal auth, and private
  state with strict test-only controls, finite waits, fail-closed
  non-test exposure, and reverse-order cleanup
  (`backend/tests/browser/deterministic_app.py`,
  `backend/tests/browser/__init__.py`).
- [x] T006 [S0401] Wire a dedicated Playwright configuration that starts and
  stops isolated backend/Vite processes, authenticates through the real login
  route, gives each run fresh state, and leaves existing Compose-driven browser
  configuration intact
  (`frontend/playwright.jobs.config.ts`, `frontend/tests/auth.setup.ts`,
  `frontend/tests/config.ts`).
- [x] T007 [S0401] Implement centralized strict course-intake schemas and
  payload shaping for exact backend bounds, discriminated modes, literal
  consent, unique bounded goals, HTTPS shape, and inactive-field removal
  (`frontend/src/lib/schemas/job.ts`,
  `frontend/src/lib/schemas/fields.ts`,
  `frontend/src/lib/schemas/index.ts`).
- [x] T008 [S0401] [P] Add validated JobId, ArtifactId, and IdempotencyKey
  brands plus safe trusted-response casts, keeping UUID and finite identifier
  rules distinct and tests descriptive
  (`frontend/src/lib/types/branded.ts`,
  `frontend/src/lib/types/index.ts`,
  `frontend/src/lib/types/branded.test.ts`).
- [x] T009 [S0401] [P] Implement bounded session-only prompt draft persistence
  with corrupt/oversized reset, revalidation on re-entry, consume/clear
  behavior, and no URL or localStorage exposure
  (`frontend/src/lib/course-draft.ts`,
  `frontend/src/lib/course-draft.test.ts`).
- [x] T010 [S0401] Define the research-atelier page hierarchy and any missing
  semantic landing/intake/progress tokens in both themes, preserving protected
  primitives, WCAG focus/contrast roles, the global reduced-motion clamp, and
  no decorative diagnostics
  (`frontend/src/index.css`, `docs/dashboard-design.md`).

---

## Implementation (11 tasks)

- [x] T011 [S0401] Add an explicit non-secret public-signup frontend build
  setting defaulted false and pass it through local/judge Docker builds, with
  backend authorization remaining authoritative and disabled/revoked fallback
  copy
  (`frontend/src/vite-env.d.ts`, `frontend/.env.example`,
  `frontend/Dockerfile`, `docker-compose.yml`,
  `docker-compose.override.yml`).
- [x] T012 [S0401] Build the public `/` research-atelier landing page with a
  source-to-four-publications signature, clear sign-in/configured-access
  action, truthful privacy/AI copy, semantic landmarks, responsive
  transformation, and product-facing copy only
  (`frontend/src/routes/index.tsx`,
  `frontend/src/components/Landing/LandingPage.tsx`).
- [x] T013 [S0401] Restructure authenticated navigation around `/create`,
  preserving current-user guards before queries, safe login/draft handoff,
  setup/admin/settings permissions, dynamic job labels, direct re-entry, and
  denied/revoked fallback behavior
  (`frontend/src/routes/_layout.tsx`,
  `frontend/src/routes/_layout/create.tsx`,
  `frontend/src/routes/login.tsx`,
  `frontend/src/routes/signup.tsx`,
  `frontend/src/hooks/useAuth.ts`,
  `frontend/src/components/Sidebar/AppSidebar.tsx`).
- [x] T014 [S0401] Build the multimode intake workbench and accessible source
  mode control with explicit empty, selected, invalid, disabled, touch,
  keyboard, and re-entry states; unregister inactive values
  (`frontend/src/components/CourseIntake/CourseIntakeForm.tsx`,
  `frontend/src/components/CourseIntake/InputModeField.tsx`,
  `frontend/src/routes/_layout/create.tsx`).
- [x] T015 [S0401] Implement optional audience, prior knowledge, level, age,
  consent, and dynamic learning-goal controls with exact labels, error
  association, focus management, 10-goal bounds, duplicate rejection, and
  no inert provider/model controls
  (`frontend/src/components/CourseIntake/LearningIntentFields.tsx`,
  `frontend/src/components/CourseIntake/CourseIntakeForm.tsx`).
- [x] T016 [S0401] Implement bounded local source/file preview for text, URL,
  file name, declared media type, and bytes with replacement/reset behavior,
  no document parsing, no object-URL leak, and long-content reflow
  (`frontend/src/components/CourseIntake/SourcePreview.tsx`,
  `frontend/src/components/CourseIntake/CourseIntakeForm.tsx`).
- [x] T017 [S0401] Implement generated-client JSON/multipart submission with a
  stable per-canonical-draft idempotency key, exact-retry reuse, rotation after
  change/success, duplicate-trigger prevention while in flight, safe Problem
  Details mapping, and navigation from the accepted identity
  (`frontend/src/hooks/useCourseSubmission.ts`,
  `frontend/src/hooks/useCourseSubmission.test.tsx`,
  `frontend/src/components/CourseIntake/CourseIntakeForm.tsx`).
- [x] T018 [S0401] Implement job query keys and an exhaustive polling policy
  using generated types, 1.5-second visible/10-second hidden intervals,
  revision-aware snapshots, transient exponential backoff capped at 30
  seconds, terminal stop, listener/timer cleanup, and revalidation on route
  re-entry
  (`frontend/src/components/CourseProgress/queries.ts`,
  `frontend/src/components/CourseProgress/queries.test.ts`).
- [x] T019 [S0401] Build `/jobs/$jobId` and the course-building stage rail from
  the server progress/status allowlist with explicit initial loading, safe
  warnings, unknown-total units, reconnecting/offline, failure, cancellation,
  completed handoff, direct refresh, and uniform missing/foreign recovery
  (`frontend/src/routes/_layout/jobs.$jobId.tsx`,
  `frontend/src/components/CourseProgress/CourseProgressPage.tsx`).
- [x] T020 [S0401] Regenerate the TanStack route tree and update auth,
  navigation, dashboard, and not-found browser assertions for `/`, `/create`,
  dynamic `/jobs/$jobId`, and retired `/items`, without hand-editing generated
  output
  (`frontend/src/routeTree.gen.ts`, `frontend/tests/dashboard.spec.ts`,
  `frontend/tests/login.spec.ts`, `frontend/tests/auth.setup.ts`).
- [x] T021 [S0401] Update current frontend/operator documentation and examples
  for public landing, configured access, intake, progress, deterministic test
  commands, generated-client ownership, and no retention/compliance
  overclaims
  (`frontend/README_frontend.md`, `frontend/AGENTS.md`,
  `docs/onboarding.md`, `docs/dashboard-design.md`,
  `examples/frontend/`).

---

## Testing (4 tasks)

- [x] T022 [S0401] Run focused backend browser-fixture, Phase 03 acceptance,
  route, Ruff/format, mypy, and ty checks from their owning package roots;
  fix every lifecycle, privacy, type, and boundary failure
  (`backend/tests/browser/`, `backend/tests/acceptance/`,
  `backend/tests/api/routes/test_jobs_submission.py`,
  `backend/tests/api/routes/test_jobs_results.py`).
- [x] T023 [S0401] Run frontend Vitest, Biome, TypeScript, route generation,
  and production build; verify generated OpenAPI/client output is unchanged
  and exhaustive external-contract handling remains type safe
  (`frontend/package.json`, `frontend/openapi.json`,
  `frontend/src/client/`).
- [x] T024 [S0401] Run the isolated journey suite and full Playwright
  regression, then inspect 375x812 and 1440x900 light/dark renders, keyboard
  focus, reduced motion, 200% zoom, long content, console/network errors, touch
  targets, layout shift, and document overflow
  (`frontend/playwright.jobs.config.ts`, `frontend/tests/`,
  `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/implementation-notes.md`).
- [x] T025 [S0401] Run repository hooks over tracked and explicit new files,
  ASCII/LF and diff-hygiene audits, secret/privacy/product-surface searches,
  and complete backend/engine/frontend regression gates; record evidence and
  mark every task complete
  (`.pre-commit-config.yaml`,
  `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/implementation-notes.md`,
  `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/tasks.md`).

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All active-session files ASCII-encoded with LF line endings
- [x] `implementation-notes.md` updated
- [x] Ready for `creview` (next step in the
      implement -> creview -> validate sequence)

---

## Next Steps

Run the `implement` workflow step.
