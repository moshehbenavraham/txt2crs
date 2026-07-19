# Documentation Audit

**Date:** 2026-07-19
**Project:** txt2crs
**Audit mode:** Phase-focused, Phase 01
**Phase base:** `c56fa822e2f5f62d64ea427ae56739fd5c17ce4d`
**Result:** PASS with two organizational decisions and one remote-CI blocker

## Scope

The deterministic analyzer reports Phase 01 complete with five completed
sessions in `backend/packages/txt2crs` and three registered packages overall.
The first Phase 01 session base plus `git diff --name-only` produced a
145-file phase manifest that includes the engine sessions and the audit,
pipeline, infrastructure, carryforward, and documentation transition work.

This was a phase-focused audit. All five Phase 01 implementation notes were
read. Deep updates target the engine application boundary, recovery tooling,
master project status, and architecture. Standard root/docs/package coverage
and the unchanged HTTP contract were still verified.

## Coverage

| Area | Required | Found | Status |
|------|----------|-------|--------|
| Root documentation | 3 | 3 | README, CONTRIBUTING, and LICENSE present |
| Standard `docs/` groups | 9 | 9 | 8 current; CODEOWNERS identity requires owner decision |
| ADR artifacts | 2 baseline | 9 total | Index, template, and seven decision records present |
| Registered package READMEs | 3 | 3 | Backend shell, engine, and frontend covered |

## Files Created

None. Every required documentation surface already exists.

## Files Updated

- `README.md` - Records Phases 00/01 complete, the public engine facade, and
  the authoritative build-enabled one-command start.
- `docs/ARCHITECTURE.md` - Replaces the planned facade with the implemented
  application/factory, preparation, managed-provider, recovery, and
  owner-erasure boundaries.
- `backend/packages/txt2crs/README_txt2crs.md` - Corrects the two-stage
  preparation flow, durable disabled-notification semantics, and exact
  `learner_age_group` contract field.
- `docs/development.md` - Links the complete PostgreSQL plus private-state
  backup/restore procedure and warns that the legacy database-only helper is
  incomplete.
- `.spec_system/PRD/PRD.md` - Corrects phase progress and removes a stale fixed
  release-version success criterion.
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` - Marks Phase 01 and
  all five sessions complete while relabeling the original repository survey
  as historical starting-state evidence.
- `docs/CHANGELOG.md` - Records the Phase 01 documentation synchronization.
- `.spec_system/docs-audit.md` - Replaces the Phase 00 report with this
  evidence-backed Phase 01 audit.

## Verified Current

- `CONTRIBUTING.md` still reflects tests-first work, package boundaries,
  generated-client ownership, and current package commands.
- Root and package licenses exist; no legal scope was invented or changed.
- `backend/README_backend.md`, `frontend/README_frontend.md`, and
  `docs/api/README_api.md` correctly state that generation routes and the
  learner UI are not implemented yet.
- The generated OpenAPI snapshot still contains only authentication, users,
  temporary items, password recovery, health, and test-email paths.
- `docs/onboarding.md` and the root quick start use repository-root Docker
  Compose; the complete build/wait topology passed the Phase 01 transition
  audit.
- Deployment, local deployment, environment, security, and incident-response
  docs match the validated complete backup/restore scripts and owner-only
  bundle contract.
- All registered packages have unique package README names. The root is the
  only tracked authored `README.md`.
- Current release metadata is synchronized at `0.5.0` across `VERSION`, the
  engine manifest, lockfile, versioning guide, changelog, commit, and tag.

## External Decision Gaps

1. `docs/CODEOWNERS` names `@aiwithapex`, but GitHub currently resolves neither
   a user nor organization by that name. Replacing it requires the repository
   owner to choose an accountable GitHub identity.
2. The private repository has no verified project security mailbox and its
   private-vulnerability-reporting API endpoint is unavailable. The owner must
   choose a durable private reporting channel before public release.
3. GitHub Actions jobs still cannot schedule because account billing rejects
   every job before runner assignment. Local equivalents pass, but remote
   CodeQL remains unavailable.

No hosted-platform decision is required: local Docker is the explicit complete
deployment scope under ADR-0008.

## Evidence Ledger

| Area | Document | Codebase or Spec Evidence | Result |
|------|----------|---------------------------|--------|
| Project state | This report | `.spec_system/scripts/analyze-project.sh --json` | Phase 01 complete; 3 packages; 5 Phase 01 sessions |
| Phase manifest | This report | First spec base plus `git diff --name-only c56fa822...HEAD` | 145-file phase-focused scope |
| Semantic changes | README, architecture, engine guide | All five Phase 01 `implementation-notes.md` files and implementation summaries | Current engine boundary documented |
| Public application boundary | README and architecture | `application/config.py`, `facade.py`, `factories.py`, `owner_lifecycle.py`; 444-test final engine evidence | Updated |
| Request/preparation flow | Engine guide | `jobs/requests.py`, `jobs/preparation.py`, `generation/pipeline.py` | Corrected exact field and stage ordering |
| Quick start | Root README and onboarding | `docker-compose.yml`, override, Phase 01 audit isolated full-stack build/health proof | Current |
| Complete recovery | Development and operations docs | `backup-local-state.sh`, `restore-local-state.sh`, safe archive helper, 6 contract tests, isolated two-store restore proof | Current |
| API contract | API and backend guides | `jq '.paths' frontend/openapi.json`; deterministic generated-client hook | No generation route overstatement |
| Package coverage | Package READMEs | Analyzer `packages` array and filesystem inspection | 3 of 3 present |
| README naming | Documentation rules | `git ls-files` README inspection | Root is the only tracked `README.md` |
| Version | PRD, system plan, versioning | `VERSION`, engine `pyproject.toml`, `uv.lock`, changelog, `v0.5.0` | Stale `0.4.0` target removed |
| Link integrity | Audited Markdown | Local target scan over root, standard docs, and package guides | 120 local links resolve |
| Encoding/format | Files changed in this gate | ASCII scan, LF/file inspection, `git diff --check` | PASS |
| CODEOWNERS | `docs/CODEOWNERS` | `gh api users/aiwithapex`; `gh api orgs/aiwithapex` | Both return 404; external decision |
| Security contact | `docs/SECURITY.md` | Private repository metadata and vulnerability-reporting endpoint inspection | External decision |
| Remote CI | Known issues and pipeline report | Current zero-step GitHub runs plus local security equivalents | Billing blocker remains |

## Next Action

The master PRD defines Phases 02 through 05 as not started, while state
tracking currently ends at completed Phase 01. The two-source rule therefore
selects `phasebuild`; it owns reconciliation and creation of Phase 02.
