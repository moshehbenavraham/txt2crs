# Session 03: Input Preferences and Policy Gate

**Session ID**: `phase01-session03-input-preferences-and-policy-gate`
**Package**: backend/packages/txt2crs
**Status**: Not Started
**Estimated Tasks**: ~20-25
**Estimated Duration**: 2-4 hours

---

## Objective

Prepare each accepted input once, resolve enforceable learning preferences,
and complete post-ingestion policy before any research or Codex resource
starts.

---

## Scope

### In Scope (MVP)

- A package-owned routing URL adapter for YouTube and general public URLs.
- Deterministic language detection with the documented English fallback.
- Auto and explicit level, audience, prior knowledge, learning goals, and P0
  server-default resolution.
- Explicit learning-contract level and learning-goal fields.
- Curriculum shape limits and local course-plan preference/alignment checks.
- Accepted resolved-preference checkpointing before module drafting.
- Provider-free bounded ingestion and cumulative input-document checkpointing.
- Submission preflight plus post-ingestion content-policy decisions.
- Safe terminal rejection/review behavior with no provider calls.
- Recovery reuse of prepared content, policy decision, and preferences without
  refetching or reinterpretation.

### Out of Scope

- Managed research MCP startup and Codex model discovery.
- FastAPI multipart transport validation and HTTP error mapping.
- UI preference controls.

---

## Prerequisites

- [ ] Session 01 exact request and recovery contracts are validated.
- [ ] Existing ingestion adapters, course-planning schemas, and policy tests
  are green before changes.

---

## Deliverables

1. Routing URL adapter and deterministic dispatch tests.
2. Preference intent resolution, learning-contract, and curriculum-shape
   validation contracts.
3. Provider-free preparation and two-stage policy pipeline.
4. Checkpoint and recovery coverage for prepared documents, policy decisions,
   and resolved preferences.

---

## Success Criteria

- [ ] Recognized YouTube hosts use transcript ingestion and other approved
  public URLs use general URL ingestion after one authoritative validation.
- [ ] Every P0 preference is enforced or resolved deterministically; no
  client-visible field is inert.
- [ ] Course plans outside shape, level, audience, language, accessibility, or
  learning-goal alignment rules do not reach module drafting.
- [ ] Binary, fetched, and transcript content is evaluated after bounded
  ingestion and before any research or Codex call.
- [ ] Recovery reuses the accepted prepared checkpoint without refetching or
  applying new defaults.
