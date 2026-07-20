# Implementation Notes

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Package**: null (cross-cutting)
**Started**: 2026-07-20 09:13 IDT
**Last Updated**: 2026-07-20 10:21 IDT

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 19 / 25 |
| Estimated Remaining | 1-2 hours plus external live prerequisites |
| Blockers | Tavily credential and GPT-5.6 entitlement; deterministic work continues |

---

## Task Log

### Task T020 - Run Focused Release Gates

**Started**: 2026-07-20 10:20 IDT
**Completed**: 2026-07-20 10:21 IDT
**Duration**: 1 minute

**Notes**:
- Re-ran release identity/privacy/canonicalization and both quality/security
  workflow contracts. The test fixture writes the same canonical candidate
  twice and requires byte identity.
- Repeated real repository candidate-version validation twice. The public
  candidate ledger remains deliberately absent because T017-T019 are not
  complete; T024, not this validator test, owns its final generation.

**Files Changed**:
- No tracked product file changed.

**Verification**:
- Command/check: focused shell release/workflow pytest and Ruff
  - Result: PASS - 32 tests; 4 files linted/formatted.
- Command/check: engine metadata, Ruff, and mypy
  - Result: PASS - 2 package metadata tests; 138-source mypy graph; Ruff.
- Command/check: repeated repository candidate CLI
  - Result: PASS - both byte-identical outputs report
    `release-version=1.0.0`.
- UI product-surface check: N/A.
- UI craft check: N/A.

**BQC Fixes**:
- Evidence honesty: deterministic canonicalization is proven without writing
  an incomplete public live ledger.

### Task T023 - Run Workflow And Security Equivalents

**Started**: 2026-07-20 10:16 IDT
**Completed**: 2026-07-20 10:20 IDT
**Duration**: 4 minutes

**Notes**:
- Ran every locally executable quality, workflow, dependency, secret, text,
  generated-file, and diff check. Remote Actions remains a zero-step billing
  condition and CodeQL remains the one documented remote-only low finding.
- The first structured validator call lacked the ignored clean-worktree
  environment and still contained Playwright's ignored auth state. Supplying
  the example environment and deleting that test state made all nine checks
  green.
- Scoped documentation links to release/plan deliverables. The engine's
  research supplement intentionally cites an external donor checkout and is
  not a portable repository-local link set.
- Normalized one active-session smart apostrophe and made the release CLI's
  existing shebang executable so tracked mode and invocation agree.

**Files Changed**:
- `scripts/release_evidence.py` - executable mode for its existing CLI
  shebang.
- `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/tasks.md`
  - ASCII apostrophe.

**Verification**:
- Command/check: `scripts/validate-changes.sh --json`
  - Result: PASS - 9/9 backend, engine, and frontend checks.
- Command/check: `pre-commit run --all-files`
  - Result: PASS - all 15 hooks, including Ruff, mypy, ty, Biome, TypeScript,
    generated client, typos, and Zizmor.
- Command/check: Gitleaks, Zizmor, and actionlint
  - Result: PASS - 61 commits and about 10.28 MB scanned with no leak; all ten
    workflows pass; actionlint is silent.
- Command/check: Python and npm dependency audits
  - Result: PASS - no known vulnerability; only local `app` and `txt2crs`
    packages are correctly non-PyPI; npm reports zero vulnerabilities.
- Command/check: release links, ASCII/LF, changed shebang modes, public
    secret/path patterns, generated files, diff hygiene, and tag absence
  - Result: PASS - 7 release/plan documents and 10 local targets; 6 active
    release files; changed CLIs executable; no risky public value; generated
    client clean; no `v1.0.0`.
- UI product-surface check: N/A - covered by T022.
- UI craft check: N/A.

**BQC Fixes**:
- Evidence correctness: no all-document portability claim is made for the
  deliberately external AIOS supplement.
- File contract: active release material is ASCII/LF and the release CLI mode
  now matches its shebang.

### Task T022 - Run Complete Frontend And Browser Matrix

**Started**: 2026-07-20 10:00 IDT
**Completed**: 2026-07-20 10:15 IDT
**Duration**: 15 minutes

**Notes**:
- Ran the frontend compiler, formatter/linter, unit suite, route-producing
  production build, and generated-client round trip under the declared Node
  26.5.0/npm 12.0.1 toolchain.
- Ran both dedicated provider-free course journeys. The broad browser matrix
  required the guarded deterministic application factory: generic production
  composition correctly returns `SYSTEM_6001` for account-wide engine purge
  while research is unconfigured, whereas the deterministic factory supplies
  that real package boundary without a provider.
- Wired the already-running isolated MailCatcher for reset-password coverage
  and removed every temporary browser state directory and local server.

**Files Changed**:
- No tracked file changed; generated routes/client remain byte-clean.

**Verification**:
- Command/check: Vitest, Biome, TypeScript, build, and client generation
  - Result: PASS - 132 unit tests; 156 Biome files; typecheck; 2,215 build
    modules; generated client and route tree unchanged.
- Command/check: completed and failed deterministic Playwright configurations
  - Result: PASS - each reported 16 passed and 1 scenario-specific skip.
- Command/check: broad Playwright against the guarded deterministic package
    boundary
  - Result: PASS - 69 passed and 11 intentional fixture/scenario skips.
  - Evidence: public, admin, auth, password reset, setup, intake, progress,
    results, mobile, desktop, contrast, keyboard, accessibility, reduced
    motion, and account cleanup surfaces passed.
- UI product-surface check: PASS.
- UI craft check: PASS - responsive, contrast, focus, reduced-motion, and
  publication interaction assertions are green.

**BQC Fixes**:
- Environment correctness: production-disabled signup/private routes and
  unconfigured live research were not weakened for testing; the explicit
  test-only application guard supplied deterministic engine lifecycle.
- Failure completeness: an observed `503 SYSTEM_6001` on user purge was
  classified as the intended unavailable production boundary, then covered
  through the correct credential-free test composition.

### Task T021 - Run Complete Python Suites

**Started**: 2026-07-20 09:57 IDT
**Completed**: 2026-07-20 09:59 IDT
**Duration**: 2 minutes

**Notes**:
- Re-ran both owning Python package roots from detached candidate revision
  `3e25c184f8187c264e163c63fa38a260764bbe93`.
- The first backend invocation inherited the root local-signup setting. That
  environment contamination correctly made three non-local configuration
  tests fail. Re-running with that unrelated variable unset made the exact
  suite green; no product change was needed.

**Files Changed**:
- No tracked file changed.

**Verification**:
- Command/check: engine pytest, Ruff, and mypy
  - Result: PASS - 470 passed, 1 explicit live skip; Ruff and mypy pass.
- Command/check: backend pytest, Ruff, and mypy with isolated PostgreSQL
  - Result: PASS - 506 passed with 106 known warnings; Ruff and mypy pass.
- UI product-surface check: N/A.
- UI craft check: N/A.

**BQC Fixes**:
- Environment correctness: the final backend matrix unsets developer-only
  public signup before testing staging/production configuration contracts.

### Task T015 - Prove Durable Replacement

**Started**: 2026-07-20 09:49 IDT
**Completed**: 2026-07-20 09:56 IDT
**Duration**: 7 minutes

**Notes**:
- Authenticated the Compose-seeded user without printing credentials, tokens,
  account identity, job identity, artifact identity, or content.
- Used the package's deterministic public factory to create one synthetic
  completed job in the mounted production private-state volume. The package
  reported four deliverables and exactly sixteen verified artifacts.
- Force-recreated only backend and frontend. PostgreSQL kept the same
  container and the private engine state kept the same named volume.
- Re-authenticated after replacement, then reopened the completed job through
  the package boundary and verified the manifest and representative artifact
  hash/size. Temporary proof identifiers were removed.

**Files Changed**:
- No tracked product file changed; proof state remains only in the isolated
  private Compose volume.

**Verification**:
- Command/check: authenticated login and current-user reads before/after
    application-tier replacement
  - Result: PASS - both authenticated shell reads returned success.
- Command/check: deterministic factory submit/execute and post-replacement
    package reopen
  - Result: PASS - completed status, four deliverables, sixteen artifacts, and
    identical representative bytes after replacement.
- Command/check: container, database, volume, health, and mode comparison
  - Result: PASS - both application container IDs changed; database container
    and private volume identities did not; backend/frontend/database are
    healthy; all seventeen stored artifact-tree files (manifest plus sixteen
    artifacts) are owner-private.
- UI product-surface check: PASS - the production frontend remains healthy.
- UI craft check: N/A - no visual implementation changed.

**BQC Fixes**:
- Evidence boundary: the temporary owner/job/hash proof lived only in the
  owner-private volume and was deleted after comparison; tracked notes retain
  aggregates only.
- External readiness separation: authenticated job HTTP routes remain
  intentionally unavailable while research is unconfigured. The durable
  package proof is complete; real shell-route/live proof remains T016-T019
  and is not overclaimed.

### Task T014 - Build And Start Production Images

**Started**: 2026-07-20 09:45 IDT
**Completed**: 2026-07-20 09:49 IDT
**Duration**: 4 minutes

**Notes**:
- A direct backend build exposed that the development stage is intentionally
  last in its Dockerfile. Added a regression contract before correcting the
  release workflow to target `production` explicitly.
- Rebuilt both images from detached revision
  `3e25c184f8187c264e163c63fa38a260764bbe93`, then launched only the root
  Compose file so the development override could not replace the production
  command or publish conflicting host ports.

**Files Changed**:
- `.github/workflows/release.yml` - explicit backend production build target.
- `backend/tests/scripts/test_release_workflow_contract.py` - release-stage
  regression contract.

**Verification**:
- Command/check: focused workflow contract red/green cycle
  - Result: PASS - the missing target failed first; all 4 checks pass after
    the workflow fix.
- Command/check: fresh image build and metadata/runtime inspection
  - Result: PASS - backend image
    `fccb6c43a22d24ca68b697baeb691c27aea3d6ed8727d4b1d863821ed62aacf3`
    runs as fixed UID 1001 (`appuser`), imports txt2crs `1.0.0`, uses one
    `fastapi run app/main.py` process, and has the expected healthcheck.
    Frontend image
    `55e15d893fa82be81e3b27bca54d382a440383c29ab12a30652280596b5c2a06`
    contains the built application and has the Nginx healthcheck.
- Command/check: isolated root Compose project
    `txt2crs-phase05-candidate`
  - Result: PASS - database, backend, and frontend are healthy; the backend
    and frontend run the exact inspected image IDs with zero restarts.
- UI product-surface check: PASS - production frontend health is green.
- UI craft check: N/A - no visual implementation changed.

**BQC Fixes**:
- Contract alignment: the hosted release workflow now inspects the same
  production target used by the local production baseline.
- Environment correctness: the proof invokes only `docker-compose.yml`;
  auto-loading the development override is explicitly avoided.

### Task T013 - Build And Inspect Python Distributions

**Started**: 2026-07-20 09:44 IDT
**Completed**: 2026-07-20 09:45 IDT
**Duration**: 1 minute

**Notes**:
- Built only the `1.0.0` wheel and source archive from the clean worktree and
  inspected required package metadata, license, README, and project manifest.

**Files Changed**:
- No tracked file changed; clean-worktree `backend/dist/` is ignored build
  output.

**Verification**:
- Command/check: `uv build --package txt2crs` plus tar/zip/hash inspection
  - Result: PASS - exactly one wheel and one source archive.
  - Evidence: wheel `fc2dab0bca88795302a47ceccc7175c2b907e0a0ed664244e01955b4c8613320`
    (194,117 bytes); source archive
    `8178e4cc00dcdc41a2c53cd29a641616fcf02accb899f8a8c5aa1bc90c4fd171`
    (588,687 bytes).
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T012 - Run The Fixed Evaluation Corpus

**Started**: 2026-07-20 09:43 IDT
**Completed**: 2026-07-20 09:44 IDT
**Duration**: 1 minute

**Notes**:
- Validated the complete packaged corpus, immutable fixture hashes, category
  coverage, dry-run planning, private snapshot replay, path confinement, and
  aggregate privacy. Planning executed no provider turn.
- The bounded `13/13` corpus-contract result is reserved for the candidate
  JSON; the JSON remains absent until live proof and artifact review complete.

**Files Changed**:
- No product file changed; exact aggregate facts are recorded here for later
  canonical evidence generation.

**Verification**:
- Command/check: focused engine evaluation cases/replay pytest
  - Result: PASS - 5 tests passed.
  - Evidence: 13 unique categories, 13 unique packaged fixture hashes, plan
    model `gpt-5.6`, `live=false`, and 0 executions.
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T011 - Execute The Clean Deterministic Matrix

**Started**: 2026-07-20 09:35 IDT
**Completed**: 2026-07-20 09:42 IDT
**Duration**: 7 minutes

**Notes**:
- Built a detached clean worktree, installed exact Python and npm lockfiles,
  installed the declared Node 26.5.0/npm 12.0.1 runtime, and ran the full
  credential-free package/application/browser matrix.
- The first clean run exposed and fixed two masked checkout defects: ignored
  runtime email HTML and backend tests requiring an ignored OpenAPI
  intermediate. It also exposed generator Biome ordering that broke in a
  `/tmp` worktree; the generator now formats before ASCII normalization.

**Files Changed**:
- `backend/app/email-templates/build/*.html`, `.gitignore` - tracked required
  runtime email assets.
- `backend/tests/scripts/test_generate_client_contract.py` - in-memory OpenAPI
  fallback and generation-order regression.
- `frontend/openapi-ts.config.ts`, `frontend/scripts/generate-client.mjs`,
  `frontend/scripts/normalize-generated-client.mjs`,
  `scripts/generate-client.sh` - clean-worktree generation.

**Verification**:
- Command/check: detached worktree at
  `6ddab6ce49edf5b7646d5f603d7a00acf0915725`
  - Result: PASS - exact lock installs; engine 470 passed/1 live skipped;
    backend 505 passed; frontend 132 passed; typecheck and 2,215-module build
    passed.
  - Evidence: complete browser 16 passed/1 skipped; failed browser 16
    passed/1 skipped.
- Command/check: generate client at the exact clean revision
  - Result: PASS - generated client has no diff and worktree status is clean.
- UI product-surface check: PASS - deterministic browser covered public,
  intake, progress, results, mobile, contrast, keyboard, failure, and cleanup.
- UI craft check: PASS - existing Phase 04 product surfaces remained green.

**BQC Fixes**:
- Contract alignment: clean backend tests now derive the server OpenAPI
  contract when its ignored generator intermediate is absent.
- Failure completeness: required runtime email assets now exist in every clean
  checkout; client generation no longer depends on a parent `/tmp` Biome
  context.

### Task T010 - Drive Focused Release Tests Fully Green

**Started**: 2026-07-20 09:33 IDT
**Completed**: 2026-07-20 09:34 IDT
**Duration**: 1 minute

**Notes**:
- Exercised every release/evidence negative fixture and the workflow contract,
  then verified the real CLI rejects a mismatched final tag with one bounded
  error.

**Files Changed**:
- `backend/tests/scripts/test_release_workflow_contract.py` - Ruff-owned format.

**Verification**:
- Command/check: focused pytest, Ruff check/format, and negative final-tag CLI
  - Result: PASS - 26 tests passed; Ruff passed; negative tag rejected.
  - Evidence: `negative-final-tag=pass`.
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T009 - Reconcile Verified Plan Status And Release Ordering

**Started**: 2026-07-20 09:31 IDT
**Completed**: 2026-07-20 09:33 IDT
**Duration**: 2 minutes

**Notes**:
- Marked every P0 application contract already proven by validated Phase 00-04
  sessions, left every submission contract open, set Phase 05 in progress,
  and aligned the source plan with candidate-before-assets-before-tag order.
- Removed the stale instruction to synchronize independently versioned shell
  and npm implementation packages.

**Files Changed**:
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` - verified status,
  `1.0.0` candidate, release surfaces, and session ordering.
- `.spec_system/PRD/PRD.md`, `.spec_system/PRD/phase_05/*.md` - planning-order
  conflict resolution created during `plansession`.

**Verification**:
- Command/check: focused plan-section inspection and `git diff --check`
  - Result: PASS - P0 has 17 checked rows; submission has 10 open rows.
  - Evidence: Phase 05 is in progress and S10 owns the final release tag.
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T008 - Synchronize The `1.0.0` Candidate

**Started**: 2026-07-20 09:29 IDT
**Completed**: 2026-07-20 09:31 IDT
**Duration**: 2 minutes

**Notes**:
- Set the root and reusable engine to the first stable `1.0.0`, regenerated
  the uv lock, promoted the release changelog, and made tag immutability/order
  explicit. The unrelated shell and npm package metadata remain independently
  versioned because the repository declares no synchronization contract for
  them.

**Files Changed**:
- `VERSION`, `backend/packages/txt2crs/pyproject.toml`, `backend/uv.lock` -
  synchronized release surfaces.
- `docs/VERSIONING.md`, `docs/CHANGELOG.md` - stable stage and dated release.

**Verification**:
- Command/check: `uv lock` and repository release validator
  - Result: PASS - lock changed txt2crs `0.7.0 -> 1.0.0`;
    `release-version=1.0.0`.
  - Evidence: lock contains exactly one txt2crs `1.0.0` record.
- Command/check: engine package metadata tests
  - Result: PASS - 2 tests passed after editable package rebuild.
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T007 - Define Public And Private Evidence Boundaries

**Started**: 2026-07-20 09:26 IDT
**Completed**: 2026-07-20 09:29 IDT
**Duration**: 3 minutes

**Notes**:
- Added a release index, public deterministic sample, sixteen-row pending
  inspection ledger, strict completion rule, private workspace ignores, local
  billing/CodeQL disclosure, and final-tag handoff.
- Deliberately left the candidate JSON absent so incomplete live work cannot
  look like successful evidence.

**Files Changed**:
- `docs/release/README_release.md` - evidence contract and final handoff.
- `docs/release/ARTIFACT_INSPECTION_1_0_0.md` - sixteen pending review rows.
- `docs/release/DETERMINISTIC_SAMPLE_1_0_0.md` - reproducible synthetic sample.
- `.gitignore` - raw/authenticated release-proof boundaries.

**Verification**:
- Command/check: ASCII/LF, relative-link, diff, and risky-string inspections
  - Result: PASS - 262 documentation lines are ASCII/LF, all local links
    resolve, diff hygiene passes, and the focused secret/path search is empty.
  - Evidence: `release-doc-links=pass`.
- UI product-surface check: N/A - judge documentation only.
- UI craft check: N/A - no application route changed.

### Task T006 - Integrate The Shared Release Workflow Validator

**Started**: 2026-07-20 09:24 IDT
**Completed**: 2026-07-20 09:25 IDT
**Duration**: 1 minute

**Notes**:
- Replaced the workflow's duplicate inline version logic with the tested
  candidate/final validator. Manual runs remain candidates; tag runs supply
  the exact observed tag.

**Files Changed**:
- `.github/workflows/release.yml` - shared identity validation command.

**Verification**:
- Command/check: focused evidence/workflow pytest and Ruff
  - Result: PASS - 26 tests passed; Ruff passed.
  - Evidence: read-only, pinned, nonpublishing, build/output, identity, and
    privacy contracts are green.
- Command/check: local candidate CLI at the Phase 04 transition revision
  - Result: PASS - `release-version=0.7.0`.
- UI product-surface check: N/A.
- UI craft check: N/A.

**BQC Fixes**:
- Contract alignment: hosted and local release identity now use one tested
  implementation (`.github/workflows/release.yml`).

### Task T005 - Implement The Release Evidence Boundary

**Started**: 2026-07-20 09:18 IDT
**Completed**: 2026-07-20 09:24 IDT
**Duration**: 6 minutes

**Notes**:
- Implemented standard-library version, identity, hash, sixteen-artifact,
  inspection, redaction, canonical JSON, atomic write, and candidate/final
  validation with bounded safe failures.
- Split the 675-line first pass into a 577-line cohesive contract and 138-line
  CLI to stay below the repository module-size ceiling.

**Files Changed**:
- `scripts/release_contract.py` - reusable strict validation boundary.
- `scripts/release_evidence.py` - local/hosted command entry point.
- `backend/tests/scripts/test_release_evidence.py` - safe sibling-module loader
  and corrected unique 64-character fixture hashes.

**Verification**:
- Command/check: focused pytest plus Ruff format/check
  - Result: PASS - 22 tests passed; all three Python files pass Ruff.
  - Evidence: candidate/final, drift, privacy, malformed input, completeness,
    and determinism cases are green.
- Command/check: module line-count and CLI help inspection
  - Result: PASS - core 577 lines, CLI 138 lines; help exits successfully.
- UI product-surface check: N/A.
- UI craft check: N/A.

**BQC Fixes**:
- Trust boundary enforcement: strict exact-field validation rejects unknown
  evidence instead of scrubbing it (`scripts/release_contract.py`).
- Failure path/resource cleanup: safe CLI errors and atomic temporary-file
  cleanup cover parse and write failures (`scripts/release_evidence.py`,
  `scripts/release_contract.py`).

### Task T002 - Write Failing Release Identity Tests

**Started**: 2026-07-20 09:15 IDT
**Completed**: 2026-07-20 09:17 IDT
**Duration**: 2 minutes

**Notes**:
- Defined synchronized root/package/lock/docs/changelog behavior, stable
  `1.0.0`, deterministic serialization, candidate revision identity, and
  exact candidate/final tag modes before implementation.

**Files Changed**:
- `backend/tests/scripts/test_release_evidence.py` - release identity contract.

**Verification**:
- Command/check: targeted pytest with the retained isolated PostgreSQL test
  connection
  - Result: PASS (expected red phase) - release tests error because
    `scripts/release_evidence.py` does not exist yet.
  - Evidence: missing module is the implementation gap; no false product or
    database failure remains after correcting the test DB environment.
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T003 - Write Failing Evidence Privacy And Completeness Tests

**Started**: 2026-07-20 09:15 IDT
**Completed**: 2026-07-20 09:17 IDT
**Duration**: 2 minutes

**Notes**:
- Added exactly sixteen deliverable/format pairs, six review dimensions, hash
  and bound checks, and nested rejection cases for risky public evidence.

**Files Changed**:
- `backend/tests/scripts/test_release_evidence.py` - privacy and ledger cases.

**Verification**:
- Command/check: targeted pytest with explicit isolated DB settings
  - Result: PASS (expected red phase) - all new evidence cases reach the
    missing release module boundary.
  - Evidence: 22 release-evidence cases error on the absent implementation.
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T004 - Write Failing Release Workflow Tests

**Started**: 2026-07-20 09:16 IDT
**Completed**: 2026-07-20 09:17 IDT
**Duration**: 1 minute

**Notes**:
- Protected shared validator use, read-only/nonpublishing behavior, immutable
  action references, both images/distributions, and bounded retained outputs.

**Files Changed**:
- `backend/tests/scripts/test_release_workflow_contract.py` - workflow contract.

**Verification**:
- Command/check: targeted pytest with explicit isolated DB settings
  - Result: PASS (expected red phase) - 3 safety checks pass and shared
    validator integration fails before workflow implementation.
  - Evidence: `1 failed, 3 passed` for the workflow module.
- UI product-surface check: N/A.
- UI craft check: N/A.

### Task T001 - Verify The Release Base And Prerequisites

**Started**: 2026-07-20 09:13 IDT
**Completed**: 2026-07-20 09:14 IDT
**Duration**: 1 minute

**Notes**:
- Confirmed the committed Phase 04 transition base was clean at
  `875808005a011a6a23538fa903805d0719463ccd`; the current diff contains only
  Phase 05 planning/state/archive changes made after that base.
- Found 13 fixed evaluation cases and deterministic integration/application
  assertions for exactly sixteen artifacts. Docker 29.5.3 and Compose 5.1.4
  are available; the retained isolated production stack is still present.
- Checked credential presence without reading or printing values. The
  operator's default Codex authentication file exists. No nonempty
  `TAVILY_API_KEY` exists in the process, root `.env`, or backend `.env`, and
  the retained app-owned Codex home is unauthenticated.

**Files Changed**:
- `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`
  - recorded the exact base, prerequisite inventory, and credential state.

**Verification**:
- Command/check: `.spec_system/scripts/analyze-project.sh --json &&
  .spec_system/scripts/check-prereqs.sh --json --env`
  - Result: PASS - Phase 05 Session 01 is active; Apex, jq, Git, and uv checks
    passed.
  - Evidence: current session directory contains `spec.md` and `tasks.md`;
    package context is correctly cross-cutting.
- Command/check: `git diff --check`, Docker/Compose version checks, focused
  `rg` inspection, safe credential-presence script, and isolated Compose state
  inspection
  - Result: PASS with one external prerequisite pending - repository
    contracts and local tooling are ready; Tavily is not configured.
  - Evidence: no diff whitespace error; Docker 29.5.3; Compose 5.1.4; 13 eval
    cases; sixteen-artifact assertions in engine and shell acceptance tests.
- UI product-surface check: N/A - no user-facing code changed.
- UI craft check: N/A - no user-facing code changed.

---

## Blockers & Solutions

### Blocker 1: Tavily Credential Is Not Configured

**Description**: The real representative course requires a private nonempty
`TAVILY_API_KEY`; none is present in the process or project environment files.
**Impact**: Tasks T016-T019 cannot truthfully complete the real Tavily proof
until a credential exists. All credential-free implementation and validation
tasks remain executable.
**Resolution**: Pending external credential availability. Continue every
deterministic and release-candidate task first; never substitute another
provider or fabricate a live result.
**Time Lost**: 0 minutes.

### Blocker 2: The Valid ChatGPT Account Is Not Entitled To GPT-5.6

**Description**: The explicit live subscription acceptance test used the
operator's valid ChatGPT credential and the exact configured `gpt-5.6` model.
Runtime readiness reported a valid credential but `model_entitled=False`.
**Impact**: T016-T019 cannot claim exact GPT-5.6 execution, even after a
Tavily key is supplied, until an authenticated app-owned account exposes that
model.
**Resolution**: Pending external account entitlement and packaged system-auth
bootstrap. Do not substitute another model; continue all provider-independent
release validation.
**Verification**: `TXT2CRS_RUN_LIVE_CODEX=1 uv run --package txt2crs pytest
packages/txt2crs/tests/acceptance -m live -q --tb=short` reached the entitlement
assertion and failed there before any generation turn.
**Time Lost**: 0 minutes.

---

## Design Decisions

### Decision 1: Tag Only After Tracked Submission Assets

**Context**: The source plan requires the judge README before release, but the
initial phase stubs tagged before Session 02 changed tracked judge assets.
**Options Considered**:
1. Tag in Session 01 - leaves the final submission commit ahead of its tag.
2. Produce the candidate now and tag after Session 02 assets - preserves one
   immutable tested identity.

**Chosen**: Produce and validate `1.0.0` in Session 01; create `v1.0.0` only
after Session 02 commits and revalidates all tracked judge assets.
**Rationale**: The submitted commit, tag, version, documentation, and build
must identify the same immutable revision.

---

## Checkpoints

### Checkpoint 1

- Completed: T001-T010.
- Scope check: release hardening only; no product behavior change.
- Tests: 26 focused release/workflow cases pass; candidate CLI accepts
  `1.0.0`; final CLI rejects a mismatched tag.
- Next task: T014 - build and inspect production images.

### Checkpoint 2

- Completed since prior checkpoint: T011-T015 and T021-T023.
- Scope check: clean candidate, build artifacts, production images,
  replacement proof, and complete provider-independent regression/security
  validation.
- Tests: engine 470/1 live skip; backend 506; frontend unit 132;
  deterministic browser 16/1 skip twice; broad browser 69/11 intentional
  skips; all workflow/security equivalents green.
- External gates: Tavily remains absent and the valid ChatGPT account is not
  entitled to exact `gpt-5.6`; T016-T020 and T024-T025 remain open where they
  depend on truthful live/canonical evidence.
- Next task: finish every provider-independent portion of T020 and T024, then
  preserve the exact external handoff.
