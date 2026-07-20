# Session 02: Results, Preview, and Experience Validation

**Session ID**: `phase04-session02-results-preview-and-experience-validation`
**Package**: frontend
**Status**: Not Started
**Estimated Tasks**: ~20-25
**Estimated Duration**: 2-4 hours

---

## Objective

Complete the durable job route as a polished publication workspace with four
distinct results, private artifact access, sandboxed preview, source/conflict
disclosure, and full responsive and accessible experience validation.

---

## Scope

### In Scope (MVP)

- Tests-first completed-result, manifest, download, preview, source, conflict,
  error, and ownership browser scenarios.
- Four publication cards for course, review pack, student assessment, and
  instructor answer key.
- Recommended PDF actions plus accessible HTML, Markdown, PDF, and DOCX format
  menus driven only by manifest entries.
- Bounded sandboxed HTML preview with explicit loading, failure, close, cleanup,
  and navigation protections.
- Source titles, canonical links, retrieval information, truncation, and
  unresolved-conflict disclosure from the public result projection.
- Collapsed-by-default instructor material with clear role separation.
- Cohesive research-atelier art direction across landing, auth, intake,
  progress, results, and existing protected routes.
- Keyboard, focus, status announcement, contrast, reduced-motion, mobile,
  tablet, desktop, zoom, overflow, and route-performance validation.
- Complete frontend, generated-contract, Playwright, and rendered visual QA.

### Out of Scope

- Course editing, quiz player, LMS export, collaboration, grading, public file
  links, or a job library.
- Backend generation, persistence, authorization, or artifact-integrity
  reimplementation.
- Decorative motion that does not clarify product state.

---

## Prerequisites

- [ ] Session 01 validated with durable terminal job state and deterministic
      browser fixtures.
- [ ] The generated manifest and artifact operations remain the only frontend
      delivery contract.

---

## Deliverables

1. Four-publication completed-result composition and safe source/conflict
   disclosure.
2. Private format menus, downloads, and sandboxed bounded HTML preview.
3. Separated instructor answer-key experience.
4. Cohesive responsive and accessible visual system across the learner path.
5. Full unit, Playwright, performance, and rendered-QA evidence.

---

## Success Criteria

- [ ] The real public projection and manifest drive every displayed result,
      source, conflict, format, byte size, and download action.
- [ ] All four publications are distinct and the answer key is visibly marked
      as instructor material.
- [ ] HTML preview cannot execute scripts, navigate the parent, or inject raw
      artifact markup into React; temporary resources are always revoked.
- [ ] Missing, wrong-owner, integrity-failed, transient, and download-error
      paths preserve safe server semantics.
- [ ] The complete journey passes desktop, mobile, keyboard, screen-reader,
      contrast, zoom, overflow, reduced-motion, and route-performance checks.
- [ ] Frontend lint, typecheck, unit tests, production build, full Playwright,
      generated-client determinism, and repository hooks pass.
