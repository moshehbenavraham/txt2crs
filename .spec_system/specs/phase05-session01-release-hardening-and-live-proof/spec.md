# Session Specification

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Phase**: 05 - Hardening and Submission
**Status**: Planned
**Created**: 2026-07-20
**Base Commit**: 875808005a011a6a23538fa903805d0719463ccd
**Package**: null
**Package Stack**: Mixed Python 3.14/FastAPI/txt2crs and React 19/TypeScript

---

## 1. Session Overview

This session freezes product behavior and proves a synchronized `1.0.0`
release candidate. It repeats the deterministic package, evaluation, browser,
distribution, production-image, and replacement-persistence gates from one
exact revision. It then completes one synthetic course through the real
ChatGPT subscription GPT-5.6 runtime and real Tavily research boundary,
inspects all sixteen private artifacts, and records only bounded public-safe
evidence.

The source implementation plan places the judge README before the final
release. The initial Phase 05 stubs placed the tag in Session 01 even though
Session 02 still changes tracked judge assets. That would make the submitted
commit diverge from the tag. This session therefore produces the tested
candidate and an explicit final-tag handoff. Session 02 completes tracked
assets, reruns the immutable release checks, and creates `v1.0.0` on that exact
commit. No final tag is created here.

The reusable engine remains the sole owner of provider orchestration,
research, checkpoints, artifacts, validation, and rendering. Release tooling
may inspect public contracts and generated evidence, but it must not duplicate
engine behavior or expose prompts, provider payloads, credentials, paths,
artifact bodies, or real learner data.

---

## 2. Objectives

1. Add tests-first, deterministic release-contract and evidence validation
   that prevents version, revision, artifact-count, checksum, and privacy
   drift.
2. Synchronize the stable public release candidate to `1.0.0` across every
   declared version, lockfile, changelog, distribution, image, and evidence
   surface.
3. Reproduce every locally executable quality, security, evaluation, browser,
   Docker, persistence, and resource-safety gate from the exact candidate.
4. Complete one synthetic real GPT-5.6 plus Tavily course and inspect all
   sixteen owner-private artifacts for alignment, citations, formatting, and
   assessment/answer separation.
5. Produce a public-safe deterministic sample, redacted live-proof ledger,
   and exact Session 02 final-tag revalidation handoff.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase04-session01-public-landing-intake-and-progress` - durable learner
      intake, progress, and deterministic end-to-end generation.
- [x] `phase04-session02-results-preview-and-experience-validation` - private
      four-publication results, sixteen artifacts, downloads, and sandboxed
      preview.
- [x] Phase 04 transition gates - audit, local workflow fallback,
      infrastructure replacement/backup proof, carryforward, and docs audit.

### Required Tools Or Knowledge

- Root `VERSION`, engine package metadata, `backend/uv.lock`, changelog, and
  annotated-tag conventions from `docs/VERSIONING.md`.
- Engine acceptance marker, system-auth CLI, GPT-5.6 fail-closed policy,
  Tavily MCP configuration, public facade, and owner-private artifact manifest.
- Existing Docker Compose smoke/rollback/backup helpers, Playwright job
  fixture, fixed evaluation corpus, and billing-blocked GitHub workflow record.

### Environment Requirements

- Installed backend uv workspace and frontend npm dependencies.
- Docker Engine/Compose with enough local disk and memory for clean production
  image builds and isolated PostgreSQL/private-state volumes.
- Private operator-controlled ChatGPT state and Tavily credential available
  only to the explicit live-proof process. Their presence is checked without
  printing values.
- Synthetic, nonpersonal live input. No real learner personal data is allowed.

---

## 4. Scope

### In Scope (MVP)

- A small standard-library release evidence validator with tests for the
  synchronized version, candidate commit, checksums, sixteen-artifact ledger,
  redaction rules, deterministic serialization, and final-tag handoff.
- Static release-workflow contract coverage so the hosted tag workflow uses
  the same validator and remains read-only, pinned, local-only, and
  nonpublishing.
- `1.0.0` synchronization in root/package metadata, uv lock, versioning docs,
  changelog, plan status text, and evidence; no frontend package version is
  invented where none exists.
- Clean candidate execution of engine, backend, frontend, generated-client,
  fixed evaluation, acceptance, Playwright, distribution, image, Compose,
  workflow-security, documentation-link, and hook checks.
- Production one-process/non-root/health inspection and backend/frontend
  replacement while preserving PostgreSQL identity, engine SQLite state, and
  private artifacts.
- One representative real course with an explicit GPT-5.6 model, real Tavily
  research before drafting, four deliverables, sixteen artifacts, and bounded
  source/conflict disclosure.
- Human inspection of every live HTML, Markdown, PDF, and DOCX artifact for
  deliverable alignment, citation usability, rendering, answer separation,
  integrity, and private access.
- Public-safe deterministic sample and live evidence containing hashes,
  counts, finite model/research facts, pass/fail judgments, and revision
  identity only.
- Exact local equivalents for billing-blocked workflows and explicit retention
  of the unresolved remote CodeQL finding.

### Out Of Scope (Deferred)

- New learner features, P1 inputs, model/provider selection, queueing,
  collaboration, hosted deployment, public domains, or runtime redesign.
- Package publication, GitHub Release creation, Devpost submission, YouTube
  publication, or the final annotated tag; Session 02 owns those final actions.
- Real personal data, public artifact URLs, raw course bodies in evidence,
  provider payloads, prompts, credentials, local absolute paths, tokens, or
  invented GDPR/compliance claims.
- Treating GitHub jobs rejected before scheduling as passing or claiming
  remote CodeQL coverage without a completed run.

---

## 5. Technical Approach

### Architecture

Add `scripts/release_evidence.py` as a deterministic, standard-library
boundary for release identity and public evidence. Its input is an explicit
bounded document assembled from already-authoritative outputs; it does not
open engine databases, call providers, read credentials, or render artifacts.
The validator confirms SemVer/package/lock/changelog agreement, exact Git
revision shape, expected distribution/image checksums, exactly four
deliverables by four formats, reviewed inspection outcomes, and a public-safe
field allowlist. It writes canonical JSON only to a caller-selected public
path and rejects absolute paths, secret-like fields, prompt/provider payload
fields, emails, and artifact bodies.

Backend script tests own the repository-wide release contract because the
existing container/workflow tests already inspect root operational files from
`backend/tests/scripts/`. The release workflow calls the tested validator
instead of maintaining a second inline version rule. Candidate mode requires
no tag; final mode, exercised deterministically in tests and used by Session
02, requires `v<version>` to match the exact revision.

The real live course runs through the normal application/facade boundary in an
isolated local Compose project or test-owned engine state. The operator
credential directories and Tavily key remain private runtime inputs. Public
evidence is derived from owner-scoped status, result, manifest, verified
downloads, finite safe runtime events, hashes, and manual inspection
judgments. Artifact content is inspected locally but never copied wholesale
into logs or release evidence.

`docs/release/README_release.md` becomes the release-evidence index. It links
the deterministic sample, candidate ledger, and artifact inspection record,
states the local-only deployment and remote-CodeQL exception, and defines the
small exact check set Session 02 must repeat after its final tracked edits.

### Release Identity

- Candidate version: `1.0.0`, because `docs/VERSIONING.md` reserves it for the
  first stable public API and Phases 00-04 validated that API.
- Candidate base: this session's final clean commit, recorded after
  implementation and validation.
- Final identity: a later Session 02 commit containing all tracked judge
  assets, revalidated and annotated as `v1.0.0`.
- Immutability rule: no tracked change may follow `v1.0.0`; any necessary
  tracked correction requires a new SemVer release.

### Evidence And Privacy Rules

- Synthetic input only; evidence stores no name, email, account ID, raw input,
  prompt, provider response, token details, filesystem path, or credential.
- Candidate JSON stores finite identifiers, hashes, counts, sizes, durations,
  test summaries, model family, research-used boolean, and inspection status.
- The human ledger may name deliverable/format pairs and findings, but it does
  not embed artifact bodies or unrestricted private links.
- Private temporary state and backups use owner-only permissions and are
  removed after evidence is safely derived.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `scripts/release_evidence.py` | Canonical candidate/final release identity and public-safe evidence validation | ~260 |
| `backend/tests/scripts/test_release_evidence.py` | Version, checksum, artifact-count, redaction, serialization, and tag-mode tests | ~300 |
| `backend/tests/scripts/test_release_workflow_contract.py` | Static tag-workflow safety and validator-integration contract | ~150 |
| `docs/release/README_release.md` | Judge-facing release evidence index and final-tag handoff | ~140 |
| `docs/release/RELEASE_CANDIDATE_1_0_0.json` | Canonical redacted candidate ledger | generated |
| `docs/release/ARTIFACT_INSPECTION_1_0_0.md` | Sixteen-artifact human inspection ledger | ~180 |
| `docs/release/DETERMINISTIC_SAMPLE_1_0_0.md` | Public-safe representative deterministic sample | ~180 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `.github/workflows/release.yml` | Reuse the tested validator for candidate/final identity and preserve read-only artifact build | ~35 |
| `.gitignore` | Exclude private live inputs, provider state, raw downloads, and transient evidence workspaces | ~15 |
| `VERSION` | Set stable candidate version to `1.0.0` | 1 |
| `backend/packages/txt2crs/pyproject.toml` | Synchronize Python package version | 1 |
| `backend/uv.lock` | Regenerate workspace lock metadata | generated |
| `docs/VERSIONING.md` | Record `1.0.0` current stage and final-tag ordering | ~20 |
| `docs/CHANGELOG.md` | Promote release changes to the dated `1.0.0` heading | ~30 |
| `backend/packages/txt2crs/tests/acceptance/README_acceptance.md` | Document representative full-course live gate separately from the small MCP probe | ~35 |
| `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` | Reconcile verified P0 rows and candidate/final tag sequencing | ~30 |
| `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md` | Exact commands, results, exceptions, live proof, privacy audit, and handoff | ~300 |

---

## 7. Success Criteria

### Release Contract

- [ ] Tests fail before implementation for version drift, malformed hashes,
      artifact-count drift, unreviewed artifacts, unsafe evidence fields,
      nondeterministic output, candidate tags, and mismatched final tags.
- [ ] `VERSION`, engine metadata, lockfile, versioning docs, changelog,
      distributions, images, and candidate evidence all identify `1.0.0`.
- [ ] The release workflow is read-only, action-pinned, nonpublishing,
      local-deployment-only, and calls the same tested validator.

### Deterministic And Production Proof

- [ ] Clean engine, backend, frontend, generated-client, fixed-evaluation,
      acceptance, Playwright, hooks, security, distribution, and documentation
      checks pass on the exact candidate.
- [ ] Production images run non-root with one FastAPI process and healthy
      backend/frontend services.
- [ ] Replacing the application tier preserves the PostgreSQL identity,
      engine job/checkpoint state, and verified private artifacts.

### Live Proof

- [ ] One synthetic job discovers and uses GPT-5.6 with no fallback, performs
      real Tavily research before drafting, and completes four deliverables
      with exactly sixteen owner-private artifacts.
- [ ] Every deliverable/format pair passes recorded alignment, citation,
      formatting, integrity, private-access, and answer-separation review.
- [ ] Logs, browser/network traces, process/listener state, public evidence,
      and Git diff contain no secret, prompt, provider payload, raw artifact
      body, private identifier, or local path.

### Handoff

- [ ] The deterministic sample and redacted candidate/live ledgers are
      reproducible and judge-safe.
- [ ] Implementation notes record exact candidate revision, commands,
      distribution/image hashes, remote workflow billing exception, live
      inspection result, and resource cleanup.
- [ ] Session 02 receives an explicit minimal revalidation list and creates the
      final tag only after all tracked judge assets are complete.

---

## 8. Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| Live credentials are absent or expired | Check presence without values, use the packaged device-auth flow, keep deterministic gates independent, and record a real blocker rather than fabricating proof |
| Provider latency or quota consumes the deadline | Use one bounded synthetic course, finite timeouts, one active worker, checkpoint recovery, and no exploratory duplicate jobs |
| Evidence leaks private data | Generate from an allowlisted schema, reject risky keys/patterns, inspect the staged diff, and keep raw downloads/state ignored and owner-only |
| Final tag drifts from submission docs | Do not tag in this session; Session 02 commits tracked assets, repeats immutable checks, then tags the exact final commit |
| GitHub Actions remain unschedulable | Record zero-step billing failures, execute every local equivalent, and retain remote CodeQL as an unresolved low finding |
| Release-only fixes change behavior | Accept only release-blocking defects, write the regression first, rerun the full matrix, and document any scope correction |

---

## 9. Session Handoff

After implementation, run the Apex `creview`, `validate`, and `updateprd`
workflow sequence. Session 01 is complete only after those gates pass and the
candidate commit is exact and clean. The next planned session is
`phase05-session02-submission-assets-and-devpost`; it owns tracked judge assets,
final revalidation, branch/tag push, video, feedback, Devpost submission, and
the receipt.
