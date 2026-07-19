# Task Checklist

**Session ID**: `phase02-session05-operator-setup-experience`
**Total Tasks**: 25
**Estimated Duration**: 3.5-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0205]` session ref; `TNNN` task ID.

---

## Setup And Evidence (3 tasks)

- [x] T001 [S0205] Verify Session 04 generated contracts, Session 03 cache
  semantics, route authorization, query/session, and sidebar prerequisites
  (`.spec_system/specs/phase02-session05-operator-setup-experience/spec.md`)
- [x] T002 [S0205] Inspect installed shadcn components/docs, current design
  system, responsive shell, reduced-motion, error, and Playwright seams
  (`frontend/components.json`, `docs/dashboard-design.md`)
- [x] T003 [S0205] Capture light/reduced-motion desktop and mobile protected
  shell baselines and record Browser-plugin fallback
  (`/tmp/txt2crs-session05-baseline-*.png`)

---

## Tests-First Foundation (6 tasks)

- [x] T004 [S0205] [P] Write presentation tests for finite status labels,
  check ordering, variants, safe fields, and exact CLI command
  (`frontend/src/components/SystemSetup/presentation.test.ts`)
- [x] T005 [S0205] [P] Write query tests for stable keys, parallel option
  factories, waiting-only polling, and terminal stop
  (`frontend/src/components/SystemSetup/queries.test.ts`)
- [x] T006 [S0205] Write Playwright route tests for superuser navigation and
  non-superuser redirect before system requests (`frontend/tests/setup.spec.ts`)
- [x] T007 [S0205] Write Playwright start/wait/poll/authenticated flow with
  safe external link, code, copy, and terminal challenge removal
  (`frontend/tests/setup.spec.ts`)
- [x] T008 [S0205] Write Playwright unavailable/failed/retry and prohibited-
  field assertions (`frontend/tests/setup.spec.ts`)
- [x] T009 [S0205] Write Playwright responsive, keyboard, live-status,
  dark-mode, and reduced-motion assertions (`frontend/tests/setup.spec.ts`)

---

## Implementation (12 tasks)

- [x] T010 [S0205] Implement finite presentation contracts, safe copy,
  ordered check/input metadata, and CLI constant
  (`frontend/src/components/SystemSetup/presentation.ts`)
- [x] T011 [S0205] Implement stable readiness/auth query options and bounded
  waiting-only status polling (`frontend/src/components/SystemSetup/queries.ts`)
- [x] T012 [S0205] Implement the readiness verdict, freshness, model, and
  enabled-input overview (`frontend/src/components/SystemSetup/ReadinessOverview.tsx`)
- [x] T013 [S0205] Implement signed-out/waiting/authenticated/failed device
  panel, mutation pending/error, external link, and code copy
  (`frontend/src/components/SystemSetup/AuthenticationPanel.tsx`)
- [x] T014 [S0205] Implement the numbered coarse-check index
  (`frontend/src/components/SystemSetup/SystemChecklist.tsx`)
- [x] T015 [S0205] Implement warnings, safe recovery actions, and exact CLI
  fallback (`frontend/src/components/SystemSetup/RecoveryPanel.tsx`)
- [x] T016 [S0205] Implement parallel suspense query/mutation composition,
  cache writes, refresh, and live state
  (`frontend/src/components/SystemSetup/SystemSetupWorkspace.tsx`)
- [x] T017 [S0205] Implement the static accessible setup skeleton
  (`frontend/src/components/Pending/PendingSystemSetup.tsx`)
- [x] T018 [S0205] Implement superuser route guard, metadata, Suspense, and
  recoverable error boundary (`frontend/src/routes/_layout/setup.tsx`)
- [x] T019 [S0205] Add the superuser-only sidebar item and setup shell label
  (`frontend/src/components/Sidebar/AppSidebar.tsx`, `frontend/src/routes/_layout.tsx`)
- [x] T020 [S0205] Regenerate the route tree through TanStack/Vite and verify
  no generated API client drift (`frontend/src/routeTree.gen.ts`)
- [x] T021 [S0205] Document the operator field-guide screen, states,
  responsive transformation, and accessibility contract
  (`docs/dashboard-design.md`)

---

## Testing And Completion (4 tasks)

- [x] T022 [S0205] Run focused Vitest and mocked Playwright setup suites.
- [x] T023 [S0205] Run complete frontend unit/E2E suites and real
  unconfigured-backend setup flow.
- [x] T024 [S0205] Run Biome, TypeScript, Vite build, generated-contract,
  repository pre-commit, dependency/protected-file, and ASCII/LF checks.
- [x] T025 [S0205] Inspect light/dark 1440x900 and 375x812 rendered states,
  keyboard/console/overlay/overflow behavior, then record exact evidence.

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] `implementation-notes.md` updated
- [x] Ready for `creview`

---

## Next Steps

Run the `creview` workflow step.
