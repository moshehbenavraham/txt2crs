# Task Checklist

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Total Tasks**: 25
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-20

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[S0501]` session ref; `TNNN` task ID.

---

## Setup (4 tasks)

- [x] T001 [S0501] Verify the clean `875808005a011a6a23538fa903805d0719463ccd`
  base, Phase 04 exit evidence, release/version surfaces, workflow contracts,
  fixed evaluation corpus, deterministic sixteen-artifact fixture, production
  helpers, and live credential readiness without printing secret values;
  record observations before changing code
  (`.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`,
  `VERSION`, `.github/workflows/`, `backend/packages/txt2crs/tests/`,
  `frontend/tests/`, `scripts/`).
- [x] T002 [S0501] Write failing release-contract tests for root/package/lock/
  docs/changelog agreement, SemVer `1.0.0`, distribution and image hashes,
  candidate revision identity, deterministic canonical JSON, and candidate
  versus final tag rules
  (`backend/tests/scripts/test_release_evidence.py`).
- [x] T003 [S0501] [P] Write failing privacy and artifact-ledger tests for
  exactly four deliverables by four formats, complete inspection judgments,
  bounded sizes/durations, safe field allowlists, and rejection of credentials,
  emails, prompts, provider payloads, tokens, absolute paths, raw bodies, and
  unrestricted links
  (`backend/tests/scripts/test_release_evidence.py`).
- [x] T004 [S0501] [P] Write failing static workflow tests requiring the tag
  workflow to call the shared validator, check exact tag/version identity,
  keep empty top-level permissions, pin every action, avoid publication and
  deployment, build both distributions/images, and upload only reviewed
  release artifacts
  (`backend/tests/scripts/test_release_workflow_contract.py`,
  `.github/workflows/release.yml`).

---

## Foundation (6 tasks)

- [x] T005 [S0501] Implement the standard-library release evidence models,
  SemVer/version-surface reader, hash validators, artifact inspection
  completeness rules, public-safe allowlist/redaction rejection, canonical
  JSON writer, candidate mode, and exact final-tag mode with generous comments
  and no engine/provider/database imports
  (`scripts/release_evidence.py`).
- [x] T006 [S0501] Integrate the release workflow with the tested validator,
  preserving its read-only permissions, pinned actions, credential-free engine
  and frontend gates, inspected wheel/sdist checksums, production images,
  fourteen-day artifacts, and no publish/deploy side effect
  (`.github/workflows/release.yml`,
  `backend/tests/scripts/test_release_workflow_contract.py`).
- [x] T007 [S0501] Define the public release-evidence directory, canonical
  candidate ledger shape, deterministic sample format, sixteen-row human
  inspection template, local-only/CodeQL disclosures, and Session 02 tag
  handoff; ignore all raw live inputs, provider state, downloads, captures,
  and temporary evidence workspaces
  (`docs/release/README_release.md`,
  `docs/release/ARTIFACT_INSPECTION_1_0_0.md`,
  `docs/release/DETERMINISTIC_SAMPLE_1_0_0.md`, `.gitignore`).
- [x] T008 [S0501] Synchronize the first stable public release candidate to
  `1.0.0` in root and engine metadata, regenerate the uv lock with the engine
  package version, update the current-stage/versioning instructions, and
  create the dated changelog heading without inventing a frontend version
  (`VERSION`, `backend/packages/txt2crs/pyproject.toml`, `backend/uv.lock`,
  `docs/VERSIONING.md`, `docs/CHANGELOG.md`).
- [x] T009 [S0501] Reconcile the master implementation plan’s already-proven
  P0 definition-of-done rows from validated Phase 00-04 evidence and document
  candidate-before-assets-before-tag ordering without reopening implemented
  behavior
  (`docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md`,
  `.spec_system/PRD/PRD.md`, `.spec_system/PRD/phase_05/`).
- [x] T010 [S0501] Run focused new release tests and negative fixtures until
  version drift, unsafe evidence, incomplete artifacts, malformed hashes, and
  tag mismatch fail closed while a minimal synthetic candidate passes
  (`backend/tests/scripts/test_release_evidence.py`,
  `backend/tests/scripts/test_release_workflow_contract.py`,
  `scripts/release_evidence.py`).

---

## Implementation (9 tasks)

- [ ] T011 [S0501] Create a detached clean candidate worktree or clone at the
  exact planned revision, install from lockfiles, and execute the engine,
  backend, frontend unit/type/build, generated-client immutability, application
  acceptance, and deterministic browser matrices without credentials or
  network; retain command/result identity only
  (`.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`).
- [ ] T012 [S0501] Run the fixed engine evaluation corpus in plan/replay mode,
  verify case/version/invariant coverage and aggregate privacy, and record only
  bounded aggregate results rather than case inputs or private references
  (`backend/packages/txt2crs/src/txt2crs/evals/`,
  `backend/packages/txt2crs/tests/unit/test_evaluation_replay.py`,
  `docs/release/RELEASE_CANDIDATE_1_0_0.json`).
- [ ] T013 [S0501] Build the `1.0.0` wheel and source distribution from the
  engine package, inspect license/README/metadata/content, calculate SHA-256
  checksums, and reject stale or extra distributions
  (`backend/packages/txt2crs/pyproject.toml`, `backend/dist/`,
  `docs/release/RELEASE_CANDIDATE_1_0_0.json`).
- [ ] T014 [S0501] Build fresh production backend/frontend images labeled with
  candidate version and revision, inspect non-root user, one FastAPI process,
  healthchecks, build configuration, package version, and image IDs/digests,
  then start one isolated root-Compose project
  (`backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`,
  `scripts/verify-production-baseline.sh`).
- [ ] T015 [S0501] Prove authentication, one completed deterministic job,
  manifest, and verified artifact persist while backend/frontend containers
  are replaced and the same PostgreSQL and private-state volumes are retained;
  confirm both services return healthy and the artifact remains owner-private
  (`scripts/deploy-smoke-check.sh`, `scripts/deploy-rollback.sh`,
  `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`).
- [ ] T016 [S0501] Provision an isolated live-proof runtime using the packaged
  system-auth flow and private Tavily environment, verify truthful GPT-5.6,
  research, storage, worker, and admission readiness without logging values,
  and document the representative full-course gate separately from the small
  deterministic MCP subscription probe
  (`backend/packages/txt2crs/tests/acceptance/README_acceptance.md`,
  `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`).
- [ ] T017 [S0501] Submit exactly one bounded synthetic education topic through
  the real application/facade boundary, observe durable monotonic checkpoints,
  confirm real Tavily research precedes drafting and exact GPT-5.6 use without
  fallback, recover from refresh if needed, and wait for terminal delivery of
  four publications and exactly sixteen artifacts
  (`backend/packages/txt2crs/tests/acceptance/test_live_codex_subscription.py`,
  `docs/release/ARTIFACT_INSPECTION_1_0_0.md`).
- [ ] T018 [S0501] Download and locally inspect every live HTML, Markdown, PDF,
  and DOCX course/review/assessment/answer-key artifact for hash/size,
  alignment, citations, formatting, private delivery, and strict student-
  assessment versus instructor-answer separation; record one explicit
  pass/finding per pair without copying raw bodies into tracked evidence
  (`docs/release/ARTIFACT_INSPECTION_1_0_0.md`).
- [ ] T019 [S0501] Audit live logs, HTTP/browser traffic, public projections,
  process tree, loopback listeners, temporary files, generated evidence,
  backups, and staged Git diff for secrets, prompts, provider payloads,
  private identifiers, paths, raw bodies, orphan resources, and overclaimed
  compliance; derive the public-safe deterministic sample and canonical
  candidate ledger, then remove raw workspaces
  (`docs/release/DETERMINISTIC_SAMPLE_1_0_0.md`,
  `docs/release/RELEASE_CANDIDATE_1_0_0.json`,
  `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`).

---

## Testing (6 tasks)

- [ ] T020 [S0501] Run focused release/evidence tests, package metadata tests,
  release workflow/security workflow contracts, Ruff, mypy, typos, and
  canonical evidence regeneration; confirm a second generation is byte-for-
  byte identical
  (`backend/tests/scripts/`, `backend/packages/txt2crs/tests/unit/test_package_metadata.py`,
  `scripts/release_evidence.py`).
- [ ] T021 [S0501] Run the complete engine and backend suites plus strict
  typing/linting from their owning package roots; keep the explicit live marker
  separate and record exact pass/skip counts
  (`backend/packages/txt2crs/`, `backend/`).
- [ ] T022 [S0501] Run frontend unit tests, Biome, TypeScript, route generation,
  production build, deterministic completed/failed job Playwright projects,
  broad browser regression, mobile/desktop/accessibility/reduced-motion
  checks, and generated OpenAPI/client immutability
  (`frontend/`).
- [ ] T023 [S0501] Run every locally executable GitHub workflow equivalent,
  pre-commit over tracked and explicit new files, Gitleaks, Zizmor, Python/npm
  dependency audits, documentation links, ASCII/LF, executable-bit, secret,
  path, generated-file, and diff-hygiene checks; preserve remote CodeQL as the
  only known low external finding if billing still rejects zero-step runs
  (`.github/workflows/`, `.pre-commit-config.yaml`,
  `.spec_system/SECURITY-COMPLIANCE.md`).
- [ ] T024 [S0501] Repeat version validation, distribution build/inspection,
  candidate JSON generation, image build/inspection, Compose health, and
  replacement smoke from the exact clean candidate revision; verify the
  recorded Git SHA and all hashes match and that no final tag exists yet
  (`VERSION`, `backend/dist/`, `docs/release/RELEASE_CANDIDATE_1_0_0.json`,
  `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`).
- [ ] T025 [S0501] Reconcile all commands, counts, inspection judgments,
  candidate revision/hashes, local workflow evidence, known external
  exceptions, cleanup proof, and the exact Session 02 final-tag revalidation
  list; run final staged hooks and mark every task complete
  (`.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md`,
  `.spec_system/specs/phase05-session01-release-hardening-and-live-proof/tasks.md`,
  `docs/release/README_release.md`).

---

## Completion Checklist

- [ ] All tasks marked `[x]`
- [ ] All tests and checks passing
- [ ] Exact `1.0.0` candidate revision and hashes recorded
- [ ] Live GPT-5.6 plus Tavily course and sixteen-artifact review complete
- [ ] Public evidence is redacted and raw/private workspaces are removed
- [ ] No final `v1.0.0` tag exists before Session 02
- [ ] Active-session files are ASCII-encoded with LF line endings
- [ ] `implementation-notes.md` updated
- [ ] Ready for `creview` (next step in the
      implement -> creview -> validate sequence)

---

## Next Steps

Run the `implement` workflow, followed by `creview`, `validate`, and
`updateprd`.
