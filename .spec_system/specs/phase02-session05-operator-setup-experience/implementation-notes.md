# Implementation Notes

**Session ID**: `phase02-session05-operator-setup-experience`
**Package**: frontend
**Started**: 2026-07-19 21:46
**Last Updated**: 2026-07-19 22:36

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | 0 minutes |
| Blockers | 0 |

---

## Outcome

The protected React shell now includes a superuser-only `/setup` operator
workspace. It combines one truthful course-system verdict with the safe
authentication state, an explicit ChatGPT device-ceremony action, a stable
eight-check index, browser-safe recovery guidance, and the exact engine CLI
fallback.

Readiness and authentication reads begin in parallel. Authentication status
polls once per second only while `waiting_for_user`, then stops at every
terminal state. Starting a ceremony writes the generated response into the
existing TanStack Query cache, and authenticated completion invalidates the
readiness cache without creating duplicate client-side server state.

The screen renders only generated coarse fields. It does not display tokens,
credentials, account identity, local paths, raw provider payloads, or
exceptions.

---

## Tests-First Evidence

Presentation, query, and browser tests were created before their production
modules. The first unit run failed collection for the missing `presentation`
and `queries` modules while 22 existing tests passed. The first focused
Playwright run passed authentication setup but failed all four setup cases
because `/setup` and its authorization guard did not yet exist.

Rendered QA later exposed two additional regressions before their repairs:
success-tense descriptions appeared beside unavailable checks, and the mobile
CLI surface had 107 pixels of hidden horizontal content. New assertions failed
for both conditions before the neutral descriptions and wrapping command
surface were implemented.

---

## Task Log

| Task Range | Result | Evidence |
|------------|--------|----------|
| T001-T003 | Complete | Session prerequisites, shadcn/design contracts, browser fallback, and protected-shell baselines inspected |
| T004-T009 | Complete | Presentation, polling, authorization, ceremony, privacy, responsive, keyboard, live-status, dark, and reduced-motion tests added first |
| T010-T021 | Complete | Presentation/query contracts, four setup regions, suspense composition, skeleton, route, shell navigation, generated route tree, and design documentation implemented |
| T022 | Complete | Focused setup unit and Playwright suites passed |
| T023 | Complete | 33 unit and 74 complete Playwright tests passed; real unconfigured backend returned both setup reads at HTTP 200 |
| T024 | Complete | Biome, TypeScript, Vite build, generated-client hook, repository pre-commit, dependency/protected-file, ASCII/LF, and patch checks passed |
| T025 | Complete | Ready, waiting, failed/unavailable, light/dark, desktop/mobile, reduced-motion, console, landmark, keyboard, and overflow states inspected |

---

## Files Created

| File | Purpose |
|------|---------|
| `frontend/src/components/SystemSetup/presentation.ts` | Finite labels, variants, input labels, check order, neutral descriptions, and CLI constant |
| `frontend/src/components/SystemSetup/queries.ts` | Stable query keys/options and waiting-only polling |
| `frontend/src/components/SystemSetup/ReadinessOverview.tsx` | Readiness verdict, model, admission, freshness, and input modes |
| `frontend/src/components/SystemSetup/AuthenticationPanel.tsx` | Signed-out, waiting, authenticated, failed, start, external-link, and copy states |
| `frontend/src/components/SystemSetup/SystemChecklist.tsx` | Stable numbered coarse-check index |
| `frontend/src/components/SystemSetup/RecoveryPanel.tsx` | Safe warnings/actions and exact wrapping CLI fallback |
| `frontend/src/components/SystemSetup/SystemSetupWorkspace.tsx` | Parallel suspense reads, mutation/cache coordination, and live announcement |
| `frontend/src/components/Pending/PendingSystemSetup.tsx` | Static geometry-matched loading state |
| `frontend/src/routes/_layout/setup.tsx` | Superuser guard, metadata, Suspense, and recoverable route error |
| `frontend/src/components/SystemSetup/*.test.ts` | Presentation and query regressions |
| `frontend/tests/setup.spec.ts` | Protected route, device ceremony, privacy, state, and rendered regressions |

## Files Modified

| File or Area | Change |
|--------------|--------|
| Protected shell/sidebar | Added the superuser-only setup navigation item and command-strip label |
| Generated route tree | Regenerated through the Vite/TanStack route plugin |
| `docs/dashboard-design.md` | Added the operator field-guide blueprint, data boundary, responsive rules, and QA contract |
| Apex PRD/state/session artifacts | Planned and recorded Session 05 implementation |

---

## Key Implementation Decisions

1. **One verdict leads**: the API status and admission flag map to one
   plain-language answer; the browser does not calculate a readiness score.
2. **Parallel reads share one boundary**: `useSuspenseQueries` starts both
   independent generated GETs without a waterfall.
3. **Polling is finite by state**: the interval is `1000` only for
   `waiting_for_user`; all terminal states return `false`.
4. **The query cache owns server state**: device start writes its response to
   the auth key rather than introducing parallel component state.
5. **Authorization happens before feature reads**: the route guard resolves
   the existing current-user query and redirects non-superusers before either
   system query mounts.
6. **Checks use neutral definitions**: a description explains what a check
   represents while the adjacent badge alone states ready or unavailable.
7. **Recovery remains browser-safe**: only API warnings/actions and the exact
   package command render; the command wraps on mobile instead of creating
   hidden or document-level overflow.
8. **No new visual runtime**: existing tokens, shadcn primitives, Lucide
   icons, and reduced-motion behavior cover the screen without a dependency,
   primitive, or motion-system change.

---

## Verification

### Focused Tests

- Vitest presentation/query and existing source tests: 33 passed.
- Focused Playwright setup project: 7 passed, including auth setup and two
  formal-review edge cases.
- Visual repair regressions: unit 33 passed; focused failed/mobile case 2
  passed including auth setup.

### Complete Frontend Suite

- `npm run test:unit`: 33 passed.
- `npm run test:e2e` with the local backend and isolated Mailcatcher: 76
  passed.

### Complete Repository And Release

- Backend shell on a fresh migrated database: 296 passed.
- Engine deterministic suite: 464 passed; 1 explicit live credential gate
  skipped.
- Complete deterministic count: 869 passed.
- Engine Ruff, strict mypy, and source-scoped ty: PASS.
- Repository/package version, lockfile, version guide, and changelog:
  `0.6.0`.
- Wheel and source distribution: PASS; wheel metadata reports `0.6.0`.

### Static And Repository Gates

- Biome: 138 files checked.
- TypeScript no-emit: PASS.
- Production Vite build: 2,204 modules transformed.
- Repository pre-commit: all hooks passed, including backend type/static
  checks, frontend checks, generated-client verification, and Zizmor.
- Dependency lock, generated API client, and protected UI primitives: no
  final diff.
- New frontend source/test files: ASCII with LF endings.
- `git diff --check`: PASS.

### Rendered And Real-Shell QA

- Mocked ready desktop/light, waiting desktop/light, and unavailable
  mobile/dark/reduced-motion states: correct page identity, one `main`, zero
  document overflow, and zero console warnings/errors.
- Waiting flow: external verification link, code copy announcement, polling,
  authenticated completion, and challenge removal passed.
- Real unconfigured shell: readiness and auth status both returned HTTP 200;
  the screen showed the truthful unavailable state with no prohibited detail,
  overflow, duplicate landmark, or console problem.
- Screenshots were inspected at:
  `/tmp/txt2crs-session05-ready-desktop.png`,
  `/tmp/txt2crs-session05-waiting-desktop.png`,
  `/tmp/txt2crs-session05-unavailable-mobile-dark.png`, and
  `/tmp/txt2crs-session05-real-unconfigured.png`. The longest allowed code
  and repeated safe values were inspected at
  `/tmp/txt2crs-session05-long-code-320.png`.

---

## Deviations And Environment Notes

- The Browser plugin was unavailable, so the documented fallback used the
  repository's JavaScript Playwright/Chromium toolchain.
- Unrelated services occupied the documented PostgreSQL, backend,
  Mailcatcher SMTP, and default frontend ports. The project used isolated
  temporary mappings: PostgreSQL `5448`, backend `8013`, frontend `5184`,
  and Mailcatcher API `1082`. No unrelated container was changed.
- The first live read reached a stale backend image and returned 404 for both
  Session 04 routes. Rebuilding/recreating only this project's backend against
  current source restored both routes at HTTP 200.
- A direct standalone client-generation invocation produced formatter-only
  churn in protected generated files. That known invocation-only diff was
  reversed; the repository's generated-client pre-commit hook passed and the
  final protected client diff is empty.
- The first complete shell run reused the browser-test database. More than 100
  E2E-created users pushed a deliberately old pagination fixture off page one,
  yielding one environment-only failure after 295 passes. A fresh isolated
  database was migrated, passed 296/296, and was removed.
- An unscoped engine `ty check` traversed the parent uv workspace and reported
  known shell-test diagnostics. The project repository `ty` hook passed, and
  the correctly source-scoped engine `ty check src` passed.
- No API, database, Alembic migration, dependency, protected primitive,
  hand-edited client, learner screen, logout/account switch, or credential
  input was added.

---

## Self-Review Repairs

Rendered mobile inspection found that the authentication card's original
two-column header could widen the document when a long terminal title and
badge competed for space. The header now stacks below `sm`, all grid children
can shrink, and a regression proves zero document overflow.

The same rendered pass found that the CLI command was technically available
through element scrolling but visibly clipped, and that success-tense check
descriptions contradicted unavailable badges. Tests now require a fully
fitting command and state-neutral definitions; both repairs pass in the dark
375x812 screenshot.

Formal base-to-head review then resolved four Medium and two Low findings:

1. Initial authenticated mounts no longer issue two StrictMode invalidations
   after the readiness request that just completed.
2. Authentication messages override the shared one-line clamp and remain
   fully readable.
3. The schema's longest allowed device code wraps at 320px without element or
   document overflow.
4. Terminal state clears temporary copy feedback from the live announcement.
5. Repeated safe input/warning/action values use collision-free React keys.
6. Readiness and check statuses stack below their descriptions before `sm`,
   preserving 230px and 152px reading widths at 320px instead of narrow word
   columns.

All six review repairs were observed failing in Playwright before their
implementations. The repaired focused suite passes 7/7, and
`code-review.md` records `Result: RESOLVED`.

---

## Next Step

Phase 02 is complete. Plan Phase 03 durable jobs API work next.
