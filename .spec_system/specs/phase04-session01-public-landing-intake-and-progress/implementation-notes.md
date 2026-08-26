# Implementation Notes

> Historical completed-session record. Event-era deployment, judge, and
> signup assumptions below are not current product restrictions.

**Session ID**: `phase04-session01-public-landing-intake-and-progress`
**Package**: null
**Started**: 2026-07-20 03:58
**Last Updated**: 2026-07-20 05:40

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | 0 minutes |
| Blockers | 0 |

---

## Task Log

### 2026-07-20 - Session Start

**Environment verified**:

- [x] Apex state and session artifacts confirmed
- [x] Node, npm, Docker, uv, jq, and Git available
- [x] Cross-package directory structure ready
- [x] Isolated PostgreSQL 18 accepts connections
- [x] Database revision matches repository Alembic head

---

### Task T001 - Verify prerequisites and current browser baseline

**Started**: 2026-07-20 03:58
**Completed**: 2026-07-20 04:00
**Duration**: 2 minutes

**Notes**:

- Confirmed Phase 04 Session 01 is the active cross-cutting session over clean
  base commit `08297e317683ad6cf608e4d9333bfbb819955ef7`.
- Verified the generated client exposes JSON/upload submission plus
  owner-scoped status, manifest, and download operations; current route
  generation contains the transitional protected root and no donor `/items`.
- Inspected the Phase 03 desktop and mobile baseline. It truthfully names the
  four assets and fits both viewports, but remains protected and has no intake
  or progress experience, exactly matching this session's starting scope.
- The Browser plugin is not available in this environment. Per the frontend
  testing guidance, rendered work uses the repository JavaScript Playwright
  toolchain.

**Files Changed**:

- `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/implementation-notes.md`
  - initialized task evidence and baseline observations.
- `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/tasks.md`
  - marked T001 complete.

**Verification**:

- Command/check: `bash .spec_system/scripts/analyze-project.sh --json`
  - Result: PASS - Phase 04, active Session 01, 14 completed prerequisite
    sessions, and all three registered packages reported.
- Command/check:
  `bash .spec_system/scripts/check-prereqs.sh --json --env` and
  `--tools "node,npm,docker,uv"`
  - Result: PASS - spec system, jq, Git, uv, Node 24.14.0, npm 11.18.0, and
    Docker 29.5.3 available.
- Command/check: isolated PostgreSQL `pg_isready`, stored `alembic_version`,
  and repository `uv run --directory backend alembic heads`
  - Result: PASS - database accepts connections and both revisions are
    `a7d9c2e4f601`.
- Command/check: pre-session commit hook chain and transition reports
  - Result: PASS - Ruff, format, mypy, ty, Biome, TypeScript, generated client,
    Zizmor, 473 backend tests, 470 engine tests plus one explicit live skip,
    and 65 Playwright tests are green at the base.
- UI product-surface check: PASS - inspected
  `/tmp/txt2crs-dashboard-desktop.png` at 1440x1000 and
  `/tmp/txt2crs-dashboard-mobile.png` at 390x1464; no diagnostic, runtime,
  route-owner, package, or scaffold copy appears.
- UI craft check: PASS - the existing editorial type, warm surfaces, semantic
  actions, mobile stacking, and four-asset hierarchy establish a coherent
  baseline for the research-atelier evolution.

**BQC Fixes**:

- State freshness: recorded the exact clean base, generated contract, and
  rendered route state before any code change.

---

## Checkpoint

**Next task**: T002 - write failing deterministic browser-application tests.

---

### Task T002 - Write failing deterministic browser-application tests

**Started**: 2026-07-20 04:00
**Completed**: 2026-07-20 04:02
**Duration**: 2 minutes

**Notes**:

- Added tests for explicit test-only enablement, production route isolation,
  real authenticated HTTP submission through durable execution, repeat reads,
  owner-hidden 404s, and post-lifespan cleanup.
- The future fixture contract accepts only a named finite scenario and isolated
  state directory. Tests use the normal authentication helper and real job
  routes rather than replacing response bodies.

**Files Changed**:

- `backend/tests/browser/test_deterministic_app.py` - added the red fixture,
  lifecycle, durable journey, and privacy contracts.
- `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/implementation-notes.md`
  - recorded tests-first evidence.
- `.spec_system/specs/phase04-session01-public-landing-intake-and-progress/tasks.md`
  - marked T002 complete.

**Verification**:

- Command/check:
  `cd backend && uv run pytest tests/browser/test_deterministic_app.py -q`
  - Result: PASS (tests-first gate) - collection fails because
    `tests.browser.deterministic_app` does not exist yet; no production code
    was present to satisfy the new contract.
- UI product-surface check: N/A - backend test source only.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:

- Trust boundary enforcement: the red contract requires explicit test-only
  enablement and proves the production OpenAPI graph contains no fixture path.
- Resource cleanup: the test owns one full TestClient lifespan and asserts all
  shell worker/readiness/submission/runtime references are cleared afterward.

---

## Checkpoint

**Next task**: T003 - write failing product-flow and state-machine tests.

---

### Task T003 - Write failing product-flow and state-machine tests

**Started**: 2026-07-20 04:02
**Completed**: 2026-07-20 04:04
**Duration**: 2 minutes

**Notes**:

- Added red Zod/payload tests for exact prompt/text/URL bounds, consent,
  unique goals, inactive-field stripping, and multipart metadata.
- Added red polling tests for generated-client delegation, stable keys, every
  non-terminal and terminal state, document visibility, transient backoff, and
  last-safe-snapshot behavior.
- Added public landing plus deterministic prompt/upload/mobile/failure browser
  scenarios. Real-job scenarios are explicitly gated to the future isolated
  Playwright configuration; the public story remains part of the normal suite.

**Files Changed**:

- `frontend/src/lib/schemas/job.test.ts` - strict request and payload red tests.
- `frontend/src/components/CourseProgress/queries.test.ts` - finite polling red
  tests.
- `frontend/tests/course-journey.spec.ts` - product-flow Playwright scenarios.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check:
  `cd frontend && npx vitest run src/lib/schemas/job.test.ts src/components/CourseProgress/queries.test.ts`
  - Result: PASS (tests-first gate) - both suites fail import because the
    `job.ts` and `queries.ts` implementations do not exist.
- Command/check:
  `cd frontend && VITE_API_URL=http://localhost:8012 npx playwright test tests/course-journey.spec.ts --list`
  - Result: PASS - setup plus five product scenarios compile and list.
- UI product-surface check: PASS (test contract) - assertions reject runtime,
  route-owner, provider, traceback, filesystem, and raw document-content copy
  from normal surfaces.
- UI craft check: PASS (test contract) - accessible product headings,
  outcome-specific actions, mobile 44px action, overflow, keyboard, and
  reduced-motion coverage are explicit.

**BQC Fixes**:

- Duplicate action prevention: the happy path deliberately double-clicks the
  mutation action and expects one durable job route.
- Contract alignment: tests enumerate every generated job status and verify
  JSON/upload payloads instead of asserting a hand-written transport.
- Failure completeness: public, reconnecting, failed, ownership, and recovery
  outcomes are included before implementation.

---

## Checkpoint 1 - Tests First

- Tasks complete: 3 / 25.
- Red backend and frontend contracts exist and fail only because their target
  implementation modules are absent.
- Session objective remains the public-to-terminal learner slice; no result
  manifest or preview scope was added.
- Next task: T004, shared deterministic test support.

---

### Task T004 - Share deterministic course test support

**Started**: 2026-07-20 04:04
**Completed**: 2026-07-20 04:05
**Duration**: 1 minute

**Notes**:

- Moved the durable harnesses, finite execution profile, canonical requests,
  evidence ledger, and complete course scenario into one typed support module.
- Kept the acceptance conftest as a thin fixture adapter and intentionally
  re-exported its existing harness type imports, so every current acceptance
  test remains source-compatible.
- Added descriptive public builders for submission-only and complete-result
  scenarios. The browser application can now reuse real deterministic engine
  behavior without copying model turns or artifact data.

**Files Changed**:

- `backend/tests/support/deterministic_course.py` - shared typed harnesses,
  profile, evidence, course, and scenario builders.
- `backend/tests/support/__init__.py` - marks the shared test-support package.
- `backend/tests/acceptance/conftest.py` - thin compatibility fixtures.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: focused submission and result/recovery acceptance suites
  against the isolated PostgreSQL 18 test service
  - Result: PASS - 14 tests passed.
- Command/check: Ruff check and format check over both moved and adapter files
  - Result: PASS - no lint or formatting drift.
- UI product-surface check: N/A - typed backend test support only.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:

- Composition integrity: there is one deterministic scenario definition for
  acceptance and browser journeys rather than a second route-response fixture.
- Compatibility: existing imports from `tests.acceptance.conftest` continue to
  resolve without modifying unrelated acceptance tests.

---

## Checkpoint

**Next task**: T005 - implement the isolated deterministic browser application.

---

### Task T005 - Implement isolated deterministic browser application

**Started**: 2026-07-20 04:05
**Completed**: 2026-07-20 04:11
**Duration**: 6 minutes

**Notes**:

- Added a fail-closed Uvicorn/FastAPI factory below `tests/` that accepts only
  the reviewed `complete` or `failed` scenarios and an explicit private state
  directory when `TXT2CRS_ENABLE_BROWSER_TEST_APP=1`.
- Reused the production app factory, routes, middleware, normal database auth,
  generated shell schemas, owner-hidden reads, runtime ownership, and real
  serial worker. Only the package lifecycle, finite test execution profile,
  and prompt/text deterministic readiness are supplied through typed seams.
- Added an execution-profile injection seam to `create_app`; its production
  default remains the existing `build_execution_profile`, while the test app
  can submit the same small profile used by the shared accepted scenario.
- Cleanup remains production-ordered: worker, readiness, authentication,
  runtime owner, then facade. The test proves all exposed state references are
  cleared after lifespan exit.

**Files Changed**:

- `backend/tests/browser/deterministic_app.py` - isolated lifecycle, local
  readiness, environment factory, scenario allowlist, and private path setup.
- `backend/tests/browser/__init__.py` - marks the browser support package.
- `backend/app/main.py` - typed execution-profile factory seam with unchanged
  production default.
- `backend/tests/browser/test_deterministic_app.py` - aligned the finite request
  with the shared accepted scenario and stopped polling on every terminal
  status.
- `frontend/tests/course-journey.spec.ts` - aligned the credential-free happy
  path with the same finite deterministic request.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: `pytest tests/browser/test_deterministic_app.py -q`
  - Result: PASS - 4 lifecycle, production-isolation, real completion, durable
    reread, and owner-hidden contracts passed.
- Command/check: app lifespan regression plus browser fixture
  - Result: PASS - 13 tests passed.
- Command/check: Ruff check/format and mypy over the app seam and browser
  fixture
  - Result: PASS - formatting clean and no type errors.
- UI product-surface check: PASS (fixture boundary) - no `/__test__` route,
  arbitrary scenario payload, credential, path, or raw exception enters the
  production OpenAPI graph.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:

- Readiness truthfulness: deterministic package composition correctly does
  not claim production upload adapters. The browser-only readiness owner
  admits only the locally supported prompt/text modes while still requiring
  live worker capacity and free runtime ownership.
- Scenario alignment: the browser request now uses the accepted scenario's
  exact learning objective, preventing a fake green result from bypassing
  engine validation.

---

## Checkpoint

**Next task**: T006 - wire isolated Playwright process orchestration.

---

### Task T006 - Wire isolated Playwright process orchestration

**Started**: 2026-07-20 04:11
**Completed**: 2026-07-20 04:14
**Duration**: 3 minutes

**Notes**:

- Added a dedicated single-worker Playwright configuration on ports 8013 and
  5184. It launches the test-only Uvicorn factory and current Vite source,
  never reuses an existing server, and leaves the normal Compose-driven
  `playwright.config.ts` unchanged.
- Each run creates an owner-only operating-system temporary directory for
  engine SQLite/artifacts and deletes it only after Playwright stops both
  servers. The configuration allowlists complete/failed scenarios.
- The setup project opts into the real local-only signup route for one unique
  normal learner, then authenticates through the real access-token route and
  writes a dedicated ignored storage-state file. Normal test configuration
  continues using the provisioned superuser behavior.
- The backend test application accepts an explicit frontend host so CORS
  remains narrow for the isolated Vite port.

**Files Changed**:

- `frontend/playwright.jobs.config.ts` - isolated backend/Vite orchestration,
  scenario selection, fresh state, normal-user setup, and cleanup.
- `frontend/tests/auth.setup.ts` - optional real signup before the existing
  login-route authentication path.
- `frontend/tests/config.ts` - environment-selectable ignored auth-state path.
- `backend/tests/browser/deterministic_app.py` - explicit isolated CORS host.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check:
  `npx playwright test --config playwright.jobs.config.ts --list`
  - Result: PASS - setup plus all five product scenarios compile and list.
- Command/check: dedicated setup project against the isolated PostgreSQL 18
  service
  - Result: PASS - backend and Vite started, real signup returned 201, real
    login returned 200, authenticated `/users/me` returned 200, and the setup
    test passed.
- Command/check: post-run port and temporary-state audit
  - Result: PASS - ports 8013/5184 were closed and no
    `/tmp/txt2crs-browser-*` directory remained.
- Command/check: targeted Biome and standalone TypeScript checks
  - Result: PASS - configuration and setup sources are formatted and type
    safe.
- UI product-surface check: PASS (orchestration) - fixture flags and scenario
  controls stay in process environment and never enter browser routes.
- UI craft check: N/A - no page rendering changed.

**BQC Fixes**:

- Account isolation: the job journey no longer mutates or assumes an operator
  password; it creates a unique normal user through the normal authorization
  path.
- Environment drift: verification used the dedicated PostgreSQL service
  credentials supplied at process start after detecting that the long-running
  user Compose database no longer matched the current dotenv password.

---

## Checkpoint

**Next task**: T007 - implement strict centralized course-intake schemas.

---

### Task T007 - Implement strict centralized course-intake schemas

**Started**: 2026-07-20 04:14
**Completed**: 2026-07-20 04:18
**Duration**: 4 minutes

**Notes**:

- Added reusable prompt, pasted-text, HTTPS, audience, prior-knowledge, goal,
  level, age, literal-consent, and PDF/DOCX/PPTX file fields with the exact
  shell character, byte, filename, extension, and MIME ceilings.
- Built one strict form schema over prompt, text, URL, YouTube, and upload
  modes. Mode-specific validation happens before a transform removes the
  inactive source field, so stale prompt text cannot enter multipart metadata
  and a stale file cannot enter JSON request identity.
- Added generated-type-backed JSON and multipart payload shaping. Optional
  empty intent fields become explicit `null`; language stays the server-aligned
  `auto` literal; no owner, model, policy, budget, or filesystem value is
  accepted.
- Kept an untouched form's consent boolean and blank controls representable
  while requiring literal `true` before any parsed submission exists.

**Files Changed**:

- `frontend/src/lib/schemas/fields.ts` - exact reusable course fields and local
  upload fact validation.
- `frontend/src/lib/schemas/job.ts` - strict intake, inactive-field removal,
  defaults, and generated-client payload union.
- `frontend/src/lib/schemas/index.ts` - centralized exports.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: `vitest run src/lib/schemas/job.test.ts`
  - Result: PASS - 11 assertions across exact payload, prompt/text/URL bounds,
    literal consent, 10-goal uniqueness, and multipart stripping passed.
- Command/check: targeted Biome check/write
  - Result: PASS - schema sources and tests are formatted with organized
    imports/exports.
- Command/check: repository TypeScript build check
  - Result: PASS for T007 - the schema implementation has no error; the only
    remaining diagnostic is the intentionally red T018 missing `queries.ts`.
- UI product-surface check: PASS (validation copy) - errors describe learner
  actions and never expose backend class, provider, path, or policy details.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:

- Request identity: inactive source values are absent after parsing rather
  than merely blanked.
- Generated contract ownership: payload types come from `@/client`; no parallel
  transport interface was introduced.

---

## Checkpoint

**Next task**: T008 - add validated course-domain identifier brands.

---

### Task T008 - Add validated course-domain identifier brands

**Started**: 2026-07-20 04:18
**Completed**: 2026-07-20 04:19
**Duration**: 1 minute

**Notes**:

- Added failing tests before implementation for the finite job/artifact
  grammar, the distinct idempotency-key first-character rule, unsafe values,
  trusted casts, and nominal type separation.
- Added separate `JobId`, `ArtifactId`, and `IdempotencyKey` brands. Job and
  artifact values share runtime grammar but remain compile-time incompatible;
  UUID-backed user identity stays separate.
- Added validating factories/guards for untrusted values and explicitly named
  `as*` casts for generated backend responses or locally generated retry keys.

**Files Changed**:

- `frontend/src/lib/types/branded.test.ts` - tests-first runtime and nominal
  contracts.
- `frontend/src/lib/types/branded.ts` - brands, exact guards, factories, and
  trusted casts.
- `frontend/src/lib/types/index.ts` - centralized exports.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: initial focused Vitest run
  - Result: PASS (tests-first gate) - all three tests failed because the new
    factories/casts did not exist.
- Command/check: focused Vitest after implementation
  - Result: PASS - 3 tests passed.
- Command/check: targeted Biome and repository TypeScript check
  - Result: PASS for T008 - branded sources are clean; only the intentionally
    red T018 missing polling module remains.
- UI product-surface check: N/A - type/domain foundation only.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:

- Identity safety: generated finite package IDs cannot be confused with
  UUID-backed user IDs or owner-scoped retry keys.
- Error privacy: validating factories describe the required grammar without
  echoing the rejected identifier.

---

## Checkpoint

**Next task**: T009 - implement bounded session-only prompt draft persistence.

---

### Task T009 - Implement bounded session-only prompt draft persistence

**Started**: 2026-07-20 04:19
**Completed**: 2026-07-20 04:21
**Duration**: 2 minutes

**Notes**:

- Added failing tests before implementation for versioned save/read/consume,
  corrupt JSON, stale version, invalid prompt, oversized storage, invalid
  replacement, unrelated storage isolation, and unavailable browser storage.
- Added a strict version-1 envelope stored only in `window.sessionStorage`.
  Reads apply a serialized-size guard before JSON parsing and re-run the exact
  prompt schema before returning text.
- Invalid replacement input clears the older draft. Consume clears valid or
  invalid data; all storage denial paths fail closed without logging or
  throwing.

**Files Changed**:

- `frontend/src/lib/course-draft.test.ts` - tests-first persistence and privacy
  contracts with isolated in-memory Storage implementations.
- `frontend/src/lib/course-draft.ts` - bounded session-only storage helpers.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: initial focused Vitest run
  - Result: PASS (tests-first gate) - collection failed because the draft
    module did not exist.
- Command/check: focused Vitest after implementation
  - Result: PASS - 7 assertions passed.
- Command/check: targeted Biome and repository TypeScript check
  - Result: PASS for T009 - draft sources are clean; only the intentionally
    red T018 missing polling module remains.
- UI product-surface check: PASS (privacy boundary) - prompt text is never
  placed in a URL, localStorage, log, or network request by this helper.
- UI craft check: N/A - no rendered UI changed.

**BQC Fixes**:

- Re-entry safety: stored data is treated as untrusted on every read and
  cleared on schema/version/size failure.
- Privacy: storage access exceptions return the safe no-draft state and never
  fall back to persistent storage.

---

## Checkpoint

**Next task**: T010 - define research-atelier hierarchy and semantic tokens.

---

### Task T010 - Define research-atelier hierarchy and semantic tokens

**Started**: 2026-07-20 04:21
**Completed**: 2026-07-20 04:23
**Duration**: 2 minutes

**Notes**:

- Applied the visual-upgrade skill's project-specific guidance to define an
  original research-atelier hierarchy without adding imagery, gradients,
  ornamental diagnostics, or a new component/motion dependency.
- Added semantic publication, workbench, inactive-stage, active-stage, and
  completed-stage roles in light/dark themes plus journey rhythm, reading
  width, workspace width, and 44px touch-target roles.
- Strengthened focus-ring roles to opaque theme-aware forest values so focus
  remains legible on background, workbench, and publication surfaces.
- Replaced the transitional route design with public landing, authenticated
  intake, and owner progress blueprints, including mobile transformation,
  content hierarchy, safe state copy, and Session 02 result boundary.

**Files Changed**:

- `frontend/src/index.css` - learner-journey semantic roles and layout tokens.
- `docs/dashboard-design.md` - current Phase 04 route map and research-atelier
  screen blueprints.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: targeted Biome CSS check
  - Result: PASS - token source is valid and formatted.
- Command/check: direct Vite production build
  - Result: PASS - 2,183 modules transformed and production assets emitted.
- Command/check: generated-route diff audit after Vite plugin execution
  - Result: PASS - `routeTree.gen.ts` remained unchanged.
- UI product-surface check: PASS (design contract) - only learner/product
  hierarchy is specified; no package/runtime/provider/path terminology appears
  in normal surface copy.
- UI craft check: PASS (design contract) - restrained semantic roles, one
  dominant action, asymmetric desktop composition, logical mobile sequence,
  theme parity, visible focus, and no decorative motion are explicit.

**BQC Fixes**:

- Token discipline: new feature code can use named roles instead of
  route-local raw colors.
- Accessibility: stage color is never sufficient without labels and progress
  copy; the documented mobile rail avoids horizontal timelines and overflow.

---

## Checkpoint

**Next task**: T011 - add explicit public-signup frontend build configuration.

---

### Task T011 - Add explicit public-signup frontend build configuration

**Started**: 2026-07-20 04:23
**Completed**: 2026-07-20 04:25
**Duration**: 2 minutes

**Notes**:

- Added failing tests before implementation for absent, empty, false,
  uppercase, and exact-true visibility values.
- Added one strict display-only parser and `publicSignupVisible` build value.
  Anything except the exact string `true` resolves false; this setting never
  grants backend authorization.
- Typed and documented the optional Vite setting, defaulted the Docker build
  argument false, and passed the backend-aligned local/judge value through
  production, development, and Playwright Compose builds.

**Files Changed**:

- `frontend/src/lib/public-config.test.ts` - strict parsing tests.
- `frontend/src/lib/public-config.ts` - display-only frontend config boundary.
- `frontend/src/vite-env.d.ts`, `frontend/.env.example`,
  `frontend/Dockerfile` - typed, documented, false-defaulted build setting.
- `docker-compose.yml`, `docker-compose.override.yml` - explicit build/runtime
  pass-through.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: initial focused Vitest run
  - Result: PASS (tests-first gate) - collection failed because the public
    config module did not exist.
- Command/check: public-config and frontend security-contract Vitest suites
  - Result: PASS - 10 tests passed.
- Command/check: `docker compose config --quiet`
  - Result: PASS - production and local overrides resolve with the new build
    argument.
- Command/check: targeted Biome and repository TypeScript check
  - Result: PASS for T011 - only the intentionally red T018 polling module
    remains missing.
- UI product-surface check: PASS (configuration) - absent/malformed values
  yield invite-only visibility, and backend rejection remains authoritative.
- UI craft check: N/A - route copy is implemented in T012/T013.

**BQC Fixes**:

- Fail-safe default: no dotenv or build argument is required to keep public
  signup hidden.
- Authority separation: the frontend value is named/documented as visibility,
  while backend `ENABLE_PUBLIC_SIGNUP` continues to decide access.

---

## Checkpoint

**Next task**: T012 - build the public research-atelier landing page.

---

### Task T012 - Build the public research-atelier landing page

**Started**: 2026-07-20 04:25
**Completed**: 2026-07-20 04:29
**Duration**: 4 minutes

**Notes**:

- Replaced the protected transitional root with a genuinely public `/` route
  that performs no current-user or job query.
- Built an asymmetric source-to-four-publications signature, precise
  three-step workflow, truthful AI/research and owner-access section, and one
  primary sign-in path. Configured account creation appears only when the
  display flag is exactly true.
- Kept static definitions outside render, used semantic landmarks and ordered
  content, and composed the visual entirely from type, keylines, theme tokens,
  and Lucide icons. No image, gradient, decorative runtime, or diagnostic copy
  was added.
- Retired the conflicting `_layout/index.tsx` file so TanStack owns one
  unambiguous public root. T013 adds the protected `/create` destination.

**Files Changed**:

- `frontend/src/components/Landing/LandingPage.tsx` - public header, hero,
  publication signature, process, trust, access, and footer composition.
- `frontend/src/routes/index.tsx` - public route and document metadata.
- `frontend/src/routes/_layout/index.tsx` - removed transitional protected
  root.
- `frontend/src/index.css` - exposed the existing strong-border role to
  Tailwind feature composition.
- `frontend/src/routeTree.gen.ts` - regenerated by the Vite router plugin.
- Session task and implementation notes - progress and evidence.

**Verification**:

- Command/check: targeted Biome and direct Vite production build
  - Result: PASS - accessibility lint is clean; 2,185 modules transformed.
- Command/check: isolated public learner Playwright story
  - Result: PASS - real setup plus the landing product contract passed.
- Command/check: repository TypeScript check
  - Result: PASS for T012 - the route/component has no diagnostic; only the
    intentionally red T018 polling module remains missing.
- Rendered QA: PASS - inspected 1440x900 light, 1440x900 dark, and 375x812
  light full-page captures; all sections preserve hierarchy and reading order.
- Responsive QA: PASS - automated document-width checks reported zero
  horizontal overflow for all three captures; mobile actions remain at least
  44px and publication sheets become one ordered column.
- UI product-surface check: PASS - required four headings and access action
  render; route owner, shell/runtime, provider detail, paths, and overclaimed
  retention/compliance copy are absent.
- UI craft check: PASS - one strong display identity, restrained source-sheet
  motif, consistent publication keylines, coherent theme parity, deliberate
  whitespace, and a transformed mobile sequence.

**BQC Fixes**:

- Accessible naming: the source/publication figure uses a real `figcaption`,
  and the repeated closing CTA has a distinct accessible name.
- Contract truth: copy says provider handling follows configured services
  rather than promising deletion or a retention schedule the product does not
  yet define.

---

## Checkpoint 2 - Public Foundation

- Tasks complete: 12 / 25.
- Public root, strict intake/domain foundations, deterministic browser server,
  and both-theme research-atelier direction are in place.
- Next task: T013, authenticated route/navigation and safe draft handoff.

---

### Task T013 - Restructure authenticated navigation around `/create`

**Started**: 2026-07-20 04:29
**Completed**: 2026-07-20 04:35
**Duration**: 6 minutes

**Notes**:

- Added the stable protected `/create` route beneath the existing layout
  current-user guard. Direct entry therefore validates the stored token before
  rendering the studio or starting any future child query.
- Moved successful login and all already-authenticated auth-route redirects to
  `/create`. A valid session-only prompt remains untouched through login and
  gets a quiet handoff notice; T014 consumes it into the intake form.
- Replaced the retired root sidebar item with `Create course`, kept setup and
  admin links superuser-only, and made the creation item active on private job
  routes. The command strip now derives a safe `Course progress` label for
  dynamic job identifiers.
- Added a fail-closed account-access state when public signup visibility is
  absent/false, plus copy explaining authoritative server rejection if access
  is revoked after the visible signup form loads.
- Cleared inherited browser auth state from the genuinely public root in the
  public story. This avoids deliberately entering the protected layout and
  racing a current-user query merely to sign out test state.

**Files Changed**:

- `frontend/src/routes/_layout/create.tsx` - stable protected intake route and
  temporary T014 workbench mounting surface.
- `frontend/src/routes/_layout.tsx` - creation/progress command-strip labels
  under the unchanged current-user validation boundary.
- `frontend/src/routes/login.tsx`, `frontend/src/routes/signup.tsx`,
  `frontend/src/routes/recover-password.tsx`,
  `frontend/src/routes/reset-password.tsx` - final auth destinations,
  configured-access fallback, and draft-preserving guidance.
- `frontend/src/hooks/useAuth.ts` - successful login destination.
- `frontend/src/components/Sidebar/AppSidebar.tsx`,
  `frontend/src/components/Sidebar/Main.tsx` - protected creation navigation,
  dynamic-job active state, and unchanged operator permissions.
- `frontend/src/routeTree.gen.ts` - regenerated by the Vite router plugin.
- `frontend/tests/course-journey.spec.ts` - race-free public-state reset.

**Verification**:

- Command/check: targeted Biome over all route, auth, sidebar, and journey
  files
  - Result: PASS - no formatting, import, accessibility, or lint findings.
- Command/check: direct Vite production build
  - Result: PASS - router discovery registered `/create`; 2,188 modules
    transformed and production assets emitted.
- Command/check: repository TypeScript check
  - Result: PASS for T013 - all new route/navigation types resolve; the only
    diagnostic is the intentionally red T018 missing polling module.
- Command/check: isolated public Playwright story with real signup/login setup
  - Result: PASS - 2 tests passed; no application console error after the
    same-origin public-state reset.
- UI product-surface check: PASS - protected navigation uses learner-facing
  creation/progress labels, configured access remains truthful, and no job
  identifier is echoed into the command strip.
- UI craft check: PASS - `/create` preserves the research-atelier typography,
  semantic workbench surface, 44px mobile sidebar trigger, theme tokens, and
  deliberately restrained transitional hierarchy before T014.

**BQC Fixes**:

- Authorization order: a child course/job page cannot start its own query
  before the parent layout confirms the current user.
- Recovery completeness: login, signup, recover-password, and reset-password
  all send an already authenticated learner to the same protected studio
  rather than the public story.

---

## Checkpoint

**Next task**: T014 - build the multimode accessible intake workbench.

---

### Task T014 - Build the multimode accessible intake workbench

**Started**: 2026-07-20 04:35
**Completed**: 2026-07-20 04:45
**Duration**: 10 minutes (shared T014-T016 implementation)

**Notes**:

- Extended the product-flow contract before implementation with mode-clearing,
  local-preview, goal-focus, and reset assertions.
- Added a five-mode Radix tab control with arrow-key semantics, visible
  selected/disabled states, source-specific labels and bounds, transformed
  two-column mobile layout, and one protected workbench mounting point.
- Explicitly unregisters the prior text/file control on mode change, clears
  its DOM file selection, and mounts a fresh active control. A same-mode reset
  remains reusable, so learners can clear and replace a source.
- Consumes a valid session-only prompt only after protected mount. Strict Mode
  re-entry is safe because a second effect pass sees no draft and does not
  overwrite the restored value.

**Files Changed**:

- `frontend/src/components/CourseIntake/InputModeField.tsx` - accessible
  multimode source selector.
- `frontend/src/components/CourseIntake/CourseIntakeForm.tsx` - strict RHF/Zod
  form lifecycle, source controls, re-entry, reset, and workbench layout.
- `frontend/src/routes/_layout/create.tsx` - protected form composition.
- `frontend/tests/course-journey.spec.ts` - tests-first source switching and
  workbench behavior.

**Verification**:

- Command/check: focused isolated Playwright source, keyboard, upload, and
  mobile stories
  - Result: PASS - real auth setup plus four workbench stories passed.
- Command/check: targeted Biome, schema/draft Vitest, and direct Vite build
  - Result: PASS - 18 assertions passed; 2,193 modules transformed.
- UI product-surface check: PASS - every mode uses learner-facing labels and
  exact server-aligned guidance; no provider/model or implementation control
  appears.
- UI craft check: PASS - mode keylines, semantic workbench surface, editorial
  hierarchy, selected state, and mobile transformation match the documented
  research-atelier direction.

**BQC Fixes**:

- Runtime lifecycle: removed global RHF `shouldUnregister` after rendered QA
  proved it also removed non-visual defaults; source-only unregistering keeps
  `inputMode` and `language` stable.
- Responsive composition: the final source tab spans the otherwise empty last
  mobile/tablet grid cell and returns to one column in the five-column desktop
  selector.

---

### Task T015 - Implement learning-intent and goal controls

**Started**: 2026-07-20 04:36
**Completed**: 2026-07-20 04:45
**Duration**: included in the shared T014-T016 slice

**Notes**:

- Added automatic/reviewed learning levels, bounded optional audience and
  prior knowledge, privacy-minimized native age radios, and an exact boolean
  consent control with truthful configured-service copy.
- Implemented zero-to-ten primitive learning goals with exact labels, per-field
  messages, case-insensitive duplicate validation from the centralized
  schema, an explicit group alert, and a live count.
- Adding a goal focuses its new input; removing a goal focuses the preceding
  surviving input. The one-goal remove action safely clears and returns focus
  instead of leaving the form with an unreachable empty array.

**Files Changed**:

- `frontend/src/components/CourseIntake/LearningIntentFields.tsx` - intent,
  age, goal, consent, error, and focus behavior.
- `frontend/src/components/CourseIntake/CourseIntakeForm.tsx` - shared form and
  pending-state integration.
- `frontend/tests/course-journey.spec.ts` - tests-first goal focus contract.

**Verification**:

- Command/check: isolated keyboard-focus journey
  - Result: PASS - new goal receives focus, removal returns focus, and consent
    begins unchecked.
- Command/check: centralized job schema tests
  - Result: PASS - exact consent, ten-goal maximum, and normalized duplicate
    rejection remain green.
- UI product-surface check: PASS - no inert language, provider, model, or
  retention control was introduced.
- UI craft check: PASS - optional context remains visually quieter than the
  required source/consent path, while selected age state has both native
  control state and a semantic border/surface cue.

**BQC Fixes**:

- Accessible naming: shortened remove-button names to `Remove goal N` so
  Playwright and assistive-technology label lookup cannot confuse them with
  the `Learning goal N` textboxes.
- Exact booleans: Radix checkbox state is normalized with `checked === true`
  before entering the form contract.

---

### Task T016 - Implement bounded local source and file preview

**Started**: 2026-07-20 04:36
**Completed**: 2026-07-20 04:45
**Duration**: included in the shared T014-T016 slice

**Notes**:

- Added an explicitly named source-preview region with empty, text, URL,
  YouTube, and document metadata states.
- Text rendering is whitespace-preserving, long-token safe, scroll-bounded,
  and capped at 720 displayed characters while the complete validated value
  remains in RHF state.
- Upload preview shows only the browser-provided file name, declared MIME
  type, and formatted bytes. It never reads file bytes, parses documents, or
  creates an object URL, so there is no preview URL lifecycle to leak.

**Files Changed**:

- `frontend/src/components/CourseIntake/SourcePreview.tsx` - bounded text/URL
  and metadata-only document preview.
- `frontend/src/components/CourseIntake/CourseIntakeForm.tsx` - preview state,
  replace/reset behavior, and file-input cleanup.
- `frontend/tests/course-journey.spec.ts` - product-facing preview and
  no-content-leak assertions.

**Verification**:

- Command/check: isolated upload and source-switch Playwright stories
  - Result: PASS - file name and MIME render, raw PDF fixture bytes do not,
    reset clears the native input, and inactive text control is absent.
- Rendered QA: PASS - inspected 1440x900 light/dark and 375x812 light
  full-page captures; mobile has zero document overflow.
- Console QA: PASS - the capture journey asserted no application console
  errors after protected re-entry and theme/viewport changes.
- UI product-surface check: PASS - preview language states exactly what is and
  is not inspected locally without promising backend retention behavior.
- UI craft check: PASS - preview is a secondary keylined reading area rather
  than a competing card, and long content cannot widen the workbench.

**BQC Fixes**:

- Replacement safety: same-mode reset no longer unregisters its still-mounted
  controller, so a learner can select a replacement after clearing.
- Visual QA timing: capture checks wait for the lazy protected route after
  each theme reload, preventing a load-event-only blank capture.

---

## Checkpoint 3 - Intake Workbench

- Tasks complete: 16 / 25.
- Source selection, learner intent, consent, draft re-entry, and bounded
  previews are complete across both themes and mobile/desktop.
- The submit action is intentionally disabled until T017 connects the
  generated client and idempotency lifecycle.
- Next task: T017, durable JSON/multipart submission.

---

### Task T017 - Implement durable generated-client submission

**Started**: 2026-07-20 04:46
**Completed**: 2026-07-20 04:51
**Duration**: 5 minutes

**Notes**:

- Added failing coordinator tests before implementation for exact generated
  JSON delegation, multipart file/metadata delegation, synchronous
  single-flight behavior, failed exact retry, rotation after success/change,
  and safe error copy.
- Implemented one in-memory coordinator per mounted intake route. It keeps a
  stable key for a failed exact canonical request, rotates when input changes
  or a durable acceptance succeeds, and shares the same Promise when a
  duplicate trigger arrives in flight.
- Uses a secure browser UUID wrapped in the reviewed idempotency grammar.
  Canonical JSON is bounded by the existing form limits and never enters
  storage/logs; upload bytes are not read and selected file identity lives in
  a WeakMap.
- Calls only generated `JobsService.submitJob` and
  `JobsService.submitJobUpload`. It passes exactly one JSON body or one
  generated multipart body and navigates from the backend-validated
  `job_id`, ignoring the returned URL as navigation input.
- Added the stable private dynamic job route boundary needed for typed
  navigation. It deliberately performs no hand-written fetch; T018/T019 own
  polling and the complete stage rail.

**Files Changed**:

- `frontend/src/hooks/useCourseSubmission.test.tsx` - tests-first transport,
  key lifecycle, duplicate, upload, and safe-error contracts.
- `frontend/src/hooks/useCourseSubmission.ts` - generated-client transport,
  canonical retry coordinator, mutation, safe Problem Details, and accepted-ID
  navigation.
- `frontend/src/components/CourseIntake/CourseIntakeForm.tsx` - pending lock
  and accessible inline server error.
- `frontend/src/routes/_layout/create.tsx` - mutation composition.
- `frontend/src/routes/_layout/jobs.$jobId.tsx` - query-free dynamic route
  boundary for the next two tasks.
- `frontend/src/routeTree.gen.ts` - regenerated by the Vite router plugin.

**Verification**:

- Command/check: initial focused Vitest run
  - Result: PASS (tests-first gate) - collection failed only because
    `useCourseSubmission.ts` did not exist.
- Command/check: submission plus centralized schema Vitest
  - Result: PASS - 16 assertions passed.
- Command/check: direct Vite production build
  - Result: PASS - `/jobs/$jobId` registered, 2,198 modules transformed, and
    generated-client calls bundled without route/type casts.
- Command/check: repository TypeScript check
  - Result: PASS for T017 - the only remaining diagnostic is the intentionally
    red T018 missing polling module.
- Isolated journey segment: PASS for T017 - the real double-click produced one
  backend `202`, one durable job, the accepted opaque job route, and the
  `Building your learning package` heading. The existing story then stopped
  only at its intentionally unimplemented T019 progress-copy assertion.
- UI product-surface check: PASS - errors expose only bounded reviewed Problem
  Details or a fixed recovery message; no request key, raw exception, status
  URL, provider, or source content is shown.
- UI craft check: PASS - pending state disables every mutable form control,
  keeps the action label stable, and places recovery copy next to the action
  without adding a competing panel.

**BQC Fixes**:

- Event-race closure: the coordinator's synchronous in-flight flag supplements
  TanStack `isPending`, closing the render gap exercised by Playwright
  `dblclick`.
- File privacy: exact upload retry identity uses File object identity and
  metadata; it never hashes or parses document bytes in the browser.

---

## Checkpoint

**Next task**: T018 - implement revision-aware generated-client polling.

---

### Task T018 - Implement revision-aware generated-client polling

**Started**: 2026-07-20 04:51
**Completed**: 2026-07-20 04:55
**Duration**: 4 minutes

**Notes**:

- Completed the tests-first policy contract with revision regression,
  cross-job protection, transient/non-transient classification, direct
  re-entry, and visibility-listener cleanup coverage.
- Added one owner-job-scoped query key and a generated
  `JobsService.readJob` query. No route or component hand-writes HTTP.
- Enumerated all nine generated job statuses. Six active states poll at 1.5
  seconds when visible and 10 seconds when hidden; completed, failed, and
  cancelled stop immediately.
- Transient connectivity/server failures use exponential delays from 1.5
  seconds through a 30-second cap. Ownership, authentication, and validation
  failures do not retry. TanStack retains the last safe snapshot while a
  background read reconnects.
- Structural sharing rejects lower/equal revisions and cross-job snapshots,
  preventing visual regression. Mount, reconnect, focus, and visible re-entry
  all revalidate; the explicit visibility listener returns exact cleanup while
  TanStack owns interval cleanup.

**Files Changed**:

- `frontend/src/components/CourseProgress/queries.test.ts` - exhaustive
  status, interval, retry, revision, re-entry, and cleanup assertions.
- `frontend/src/components/CourseProgress/queries.ts` - generated query
  options, finite polling/backoff policy, snapshot guard, visibility adapter,
  and progress hook.

**Verification**:

- Command/check: focused polling Vitest
  - Result: PASS - 15 assertions passed.
- Command/check: full frontend TypeScript check
  - Result: PASS - the last intentionally red missing module is implemented;
    the repository frontend typecheck is now clean.
- Command/check: normal `npm run build`
  - Result: PASS - TypeScript and Vite both passed; 2,198 modules transformed.
- UI product-surface check: PASS (state foundation) - only generated
  allowlisted status/progress data reaches the future view, and read errors
  cannot expose a different owner's existence through retry behavior.
- UI craft check: PASS (state foundation) - snapshot regression is prevented,
  hidden tabs are intentionally quieter, and terminal views cannot keep
  visibly churning.

**BQC Fixes**:

- Exhaustiveness: a future generated status breaks the `never` branch until
  its terminal/polling decision is reviewed.
- React lifecycle: memoized the per-job query key so the visibility effect
  does not unsubscribe/resubscribe on ordinary renders.
- TanStack typing: isolated its intentionally `unknown` structural-sharing
  callback boundary and immediately narrowed to the generated query type.

---

## Checkpoint

**Next task**: T019 - build the full progress stage rail and route states.

---

### Task T019 - Build the complete progress stage rail and route states

**Started**: 2026-07-20 04:55
**Completed**: 2026-07-20 05:06
**Duration**: 11 minutes

**Notes**:

- Added failing pure presentation tests before implementation for every
  generated active/terminal state, known/unknown units, completed rail, and
  terminal no-invention behavior.
- Built a seven-stage vertical rail directly from the public progress-stage
  allowlist. Active, completed, upcoming, and terminal-neutral states combine
  text, native semantics, and icons; no private checkpoint is inferred when a
  failure response intentionally omits where execution stopped.
- Added deliberate initial loading, offline, reconnecting-with-last-snapshot,
  retry, completed summary, failed/cancelled recovery, invalid-route, and
  refresh-safe unexpected-error states. Progress units never invent a
  percentage when the total is unknown.
- Added a persistent, truncated opaque job reference with a copy action and
  live result announcement. Its reset timer, elapsed-time interval, query
  timer, online subscription, and visibility listener all clean up.
- Completed results remain on the same durable URL and hand off a small
  server-result summary; Session 02 expands that exact location into the four
  publication workspace.
- Added a real second-owner browser regression. Existing foreign and missing
  jobs render byte-for-byte-equivalent recovery copy and neither echoes the
  requested identifier.

**Files Changed**:

- `frontend/src/components/CourseProgress/presentation.test.ts` - tests-first
  generated status/stage and unit-label contract.
- `frontend/src/components/CourseProgress/presentation.ts` - exhaustive
  learner-facing stage and terminal mapping.
- `frontend/src/components/CourseProgress/CourseProgressPage.tsx` - loading,
  stage rail, progress, elapsed time, connection, terminal, handoff, copy,
  recovery, and error compositions.
- `frontend/src/routes/_layout/jobs.$jobId.tsx` - validated route parameter,
  private progress composition, and safe route error boundary.
- `frontend/src/lib/schemas/job.ts`,
  `frontend/src/lib/schemas/job.test.ts` - corrected the backend-aligned
  optional-goal contract exposed by the failed-terminal browser story.
- `frontend/tests/course-journey.spec.ts` - fast-completion-safe refresh
  assertion and real foreign/missing privacy regression.

**Verification**:

- Command/check: progress presentation, polling, schema, and submission Vitest
  suites
  - Result: PASS - 42 assertions passed.
- Command/check: full TypeScript and production build
  - Result: PASS - 2,202 modules transformed and the lazy progress composition
    emitted as its own route chunk.
- Isolated complete journey: PASS - one real double-click submission, accepted
  job navigation, completed polling, and direct full-page refresh passed.
- Isolated failed journey: PASS - generated safe failure heading, retry path,
  and traceback/provider/filesystem absence passed.
- Isolated owner privacy journey: PASS - a real foreign-owned completed job
  and a missing job produced the same not-available heading and copy.
- Rendered QA: PASS - inspected completed 1440x900 light/dark and 375x812
  light full-page captures; mobile reported zero document overflow and the
  capture asserted zero application console errors.
- UI product-surface check: PASS - server message/failure/result allowlists are
  the only dynamic copy; no raw exception, private checkpoint, provider,
  filesystem path, or source body appears.
- UI craft check: PASS - a precise editorial rail, one dominant status
  workbench, restrained terminal handoff, theme parity, persistent job
  reference, and transformed mobile reading order match the research atelier.

**BQC Fixes**:

- Optional intent correctness: an untouched initial goal row now serializes to
  `learning_goals: []`; nonblank values still receive exact min/max and
  case-insensitive duplicate validation.
- Online store lifecycle: wrapped TanStack `onlineManager` methods to preserve
  their instance binding before subscribing through `useSyncExternalStore`.
- Fast deterministic completion: the browser assertion accepts either the
  active or already-completed h1, then requires the server status h2 after
  refresh.
- Accessible uniqueness: the refresh assertion targets the level-two server
  update, avoiding ambiguity with the completed page title.

---

## Checkpoint 4 - Durable Learner Journey

- Tasks complete: 19 / 25.
- Public landing through authenticated intake, one durable submission, direct
  progress refresh, completed handoff, failure recovery, and owner privacy are
  implemented.
- Next task: T020, regenerate routes and update the broader browser regression
  suite for the new public/protected map.

---

### Task T020 - Regenerate routes and align browser navigation contracts

**Started**: 2026-07-20 05:07
**Completed**: 2026-07-20 05:15
**Duration**: 8 minutes

**Notes**:

- Regenerated the TanStack route tree through the Vite router plugin. The
  generated graph now owns public `/`, protected `/create`, and protected
  `/jobs/$jobId`; the donor `/items` route is absent and no generated output
  was hand-edited.
- Reframed the former dashboard browser story around the public
  source-to-four-publications landing page, authenticated creation handoff,
  mobile target/overflow checks, reduced motion, and the intentional retired
  route recovery surface.
- Updated shared authentication setup, login assertions, and login helpers to
  use `/create` as the final protected route. The setup validates the actual
  current-user guard before persisting its localStorage migration seed.
- Made login assertions follow the active test environment's credentials:
  Compose continues to use the configured operator while the isolated suite
  uses its freshly created normal user.
- Updated forbidden and not-found actions to typed routes and current product
  copy instead of donor-dashboard language.

**Files Changed**:

- `frontend/src/routeTree.gen.ts` - plugin-generated public, create, and
  dynamic job route graph.
- `frontend/tests/dashboard.spec.ts` - public landing, `/create` handoff,
  retired `/items`, mobile, and reduced-motion assertions.
- `frontend/tests/login.spec.ts` - `/create` destination and
  environment-owned credentials.
- `frontend/tests/auth.setup.ts`, `frontend/tests/utils/user.ts` - protected
  destination, current-user guard, and session-storage migration setup.
- `frontend/src/components/Common/NotFound.tsx`,
  `frontend/src/routes/_layout/forbidden.tsx` - typed product navigation and
  current recovery copy.

**Verification**:

- Command/check: targeted Biome write/check
  - Result: PASS - all six route/auth files formatted and lint-clean.
- Command/check: direct Vite production build
  - Result: PASS - 2,202 modules transformed and the new route chunks emitted.
- Command/check: stale donor-route and destination search
  - Result: PASS - only the deliberate `/items` not-found assertion remains.
- Browser regression subset: PASS - auth setup plus 13 dashboard/login
  assertions passed against a fresh isolated user and real backend auth.
- UI product-surface check: PASS - navigation names the actual course journey;
  missing and denied routes expose no object or owner detail.
- UI craft check: PASS - 44-pixel mobile action, zero horizontal overflow,
  and reduced-motion creation handoff remain explicitly covered.

**BQC Fixes**:

- Test-environment ownership: removed the hidden assumption that every browser
  run uses the Compose superuser.
- Origin accuracy: the verification backend used the exact temporary frontend
  origin so the real CSRF dependency, not a bypass, accepted valid login.

---

## Checkpoint 5 - Complete Application Route Map

- Tasks complete: 20 / 25.
- Public and protected route ownership, authentication handoff, dynamic job
  re-entry, and retired donor-route recovery are regression-covered.
- Next task: T021, update frontend/operator documentation and examples.

---

### Task T021 - Update learner-journey documentation and examples

**Started**: 2026-07-20 05:15
**Completed**: 2026-07-20 05:20
**Duration**: 5 minutes

**Notes**:

- Updated the frontend route catalog and onboarding sequence for public `/`,
  authenticated `/create`, owner-scoped `/jobs/$jobId`, configured signup,
  and the Session 02 result expansion.
- Documented that `VITE_ENABLE_PUBLIC_SIGNUP` is public build-time display
  configuration while backend `ENABLE_PUBLIC_SIGNUP` remains authoritative.
- Recorded the five intake modes, strict shared schema, inactive-field
  removal, consent boundary, local bounded preview, canonical submission
  coordinator, and durable direct/refresh progress behavior.
- Added complete and failed deterministic Playwright commands and explained
  the finite test-only composition, normal route/auth/worker coverage, and
  fail-closed enable flag.
- Reworked coding-agent guidance and curated examples to compose
  `useCourseSubmission` and `useJobProgressQuery`. They no longer teach a
  second idempotency or polling implementation.
- Added explicit guardrails against turning browser storage choices into
  unsupported server-retention, provider-policy, regulatory-compliance, or
  privacy guarantees.

**Files Changed**:

- `frontend/README_frontend.md` - current routes, access, intake/progress
  ownership, generated files, and deterministic browser commands.
- `frontend/AGENTS.md` - current learner boundaries, schema/components,
  composition examples, signup semantics, and test guidance.
- `docs/onboarding.md` - operator access setup, learner URLs, deterministic
  tests, generated route ownership, and retention-claim warning.
- `docs/dashboard-design.md` - current page identity and rendered-QA coverage.
- `examples/frontend/hooks/use_mutation_with_toast.ts` - canonical submission
  composition example.
- `examples/frontend/hooks/use_query_with_suspense.ts` - reviewed progress
  query composition example.

**Verification**:

- Command/check: stale Phase 04 and authenticated-root language search
  - Result: PASS - no obsolete implementation-coming or donor-root guidance
    remains in the edited documentation.
- Command/check: required access/test/ownership/retention term search
  - Result: PASS - each operational contract is present at its intended
    developer or operator surface.
- Command/check: Biome over both TypeScript examples
  - Result: PASS - both examples are formatting and lint clean.
- Command/check: targeted `git diff --check`
  - Result: PASS - no whitespace errors.
- UI product-surface check: PASS (documentation) - examples and copy expose
  only generated public contracts and reviewed product concepts.
- UI craft check: PASS (documentation) - the design source of truth now names
  the actual public/intake/progress surfaces and complete QA matrix.

---

## Checkpoint 6 - Current Operator and Developer Handoff

- Tasks complete: 21 / 25.
- Route, access, lifecycle, generated ownership, test, and product-claim
  documentation match the implemented learner journey.
- Next task: T022, run backend browser, acceptance, route, and static gates.

---

### Task T022 - Run backend lifecycle, route, lint, and type gates

**Started**: 2026-07-20 05:20
**Completed**: 2026-07-20 05:21
**Duration**: 1 minute

**Verification**:

- Command/check: browser fixture, Phase 03 acceptance, submission route, and
  result route Pytest selection
  - Result: PASS - 50 tests passed with no failures.
- Command/check: Ruff lint and format check over `app`, browser/support,
  acceptance support, and job route tests
  - Result: PASS - all checks passed; 55 files already formatted.
- Command/check: strict mypy over `app`
  - Result: PASS - no issues in 47 source files.
- Command/check: ty over `app`
  - Result: PASS - all checks passed.
- Lifecycle/privacy review: PASS - test-only enablement, production route
  isolation, durable reopen, cross-owner equivalence, reverse cleanup,
  submission privacy headers, verified artifact streaming, and response
  construction cleanup all passed their executable contracts.

**Warnings Reviewed**:

- The focused run reported only the checkout's known short local JWT-key
  warnings and one upstream HTTPX raw-upload deprecation warning. No learner
  source, credential, provider detail, or filesystem location was emitted by
  application assertions.

---

## Checkpoint 7 - Backend Boundary Verified

- Tasks complete: 22 / 25.
- Deterministic browser composition, Phase 03 durability/recovery, job HTTP
  boundaries, formatting, lint, and strict types are green.
- Next task: T023, run complete frontend static, unit, generation, and build
  gates with generated-contract drift checks.

---

### Task T023 - Run frontend unit, static, generation, and build gates

**Started**: 2026-07-20 05:21
**Completed**: 2026-07-20 05:23
**Duration**: 2 minutes

**Verification**:

- Command/check: root `scripts/generate-client.sh`
  - Result: PASS - OpenAPI export and all generated-client files reproduced
    byte-for-byte with no tracked diff.
- Command/check: full frontend Vitest suite
  - Result: PASS - 90 tests passed across 14 files.
- Command/check: full Biome write/check
  - Result: PASS - 140 files checked; two mechanical formatting fixes applied.
- Command/check: TypeScript build configuration with no emit
  - Result: PASS - no diagnostics.
- Command/check: production TypeScript and Vite build
  - Result: PASS - 2,202 modules transformed; public, create, and lazy dynamic
    progress chunks emitted.
- Command/check: generated-client and OpenAPI post-build diff
  - Result: PASS - no generated contract drift.
- Command/check: frontend diff whitespace audit
  - Result: PASS - no whitespace errors.
- Exhaustiveness review: PASS - generated status additions remain forced
  through the polling and presentation `never` branches, while route IDs and
  accepted submission identities remain branded at their trust boundaries.

---

## Checkpoint 8 - Frontend Contracts Verified

- Tasks complete: 23 / 25.
- All frontend unit, lint, type, generated-contract, route-generation, and
  production-build gates are green.
- Next task: T024, run isolated and full browser regressions plus the complete
  rendered-accessibility matrix.

---

### Task T024 - Run browser regressions and rendered acceptance matrix

**Started**: 2026-07-20 05:23
**Completed**: 2026-07-20 05:35
**Duration**: 12 minutes

**Notes**:

- Ran both finite deterministic scenarios through the isolated
  Playwright-owned backend and Vite processes. The completion story and its
  direct refresh remained owned by the complete scenario; the failed scenario
  now skips that completion-only story and exclusively verifies its terminal
  recovery contract.
- Built the production Compose images and exercised the broad browser suite
  against a clean, separately named Phase 04 service project. Its database,
  backend, frontend, mail service, ports, networks, and volumes were isolated
  from every pre-existing user container.
- Used the production frontend image with the deterministic backend facade for
  the complete broad regression, so browser state remained finite while Nginx,
  the built assets, normal authentication, PostgreSQL, and the ordinary shell
  routes stayed under test.
- Rendered the public and intake surfaces at 1440x900 and 375x812 in light and
  dark themes, plus a 720x450 viewport representing the layout dimensions at
  200% zoom. Long unbroken source, audience, and goal values reflow without
  document overflow.
- Verified keyboard tab selection, focus visibility, 44-pixel mobile actions,
  reduced-motion behavior, bounded layout shift below 0.1, and zero
  application console, page, or failed-request errors.
- Production QA exposed a real content-security-policy mismatch: `index.html`
  requested Google Fonts while the Nginx policy correctly blocked external
  styles. Removed the external requests, changed the documented display/body/
  mono typography stacks to deliberate local and system faces, rebuilt the
  image, and repeated the rendered checks with zero errors.
- Removed the temporary rendered-QA spec and Compose override, destroyed only
  the `txt2crs-phase04` project and its volumes, and confirmed the retained
  `txt2crs-phase03-db` plus all `python-react-boilerplate-*` user containers
  remained running.

**Files Changed**:

- `frontend/tests/course-journey.spec.ts` - made completion-only refresh
  ownership explicit for the finite failed scenario.
- `frontend/index.html` - removed CSP-incompatible external font requests.
- `frontend/src/index.css` - selected local/system typography stacks.
- `docs/dashboard-design.md` - synchronized the production typography
  contract.

**Verification**:

- Isolated complete scenario: PASS - 8 passed and 1 setup project skipped.
- Isolated failed scenario: PASS - 8 passed and 1 setup project skipped.
- Full production browser regression: PASS - 66 passed and 7 intentionally
  skipped tests.
- Production Compose build: PASS - backend and frontend images built from the
  current source.
- Temporary rendered matrix: PASS - three QA stories covering both themes,
  desktop/mobile/200%-layout viewports, long content, keyboard operation,
  touch targets, layout shift, request failures, console errors, and overflow.
- Post-font-fix frontend regression: PASS - Biome checked 140 files, TypeScript
  reported no diagnostics, 90 Vitest assertions passed, and the production
  Vite build completed.
- Visual inspection: PASS - landing light/dark desktop and mobile, intake long
  content at the 200%-layout viewport, and the previously captured
  intake/progress light/dark desktop/mobile states preserve hierarchy,
  readable rhythm, and action priority.

**BQC Fixes**:

- Scenario determinism: the failed facade no longer races a completion-only
  browser story before its own terminal assertion.
- Production asset policy: local typography now matches the existing
  restrictive CSP instead of depending on a silently blocked remote request.
- Environment isolation: temporary services used project-scoped names and
  non-conflicting ports, then underwent explicit volume/network cleanup.

---

## Checkpoint 9 - Rendered Learner Journey Accepted

- Tasks complete: 24 / 25.
- The public-to-terminal journey is green in isolated finite scenarios and the
  broad production browser suite, with responsive, theme, keyboard, motion,
  zoom, overflow, network, console, and layout-shift evidence.
- Next task: T025, run repository-wide hooks, hygiene/security searches, and
  complete cross-package regression gates.

---

### Task T025 - Run repository-wide regression and hygiene gates

**Started**: 2026-07-20 05:35
**Completed**: 2026-07-20 05:40
**Duration**: 5 minutes

**Notes**:

- Ran the complete configured pre-commit chain over all existing tracked files
  plus every explicit untracked file, so new session modules were not omitted
  by Git's index state.
- Ran the full application-shell, reusable engine, and frontend unit/static/
  production-build gates from their owning package roots.
- Audited active-session changed and new text for ASCII/LF, changed/new files
  for common high-confidence credential shapes, primary learner surfaces for
  private diagnostic vocabulary, and the draft/submission boundary for URL or
  local-storage writes.
- The encoding audit found four visible middle dots in new JSX and one
  ellipsis in edited frontend guidance. Replaced source characters with ASCII
  Unicode escapes or punctuation, preserving rendered product copy while
  satisfying repository source rules.
- Confirmed the generated OpenAPI/client tree has no diff, no temporary Phase
  04 Compose or rendered-QA fixture remains, and `git diff --check` is clean.
- `docs/ongoing-projects/TODO.md` contains no actionable item, so there was no
  completed TODO entry to move. Added the shipped Session 01 learner journey,
  deterministic browser composition, route/CSP changes, and privacy controls
  to the current Unreleased changelog; it remains below the archive threshold.

**Verification**:

- Repository hooks: PASS - large-file, case, TOML, YAML, EOF, whitespace,
  typos, Ruff, Ruff format, backend mypy/ty, frontend Biome/TypeScript,
  generated client, and Zizmor hooks all passed.
- Backend shell: PASS - 478 tests passed; Ruff and format passed over 58
  focused source/test files; mypy passed 47 source files; ty passed.
- Reusable engine: PASS - 470 tests passed and the explicit credentialed live
  Codex acceptance remained skipped; Ruff/format and mypy passed all 138
  source files.
- Frontend: PASS - 90 Vitest assertions passed; Biome, TypeScript, and the
  2,202-module production build passed after final source normalization.
- Hygiene: PASS - active-session text is ASCII/LF, changed/new files contain
  no reviewed high-confidence secret shape, primary product routes contain no
  private diagnostic vocabulary or disallowed storage path, generated output
  is unchanged, and the diff has no whitespace errors.

**Warnings Reviewed**:

- Backend tests retain the known local short-JWT-key warning and one upstream
  HTTPX raw-upload deprecation warning. Neither is introduced by the learner
  journey or exposes source, credential, provider, or private-path data.
- The engine's only skip is the intentionally opt-in live subscription
  acceptance requiring `TXT2CRS_RUN_LIVE_CODEX=1`.

**BQC Fixes**:

- Explicit-new-file coverage: hook invocation includes untracked session
  modules rather than relying on an already staged index.
- Source normalization: product punctuation remains visually correct while
  all active-session source and documentation use repository-safe ASCII/LF.
- Change accounting: current public/intake/progress behavior and security
  boundaries are recorded under Unreleased without claiming a new release.

---

## Session Implementation Complete

- Tasks complete: 25 / 25.
- Tests-first implementation, broad browser acceptance, rendered QA, static
  analysis, full regressions, hooks, and hygiene checks are green.
- No blocker, temporary test service, or unreviewed generated-client change
  remains.
- Ready for the `creview` step in the required
  `implement -> creview -> validate` sequence.

---

## Creview Repair Pass

**Started**: 2026-07-20 05:40
**Completed**: 2026-07-20 06:14
**Duration**: 34 minutes

### Review Findings Repaired

- Added the missing public topic producer for the existing bounded
  session-storage handoff, then proved public -> login -> `/create` restores
  the topic once and consumes it on direct refresh.
- Rendered bounded extraction notes and the truncation signal on the owner
  progress page. Duplicate notes now receive stable response-order keys, and
  truncation copy says omitted notes are omitted rather than claiming they are
  available elsewhere.
- Changed the deterministic browser harness from a shared `/tmp/browser-worker`
  sibling into one private run root containing `state`, `browser-worker`, and
  auth state. The test application refuses pre-existing or symlink-parent
  state paths instead of chmodding caller-owned directories.
- Added a Playwright teardown project that deletes the fresh normal learner
  through the real account-purge route. Foreign-owner test setup also deletes
  its account in `finally`, so PostgreSQL and engine state are clean after
  assertion failures.
- Covered all seven P0 input families at the generated-client browser boundary,
  plus warning, cancellation, reconnecting, and resource cleanup behavior.
- Repaired a 320px public-handoff overflow caused by the primary button's
  non-wrapping minimum width. The maximum-length draft case now has a dedicated
  browser regression.
- Synchronized the design guide with the implemented local typography,
  tab-scoped topic handoff, first-invalid-field focus, and current-update
  composition.

### Tests-First Evidence

- Backend state ownership regression before repair: expected failure, one
  failed and four passed because an existing state directory was accepted and
  chmodded.
- Progress warning presentation before repair: expected TypeError because no
  warning presentation function existed.
- Public handoff, teardown, and input-family browser assertions were added
  before their respective implementation/fixture repairs.
- Minimum-width browser regression before repair: expected failure with
  51 pixels of document-level horizontal overflow at 320px.
- Minimum-width browser regression after repair: three tests passed, including
  setup and teardown, with zero overflow.

### Final Verification

- Backend shell: PASS - 479 tests passed with only the known local JWT-key and
  upstream HTTPX warnings; Ruff, Ruff format, mypy over 47 source files, and ty
  passed.
- Reusable engine: PASS - 470 tests passed and the explicit live-subscription
  acceptance remained skipped; Ruff, format, and mypy over 138 source files
  passed.
- Frontend: PASS - 97 Vitest assertions, Biome over 141 files, TypeScript,
  generated-client reproduction, and the 2,202-module production build passed.
- Isolated complete scenario: PASS - 14 passed, 1 intentionally skipped.
- Isolated failed scenario: PASS - 14 passed, 1 intentionally skipped.
- Rendered QA: PASS - desktop light/dark, 375px light/dark, 720px
  zoom-equivalent, and 320px maximum-draft layouts have zero overflow, zero
  layout shift, visible focus, 48px primary actions, no remote resources, and
  no console, page, or request failures.
- Archive provenance: PASS - all 35 Phase 02 destination files are
  byte-identical to their base-commit source.
- Security/resource audit: PASS - zero secret-pattern files, production
  test-only imports, dangerous render/eval calls, course-source local-storage
  writes, direct feature transports, debug statements, generated-contract
  drift, browser test users, temporary browser roots, or test listener
  processes.
- Repository hooks: PASS - all applicable hooks passed over every changed and
  explicit new file.
- Source hygiene: PASS - active-session text is ASCII with Unix LF, and
  `git diff --check` is clean.

---

## Validate Contrast Repair

**Started**: 2026-07-20 06:22
**Completed**: 2026-07-20 06:28
**Duration**: 6 minutes

### Finding and Tests-First Evidence

- The rendered validation audit measured light footer text at 3.06:1 and its
  separator at 1.30:1. Dark primary captions and actions measured from 4.14:1
  to 4.37:1, below the 4.5:1 normal-text requirement.
- Added a browser-side WCAG audit that parses computed OKLCH colors, composes
  ancestor surfaces, ignores screen-reader-only text, and checks every visible
  landing text node in both explicit themes.
- The focused browser test failed before the style repair with the exact light
  footer ratios, then passed after the repair.

### Repair

- Dark primary roles now use luminous forest green for text/fills and charcoal
  foreground text on primary-filled controls. Button and badge primitives use
  the same accessible dark fill instead of stale hard-coded values.
- Footer metadata now uses the full muted-foreground role, while the visual
  separator is a decorative CSS rule rather than low-contrast text.

### Verification

- Focused contrast journey: PASS - setup, light/dark computed contrast audit,
  and account teardown all passed.
- Complete isolated journey: PASS - 15 passed, 1 intentional failure-only
  skip.
- Failed isolated journey: PASS - 15 passed, 1 intentional complete-only skip.
- Frontend static/unit/build: PASS - 97 Vitest assertions, Biome over 141
  files, TypeScript, and the 2,202-module production build passed.
- Rendered inspection: PASS - updated dark full-page and light footer captures
  preserve the research-atelier hierarchy and make both primary actions and
  footer metadata visibly legible.
