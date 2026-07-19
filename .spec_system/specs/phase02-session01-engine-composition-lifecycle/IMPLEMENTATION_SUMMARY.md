# Implementation Summary

**Session ID**: `phase02-session01-engine-composition-lifecycle`
**Package**: `backend`
**Completed**: 2026-07-19
**Duration**: 1.0 hours

---

## Overview

Session 01 gave the FastAPI shell one explicit owner for the public
`txt2crs` application facade. Validated finite settings now translate into one
immutable execution, storage, research, model, and admission configuration.
A missing Tavily secret produces a truthful unconfigured lifespan without
constructing a provider graph, while configured startup owns exactly one
facade and closes it on every normal and exceptional path.

The narrow public engine configuration correction also makes the factory honor
the already-deployed SQLite, artifact, Codex-home, and ephemeral worker paths.
The shell continues to import only documented public `txt2crs` boundaries.

---

## Deliverables

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `backend/app/services/txt2crs_application.py` | Public configuration translation and facade lifecycle | 321 |
| `backend/tests/services/__init__.py` | Shell service-test package marker | 1 |
| `backend/tests/services/test_txt2crs_application.py` | Exact translation, import, lifecycle, and cleanup regressions | 523 |
| `backend/tests/test_txt2crs_lifespan.py` | FastAPI lifespan ownership and route regressions | 143 |

### Files Modified

| File or Area | Changes |
|--------------|---------|
| `backend/app/core/config.py` | Added bounded P0 model, input, retry, research, run, artifact, and admission settings |
| `backend/app/main.py` and `backend/app/services/__init__.py` | Added injectable lifespan ownership and the documented shell service export |
| `backend/.env.example` | Documented 41 composition settings with a blank provider secret |
| `backend/packages/txt2crs/src/txt2crs/application/` | Added exact confined storage paths and one ephemeral worker-root contract |
| Changed shell and engine tests | Added settings, public-boundary, exact-path, cleanup, logging, and lifespan coverage |
| Apex and release records | Added session review/validation evidence, Phase 02 progress, and version synchronization |

---

## Technical Decisions

1. **Absence is an explicit capability state**: Missing or disabled research
   returns no real application config, so OpenAPI and future setup routes can
   load without a synthetic secret.
2. **The package factory remains authoritative**: Shell code translates only
   public immutable contracts and never reconstructs stores, research,
   providers, pipelines, or renderers.
3. **Exact deployed paths cross the public boundary**: SQLite and artifact
   paths are canonical strict children of one private state root; Codex
   credentials may be a distinct sibling there, while every Codex cwd remains
   under the disjoint ephemeral worker root.
4. **Cleanup outranks observers**: Facade ownership is cleared before cleanup,
   every acquired facade is closed once, and logging failures cannot skip
   cleanup or mask its authoritative error.
5. **P0 retention remains explicit**: No new time-based purge setting exists;
   the package maximum defers expiry until coordinated request/artifact
   retention is designed.

---

## Test Results

| Metric | Value |
|--------|-------|
| Complete deterministic tests | 692 collected |
| Passed | 691 |
| Explicitly live-gated | 1 Codex/Tavily acceptance |
| Focused session validation | 56 passed |
| Ruff | PASS |
| Strict mypy and ty | PASS |
| Pre-commit repository gate | PASS |
| Coverage | Not collected; no session threshold exists |

---

## Code Review Repairs

The formal base-to-head review resolved 2 High and 1 Medium findings:

1. Closed a facade returned before a later startup failure and preserved the
   primary exception when cleanup also failed.
2. Ensured shutdown logging cannot prevent facade cleanup or mask the package
   cleanup error.
3. Moved the dedicated authentication Codex cwd from durable state to the
   configured ephemeral worker root.

---

## Lessons Learned

1. Resource ownership begins when a factory returns, not when the final
   startup event is emitted.
2. Observability belongs outside authoritative cleanup ordering; logging
   failures must not leak or double-close resources.
3. Public path contracts must describe the deployed backup boundary exactly,
   including the distinction between durable credentials and ephemeral cwd.

---

## Future Considerations

Items for future sessions:

1. Session 02 should recover runnable jobs before polling and serialize all
   execution through public `ApplicationExecutor` handles.
2. Session 03 should cache bounded readiness snapshots and share runtime
   ownership with the worker and authentication ceremony.
3. Session 04 should expose safe superuser-only readiness/authentication
   routes without returning account identity, provider detail, or paths.
4. The credentialed live GPT-5.6/Tavily proof remains required before release.

---

## Session Statistics

- **Tasks**: 24 completed
- **Implementation/test files created**: 4
- **Implementation/test files modified**: 9
- **Deterministic test cases added**: 46
- **Code review findings**: 3 resolved
- **Success criteria**: 18/18
- **Blockers**: 1 local database-port conflict resolved
