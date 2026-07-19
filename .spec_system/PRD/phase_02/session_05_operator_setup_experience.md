# Session 05: Operator Setup Experience

**Session ID**: `phase02-session05-operator-setup-experience`
**Package**: frontend
**Status**: Not Started
**Estimated Tasks**: ~12-25
**Estimated Duration**: 2-4 hours

---

## Objective

Create an accessible operator setup route that presents safe composite
readiness, guides the superuser device-code ceremony, and provides actionable
CLI recovery without exposing credentials or provider internals.

---

## Scope

### In Scope (MVP)

- Protected superuser `/setup` route and navigation entry.
- Safe readiness summary, enabled-input states, warnings, and recovery steps.
- Device login start and bounded status polling using the generated client.
- CLI recovery guidance for unavailable browser authentication.
- Responsive, keyboard, status-announcement, and reduced-motion behavior.

### Out of Scope

- Learner create, progress, results, or library experiences.
- Credential input fields or token display.
- New provider or model selection controls.
- Hosted deployment instructions.

---

## Prerequisites

- [x] Session 04 system routes and generated client are available.
- [ ] Existing frontend authentication and superuser identity are preserved.

---

## Deliverables

1. Component and route tests for readiness and device-login states.
2. Superuser setup route built from existing shadcn/Radix primitives.
3. Query and mutation hooks using generated client contracts.
4. Safe empty, loading, unavailable, busy, expired, success, and error states.
5. Browser validation at the required responsive widths and keyboard flow.

---

## Success Criteria

- [ ] Superusers can start and finish the browser-guided device ceremony.
- [ ] Other authenticated users cannot access operator setup.
- [ ] Readiness communicates why work is unavailable and what an operator can
  safely do next.
- [ ] The UI never displays tokens, filesystem paths, raw provider errors, or
  unbounded diagnostics.
- [ ] Keyboard focus, live status announcements, contrast, and reduced motion
  satisfy the project accessibility contract.
- [ ] Frontend tests, type checks, lint, build, and focused browser checks
  pass.
