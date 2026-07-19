# Implementation Notes

**Session ID**: `phase01-session03-input-preferences-and-policy-gate`
**Package**: backend/packages/txt2crs
**Started**: 2026-07-19 14:30 IDT
**Last Updated**: 2026-07-19 15:25 IDT

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 24 / 24 |
| Estimated Remaining | Code review and validation |
| Blockers | 0 |

---

## Task Log

### 2026-07-19 - Session Start

**Environment verified**:

- [x] Apex Spec analyzer identifies the active Session 03 directory.
- [x] Package prerequisites pass for `backend/packages/txt2crs`.
- [x] uv, jq, git, Python package manifest, and directory structure are ready.
- [x] Engine SQLite uses package-owned migrations; no PostgreSQL/Alembic change
  is in this session.

---

### Task T001 - Verify The Existing Engine Baseline

**Started**: 2026-07-19 14:30 IDT
**Completed**: 2026-07-19 14:31 IDT
**Duration**: 1 minute

**Notes**:

- Confirmed the active package and session using the repository-local Apex Spec
  scripts.
- Proved the existing request, ingestion, policy, pipeline, executor, and
  projection contracts are green before production edits.

**Files Changed**:

- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/implementation-notes.md`
  - Recorded environment and baseline evidence.

**Verification**:

- Command/check: `.spec_system/scripts/analyze-project.sh --json`
  - Result: PASS - Session 03 and its `spec.md`/`tasks.md` were recognized.
- Command/check: `.spec_system/scripts/check-prereqs.sh --json --env --package backend/packages/txt2crs`
  - Result: PASS - All required environment and package checks passed.
- Command/check: `uv run --package txt2crs pytest tests/unit/test_generation_requests.py tests/unit/test_ingestion_service.py tests/unit/test_url_ingestion.py tests/unit/test_media_ingestion.py tests/unit/test_content_policy.py tests/integration/test_generation_pipeline.py tests/integration/test_generation_job_executor.py tests/unit/test_public_job_queries.py -q`
  - Result: PASS - 83 tests passed in 2.27 seconds.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**: None; this task established the unchanged behavioral baseline.

---

### Task T002 - Add Failing URL Routing Tests

**Started**: 2026-07-19 14:31 IDT
**Completed**: 2026-07-19 14:34 IDT
**Duration**: 3 minutes

**Notes**:

- Defined observable tests for exact YouTube host routing, general URL routing,
  one canonicalization, canonical child payloads, and fail-closed input.
- Recording adapters assert that only the selected ingestion path runs.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py` - Added
  the routing contract tests and recording fakes.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_routing_url_ingestion.py -q`
  - Result: EXPECTED FAIL - Collection reports only the intentionally missing
    `txt2crs.ingestion.routing_url` production module.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Trust boundary enforcement: tests require type validation and canonical URL
  validation before child-adapter calls.

---

### Task T003 - Add Failing Preference And Shape Tests

**Started**: 2026-07-19 14:34 IDT
**Completed**: 2026-07-19 14:39 IDT
**Duration**: 5 minutes

**Notes**:

- Added request tests proving defaults and shape ranges are frozen and hashed.
- Added deterministic auto/explicit resolution, alignment, and pre-drafting
  curriculum rejection scenarios.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_generation_requests.py` - Added
  execution-profile default/shape identity tests.
- `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py`
  - Added resolution and local course-plan gate tests.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_generation_requests.py tests/unit/test_learning_preference_resolution.py -q`
  - Result: EXPECTED FAIL - Collection identifies only the planned missing
    `CurriculumShapeLimits` and `generation.preferences` contracts.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Contract alignment: tests bind every documented P0 default and range to the
  immutable request profile.
- Failure path completeness: tests require stable local resolution error codes.

---

### Task T004 - Add Failing Two-Stage Policy And Preparation Tests

**Started**: 2026-07-19 14:39 IDT
**Completed**: 2026-07-19 14:45 IDT
**Duration**: 6 minutes

**Notes**:

- Replaced raw-age policy tests with privacy-minimized age-group and explicit
  preflight/post-ingestion contracts.
- Added preparation tests for zero ingestion on cheap denial, exactly one
  ingestion before post-policy denial, immutable accepted state, and request
  hash binding.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_content_policy.py` - Added
  versioned two-stage policy scenarios.
- `backend/packages/txt2crs/tests/unit/test_generation_preparation.py` - Added
  provider-free preparation contract tests.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_content_policy.py tests/unit/test_generation_preparation.py -q`
  - Result: EXPECTED FAIL - Collection identifies only the planned missing
    policy compatibility/stage and `jobs.preparation` contracts.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Failure path completeness: tests require safe terminal reason codes without
  normalized content in error strings.
- State freshness on re-entry: preparation is bound to the exact request hash.

---

### Task T005 - Add Failing Prepared Pipeline And Plan-Gate Tests

**Started**: 2026-07-19 14:45 IDT
**Completed**: 2026-07-19 14:51 IDT
**Duration**: 6 minutes

**Notes**:

- Added prepared-input and sequence-2 pipeline entry expectations.
- Added one-repair, two-failure, request-hash binding, resolved-preference
  ordering, and module content-block range scenarios.

**Files Changed**:

- `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py` -
  Added preparation fixtures and local acceptance/recovery tests.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/integration/test_generation_pipeline.py -q`
  - Result: EXPECTED FAIL - Collection stops at the planned missing
    `txt2crs.jobs.preparation` boundary.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Duplicate action prevention: tests require no `ingest_input` replay inside
  the provider-backed pipeline.
- Contract alignment: course-plan schema success alone cannot bypass the stored
  learning contract or shape limits.

---

### Task T006 - Add Failing Executor Ordering And Recovery Tests

**Started**: 2026-07-19 14:51 IDT
**Completed**: 2026-07-19 15:01 IDT
**Duration**: 10 minutes

**Notes**:

- Reframed executor tests around its durable stored request and lazy pipeline
  factory rather than caller-supplied payload/policy values.
- Added real SQLite restart coverage at preparation, resolved-plan, and
  delivery boundaries plus zero-construction denial assertions.

**Files Changed**:

- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
  - Replaced eager-pipeline tests with preparation-first lifecycle coverage.
- `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py` -
  Exposed one canonical compact request fixture for executor integration.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/integration/test_generation_job_executor.py -q`
  - Result: EXPECTED FAIL - Collection stops at the planned missing preparation
    module before any existing production behavior can satisfy the new tests.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- State freshness on re-entry: real SQLite replacements must use preparation
  and resolved preferences from the latest accepted checkpoint.
- Resource ordering: denial and local delivery recovery must not construct a
  provider-backed pipeline.

---

### Task T007 - Add Failing Preparation Projection And Record Red Milestone

**Started**: 2026-07-19 15:01 IDT
**Completed**: 2026-07-19 15:04 IDT
**Duration**: 3 minutes

**Notes**:

- Added a preparation-only public snapshot that exposes sequence-1 progress and
  safe input metadata.
- The privacy assertions cover normalized content, goals, request hash, policy
  fields, and planning defaults.
- Re-ran all eight focused files and confirmed failures are confined to the
  planned missing production contracts.

**Files Changed**:

- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` - Added
  preparation-only progress and privacy coverage.
- `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/implementation-notes.md`
  - Recorded the complete tests-first milestone.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_routing_url_ingestion.py tests/unit/test_generation_requests.py tests/unit/test_learning_preference_resolution.py tests/unit/test_content_policy.py tests/unit/test_generation_preparation.py tests/integration/test_generation_pipeline.py tests/integration/test_generation_job_executor.py tests/unit/test_public_job_queries.py -q`
  - Result: EXPECTED FAIL - Eight collection errors identify only the planned
    routing, defaults/shape, preferences, two-stage policy, and preparation
    boundaries; no production code has been added.
- Checkpoint review: Re-read Session 03 objectives/success criteria.
  - Result: PASS - Tests cover all five objectives and do not add shell,
    frontend, managed-runtime, or provider-discovery scope.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Error information boundaries: public JSON assertions exclude all new private
  preparation and policy fields.

---

### Task T008 - Freeze Defaults And Curriculum Limits In Requests

**Started**: 2026-07-19 15:04 IDT
**Completed**: 2026-07-19 15:07 IDT
**Duration**: 3 minutes

**Notes**:

- Added frozen, strict P0 learning defaults and ordered curriculum shape
  ranges to every execution profile.
- Because Pydantic serializes defaulted fields, new canonical request hashes
  include these values even when a server uses the documented defaults.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` - Added
  `LearningPreferenceDefaults`, `CurriculumShapeLimits`, validation, and
  execution-profile fields.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_generation_requests.py -q`
  - Result: PASS - 39 request/profile tests passed.
- BQC contract scan: strict/frozen models, finite bounds, ordered ranges, and
  canonical model dumps inspected.
  - Result: PASS - No mutable or unbounded generation-affecting profile value
    was introduced.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**: None after implementation; contract alignment checks passed.

---

### Task T009 - Add Prepared And Concrete Preference Contracts

**Started**: 2026-07-19 15:07 IDT
**Completed**: 2026-07-19 15:11 IDT
**Duration**: 4 minutes

**Notes**:

- Made the concrete learning contract immutable and added explicit level and
  learning goals.
- Added a distinct pre-plan contract that freezes auto language and all stored
  defaults without pretending auto level/audience/goals are resolved.
- Added context-free resolution errors and normalized uniqueness helpers.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/generation/models.py` - Extended and
  froze `LearningPreferences`.
- `backend/packages/txt2crs/src/txt2crs/generation/preferences.py` - Added
  prepared preference and safe resolution contracts.

**Verification**:

- Command/check: `uv run --package txt2crs python -` contract construction and
  mutation probe.
  - Result: PASS - Prepared values match the request hash/language and concrete
    preferences reject mutation.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/generation/models.py src/txt2crs/generation/preferences.py`
  - Result: PASS - Ruff reported no findings.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Contract alignment: unresolved intent and concrete accepted preferences are
  separate types, preventing an `auto` value from crossing the resolved
  boundary.

---

### Task T010 - Implement Versioned Two-Stage Content Policy

**Started**: 2026-07-19 15:11 IDT
**Completed**: 2026-07-19 15:15 IDT
**Duration**: 4 minutes

**Notes**:

- Split request preflight from normalized post-ingestion evaluation.
- Replaced raw learner age in the new boundary with `LearnerAgeGroup` and added
  explicit policy stage/version fields.
- Added safe compatibility failure when stored and executing policy versions
  differ.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/security/policy.py` - Added the
  versioned two-stage policy API and strict immutable decisions.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_content_policy.py -q`
  - Result: PASS - 10 policy tests passed.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/security/policy.py tests/unit/test_content_policy.py`
  - Result: PASS - Ruff reported no findings.
- BQC error-boundary scan: mismatch and decision strings inspected.
  - Result: PASS - No request content, URL, file name, or private policy input
    enters compatibility errors.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**: None after implementation; trust and failure boundaries passed.

---

### Task T011 - Implement Provider-Free Generation Preparation

**Started**: 2026-07-19 15:15 IDT
**Completed**: 2026-07-19 15:19 IDT
**Duration**: 4 minutes

**Notes**:

- Added the cumulative sequence-1 preparation model and service.
- Preparation checks preflight before ingestion, distrusts adapter output,
  enforces the stored normalized limit, then requires post-ingestion allow.
- P0 review and reject outcomes use safe terminal errors; accepted preparation
  requires a post-ingestion, non-high-risk decision.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/preparation.py` - Added
  preparation contracts, protocol, service, validation, and safe errors.
- `backend/packages/txt2crs/src/txt2crs/security/policy.py` - Aligned the
  consent message with the reviewed public failure copy.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_content_policy.py tests/unit/test_generation_preparation.py -q`
  - Result: PASS - 15 two-stage policy/preparation tests passed.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/preparation.py src/txt2crs/security/policy.py tests/unit/test_generation_preparation.py`
  - Result: PASS - Ruff reported no findings.
- BQC trust/failure scan: adapter result, bounds, policy state, and error strings
  inspected.
  - Result: PASS - Mismatched adapter types and oversized normalized content
    fail before persistence; terminal errors expose only reviewed messages.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Trust boundary enforcement: adapter output is checked against the exact
  request input type and stored character limit before checkpointing.

---

### Task T012 - Update Canonical Test Factories

**Started**: 2026-07-19 15:19 IDT
**Completed**: 2026-07-19 15:23 IDT
**Duration**: 4 minutes

**Notes**:

- Made stored defaults and shape limits explicit in the shared profile fixture.
- Added canonical input-document, allowed-preparation, and concrete resolved
  preference factories for later checkpoint/projection tests.
- Removed unsafe test casts now that preparation exposes an ingestion protocol.

**Files Changed**:

- `backend/packages/txt2crs/tests/factories.py` - Added preparation and
  preference fixtures and explicit execution-profile values.
- `backend/packages/txt2crs/tests/unit/test_generation_preparation.py` -
  Adopted the structural ingestion protocol.
- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
  - Removed the temporary preparation-service cast.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_generation_requests.py tests/unit/test_generation_preparation.py -q`
  - Result: PASS - 44 request/preparation tests passed.
- Command/check: `uv run --package txt2crs ruff check tests/factories.py tests/unit/test_generation_preparation.py`
  - Result: PASS after Ruff organized the new imports.
- Checkpoint review: Tasks T008-T012 compared with Session 03 objectives.
  - Result: PASS - Immutable defaults, intent split, two-stage policy, and
    provider-free preparation are implemented; next work stays inside
    ingestion/pipeline/executor package scope.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Contract alignment: tests now create preparation and resolved preference
  state through shared strict contracts rather than ad hoc dictionaries.

---

### Task T013 - Implement Canonical URL Routing

**Started**: 2026-07-19 15:23 IDT
**Completed**: 2026-07-19 15:27 IDT
**Duration**: 4 minutes

**Notes**:

- Added one package adapter that canonicalizes the accepted URL, parses the
  canonical host, and delegates to exactly one reviewed child.
- Child payloads are deep copies with only the canonical URL replaced; request
  media type and metadata remain exact.
- Corrected the new test expectation to account for strict `InputPayload`
  whitespace normalization before adapter entry.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/ingestion/routing_url.py` - Added exact
  YouTube-host and general-URL routing.
- `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py` - Exported the
  supported routing adapter.
- `backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py` - Aligned
  the raw-value assertion with accepted payload normalization.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_routing_url_ingestion.py tests/unit/test_url_ingestion.py tests/unit/test_media_ingestion.py -q`
  - Result: PASS - 20 routing/URL/transcript tests passed.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/ingestion/routing_url.py src/txt2crs/ingestion/__init__.py tests/unit/test_routing_url_ingestion.py`
  - Result: PASS - Ruff reported no findings.
- BQC trust-boundary scan: non-string, normalizer rejection, hostname absence,
  exact allowlist, and non-selected adapter behavior inspected.
  - Result: PASS - No child adapter runs before canonical host selection.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Trust boundary enforcement: canonical hostname is required even when an
  injected normalizer returns malformed output.

---

### Task T014 - Resolve And Enforce Learning Preferences

**Started**: 2026-07-19 15:27 IDT
**Completed**: 2026-07-19 15:32 IDT
**Duration**: 5 minutes

**Notes**:

- Implemented deterministic audience, prior-knowledge, goal, level, language,
  duration, accessibility, and P0-default resolution.
- Implemented local objective/module/section bounds before module drafting.
- Repaired two test mutators so their `CoursePlan` references remain valid and
  the intended local shape gate, rather than base schema validation, is tested.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/generation/preferences.py` - Added the
  full local resolution and pre-drafting acceptance gate.
- `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py`
  - Kept shape-drift fixtures structurally valid.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_learning_preference_resolution.py -q`
  - Result: PASS - 11 preference and course-plan gate tests passed.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/generation/preferences.py tests/unit/test_learning_preference_resolution.py`
  - Result: PASS after Ruff organized imports and simplified formatting.
- BQC contract/failure scan: explicit/auto branches and safe errors inspected.
  - Result: PASS - No semantic guessing or plan content enters error messages;
    all client-visible intent is enforced or resolved.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Failure path completeness: every local mismatch now has a stable code behind
  one context-free public-safe message.

---

### Task T015 - Add Stored Module Content-Block Shape Gate

**Started**: 2026-07-19 15:32 IDT
**Completed**: 2026-07-19 15:36 IDT
**Duration**: 4 minutes

**Notes**:

- Added deterministic per-section content-block range validation for accepted
  module drafts.
- Added the pipeline acceptance hook that Session T016 will feed from the
  preparation's stored execution profile.
- Resolved a package initialization cycle by deferring the pipeline's
  preference validator import to the acceptance call.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/generation/preferences.py` - Added
  module content-block shape validation.
- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py` - Added the
  optional stored-limit acceptance hook and type-only import.

**Verification**:

- Command/check: `uv run --package txt2crs python -` with a one-block module
  and a stored two-block minimum.
  - Result: PASS - The gate returned
    `content_block_count_out_of_bounds`.
- Command/check: `uv run --package txt2crs pytest tests/unit/test_learning_preference_resolution.py -q`
  - Result: PASS - 11 local preference/plan tests passed.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/generation/preferences.py src/txt2crs/generation/pipeline.py`
  - Result: PASS after removing a redundant quoted annotation exposed by
    postponed annotations.
- BQC contract scan: range source and import lifecycle inspected.
  - Result: PASS - Bounds come from the persisted profile type and no package
    import cycle remains.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Contract alignment: the content-block gate accepts `CurriculumShapeLimits`,
  never process globals.
- State freshness: a lazy runtime import avoids partially initialized package
  state.

---

## Design Decisions

### Decision 1: Preparation Is The First Durable Stage

**Context**: The current pipeline ingests inside an object that already owns
provider dependencies, while recovery needs accepted normalized content and
policy state before those dependencies start.

**Options Considered**:

1. Keep `ingest_input` inside the pipeline and add policy afterward - cannot
   prevent provider-graph startup or reliably reuse policy state.
2. Persist `prepare_input` as sequence 1 and pass it into a lazy pipeline -
   preserves later sequence numbers and makes ordering testable.

**Chosen**: Sequence-1 `prepare_input` plus a lazy pipeline factory.

**Rationale**: It is the smallest change that makes no-provider-before-policy a
package invariant and gives recovery one cumulative checkpoint.

---

### Task T016 - Refactor Pipeline Around Durable Preparation

**Started**: 2026-07-19 14:36 IDT
**Completed**: 2026-07-19 14:58 IDT
**Duration**: 22 minutes

**Notes**:

- Replaced pipeline-owned ingestion with an immutable accepted preparation
  input that is bound to the canonical generation-request hash.
- Made every cumulative pipeline checkpoint carry the exact preparation and
  made `design_course` the first checkpoint that must contain resolved
  preferences.
- Added a single local course-plan repair opportunity before module drafting;
  a second shape or alignment failure terminates generation deterministically.
- Kept the public `input_document` checkpoint accessor for compatible internal
  consumers while storing only the new cumulative preparation contract.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py` - Refactored
  input ownership, durable checkpoint validation, plan acceptance/repair,
  resolved-preference propagation, and stored module bounds.
- `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py` -
  Exercised prepared input, request binding, resolution timing, repair limits,
  resume behavior, and content-block bounds.
- `backend/packages/txt2crs/tests/factories.py` - Updated cumulative checkpoint
  fixtures to build the accepted preparation contract.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/integration/test_generation_pipeline.py -x -q`
  - Result: PASS - 14 pipeline integration tests passed.
- Contract scan: searched the pipeline and tests for the removed
  `ingestion_service`, raw `preferences`, and derived request-hash paths.
  - Result: PASS - generation starts from the caller-supplied preparation and
    uses its canonical request identity.
- BQC recovery scan: inspected early, design, module, assessment, and final
  checkpoint invariants.
  - Result: PASS - preparation is cumulative and resolved preferences become
    mandatory exactly when the plan has been accepted.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Durable-state correctness: resume rejects a different preparation even when
  the caller presents another structurally valid object.
- Failure-path completeness: local course-plan rejection is repaired once and
  then fails with a stable generation error before any module draft call.

---

## Next Task

### Task T017 - Persist Preparation Before Lazy Pipeline Construction

**Started**: 2026-07-19 14:59 IDT
**Completed**: 2026-07-19 15:10 IDT
**Duration**: 11 minutes

**Notes**:

- Removed caller-supplied payload, preference, consent, age, and review values
  from execution; the worker now loads the exact accepted request from durable
  resume state.
- Added a lazy pipeline factory boundary that is reached only after an allowed
  preparation has been committed as sequence 1.
- Added restart parsing for both preparation-only and cumulative pipeline
  checkpoints, with request-hash validation at every recovery boundary.
- Preserved rendering/delivery recovery without constructing a provider graph
  or repeating ingestion.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` - Added the
  preparation-first state machine, safe policy settlement, exact request
  loading, lazy pipeline protocol, and restart reuse.
- `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`
  - Reworked real-SQLite scenarios around preparation ordering and replacement
  workers.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/integration/test_generation_job_executor.py -x -q`
  - Result: PASS - 6 preparation-first executor scenarios passed.
- Command/check: `uv run --package txt2crs mypy src/txt2crs/jobs/executor.py`
  - Result: PASS - strict type checking reported no issues.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/executor.py`
  - Result: PASS - executor lint passed.
- BQC ordering/recovery scan: policy denial, worker replacement after
  preparation, replacement after resolved preferences, and delivery restart.
  - Result: PASS - no pipeline exists before sequence 1 and no accepted source
    or preference decision is reinterpreted.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Trust-boundary closure: all execution-affecting values come from the stored
  generation request and its cumulative checkpoints.
- Recovery correctness: preparation, resolved preferences, and final bundles
  are reused at their respective restart points.

---

## Next Task

### Task T018 - Project Preparation Progress Without Private State

**Started**: 2026-07-19 15:11 IDT
**Completed**: 2026-07-19 15:22 IDT
**Duration**: 11 minutes

**Notes**:

- Added stage-discriminated parsing for sequence-1 preparation and later
  cumulative pipeline checkpoints.
- Copied only the accepted input type, safe display label, sanitized warnings,
  accepted stage, and bounded progress from preparation state.
- Kept normalized source text, policy decisions, preference values, request
  hashes, and all provider accounting behind a small internal projection.
- Updated the SQLite/filesystem restart query scenario to persist the new
  preparation checkpoint instead of the removed ingestion checkpoint.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` - Added the
  checkpoint union projection and preparation-only progress.
- `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` - Covered
  preparation-only privacy and useful safe output.
- `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py`
  - Migrated restart-safe query coverage to `prepare_input`.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_public_job_queries.py tests/integration/test_public_job_query_service.py -q`
  - Result: PASS - all 14 public projection/query integration tests passed.
- Command/check: `uv run --package txt2crs mypy src/txt2crs/jobs/public_queries.py`
  - Result: PASS - strict type checking reported no issues.
- Command/check: `uv run --package txt2crs ruff check src/txt2crs/jobs/public_queries.py tests/integration/test_public_job_query_service.py`
  - Result: PASS after import organization.
- Privacy scan: serialized the preparation-only snapshot with sentinels in
  normalized text, learning goals, hashes, policy metadata, and defaults.
  - Result: PASS - no private sentinel or private contract value appeared.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Information disclosure: the public builder receives a narrow reviewed
  projection rather than a full preparation artifact.
- Compatibility: both supported private checkpoint variants now produce the
  same stable public snapshot contract.

---

## Next Task

### Task T019 - Publish Supported Composition Contracts

**Started**: 2026-07-19 15:23 IDT
**Completed**: 2026-07-19 15:38 IDT
**Duration**: 15 minutes

**Notes**:

- Exported immutable preference defaults, curriculum limits, preparation
  contracts/service/protocol/error, resolved learning preferences, and the
  routing URL adapter from their supported package boundaries.
- Kept course-plan resolution, module acceptance, policy matching, and private
  checkpoint projection helpers out of package-level exports.
- Replaced eager cross-package initialization with narrow lazy exports so
  `jobs.preparation` and `generation.pipeline` work from a clean interpreter in
  either import order.
- Added a clean-process regression test because the normal pytest import order
  had previously hidden the partially initialized module failure.

**Files Changed**:

- `backend/packages/txt2crs/src/txt2crs/generation/__init__.py` - Published
  preference contracts and lazily exposed the preparation-dependent pipeline.
- `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` - Published request
  defaults/limits and lazily exposed preparation/public-query contracts.
- `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py` - Retained the
  supported routing URL adapter export.
- `backend/packages/txt2crs/tests/unit/test_public_package_exports.py` - Added
  clean-process import and internal-helper allowlist coverage.

**Verification**:

- Command/check: `uv run --package txt2crs pytest tests/unit/test_public_package_exports.py -q`
  - Result: PASS - both clean-import and export-boundary tests passed.
- Command/check: three separate `uv run --package txt2crs python -c ...`
  clean-process import probes.
  - Result: PASS - preparation direct import, generation facade import, and
    jobs facade import all succeeded.
- Command/check: `uv run --package txt2crs mypy src/txt2crs/generation/__init__.py src/txt2crs/jobs/__init__.py src/txt2crs/ingestion/__init__.py`
  - Result: PASS - strict type checking reported no issues.
- Command/check: focused Ruff check for the three package initializers and
  export test.
  - Result: PASS.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- State freshness/import safety: supported exports no longer rely on pytest's
  incidental module import order.
- API containment: local acceptance and private projection helpers remain
  module-internal even though their persisted contracts are composable.

---

## Next Task

### Task T020 - Pass The Focused Session Regression Gate

**Started**: 2026-07-19 15:39 IDT
**Completed**: 2026-07-19 15:43 IDT
**Duration**: 4 minutes

**Notes**:

- Ran all session-touched routing, media/URL compatibility, request/default,
  preference, policy, preparation, pipeline, executor, projection, restart,
  and facade tests in one process.
- Confirmed the lazy package exports do not mask cross-suite import behavior.

**Verification**:

- Command/check: focused 12-file pytest command from the engine package root.
  - Result: PASS - 121 tests passed in 3.77 seconds.
- BQC integration scan: ordering, recovery, curriculum bounds, terminal policy,
  public privacy, and import-order assertions all ran together.
  - Result: PASS - no focused regression remained.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

---

## Next Task

### Task T021 - Pass The Complete Engine Suite

**Started**: 2026-07-19 15:44 IDT
**Completed**: 2026-07-19 15:45 IDT
**Duration**: 1 minute

**Verification**:

- Command/check: `uv run --package txt2crs pytest -q`
  - Result: PASS - 350 tests passed and the one live Codex subscription
    acceptance test remained explicitly skipped behind
    `TXT2CRS_RUN_LIVE_CODEX=1`.
- Regression scope: all credential-free engine unit, integration, acceptance,
  package-boundary, persistence, rendering, and security tests.
  - Result: PASS - no session-caused regression remained.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

---

## Next Task

### Task T022 - Pass Formatting, Lint, And Strict Types

**Started**: 2026-07-19 15:46 IDT
**Completed**: 2026-07-19 15:50 IDT
**Duration**: 4 minutes

**Notes**:

- Applied the package formatter to 11 session-touched files and organized two
  test import blocks.
- Tightened the executor test helper to the actual lazy pipeline-factory
  protocol after strict mypy identified an overly broad `object` annotation.

**Verification**:

- Command/check: `uv run --package txt2crs ruff format --check .`
  - Result: PASS - all 119 files are formatted.
- Command/check: `uv run --package txt2crs ruff check .`
  - Result: PASS - no lint findings.
- Command/check: `uv run --package txt2crs mypy`
  - Result: PASS - no issues in 119 source files.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Contract typing: the test composition boundary now proves structural
  conformance to `DurablePipelineFactory`.

---

## Next Task

### Task T023 - Validate Distribution And Repository Engine Gate

**Started**: 2026-07-19 15:51 IDT
**Completed**: 2026-07-19 15:53 IDT
**Duration**: 2 minutes

**Verification**:

- Command/check: `uv run --package txt2crs python -m build --outdir /tmp/txt2crs-session03-dist`
  - Result: PASS - built `txt2crs-0.3.5.tar.gz` and
    `txt2crs-0.3.5-py3-none-any.whl`.
- Archive inspection: checked both distribution member lists for
  `generation/preferences.py`, `ingestion/routing_url.py`, and
  `jobs/preparation.py`.
  - Result: PASS - every new runtime module is present in wheel and sdist.
- Command/check: `scripts/validate-changes.sh engine`
  - Result: PASS - repository engine lint, strict mypy, and complete pytest
    gates all passed.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

---

## Next Task

### Task T024 - Complete Session Audit

**Started**: 2026-07-19 15:54 IDT
**Completed**: 2026-07-19 16:01 IDT
**Duration**: 7 minutes

**Notes**:

- Audited every tracked or untracked session file for ASCII content, Unix LF
  line endings, final newlines, and whitespace errors.
- Replaced a non-ASCII language fixture with an ASCII transliteration while
  preserving the explicit detected-language contract.
- Removed the obsolete exact-age/raw-text `ContentPolicy.evaluate` compatibility
  method now that the executor uses only stored `LearnerAgeGroup` and explicit
  two-stage policy APIs.
- Rechecked the public projection and safe exception paths for input text,
  provider values, request hashes, policy internals, and checkpoint data.

**Verification**:

- Command/check: `git diff --check`
  - Result: PASS - no whitespace errors.
- Encoding/line-ending audit across 29 changed/untracked files.
  - Result: PASS - zero non-ASCII files, zero carriage returns, and zero
    missing final newlines.
- Public/private field scan plus the sentinel-based public projection tests.
  - Result: PASS - no normalized input, policy decision, prepared preferences,
    request hash, usage record, or budget snapshot is copied to public output.
- Safe error scan plus policy/preparation/executor tests.
  - Result: PASS - terminal errors expose only fixed reviewed messages and
    stable codes.
- Final command/check: package-wide Ruff format/lint, strict mypy, and pytest.
  - Result: PASS - 119 files formatted/lint-clean/type-clean; 350 tests passed
    and one live credential-gated test skipped.
- UI product-surface check: N/A - Engine-only session.
- UI craft check: N/A - Engine-only session.

**BQC Fixes**:

- Privacy minimization: removed the last exact-age compatibility surface from
  content policy.
- Repository hygiene: all session-authored files now satisfy the required
  ASCII/LF contract.

---

## Session Summary

All 24 tasks are complete. Session 03 now provides canonical URL routing,
immutable preference/default/shape contracts, two-stage provider-free policy
preparation, local plan/module gates, durable resolved preferences,
preparation-first lazy execution, restart reuse, and privacy-safe public
progress.

## Next Task

Run `creview` for `phase01-session03-input-preferences-and-policy-gate`.
