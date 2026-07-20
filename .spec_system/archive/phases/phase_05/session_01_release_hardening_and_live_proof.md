# Session 01: Release Hardening and Live Proof

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Packages**: backend/packages/txt2crs, backend, frontend
**Status**: Complete
**Estimated Tasks**: ~20-25
**Estimated Duration**: 2-4 hours

---

## Objective

Prove one exact feature-frozen revision through clean deterministic,
evaluation, distribution, production-image, persistence, and synthetic live
GPT-5.6 plus Tavily evidence, then prepare its synchronized `1.0.0`
release-candidate commit for the final judge-asset and tag gate.

---

## Scope

### In Scope (MVP)

- Tests-first release-contract checks for version, artifact, image, sample,
  evidence, and tag synchronization.
- Clean-checkout execution of engine, backend, frontend, generated-contract,
  acceptance, browser, workflow-security, and fixed evaluation gates.
- Production Compose startup, health, one-process/non-root checks, and
  authentication/job/artifact persistence across container replacement.
- One synthetic representative course through the real GPT-5.6 and Tavily
  runtime with the exact configured model and no fallback.
- Human inspection ledger for all 16 live artifacts: alignment, citations,
  formatting, assessment/answer separation, integrity, and private access.
- Redacted logs/browser/network/resource inspection and a deterministic sample
  plus redacted live-demo evidence.
- `1.0.0` version selection, synchronized version/changelog/lockfile metadata,
  Python distribution and image builds, and an exact tested candidate commit.
- Exact local fallbacks for billing-blocked GitHub jobs and preservation of the
  remote CodeQL known issue.

### Out of Scope

- New learner features, P1 modes, model/provider selection, or behavior
  changes unrelated to a release-blocking defect.
- Hosted deployment, public domains, package publication, or GitHub Release
  creation.
- Final annotated tag creation; Session 02 must first complete tracked judge
  assets and rerun the immutable release checks on the exact tagged commit.
- Real learner personal data or unredacted provider/runtime evidence.

---

## Prerequisites

- [x] Phase 04 learner and transition gates remain green at the selected base.
- [x] The operator-controlled ChatGPT identity and Tavily credential are
      available only to the explicit live-proof process.
- [x] The working tree can be reduced to one intentional release scope before
      the final clean-checkout proof.

---

## Deliverables

1. Reproducible clean-checkout release and production-smoke evidence.
2. One completed synthetic live course plus a 16-artifact inspection ledger
   and redacted demo sample.
3. Secret/privacy/resource audit for logs, browser traffic, processes, and
   generated evidence.
4. Synchronized `1.0.0` candidate version, changelog, distributions, image
   inspection, exact tested commit, and handoff requirements for the final tag.

---

## Success Criteria

- [x] Every deterministic, fixed-evaluation, generated-client, production
      image, Compose, browser, and workflow-safety gate passes from the exact
      release revision.
- [x] Backend/frontend replacement preserves the expected durable stores and
      returns both services to healthy.
- [x] The live system discovers and uses GPT-5.6, completes Tavily research
      before drafting, and produces exactly 16 owner-private verified
      artifacts.
- [x] All live publications pass the recorded human quality and answer-
      separation inspection with no secret, prompt, path, provider payload, or
      raw artifact body in evidence logs.
- [x] Root/package versions, lockfile, changelog, distributions, images, and
      candidate commit all identify `1.0.0`; the handoff states the exact
      checks Session 02 must repeat before tagging.
- [x] Any GitHub-hosted failure is proven to be the existing zero-step billing
      condition and has a passing exact local equivalent where one exists.
