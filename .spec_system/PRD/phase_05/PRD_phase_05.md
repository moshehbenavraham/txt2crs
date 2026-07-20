# PRD Phase 05: Hardening and Submission

**Status**: In Progress
**Sessions**: 2 (initial estimate)
**Estimated Duration**: 1-2 days

**Progress**: 1/2 sessions (50%)

---

## Overview

Freeze feature scope, prove a synchronized release candidate under
deterministic and production-like conditions, complete one synthetic
representative GPT-5.6 plus Tavily course, finish every tracked judge-facing
OpenAI/Devpost asset, and only then publish the exact final release submitted
to judges. This phase adds no P1 product feature and does not introduce hosted
deployment.

---

## Progress Tracker

| Session | Name | Status | Est. Tasks | Validated |
|---------|------|--------|------------|-----------|
| 01 | Release Hardening and Live Proof | Complete | 25 | 2026-07-20 |
| 02 | Submission Assets and Devpost | Not Started | ~20-25 | - |

---

## Completed Sessions

- Session 01: Release Hardening and Live Proof - completed 2026-07-20.

---

## Upcoming Sessions

- Session 02: Submission Assets and Devpost

---

## Objectives

1. Reproduce all deterministic, evaluation, distribution, image, persistence,
   and browser gates from the exact release revision.
2. Complete and inspect one synthetic representative GPT-5.6 plus Tavily job
   with all 16 private artifacts and redacted operational evidence.
3. Synchronize and build a `1.0.0` release candidate, then tag and push the
   exact final judge-asset revision without publishing packages or deploying a
   hosted environment.
4. Finish the judge README, sample evidence, license/access check, Codex
   feedback Session ID, public sub-three-minute video, Education-category
   Devpost fields, and confirmed submission receipt.

---

## Prerequisites

- Phase 04 completed with both learner-experience sessions validated.
- Phase 04 transition audit, pipeline fallback, infrastructure, carryforward,
  and documentation gates passed.
- The live-only proof uses one operator-controlled ChatGPT identity and a
  Tavily credential supplied through private runtime configuration.

---

## Planning Assumptions And Resolutions

### Working Assumptions

- **Local Docker remains the complete target**: ADR-0008, the master PRD, and
  validated infrastructure all define repository-root Docker Compose as the
  release, demo, and judge execution path. Phase 05 does not add hosting.
- **Live evidence uses synthetic content**: The cumulative GDPR record still
  lacks formal legal-basis, provider-transfer, retention, backup-erasure, and
  provider-copy decisions. The representative course therefore uses no real
  learner personal data and the submission states the current limits without
  claiming compliance.
- **Remote CI has an exact local fallback**: GitHub Actions billing currently
  rejects jobs before scheduling. Session 01 repeats every executable
  workflow equivalent locally, preserves the remote CodeQL exception, and
  does not misrepresent the hosted checks as green.
- **The final version is `1.0.0`**: `0.7.0` is the current synchronized
  release and `docs/VERSIONING.md` reserves `1.0.0` for the first stable
  public API. Phases 00-04 delivered and validated that public boundary, so
  Session 01 synchronizes the `1.0.0` release candidate and Session 02 creates
  the final immutable tag after tracked judge assets are complete.

### Conflict Resolutions

- **Source-plan S09/S10 versus phase-local numbering**: The implementation
  plan labels the final work S09 and S10 across the whole product. Apex state
  and every existing phase use phase-local session numbers. Those scopes map
  to Phase 05 Session 01 and Session 02 without changing their order.
- **Unchecked legacy definition-of-done rows versus completed state**:
  Validated session summaries and state tracking prove Phases 00-04 complete,
  while the older master-plan checklist still contains unchecked implemented
  items. Phase 05 verifies those contracts from a clean revision; it does not
  reopen them as new feature work.
- **Final tag follows tracked submission assets**: The source implementation
  plan orders the judge README before release, but the initial phase stubs put
  the tag in Session 01 and tracked assets in Session 02. Session 01 now
  produces the tested candidate; Session 02 completes repository assets,
  repeats the immutable release checks, and tags that exact commit. No tracked
  change may follow the final tag without a new version.

---

## Technical Considerations

### Architecture

- Keep the public engine facade, generated OpenAPI client, single-process
  serial worker, owner-hidden reads, verified artifact delivery, and sandboxed
  preview boundaries unchanged during the feature freeze.
- Candidate evidence must identify one tested revision, one synchronized
  SemVer value, and matching Python distributions and Docker images. The final
  Session 02 ledger adds the exact annotated tag after judge assets are
  complete and revalidated.
- Live evidence is redacted and path-free. It may record finite model,
  research, artifact, timing, and validation facts but never credentials,
  provider payloads, prompts, private paths, or artifact bodies in logs.
- Submission assets link to sources of truth rather than duplicating mutable
  setup, architecture, privacy, or testing instructions.

### Technologies

- Python 3.14, uv, pytest, fixed engine evaluations, and package build tooling
- React 19, Vitest, TypeScript, Vite, and Playwright
- Docker Compose, production backend/frontend images, PostgreSQL 18, and
  private engine state
- Git, GitHub release-validation workflow, annotated tags, YouTube, Codex
  feedback, and Devpost

### Risks

- **Deadline compression**: Freeze P0 behavior and prioritize release
  integrity, the representative proof, video, and confirmed submission over
  polish or any P1 feature.
- **External authentication**: Keep deterministic gates credential-free; use
  private operator credentials only for the isolated live proof and platform
  submission actions.
- **Submission drift**: Recheck commit, tag, version, sample, video copy, and
  Devpost links immediately before final submission.
- **Remote CI billing**: Preserve exact local workflow evidence and disclose
  the remote CodeQL exception until billing is restored.
- **Privacy overclaim**: Use synthetic demo data and current documented
  limitations; do not invent a legal basis, retention promise, provider
  deletion guarantee, or regulatory status.

### Relevant Considerations

- [P01-backend/packages/txt2crs] **Credentialed provider proof is still
  gated**: Session 01 owns the one required GPT-5.6 plus Tavily course.
- [P01-backend/packages/txt2crs] **Private-state retention is undefined**:
  Live input remains synthetic and submission copy links to current privacy
  limitations rather than claiming policy-complete erasure.
- [P00] **GitHub Actions billing is disabled**: Every local equivalent remains
  mandatory, and remote CodeQL stays explicitly unresolved.
- [P00] **Deployment is intentionally local-only**: Release validation builds
  images but never adds hosted CD.
- [P04-frontend] **Artifact preview needs independent barriers**: Release
  changes preserve transfer verification, inert parsing, CSP, empty sandbox,
  and temporary URL cleanup.

---

## Success Criteria

Phase complete when:

- [ ] Both sessions are completed and validated.
- [ ] The exact release revision passes clean deterministic package,
      acceptance, browser, evaluation, distribution, and production-image
      gates.
- [ ] Container replacement preserves authentication, job state, and private
      artifacts under the documented one-process topology.
- [ ] One synthetic live GPT-5.6 plus Tavily course completes and all 16
      artifacts pass recorded human inspection for alignment, citations,
      formatting, and answer separation.
- [ ] Logs, browser/network evidence, release artifacts, and submission
      materials contain no secret or private implementation data.
- [ ] The selected final SemVer is synchronized and built as a release
      candidate, then the complete judge-asset revision is revalidated,
      committed, annotated as the exact matching tag, and pushed.
- [ ] The root README, sample, AI-usage explanation, privacy/limits,
      architecture, setup, and test instructions are judge-ready.
- [ ] Repository license and judge access are verified without inventing a
      CODEOWNERS or security-contact decision.
- [ ] A narrated public YouTube demo under three minutes explains the product,
      Codex development work, and GPT-5.6 runtime.
- [ ] The primary Codex feedback Session ID, Education-category Devpost fields,
      exact release link, and submission receipt are recorded before
      2026-07-22 00:00 UTC.

---

## Dependencies

### Depends On

- Phase 04: Learner Experience

### Enables

- Post-submission P1 work only after the Devpost receipt is confirmed.
