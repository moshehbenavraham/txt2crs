# Session 01: Public Landing, Intake, and Progress

**Session ID**: `phase04-session01-public-landing-intake-and-progress`
**Packages**: frontend, backend
**Status**: Complete
**Estimated Tasks**: ~20-25
**Estimated Duration**: 2-4 hours

---

## Objective

Ship the truthful learner journey from public discovery through authenticated,
idempotent multimode submission and refresh-safe durable progress, backed by a
credential-free browser harness that exercises the real shell/package
boundaries.

---

## Scope

### In Scope (MVP)

- Tests-first deterministic FastAPI/browser fixture with no provider or
  network requirement and no non-test exposure.
- Public `/` landing page and safe sign-in/create handoff.
- Authenticated `/create` route and preserved drafted prompt when practical.
- Configuration-accurate signup visibility and invite-only judge/demo copy.
- Central Zod request schemas and branded job/artifact/idempotency identifiers.
- Prompt, text, URL, YouTube, PDF, DOCX, and PPTX intake with bounded local
  preview and the exact generated client operations.
- Stable per-draft idempotency, repeat-click prevention, and safe Problem
  Details handling.
- Owner job route with checkpoint-derived progress, revision-aware polling,
  transient reconnect/backoff, extraction warnings, and safe terminal states.
- Refresh, direct-link, auth, ownership, failure, responsive, and
  reduced-motion browser coverage for this slice.

### Out of Scope

- Artifact manifest menus, downloads, HTML preview, and complete results
  composition; Session 02 owns them.
- Job library, cancellation API, per-job deletion, email outbox, or new input
  modes.
- Provider/model controls, hidden policy detail, or hosted deployment.

---

## Prerequisites

- [ ] Phase 03 transition, generated jobs client, and full validation remain
      green.
- [ ] Existing authentication/session and setup flows are characterized before
      route restructuring.

---

## Deliverables

1. Deterministic end-to-end browser fixture through public application
   boundaries.
2. Public landing and authenticated creation route with correct access policy.
3. Strict multimode intake and idempotent generated-client submission.
4. Durable progress route with bounded polling and complete safe states.
5. Unit and Playwright evidence for refresh, failure, ownership, accessibility,
   responsive layout, and reduced motion.

---

## Success Criteria

- [ ] A signed-out visitor reaches a truthful product story without entering
      the protected shell.
- [ ] An authenticated user can submit every enabled P0 mode once and lands on
      the durable server-provided status URL.
- [ ] Double-click and exact retry behavior preserve one request key and do not
      create duplicate work.
- [ ] Job progress survives refresh, stops polling at terminal state, and never
      invents provider work.
- [ ] The deterministic browser suite requires no ChatGPT, Tavily, or external
      network access and does not bypass persistence with route-only mocks.
- [ ] Auth, privacy, mobile, keyboard, and reduced-motion checks pass without
      regressing `/setup`, settings, or administration.
