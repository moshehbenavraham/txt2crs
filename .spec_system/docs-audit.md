# Documentation Audit

**Date:** 2026-07-20
**Project:** txt2crs
**Audit mode:** Phase-focused, Phase 03
**Phase base:** `3dfbd01cf771a67d94b783fdfe269dcb9d357161`
**Result:** PASS with legal/organizational decisions and one remote-CI blocker

## Scope

The deterministic analyzer reports Phase 03 complete with three completed
sessions and three registered packages: backend shell, reusable engine, and
frontend. The first Phase 03 session base plus `git diff --name-only` produced
a 128-file committed phase manifest. The transition worktree adds a 62-file
manifest covering frontend donor retirement, audit, pipeline, infrastructure,
carryforward, and documentation corrections.

This was a phase-focused audit. All three Phase 03 implementation summaries,
implementation notes, security records, session specifications, and validation
records were read. Deep updates target durable submission, owner-scoped job
reads, artifact delivery, restart behavior, coordinated account erasure, donor
retirement, the transitional learner workspace, and deployment-helper
execution. Standard root, docs, and package coverage was also verified.

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

- `README.md` - Marks Phase 03 complete, records the durable owner-scoped jobs
  API, removes the retired donor-domain claim, and describes the truthful
  transitional course workspace.
- `docs/ARCHITECTURE.md` - Describes the current static course overview and
  reserves interactive submission, progress, and results for Phase 04.
- `docs/onboarding.md` - Aligns setup guidance with the implemented Phase 03
  API and current authenticated root.
- `docs/local-deploy.md` - Corrects the backend verification command to the
  implemented readiness path.
- `docs/TXT2CRS_FOLDER_ARCHITECTURE.md` - Replaces the stale "routes not
  exposed" statement with the implemented public-facade route boundary.
- `docs/dashboard-design.md` - Makes the Phase 03 transition authoritative,
  marks donor library/Items blueprints as history, and records current route
  and browser-test behavior.
- `backend/packages/txt2crs/README_txt2crs.md` - Replaces future setup-screen
  language with the implemented browser flow and CLI recovery role.
- `.spec_system/PRD/PRD.md` - Reconciles the conflict note with the completed
  Phase 03 table and validated transition evidence.
- `.spec_system/CONSIDERATIONS.md` and
  `.spec_system/SECURITY-COMPLIANCE.md` - Carry forward Phase 03 job privacy,
  stream ownership, cross-store erasure, retention, and release risks.
- `docs/CHANGELOG.md` - Records Phase 03 documentation synchronization,
  frontend donor retirement, and executable deployment helpers.
- `.spec_system/docs-audit.md` - Replaces the Phase 02 report with this
  evidence-backed Phase 03 audit.

## Verified Current

- `CONTRIBUTING.md` still reflects tests-first work, the shell/package
  boundary, generated-client ownership, and current package commands.
- Root and package licenses exist; no legal scope was invented or changed.
- `backend/README_backend.md` and `docs/api/README_api.md` document all five
  job path patterns, durable `202`, idempotency, owner-hidden reads, private
  delivery headers, stream cleanup, restart replay, and account purge.
- `frontend/README_frontend.md` matches the generated route tree: `/` is the
  course overview, `/setup` is privileged setup, and `/items` is absent.
- `docs/development.md`, `docs/environments.md`, `docs/deployment.md`,
  `docs/deployment-policy.md`, and the incident runbook match the validated
  local-only topology, single process, complete backup/restore path, and
  current health endpoints.
- Repository-root Docker Compose remains the only deployment target under
  ADR-0008; no hosted platform or remote environment was invented.
- All registered packages have unique package README names. The root is the
  only tracked authored `README.md`.

## External Decision Gaps

1. `docs/CODEOWNERS` names `@aiwithapex`, but GitHub resolves neither a user
   nor organization by that name. Replacing it requires the repository owner
   to choose an accountable GitHub identity.
2. The private repository has no verified project security mailbox and its
   private-vulnerability-reporting API endpoint returns 404. The owner must
   choose a durable private reporting channel before public release.
3. Formal legal-basis, third-party-transfer, log/state/artifact/backup
   retention, backup erasure, and provider-copy records remain incomplete.
   These require product/legal and operator decisions before real learner data
   can be accepted under a compliant public policy.
4. GitHub Actions jobs at the current Phase 03 commit cannot schedule because
   account billing rejects every job before runner assignment. Local
   equivalents pass, but remote CodeQL remains unavailable.

No hosted-platform decision is required: local Docker is the explicit complete
deployment scope under ADR-0008.

## Evidence Ledger

| Area | Document | Codebase or Spec Evidence | Result |
|------|----------|---------------------------|--------|
| Project state | This report | `.spec_system/scripts/analyze-project.sh --json` | Phase 03 complete; 3 packages; 3 Phase 03 sessions |
| Phase manifest | This report | First spec base plus committed and worktree `git diff --name-only` manifests | 128 committed files and 62 transition files inspected |
| Semantic changes | README, architecture, API, package guides | Three Phase 03 summaries, notes, validations, and security records | Durable jobs, delivery, erasure, and donor retirement documented |
| Public jobs API | API and backend guides | `frontend/openapi.json`, generated client, job routes/schemas, route and acceptance tests | Five job path patterns verified |
| Owner privacy and delivery | API, architecture, incident guide | Public query service, `artifact_response.py`, owner/stream/response tests | Owner-hidden reads and exactly-once cleanup documented |
| Recovery | API, architecture, incident guide | Seven-scenario restart and delivery acceptance matrix | Current |
| Account erasure | API and backend guides | Both user deletion routes, facade purge barrier, cross-store acceptance | Engine-first retryable behavior documented |
| Frontend transition | Root, frontend guide, design guide | Generated route tree, current root route, dashboard tests, 65-test Playwright run | Donor UI absent; static course overview current |
| Local deployment | Deployment guides | `docker compose config --quiet`, script syntax checks, production Compose validation | Commands and topology current |
| Backup/restore | Deployment and incident guides | Isolated destructive PostgreSQL plus engine-volume restore proof | Current |
| Deploy helpers | Changelog and deployment guide | Executable-mode regression; `stat` reports both helpers as 0755 | Direct invocation current |
| Package coverage | Package READMEs | Analyzer package array and filesystem inspection | 3 of 3 present |
| README naming | Documentation rules | `git ls-files` README inspection | Root is the only tracked `README.md` |
| Link integrity | Audited Markdown | Local target scan over 27 root, standard-doc, ADR, runbook, API, architecture, and package-guide files | 91 local links resolve |
| Encoding/format | Files changed in this gate | ASCII scan and `git diff --check` | PASS |
| CODEOWNERS | `docs/CODEOWNERS` | `gh api users/aiwithapex` and `gh api orgs/aiwithapex` | Both return 404; external decision |
| Security contact | `docs/SECURITY.md` | Repository private-vulnerability-reporting endpoint | 404; external decision |
| Privacy posture | Security and environment docs | Fresh cumulative security/compliance synthesis | GDPR remains non-compliant pending policy decisions |
| Remote CI | Pipeline report | Seven zero-step Phase 03 workflow failures plus exact local fallbacks | Billing blocker remains |

## Next Action

The master PRD defines Phases 04 and 05 as unfinished, while state tracking
ends at completed Phase 03. The two-source rule therefore selects
`phasebuild`; it owns reconciliation and creation of Phase 04.
