# Implementation Summary

**Session ID**:
`phase04-session01-public-landing-intake-and-progress`
**Package**: cross-cutting (`backend`, `backend/packages/txt2crs`, `frontend`)
**Completed**: 2026-07-20
**Duration**: 3.5 hours

---

## Overview

Session 01 delivered the first complete learner-facing vertical slice. A
signed-out visitor now understands the one-source-to-four-publications product
at `/`, can preserve one bounded topic through normal sign-in, and arrives at
a protected `/create` workbench. Authenticated learners can submit prompt,
text, URL, YouTube, PDF, DOCX, or PPTX sources with exact mirrored bounds,
explicit AI/research consent, stable canonical idempotency, and no inactive
source fields.

Accepted work navigates to the server-provided `/jobs/$jobId` owner route.
TanStack Query presents durable checkpoint progress, extraction notes,
reconnection, safe missing/foreign recovery, and completed, failed, or
cancelled outcomes without inventing provider state. The generated client
remains the only frontend transport contract.

A fail-closed deterministic browser composition now exercises normal FastAPI
authentication, real txt2crs persistence, the serial worker, rendering,
restart-safe owner reads, and cleanup without external provider credentials.
Run-owned engine, process, browser-auth, PostgreSQL-user, and temporary state
are removed after both successful and failed scenarios.

---

## Deliverables

### Files Created

| File or Area | Purpose | Lines |
|--------------|---------|-------|
| `backend/tests/browser/` | Isolated deterministic FastAPI lifecycle, production isolation, and cleanup contracts | ~500 |
| `backend/tests/support/deterministic_course.py` | Shared credential-free complete-course scenario used by acceptance and browser composition | ~300 |
| `frontend/src/routes/index.tsx` and `components/Landing/` | Public research-atelier product story and bounded sign-in topic handoff | ~430 |
| `frontend/src/routes/_layout/create.tsx` and `components/CourseIntake/` | Strict multimode source and learning-intent workbench | ~1,000 |
| `frontend/src/routes/_layout/jobs.$jobId.tsx` and `components/CourseProgress/` | Owner-safe progress, warnings, polling, and terminal composition | ~900 |
| Frontend schema, identity, draft, public-setting, and submission modules | Exact request shaping, validated brands, session-only handoff, and canonical single-flight mutation | ~900 |
| `frontend/playwright.jobs.config.ts`, auth teardown, and course journey | Private run orchestration and complete/failed browser acceptance | ~1,050 |
| Session workflow artifacts | Specification, tasks, notes, review, security, validation, and this summary | 7 files |

### Files Modified

| File or Area | Changes |
|--------------|---------|
| Authentication, layout, sidebar, and route tree | Made `/` public, `/create` the protected destination, and `/jobs/$jobId` refresh-safe |
| Frontend validation and branded-type exports | Added exact job bounds and safe job/artifact/idempotency identities |
| Theme tokens and protected UI primitives | Added accessible learner roles, local typography, WCAG AA dark actions, and legible footer metadata |
| Frontend build and Compose settings | Added explicit non-secret signup visibility while keeping backend authorization authoritative |
| Deterministic acceptance support and FastAPI test composition | Shared one validated course scenario and preserved production route isolation |
| Frontend/operator/design documentation and examples | Replaced donor/transitional guidance with the implemented learner workflow |
| Changelog and Apex tracking | Recorded the learner slice, archived completed Phase 02 session artifacts, and advanced Phase 04 to 1/2 |
| Root/package version files and lockfile | Advanced the synchronized project/txt2crs engine release from 0.6.0 to 0.6.1 |

### Files Deleted

| File or Area | Reason |
|--------------|--------|
| `frontend/src/routes/_layout/index.tsx` | Transitional protected overview was replaced by public discovery and focused creation |
| Active Phase 02 session workflow files | Moved byte-for-byte into `.spec_system/archive/sessions/` after phase completion |

---

## Technical Decisions

1. **Generated-client authority**: use generated submission/read services and
   mirrored Zod bounds instead of creating a second request contract.
2. **Canonical single-flight identity**: retain one UUID idempotency key only
   while the canonical draft is unchanged, prevent duplicate pending
   triggers, and rotate after changes or success.
3. **Tab-scoped public handoff**: store only one validated bounded prompt in
   session storage, consume it once, and never put source text in URLs or
   persistent browser storage.
4. **Server-state truth**: map only generated finite job/progress fields and
   safe Problem Details; no hidden review stage, provider guess, or synthetic
   completion percentage enters the UI.
5. **Test-only real composition**: inject a deterministic public engine
   application under `backend/tests/browser/` instead of adding production
   fixture routes or mocking durable HTTP responses.
6. **Run-owned cleanup**: allocate one private fresh root and account per
   Playwright run, reject caller-owned/symlinked state, and erase state through
   normal lifecycle/account APIs.
7. **Accessible semantic color roles**: use luminous green with charcoal text
   for dark primary controls and browser-computed contrast regression rather
   than relying on token names alone.

---

## Test Results

| Metric | Value |
|--------|-------|
| Backend shell | 479 passed |
| Reusable engine | 470 passed; 1 opt-in live test skipped |
| Frontend unit | 97 passed |
| Isolated complete journey | 15 passed; 1 scenario-specific skip |
| Isolated failed journey | 15 passed; 1 scenario-specific skip |
| Broad production browser regression | 66 passed; 7 intentional skips |
| Static quality | Backend/engine Ruff, format, mypy, ty; frontend Biome, TypeScript, and production build passed |
| Generated contract | Reproduced with zero OpenAPI/client base delta |
| Coverage | N/A - authoritative validation commands did not enable coverage |

---

## Review And Validation Repairs

Formal review and validation resolved 0 critical, 2 high, 4 medium, and 2 low
findings:

1. Added the missing public producer for the bounded topic handoff.
2. Made browser state/account/auth ownership private, fresh, and failure-safe.
3. Rendered bounded extraction notes and truthful truncation copy.
4. Covered all seven request families plus warnings, cancellation, and
   reconnection at the browser boundary.
5. Removed 51 pixels of 320px document overflow from the maximum-draft action.
6. Corrected stale design documentation and warning-key/copy details.
7. Added light/dark computed WCAG contrast coverage and repaired dark primary
   actions plus footer metadata.

No review, validation, security, privacy, resource, or generated-contract
blocker remains.

---

## Lessons Learned

1. A persistence consumer is not a feature until its producer and one-time
   lifecycle are proven through the real authentication journey.
2. Browser fixtures need the same explicit ownership model as production
   resources; shared temporary paths and test accounts are hidden global
   state.
3. Generated types prove shape, while rendered browser tests prove that every
   supported source family reaches the serializer with the intended request.
4. Design-token intent does not prove accessibility. Computed colors over
   composed rendered surfaces catch opacity and role conflicts that source
   inspection misses.
5. A deterministic real-facade journey can remain fast and credential-free
   while still proving durable persistence, execution, recovery, and cleanup.

---

## Future Considerations

Items for Session 02:

1. Compose completed result, source, conflict, and artifact-manifest fields
   without exposing private checkpoint or filesystem data.
2. Add four publication cards and private format actions driven only by
   manifest entries.
3. Preview bounded verified HTML in a sandboxed child context; never inject
   artifact markup into the React document.
4. Keep instructor material visually and semantically separate and collapsed
   by default.
5. Preserve the new contrast, resource-cleanup, owner-indistinguishability,
   generated-client, and responsive regressions across the final experience.

---

## Session Statistics

- **Tasks**: 25 completed
- **Runtime/test files created**: 30
- **Implementation files modified**: 40
- **Workflow archive files moved**: 35 byte-identical
- **Tests added**: 47 test declarations plus parameterized cases
- **Blockers**: 0
- **Review/validation findings**: 8 resolved
