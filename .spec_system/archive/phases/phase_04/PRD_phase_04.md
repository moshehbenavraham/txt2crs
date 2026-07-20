# PRD Phase 04: Learner Experience

**Status**: Complete
**Sessions**: 2 (initial estimate)
**Estimated Duration**: 1-2 days

**Progress**: 2/2 sessions (100%)

---

## Overview

Connect the generated jobs client to a complete, truthful learner journey:
public product discovery, authenticated multimode intake, refresh-safe progress,
four publication-focused results, private artifact access, and accessible
responsive presentation. Every visible state comes from the durable Phase 03
API or an explicitly local form state.

---

## Progress Tracker

| Session | Name | Status | Est. Tasks | Validated |
|---------|------|--------|------------|-----------|
| 01 | Public Landing, Intake, and Progress | Complete | 25 | 2026-07-20 |
| 02 | Results, Preview, and Experience Validation | Complete | 25 | 2026-07-20 |

---

## Completed Sessions

- Session 01: Public Landing, Intake, and Progress - completed 2026-07-20.
- Session 02: Results, Preview, and Experience Validation - completed
  2026-07-20.

---

## Upcoming Sessions

- None - Phase 04 is complete.

---

## Objectives

1. Split public product discovery from the authenticated `/create` workspace
   and preserve safe authentication handoff.
2. Submit every enabled P0 input through strict centralized schemas, generated
   client operations, and owner-scoped idempotency.
3. Present durable checkpoint-derived progress and safe terminal or
   reconnecting states on a refresh-stable job URL.
4. Present four distinct publications with private downloads, sandboxed HTML
   preview, source/conflict disclosure, and separated instructor material.
5. Validate the complete journey across keyboard, screen reader, reduced
   motion, contrast, mobile, desktop, failure, refresh, and ownership states.

---

## Prerequisites

- Phase 03 complete with durable submission, owner-scoped status/result,
  manifest, artifact, recovery, and account-erasure acceptance coverage.
- Generated frontend client contains the current Phase 03 jobs contract.
- Donor Item routes, components, schemas, and generated operations are absent.

---

## Planning Assumptions And Resolutions

### Working Assumptions

- The two-session split from the product plan remains viable because Phase 03
  already delivered the complete HTTP contract and the transition audit
  removed donor UI. Session 01 owns the journey through durable terminal job
  state; Session 02 owns publication delivery and complete experience quality.
- Credential-free browser tests need a deterministic harness through normal
  FastAPI and public package boundaries. Session 01 may add test-only shell
  composition, but it must fail closed outside explicit test execution and
  must not become a public development API or a route-only persistence mock.
- The Phase 03 static root is transitional content, not a competing product
  route. Its verified four-publication copy and visual primitives can move
  into the public landing page while authenticated creation moves to
  `/create`, as the product plan requires.

### Conflict Resolutions

- The original Phase 04 work list still includes donor Item removal, while the
  completed Phase 03 transition already removed backend, generated, and
  frontend donor surfaces. Validated repository state wins: Phase 04 verifies
  continued absence and adds no compatibility shim.
- The source plan describes a browser-visible `review-required` state, while
  the durable public contract may expose only its existing finite status and
  safe failure projection. The UI maps only generated contract values and
  safe server messages; it does not invent a hidden provider or policy state.

---

## Technical Considerations

### Architecture

- Frontend code consumes generated `JobsService` operations; it never
  reconstructs backend request or response contracts.
- TanStack Query owns server state and bounded polling. Route parameters and
  durable revisions, not component-local timers, determine re-entry behavior.
- FastAPI and the public `txt2crs` package boundary remain the only owners of
  authorization, policy, admission, persistence, recovery, and integrity.
- HTML preview uses a sandboxed child browsing context and bounded verified
  bytes. Artifact markup is never injected into the React document.
- Wrong-owner and missing resources keep the same server-provided 404
  treatment. The browser must not add existence probes or leak private detail.

### Technologies

- React 19, TypeScript, TanStack Router and Query
- React Hook Form, Zod, generated OpenAPI client
- Tailwind CSS 4, shadcn/Radix, current editorial design tokens
- Vitest and Playwright, with accessibility tooling where required

### Risks

- **Polling drift**: Poll only non-terminal generated states, compare durable
  revisions, back off transient failures, and stop immediately at terminal
  state.
- **Duplicate paid work**: Generate one key per draft, disable repeated
  submission, and reuse the same key only for an exact transport retry.
- **Unsafe preview**: Enforce response size/type before creating a sandboxed
  preview and revoke every temporary object URL.
- **Privacy regression**: Render only public projection fields and safe
  Problem Details; never log or display source bodies, provider data, paths,
  tokens, artifact bytes, or account credentials.
- **Deadline compression**: Preserve the end-to-end journey, privacy,
  accessibility, and deterministic tests; defer decorative motion before any
  product or safety contract.

### Relevant Considerations

- [P03-frontend+backend] **The learner workspace needs real job integration**:
  Replace the static overview with generated-client submission, status,
  manifest, and download composition without reintroducing donor abstractions.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**:
  Never edit generated files or create a parallel fetch contract.
- [P03-backend+backend/packages/txt2crs] **Job HTTP routes use public handles**:
  Preserve durable admission, owner-hidden reads, constructed allowlists, and
  private response behavior.
- [P02-backend+frontend] **Authorization and polling follow server state**:
  Run guards before queries, poll only waiting states, and react to genuine
  transitions instead of StrictMode mounts.
- [P00-frontend] **Rendered QA complements source checks**: Inspect the real
  browser at target widths, themes, keyboard, and reduced-motion settings.
- [P01-backend/packages/txt2crs] **Private-state retention is undefined**:
  Do not claim policy-complete erasure or retention in learner-facing copy.

---

## Success Criteria

Phase complete when:

- [x] Both sessions are completed and validated.
- [x] Signed-out visitors can understand the product and reach the configured
      access path; authenticated users create work at `/create`.
- [x] Every enabled input mode submits through mirrored Zod rules, a stable
      idempotency key, and the generated client.
- [x] `/jobs/$jobId` is refresh-safe and renders only checkpoint-derived
      progress, safe reconnect/failure states, and terminal server results.
- [x] All four publications and enabled private formats are accessible, HTML
      preview is sandboxed, and instructor material is clearly separated.
- [x] No raw artifact HTML enters the React document and no private server
      field or ownership oracle is introduced.
- [x] Desktop, mobile, keyboard, screen-reader, contrast, reduced-motion, and
      route-performance gates pass.
- [x] Frontend unit/build/lint/type checks, full Playwright, backend fixture
      checks, generated-client determinism, and repository hooks pass.

---

## Dependencies

### Depends On

- Phase 03: Durable Jobs API

### Enables

- Phase 05: Hardening and Submission
