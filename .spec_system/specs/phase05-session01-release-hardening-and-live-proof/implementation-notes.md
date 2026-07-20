# Implementation Notes

**Session ID**: `phase05-session01-release-hardening-and-live-proof`
**Package**: null (cross-cutting)
**Started**: 2026-07-20 09:13 IDT
**Last Updated**: 2026-07-20 09:14 IDT

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 10 / 25 |
| Estimated Remaining | 2-3 hours plus external live credential |
| Blockers | 1 external credential pending; deterministic work continues |

---

## Task Log

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

### Blocker 1: Tavily Credential Is Not Configured

**Description**: The real representative course requires a private nonempty
`TAVILY_API_KEY`; none is present in the process or project environment files.
**Impact**: Tasks T016-T019 cannot truthfully complete the real Tavily proof
until a credential exists. All credential-free implementation and validation
tasks remain executable.
**Resolution**: Pending external credential availability. Continue every
deterministic and release-candidate task first; never substitute another
provider or fabricate a live result.
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
- Next task: T011 - execute the clean deterministic matrix.
