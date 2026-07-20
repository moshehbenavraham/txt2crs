# Documentation Audit

**Date:** 2026-07-20
**Project:** txt2crs
**Audit mode:** Phase-focused, Phase 04
**Phase base:** `08297e317683ad6cf608e4d9333bfbb819955ef7`
**Result:** PASS with external legal/organizational decisions and one
remote-CI blocker

## Scope

The deterministic analyzer reports Phase 04 complete with two completed
sessions and three registered packages: backend shell, reusable engine, and
frontend. The first Phase 04 session base plus
`git diff --name-only 08297e3..HEAD` supplied the authoritative committed
phase manifest; the worktree adds the audit, pipeline, infrastructure,
carryforward, and documentation transition changes.

This was a phase-focused audit. Both Phase 04 implementation summaries,
session specifications, security records, archived phase PRD/session stubs,
and the implementation notes containing review discoveries were read. Deep
updates target the public landing, strict multimode intake, durable progress,
four-publication results, verified transfer, sandboxed preview, local release
validation, and completed transition infrastructure. Standard root, docs,
ADR, runbook, API, and registered-package coverage was also verified.

## Coverage

| Area | Required | Found | Status |
|------|----------|-------|--------|
| Root documentation | 3 | 3 | README, CONTRIBUTING, and LICENSE present |
| Standard `docs/` groups | 9 | 9 | Eight current; CODEOWNERS identity requires owner decision |
| ADR artifacts | 2 baseline | 9 total | Index, template, and seven decision records present |
| Registered package READMEs | 3 | 3 | Backend shell, engine, and frontend covered |

## Files Created

No required documentation file was missing. The transition created the
evidence reports `.spec_system/audit/pipeline.md` and
`.spec_system/audit/infra.md`; this audit verified and linked their current
conclusions rather than duplicating them into operator guides.

## Files Updated

- `README.md` - Marks Phases 00-04 complete, identifies Phase 05 release work,
  describes the implemented public-to-publications journey, and makes the
  one-command stack startup explicit after one-time environment setup.
- `docs/ARCHITECTURE.md` - Replaces the planned/static Phase 04 description
  with current frontend responsibilities and the generated-client learner
  flow, including retry identity, polling, manifest, and preview boundaries.
- `docs/onboarding.md` - Removes stale phase-qualified backend language while
  retaining the verified current setup and learner route sequence.
- `docs/deployment.md` - Documents the tag/manual read-only release workflow,
  its exact artifact gates, 14-day retention, no-deploy boundary, and current
  hosted-run billing condition.
- `docs/dashboard-design.md` - Marks the four-publication experience complete,
  fixes protected navigation, removes donor dashboard motion from the active
  design contract, records dormant legacy CSS utilities truthfully, and
  updates the current primitive count and learner header example.
- `.spec_system/CONSIDERATIONS.md` - Resolves the learner-workspace concern and
  carries forward canonical retry, real-facade browser, polling, rendered
  accessibility, and sandboxed-preview lessons.
- `.spec_system/SECURITY-COMPLIANCE.md` - Adds the bounded topic handoff and
  temporary artifact URL to the data inventory, records Phase 04, and updates
  current dependency/workflow audit evidence.
- `.spec_system/CONVENTIONS.md` - Records the validated Security and Deploy
  bundles plus exact backup retention and rollback ownership.
- `docs/CHANGELOG.md` - Records release validation, documentation
  synchronization, infrastructure proof, and cache-poisoning hardening under
  Unreleased.
- `.spec_system/docs-audit.md` - Replaces the Phase 03 report with this
  evidence-backed Phase 04 audit.

## Verified Current

- `CONTRIBUTING.md` still requires tests before implementation, the strict
  shell/package boundary, generated-client ownership, current package
  commands, and focused review.
- Root and package licenses exist with explicit scope; no legal choice was
  inferred or changed.
- `backend/README_backend.md`, `backend/packages/txt2crs/README_txt2crs.md`,
  and `docs/api/README_api.md` remain current for durable submission,
  recovery, owner-hidden reads, artifact delivery, erasure, and the public
  package facade.
- `frontend/README_frontend.md` matches the generated route tree and current
  public, intake, progress, results, setup, authentication, settings, and
  administration surfaces.
- `docs/development.md`, `docs/environments.md`,
  `docs/deployment-policy.md`, and the incident runbook match the validated
  local-only topology, one-process contract, health endpoints, private state,
  complete backup/restore, and environment-specific rate limits.
- Repository-root Docker Compose remains the only deployment target under
  ADR-0008. The new release workflow validates artifacts but does not publish,
  create a release, or deploy.
- All three analyzer-registered packages have uniquely named README files.
  The root is the only tracked authored `README.md`.
- `VERSION` and the engine package remain synchronized at `0.7.0`.

## External Decision Gaps

1. `docs/CODEOWNERS` names `@aiwithapex`, but GitHub resolves neither a user
   nor organization by that name. Replacing it requires the repository owner
   to select an accountable GitHub identity.
2. The private repository has no verified project security mailbox and its
   private-vulnerability-reporting API endpoint returns 404. The owner must
   select a durable private reporting channel before public release.
3. Formal legal-basis, third-party-transfer, log/state/artifact/backup
   retention, backup erasure, and provider-copy records remain incomplete.
   These require product/legal and operator decisions before real learner data
   can be accepted under a compliant public policy.
4. GitHub Actions jobs at the Phase 04 release revision cannot schedule
   because account billing rejects every job before runner assignment. Local
   equivalents pass, but remote CodeQL remains unavailable.

No hosting decision is required: local Docker is the explicit complete
deployment scope under ADR-0008.

## Evidence Ledger

| Area | Document | Codebase or Spec Evidence | Result |
|------|----------|---------------------------|--------|
| Project state | This report | `.spec_system/scripts/analyze-project.sh --json` | Phase 04 complete; 3 packages; 2 Phase 04 sessions |
| Phase manifest | This report | First spec base plus `git diff --name-only 08297e3..HEAD` | Committed Phase 04 file manifest inspected |
| Semantic changes | Root, architecture, frontend, design guides | Both Phase 04 summaries/security reports, archived PRD/stubs, and discovery-bearing implementation notes | Complete learner journey documented |
| Public route map | Root, frontend, architecture, design guides | `frontend/src/routeTree.gen.ts`, route files, AppSidebar, and 69-test browser regression | `/`, `/create`, `/jobs/$jobId`, auth, setup, settings, and admin current |
| Intake and retry | Architecture and frontend guide | Central Zod contracts, `useCourseSubmission`, and unit/browser tests | Exact source shaping and retry identity current |
| Progress and ownership | Architecture and frontend guide | Generated query/presentation modules plus foreign/missing browser proof | Monotonic polling and owner-hidden recovery current |
| Results and preview | Architecture, frontend, design guides | CourseResults modules, 132 unit tests, and completed deterministic journey | Four publications, verified transfer, and sandbox isolation current |
| Visual contract | Design guide | AppSidebar inspection, CSS consumer search, 27 UI component files, and rendered Phase 04 matrix | Active donor motion removed from documentation |
| Release validation | Deployment guide | `.github/workflows/release.yml`, actionlint, Zizmor, distribution/image inspection, and pipeline report | Current; never deploys |
| Local infrastructure | Deployment guides | Isolated health, production `429`, destructive backup/restore, and executable image rollback recorded in `audit/infra.md` | All four bundles pass |
| Package coverage | Package READMEs | Analyzer package array and filesystem inspection | 3 of 3 present |
| README naming | Documentation rules | `git ls-files` README inspection | Root is the only tracked `README.md` |
| Command availability | Root and operator guides | Executable checks for validation, generation, image smoke, deploy smoke, rollback, backup, and restore scripts | PASS |
| Link integrity | Audited Markdown | Local target scan over 24 root, standard-doc, ADR, runbook, API, architecture, and package-guide files | 109 local links resolve |
| Version accuracy | Root and release docs | `VERSION` and engine `pyproject.toml` inspection | Both `0.7.0` |
| Encoding/format | Files changed in this gate | ASCII/LF scan, `git diff --check`, and focused pre-commit | PASS |
| CODEOWNERS | `docs/CODEOWNERS` | `gh api users/aiwithapex` and `gh api orgs/aiwithapex` | Both return 404; external decision |
| Security contact | `docs/SECURITY.md` | Repository private-vulnerability-reporting endpoint | 404; external decision |
| Privacy posture | Security and environment docs | Fresh cumulative Phase 04 security/compliance synthesis | GDPR remains non-compliant pending policy decisions |
| Remote CI | Pipeline and known-issues reports | Seven zero-step Phase 04 runs and exact local fallbacks for all ten workflows | Billing blocker remains |

## Next Action

The master PRD explicitly defines Phase 05 Hardening and Submission as Not
Started while state tracking ends at completed Phase 04. The two-source rule
therefore selects `phasebuild`; it owns reconciliation and creation of
Phase 05.
