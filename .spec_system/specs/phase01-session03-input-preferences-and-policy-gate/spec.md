# Session Specification

**Session ID**: `phase01-session03-input-preferences-and-policy-gate`
**Phase**: 01 - Engine Application Boundary
**Status**: Planned
**Created**: 2026-07-19
**Base Commit**: 70ce4599cbf9bd212b226e6328b8763318561d3e
**Package**: backend/packages/txt2crs
**Package Stack**: Python 3.14, Pydantic v2, SQLite

---

## 1. Session Overview

This session establishes a durable, provider-free preparation boundary between
an accepted `GenerationRequest` and provider-backed course generation. The
engine will run cheap request preflight, route and ingest the accepted source,
evaluate the normalized content, freeze the accepted policy decision and
pre-planning preferences, and persist that cumulative preparation before any
research coordinator or Codex runtime method can run.

The session also closes the preference gap in the generation pipeline. P0
defaults and curriculum bounds become immutable execution-profile data;
language is resolved deterministically during ingestion; and audience, prior
knowledge, learning goals, and level are either enforced from explicit intent
or resolved from the accepted course plan. The resolved learning contract is
checkpointed with the locally accepted course plan before module drafting.

It follows durable request recovery because preparation must load the exact
stored request rather than accept caller-supplied generation values. It
precedes managed runtime work because Session 04 must start provider resources
only after this session's accepted preparation checkpoint exists.

---

## 2. Objectives

1. Route one validated public URL to YouTube transcript ingestion or general
   URL ingestion entirely inside the package.
2. Store stable P0 preference defaults and curriculum shape limits with the
   accepted execution profile.
3. Split policy into cheap preflight and normalized-content decisions using the
   privacy-minimized learner age group.
4. Persist and recover accepted prepared content, policy state, and preference
   state without refetching input or applying current defaults.
5. Locally accept only course plans aligned with the learning contract and
   checkpoint resolved preferences before any module drafting call.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase01-session01-durable-requests-and-recovery` - Provides the exact
  stored request, immutable execution profile, atomic admission, latest
  checkpoint, and deterministic runnable-job recovery contracts.
- [x] `phase01-session02-safe-queries-and-artifact-access` - Provides the
  public projection that must remain compatible with the new preparation
  checkpoint.

### Required Tools Or Knowledge

- Existing `IngestionService`, typed file/URL/transcript adapters,
  `ContentPolicy`, `CourseGenerationPipeline`, and `GenerationJobExecutor`.
- Pydantic v2 strict contracts, package SQLite checkpoints, deterministic
  canonical hashing, local curriculum validation, and bounded repair behavior.
- The implementation-plan defaults in sections 5.5 and 5.6.

### Environment Requirements

- Run package commands from `backend/packages/txt2crs/`.
- Default verification is credential-free and network-free.
- Provider and ingestion fakes can count construction, fetch, research, and
  model calls independently.

---

## 4. Scope

### In Scope (MVP)

- A `RoutingUrlAdapter` registered for the existing `url` input type. It
  canonicalizes one public URL at the routing boundary, recognizes the exact
  supported YouTube host allowlist, and delegates to only the selected adapter.
- Deterministic script-level language detection with the existing English
  fallback. `language="auto"` freezes the detected value; an explicit
  language remains an enforceable course-plan value.
- Immutable execution-profile contracts for the documented P0 preference
  defaults and curriculum shape limits: 5-12 objectives, 3-6 modules, 2-5
  sections per module, and 3-12 content blocks per section.
- A concrete resolved learning contract with explicit `level` and
  `learning_goals`; neither field is overloaded into `desired_depth`.
- Required consent, age-group-aware preflight, and normalized post-ingestion
  policy with a versioned, safe decision code.
- One cumulative preparation checkpoint containing the exact request hash,
  bounded `InputDocument`, accepted policy decision, and frozen planning
  preferences.
- Pipeline checkpoints that carry preparation forward and require resolved
  preferences with the accepted course plan.
- Local plan validation for objective/module/section bounds and explicit
  audience, prior knowledge, language, level, duration, accessibility, and
  learning-goal alignment. Content-block bounds are enforced when each module
  draft is accepted.
- One bounded course-plan repair opportunity after either schema rejection or
  local learning-contract rejection.
- Executor recovery from preparation or later cumulative checkpoints without
  re-ingestion, policy reinterpretation, or caller-supplied generation values.
- Safe terminal failure for rejected and review-required P0 decisions, with no
  research or Codex factory/call after that outcome.
- Public job projection compatibility for a preparation-only latest
  checkpoint without exposing prepared text, policy internals, or preferences.

### Out Of Scope (Deferred)

- Managed FastMCP startup/stop, Codex discovery, GPT-5.6 selection, provider
  authentication, and context-managed provider graph cleanup - Session 04.
- Final real/deterministic application factories and owner-wide purge -
  Session 05.
- FastAPI multipart validation, HTTP error mapping, and submission endpoints -
  Phase 03.
- Learner preference controls, language/RTL controls, and accessibility UI -
  Phase 04 or P1 as assigned by the master plan.
- Image, audio, and video product enablement.

---

## 5. Technical Approach

### Architecture

Add `txt2crs.ingestion.routing_url` with a small URL-normalizer protocol and a
`RoutingUrlAdapter`. The router requires a string URL, canonicalizes it once for
dispatch, selects YouTube only from the reviewed exact host set, rebuilds the
payload with the canonical URL, and invokes one child adapter. Child adapters
retain their own transport-response validation; the shell never parses hosts or
selects ingestion behavior.

Add immutable `LearningPreferenceDefaults` and `CurriculumShapeLimits` to the
accepted `ExecutionProfile`. New requests therefore hash every server-selected
default and bound that can change output. Existing incompatible persisted
profiles fail through the request compatibility boundary; recovery never
substitutes current settings. Extend `LearningPreferences` into the concrete
post-plan contract with a non-auto level and explicit learning goals. Keep the
pre-plan state separate so an unresolved value cannot masquerade as resolved.

Refactor `ContentPolicy` into two explicit methods. `evaluate_preflight` checks
consent and the available prompt/text/URL request language. Binary file names
are not treated as document content. `evaluate_ingested_content` checks the
bounded normalized `InputDocument`. Both methods use `LearnerAgeGroup`, return
strict versioned `PolicyDecision` objects, and never accept a client-controlled
high-risk override. In P0, both `human_review` and `rejected` are terminal.

Add `txt2crs.jobs.preparation`. `GenerationPreparationService` accepts the
stored `GenerationRequest`, repeats/uses the cheap preflight as a fail-closed
package boundary, ingests the exact payload, runs post-ingestion policy, and
builds an immutable `GenerationPreparation`. That model freezes the request
hash, `InputDocument`, accepted policy decision, detected/explicit language,
original preference intent, and execution-profile defaults. It contains no
runtime, research client, token data, credentials, or filesystem path.

Persist preparation as sequence 1, stage `prepare_input`, while the job remains
non-terminal. Later `PipelineCheckpoint` objects embed the complete accepted
preparation, begin with `plan_research` at sequence 2, and include
`resolved_preferences` from `design_course` onward. The pipeline no longer owns
raw input ingestion. It receives accepted preparation, validates its request
hash on resume, and uses only checkpointed values.

Add a preference resolver and local course-plan gate. Before planning, fixed
defaults and the frozen language are available to the research/course turns.
After `CoursePlan` returns, the resolver:

- preserves explicit audience, prior knowledge, language, level, and goals;
- derives omitted audience and goals from the accepted plan;
- represents no prerequisites with one stable P0 phrase;
- copies a concrete auto-selected level from the schema-constrained plan;
- requires explicit goals to match objective descriptions after deterministic
  whitespace/case normalization;
- requires the plan to preserve duration and accessibility defaults; and
- enforces execution-profile objective/module/section bounds.

The design-course stage may spend the existing single repair allowance when
the local gate rejects an otherwise schema-valid plan. The accepted plan and
resolved preferences are checkpointed atomically before the first
`write_module` call. Module acceptance also enforces the stored content-block
range.

Refactor `GenerationJobExecutor` to load its request from `ResumeState`, not
from method arguments. It prepares and checkpoints once when no checkpoint
exists, reuses a `GenerationPreparation` when sequence 1 already exists, and
invokes a lazy pipeline factory only after allowed preparation is durable.
Recording tests prove ingestion adapters are not repeated after restart and
pipeline factory/research/model calls remain zero on all terminal policy paths.
Session 04 may strengthen the lazy factory into a managed resource context
without changing this ordering contract.

Update public projection to parse either a preparation checkpoint or a
cumulative pipeline checkpoint. It can derive only the already-approved safe
input label, warnings, stage, and bounded progress; prepared text, decisions,
preference values, and request hashes remain private.

### Design Patterns

- Two-phase gate: cheap request preflight followed by normalized-content
  policy after bounded ingestion.
- Durable prepare-then-run: checkpoint all provider-independent work before
  obtaining the provider-backed pipeline.
- Intent/resolution split: keep learner intent distinct from the concrete
  accepted learning contract.
- Versioned configuration snapshot: hash defaults and shape limits into the
  execution profile instead of reading mutable server values during recovery.
- Local acceptance gate: treat schema validity as necessary but not sufficient
  for a course plan.
- Lazy dependency factory: construction/calls for provider work are impossible
  before accepted preparation is persisted.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/ingestion/routing_url.py` | Canonical public-URL routing to the YouTube or general URL adapter | ~130 |
| `backend/packages/txt2crs/src/txt2crs/generation/preferences.py` | Pre-plan preference snapshot, resolved contract, shape/alignment validation, and safe errors | ~260 |
| `backend/packages/txt2crs/src/txt2crs/jobs/preparation.py` | Provider-free preflight, ingestion, post-policy decision, and cumulative preparation contract | ~240 |
| `backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py` | One-validation dispatch, host allowlist, canonical payload, and selected-adapter tests | ~180 |
| `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py` | Default/auto/explicit resolution and curriculum shape/alignment tests | ~300 |
| `backend/packages/txt2crs/tests/unit/test_generation_preparation.py` | Two-stage policy, bounded ingestion, immutable checkpoint, and terminal decision tests | ~300 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` | Add immutable P0 defaults/shape limits to the execution profile and canonical request identity | ~120 |
| `backend/packages/txt2crs/src/txt2crs/generation/models.py` | Define the explicit concrete level and learning-goal contract | ~45 |
| `backend/packages/txt2crs/src/txt2crs/security/policy.py` | Split preflight/post-ingestion evaluation and version safe decisions | ~150 |
| `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py` | Consume preparation, persist resolved preferences, shift sequences, validate/repair plans, and enforce module block bounds | ~260 |
| `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` | Load durable requests, persist/reuse preparation, terminally settle policy, and lazily obtain the pipeline | ~220 |
| `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` | Safely project preparation-only and cumulative pipeline checkpoints | ~90 |
| `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py` | Export the supported routing adapter | ~15 |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Export supported preparation contracts/errors | ~20 |
| `backend/packages/txt2crs/tests/factories.py` | Supply versioned defaults, shape limits, preparation, and resolved checkpoint fixtures | ~180 |
| `backend/packages/txt2crs/tests/unit/test_content_policy.py` | Cover age-group preflight/post-ingestion outcomes and safe versioned codes | ~180 |
| `backend/packages/txt2crs/tests/unit/test_generation_requests.py` | Cover canonical defaults/limits, mutation isolation, and recovery compatibility | ~140 |
| `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py` | Cover local plan repair/rejection and resolved-preference checkpoint order | ~260 |
| `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` | Cover real SQLite preparation persistence, lazy provider ordering, terminal policy, and restart reuse | ~320 |
| `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` | Cover safe preparation-only progress and privacy projection | ~100 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] Recognized YouTube hosts reach only transcript ingestion; other approved
  public hosts reach only general URL ingestion after one routing
  canonicalization.
- [ ] The accepted request hash covers every P0 default and curriculum bound.
- [ ] Auto language freezes deterministic ingestion detection with English
  fallback, while explicit language and level remain locally enforceable.
- [ ] Omitted and explicit audience, prior knowledge, learning goals, and level
  resolve deterministically into one concrete learning contract.
- [ ] Course plans outside objective/module/section, level, audience,
  prerequisite, language, duration, accessibility, or goal-alignment rules
  never reach module drafting.
- [ ] Module drafts outside the stored content-block range cannot be
  checkpointed.
- [ ] Consent/available request text is evaluated at preflight and normalized
  content is evaluated after ingestion.
- [ ] Rejected or review-required policy outcomes settle safely and never
  construct or call the pipeline, research coordinator, or model runtime.
- [ ] Accepted preparation is durable before the first provider-backed
  pipeline action.
- [ ] Restart from preparation or a later checkpoint neither refetches the
  input nor applies new policy/default/preference interpretation.
- [ ] Public projection accepts preparation-only state without exposing source
  text, policy details, preferences, request hashes, or provider state.

### Testing Requirements

- [ ] Failing routing, preference, policy/preparation, pipeline, executor, and
  projection tests are written and observed before production implementation.
- [ ] Focused tests use recording fakes to prove call ordering and zero provider
  work on every denied path.
- [ ] A real SQLite restart test reuses the preparation checkpoint and resolved
  course-plan checkpoint.
- [ ] The complete credential-free engine suite passes with live tests gated.
- [ ] The built wheel contains the new preparation, preference, and routing
  modules.

### Non-Functional Requirements

- [ ] Input transport and normalized content remain within stored execution
  limits; no silent truncation is introduced.
- [ ] Preparation and resolved-preference contracts are strict, immutable, and
  bound to the exact durable request hash.
- [ ] Safe policy exceptions/messages do not include request text, normalized
  content, URLs, file names, provider values, or checkpoint dictionaries.
- [ ] No FastAPI, PostgreSQL, Alembic, frontend, credential, or filesystem-path
  behavior enters the package session.

### Quality Gates

- [ ] All session-authored files are ASCII-encoded with Unix LF endings.
- [ ] Code has complete types, descriptive names, and intern-friendly comments
  around routing, policy ordering, immutable resolution, checkpoint unions,
  local acceptance, and lazy provider construction.
- [ ] Ruff formatting/lint, strict mypy, pytest, package build, and repository
  engine validation pass from their documented roots.

---

## 8. Implementation Notes

### Working Assumptions

- "Provider-free preparation" forbids research coordination, Tavily research,
  and Codex work. A selected source-ingestion transport may fetch the submitted
  public URL or transcript because obtaining normalized input is the purpose of
  preparation; tests keep those transports behind recording adapters.
- The current script detector is the authoritative P0 language detector.
  Unsupported/no-script input retains its existing English fallback, and
  mixed-script input retains the existing `mixed` value and warning.
- Exact normalized description matching is the P0 learning-goal alignment
  rule. The course-planning prompt must copy explicit goals into objective
  descriptions; semantic similarity is not treated as a deterministic local
  check.
- An omitted audience is accepted from the course plan. Omitted prior knowledge
  resolves from plan prerequisites, falling back to the documented
  no-prerequisite phrase when the plan supplies none.
- Preparation stage sequence 1 replaces the pipeline-owned `ingest_input`
  checkpoint. This preserves the existing later sequence numbers
  (`plan_research` remains sequence 2) while moving ingestion out of the
  provider-backed pipeline.

### Conflict Resolutions

- Existing `GenerationJobExecutor.execute` accepts raw payload, concrete
  preferences, consent, and age values even though the durable request is the
  source of truth. The durable request wins; this session removes those
  caller-supplied generation values.
- Existing `LearningPreferences` lacks level and goals and is supplied before
  `auto` values can be selected. The plan requirement wins; this session keeps
  a separate frozen pre-plan context and creates the concrete learning contract
  only after local course-plan acceptance.
- Existing policy treats an approved high-risk flag as a continuation path.
  P0 has no qualified-review workflow, so the implementation-plan terminal
  policy wins and no client or caller can approve the job through.
- Existing pipeline checkpoints contain an `ingest_input` stage and do not
  record policy or resolved preferences. Recovery correctness wins; the new
  cumulative checkpoint schema begins with `prepare_input` and fails closed on
  incompatible private state instead of refetching or guessing.

---

## 9. Dependencies

### Depends On

- `phase01-session01-durable-requests-and-recovery`
- `phase01-session02-safe-queries-and-artifact-access`
- Existing package ingestion, policy, generation, job-store, and projection
  contracts.

### Enables

- `phase01-session04-managed-runtime-and-model-policy`
- `phase01-session05-public-facade-and-owner-lifecycle`
- Phase 02 truthful application composition/readiness.
- Phase 03 shell submission and worker lifecycle without duplicated policy.

---

## 10. Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| New preparation checkpoint breaks public projection or later resume | High | Parse stage-discriminated checkpoint contracts and cover preparation/pipeline restart paths with real SQLite |
| Auto values are re-resolved after restart | High | Freeze language/default context in preparation and concrete preferences with course-plan acceptance |
| Policy denial still starts provider resources | Critical | Lazy pipeline factory plus zero-call recording tests for preflight and post-ingestion denial |
| Course plan is schema-valid but ignores learner intent | High | Local deterministic gate and one bounded repair before checkpoint/drafting |
| URL host parsing creates a shell or adapter bypass | High | One package router, exact host allowlist, canonical payload, and selected-child-only tests |
| Execution-profile additions change old request compatibility | Medium | Treat incompatible stored profiles as safe compatibility failures; never hydrate from mutable current configuration |
| Broad pipeline fixture changes cause regressions | Medium | Update shared factories first after failing contract tests, then run focused and complete suites |

---

## 11. References

- `.spec_system/PRD/PRD.md`
- `.spec_system/PRD/phase_01/PRD_phase_01.md`
- `.spec_system/PRD/phase_01/session_03_input_preferences_and_policy_gate.md`
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` sections 5.5 and 5.6
- `.spec_system/CONSIDERATIONS.md`
- `.spec_system/SECURITY-COMPLIANCE.md`
- `backend/AGENTS.md`
- `backend/packages/txt2crs/src/txt2crs/jobs/requests.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`
- `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`
- `backend/packages/txt2crs/src/txt2crs/security/policy.py`
- `backend/packages/txt2crs/src/txt2crs/ingestion/service.py`
