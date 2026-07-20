# Session Specification

**Session ID**: `phase04-session02-results-preview-and-experience-validation`
**Phase**: 04 - Learner Experience
**Status**: Complete
**Created**: 2026-07-20
**Base Commit**: acb55418a22beef91e3349eb9a66f734eb112995
**Package**: frontend
**Package Stack**: React 19, TypeScript, Vite, TanStack Query/Router, generated OpenAPI client

---

## 1. Session Overview

This session completes the learner journey at the durable job URL. A completed
job becomes a four-publication results workspace for the course, review pack,
assessment, and instructor answer key. Each publication exposes its real
rendered formats, byte size, primary PDF download, secondary format menu, and a
private HTML preview. The same workspace discloses source provenance,
conflicts, and truncation truthfully without exposing private engine state.

It is next because Session 01 already submits through the generated jobs
client, polls the durable job to a terminal state, and proves a deterministic
course with all sixteen artifacts. The backend already owns authorization,
manifest integrity, content delivery, and artifact verification. This session
does not duplicate those responsibilities: it composes the generated manifest
and artifact operations into a secure, accessible frontend.

The preview is an authenticated, bounded, preview-only copy of a rendered HTML
artifact. It is parsed outside the React tree, receives a restrictive CSP and
defense-in-depth navigation stripping, and is shown in a sandboxed iframe. The
original artifact remains unchanged for download. No artifact HTML is inserted
into the parent document.

---

## 2. Objectives

1. Render exactly four publication cards from the owner-private artifact
   manifest and preserve the generated format contract.
2. Make PDF the clear primary download while keeping HTML, Markdown, PDF, and
   DOCX available through an accessible format menu.
3. Preview bounded HTML safely in a sandboxed, no-referrer iframe with strict
   lifecycle cleanup and no parent DOM injection.
4. Disclose sources, conflicts, truncation, and instructor-only answer-key
   intent using truthful server data and progressive disclosure.
5. Prove the full signed-out-to-results journey at mobile, tablet, desktop,
   light, dark, keyboard, reduced-motion, and zoom-equivalent targets.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase04-session01-public-landing-intake-and-progress` - public access,
      strict intake, deterministic browser composition, and refresh-safe
      progress at the durable job URL.
- [x] `phase03-session02-owner-scoped-job-results-and-recovery` - owner-private
      result, manifest, artifact download, renderer validation, and uniform
      missing/foreign behavior.

### Required Tools Or Knowledge

- Generated `JobsService.readJobArtifacts` and
  `JobsService.downloadJobArtifact` operations and generated result/manifest
  unions.
- TanStack Query terminal-state composition, Radix/shadcn Dialog,
  DropdownMenu, and Collapsible primitives.
- Browser `DOMParser`, Blob/Object URL lifecycle, iframe sandboxing, CSP, and
  Playwright accessibility-tree and rendered-state assertions.

### Environment Requirements

- Node.js/npm dependencies installed under `frontend/`.
- Isolated deterministic browser fixture from Session 01 available; it
  requires no provider credentials or external network.
- Backend uv workspace synchronized for cross-boundary regression checks.
- No change to the user's retained Docker services or private application
  state.

---

## 4. Scope

### In Scope (MVP)

- A completed `/jobs/$jobId` loads `readJobArtifacts` only after the job is
  terminal-complete and renders course, review pack, assessment, and answer key
  in stable product order.
- Every publication presents only manifest-backed formats with human-readable
  sizes; the deterministic journey proves all four expected formats per
  publication and sixteen artifacts total.
- PDF is the primary download. HTML, Markdown, PDF, and DOCX are available in
  a keyboard-operable secondary menu when present.
- Artifact transfers use `downloadJobArtifact`, reject metadata/content
  mismatches safely, preserve the server-provided safe filename, prevent
  duplicate triggers, and release every temporary object URL.
- HTML preview is allowed only when the manifest declares compatible HTML and
  the exact content size is at or below a public frontend cap that defaults to
  5,242,880 bytes.
- Preview content is parsed into a preview-only document, supplied a restrictive
  CSP, stripped of navigation/active-content affordances, and rendered in an
  iframe with an empty sandbox capability set and `no-referrer`.
- Preview dialog loading, unavailable, oversize, malformed, offline, retry,
  close, focus-return, route re-entry, and cleanup states are explicit.
- Source links, source count, conflict records, and source/conflict truncation
  are disclosed from `JobResult`; external links use safe protocol handling
  and opener isolation.
- The instructor answer key is visually distinct and collapsed by default,
  with its availability announced without exposing artifact content early.
- Manifest loading, retry, invalid/missing formats, artifact denial, and the
  existing uniform missing/foreign job behavior remain safe and comprehensible.
- The full deterministic browser journey validates real manifest and artifact
  responses, not route-level mocks.
- Documentation describes the results route, private delivery, preview cap,
  sandbox boundary, generated-client ownership, and current compliance limits.

### Out Of Scope (Deferred)

- Editing, regeneration, collaboration, share links, public artifacts, LMS
  export, grading, quiz playback, job library, per-job deletion, or
  cancellation - no approved API exists for these behaviors.
- Recomputing artifact hashes in the browser - the backend already verifies
  the stored content hash before delivery; the frontend validates response
  bytes and declared media compatibility.
- Trusting or executing artifact scripts, forms, popups, downloads,
  same-origin capabilities, or top-level navigation in preview.
- New backend generation, research, validation, persistence, rendering,
  authorization, manifest, or artifact logic.
- Claims of formal GDPR compliance, guaranteed provider deletion, or retention
  policy beyond the implemented owner-private behavior.

---

## 5. Technical Approach

### Architecture

Add a `CourseResults` feature under `frontend/src/components/` and mount it
from the completed branch of `CourseProgressPage`. The durable job route and
its protected parent remain unchanged. A terminal-enabled TanStack query calls
the generated manifest operation; it has no independent polling loop.

Keep pure generated-contract interpretation in `presentation.ts`. It maps the
finite deliverable and format unions into a stable four-card view, formats
bytes, validates preview eligibility, and fails closed on malformed runtime
data. `artifact-transfer.ts` normalizes the generated client's Blob/File/string
response without introducing direct `fetch`. `useArtifactTransfer` owns one
in-flight transfer per artifact and the complete object URL lifecycle.

`preview-document.ts` uses `DOMParser` to create a separate HTML document,
removes active/navigation affordances, replaces any document CSP with the
session's restrictive policy, and serializes only the bounded preview copy.
`HtmlArtifactPreview` is lazy-loaded, obtains HTML through the same generated
artifact mutation, verifies exact byte size against the manifest entry, and
places a revocable Blob URL in an iframe. The iframe receives `sandbox=""`,
`referrerPolicy="no-referrer"`, a descriptive title, and no permission
attributes.

The public preview cap uses `VITE_HTML_PREVIEW_MAX_BYTES`, parsed as a positive
finite integer with a 5 MiB fallback. Docker and Compose pass the same
non-secret setting at build time. The backend remains authoritative for
delivery; this frontend value only controls whether a delivered artifact may
be previewed.

The deterministic Session 01 scenario already yields sixteen real artifacts,
so browser tests extend that story without a new backend fixture endpoint.
Tests assert user-visible cards/actions and the actual iframe security
attributes, resource cleanup, real response sizes, accessibility semantics,
and absence of parent-document artifact content.

### Design Patterns

- **Publication folio**: The completed state feels like a coherent editorial
  collection, with four distinct covers sharing one typographic and spacing
  system.
- **Progressive privacy**: The answer key starts closed and source/conflict
  detail expands on demand; the existence and purpose of each remain clear.
- **One obvious action**: PDF is the primary action; alternate formats live in
  a labeled menu rather than four competing buttons.
- **Generated-contract truth**: Cards, formats, sizes, sources, and warnings
  come from generated response fields. No client invents artifacts or
  completion metadata.
- **Defense in depth**: Authenticated delivery, server integrity checks,
  frontend byte/media checks, preview sanitization, CSP, iframe sandboxing,
  no-referrer, and URL cleanup are independent boundaries.
- **Responsive folio**: Four columns can become two and then one without
  changing semantic order, clipping long titles, or pushing actions off-screen.
- **Quiet motion**: Existing primitive transitions and the global
  reduced-motion clamp are sufficient; this session adds no choreographed
  route or scroll motion.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `frontend/src/components/CourseResults/CourseResultsWorkspace.tsx` | Result query state and four-publication composition | ~220 |
| `frontend/src/components/CourseResults/PublicationCard.tsx` | Publication-specific card and disclosure shell | ~170 |
| `frontend/src/components/CourseResults/ArtifactActions.tsx` | Primary PDF and alternate-format actions | ~170 |
| `frontend/src/components/CourseResults/HtmlArtifactPreview.tsx` | Lazy sandboxed preview dialog | ~220 |
| `frontend/src/components/CourseResults/ResultDisclosure.tsx` | Sources, conflicts, truncation, and privacy copy | ~190 |
| `frontend/src/components/CourseResults/presentation.ts` | Strict manifest-to-view mapping and byte labels | ~190 |
| `frontend/src/components/CourseResults/presentation.test.ts` | Manifest, order, format, and disclosure tests | ~220 |
| `frontend/src/components/CourseResults/queries.ts` | Terminal manifest query options | ~100 |
| `frontend/src/components/CourseResults/queries.test.ts` | Query enablement and retry tests | ~120 |
| `frontend/src/components/CourseResults/artifact-transfer.ts` | Response normalization and metadata checks | ~140 |
| `frontend/src/components/CourseResults/artifact-transfer.test.ts` | Blob/string/File and mismatch tests | ~170 |
| `frontend/src/components/CourseResults/useArtifactTransfer.ts` | Generated-client mutation and URL cleanup | ~170 |
| `frontend/src/components/CourseResults/useArtifactTransfer.test.tsx` | Duplicate trigger and cleanup tests | ~180 |
| `frontend/src/components/CourseResults/preview-document.ts` | CSP insertion and active/navigation stripping | ~170 |
| `frontend/src/components/CourseResults/preview-document.test.ts` | Hostile document and policy tests | ~200 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `frontend/src/components/CourseProgress/CourseProgressPage.tsx` | Mount results in the completed durable route | ~45 |
| `frontend/src/lib/public-config.ts` | Parse the bounded public preview cap | ~35 |
| `frontend/src/lib/public-config.test.ts` | Preview-cap fallback and bound tests | ~50 |
| `frontend/src/vite-env.d.ts` | Type the preview-cap build variable | ~3 |
| `frontend/.env.example` | Document the non-secret preview cap | ~3 |
| `frontend/Dockerfile` | Accept and expose the preview-cap build argument | ~4 |
| `docker-compose.yml` | Pass the preview cap to production frontend build | ~3 |
| `docker-compose.override.yml` | Keep the local preview cap explicit | ~3 |
| `frontend/src/index.css` | Add semantic result-folio roles in both themes | ~90 |
| `frontend/tests/course-journey.spec.ts` | Real results, transfers, preview, and accessibility E2E | ~260 |
| `docs/dashboard-design.md` | Record implemented results anatomy and states | ~80 |
| `frontend/README_frontend.md` | Document private results and preview boundary | ~25 |
| `docs/onboarding.md` | Add deterministic results verification commands | ~20 |
| `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` | Reconcile delivered learner-experience details | ~20 |
| `docs/CHANGELOG.md` | Record completed results workspace changes | ~20 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] A completed owner job renders exactly four ordered publication cards
      backed by the real private manifest.
- [ ] The deterministic course exposes all sixteen artifacts and each card
      lists only its four manifest-backed formats with correct byte labels.
- [ ] PDF is the primary action and the alternate format menu is complete,
      keyboard operable, and disabled while that artifact is transferring.
- [ ] Downloads use the generated artifact operation, retain the safe manifest
      filename, reject response mismatches, and never double-trigger.
- [ ] HTML preview is capped at 5 MiB by default, fetched privately, and never
      inserted into the parent React DOM.
- [ ] Preview uses a restrictive CSP, empty sandbox capability set,
      `no-referrer`, safe title, and complete Blob/Object URL cleanup.
- [ ] Sources, conflicts, and truncation match the server result; unsafe source
      links do not become navigable.
- [ ] The instructor answer key is distinct and collapsed by default.
- [ ] Manifest, transfer, preview, offline, missing/foreign, and retry states
      are safe, comprehensible, and refresh-stable at the same job URL.

### Testing Requirements

- [ ] Failing unit and browser tests precede manifest mapping, transfer,
      preview, and results component implementation.
- [ ] Vitest covers exact group/format order, malformed runtime data, byte/media
      mismatch, cap parsing, hostile HTML, duplicate action, and URL cleanup.
- [ ] Playwright proves the real sixteen-artifact manifest, a real download,
      preview sandbox/CSP, answer-key disclosure, direct refresh, and failure
      recovery through the deterministic application.
- [ ] Keyboard order, focus return, accessibility tree, live status,
      320/375/mobile, tablet, desktop, dark/light, reduced-motion, long title,
      and 200% zoom-equivalent states are verified.
- [ ] Full frontend, backend browser fixture, engine, generated-client,
      repository hook, ASCII/LF, secret, privacy, and resource-leak gates pass.

### Non-Functional Requirements

- [ ] Manifest fetching begins only after durable completion and creates no
      terminal polling loop.
- [ ] Preview parsing and serialization are bounded; files above the exact cap
      remain downloadable but are not previewable.
- [ ] No preview capability permits scripts, forms, popups, downloads,
      same-origin access, referrer disclosure, or top navigation.
- [ ] Every object URL, listener, query observer, and async continuation is
      released or safely ignored on close, route change, retry, and unmount.
- [ ] The results grid has no document-level horizontal overflow or visible
      layout shift at required viewports.
- [ ] Existing public landing, intake, progress, auth, setup, settings, admin,
      and account-deletion behavior remains intact.

### Code Quality Requirements

- [ ] Generated files under `frontend/src/client/` remain untouched.
- [ ] Route components call the generated txt2crs shell boundary and contain
      no research, rendering, persistence, or authorization duplication.
- [ ] Pure contract interpretation, transfer checks, and preview transformation
      are independently tested and named descriptively.
- [ ] New code uses centralized types/configuration, descriptive names, and
      generous first-year-intern-oriented boundary comments.
- [ ] No `dangerouslySetInnerHTML`, direct artifact `fetch`, inline script,
      `javascript:` navigation, or broad iframe sandbox token appears.
- [ ] Biome, TypeScript, Vitest, Vite build, Playwright, and repository hooks
      pass without ignored diagnostics.
- [ ] Product UI contains learner-facing language only; diagnostics and fixture
      controls remain test-only.

---

## 8. Assumptions And Resolved Conflicts

1. The Session 01 deterministic course remains the canonical browser fixture
   because it already renders four deliverables in four formats; no backend
   test-control expansion is needed.
2. `VITE_HTML_PREVIEW_MAX_BYTES` mirrors the backend's 5,242,880-byte default
   for predictable presentation, but it is a frontend preview policy only.
3. The backend is the artifact hash authority. The browser verifies actual
   bytes and media compatibility but does not reimplement server hashing.
4. Renderer output currently has no CSP meta. The client inserts one into a
   separate preview-only parsed document; the downloadable original is never
   changed.
5. Package ownership is `frontend`. Root Compose and documentation edits are
   derivative build/configuration records and do not change backend behavior.
6. Screen-reader validation uses semantic roles, accessible names, live
   regions, keyboard behavior, and the browser accessibility tree. The project
   has no axe dependency, and this session does not add one solely for a
   redundant test layer.
7. The generated job status has no `review-required` state. This session does
   not invent one; answer-key disclosure is a completed-results presentation.

---

## 9. Security And Privacy Notes

- Owner authorization and missing/foreign indistinguishability remain server
  responsibilities and are preserved by generated client use.
- Result HTML is untrusted even when deterministically rendered. Sanitization,
  CSP, sandboxing, no-referrer, byte/media checks, and cleanup all fail closed.
- External source URLs accept safe HTTP(S) presentation only and receive
  opener/referrer isolation.
- No artifact content, signed path, auth token, or source text is persisted in
  localStorage, URL parameters, logs, analytics, or error copy.
- Copy states current owner-private delivery accurately and avoids formal
  compliance, deletion-timeline, or provider-retention promises.

---

## 10. Completion Gate

The session is complete only after implementation, code review, validation,
PRD/state reconciliation, version synchronization, changelog entry, and a
clean committed/pushed worktree. Phase 04 may then be marked complete.
