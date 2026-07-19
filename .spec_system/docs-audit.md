# Documentation Audit

**Date:** 2026-07-19
**Project:** txt2crs
**Audit mode:** Phase-focused, Phase 02
**Phase base:** `0c779c910445e636db01a7bca284a72532ef57b6`
**Result:** PASS with two organizational decisions and one remote-CI blocker

## Scope

The deterministic analyzer reports Phase 02 complete with five completed
sessions and three registered packages: backend shell, reusable engine, and
frontend. The first Phase 02 session base plus `git diff --name-only` produced
a 186-file phase manifest including implementation and the audit, pipeline,
infrastructure, carryforward, and documentation transition work.

This was a phase-focused audit. All five Phase 02 implementation summaries,
implementation notes, security records, session specifications, and
validation records were read. Deep updates target facade composition, the
serial worker, cached readiness, system authentication, operator setup,
configuration, and recovery. Standard root, docs, and package coverage was
also verified.

## Coverage

| Area | Required | Found | Status |
|------|----------|-------|--------|
| Root documentation | 3 | 3 | README, CONTRIBUTING, and LICENSE present |
| Standard `docs/` groups | 9 | 9 | Eight current; CODEOWNERS identity requires owner decision |
| ADR artifacts | 2 baseline | 9 total | Index, template, and seven decision records present |
| Registered package READMEs | 3 | 3 | Backend shell, engine, and frontend covered |

## Files Created

None. Every required documentation surface already exists.

## Files Updated

- `.env.example` - Adds the research switch and empty Tavily secret expected
  by the operator quick-start path.
- `README.md` - Records Phases 00-02 complete, lifespan composition, the
  serial worker, safe system APIs, and the protected setup workspace.
- `docs/ARCHITECTURE.md` - Replaces planned composition and readiness language
  with the implemented service ownership, cache, worker, and authentication
  boundaries.
- `docs/CONFIGURATION.md` - Documents all course-system storage, runtime,
  research, input, run-budget, retry, and admission settings and invariants.
- `docs/environments.md` - Adds the single-process course-system behavior and
  corrects the already-remediated request-metadata logging statement.
- `docs/onboarding.md` - Adds the superuser setup, Tavily, ChatGPT device
  login, and CLI recovery path.
- `docs/runbooks/incident-response.md` - Adds readiness/authentication recovery
  and corrects request-log privacy guidance.
- `frontend/README_frontend.md` - Documents the superuser `/setup` route.
- `.spec_system/PRD/PRD.md` - Marks Phase 02 complete.
- All five Phase 02 session specifications - Reconcile their status with
  completed phase-transition evidence.
- `docs/CHANGELOG.md` - Records the Phase 02 documentation synchronization.
- `.spec_system/docs-audit.md` - Replaces the Phase 01 report with this
  Phase 02 evidence.

## Verified Current

- `CONTRIBUTING.md` still reflects tests-first work, package boundaries,
  generated-client ownership, and current package commands.
- Root and package licenses exist; no legal scope was invented or changed.
- `backend/README_backend.md` and `docs/api/README_api.md` already document the
  authenticated cached-readiness route, superuser device-authentication
  routes, safe fields, cache-only reads, and CLI recovery.
- `backend/packages/txt2crs/README_txt2crs.md` already documents facade
  factories, readiness, authentication, serial execution handles, recovery,
  and owner purge.
- The generated OpenAPI snapshot and generated TypeScript client include the
  three system routes but no learner submission, status, or artifact route.
- `docs/development.md`, deployment guides, and the incident runbook match the
  validated complete PostgreSQL plus private-state backup/restore scripts.
- Repository-root Docker Compose remains the only deployment target under
  ADR-0008; no hosted platform or WAF workflow was invented.
- All registered packages have unique package README names. The root is the
  only tracked authored `README.md`.
- Current release metadata is synchronized at `0.6.0` across `VERSION`, the
  engine manifest, lockfile, versioning guide, changelog archive, release
  commit, and annotated tag target.

## External Decision Gaps

1. `docs/CODEOWNERS` names `@aiwithapex`, but GitHub resolves neither a user
   nor organization by that name. Replacing it requires the repository owner
   to choose an accountable GitHub identity.
2. The private repository has no verified project security mailbox and its
   private-vulnerability-reporting API endpoint is unavailable. The owner must
   choose a durable private reporting channel before public release.
3. GitHub Actions jobs at the Phase 02 release commit cannot schedule because
   account billing rejects every job before runner assignment. Local
   equivalents pass, but remote CodeQL remains unavailable.

No hosted-platform decision is required: local Docker is the explicit complete
deployment scope under ADR-0008.

## Evidence Ledger

| Area | Document | Codebase or Spec Evidence | Result |
|------|----------|---------------------------|--------|
| Project state | This report | `.spec_system/scripts/analyze-project.sh --json` | Phase 02 complete; 3 packages; 5 Phase 02 sessions |
| Phase manifest | This report | First spec base plus `git diff --name-only 0c779c91...` | 186-file phase-focused scope |
| Semantic changes | README, architecture, operator docs | Five Phase 02 implementation summaries and notes | Current composition and setup documented |
| Composition | README and architecture | `txt2crs_lifespan.py`, composition service, worker supervisor, readiness coordinator, auth coordinator | Implemented ownership documented |
| Public system API | API, backend, frontend guides | System routes/schemas, generated OpenAPI and client, shell route tests | Three safe system routes verified |
| Operator setup | Onboarding and frontend guide | `/setup` route, setup components, unit and Playwright coverage | Protected workflow documented |
| Configuration | Configuration and environment guides | `app/core/config.py`, both environment examples, Compose fixed paths | All Phase 02 settings and invariants covered |
| Privacy | Environment and incident guides | Middleware implementation and `test_middleware.py` | Raw query/path parameter/IP claim removed |
| Complete recovery | Development and incident docs | Backup/restore scripts, isolated two-store restore proof | Current |
| Package coverage | Package READMEs | Analyzer package array and filesystem inspection | 3 of 3 present |
| README naming | Documentation rules | `git ls-files` README inspection | Root is the only tracked `README.md` |
| Version | README and versioning | `VERSION`, engine manifest, `uv.lock`, changelog archive, `v0.6.0^{}` | All resolve to release `3dfbd01` |
| Link integrity | Audited Markdown | Local target scan over 34 root, standard-doc, ADR, runbook, API, and package-guide files | 114 local links resolve |
| Encoding/format | Files changed in this gate | ASCII scan and `git diff --check` | PASS |
| CODEOWNERS | `docs/CODEOWNERS` | `gh api users/aiwithapex`; `gh api orgs/aiwithapex` | Both return 404; external decision |
| Security contact | `docs/SECURITY.md` | Private-vulnerability-reporting endpoint inspection | External decision |
| Remote CI | Pipeline report | Seven zero-step release-commit workflow failures plus local fallbacks | Billing blocker remains |

## Next Action

The master PRD defines Phases 03 through 05 as unfinished, while state tracking
currently ends at completed Phase 02. The two-source rule therefore selects
`phasebuild`; it owns reconciliation and creation of Phase 03.
