# Code Review and Repair Report

**Session ID**: `phase00-session01-baseline-container-and-state`
**Package**: cross-cutting (`backend-shell`, `txt2crs-engine`, `frontend`)
**Reviewed**: 2026-07-19
**Base Commit**: `c26350a3f60f9b841762ad7ccbf52f65c2bdcbce`
**Scope**: All changes since the base commit (uncommitted work plus
mid-session commits)
**Result**: RESOLVED

## Review Surface

**Files reviewed** (all changes since the base commit):

- `.env.example` - tracked-modified
- `backend/.env.example` - tracked-modified
- `backend/Dockerfile` - tracked-modified
- `backend/app/core/config.py` - tracked-modified
- `docker-compose.override.yml` - tracked-modified
- `docker-compose.yml` - tracked-modified
- `frontend/index.html` - tracked-modified
- `frontend/package-lock.json` - tracked-modified
- `frontend/package.json` - tracked-modified
- `frontend/public/assets/images/apex-icon-light.svg` - tracked-modified
- `frontend/public/assets/images/apex-icon.svg` - tracked-modified
- `frontend/public/assets/images/apex-logo-light.svg` - tracked-modified
- `frontend/public/assets/images/apex-logo.svg` - tracked-modified
- `frontend/src/components/Common/Footer.tsx` - tracked-modified
- `frontend/src/components/Common/Logo.tsx` - tracked-modified
- `frontend/src/routes/__root.tsx` - tracked-modified
- `frontend/src/routes/_layout/admin.tsx` - tracked-modified
- `frontend/src/routes/_layout/forbidden.tsx` - tracked-modified
- `frontend/src/routes/_layout/index.tsx` - tracked-modified
- `frontend/src/routes/_layout/items.tsx` - tracked-modified
- `frontend/src/routes/_layout/settings.tsx` - tracked-modified
- `frontend/src/routes/login.tsx` - tracked-modified
- `frontend/src/routes/recover-password.tsx` - tracked-modified
- `frontend/src/routes/reset-password.tsx` - tracked-modified
- `frontend/src/routes/signup.tsx` - tracked-modified
- `scripts/validate-changes.sh` - tracked-modified
- `.spec_system/CONSIDERATIONS.md` - untracked text
- `.spec_system/CONVENTIONS.md` - untracked text
- `.spec_system/PRD/PRD.md` - untracked text
- `.spec_system/PRD/phase_00/PRD_phase_00.md` - untracked text
- `.spec_system/PRD/phase_00/session_01_baseline_container_and_state.md` -
  untracked text
- `.spec_system/SECURITY-COMPLIANCE.md` - untracked text
- `.spec_system/archive/PRD/PRD-backup-20260719-083759.md` - untracked text
- `.spec_system/scripts/analyze-project.sh` - untracked shell script
- `.spec_system/scripts/check-prereqs.sh` - untracked shell script
- `.spec_system/scripts/common.sh` - untracked shell script
- `.spec_system/specs/phase00-session01-baseline-container-and-state/code-review.md`
  - untracked review report created during this gate
- `.spec_system/specs/phase00-session01-baseline-container-and-state/implementation-notes.md`
  - untracked text
- `.spec_system/specs/phase00-session01-baseline-container-and-state/spec.md` -
  untracked text
- `.spec_system/specs/phase00-session01-baseline-container-and-state/tasks.md`
  - untracked text
- `.spec_system/state.json` - untracked JSON
- `backend/tests/core/test_txt2crs_settings.py` - untracked Python test
- `backend/tests/scripts/test_container_contract.py` - untracked Python test
- `frontend/src/lib/branding.test.ts` - untracked TypeScript test
- `frontend/src/lib/branding.ts` - untracked TypeScript source
- `scripts/verify-production-baseline.sh` - untracked shell script

There were 46 files in the final review surface: 26 tracked modifications and
20 untracked files. There were no staged changes and no commits after the base
commit.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`,
`git ls-files --others --exclude-standard`

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `docker-compose.yml:95` - Compose accepted a custom state mount target, but
  the image provisions UID/GID 1001 ownership only at `/var/lib/txt2crs`. A
  fresh volume mounted elsewhere was root-owned and unwritable by `appuser`.
  Reproduction: a temporary volume mounted at `/srv/txt2crs` failed with
  `Permission denied`. | Fix: pinned all container engine paths and the named
  volume target to the image-owned directories, kept host-only Settings
  overrides in `backend/.env.example`, and hardened the Compose contract test.
  | Status: FIXED
- `backend/tests/core/test_txt2crs_settings.py:15` - the focused Settings
  tests disabled dotenv files but still inherited exported process variables.
  A full-suite run under an explicit txt2crs environment produced 7 failures,
  so the claimed deterministic contract did not hold in CI or configured
  operator shells. | Fix: added an autouse fixture that removes only the five
  path variables under test and proved the suite passes with conflicting
  ambient values exported. | Status: FIXED

### Low

- `.spec_system/scripts/check-prereqs.sh:543` - the project-local prerequisite
  script reported this registered uv/npm monorepo as having no workspace
  manager and omitted the recorded `stack_hint`. | Fix: detect nested
  registered uv workspace manifests and read `stack_hint` with backward
  compatibility for `stack`. | Status: FIXED
- `.spec_system/SECURITY-COMPLIANCE.md:28` - the generated baseline said no
  personal data existed even though the imported authentication shell already
  stores account identity and password hashes. | Fix: recorded the existing
  data inventory and scoped Phase 00 GDPR status to this session's
  non-data-handling changes. | Status: FIXED
- `.spec_system/specs/phase00-session01-baseline-container-and-state/implementation-notes.md:654`
  - the database blocker resolution described a future configuration change
  that was not made. | Fix: recorded the actual isolated PostgreSQL 18.4
  container on port 5448 and its cleanup. | Status: FIXED
- `scripts/verify-production-baseline.sh:12` - ShellCheck SC2155 found three
  declaration/assignment pairs that could mask discovery failures. | Fix:
  separated assignment from `readonly` declarations. | Status: FIXED
- `backend/tests/core/test_txt2crs_settings.py:169` and
  `backend/tests/scripts/test_container_contract.py:67` - regression coverage
  omitted the SQLite symlink endpoint and used repository-wide string counts
  instead of proving private-directory setup in each image stage. The
  repository gate also excluded both new tests from Ruff lint and format
  checks, allowing import/format drift. | Fix: added the database symlink
  case, scoped non-root directory assertions to production and development
  separately, formatted both modules, and extended both validation modes to
  lint and format them. | Status: FIXED
- `frontend/package.json:36` - removal of the learner-visible devtool
  launchers left three direct devtool packages and their transitive nodes
  unused. | Fix: removed the direct dependencies with `npm uninstall` and
  regenerated `package-lock.json`; `npm audit` reported zero vulnerabilities.
  | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- Container paths are intentionally fixed to the directories whose ownership
  is baked into the image. Typed Settings remain configurable for host-only
  development. This is the safest behavior supported by the current non-root
  image; dynamically relocating a named volume would require a separate,
  explicitly designed initialization boundary.
- The four SVG filenames retain the temporary `apex-` prefix because the
  session specification explicitly says to retain temporary assets. Their
  visible text, titles, and image alternatives use `txt2crs`.
- The donor `items` route and table remain because the session specification
  explicitly defers their removal until Phase 03 acceptance coverage exists.
- An extra `uv run --package txt2crs ruff format --check .` probe reports 16
  pre-existing format candidates under the unchanged engine source and tests.
  `git diff --quiet "$BASE" -- backend/packages/txt2crs/src
  backend/packages/txt2crs/tests` confirms they are outside this review
  surface, and the engine's configured required gate is `ruff check .`.
  Reformatting them here would violate the surgical review-scope rule.

## Behavior Changes

- Docker Compose no longer honors custom txt2crs container state paths; it
  pins the validated environment and volume mount to the image-owned paths so
  the non-root runtime can always write a fresh volume.
- The project-local prerequisite command now recognizes the nested uv
  workspace and reports package stack hints.
- TanStack router/query devtool launchers and their now-unused direct packages
  are absent from the learner application and optimized dependency graph.

## Evidence Ledger

Every row names the exact command or targeted inspection used.

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Dynamic mount reproduction | `docker run --rm --volume "$volume:/srv/txt2crs" --entrypoint sh txt2crs-baseline:local -eu -c 'touch /srv/txt2crs/probe'` | PASS | Before repair, reproduced `Permission denied`; temporary volume removed |
| Focused backend tests | `cd backend && uv run pytest --confcutdir=tests/core tests/core/test_txt2crs_settings.py -q && uv run pytest --confcutdir=tests/scripts tests/scripts/test_container_contract.py -q` | PASS | 19 settings and 7 deployment tests passed |
| Prerequisite behavior | `bash .spec_system/scripts/check-prereqs.sh --json --env` and `bash .spec_system/scripts/check-prereqs.sh --json --package backend` | PASS | uv workspace and backend stack hint reported; no issues |
| Frontend tests/build | `cd frontend && npm run typecheck && npm run test:unit && npm run build` | PASS | 5 files / 18 tests passed; 2,192 modules built |
| Shell linter | `shellcheck scripts/verify-production-baseline.sh scripts/validate-changes.sh .spec_system/scripts/analyze-project.sh .spec_system/scripts/check-prereqs.sh .spec_system/scripts/common.sh` | PASS | No findings after SC2155 repair |
| Ambient-environment regression | `TXT2CRS_STATE_ROOT=/tmp/ambient-state ... uv run pytest --confcutdir=tests/core tests/core/test_txt2crs_settings.py -q` | PASS | 19 tests passed with all five conflicting path variables exported |
| Backend tests | Temporary PostgreSQL 18.4, `uv run alembic upgrade head`, then `uv run pytest tests/ -q` | PASS | All migrations applied; 180 tests passed; temporary container removed |
| Engine tests | `cd backend/packages/txt2crs && uv run --package txt2crs pytest -q` | PASS | 223 passed; 1 explicitly live-gated test skipped |
| Production runtime | `./scripts/verify-production-baseline.sh` | PASS | Production import, appuser, one process, private modes, and replacement-container reopen passed |
| Development runtime | `docker build --target development ...` plus non-root `import txt2crs` and image inspection | PASS | Imported `txt2crs` as UID 1001; command and user matched; temporary image removed |
| Compose topology | `docker compose config --format json \| jq ...` plus a conflicting environment override | PASS | Fixed image-owned paths, separate named volume, and zero published port 8765 |
| Repository gate | `./scripts/validate-changes.sh --json` | PASS | 9 of 9 backend, engine, and frontend steps passed |
| Linter | Repository gate plus targeted ShellCheck | PASS | Ruff, Biome, and ShellCheck clean on the review surface |
| Formatter | Backend Ruff review-surface check and frontend Biome repository gate | PASS | 37 backend files formatted; frontend clean; engine-only drift is unchanged and out of scope as documented above |
| Type checker | Repository gate | PASS | Backend mypy, engine mypy (103 files), and frontend TypeScript passed |
| Encoding and cleanup | Review-surface ASCII/CRLF loop, `git diff --check "$BASE"`, and temporary Docker resource search | PASS | 46 files clean; no temporary review container or volume remained |
| Final diff re-read | `git diff "$BASE"` plus all untracked files | PASS | 26 tracked modifications and 20 untracked files re-read; no unresolved issue or debug artifact remained |

## Summary

1. Reviewed the complete 46-file surface across the application shell,
   engine/deployment contract, frontend identity, tests, and Apex artifacts.
2. Found 0 critical, 0 high, 2 medium, and 6 low issues; every finding is
   repaired.
3. Deliberately retained only the temporary asset filenames and donor items
   domain that the session specification explicitly defers.
4. The full repository, database-backed backend, engine, frontend, production
   and development images, Compose, formatting, typing, encoding, cleanup, and
   final diff evidence is green.
