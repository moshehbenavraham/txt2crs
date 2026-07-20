# Implementation Notes

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Package**: null (cross-cutting)
**Started**: 2026-07-20 09:13 IDT
**Last Updated**: 2026-07-20 14:17 IDT

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | Session code review and validation handoff |
| Blockers | None |

---

## Task Log

### Task T016 - Provision Live Runtime

**Started**: 2026-07-20 11:22 IDT
**Completed**: 2026-07-20 12:05 IDT
**Duration**: 43 minutes

**Notes**:
- Added one short repository-root command for the packaged device-code flow:
  `./scripts/auth-codex.sh`.
- The helper resolves its own repository path, runs from the backend package
  root, stores credentials only below the ignored `.txt2crs-system`, enforces
  owner-only permissions, and forwards optional CLI flags.
- Replaced the long acceptance-guide bootstrap command and corrected its stale
  model environment name to `TXT2CRS_MODEL_ID`.
- Confirmed the private root environment now supplies a nonempty Tavily
  credential and explicitly selects `gpt-5.6-sol`; no value was printed.
- Diagnosed the post-login false negative from the local Hermes and AIOS source
  trees. A successful device token exchange establishes ChatGPT mode even when
  the same app-server has not refreshed its account projection yet; persisted
  OAuth presence is detected from metadata, never by reading token values.
- Added the regression first, then made successful login verification reopen a
  fresh packaged client. API-key rejection is now reported only for an exact
  `apiKey` account type; an unavailable account projection receives a truthful
  retry message instead.
- Upgraded the bundled SDK and CLI binary from the stale two-model catalog to
  `0.144.4`, regenerated the exact app-server protocol fixture, and verified
  the dedicated identity discovers `gpt-5.6-sol`. Readiness reports valid
  credentials and model entitlement without running a model turn.
- Started the real FastAPI lifespan against owner-only live-proof storage,
  packaged system auth, the private Tavily environment, and an ephemeral
  worker. The cached aggregate returned `ready`, `accepting_jobs=true`, eight
  input modes, and ready authentication, model, research, storage, worker,
  inputs, admission, and runtime-ownership checks.
- Documented the deterministic MCP subscription probe and the separately
  gated representative Sol/Tavily course as different operations. The full
  gate uses one stable idempotency key so a rerun resumes or replays the same
  durable job instead of purchasing duplicate work.

**Files Changed**:
- `scripts/auth-codex.sh` - concise executable device-auth shortcut.
- `backend/tests/scripts/test_system_auth_script_contract.py` - executable,
  path, argument, private-state, and documentation contracts.
- `backend/packages/txt2crs/tests/acceptance/README_acceptance.md` - short
  helper plus separate small-probe and full-course runbooks.
- `backend/packages/txt2crs/src/txt2crs/ai/system_authentication.py` and its
  contract tests - fresh-client post-login verification and truthful fallback.
- `backend/packages/txt2crs/pyproject.toml`, `backend/uv.lock`, protocol
  contract, and `docs/fixtures/codex_app_server_0.144.4/` - exact packaged
  runtime and matching generated protocol surface.
- `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`
  - separately gated, idempotent representative full-course proof.

**Verification**:
- Command/check: focused helper contract before and after implementation
  - Result: RED/GREEN - 2 missing-script failures first; 3 tests pass after
    implementation and documentation.
- Command/check: Ruff, `bash -n`, ShellCheck, and real helper `--help`
  - Result: PASS - Python and shell checks are clean; packaged CLI help exits
    zero without starting authentication.
- Command/check: focused post-login regressions before and after the fix
  - Result: RED/GREEN - 2 new failures first; all 7 system-authentication
    contracts pass after the fresh-client verification change.
- Command/check: packaged protocol and version contracts
  - Result: RED/GREEN - stale pins and missing `0.144.4` fixture failed first;
    10 combined protocol/authentication contracts pass after the upgrade.
- Command/check: dedicated account and exact-model readiness
  - Result: PASS - account mode is ChatGPT; five models are visible;
    `gpt-5.6-sol` is discovered with valid credentials and entitlement. No
    paid generation turn ran.
- Command/check: real FastAPI lifespan and cached aggregate readiness
  - Result: PASS - status ready, accepting jobs true, all eight safe checks
    ready, and reverse-order worker/auth/application cleanup completed.
- Command/check: full-course gate static validation
  - Result: PASS - Ruff, mypy, and 3 helper/document contracts pass; both live
    tests remain explicitly skipped in the default suite.
- UI product-surface check: N/A - local operator CLI only.
- UI craft check: N/A - no application UI changed.

**BQC Fixes**:
- Resource/privacy boundary: owner-only state creation precedes the packaged
  login, and `exec` preserves its exit status without a wrapper process.
- Contract alignment: the guide now names the environment variable consumed
  by the live test instead of the obsolete `TXT2CRS_LIVE_MODEL`.

### Task T017 - Execute The Representative Live Course

**Started**: 2026-07-20 12:08 IDT
**Completed**: 2026-07-20 13:43 IDT
**Duration**: 95 minutes, including tests-first release-blocking repairs

**Notes**:
- Ran the separately gated application/facade acceptance path with the
  dedicated ChatGPT subscription identity, exact `gpt-5.6-sol`, and real
  Tavily research. No OpenAI documentation or web research informed the
  authentication/model work; the implementation was grounded in repository
  behavior and the operator-provided local Hermes and AIOS source trees.
- The canonical release proof is one delivered compact synthetic DNS course.
  It completed in 258 seconds with six sources, six excerpts, six model-usage
  records, one module, three sections, nine durable checkpoints, four
  publications, and exactly sixteen artifacts.
- Confirmed every usage record identifies exact `gpt-5.6-sol` and ChatGPT
  subscription billing. The collected evidence checkpoint precedes design
  and module drafting, and no model fallback occurred.
- Preliminary provider attempts exposed release-blocking strict-schema,
  research-budget, alignment, citation, excerpt-hash, rendering, and fixture
  budget defects. Each defect failed safely, received a regression before its
  fix, and was either purged after failure or explicitly retired and purged
  before the final canonical run. They are not represented as additional
  delivered release courses.
- The final bounded execution consumed 186,889 input tokens and 10,897 output
  tokens, below its finite 300,000/60,000 caps. The course truthfully requests
  fifteen minutes rather than presenting a compact module as an hour-long
  lesson.

**Files Changed**:
- `backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`
  - exact-model, research-order, checkpoint, usage, artifact, and
    student/instructor assertions for the separately gated course proof.
- `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py` and
  `backend/packages/txt2crs/src/txt2crs/ai/runtime.py` - supported strict
  provider schemas plus trusted prompt-schema fallback with local validation.
- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py` and focused
  integration tests - bounded plan/module repair, exact output contracts,
  alignment, and block-level citation validation.
- `backend/packages/txt2crs/src/txt2crs/research/coordinator.py` and focused
  integration tests - attempted-URL accounting and stable stripped excerpt
  hashing at the extraction cutoff.

**Verification**:
- Command/check: separately gated representative acceptance test
  - Result: PASS - `1 passed in 259.88s`; safe summary reports GPT-5.6 family,
    sixteen artifacts, 258 seconds, and eight checkpoints observed during
    polling. Final durable recovery contains checkpoint sequence nine.
- Command/check: final checkpoint and manifest inspection through the
  owner-scoped facade
  - Result: PASS - real research exists before drafting; all six usage records
    identify exact Sol and subscription billing; manifest coverage is four by
    four and every reopened byte stream matches its recorded size and hash.
- Command/check: focused regressions followed by the complete engine suite
  - Result: RED/GREEN - every discovered defect failed its new focused test
    first; the latest provider-independent engine suite passes 486 tests with
    two explicit live skips.
- UI product-surface check: N/A - the live proof exercises the existing
  application boundary without changing the frontend.
- UI craft check: N/A - no frontend code changed.

**BQC Fixes**:
- Evidence honesty: records one canonical delivered proof while disclosing the
  preliminary failed/superseded attempts instead of claiming no prior provider
  calls occurred.
- Resource safety: every failed or superseded owner state was removed through
  `application.purge_owner`; the final raw state is retained only until T019
  derives and validates the bounded public evidence.

### Task T018 - Inspect All Sixteen Live Artifacts

**Started**: 2026-07-20 13:43 IDT
**Completed**: 2026-07-20 13:56 IDT
**Duration**: 13 minutes

**Notes**:
- Reopened all sixteen owner-private artifacts through the application facade
  and independently matched every byte count and SHA-256 digest recorded in
  the human ledger.
- Compared canonical course, review, assessment, and answer content across
  HTML, Markdown, PDF, and DOCX. All formats preserve the same meaning, and
  the learner assessment remains separate from instructor-only answers,
  grading criteria, rationales, and evidence links.
- Confirmed the renderer removes internal schema labels, stale long and
  compact identifiers, duplicate objective labels, empty optional sections,
  raw inline Markdown in PDF/DOCX, and incorrect singular point grammar.
  Instructor answer keys disclose applicable source links for each item.
- Opened and visually reviewed every PDF page. Verified all four DOCX files as
  ZIP packages, converted them successfully with LibreOffice, and reviewed
  their rendered pages. Text extraction and bounding-box checks confirmed
  long headings remain intact within the document bounds.
- Verified owner mismatch and missing-artifact requests remain
  indistinguishable. No raw artifact body or private download link was copied
  into tracked evidence.

**Files Changed**:
- `backend/packages/txt2crs/src/txt2crs/rendering/artifacts.py` and
  `backend/packages/txt2crs/tests/unit/test_rendering.py` - tests-first
  reader-facing labels, optional-section handling, identifier cleanup,
  Markdown stripping, punctuation normalization, evidence disclosure, and
  point grammar.
- `docs/release/ARTIFACT_INSPECTION_1_0_0.md` - sixteen explicit PASS rows,
  final hashes and sizes, and bounded cross-publication findings.

**Verification**:
- Command/check: hash and size comparison for sixteen reopened artifacts
  - Result: PASS - exact coverage and integrity for all four deliverables in
    all four formats.
- Command/check: semantic, citation, identifier, Markdown-debris, and
  student/instructor separation inspection
  - Result: PASS - every required cross-publication boundary holds.
- Command/check: PDF parsing/rendered page review and DOCX ZIP/conversion
  review
  - Result: PASS - four searchable PDFs and four valid, renderable DOCX
    packages; course 3 pages, review pack 8, assessment 2, answer key 3.
- Command/check: renderer unit suite
  - Result: PASS - 20 renderer tests.
- UI product-surface check: N/A - artifact publications, not application UI.
- UI craft check: PASS - each generated format is readable and complete.

**BQC Fixes**:
- Reader quality: artifact prose no longer exposes internal generation IDs or
  empty/redundant headings.
- Separation: source evidence appears only in the instructor answer key, never
  in the student assessment.

### Task T019 - Audit And Reduce Live Evidence

**Started**: 2026-07-20 13:56 IDT
**Completed**: 2026-07-20 14:09 IDT
**Duration**: 13 minutes

**Notes**:
- Audited the ignored live state, repository-local trace/log/backup/temp
  surfaces, open descriptors, provider/worker process state, loopback
  listeners, ignored release workspaces, tracked diff, and staged diff without
  printing credentials, provider payloads, private identifiers, or artifact
  bodies.
- The live workspace contained the expected one owner-private job and sixteen
  artifacts. Its root and directories were mode `0700`; files were tightened
  to owner-only permissions before cleanup. No process retained an open
  descriptor to the workspace.
- Found no repository-local HAR, trace, log, backup, or temporary evidence
  file; no ignored release-evidence workspace; no live loopback listener; no
  staged diff; and no secret finding in the redacted Gitleaks scan of the
  uncommitted project diff.
- Custom added-line checks found zero credential assignments, emails, absolute
  home paths, provider-payload fields, prompt transcripts, or raw artifact
  body fields. The deterministic sample remains synthetic and contains no live
  body or provider claim.
- Purged the canonical owner through `application.purge_owner`: one job and
  one artifact job tree were deleted. A repeated purge returned zero for both
  counts. Removed the now-redundant raw state directory, purge worker, and two
  live worker temp paths; all are confirmed absent.
- Preserved only the separate ignored dedicated Codex authentication home.
  Deleting that credential would log the application out and is neither raw
  course evidence nor necessary for the privacy requirement.
- Generated the candidate ledger only after the exact source revision and
  repeat-build hashes existed. The strict validator accepted its sixteen
  unique artifact pairs, bounded live facts, build hashes, and sole reviewed
  external exception; a second canonical rewrite was byte-identical.

**Files Changed**:
- `docs/CHANGELOG.md` - bounded live-proof, repair, and cleanup release notes.
- `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`
  - safe audit counts and cleanup proof.
- `docs/release/RELEASE_CANDIDATE_1_0_0.json` - canonical allowlisted public
  ledger for exact candidate revision
  `a80700863e99cdd34bed757873d969236cdf36fa`.

**Verification**:
- Command/check: private workspace modes and `/proc` descriptor audit
  - Result: PASS - owner-only boundary; zero external open descriptors.
- Command/check: repository trace/log/backup/temp and ignored-workspace audit
  - Result: PASS - zero retained raw evidence files or release workspaces.
- Command/check: redacted Gitleaks diff scan and bounded added-line patterns
  - Result: PASS - no leak finding and zero risky-value matches.
- Command/check: application owner purge plus idempotent replay
  - Result: PASS - first purge deleted one job and one artifact tree; second
    purge deleted zero; all raw live and worker paths are absent.
- Command/check: strict candidate validation, public-pattern scan, and
  repeated canonical rewrite
  - Result: PASS - sixteen unique artifact pairs; no private value shape;
    byte-identical canonical SHA-256
    `43e811fc58efdce308b33d74112ab3a5969bca6fa3585e9a347643f6d052bbbd`.
- UI product-surface check: N/A - privacy/evidence operations only.
- UI craft check: N/A - no frontend code changed.

**BQC Fixes**:
- File defense: tightened private child-file modes even though the `0700`
  ancestor already prevented non-owner traversal.
- Cleanup honesty: retained the dedicated login because it is authentication
  state, while removing every raw course and inspection workspace.

### Task T024 - Repeat Candidate Gates (Provider-Independent Portion)

**Started**: 2026-07-20 10:21 IDT
**Completed**: 2026-07-20 14:09 IDT
**Duration**: 228 elapsed minutes, interleaved with T016-T019

**Notes**:
- Repeated version validation and both distribution builds from detached
  revision `c72137e13ee1c6770d06b4a77655e4722041ffa9`. The distribution hashes
  and sizes were byte-identical to T013.
- The first backend repeat exposed a real reproducibility defect: nested
  package type-check and test caches entered the Docker build context, which
  grew from about 73 kB to 25.44 MB and changed the image ID. Wrote the static
  recursive-ignore regression first, observed its focused failure, then
  corrected the backend context contract in commit
  `ce2558a878eea5f575f032b8994b5175c7605be5`.
- Repeated the provider-independent candidate build from detached revision
  `ce2558a878eea5f575f032b8994b5175c7605be5` while 25 MB of ignored nested
  caches remained present. The backend context was only 53.32 kB. Adding a
  new ignored sentinel below the nested package cache produced the same
  context size, full build cache hit, and backend image ID.
- Replaced the isolated candidate backend/frontend/prestart tier with those
  exact images. Both application container IDs changed, while the PostgreSQL
  container identity and private engine-state volume mount remained
  identical; backend, frontend, and database returned healthy.
- Committed the release-blocking fixes and bounded evidence inputs as exact
  candidate source revision
  `a80700863e99cdd34bed757873d969236cdf36fa`, excluding the operator's
  unrelated root README edit. Repeated the candidate gates from a detached,
  clean worktree at that revision.
- Rebuilt and inspected both Python distributions twice with byte-identical
  outputs. Rebuilt both labeled production images, repeated the backend build
  after adding an ignored nested-cache sentinel, and reproduced the exact
  backend image ID.
- Started a new isolated root-only Compose project with the exact images.
  Database, backend, and frontend became healthy, prestart exited zero, and
  all restart counts remained zero. Force-replacing backend/frontend changed
  both application container IDs while preserving the database container,
  private-state volume, owner-only marker, and marker bytes.
- Generated and twice validated the canonical candidate ledger with the exact
  revision and final distribution/image/artifact hashes. No `v1.0.0` tag
  exists.

**Files Changed**:
- `backend/tests/scripts/test_container_contract.py` - tests-first recursive
  build-context regression.
- `backend/.dockerignore` - recursive exclusions for package caches, virtual
  environments, coverage, and distribution/build outputs.

**Verification**:
- Command/check: isolated container-contract pytest before and after the fix
  - Result: RED/GREEN - the new assertion failed with the original root-only
    patterns; all 14 static container contracts pass after correction.
- Command/check: detached distribution repeat
  - Result: PASS - wheel
    `fc2dab0bca88795302a47ceccc7175c2b907e0a0ed664244e01955b4c8613320`
    (194,117 bytes); source archive
    `8178e4cc00dcdc41a2c53cd29a641616fcf02accb899f8a8c5aa1bc90c4fd171`
    (588,687 bytes).
- Command/check: cache-filled production image build and ignored-sentinel
    repeat
  - Result: PASS - backend
    `c9933b7091617355fa271833bc9a40ec5dde79c18fa29727bdf1f80c30dd03b2`
    remained identical after the ignored cache changed; frontend
    `a37f5471fad43754486e192bed261b0c90df3157c3ab0630a6c36a43783798ca`
    built successfully.
- Command/check: root-only candidate Compose replacement and health wait
  - Result: PASS - application tier replaced; database container and state
    volume retained; backend/frontend/database healthy; prestart exited zero.
- Command/check: final detached revision and candidate repository validator
  - Result: PASS - clean source revision
    `a80700863e99cdd34bed757873d969236cdf36fa`; synchronized `1.0.0`
    surfaces; candidate mode; no final tag.
- Command/check: final distribution build, inspection, and repeat
  - Result: PASS - wheel
    `c21c64a34ebf19c237cbac031351015fcf75c9a7e58f2a4bd5599a93ae3e2212`
    (199,716 bytes); source archive
    `d8f8a50a0116d2fefb55af6a4d221fa1fb4f1b0327364ac06b5868efd242f601`
    (632,606 bytes); repeated bytes identical.
- Command/check: final labeled image build and ignored-cache repeat
  - Result: PASS - backend
    `cc6c2b8dfd52d741247c0dc01f699b19883d5fe4acf03151fd6065af05f1a7e0`;
    frontend
    `10baf7ec0bc99bb89ea6bca2b00045456e04fb134538c924fb23cbd04f709266`;
    exact version/revision labels and runtime inspections pass.
- Command/check: final isolated Compose health and replacement smoke
  - Result: PASS - all service health/prestart/restart assertions pass;
    application containers replaced while database and private volume
    persisted.
- UI product-surface check: PASS - the production frontend remains healthy.
- UI craft check: N/A - no visual implementation changed.

**BQC Fixes**:
- Reproducibility: local workspace outputs can no longer alter the production
  context copied from `packages/txt2crs`.
- Evidence honesty: provisional image IDs are recorded as a partial repeat,
  not mislabeled as the final candidate revision or canonical live ledger.

### Task T025 - Reconcile The Candidate Handoff

**Started**: 2026-07-20 14:09 IDT
**Completed**: 2026-07-20 14:17 IDT
**Duration**: 8 minutes

**Notes**:
- Reconciled the exact candidate revision, synchronized version, two
  distribution hashes, two image hashes, thirteen-case evaluation aggregate,
  representative live facts, sixteen artifact rows, sole reviewed external
  exception, raw-state cleanup, and Session 02 tag handoff across the
  candidate ledger, release index, inspection ledger, task checklist, and
  implementation notes.
- Re-ran all three owning codebase gates after the exact candidate build.
  Engine, backend, and frontend tests, linting, strict typing, frontend build,
  and authoritative generated-client round trip are green.
- The first backend attempt inherited an unrelated local database password and
  failed at fixture setup. A disposable loopback PostgreSQL instance then
  proved connectivity but correctly required migrations. After `alembic
  upgrade head`, the complete backend suite passed; no product correction was
  needed.
- A direct frontend package generator invocation bypassed the repository
  wrapper's final normalization and made one ASCII contract fail. Running
  `scripts/generate-client.sh` restored the authoritative Biome plus ASCII/LF
  pipeline, left no generated diff, and the complete backend rerun passed.
- Removed the isolated candidate Compose project, its two volumes, the
  disposable test database, and all candidate temp state. Zero candidate
  containers or volumes remain. The local reviewed distribution files and
  labeled image IDs still match the canonical ledger exactly.

**Files Changed**:
- `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/tasks.md`
  - final completion and handoff checklist.
- `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`
  - exact final commands, counts, hashes, exceptions, and cleanup.
- `docs/release/README_release.md` - completed candidate state and linked
  canonical ledger.
- `docs/release/RELEASE_CANDIDATE_1_0_0.json` - validated canonical evidence.

**Verification**:
- Command/check: complete engine suite, Ruff, and strict mypy
  - Result: PASS - 486 passed and two explicit live skips; Ruff; 138-source
    mypy graph.
- Command/check: migrated disposable PostgreSQL plus complete backend suite,
  Ruff, and strict mypy
  - Result: PASS - 510 passed with one dependency deprecation warning; Ruff;
    47-source mypy graph.
- Command/check: frontend unit, Biome, TypeScript, production build, and
  authoritative client generation
  - Result: PASS - 132 tests; 158 files; 2,215 build modules; generated client
    ASCII/LF and byte-clean.
- Command/check: `scripts/validate-changes.sh --json`
  - Result: PASS - all nine backend, engine, and frontend gates.
- Command/check: candidate resource and hash reconciliation
  - Result: PASS - local distributions/images match the ledger; zero orphan
    candidate containers, volumes, or disposable database containers.
- Command/check: final staged diff, release validators, Gitleaks, and
  pre-commit hooks
  - Result: PASS - diff hygiene; repository/evidence identity; no leak; all
    applicable staged hooks.
- Command/check: active-session/release ASCII/LF, local links, raw workspace,
  staged README, and final-tag audits
  - Result: PASS - seven files and four local links; zero raw/private
    workspaces; operator README excluded; no `v1.0.0` tag.
- UI product-surface check: PASS - frontend unit/build gates and the earlier
  complete browser matrix remain green; no frontend source changed.
- UI craft check: PASS - the earlier mobile/desktop/accessibility/reduced-
  motion matrix and the final artifact-format reviews remain green.

**BQC Fixes**:
- Environment correctness: fixture setup failures were resolved with a
  migrated disposable database instead of weakening authentication or
  changing product configuration.
- Generated-source ownership: used the repository wrapper and left
  `frontend/src/client/` untouched by hand.

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

### Blocker 1: Tavily Credential Was Not Configured

**Description**: The real representative course required a private nonempty
`TAVILY_API_KEY`; none was initially present in the process or project
environment files.
**Impact**: Tasks T016-T019 cannot truthfully complete the real Tavily proof
until a credential exists. All credential-free implementation and validation
tasks remain executable.
**Resolution**: Resolved 2026-07-20 11:20 IDT - the private root `.env` now
contains a nonempty value and Compose passes it to the backend. Real provider
authentication remains part of the single T017 live run.
**Rechecked**: 2026-07-20 10:32 IDT - process environment, root `.env`,
backend `.env`, and retained candidate backend all remain empty or absent.
**Time Lost**: 0 minutes.

### Blocker 2: Dedicated ChatGPT Identity Did Not Discover Sol

**Description**: The explicit live subscription acceptance test used the
operator's valid default ChatGPT credential. Exact `gpt-5.6` and follow-up
readiness-only `gpt-5.6-sol` checks both returned `model_entitled=False`; the
current two-model catalog contains no reviewed GPT-5.6 family identifier.
**Impact**: T016-T019 cannot claim exact Sol execution until the dedicated
app-owned identity discovers `gpt-5.6-sol`.
**Resolution**: Resolved 2026-07-20 11:58 IDT. The operator completed the
packaged device-code flow, the false negative was repaired from local
Hermes/AIOS behavior, and the bundled SDK/CLI was upgraded to `0.144.4`.
The dedicated catalog now contains five models including exact
`gpt-5.6-sol`; aggregate readiness is ready without a fallback.
**Verification**: `TXT2CRS_RUN_LIVE_CODEX=1 uv run --package txt2crs pytest
packages/txt2crs/tests/acceptance -m live -q --tb=short` reached the entitlement
assertion and failed there before any generation turn.
**Rechecked**: 2026-07-20 12:00 IDT - the dedicated credential is valid, exact
Sol is entitled, and the complete application readiness projection is ready.
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
  entitled to exact `gpt-5.6`; T016-T019 and the live-dependent portions of
  T024-T025 remain open.
- Next task: provision both external prerequisites, then resume T016 without
  substituting a provider or model.

### Checkpoint 3

- Resumed the Apex `implement` workflow from clean revision
  `d3b7516975d093502c5a64c6130caee40e0c5f79`.
- Re-ran the non-secret Tavily presence audit and exact packaged live
  entitlement test. Both external blockers are unchanged; no paid generation
  turn or synthetic live job ran.
- Confirmed the retained candidate backend, frontend, and database are
  healthy. The incomplete candidate JSON and premature `v1.0.0` tag remain
  absent.
- Next task: T016 immediately after a private Tavily key and a ChatGPT account
  entitled to exact `gpt-5.6` are available.

### Checkpoint 4

- Completed T016 with packaged device authentication, exact Sol catalog
  discovery, private Tavily configuration, owner-only storage, live worker,
  and complete application readiness.
- Used only repository code and the operator-provided local Hermes and AIOS
  sources for the authentication/catalog diagnosis; no OpenAI documentation
  was used.
- Added the separately gated representative course proof. The normal suite
  still performs no network or paid generation work.
- Next task: run the one T017 synthetic course, then inspect its sixteen
  artifacts and complete the T018-T019 privacy ledger before final gates.
