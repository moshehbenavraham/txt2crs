# Implementation Summary

**Session ID**: `phase01-session03-input-preferences-and-policy-gate`
**Package**: backend/packages/txt2crs
**Completed**: 2026-07-19
**Duration**: 1.1 hours

---

## Overview

Session 03 established the provider-free boundary between one durable
generation request and provider-backed course work. The engine now routes
accepted URLs inside the package, freezes generation-affecting defaults,
evaluates request and normalized content policy in order, checkpoints accepted
preparation, resolves the concrete learning contract, rejects locally
misaligned plans and modules, and safely resumes or projects the new state.

---

## Deliverables

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `backend/packages/txt2crs/src/txt2crs/generation/preferences.py` | Frozen intent, concrete preference resolution, and local shape/alignment gates | 309 |
| `backend/packages/txt2crs/src/txt2crs/ingestion/routing_url.py` | Canonical YouTube/general URL delegation | 73 |
| `backend/packages/txt2crs/src/txt2crs/jobs/preparation.py` | Provider-free policy, ingestion, and durable preparation boundary | 175 |
| `backend/packages/txt2crs/tests/unit/test_generation_preparation.py` | Preparation ordering, bounds, immutability, and failure coverage | 206 |
| `backend/packages/txt2crs/tests/unit/test_learning_preference_resolution.py` | Resolution, alignment, and curriculum-limit coverage | 327 |
| `backend/packages/txt2crs/tests/unit/test_public_package_exports.py` | Clean-process facade and private-helper boundary coverage | 61 |
| `backend/packages/txt2crs/tests/unit/test_routing_url_ingestion.py` | Canonical host routing and selected-adapter coverage | 201 |

### Files Modified

| File | Changes |
|------|---------|
| `backend/packages/txt2crs/src/txt2crs/generation/__init__.py` | Exported supported preference contracts through import-safe lazy boundaries |
| `backend/packages/txt2crs/src/txt2crs/generation/models.py` | Added immutable concrete level and learning goals |
| `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py` | Consumed preparation, enforced local plan/module gates, and checkpointed resolved preferences |
| `backend/packages/txt2crs/src/txt2crs/ingestion/__init__.py` | Exported the routing URL adapter |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Exported preparation/default contracts through lazy package boundaries |
| `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` | Loaded durable requests, persisted/reused preparation, and delayed provider construction |
| `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` | Projected preparation-only progress through a private-state allowlist |
| `backend/packages/txt2crs/src/txt2crs/jobs/requests.py` | Hashed immutable P0 defaults and curriculum limits into accepted requests |
| `backend/packages/txt2crs/src/txt2crs/security/policy.py` | Split versioned preflight and normalized-content policy |
| `backend/packages/txt2crs/tests/factories.py` | Centralized canonical preparation, preferences, and checkpoint fixtures |
| `backend/packages/txt2crs/tests/integration/test_generation_job_executor.py` | Added real SQLite ordering, denial, settlement, and restart scenarios |
| `backend/packages/txt2crs/tests/integration/test_generation_pipeline.py` | Added prepared pipeline, repair, bounds, checkpoint, and resume scenarios |
| `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py` | Migrated restart projection coverage to preparation checkpoints |
| `backend/packages/txt2crs/tests/unit/test_content_policy.py` | Covered age-group-aware two-stage decisions and safe compatibility errors |
| `backend/packages/txt2crs/tests/unit/test_generation_requests.py` | Covered immutable defaults, ranges, hashing, and compatibility |
| `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` | Covered preparation privacy and job/request/checkpoint identity rejection |

---

## Technical Decisions

1. **Preparation is sequence one**: Persisting normalized content and its
   accepted policy decision before obtaining a provider graph makes ordering
   and recovery deterministic.
2. **Intent and resolution use different contracts**: Auto or omitted learner
   intent cannot masquerade as the concrete contract accepted with a course
   plan.
3. **Defaults are request identity**: Every server-selected P0 default and
   curriculum bound is stored and hashed so restart never applies current
   configuration.
4. **Local acceptance follows schema validation**: One bounded repair is
   allowed, but schema-valid work that violates the learner contract or stored
   shape never reaches the next checkpoint.
5. **Public state is an allowlist**: Preparation and pipeline checkpoints are
   parsed privately, bound to the exact job/request, and reduced to reviewed
   display/progress fields.

---

## Test Results

| Metric | Value |
|--------|-------|
| Tests Collected | 360 |
| Passed | 359 |
| Explicitly Gated | 1 live Codex subscription test |
| Failed | 0 |
| Coverage | Not collected by the documented package validation command |

Ruff format/lint, strict mypy, package build, wheel/sdist content inspection,
and the repository engine validation command also passed.

---

## Lessons Learned

1. Checkpoint labels must reject future artifacts, not merely require earlier
   artifacts, or a tampered resume can skip acceptance work.
2. Lazy construction is safe only when construction itself is inside terminal
   failure settlement.
3. Clean-process import tests are necessary when package facades expose
   contracts from modules with mutual type relationships.
4. Public projection must bind the job, stored request, checkpoint row, and
   nested request hash before copying even safe leaves.

---

## Future Considerations

Items for future sessions:

1. Session 04 must own one context-managed research MCP/Codex lifecycle and
   enforce reviewed GPT-5.6 discovery without fallback.
2. Session 05 must publish real/deterministic application factories and an
   idempotent owner-wide purge covering request, checkpoints, artifacts, and
   provider-owned state.
3. Phase 03 should map typed package policy and execution failures centrally
   without reconstructing preparation or provider ordering in FastAPI routes.

---

## Session Statistics

- **Tasks**: 24 completed
- **Files Created**: 7
- **Files Modified**: 16
- **Tests Added**: 48
- **Blockers**: 0 unresolved; 8 code-review findings resolved
