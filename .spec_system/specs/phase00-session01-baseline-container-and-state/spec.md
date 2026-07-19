# Session Specification

**Session ID**: `phase00-session01-baseline-container-and-state`
**Phase**: 00 - Application Baseline
**Status**: Complete
**Created**: 2026-07-19
**Base Commit**: c26350a3f60f9b841762ad7ccbf52f65c2bdcbce
**Package**: null
**Package Stack**: Python 3.14/FastAPI/uv, Docker Compose, React 19/TypeScript

---

## 1. Session Overview

This cross-cutting baseline session makes the existing application shell
reproducible in the same production image and Compose topology that later
sessions will use. It closes the verified host-only engine import gap, removes
the four-worker runtime conflict, and gives the shell a typed private state
boundary before any durable job endpoints are introduced.

The session is next because every engine facade, readiness, worker, and jobs
session depends on a production image that can install `txt2crs`, run exactly
one non-root process, and retain SQLite, artifacts, and Codex credentials.
Existing authentication and donor-item behavior stays intact so the baseline
remains testable until Phase 03 replaces that domain.

---

## 2. Objectives

1. Prove and correct workspace-aware `txt2crs` installation in both backend
   image targets.
2. Enforce one non-root FastAPI process with private state directories owned
   by the runtime user.
3. Add typed, absolute, confined engine state paths and document their local
   and container values.
4. Persist the private state root through backend container replacement while
   preserving the existing shell smoke paths.

---

## 3. Prerequisites

### Required Sessions

- None - this is the first structured implementation session.

### Required Tools Or Knowledge

- Docker with Compose v2 and BuildKit for production-image verification.
- uv, Python 3.14, npm, and the existing repository validation scripts.
- Root, backend, and frontend `AGENTS.md` conventions.

### Environment Requirements

- Deterministic checks require no Codex or Tavily credentials.
- Full backend authentication and item smoke tests require the existing
  Compose PostgreSQL service and local `.env`.

---

## 4. Scope

### In Scope (MVP)

- The operator can build an image that imports the workspace engine - copy
  workspace package sources before dependency synchronization and verify the
  resulting production target.
- The operator can run one safe application instance - use one non-root
  FastAPI process in development and production image targets.
- The application can resolve private engine paths safely - add typed
  absolute settings for the state root, SQLite file, artifact directory,
  isolated `CODEX_HOME`, and worker directory with explicit confinement.
- The backend can retain private state - mount one named state volume separate
  from PostgreSQL and keep the research MCP port unpublished.
- A user still sees a truthful txt2crs shell - replace remaining donor product
  names in environment defaults and page metadata without redesigning routes
  or deleting `items`.
- Maintainers can detect regression - add deterministic settings and container
  contract tests plus a production runtime smoke script.

### Out Of Scope (Deferred)

- Full engine limits, secrets, readiness, and factory settings - Reason:
  Phase 02 owns composition and runtime readiness after the Phase 01 facade.
- Durable request persistence and recovery APIs - Reason: Phase 01 owns the
  engine application boundary.
- Jobs HTTP routes and donor-item removal - Reason: Phase 03 requires jobs
  acceptance coverage before the donor migration.
- Learner-facing visual redesign - Reason: Phase 04 owns the complete product
  experience.

---

## 5. Technical Approach

### Architecture

Keep configuration and deployment ownership in the FastAPI shell. `Settings`
will expose `pathlib.Path` values, derive child defaults from
`TXT2CRS_STATE_ROOT`, require absolute normalized paths, and reject persistent
children outside that root. The worker root remains an absolute, isolated,
ephemeral path outside the persistent tree.

The backend Dockerfile will copy `backend/packages/` before the first uv
workspace sync. Both image targets will create the same fixed-UID non-root
user, private state directories with owner-only modes, and a one-process
FastAPI command. Compose will mount a named volume at the configured state
root and pass explicit paths to the backend without publishing internal engine
ports.

Static contract tests will catch install ordering, worker-count, user, and
Compose-volume regressions quickly. A separate Docker runtime script will
build the production target, import `txt2crs`, assert the non-root UID, and
write then reopen a marker through a temporary named volume.

### Design Patterns

- Validated configuration boundary: fail startup before an unsafe filesystem
  layout reaches package factories.
- One application-owned state root: keep SQLite, artifacts, and Codex
  credentials private and portable as one deployment unit.
- Layered verification: use fast static and Pydantic tests for development,
  then a real image smoke for host/container parity.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/tests/core/test_txt2crs_settings.py` | Failing-first path default, override, and confinement tests | ~150 |
| `backend/tests/scripts/test_container_contract.py` | Dockerfile and Compose topology regression tests | ~180 |
| `frontend/src/lib/branding.ts` | One typed txt2crs product-name and page-title helper | ~25 |
| `frontend/src/lib/branding.test.ts` | Unit coverage for public page titles | ~45 |
| `scripts/verify-production-baseline.sh` | Real production image import, user, and volume-reopen smoke | ~120 |
| `.spec_system/specs/phase00-session01-baseline-container-and-state/implementation-notes.md` | Task evidence, decisions, and verification results | ~120 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/Dockerfile` | Copy workspace packages before sync; create private paths; run both targets as one non-root process | ~35 |
| `backend/app/core/config.py` | Add typed txt2crs path settings and confinement validation | ~110 |
| `.env.example` | Replace donor defaults and document container engine paths | ~25 |
| `backend/.env.example` | Replace donor defaults and document local engine paths | ~20 |
| `docker-compose.yml` | Pass engine paths and mount the named private state volume | ~25 |
| `docker-compose.override.yml` | Use txt2crs tracing default and preserve the non-root one-process dev command | ~5 |
| `scripts/validate-changes.sh` | Run the deterministic baseline regression subset | ~15 |
| `frontend/index.html` | Use txt2crs document identity | ~3 |
| `frontend/src/components/Common/Logo.tsx` | Use truthful txt2crs accessible naming while retaining temporary assets | ~5 |
| `frontend/src/components/Common/Footer.tsx` | Replace donor-visible footer product naming | ~5 |
| `frontend/src/routes/login.tsx` | Build the login title from shared branding | ~3 |
| `frontend/src/routes/signup.tsx` | Build the signup title from shared branding | ~3 |
| `frontend/src/routes/recover-password.tsx` | Build the recovery title from shared branding | ~3 |
| `frontend/src/routes/reset-password.tsx` | Build the reset title from shared branding | ~3 |
| `frontend/src/routes/_layout/index.tsx` | Build the dashboard title from shared branding | ~3 |
| `frontend/src/routes/_layout/items.tsx` | Build the temporary items title from shared branding | ~3 |
| `frontend/src/routes/_layout/settings.tsx` | Build the settings title from shared branding | ~3 |
| `frontend/src/routes/_layout/admin.tsx` | Build the admin title from shared branding | ~3 |
| `frontend/src/routes/_layout/forbidden.tsx` | Build the authorization title from shared branding | ~3 |

---

## 7. Success Criteria

### Functional Requirements

- [x] Production and development image targets install and import `txt2crs`.
- [x] Both image targets declare one non-root FastAPI process.
- [x] Default persistent paths resolve below `/var/lib/txt2crs` and unsafe
  overrides fail settings validation.
- [x] Compose mounts one named state volume independently from PostgreSQL.
- [x] A marker written as the runtime user remains readable from a replacement
  container using the same temporary volume.
- [x] Existing login, signup, and item smoke scenarios remain functional.

### Testing Requirements

- [x] Failing settings and container contract tests are written before
  implementation changes and pass afterward.
- [x] Frontend branding unit coverage passes.
- [x] Engine, backend, frontend, Compose, and production image verification
  scenarios complete.

### Non-Functional Requirements

- [x] State directories are owner-only and the runtime UID is not zero.
- [x] No Codex or Tavily credential is required for build, import, config, or
  deterministic tests.
- [x] The internal research MCP port is not published by Compose.

### Quality Gates

- [x] All new session-authored files are ASCII-encoded.
- [x] Unix LF line endings are preserved.
- [x] Code follows project conventions and contains intern-friendly comments
  for non-obvious deployment and path security logic.
- [x] User-facing metadata contains product-facing copy only.

---

## 8. Implementation Notes

### Working Assumptions

- This is a cross-cutting session with `Package: null`: the backend shell owns
  the primary Docker, settings, and Compose deliverables; the engine is a
  secondary import contract and the frontend receives only narrow product-name
  cleanup. Repository layout and the Phase 00 stub support this boundary.
- Initial typed engine settings mean the five filesystem paths required to
  establish the private state boundary. The remaining model, research, budget,
  admission, and feature settings stay with later composition work because
  they depend on Phase 01 public factories.

### Conflict Resolutions

- The adopted plan calls the imported baseline partially complete, while
  spec-system state begins Phase 00 at zero completed sessions. Existing shell
  code is treated as prerequisite donor code, not a completed structured
  session; all remaining Phase 00 exit criteria stay in this checklist.

### Key Considerations

- The Docker build context is `backend/`, so `COPY ./packages /app/packages`
  is the workspace-aware source path.
- The Compose development override currently replaces the image command; it
  must remain a one-process reload command after the base image changes.
- Existing donor-item behavior remains intentionally reachable until jobs
  acceptance coverage is present.

### Potential Challenges

- A fresh Docker named volume may receive root ownership: seed the mount-point
  ownership and mode in the image, then prove actual writes as `appuser`.
- Path overrides can use `..` or symlinks to escape lexical checks: normalize
  paths before enforcing ancestry and reject existing symlink endpoints.
- Full backend smoke tests need PostgreSQL: keep deterministic contract tests
  separate and record any environment-specific runtime failure precisely.

### Behavioral Quality Focus

Checklist active: Yes
Top behavioral risks for this session:

- The application succeeds on the host but the production image omits the
  workspace engine.
- Multiple backend processes race over one SQLite store and one serial worker.
- Misconfigured paths place credentials or artifacts outside the private
  persistent root.

---

## 9. Testing Strategy

### Unit Tests

- Instantiate `Settings` with defaults and safe custom roots, then reject
  relative, escaping, overlapping, and symlinked paths.
- Inspect Dockerfile stages and rendered Compose text for workspace copy
  order, one-process commands, non-root users, explicit path variables, and
  one state volume.
- Verify the frontend page-title helper always includes `txt2crs`.

### Integration Tests

- Run the existing backend login, signup/user, and item route tests against
  the Compose PostgreSQL service.
- Run the engine deterministic suite to ensure packaging changes do not alter
  engine behavior.

### Runtime Verification

- Build the production target, import `txt2crs`, assert a non-zero UID, create
  a private marker through a temporary named volume, and reopen it in a second
  container.
- Render `docker compose config --quiet` with local environment values and
  confirm no internal research port is published.

### Edge Cases

- A custom state root with omitted child paths derives all persistent children
  from the custom root.
- Relative paths, normalized parent escapes, existing symlink endpoints, and
  a worker root inside the persistent tree fail closed.
- Re-running the production smoke cleans its temporary container and volume
  even after a failed assertion.

---

## 10. Dependencies

### Other Sessions

- Depends on: none
- Depended by: all Phase 01 through Phase 05 sessions

---

## Next Steps

Run the `implement` workflow step to begin implementation.
