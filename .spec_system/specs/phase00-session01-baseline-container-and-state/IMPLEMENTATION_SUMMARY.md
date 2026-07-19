# Implementation Summary

**Session ID**: `phase00-session01-baseline-container-and-state`
**Package**: cross-cutting (`backend-shell`, `txt2crs-engine`, `frontend`)
**Completed**: 2026-07-19
**Duration**: approximately 1 hour

---

## Overview

Completed the reproducible application baseline for txt2crs. Both backend
image targets now install the workspace engine, run one non-root FastAPI
process, and provision private owner-only state. The shell validates typed
filesystem boundaries, Compose persists the image-owned state root, and the
remaining visible donor identity was replaced with shared txt2crs branding.
Deterministic tests, real image smokes, rendered UI checks, and database-backed
application coverage protect the baseline.

---

## Deliverables

### Files Created

| File | Purpose | Lines |
|------|---------|-------|
| `backend/tests/core/test_txt2crs_settings.py` | Typed private-path and confinement regressions | 238 |
| `backend/tests/scripts/test_container_contract.py` | Image and Compose topology contracts | 116 |
| `frontend/src/lib/branding.ts` | Canonical product name and page-title helper | 19 |
| `frontend/src/lib/branding.test.ts` | Shared branding unit contract | 18 |
| `scripts/verify-production-baseline.sh` | Production import, identity, mode, and volume-reopen smoke | 90 |
| `implementation-notes.md` | Task-by-task decisions and implementation evidence | 786 |
| `code-review.md` | Base-commit review and repair ledger | 200 |
| `security-compliance.md` | Scoped security and GDPR validation | 107 |
| `validation.md` | Complete validation gate and evidence mapping | 255 |

### Files Modified

| File | Changes |
|------|---------|
| `backend/Dockerfile` | Workspace install order, fixed non-root identity, private directories, and one process |
| `backend/app/core/config.py` | Typed normalized private paths with confinement and overlap validation |
| `.env.example`, `backend/.env.example` | Truthful product and container/host path documentation |
| `docker-compose.yml`, `docker-compose.override.yml` | Fixed private state topology, safe local command, and txt2crs tracing identity |
| `scripts/validate-changes.sh` | Deterministic baseline tests plus review-surface lint/format coverage |
| `frontend/index.html`, components, routes, and SVG assets | Shared txt2crs document, visible, and accessible identity |
| `frontend/package.json`, `frontend/package-lock.json` | Removed unused learner-surface devtool packages |
| `.spec_system/` PRD and state files | Recorded validation, completion, and Phase 00 archive state |

---

## Technical Decisions

1. **Pin container state to the image-owned path**: A non-root image cannot
   safely initialize an arbitrary fresh volume target. Compose therefore uses
   `/var/lib/txt2crs`, while host-only Settings remain configurable.
2. **Reject unsafe paths at startup**: Absolute, normalized, non-symlinked,
   non-overlapping persistent children fail closed before engine composition.
3. **Keep one application process**: The P0 serial worker and SQLite store
   require one FastAPI process until a future queue architecture exists.
4. **Keep branding centralized**: Route metadata and accessible names use one
   typed helper, avoiding repeated donor or product strings.

---

## Test Results

| Metric | Value |
|--------|-------|
| Tests collected | 422 |
| Passed | 421 |
| Failed | 0 |
| Skipped | 1 explicitly live-gated provider test |
| Coverage | N/A - not part of the configured Phase 00 gate |

Production and development images also imported `txt2crs` as UID 1001, and
the production marker survived replacement-container reopen.

---

## Lessons Learned

1. A configurable container mount target is unsafe unless its ownership is
   initialized by an explicit privileged boundary; fixed image-owned targets
   keep the non-root contract honest.
2. `_env_file=None` does not disable inherited process variables in Pydantic
   Settings tests; deterministic configuration tests must isolate the exact
   environment keys they own.
3. Rendered QA caught learner-visible devtool launchers that static title
   checks could not reveal.

---

## Future Considerations

1. Phase 01 should compose only through the public `txt2crs` facade and reuse
   these validated paths rather than adding shell-side engine logic.
2. Phase 02 should make readiness and lifecycle ownership explicit before any
   request is admitted.
3. Phase 03 should remove the donor `items` domain only after durable jobs
   acceptance coverage passes.

---

## Session Statistics

- **Tasks**: 21 completed
- **Product/test files created**: 5
- **Implementation files modified**: 26 before workflow closeout
- **Tests added**: 29
- **Implementation blockers**: 2 resolved
- **Code-review findings**: 8 resolved
