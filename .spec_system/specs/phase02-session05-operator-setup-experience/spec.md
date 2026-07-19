# Session Specification

**Session ID**: `phase02-session05-operator-setup-experience`
**Phase**: 02 - Composition and Readiness
**Status**: Implemented
**Created**: 2026-07-19
**Base Commit**: 3b1986b7a9aa977d9649371625354171c1866590
**Package**: frontend
**Package Stack**: React 19, TypeScript 7, TanStack Router/Query, Tailwind CSS
4, shadcn/Radix, and generated OpenAPI client

---

## 1. Session Overview

This session completes Phase 02 with a protected superuser `/setup` route.
The screen extends the existing refined-editorial workspace into an operator
field guide: one readiness verdict, one dedicated ChatGPT connection action,
a numbered system checklist, enabled input capabilities, and exact CLI
recovery.

The route reads only Session 04's generated cache endpoints. Independent
readiness and authentication requests start together under one Suspense
boundary. Authentication status polls only while the safe state is
`waiting_for_user`, then stops on authenticated, failed, route unmount, or
query cancellation. Starting a ceremony updates the existing query cache
instead of creating parallel local server state.

No token, credential field, account identity, provider payload, raw exception,
path, port, or unbounded diagnostic enters the browser surface.

---

## 2. Objectives

1. Give a superuser a truthful at-a-glance answer to whether course work can
   be accepted and which coarse system checks are ready.
2. Guide one browser-safe ChatGPT device ceremony from start through terminal
   state using only generated client contracts.
3. Make unavailable, busy, failed, loading, and recovery states actionable
   without exposing provider or infrastructure internals.
4. Preserve route authorization, query/session behavior, existing design
   tokens, responsive shell, keyboard focus, live announcements, and reduced
   motion.
5. Prove the screen in light/dark desktop and mobile with deterministic mocked
   browser states plus the real unconfigured local backend.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase02-session04-system-readiness-and-auth-api` - provides protected
  cached readiness/start/status routes and generated frontend contracts.
- [x] `phase02-session03-cached-readiness-and-observability` - defines coarse
  safe state, freshness, warnings, recovery actions, and side-effect-free
  reads.
- [x] `phase02-session01-engine-composition-lifecycle` - keeps missing
  external credentials a truthful loadable setup state.

### Required Tools Or Knowledge

- TanStack Router route guards and generated file routing.
- TanStack Query suspense, mutation cache updates, and conditional polling.
- Existing shadcn/Radix Alert, Badge, Button, Card, Separator, and Skeleton
  compositions.
- Playwright route mocking, keyboard checks, responsive viewports, and theme
  validation.

### Environment Requirements

- Deterministic unit and browser tests require no Codex login, Tavily key, MCP
  listener, or external network.
- Real-shell QA uses the local backend and project PostgreSQL through temporary
  host-port overrides when unrelated processes own the documented ports.
- The Browser plugin is not installed in this session, so rendered QA uses the
  repository's regular Playwright/Chromium workflow.

---

## 4. Scope

### In Scope (MVP)

- Superuser-only `/setup` route guard and page metadata.
- Superuser-only sidebar navigation entry and command-strip label.
- Parallel suspense queries for cached readiness and auth status.
- Conditional bounded polling only while waiting for device approval.
- Start/replay mutation with safe inline error and query-cache updates.
- Readiness verdict, freshness, model, input modes, coarse checks, warnings,
  and recovery actions.
- Waiting challenge with external OpenAI link, bounded code, copy feedback,
  and live status.
- Signed-out, waiting, authenticated, failed, unavailable, busy, loading, and
  retry states.
- Exact documented CLI recovery command.
- Responsive light/dark composition, keyboard focus, 44-pixel practical touch
  targets, status announcements, and reduced-motion behavior.
- Unit, Playwright, rendered screenshot, frontend static/build, and repository
  validation.
- Design-system documentation update for the setup screen blueprint.

### Out Of Scope (Deferred)

- Device-auth logout or account switching.
- Learner create, progress, results, library, or artifact experiences.
- Credential/token input fields or account email display.
- New backend route, API schema, provider choice, model choice, or generated
  client edit.
- Hosted deployment, multi-operator auth pools, or live credentialed proof.
- New animation library, route transition, image asset, shadcn primitive, or
  dependency.

---

## 5. Visual And Technical Approach

### Design Thesis

The setup screen should feel like an editorial field guide joined to a
precise preflight checklist because a trusted operator must understand the
system before allowing learner work. It avoids a generic status-card grid and
uses one strong verdict, a restrained two-column desktop composition, numbered
checks, technical mono values, and plain recovery copy so the operator believes
the state is truthful before starting authentication.

### Load-Bearing Visual Decisions

1. **One verdict leads**: Page identity and a single readiness statement appear
   before details; color always accompanies explicit status text.
2. **Authentication is the action surface**: The device ceremony receives the
   largest interactive panel; diagnostics stay secondary.
3. **Checks form an index, not KPI tiles**: Eight coarse checks use compact
   numbered rows so the page stays scannable and product-specific.
4. **Technical values stay technical**: Model, user code, timestamp, and CLI
   command use the established mono role; narrative/recovery copy uses body
   type.
5. **Mobile reorders by task**: Verdict, authentication action/code, recovery,
   then the detailed check index. Buttons remain full-width and touch-friendly.
6. **Motion remains feedback-only**: Existing button/focus transitions stay;
   polling changes text/icon state without new entrance or looping animation.

### Data And State Architecture

Create feature-local query option factories with stable keys:

- `["system", "readiness"]`
- `["system", "authentication"]`

Use `useSuspenseQueries` so independent GETs begin together. The auth query's
`refetchInterval` returns a finite interval only for
`waiting_for_user`; terminal states return `false`. The start mutation writes
its response directly to the auth query cache. It invalidates readiness after
authenticated state becomes observable, while the existing backend cache
remains the truth.

Presentation helpers map generated finite states to labels, icon roles, Badge/
Alert variants, and operator copy. They never reinterpret readiness or invent
progress/expiry. The package exposes no expiry, so the session PRD's historical
"expired" state resolves to the API's safe `failed` recovery state.

### Route And Authorization

`/_layout/setup` uses the existing current-user query key and the same
superuser `beforeLoad` pattern as `/admin`. Non-superusers redirect to
`/forbidden` before any system query. The sidebar entry is rendered only when
`currentUser.is_superuser` is true.

### Error And Privacy Boundary

Generated requests throw the project's `ApiError`. The page uses
`getApiErrorMessage()` only for the server's already-safe RFC 9457 detail and
offers retry/start-again actions. It never logs or serializes the error object.
No response field outside the generated allowlist is rendered.

---

## 6. Screen Blueprint

### Name

System Setup

### User Job

Confirm that course generation is operational and connect the one dedicated
ChatGPT subscription identity when needed.

### Primary Action

`Connect ChatGPT` -> `Open verification page` -> terminal
`ChatGPT connected` or safe `Try connection again`.

### Desktop Composition

- Page header with operator eyebrow, stable title, and refresh action.
- Full-width readiness verdict strip with freshness/model metadata.
- Two columns: authentication action panel (wider) and operator recovery with
  warnings/actions plus the exact CLI command.
- Full-width numbered system checklist after the action-oriented panels.

### Mobile Transformation

- Header and refresh stack.
- Verdict remains first.
- Authentication action/code comes before diagnostics.
- Recovery precedes the detailed checks, and the exact command wraps within
  its bounded code surface rather than causing page overflow.

### Loading

One page-level status announcement and static skeleton geometry matching the
verdict, authentication panel, and check rows. No shimmer.

### Error And Recovery

Inline destructive Alert preserves the shell and explains that safe setup
state could not be loaded. `Try again` resets both suspense queries. Mutation
errors remain inside the authentication panel.

### Success

Authenticated state removes challenge URL/code, announces completion, and
shows a success Badge/Alert plus readiness refresh.

### Keyboard And Focus

- Route order follows visual order.
- Refresh, start, external verification, and copy are native buttons/links.
- External link has an explicit accessible name and `rel="noreferrer"`.
- Copy feedback is announced politely.
- No focus moves automatically during polling.

### Motion Role

Still by default. Existing control hover/focus transitions remain; no new
looping, route, layout, or scroll-linked motion.

---

## 7. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `frontend/src/components/SystemSetup/presentation.ts` | Finite labels, variants, ordering, CLI command, and safe helpers | ~220 |
| `frontend/src/components/SystemSetup/queries.ts` | Stable query options, bounded polling, and cache keys | ~150 |
| `frontend/src/components/SystemSetup/ReadinessOverview.tsx` | One verdict with model/freshness/input context | ~220 |
| `frontend/src/components/SystemSetup/AuthenticationPanel.tsx` | Start/replay/challenge/copy/terminal/error experience | ~300 |
| `frontend/src/components/SystemSetup/SystemChecklist.tsx` | Numbered coarse-check index | ~180 |
| `frontend/src/components/SystemSetup/RecoveryPanel.tsx` | Warnings, actions, and exact CLI fallback | ~180 |
| `frontend/src/components/SystemSetup/SystemSetupWorkspace.tsx` | Parallel queries, mutation, and screen composition | ~260 |
| `frontend/src/components/Pending/PendingSystemSetup.tsx` | Static accessible route skeleton | ~150 |
| `frontend/src/routes/_layout/setup.tsx` | Route guard, metadata, Suspense, and error boundary | ~180 |
| Focused unit tests and `frontend/tests/setup.spec.ts` | State/polling and browser-flow regressions | ~650 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `frontend/src/components/Sidebar/AppSidebar.tsx` | Add superuser-only system setup entry | ~8 |
| `frontend/src/routes/_layout.tsx` | Add setup command-strip label | ~2 |
| `frontend/src/routeTree.gen.ts` | Generated route registration; never hand-edit | generated |
| `docs/dashboard-design.md` | Record setup blueprint, states, and QA contract | ~80 |
| Apex PRD/state/session artifacts | Record implementation, review, validation, and phase completion | ~400 |

---

## 8. Success Criteria

### Functional Requirements

- [x] Only superusers can navigate to or directly load `/setup`; denial occurs
  before system endpoint access.
- [x] Readiness and auth status start in parallel and render only generated
  safe fields.
- [x] Signed-out operators can start exactly one ceremony and receive the
  validated external URL, bounded code, and safe message.
- [x] Waiting status polls at a bounded interval and stops automatically on
  authenticated, failed, or unmount state.
- [x] Repeated start uses the server replay response and does not create a
  second client-side ceremony.
- [x] Authenticated/failed states remove URL/code and show stable next actions.
- [x] Unavailable/busy/readiness warnings expose only safe recovery copy and
  exact documented CLI fallback.
- [x] Refresh resets/reloads both caches without clearing authentication
  session or changing route.

### Testing Requirements

- [x] Tests are written and observed failing before feature implementation.
- [x] Presentation and query/polling unit tests pass.
- [x] Focused Playwright covers permission, ready, waiting, terminal, failed,
  responsive, keyboard, live-region, and safe-field behavior.
- [x] Complete frontend unit and E2E suites remain green with the required
  backend environment.

### Non-Functional Requirements

- [x] No dependency, generated client, protected primitive, API, or database
  source is manually changed.
- [x] Independent requests avoid waterfalls; cache updates avoid duplicate
  local server state and unnecessary rerenders.
- [x] Light/dark desktop and 375x812 mobile remain readable with no clipping,
  accidental page overflow, or layout shift.
- [x] Touch targets, focus visibility, heading order, landmarks, live status,
  external-link labeling, and reduced motion satisfy the accessibility
  contract.
- [x] Tokens and existing primitives produce one coherent editorial operator
  experience without raw status colors or one-off design-system values.

### Quality Gates

- [x] All changed text files are ASCII with Unix LF line endings.
- [x] Code includes intern-friendly comments for authorization, query cache,
  polling termination, privacy, and accessible state changes.
- [x] Biome, TypeScript, Vite build, Playwright, repository pre-commit, and
  rendered browser QA pass.

---

## 9. Validation Plan

1. Observe missing helper/route tests fail before implementation.
2. Run focused Vitest presentation and query tests.
3. Run mocked Playwright permission, state, polling, external-link, keyboard,
   and responsive flows.
4. Run the real local unconfigured-backend setup flow without external
   credentials.
5. Inspect 1440x900 and 375x812 in light and dark, plus reduced motion.
6. Check page identity, nonblank DOM, framework overlay, console health,
   interaction state, focus order, clipping, overflow, and long safe copy.
7. Run complete frontend unit and E2E suites.
8. Run Biome, TypeScript, production build, and repository pre-commit.
9. Verify generated/protected files, dependency lock, safe field inventory,
   ASCII/LF, patch integrity, and final status.

---

## 10. Relevant Considerations

- [P02-backend+frontend] **Auth polling reads only generated safe state**.
- [P02-backend] **A lease follows background work, not the request**.
- [P02-backend] **Browser readiness reads only the cache**.
- [P02-backend] **Operational logs use field allowlists**.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**.
- [P00] **Client generation is formatter-owning**.
- [P00-frontend] **Rendered QA complements source checks**.
- [P00-backend+backend/packages/txt2crs] **One process is mandatory**.
