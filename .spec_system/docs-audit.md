# Documentation Audit

**Date:** 2026-07-19
**Project:** txt2crs
**Audit mode:** Phase-focused, Phase 00
**Phase base:** `c26350a3f60f9b841762ad7ccbf52f65c2bdcbce`
**Result:** PASS with two organizational decisions and one remote-CI blocker

## Scope

The deterministic analyzer reports Phase 00 complete, one completed session,
and three registered packages. The Phase 00 implementation notes and the diff
from the first session's base commit supplied the change manifest.

During this audit, the owner corrected an inherited deployment assumption:
repository-root Docker Compose is the complete project deployment scope.
ADR-0008 now records that decision. Active hosted deployment workflows,
platform tooling, and platform variables were removed. A future hosted
platform is not selected and is not a documentation gap.

## Coverage

| Area | Required | Found | Status |
|------|----------|-------|--------|
| Root documentation | 3 | 3 | README, CONTRIBUTING, and LICENSE present |
| Standard `docs/` groups | 9 | 9 | 8 current; CODEOWNERS identity requires owner decision |
| ADR artifacts | 2 baseline | 9 total | Index, template, and seven decision records present |
| Registered package READMEs | 3 | 3 | Backend shell, engine, and frontend covered |

## Files Created

- `.spec_system/docs-audit.md`
- `docs/adr/0008-local-only-deployment-scope.md`

## Files Renamed

- `docs/ENVIRONMENTS.md` to `docs/environments.md`
- `docs/adr/README.md` to `docs/adr/README_adr.md`

Both renames enforce the repository documentation naming rules.

## Files Updated

### Entry Points and Package Guides

- `README.md`
- `CONTRIBUTING.md`
- `llms.txt`
- `backend/README_backend.md`
- `backend/tests/README_backend_tests.md`
- `backend/packages/txt2crs/README_txt2crs.md`
- `backend/packages/txt2crs/docs/README_txt2crs_docs.md`
- `backend/packages/txt2crs/docs/IMPLEMENTATION_COMPLIANCE.md`
- `frontend/README_frontend.md`

### Architecture, Development, and Operations

- `docs/README_docs.md`
- `docs/ARCHITECTURE.md`
- `docs/CONFIGURATION.md`
- `docs/environments.md`
- `docs/FILE_ORGANIZATION.md`
- `docs/TXT2CRS_FOLDER_ARCHITECTURE.md`
- `docs/onboarding.md`
- `docs/development.md`
- `docs/deployment.md`
- `docs/deployment-policy.md`
- `docs/local-deploy.md`
- `docs/runbooks/incident-response.md`
- `docs/adr/README_adr.md`
- `docs/adr/0007-coolify-deployment-platform.md`

### API, Security, and Planning

- `docs/api/README_api.md`
- `docs/SECURITY.md`
- `docs/CHANGELOG.md`
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md`
- `.spec_system/PRD/PRD.md`
- `.spec_system/CONSIDERATIONS.md`
- `.spec_system/CONVENTIONS.md`
- `.spec_system/SECURITY-COMPLIANCE.md`
- `.spec_system/audit/known-issues.md`
- `.spec_system/pipeline/pipeline.md`
- `.spec_system/infra/infra.md`

## Verified Current

- Root and package licenses exist; no legal scope was invented.
- The engine package README and implementation-compliance map match the
  reusable package boundary.
- The current HTTP docs list only routes returned by FastAPI OpenAPI; course
  generation routes are explicitly absent.
- The one-command quick start is repository-root Docker Compose.
- Backend and frontend health paths match code and container checks.
- The incident runbook preserves both named volumes by default.
- All subdirectory documentation indexes use unique `README_<scope>.md`
  names; only the repository root uses `README.md`.
- Docker Compose is the only deployment target. GitHub Actions has validation
  workflows but no environment-deployment workflow.

## External Decision Gaps

1. `docs/CODEOWNERS` names `@aiwithapex`, but GitHub resolves neither a user
   nor organization by that name. Replacing it requires the repository owner
   to select an accountable GitHub identity.
2. The repository has no verified security mailbox and GitHub private
   vulnerability reporting is unavailable. The owner must select a durable
   private reporting channel before any public release.
3. GitHub Actions jobs cannot schedule because of the account billing/spending
   limit. Local equivalents pass, but remote CodeQL remains unavailable.

No hosted-platform decision is needed for this project: hosting is explicitly
outside scope.

## Evidence Ledger

| Area | Document | Codebase or Spec Evidence | Result |
|------|----------|---------------------------|--------|
| Project state | This report | `.spec_system/scripts/analyze-project.sh --json` | Phase 00 complete; 3 packages; 1 completed session |
| Phase manifest | This report | First spec base plus `git diff --name-only c26350a3...HEAD` | Phase-focused scope established |
| Product truth | `README.md`, `ARCHITECTURE.md` | Phase 00 implementation notes and current shell/package trees | Updated |
| Quick start | `README.md`, onboarding, deployment | Isolated `docker compose ... up --detach --build --wait` | Backend, frontend, and database healthy |
| Local deployment scope | Deployment docs, ADR-0008 | Owner direction; absence contract in `test_container_contract.py` | Hosted workflows/tooling removed; 10 tests pass |
| Frontend health | Deployment docs and frontend README | `nginx.conf`, `frontend/Dockerfile`, focused Vitest | `/health` JSON and image check verified; 5 tests pass |
| Backend health | Architecture and deployment docs | `backend/app/api/routes/utils.py`; isolated HTTP smoke | Readiness and liveness paths verified |
| API contract | `docs/api/README_api.md` | `app.openapi()["paths"]` targeted inspection | Current auth, user, item, utility paths documented |
| Environment behavior | Configuration and environments docs | `backend/app/core/config.py`, rate limiting, Compose files | Current local and inactive validation profiles documented |
| Private state | Architecture and operations docs | Typed settings, Dockerfiles, Compose mount, replacement-container smoke | Fixed local paths and volume ownership documented |
| Package coverage | Package READMEs | Analyzer `packages` array and package manifests | 3 of 3 present |
| README naming | Documentation index and file guide | Filesystem search for subdirectory `README.md` | Root is the only authored `README.md` |
| Workflow safety | Pipeline records | `actionlint .github/workflows/*.yml`; `zizmor` | 9 validation workflows pass, no Zizmor findings |
| CODEOWNERS | `docs/CODEOWNERS` | GitHub user and organization API lookups for `aiwithapex` | External owner decision required |
| Security contact | `docs/SECURITY.md` | Repository security endpoint inspection | External owner decision required |
| Links and ASCII | All audited documentation | Local Markdown link scan and non-ASCII scan | PASS after this report was created |

## Next Action

PRD.md defines Phases 01 through 05 as not started, while state tracking
currently ends at completed Phase 00. The two-source rule therefore selects
`phasebuild`; that workflow owns reconciliation and Phase 01 creation.
