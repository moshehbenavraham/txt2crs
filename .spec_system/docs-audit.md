# Documentation Audit

**Date:** 2026-07-21
**Project:** txt2crs
**Audit mode:** Full repository documentation and archival-readiness review
**Result:** PASS with four explicit external owner/platform gaps

## Outcome

Every file in `docs/ongoing-projects/` has been reviewed against the current
implementation and primary documentation. Genuine enduring requirements,
architecture constraints, public contracts, operational guidance, security
controls, engine quality gates, and institutional lessons have been moved into
their canonical documents. Historical timelines, superseded proposals,
duplicated submission requirements, empty task placeholders, and an inaccurate
legacy promotional image were intentionally not promoted.

No source file was deleted, and every source record remains available for
manual review. Primary documentation has no live link to the folder, so the
owner can delete it after review without breaking the current documentation
graph. Archived changelogs may retain plain historical path mentions as
immutable release history; they are not current references.

The deterministic project analyzer reports all six phases and all eighteen
sessions complete. The master PRD and state file define no later phase.

## Ongoing-Project Archival Matrix

| Source record | Enduring value retained | Canonical destination | Disposition |
|---------------|-------------------------|-----------------------|-------------|
| `COURSE_LIBRARY_NAVIGATION_INVESTIGATION.md` | Owner-scoped stable pagination, bounded summaries, library polling, and route reuse | `docs/api/README_api.md`, `frontend/README_frontend.md`, `docs/dashboard-design.md`, `.spec_system/PRD/PRD.md` | Contract promoted; investigation timeline remains historical |
| `E2E_PLATFORM_CHECK_20260721.md` | Sanitized `srcdoc` preview, permanent-error polling stop, root E2E environment, run-owned browser auth DB, shell test DB guard, capacity, and loading/fold corrections | Frontend/backend READMEs, onboarding, development, architecture, security/compliance, considerations, and PRD | All resolved behavior promoted; defect narrative remains historical |
| `INPUT_TO_COURSE_SYSTEM_PLAN.md` | Package ownership, resource lifetimes, recovery semantics, current requirements, and explicit evolution triggers | `docs/ARCHITECTURE.md`, `.spec_system/PRD/PRD.md`, package READMEs, runbook | Durable rules promoted; stale phase statuses and superseded limits were rejected |
| `JOB_job-16a288f24f554c188e11c2aceb8d7df7_MONITORING_NOTES.md` | Checkpoint-versus-heartbeat diagnosis and safe stalled-job response | `docs/runbooks/incident-response.md`, API/frontend docs, `.spec_system/CONSIDERATIONS.md` | Operational lesson promoted; one-run timings are not an SLA |
| `JOB_job-dc80a8c30f994603a3e525f0eb2f80c6_MONITORING_NOTES.md` | Host-computed claim hashes, independent citation support, module pedagogy gates, research source floors/diversity, deduplication, community classification, and Codex instruction-layer lesson | Engine README and `.spec_system/CONSIDERATIONS.md` | Remediated quality boundaries promoted; failed-run transcript remains historical |
| `OPENAI_BUILD_WEEK_REQUIREMENTS.md` | No unique enduring content; the dated submission constraints remain release history | Existing `.spec_system/PRD/PRD.md` and `docs/archive/build-week/` package | Existing canonical coverage retained; no duplicate promoted |
| `TODO.md` | None; only empty section placeholders | `.spec_system` task state and `docs/CHANGELOG.md` already own planning/completion | Nothing promoted |
| `maxs-notes.md` | Beginner-readable code, subscription runtime, and boilerplate provenance | Existing `AGENTS.md`, root README, architecture, notices, and package docs | No unique current content |
| `txt2crs-01.png` | None suitable for the current product | Current reviewed submission media remains under `docs/archive/build-week/` | Not promoted: it advertises unsupported application image input and obsolete product visuals |

## Durable Content Promoted

- The API guide now documents both owner collection endpoints, cursor and
  ordering rules, bounded library summaries, truthful admission capacity,
  content-free runtime activity, and fetched/charged/accepted source metrics.
- Architecture now distinguishes application- and job-lifetime resources,
  includes the retained-course browser flow, describes sanitized `srcdoc`, and
  records explicit triggers for replacing SQLite, serial work, polling, the
  exact model, local artifacts, or local deployment.
- The engine guide now records pre-freeze source-quality controls and
  pre-checkpoint module acceptance gates, including host-computed claim hashes,
  one bounded repair, and Codex `developer_instructions` usage.
- Product and frontend documents now treat the course library and admission
  capacity as implemented requirements, distinguish heartbeat from checkpoint
  progress, and stop polling after permanent read failures.
- Backend/development guidance now warns that the destructive application
  suite refuses normal database names and requires a separately provisioned
  `test_*` or `*_test` database; deterministic browser auth uses run-owned
  SQLite.
- Incident response now uses both checkpoint revision and content-free runtime
  activity to distinguish long provider work from a genuinely stalled worker.
- Security/compliance and institutional memory now preserve the database
  isolation, inert preview, engine acceptance, recovery, and Codex protocol
  lessons discovered during final platform validation.

## Primary Files Updated

- `README.md`, `AGENTS.md`, and `llms.txt`
- `docs/README_docs.md`, `docs/FILE_ORGANIZATION.md`,
  `docs/ARCHITECTURE.md`, `docs/api/README_api.md`, `docs/development.md`,
  `docs/onboarding.md`, `docs/dashboard-design.md`,
  `docs/runbooks/incident-response.md`, and `docs/CHANGELOG.md`
- `backend/README_backend.md`,
  `backend/packages/txt2crs/README_txt2crs.md`, and
  `frontend/README_frontend.md`
- `.spec_system/PRD/PRD.md`, `.spec_system/CONSIDERATIONS.md`, and
  `.spec_system/SECURITY-COMPLIANCE.md`
- `docs/adr/0008-local-only-deployment-scope.md` and
  `make-scenarios/FEATURE_AND_SUBMISSION_PLAN.md`

## Evidence And Verification

The audit read every Markdown file in the candidate folder and inspected its
PNG. Candidate claims were checked against:

- FastAPI job routes and Pydantic response schemas for collection bounds,
  capacity, status heartbeat, and research counters;
- package public job queries, SQLite migrations, worker heartbeat, research
  coordinator, evidence quality, generation pipeline, and Codex runtime;
- frontend library, capacity, progress, preview, route, and Playwright
  composition sources plus their focused tests;
- backend database-safety preflight, root fixture, deterministic browser app,
  CI workflow environments, and test entrypoint; and
- current product, architecture, API, operations, security, release, and
  submission documentation.

The final validation checks the modified Markdown graph for missing local
links, scans current primary documents for dependencies on the candidate
folder, verifies ASCII-only Apex records, and runs repository whitespace and
diff checks. No command in this audit mutates provider, deployment, GitHub,
YouTube, Devpost, or owner data.

## Current Documentation Coverage

| Area | Status | Primary source |
|------|--------|----------------|
| Product requirements and completed phases | PASS | `.spec_system/PRD/PRD.md` |
| Package boundaries and evolution rules | PASS | `docs/ARCHITECTURE.md` and package READMEs |
| Public HTTP contracts | PASS | `docs/api/README_api.md` and generated OpenAPI |
| Learner interaction and accessibility | PASS | `frontend/README_frontend.md` and `docs/dashboard-design.md` |
| Local setup, testing, and operations | PASS | onboarding, development, backend README, and incident runbook |
| Security, privacy, and unresolved compliance | PASS | `.spec_system/SECURITY-COMPLIANCE.md` and `docs/SECURITY.md` |
| Release and submission evidence | PASS | `docs/release/` and `docs/archive/build-week/` indexes |
| Repository history | PASS | `docs/CHANGELOG.md`, archived changelogs, ADRs, and git history |

## Explicit External Gaps

These findings require owner, organizer, or platform action and are not
silently filled with invented values:

1. `docs/CODEOWNERS` names `@aiwithapex`, but that GitHub identity has not been
   verified as a resolvable repository owner.
2. No verified security mailbox or GitHub private-vulnerability-reporting
   channel has been supplied.
3. Formal legal-basis, provider-transfer, retention, log-erasure,
   backup-erasure, and provider-copy policies are incomplete. The release
   remains a synthetic local demonstration and makes no GDPR claim.
4. GitHub Actions billing rejects remote jobs before runner assignment, so
   remote CodeQL remains an open low-severity platform finding even though all
   locally executable equivalents pass.

## Completion Decision

Documentation archival readiness is **PASS**. All enduring, implementation-
verified value from the candidate folder is represented in primary documents,
and no primary document relies on that folder. The owner can now perform the
requested manual review and deletion without losing a current contract or
operational rule.

**Next Apex command:** none. Neither the master PRD nor deterministic state
defines a remaining implementation phase.
