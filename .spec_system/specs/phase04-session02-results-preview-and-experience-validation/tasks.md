# Task Checklist

**Session ID**: `phase04-session02-results-preview-and-experience-validation`
**Total Tasks**: 25
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-20

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0402]` session ref; `TNNN` task ID.

---

## Setup (3 tasks)

- [x] T001 [S0402] Verify the clean Session 01 base, generated result/manifest
  and artifact contracts, deterministic sixteen-artifact scenario, current
  completed-state render, public configuration path, and browser baseline;
  record observations without changing user services
  (`.spec_system/specs/phase04-session02-results-preview-and-experience-validation/implementation-notes.md`,
  `frontend/src/client/`, `frontend/tests/course-journey.spec.ts`).
- [x] T002 [S0402] Write failing unit tests for stable publication/format
  mapping, malformed runtime data, terminal query enablement, preview-cap
  parsing, response normalization, byte/media mismatch, hostile HTML policy,
  duplicate transfer prevention, and URL cleanup
  (`frontend/src/components/CourseResults/*.test.ts`,
  `frontend/src/components/CourseResults/*.test.tsx`,
  `frontend/src/lib/public-config.test.ts`).
- [x] T003 [S0402] [P] Write failing product-flow tests for the real
  sixteen-artifact results workspace, PDF and alternate downloads, answer-key
  disclosure, sandboxed preview/CSP, hostile/oversize failure behavior,
  refresh, retry, mobile, keyboard, focus return, accessibility tree, and
  reduced motion using product-facing assertions
  (`frontend/tests/course-journey.spec.ts`).

---

## Foundation (7 tasks)

- [x] T004 [S0402] Add a typed non-secret `VITE_HTML_PREVIEW_MAX_BYTES`
  frontend build setting with strict positive-integer parsing, exact
  5,242,880-byte fallback, environment documentation, and Compose/Docker
  propagation while leaving backend delivery authoritative
  (`frontend/src/lib/public-config.ts`, `frontend/src/vite-env.d.ts`,
  `frontend/.env.example`, `frontend/Dockerfile`, `docker-compose.yml`,
  `docker-compose.override.yml`).
- [x] T005 [S0402] Implement pure manifest presentation mapping with exhaustive
  generated deliverable/format order, exactly four groups, safe runtime
  rejection, human-readable bytes, preview eligibility, and source/conflict
  labels
  (`frontend/src/components/CourseResults/presentation.ts`,
  `frontend/src/components/CourseResults/presentation.test.ts`).
- [x] T006 [S0402] [P] Implement a terminal-only artifact-manifest TanStack
  query with generated `readJobArtifacts`, owner-scoped keys, finite retry,
  cancellation-safe re-entry, and no completed-state polling loop
  (`frontend/src/components/CourseResults/queries.ts`,
  `frontend/src/components/CourseResults/queries.test.ts`).
- [x] T007 [S0402] [P] Implement artifact response normalization for generated
  Blob/File/string results with UTF-8 byte measurement, exact manifest-size
  comparison, compatible declared media types, safe filename retention, and
  fail-closed errors
  (`frontend/src/components/CourseResults/artifact-transfer.ts`,
  `frontend/src/components/CourseResults/artifact-transfer.test.ts`).
- [x] T008 [S0402] Implement the generated-client artifact transfer hook with
  one in-flight operation per artifact, duplicate-trigger prevention,
  accessible state, safe errors, revocable download URLs, and cleanup on every
  resolve/reject/unmount path
  (`frontend/src/components/CourseResults/useArtifactTransfer.ts`,
  `frontend/src/components/CourseResults/useArtifactTransfer.test.tsx`).
- [x] T009 [S0402] [P] Implement bounded preview-document transformation with
  `DOMParser`, one restrictive CSP, active element and navigation stripping,
  no executable/same-origin dependency, stable serialization, and malformed
  document rejection
  (`frontend/src/components/CourseResults/preview-document.ts`,
  `frontend/src/components/CourseResults/preview-document.test.ts`).
- [x] T010 [S0402] Define the publication-folio hierarchy and missing semantic
  results tokens for light/dark themes, stable card dimensions, visible focus,
  44px practical targets, long-content reflow, global reduced-motion behavior,
  and no decorative diagnostics
  (`frontend/src/index.css`, `docs/dashboard-design.md`).

---

## Implementation (11 tasks)

- [x] T011 [S0402] Build the results workspace around completed job data and
  the terminal manifest query with explicit initial loading, retry, empty,
  malformed, offline, denied, and ready states that preserve uniform
  missing/foreign job recovery
  (`frontend/src/components/CourseResults/CourseResultsWorkspace.tsx`).
- [x] T012 [S0402] Build four semantically ordered, visually distinct
  publication cards for course, review pack, assessment, and instructor answer
  key using only generated manifest/result facts and responsive product-facing
  composition
  (`frontend/src/components/CourseResults/PublicationCard.tsx`,
  `frontend/src/components/CourseResults/CourseResultsWorkspace.tsx`).
- [x] T013 [S0402] Build artifact actions with one clear PDF primary action,
  an accessible HTML/Markdown/PDF/DOCX alternate-format menu, format/size
  labels, per-artifact busy state, duplicate protection, safe transfer errors,
  and no direct fetch
  (`frontend/src/components/CourseResults/ArtifactActions.tsx`,
  `frontend/src/components/CourseResults/useArtifactTransfer.ts`).
- [x] T014 [S0402] Build the lazy HTML preview dialog with generated private
  transfer, exact cap/byte/media checks, preview-only CSP transformation,
  revocable Blob iframe URL, empty sandbox capability set, no-referrer,
  descriptive title, focus return, and close/re-entry/unmount cleanup
  (`frontend/src/components/CourseResults/HtmlArtifactPreview.tsx`,
  `frontend/src/components/CourseResults/ArtifactActions.tsx`).
- [x] T015 [S0402] Build truthful source, conflict, and truncation disclosure
  with safe HTTP(S)-only external links, opener/referrer isolation, empty and
  truncated states, progressive detail, and no compliance or research-quality
  overclaims
  (`frontend/src/components/CourseResults/ResultDisclosure.tsx`,
  `frontend/src/components/CourseResults/CourseResultsWorkspace.tsx`).
- [x] T016 [S0402] Make the instructor answer key visibly private-purpose and
  collapsed by default with correct button state, accessible relationship,
  keyboard toggle, persistent format visibility after expansion, and no
  premature artifact-content exposure
  (`frontend/src/components/CourseResults/PublicationCard.tsx`).
- [x] T017 [S0402] Integrate the completed results workspace into the existing
  `/jobs/$jobId` progress page while preserving the status summary, direct
  refresh, durable URL, terminal polling stop, re-entry, responsive order, and
  current failed/cancelled behavior
  (`frontend/src/components/CourseProgress/CourseProgressPage.tsx`).
- [x] T018 [S0402] Reconcile manifest/download/preview error recovery across
  disabled, retrying, offline, stale-session, owner-denied, removed artifact,
  incompatible media, size mismatch, oversize, and aborted-navigation paths
  with safe Problem Details handling and no private response leakage
  (`frontend/src/components/CourseResults/`,
  `frontend/tests/course-journey.spec.ts`).
- [x] T019 [S0402] Extend the deterministic browser story through real
  completed manifest delivery and at least one real artifact download,
  asserting all sixteen manifest entries, safe filenames, exact sizes,
  format-menu keyboard behavior, answer-key default, and direct refresh
  (`frontend/tests/course-journey.spec.ts`,
  `frontend/playwright.jobs.config.ts`).
- [x] T020 [S0402] Prove preview defense in depth with real HTML plus bounded
  hostile/oversize test inputs or response interception limited to artifact
  payloads, asserting CSP, empty sandbox, no parent DOM injection, no
  navigation/network/console escape, focus return, and object URL cleanup
  (`frontend/tests/course-journey.spec.ts`).
- [x] T021 [S0402] Update frontend, onboarding, design, master-plan, and
  changelog documentation for four-publication results, owner-private
  transfers, preview cap/sandbox, generated-client ownership, deterministic
  verification, and current compliance limits
  (`frontend/README_frontend.md`, `docs/onboarding.md`,
  `docs/dashboard-design.md`,
  `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md`,
  `docs/CHANGELOG.md`).

---

## Testing (4 tasks)

- [x] T022 [S0402] Run focused Vitest, Biome, TypeScript, route generation,
  production build, and generated OpenAPI/client immutability checks; fix
  every contract, accessibility, lifecycle, and bundle diagnostic
  (`frontend/package.json`, `frontend/openapi.json`,
  `frontend/src/client/`).
- [x] T023 [S0402] Run the isolated completed and failed course journeys plus
  the broad Playwright regression, validating real transfers and retaining the
  Session 01 public/intake/progress behavior
  (`frontend/playwright.jobs.config.ts`, `frontend/tests/`).
- [x] T024 [S0402] Inspect 320x568, 375x812, tablet, and 1440x900 light/dark
  rendered results; verify keyboard sequence, accessibility tree/live states,
  focus return, reduced motion, 200% zoom-equivalent reflow, long titles,
  target sizes, layout shift, document overflow, and console/network errors
  with product-facing evidence only
  (`frontend/tests/course-journey.spec.ts`,
  `.spec_system/specs/phase04-session02-results-preview-and-experience-validation/implementation-notes.md`).
- [x] T025 [S0402] Run repository hooks over tracked and explicit new files,
  ASCII/LF and diff-hygiene audits, secret/privacy/sandbox/direct-fetch
  searches, generated-file checks, backend browser fixture, engine, frontend,
  resource-leak, version, and documentation gates; record evidence and mark
  every task complete
  (`.pre-commit-config.yaml`,
  `.spec_system/specs/phase04-session02-results-preview-and-experience-validation/implementation-notes.md`,
  `.spec_system/specs/phase04-session02-results-preview-and-experience-validation/tasks.md`).

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

Run the `creview` workflow step.
