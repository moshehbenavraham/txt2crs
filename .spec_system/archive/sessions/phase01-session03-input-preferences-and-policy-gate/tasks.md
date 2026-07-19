# Task Checklist

**Session ID**: `phase01-session03-input-preferences-and-policy-gate`
**Total Tasks**: 24
**Estimated Duration**: 3-4 hours
**Created**: 2026-07-19

---

Legend: `[x]` completed; `[ ]` pending; `[P]` parallelizable; `[SNNMM]` session ref; `TNNN` task ID.

---

## Setup And Tests First (7 tasks)

- [x] T001 [S0103] Run the Apex Spec analyzer plus the existing request, ingestion, URL/transcript, policy, pipeline, executor, and public-projection baselines from the engine package root (`.spec_system/scripts/analyze-project.sh`, `backend/packages/txt2crs/tests/unit/test_generation_requests.py`, `backend/packages/txt2crs/tests/unit/test_ingestion_service.py`, `backend/packages/txt2crs/tests/unit/test_url_ingestion.py`, `backend/packages/txt2crs/tests/unit/test_media_ingestion.py`, `backend/packages/txt2crs/tests/unit/test_content_policy.py`, `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py`, `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`, `backend/packages/txt2crs/tests/unit/test_public_job_queries.py`)
- [x] T002 [S0103] Write failing URL-router tests for one canonicalization, exact YouTube-host selection, general public-host selection, canonical child payloads, malformed/non-string input, and selected-child-only calls (`backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py`)
- [x] T003 [S0103] Write failing request/profile and preference tests for frozen P0 defaults, curriculum bounds, canonical hashing, auto/explicit language and level, audience/prior-knowledge resolution, explicit/derived goals, and local alignment/shape rejection (`backend/packages/txt2crs/tests/unit/test_generation_requests.py`, `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py`)
- [x] T004 [S0103] Write failing two-stage policy and preparation tests for consent, privacy-minimized age groups, request-text availability, binary post-ingestion detection, safe versioned decisions, immutable preparation, and bounded adapter calls (`backend/packages/txt2crs/tests/unit/test_content_policy.py`, `backend/packages/txt2crs/tests/unit/test_generation_preparation.py`)
- [x] T005 [S0103] Write failing pipeline tests for prepared-input consumption, request-hash binding, local course-plan repair/rejection, resolved-preference checkpointing before module drafting, and content-block bounds (`backend/packages/txt2crs/tests/integration/test_generation_pipeline.py`)
- [x] T006 [S0103] Write failing real-SQLite executor tests for preparation-first persistence, lazy pipeline creation, terminal preflight/post-ingestion policy, preparation restart reuse, resolved-preference restart reuse, and removal of caller-supplied request values (`backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`)
- [x] T007 [S0103] Write failing preparation-only public projection/privacy tests, run every new focused suite, and record the expected pre-implementation failures (`backend/packages/txt2crs/tests/unit/test_public_job_queries.py`, `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/implementation-notes.md`)

---

## Foundation (5 tasks)

- [x] T008 [S0103] Implement strict immutable P0 preference-default and curriculum-shape contracts in the accepted execution profile, including canonical request identity and compatibility failure behavior (`backend/packages/txt2crs/src/txt2crs/jobs/requests.py`)
- [x] T009 [S0103] Implement the explicit concrete `LearningPreferences` level/learning-goal contract plus frozen pre-plan and safe resolution-error contracts (`backend/packages/txt2crs/src/txt2crs/generation/models.py`, `backend/packages/txt2crs/src/txt2crs/generation/preferences.py`)
- [x] T010 [S0103] Implement versioned preflight/post-ingestion `ContentPolicy` decisions using `LearnerAgeGroup` and remove caller-approved high-risk continuation (`backend/packages/txt2crs/src/txt2crs/security/policy.py`)
- [x] T011 [S0103] Implement strict immutable `GenerationPreparation`, safe terminal error, and provider-free `GenerationPreparationService` contracts bound to the exact request hash (`backend/packages/txt2crs/src/txt2crs/jobs/preparation.py`)
- [x] T012 [S0103] Update shared request, preparation, resolved-preference, and cumulative-checkpoint factories so all later tests use one canonical contract source (`backend/packages/txt2crs/tests/factories.py`)

---

## Implementation (7 tasks)

- [x] T013 [S0103] Implement `RoutingUrlAdapter` canonical dispatch and export it without moving URL/host behavior into the shell (`backend/packages/txt2crs/src/txt2crs/ingestion/routing_url.py`, `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py`)
- [x] T014 [S0103] Implement deterministic planning-preference freezing and course-plan resolution for auto/explicit language, level, audience, prior knowledge, goals, and all server defaults (`backend/packages/txt2crs/src/txt2crs/generation/preferences.py`)
- [x] T015 [S0103] Implement local objective/module/section/alignment validation and module content-block validation against the stored `CurriculumShapeLimits` (`backend/packages/txt2crs/src/txt2crs/generation/preferences.py`, `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`)
- [x] T016 [S0103] Refactor cumulative checkpoints and the pipeline to consume accepted preparation, bind the durable request hash, carry preparation forward, checkpoint resolved preferences with `design_course`, and spend at most one repair before drafting (`backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`)
- [x] T017 [S0103] Refactor the executor to load `GenerationRequest` from resume state, persist/reuse sequence-1 preparation, settle denied policy safely, and obtain/call the lazy pipeline only after accepted preparation is durable (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`)
- [x] T018 [S0103] Extend public projection to recognize preparation-only and pipeline checkpoints while allowlisting only safe input/progress data (`backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py`)
- [x] T019 [S0103] Export supported preparation/preference contracts and update package call sites/tests without exporting internal resolver, policy-matching, or checkpoint parsing helpers (`backend/packages/txt2crs/src/txt2crs/jobs/__init__.py`, `backend/packages/txt2crs/src/txt2crs/generation/__init__.py`, `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py`)

---

## Testing And Completion (5 tasks)

- [x] T020 [S0103] Run and repair the focused routing, request/preference, policy/preparation, pipeline, executor, and projection suites until all ordering, recovery, bounds, and privacy assertions pass (`backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py`, `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py`, `backend/packages/txt2crs/tests/unit/test_generation_preparation.py`, `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py`, `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`)
- [x] T021 [S0103] Run the complete credential-free engine suite and repair every session-caused regression, leaving the live compatibility test explicitly gated (`backend/packages/txt2crs/pyproject.toml`)
- [x] T022 [S0103] Run Ruff formatting/lint and strict mypy from the engine package root and repair all findings (`backend/packages/txt2crs/pyproject.toml`)
- [x] T023 [S0103] Build wheel/sdist, inspect that routing/preparation/preference modules ship, and run the repository engine validation command (`backend/packages/txt2crs/pyproject.toml`, `scripts/validate-changes.sh`)
- [x] T024 [S0103] Audit session files for ASCII/LF, confirm no input/provider/private policy state entered public output or errors, update task evidence and implementation notes, and prepare the session for `creview` (`.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/implementation-notes.md`, `.spec_system/specs/phase01-session03-input-preferences-and-policy-gate/tasks.md`)

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] implementation-notes.md updated
- [x] Ready for `creview` (next step in the implement -> creview -> validate sequence)

---

## Next Steps

Run the `validate` workflow step after `creview` records all findings resolved.
