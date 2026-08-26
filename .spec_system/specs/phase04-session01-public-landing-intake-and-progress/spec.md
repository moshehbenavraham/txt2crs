# Session Specification

> Historical completed-session record. Any local-only, judge, model-family, or
> signup-default statement below records the July 2026 implementation context;
> it is superseded by the current PRD, ADR-0009, and application configuration.

**Session ID**: `phase04-session01-public-landing-intake-and-progress`
**Phase**: 04 - Learner Experience
**Status**: Complete
**Created**: 2026-07-20
**Base Commit**: 08297e317683ad6cf608e4d9333bfbb819955ef7
**Package**: null
**Package Stack**: React 19, TypeScript, Vite, FastAPI, deterministic txt2crs facade

---

## 1. Session Overview

This session ships the first complete learner vertical slice: a signed-out
visitor understands the product at `/`, an authenticated learner builds a
strict request at `/create`, and the server-provided durable status URL opens a
refresh-safe progress experience. The generated jobs client, not a parallel
fetch contract, remains the frontend boundary.

It is next because Phase 03 completed durable admission, owner-private reads,
recovery, and generated contracts, while the transition audit removed the
donor library and left a truthful static four-publication overview. The only
cross-package work is a test-only deterministic FastAPI composition so
Playwright can exercise real shell, SQLite, public facade, worker, and renderer
behavior without ChatGPT, Tavily, or route-only response mocks.

Primary product surfaces are the public landing page, login access handoff,
authenticated intake, and owner job progress route. No developer diagnostic
surface is required. Test fixture controls, if needed, exist only in a
separate test application module and never enter the production route graph.

---

## 2. Objectives

1. Give signed-out visitors a product-specific landing page and route
   authenticated learners to a focused `/create` workbench.
2. Mirror every Phase 03 learner-selectable request bound in centralized Zod
   schemas and safe branded identifiers.
3. Submit prompt, text, URL, YouTube, PDF, DOCX, and PPTX inputs through the
   generated client with stable idempotency and duplicate-trigger prevention.
4. Render server-derived progress, extraction warnings, reconnecting behavior,
   and terminal states at `/jobs/$jobId` with bounded revision-aware polling.
5. Prove the journey through a credential-free deterministic browser harness,
   responsive rendered QA, keyboard use, and reduced-motion behavior.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase03-session01-durable-job-submission-and-admission` - strict JSON
      and multipart admission plus generated submission client.
- [x] `phase03-session02-owner-scoped-job-results-and-recovery` - public status,
      result, manifest, artifact, and restart behavior.
- [x] `phase03-session03-account-purge-and-donor-retirement` - coordinated
      erasure and complete donor contract removal.

### Required Tools Or Knowledge

- React Hook Form, Zod 4, TanStack Router/Query, generated `JobsService`, and
  the repository Problem Details adapter.
- FastAPI `create_app` injection seams, `DeterministicApplicationFactory`, and
  `SerialTxt2CrsWorker`.
- Playwright browser/runtime setup and the repository frontend visual-upgrade
  playbook.

### Environment Requirements

- Node.js/npm dependencies installed under `frontend/`.
- Backend uv workspace synchronized with a PostgreSQL 18 test database.
- No ChatGPT, Tavily, or external network credential is required.
- Current production Compose services remain untouched by the isolated browser
  fixture.

---

## 4. Scope

### In Scope (MVP)

- A signed-out visitor can understand the four-publication transformation at
  `/` and choose the configured sign-in or create-account path - use a public
  route outside `_layout` and product-facing copy only.
- A local judge/demo visitor sees invite-only access language when public
  signup is disabled - mirror the backend default through explicit frontend
  build configuration without exposing credentials.
- An authenticated learner can create work at `/create` - move the protected
  static overview into a focused intake route and redirect auth success there.
- A learner can preserve a safe drafted prompt across the public-to-login
  handoff when practical - retain only bounded draft text in session storage
  and clear or revalidate it on use.
- A learner can select prompt, text, URL, YouTube, PDF, DOCX, or PPTX input -
  use discriminated form state and exact backend bounds.
- A learner can provide optional audience, prior knowledge, up to ten unique
  goals, level, age group, and exact consent - expose no inert language,
  duration, tone, model, policy, or budget controls.
- A learner sees a safe local preview of text/URL or file name, media type, and
  bytes - never parse document contents in the browser.
- A learner submits through `JobsService.submitJob` or
  `JobsService.submitJobUpload` - preserve one `crypto.randomUUID()` key for an
  exact retry and rotate it only after request-shape changes or success.
- An owner can revisit `/jobs/$jobId` - validate the path identifier, call
  `JobsService.readJob`, and preserve missing/foreign 404 indistinguishability.
- A learner sees queued/researching/drafting/validating/rendering/delivering
  progress and completed/failed/cancelled outcomes - map exhaustively from the
  generated finite status and `progress` fields.
- A transient network loss becomes a reconnecting presentation - keep the last
  safe snapshot, apply 1.5-second visible polling, 10-second hidden polling,
  exponential transient backoff capped at 30 seconds, and stop at terminal
  state.
- Browser tests exercise real authenticated FastAPI routes and production
  engine persistence through an isolated deterministic application - fixture
  control is test-only, schema validated, bounded, and cleaned on scope exit.

### Out Of Scope (Deferred)

- Manifest, download menus, HTML preview, source/conflict presentation, and
  final results composition - Session 02 owns publication delivery.
- Job library, job cancellation endpoint, per-job deletion, notification
  outbox, LMS export, editing, collaboration, grading, and quiz playback -
  deferred requirements have no Phase 03 API.
- Hosted deployment, public domains, open judge signup, provider selection, or
  model/budget controls - outside the local-only P0 scope.
- New backend generation, research, validation, persistence, or rendering
  logic - the deterministic fixture composes the existing public package only.

---

## 5. Technical Approach

### Architecture

Create a public `frontend/src/routes/index.tsx` and protected
`frontend/src/routes/_layout/create.tsx` plus
`frontend/src/routes/_layout/jobs.$jobId.tsx`. The protected shell remains the
only owner of current-user validation. Login and sidebar navigation target
`/create`; the public landing never mounts protected queries.

Centralize request validation in `frontend/src/lib/schemas/job.ts` and domain
identity in `frontend/src/lib/types/branded.ts`. A feature hook under
`frontend/src/hooks/useCourseSubmission.ts` owns stable request identity and
generated-client mutation. Query options and finite polling decisions live in
`frontend/src/components/CourseProgress/queries.ts`, keeping server state out
of local route timers.

The deterministic browser server lives under `backend/tests/browser/`, not
`backend/app/`. It creates the normal FastAPI app with an injected lifecycle
over `DeterministicApplicationFactory`, the real serial worker, isolated
SQLite/artifacts, and normal authentication/PostgreSQL. Reusable deterministic
scenario builders move from acceptance `conftest.py` into a test support
module so both acceptance and browser composition exercise the same validated
course. Any test control endpoint is registered only by that test module,
requires a finite strict schema, and is unreachable from the production app.

Playwright receives a dedicated jobs configuration that starts the isolated
backend and Vite servers, seeds authenticated storage through the normal login
API, and proves real durable submission and reads. Existing Compose-driven
Playwright remains valid for the full application.

### Design Patterns

- **Research atelier**: Warm publication surfaces and editorial type establish
  trust, while restrained technical labels and a precise stage rail make
  durable state legible.
- **Source-to-publications signature**: The landing page visually transforms
  one bounded source tile into four named publications using CSS layout and
  semantic content, not decorative generated imagery.
- **Focused workbench**: `/create` prioritizes mode, source, learning intent,
  consent, and one outcome-specific action instead of a generic dashboard
  grid.
- **Server-state truth**: Generated types and exhaustive status mappings drive
  copy, polling, and route outcomes. The UI never invents provider turns,
  completion percentages, recency, or hidden review states.
- **State machine at boundaries**: Draft identity, submission mutation, polling
  cadence, visibility, reconnecting, and terminal states are explicit and
  independently testable.
- **Progressive disclosure**: Optional intent fields and long warnings remain
  understandable without obscuring the primary source-and-create flow.
- **Responsive transformation**: The landing motif and intake sidecar become a
  logical single-column story on mobile; primary controls remain at least 44px
  high where practical.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/tests/browser/__init__.py` | Browser fixture package boundary | ~10 |
| `backend/tests/browser/deterministic_app.py` | Isolated real FastAPI/facade/worker test server | ~220 |
| `backend/tests/browser/test_deterministic_app.py` | Fail-closed fixture and lifecycle contracts | ~180 |
| `backend/tests/support/deterministic_course.py` | Shared deterministic request/profile/scenario builders | ~300 |
| `frontend/src/routes/index.tsx` | Public research-atelier landing page | ~220 |
| `frontend/src/routes/_layout/create.tsx` | Authenticated course intake route | ~100 |
| `frontend/src/routes/_layout/jobs.$jobId.tsx` | Owner progress route and route boundary | ~140 |
| `frontend/src/components/Landing/LandingPage.tsx` | Public story, proof, and access composition | ~260 |
| `frontend/src/components/CourseIntake/CourseIntakeForm.tsx` | Multimode form orchestration | ~300 |
| `frontend/src/components/CourseIntake/InputModeField.tsx` | Accessible source-mode selection and input | ~180 |
| `frontend/src/components/CourseIntake/LearningIntentFields.tsx` | Optional preference and goal fields | ~200 |
| `frontend/src/components/CourseIntake/SourcePreview.tsx` | Bounded local source/file preview | ~110 |
| `frontend/src/components/CourseProgress/CourseProgressPage.tsx` | Progress and safe terminal presentation | ~260 |
| `frontend/src/components/CourseProgress/queries.ts` | Query keys and bounded polling decisions | ~170 |
| `frontend/src/lib/schemas/job.ts` | Strict mirrored intake and draft schemas | ~220 |
| `frontend/src/lib/course-draft.ts` | Session-scoped bounded draft persistence | ~100 |
| `frontend/src/hooks/useCourseSubmission.ts` | Generated-client mutation and idempotency lifecycle | ~170 |
| `frontend/src/lib/schemas/job.test.ts` | Request-bound and payload-shaping unit tests | ~220 |
| `frontend/src/lib/course-draft.test.ts` | Draft cleanup and re-entry tests | ~100 |
| `frontend/src/components/CourseProgress/queries.test.ts` | Polling/status state-machine tests | ~200 |
| `frontend/src/hooks/useCourseSubmission.test.tsx` | Idempotency and duplicate-trigger tests | ~180 |
| `frontend/tests/course-journey.spec.ts` | Public, intake, progress, refresh, and failure E2E | ~320 |
| `frontend/playwright.jobs.config.ts` | Isolated deterministic browser server configuration | ~120 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/tests/acceptance/conftest.py` | Import shared deterministic builders without changing acceptance behavior | ~40 |
| `frontend/src/routes/_layout/index.tsx` | Retire transitional protected index after `/create` replacement | ~10 |
| `frontend/src/routes/_layout.tsx` | Add `/create` and dynamic job section labels | ~20 |
| `frontend/src/routes/login.tsx` | Preserve safe draft handoff and navigate to `/create` | ~25 |
| `frontend/src/routes/signup.tsx` | Render configuration-accurate invite or signup path | ~35 |
| `frontend/src/components/Sidebar/AppSidebar.tsx` | Make course creation the primary workspace destination | ~15 |
| `frontend/src/lib/schemas/fields.ts` | Add reusable exact job field bounds | ~100 |
| `frontend/src/lib/schemas/index.ts` | Export job schemas and types | ~15 |
| `frontend/src/lib/types/branded.ts` | Add JobId, ArtifactId, and IdempotencyKey factories/guards | ~140 |
| `frontend/src/lib/types/index.ts` | Export course domain brands | ~15 |
| `frontend/src/hooks/useAuth.ts` | Use the authenticated create destination | ~10 |
| `frontend/src/vite-env.d.ts` | Type the explicit signup build setting | ~5 |
| `frontend/.env.example` | Document the frontend signup visibility setting | ~3 |
| `frontend/Dockerfile` | Accept the matching non-secret build argument | ~5 |
| `docker-compose.yml` | Pass judge/demo signup visibility to the frontend build | ~5 |
| `docker-compose.override.yml` | Keep local behavior explicit and testable | ~5 |
| `frontend/tests/auth.setup.ts` | Seed auth at the new protected destination | ~10 |
| `frontend/tests/login.spec.ts` | Verify access handoff and invite-only copy | ~60 |
| `frontend/src/index.css` | Add semantic landing/intake/progress composition roles only where tokens are missing | ~80 |
| `frontend/src/routeTree.gen.ts` | Regenerated by TanStack Router; never hand edited | generated |
| `docs/dashboard-design.md` | Replace transitional route guidance with implemented Phase 04 slice | ~80 |
| `frontend/README_frontend.md` | Document public, create, and job progress routes | ~20 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] Signed-out `/` renders the product story and no protected user query.
- [ ] Login, configured signup, and safe draft handoff reach `/create`.
- [ ] All seven enabled input modes build only the exact JSON or multipart
      request declared by the generated client.
- [ ] One stable idempotency key survives an exact retry; source/preference
      changes rotate it; repeated clicks while pending do nothing.
- [ ] Accepted submissions navigate using the server-provided job identity and
      the owner route survives direct load and refresh.
- [ ] Polling renders the generated finite states, warnings, units, and safe
      failure fields, backs transient loss off, and stops at terminal state.
- [ ] Missing and foreign jobs remain the same safe not-found experience.
- [ ] Existing `/setup`, `/settings`, `/admin`, auth recovery, and account
      deletion behavior remain intact.

### Testing Requirements

- [ ] Failing tests precede deterministic fixture, schema, identity, mutation,
      route, and polling implementation.
- [ ] Backend test server proves real durable commit, execution, read,
      replacement, cleanup, and non-production isolation.
- [ ] Vitest covers exact bounds, draft reset, idempotency, exhaustive states,
      visibility cadence, transient backoff, and terminal stop.
- [ ] Playwright covers signed-out landing, configured access, every intake
      family, double click, refresh, ownership, warnings, failure,
      reconnecting, mobile, keyboard, and reduced motion.

### Non-Functional Requirements

- [ ] Polling is 1.5 seconds while visible, 10 seconds while hidden, backs
      transient failures off to at most 30 seconds, and performs no terminal
      requests.
- [ ] Main mobile actions are at least 44px high where practical and the page
      has no document-level horizontal overflow at 320px or 200% zoom.
- [ ] Both themes meet WCAG 2.2 AA for rendered text and controls; state is not
      communicated by color or motion alone.
- [ ] Product surfaces contain no debug labels, package/version detail,
      readiness telemetry, provider detail, private paths, tokens, input body,
      or artifact bytes.
- [ ] The deterministic browser path is credential-free, network-free, finite,
      isolated, and cleans every worker, facade, file, and temporary directory.

### Quality Gates

- [ ] All files are ASCII-encoded with Unix LF line endings.
- [ ] Code follows project and package conventions with first-year-friendly
      comments around non-obvious state, cleanup, and security behavior.
- [ ] Backend Ruff, format, mypy, ty, focused/full tests, and package boundary
      checks pass.
- [ ] Frontend Biome, TypeScript, Vitest, production build, generated route,
      and full relevant Playwright checks pass.
- [ ] Generated OpenAPI/client output remains deterministic and unedited.
- [ ] Primary user-facing surfaces contain product-facing copy only.
- [ ] Rendered QA passes at 375x812 and 1440x900 in light/dark, keyboard, and
      reduced-motion modes, with baseline and completed observations recorded.

---

## 8. Implementation Notes

### Working Assumptions

- A separate browser-test FastAPI module is the narrowest truthful fixture:
  `create_app` already injects lifecycle, worker, readiness, and authentication
  factories, while the acceptance suite already owns a complete deterministic
  scenario. Reusing those public seams exercises persistence without adding a
  production flag or route-only job mock.
- Signup visibility needs an explicit frontend build-time boolean because the
  public API intentionally does not reveal server configuration. The value is
  non-secret, defaults to false like the backend, and affects only access copy
  and navigation; the backend remains authoritative on registration.
- The existing editorial type, warm-neutral tokens, forest action color, and
  restrained technical accents fit the research-atelier direction. This
  session evolves composition and state anatomy rather than replacing
  protected primitives or introducing bitmap art.

### Conflict Resolutions

- The product plan asks for `review-required`, but the generated `JobStatus`
  union has only accepted, researching, drafting, validating, rendering,
  delivering, completed, failed, and cancelled. The UI renders the finite
  contract and safe failure message only; it does not synthesize a hidden
  review status.
- The visual-skill project map still inventories deleted donor Dashboard and
  Items components. Current worktree, generated route tree, transition
  Playwright tests, and the updated design guide are authoritative; no donor
  component or shared transition returns.
- The source plan says preserve a drafted prompt "when practical." Session
  storage is selected because auth tokens are already session-scoped and a
  bounded prompt can survive login without entering URLs, persistent storage,
  logs, or server state.

### Key Considerations

- The JSON route supports `youtube` intent even though the package stores it as
  URL input; frontend discrimination must preserve the browser intent exactly.
- Browser upload preview shows metadata only. File bytes cross directly to the
  generated multipart serializer after Zod and local size/type checks.
- Current API failure fields and progress copy are already safe. Components
  should display them without appending exception, policy, provider, or retry
  speculation.
- Test server faults and pauses are diagnostics confined to the isolated test
  app and test code. No learner route can discover or activate them.

### Potential Challenges

- **Deterministic work completes too quickly for progress assertions**: Add
  bounded test-only stage gates around the real worker/executor composition,
  not mocked HTTP snapshots, and always release them during fixture cleanup.
- **Form state becomes too large across seven modes**: Keep one discriminated
  source union and compose preference fields; unregister inactive input values
  so no extra field reaches the request.
- **Visibility and network callbacks create stale timers**: Derive the next
  interval from query state and `document.visibilityState`, clean listeners on
  scope exit, and use fake timers in unit tests.
- **Signup UI and backend settings drift**: Default both to false, document the
  same root setting through Compose, and test both enabled and disabled builds
  while retaining backend 403 authority.
- **Route restructuring regresses auth tests**: Update route destinations and
  selectors in the same task, then run the full existing Playwright suite.

### Relevant Considerations

- [P03-frontend+backend] **The learner workspace needs real job integration**:
  This session replaces the static protected overview with generated-client
  intake and status composition.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**:
  Request shaping imports generated types and uses `JobsService`; generated
  files remain script-owned.
- [P03-backend+backend/packages/txt2crs] **Job HTTP routes use public handles**:
  The test harness and UI preserve durable admission, public allowlists,
  owner-hidden reads, and private delivery semantics.
- [P02-backend+frontend] **Authorization and polling follow server state**:
  `_layout` guards run before job queries, and polling is finite,
  visibility-aware, revision-aware, and terminal-stopping.
- [P00-frontend] **Rendered QA complements source checks**: Current and changed
  light/dark mobile/desktop surfaces require browser inspection.
- [P01-backend/packages/txt2crs] **Private-state retention is undefined**:
  Landing/privacy copy states local privacy behavior without claiming a final
  legal basis, provider-copy erasure, or retention schedule.

### Behavioral Quality Focus

Checklist active: Yes

Top behavioral risks for this session:

- Duplicate paid generation from repeat clicks, transport retry, remount, or
  a changed request using a stale idempotency key.
- Polling leaks, stale snapshots, infinite retry, or invented progress after
  visibility changes, route re-entry, auth loss, and terminal state.
- Test-only lifecycle, worker, timer, object, file, or temporary-directory
  resources escaping their scope or becoming reachable in production.
- Private source/provider/error content reaching product copy, logs, URLs,
  persistent browser storage, or diagnostic UI.
- Responsive mode/form transitions retaining inactive fields, losing focus, or
  making the primary action unavailable to keyboard and touch users.

---

## 9. Testing Strategy

### Unit Tests

- Zod: exact string/file bounds, HTTPS shape, unique goals, literal consent,
  age/level enums, inactive-mode stripping, and JSON/multipart payload shape.
- Brands and draft storage: validated IDs/keys, bounded prompt persistence,
  corrupt/oversized reset, consume/revalidate behavior, and no localStorage.
- Submission: key reuse for exact retry, rotation after any canonical form
  change or success, pending duplicate prevention, safe Problem Details, and
  cleanup after route exit.
- Query policy: every generated status, visible/hidden intervals, backoff cap,
  recovery after transient failure, revision comparison, and terminal stop.

### Integration Tests

- Start the test-only FastAPI app over isolated deterministic package state,
  authenticate normally, submit through HTTP, observe real durable revisions,
  reopen/read the same job, and verify cleanup.
- Prove the production `app.main:app` route graph has no test control path and
  the test module fails closed without its explicit isolated environment.
- Run existing Phase 03 backend acceptance tests after moving scenario support
  to prove no behavioral drift.

### Runtime Verification

- Inspect public landing, intake, progress, reconnecting, failed, cancelled,
  and completed handoff states at 375x812 and 1440x900 in light and dark.
- Exercise keyboard-only mode selection, goals, consent, submit, direct job
  reload, sidebar navigation, and error recovery with visible focus.
- Emulate reduced motion and hidden/visible document state; confirm complete
  static presentation, finite requests, no overflow, and no layout shift.
- Review browser console, failed network requests, accessible landmarks,
  headings, status announcements, touch targets, and long source/warning copy.

### Edge Cases

- Empty, whitespace, 2/3/10,000-character prompt, 200,000-character text,
  malformed/non-HTTPS/credentialed/fragment URL, and long YouTube URL.
- Zero, one, ten, eleven, duplicate-case, long, and reordered learning goals.
- File absent, wrong extension/type, zero bytes, exact/over 20 MiB, replacement,
  and mode switching after selection.
- Double click, Enter plus click, exact retry, changed request after failure,
  refresh during pending, and direct terminal re-entry.
- 401 token loss, uniform 404 missing/foreign, 409 key conflict, 413/415/422,
  429 admission/rate limit, 503 readiness, safe 500, offline, and recovery.
- Unknown runtime status despite compile-time exhaustiveness must fail to a
  safe generic error boundary, never a guessed stage.

---

## 10. Dependencies

### Other Sessions

- Depends on: Phase 03 sessions 01-03.
- Depended by:
  `phase04-session02-results-preview-and-experience-validation`.

---

## Next Steps

Run the `implement` workflow step to begin implementation.
