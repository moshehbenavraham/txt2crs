# Implementation Notes

**Session ID**: `phase00-session01-baseline-container-and-state`
**Package**: null
**Started**: 2026-07-19 09:09 IDT
**Last Updated**: 2026-07-19 09:34 IDT

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 21 / 21 |
| Estimated Remaining | 0 hours |
| Blockers | 0 |

---

## Task Log

### 2026-07-19 - Session Start

**Environment verified**:

- [x] Spec-system structure and active session confirmed.
- [x] Docker 29.5.3 and Compose v5.1.4 available.
- [x] uv 0.9.4, repository Python 3.14 environment, npm, git, and jq available.
- [x] Ignored local `.env` files initialized from checked-in development
  examples because the repository did not contain local copies.

The generic prerequisite script reports no root workspace manager for this
mixed uv/npm monorepo. The spec state explicitly registers `backend`,
`backend/packages/txt2crs`, and `frontend`; direct uv and npm tool checks
passed, so this detector limitation does not block the cross-cutting session.

---

### Task T001 - Record The Pre-Change Baseline

**Started**: 2026-07-19 09:09 IDT
**Completed**: 2026-07-19 09:09 IDT
**Duration**: 1 minute

**Notes**:

- Confirmed the host workspace already imports `txt2crs`.
- Confirmed both Docker targets declare four workers, the development target
  lacks `USER appuser`, no workspace package copy precedes uv sync, Compose
  has no engine state volume, engine path settings are absent, and donor
  product names remain in environment and frontend metadata.

**Files Changed**:

- `.env` - initialized ignored local Compose settings from the example.
- `backend/.env` - initialized ignored local backend settings from the example.

**Verification**:

- Command/check: `cd backend && uv run python -c "import txt2crs; print(txt2crs.__name__)"`
  - Result: PASS - printed `txt2crs`.
  - Evidence: host workspace import succeeds before container changes.
- Command/check: targeted `rg` across Dockerfile, Compose, settings, examples,
  and frontend metadata
  - Result: PASS - found both `--workers 4` commands, no engine path fields,
    four donor environment defaults, and ten donor page titles.
  - Evidence: exact pre-change gaps match the adopted plan.
- UI product-surface check: N/A - inspection only; no UI change yet.
- UI craft check: N/A - inspection only; no UI change yet.

---

### Task T002 - Write Failing Filesystem Settings Tests

**Started**: 2026-07-19 09:10 IDT
**Completed**: 2026-07-19 09:11 IDT
**Duration**: 1 minute

**Notes**:

- Added 18 tests for container defaults, custom-root derivation,
  normalization, relative and escaping paths, boundary overlap, ephemeral
  worker isolation, and existing symlink endpoints.
- Used `--confcutdir=tests/core` for this pure settings suite so the
  repository's session-wide database fixture does not mask the intended
  failing-first evidence.

**Files Changed**:

- `backend/tests/core/test_txt2crs_settings.py` - added the failing path
  contract.

**Verification**:

- Command/check: `uv run pytest --confcutdir=tests/core tests/core/test_txt2crs_settings.py -q`
  - Result: PASS - failing-first gate behaved as expected.
  - Evidence: 18 tests failed only because the five planned `Settings` fields
    and their validation do not exist yet.
- UI product-surface check: N/A - backend settings tests only.
- UI craft check: N/A - backend settings tests only.

---

### Task T003 - Write Failing Container Contract Tests

**Started**: 2026-07-19 09:11 IDT
**Completed**: 2026-07-19 09:12 IDT
**Duration**: 1 minute

**Notes**:

- Added fast static checks scoped to individual Docker stages and Compose
  services so unrelated text cannot produce false positives.
- Covered workspace copy order, one-process commands, non-root targets,
  private directory creation, explicit engine environment, volume separation,
  and unpublished research ports.

**Files Changed**:

- `backend/tests/scripts/test_container_contract.py` - added seven deployment
  contract tests.

**Verification**:

- Command/check: `uv run pytest --confcutdir=tests/scripts tests/scripts/test_container_contract.py -q`
  - Result: PASS - failing-first gate behaved as expected.
  - Evidence: 5 failed on the exact missing workspace copy, process/user,
    directory, environment, and state-volume contracts; 2 existing
    unpublished-port and reload-process constraints already passed.
- UI product-surface check: N/A - deployment tests only.
- UI craft check: N/A - deployment tests only.

---

### Task T004 - Copy Workspace Packages Before Image Sync

**Started**: 2026-07-19 09:12 IDT
**Completed**: 2026-07-19 09:12 IDT
**Duration**: 1 minute

**Notes**:

- Copied the complete backend `packages/` tree in the base stage before any uv
  sync so both downstream targets resolve the declared workspace member.
- Added an intern-facing comment explaining the host/container parity risk.

**Files Changed**:

- `backend/Dockerfile` - added the workspace package copy before dependency
  installation.

**Verification**:

- Command/check: focused
  `test_workspace_packages_are_copied_before_first_uv_sync`
  - Result: PASS - 1 passed.
  - Evidence: the copy statement now precedes the first `uv sync`.
- UI product-surface check: N/A - Dockerfile only.
- UI craft check: N/A - Dockerfile only.

---

### Task T005 - Create Non-Root Private Runtime Directories

**Started**: 2026-07-19 09:12 IDT
**Completed**: 2026-07-19 09:13 IDT
**Duration**: 1 minute

**Notes**:

- Added the fixed UID/GID 1001 application identity to both image targets.
- Seeded the state, artifact, Codex home, and worker directories with mode
  `0700` and runtime-user ownership, then switched development to `appuser`.

**Files Changed**:

- `backend/Dockerfile` - aligned development and production users, ownership,
  and private directory modes.

**Verification**:

- Command/check: focused
  `test_both_targets_create_owner_only_private_runtime_directories`
  - Result: PASS - 1 passed.
  - Evidence: both stages contain the fixed user and owner-only state setup.
- BQC resource boundary check: PASS - directories have explicit ownership and
  no new runtime resource is acquired.
- UI product-surface check: N/A - Dockerfile only.
- UI craft check: N/A - Dockerfile only.

---

### Task T006 - Enforce One Backend Process

**Started**: 2026-07-19 09:13 IDT
**Completed**: 2026-07-19 09:13 IDT
**Duration**: 1 minute

**Notes**:

- Removed the four-worker option from both image targets and named
  `app/main.py` explicitly.
- Preserved the local reload override, which already runs one process.

**Files Changed**:

- `backend/Dockerfile` - set one-process commands and documented the serial
  worker topology constraint.

**Verification**:

- Command/check: focused one-process image and override contract tests
  - Result: PASS - 2 passed.
  - Evidence: production, development, and reload paths contain no worker
    multiplier.
- BQC concurrency check: PASS - the deployment can no longer start duplicate
  in-process engine supervisors by default.
- UI product-surface check: N/A - deployment command only.
- UI craft check: N/A - deployment command only.

---

### Task T007 - Add Typed Engine Path Settings

**Started**: 2026-07-19 09:13 IDT
**Completed**: 2026-07-19 09:14 IDT
**Duration**: 1 minute

**Notes**:

- Added five `Path` settings for persistent state, job SQLite, artifacts,
  isolated `CODEX_HOME`, and ephemeral worker storage.
- Derived omitted persistent children from a custom state root while
  preserving explicit child overrides.

**Files Changed**:

- `backend/app/core/config.py` - added typed engine path configuration and
  custom-root derivation.

**Verification**:

- Command/check: focused default and custom-root settings tests
  - Result: PASS - 2 passed.
  - Evidence: container defaults and child derivation match the plan.
- Command/check: `uv run mypy app/core/config.py --strict`
  - Result: PASS - no issues in 1 source file.
- BQC contract alignment check: PASS - all paths are strongly typed and
  explicit at the shell boundary.
- UI product-surface check: N/A - backend configuration only.
- UI craft check: N/A - backend configuration only.

---

### Task T008 - Enforce Safe Filesystem Boundaries

**Started**: 2026-07-19 09:14 IDT
**Completed**: 2026-07-19 09:15 IDT
**Duration**: 1 minute

**Notes**:

- Rejected relative paths and existing symlink endpoints or parents before
  normalizing with `Path.resolve`.
- Enforced strict persistent-child ancestry, distinct artifact/Codex/database
  boundaries, and an ephemeral worker root outside persistent state.
- Stored normalized paths back on the settings object so later composition
  code receives one canonical representation.

**Files Changed**:

- `backend/app/core/config.py` - added symlink detection, normalization, and
  boundary validation.

**Verification**:

- Command/check: full focused txt2crs settings suite
  - Result: PASS - 18 passed.
  - Evidence: all default, custom, escape, overlap, and symlink scenarios pass.
- Command/check: Ruff on settings and tests; strict mypy on settings
  - Result: PASS - no lint or type errors.
- BQC trust-boundary check: PASS - unsafe external configuration fails at
  startup before filesystem access.
- UI product-surface check: N/A - backend configuration only.
- UI craft check: N/A - backend configuration only.

---

### Task T009 - Document Truthful Environment Defaults

**Started**: 2026-07-19 09:15 IDT
**Completed**: 2026-07-19 09:16 IDT
**Duration**: 1 minute

**Notes**:

- Renamed donor image, stack, and project defaults to txt2crs.
- Documented the image-owned container paths in the root example and added
  configurable host-development paths to the backend example.
- Synchronized the ignored local environment files without adding real
  credentials.

**Files Changed**:

- `.env.example` - added txt2crs deployment and container path defaults.
- `backend/.env.example` - added txt2crs host-development path defaults.
- `.env` and `backend/.env` - synchronized ignored local placeholders.

**Verification**:

- Command/check: donor-name search plus direct backend settings import
  - Result: PASS - no donor defaults remain in examples.
  - Evidence: settings printed `txt2crs` and all five expected local paths.
- BQC contract alignment check: PASS - example values satisfy the same path
  validator used at runtime.
- UI product-surface check: N/A - environment documentation only.
- UI craft check: N/A - environment documentation only.

---

### Task T010 - Wire Compose Engine State

**Started**: 2026-07-19 09:16 IDT
**Completed**: 2026-07-19 09:19 IDT
**Duration**: 3 minutes

**Notes**:

- Passed all five validated path settings to prestart and backend.
- Mounted one named volume at the image-owned state root only for the runtime
  backend, independently from the PostgreSQL data volume.
- Kept the loopback research port unpublished.

**Files Changed**:

- `docker-compose.yml` - added engine environment, backend state mount, and
  named volume.
- `backend/tests/scripts/test_container_contract.py` - asserted the
  image-owned mount target and volume separation.

**Verification**:

- Command/check: three focused Compose contract tests
  - Result: PASS - 3 passed.
  - Evidence: environment, volume separation, and unpublished-port contracts
    hold.
- Command/check: `docker compose config --quiet` and rendered JSON inspection
  - Result: PASS - configuration rendered successfully.
  - Evidence: five engine paths, `/var/lib/txt2crs` named mount, and separate
    `app-db-data` plus `txt2crs-state` volumes are present.
- BQC state-boundary check: PASS - persistent data has one explicit owner and
  no engine port crosses the container boundary.
- UI product-surface check: N/A - Compose only.
- UI craft check: N/A - Compose only.

---

### Task T011 - Preserve The Safe Local Override

**Started**: 2026-07-19 09:19 IDT
**Completed**: 2026-07-19 09:20 IDT
**Duration**: 1 minute

**Notes**:

- Documented that the local override inherits `USER appuser` from the
  development image and must not replace it.
- Renamed the OpenTelemetry fallback service identity to txt2crs while
  preserving the one-process reload command.

**Files Changed**:

- `docker-compose.override.yml` - clarified non-root inheritance and removed
  the donor tracing fallback.

**Verification**:

- Command/check: focused development override contract test
  - Result: PASS - 1 passed.
  - Evidence: reload remains enabled and no worker multiplier is present.
- Command/check: Compose render plus donor/root/worker search
  - Result: PASS - config rendered; no donor fallback, root user, or workers
    override remains.
- BQC concurrency check: PASS - local development preserves the same
  single-process topology.
- UI product-surface check: N/A - Compose only.
- UI craft check: N/A - Compose only.

---

### Task T012 - Add Shared Frontend Branding

**Started**: 2026-07-19 09:21 IDT
**Completed**: 2026-07-19 09:21 IDT
**Duration**: 1 minute

**Notes**:

- Wrote the unit contract first and observed the expected missing-module
  failure.
- Added one module-level product constant and title helper with trimmed
  fallback behavior; no React state or render-time allocation is needed.

**Files Changed**:

- `frontend/src/lib/branding.test.ts` - added three branding contract tests.
- `frontend/src/lib/branding.ts` - added canonical product and page-title
  helpers.

**Verification**:

- Command/check: pre-implementation focused Vitest run
  - Result: PASS - failing-first gate behaved as expected.
  - Evidence: suite failed because `./branding` did not exist.
- Command/check: focused Vitest, Biome, and frontend TypeScript checks
  - Result: PASS - 3 tests passed; 2 files clean; typecheck exited zero.
- BQC contract alignment check: PASS - all route consumers will use one typed
  title contract.
- UI product-surface check: N/A - helper is not rendered until T013.
- UI craft check: N/A - no rendered change yet.

---

### Task T013 - Apply Truthful Product Identity

**Started**: 2026-07-19 09:21 IDT
**Completed**: 2026-07-19 09:25 IDT
**Duration**: 4 minutes

**Notes**:

- Routed all document titles through the shared helper and replaced donor
  names in base HTML, logo metadata, wordmark SVGs, and the footer.
- Kept the existing routes and visual language while changing the temporary
  vector wordmark text to txt2crs.
- Rendered QA found both TanStack devtool launchers in the normal product
  viewport. Removed them from the root route to keep diagnostics out of the
  learner surface and reduce the production bundle.

**Files Changed**:

- `frontend/index.html`, `frontend/src/lib/branding.ts`, and nine route modules
  - standardized txt2crs document titles.
- `frontend/src/components/Common/Logo.tsx`,
  `frontend/src/components/Common/Footer.tsx`, and four existing SVG assets -
  replaced visible and accessible donor identity.
- `frontend/src/routes/__root.tsx` - removed normal-surface devtool launchers.

**Verification**:

- Command/check: focused Vitest, Biome, TypeScript, and donor-name search
  - Result: PASS - 3 tests passed; lint/typecheck clean; no donor product name
    remains in HTML or application source.
- Command/check: Playwright login QA at 1440x900 and 390x844
  - Result: PASS - both URLs and `Log in | txt2crs` titles matched, meaningful
    content rendered, no Vite overlay or console problems appeared, and the
    password reveal control changed `type=password` to `type=text`.
- UI product-surface check: PASS - desktop and mobile screenshots contain
  product content only; the initially observed devtool controls were removed.
- UI craft check: PASS - existing hierarchy, responsive split layout, focus
  styling, and mobile form spacing remain intact.

**BQC Fixes**:

- Product surface discipline: removed unconditionally rendered router/query
  devtool controls (`frontend/src/routes/__root.tsx`).
- Accessibility: retained labeled password reveal and changed all wordmark
  alternatives to the canonical product name.

---

### Task T014 - Add Baseline Tests To Repository Validation

**Started**: 2026-07-19 09:25 IDT
**Completed**: 2026-07-19 09:26 IDT
**Duration**: 1 minute

**Notes**:

- Added the database-free settings and container suites to both JSON and
  human-readable backend validation.
- Kept the existing note that full route coverage still requires PostgreSQL.
- The first full backend check found one format drift in the new validator;
  Ruff formatted it before the task was closed.

**Files Changed**:

- `scripts/validate-changes.sh` - added deterministic baseline test gates.
- `backend/app/core/config.py` - applied repository Ruff formatting.

**Verification**:

- Command/check: `./scripts/validate-changes.sh backend --json`
  - Result: PASS - 4 of 4 steps passed.
  - Evidence: lint, format, strict mypy, and 25 focused baseline tests are
    green.
- UI product-surface check: N/A - validation wiring only.
- UI craft check: N/A - validation wiring only.

---

### Task T015 - Add The Production Runtime Smoke

**Started**: 2026-07-19 09:26 IDT
**Completed**: 2026-07-19 09:27 IDT
**Duration**: 1 minute

**Notes**:

- Added an executable, credential-free script that builds the production
  target and checks its configured user and exact one-process command.
- Added real container checks for engine import, UID 1001, `0700` state,
  `0600` files, and marker reopen through a replacement container.
- Used an idempotent exit trap to remove temporary containers and the named
  volume after success, failure, or interruption.

**Files Changed**:

- `scripts/verify-production-baseline.sh` - added the production image smoke.

**Verification**:

- Command/check: executable-bit check plus `bash -n`
  - Result: PASS - script is executable and syntax is valid.
  - Evidence: targeted inspection found cleanup trap, image command, engine
    import, UID/mode assertions, and replacement-container read.
- BQC resource cleanup check: PASS - all temporary Docker resources are
  covered by the idempotent trap.
- UI product-surface check: N/A - verification script only.
- UI craft check: N/A - verification script only.

---

### Task T016 - Run The Focused Regression Set

**Started**: 2026-07-19 09:28 IDT
**Completed**: 2026-07-19 09:28 IDT
**Duration**: 1 minute

**Notes**:

- Ran every failing-first contract together after implementation.
- No assertion required weakening and no additional defect was found.

**Files Changed**:

- None - verification-only task.

**Verification**:

- Command/check: focused backend settings and container pytest commands
  - Result: PASS - 18 settings tests and 7 container tests passed.
- Command/check: focused frontend Vitest, Biome, and TypeScript commands
  - Result: PASS - 3 tests passed; lint and typecheck clean.
- BQC priority spot-check: PASS - trust boundaries, resource cleanup,
  concurrency topology, contract alignment, and product-surface discipline
  remain covered.
- UI product-surface check: PASS - T013 desktop/mobile evidence remains
  authoritative for the unchanged rendered code.
- UI craft check: PASS - no rendered code changed after T013.

---

### Task T017 - Run The Backend Quality Gate

**Started**: 2026-07-19 09:29 IDT
**Completed**: 2026-07-19 09:29 IDT
**Duration**: 1 minute

**Notes**:

- Ran the repository backend selector after the focused regression checkpoint.

**Files Changed**:

- None - verification-only task.

**Verification**:

- Command/check: `./scripts/validate-changes.sh backend`
  - Result: PASS - all backend checks passed.
  - Evidence: strict mypy, Ruff lint, Ruff format, and the 25-test baseline
    contract gate are green.
- UI product-surface check: N/A - backend verification only.
- UI craft check: N/A - backend verification only.

---

### Task T018 - Run The Engine Quality And Build Gates

**Started**: 2026-07-19 09:29 IDT
**Completed**: 2026-07-19 09:29 IDT
**Duration**: 1 minute

**Notes**:

- Ran all engine checks from the package directory so its own pyproject
  configuration applied.

**Files Changed**:

- `backend/dist/txt2crs-0.3.2.tar.gz` and
  `backend/dist/txt2crs-0.3.2-py3-none-any.whl` - rebuilt package artifacts.

**Verification**:

- Command/check: engine Ruff, mypy, pytest, and `uv build --package txt2crs`
  - Result: PASS - all four gates passed.
  - Evidence: 103 typed source files clean; 223 tests passed, 1
    credential-gated live test skipped; sdist and wheel built.
- UI product-surface check: N/A - engine verification only.
- UI craft check: N/A - engine verification only.

---

### Task T019 - Run The Frontend Quality And Build Gates

**Started**: 2026-07-19 09:30 IDT
**Completed**: 2026-07-19 09:30 IDT
**Duration**: 1 minute

**Notes**:

- Ran the complete frontend source check, unit suite, and optimized build.
- Production chunks no longer include the removed router/query devtool
  launchers.

**Files Changed**:

- `frontend/dist/` - rebuilt ignored production output.

**Verification**:

- Command/check: Biome, `npm run typecheck`, `npm run test:unit`, and
  `npm run build`
  - Result: PASS - all four gates passed.
  - Evidence: 124 files clean, 5 test files/18 tests passed, 2,192 modules
    transformed, and the production build completed.
- UI product-surface check: PASS - production output contains no devtool
  chunk and T013 render evidence remains green.
- UI craft check: PASS - desktop and mobile QA already covered the affected
  surface.

---

### Task T020 - Run Production And Database-Backed Smoke Checks

**Started**: 2026-07-19 09:31 IDT
**Completed**: 2026-07-19 09:33 IDT
**Duration**: 2 minutes

**Notes**:

- Rendered the Compose configuration and ran the real production image smoke.
- Preserved the unrelated older boilerplate stack that owned port 5447 and
  used an isolated PostgreSQL 18.4 container on localhost:5448.
- Applied every Alembic migration, ran login/user-signup/item route coverage,
  and removed all temporary test containers and volumes afterward.

**Files Changed**:

- None - verification-only task.

**Verification**:

- Command/check: `docker compose config --quiet` and
  `./scripts/verify-production-baseline.sh`
  - Result: PASS - production image built and all runtime assertions passed.
  - Evidence: image imports `txt2crs`, declares `appuser` plus one FastAPI
    process, writes `0700`/`0600` state, and reopens the marker from a
    replacement container.
- Command/check: isolated PostgreSQL migration plus login/users/items pytest
  run
  - Result: PASS - all migrations applied and 53 route tests passed.
- Command/check: temporary Docker resource search
  - Result: PASS - no baseline writer/reader, session database, or temporary
    baseline volume remains.
- BQC resource cleanup check: PASS - both scripted and database test resources
  were released.
- UI product-surface check: PASS - existing login/signup behavior remained
  green under route coverage; rendered login evidence is recorded in T013.
- UI craft check: PASS - no visual code changed after T013.

---

### Task T021 - Complete The Final Encoding And Evidence Audit

**Started**: 2026-07-19 09:33 IDT
**Completed**: 2026-07-19 09:34 IDT
**Duration**: 1 minute

**Notes**:

- Normalized the two remaining pre-existing non-ASCII separators in modified
  files and audited every tracked or untracked session file for ASCII and LF.
- Re-ran the full repository validation selector after the final edits.

**Files Changed**:

- `frontend/src/components/Common/Footer.tsx` - replaced the non-ASCII
  separator with an ASCII product footer separator.
- `scripts/validate-changes.sh` - normalized one existing comment separator.
- `.spec_system/specs/phase00-session01-baseline-container-and-state/implementation-notes.md`
  - finalized task evidence and checkpoint.

**Verification**:

- Command/check: changed-file ASCII/CRLF scan, `git diff --check`, script
  syntax, and `docker compose config --quiet`
  - Result: PASS - no encoding, line-ending, whitespace, syntax, or Compose
    errors.
- Command/check: `./scripts/validate-changes.sh --json`
  - Result: PASS - 9 of 9 repository validation steps passed.
  - Evidence: backend, engine, and frontend lint, format, type, focused tests,
    and the 223-test engine suite are green.
- BQC priority spot-check: PASS - trust boundaries, cleanup, concurrency,
  failure behavior, contract alignment, and product-surface discipline are
  covered by task evidence.
- UI product-surface check: PASS - desktop/mobile screenshots and interaction
  evidence are recorded under T013.
- UI craft check: PASS - the affected login surface remains responsive,
  accessible, and free of diagnostics.

---

## Blockers And Solutions

### Blocker 1: Missing Local Environment Files

**Description**: Compose interpolation and backend settings import failed
because the ignored root and backend `.env` files were absent.
**Impact**: Environment and database prerequisite checks.
**Resolution**: Created ignored local development files from the committed
examples with placeholder-only local values.
**Time Lost**: 2 minutes.

### Blocker 2: Existing Service Owns The Default PostgreSQL Port

**Description**: An older `python-react-boilerplate` Compose project already
binds host port 5447, and its unknown local password does not match the new
placeholder environment.
**Impact**: Migration and backend smoke prerequisites only; no database schema
changes are in this session.
**Resolution**: Preserved the unrelated running stack and started a temporary,
isolated PostgreSQL 18.4 container on localhost port 5448 for the T020 migration
and route checks. The temporary container was removed after verification.
**Time Lost**: 2 minutes.

---

## Design Decisions

### Decision 1: Treat The Session As Cross-Cutting

**Context**: Docker, shell settings, engine import, and frontend metadata span
all registered packages.
**Options Considered**:

1. Declare `backend` only - simpler package filtering but falsely excludes
   required frontend and root deployment files.
2. Use `Package: null` - accurately represents the bounded cross-package work.

**Chosen**: `Package: null`.
**Rationale**: The session spec and task paths intentionally span root,
backend, engine verification, and narrow frontend branding.

---

## Checkpoint

**Completed Through**: T021.

**Checks Run**:

- Full repository validation: 9 of 9 steps passed.
- Engine package build: PASS (223 tests passed, 1 live-gated skip).
- Frontend unit/build/rendered QA: PASS at 1440x900 and 390x844.
- Production image and persistent volume smoke: PASS.
- Database migrations and 53 shell route tests: PASS.
- ASCII, LF, diff whitespace, and Compose configuration: PASS.

**Scope Review**: The work remains confined to the Phase 00 image, topology,
path settings, narrow identity cleanup, and regression gates.

**Next Task**: Run `creview` across all changes since base commit
`c26350a3f60f9b841762ad7ccbf52f65c2bdcbce`.
