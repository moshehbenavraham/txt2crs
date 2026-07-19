# PRD Phase 01: Engine Application Boundary

**Status**: In Progress
**Sessions**: 5
**Estimated Duration**: 2-4 days

**Progress**: 2/5 sessions (40%)

---

## Overview

Expose every durable, owner-safe, policy-enforced, and lifecycle-managed
operation that the FastAPI shell needs through documented `txt2crs` package
contracts. This phase keeps generation, research, validation, persistence,
recovery, and artifact behavior inside the reusable engine while closing the
gaps that currently prevent application composition.

---

## Progress Tracker

| Session | Name | Status | Est. Tasks | Validated |
|---------|------|--------|------------|-----------|
| 01 | Durable Requests and Recovery | Complete | ~18-24 | 2026-07-19 |
| 02 | Safe Queries and Artifact Access | Complete | 22 | 2026-07-19 |
| 03 | Input Preferences and Policy Gate | Not Started | ~20-25 | - |
| 04 | Managed Runtime and Model Policy | Not Started | ~18-24 | - |
| 05 | Public Facade and Owner Lifecycle | Not Started | ~16-22 | - |

---

## Completed Sessions

- Session 01: Durable Requests and Recovery - completed 2026-07-19
- Session 02: Safe Queries and Artifact Access - completed 2026-07-19

---

## Upcoming Sessions

- Session 03: Input Preferences and Policy Gate
- Session 04: Managed Runtime and Model Policy
- Session 05: Public Facade and Owner Lifecycle

---

## Objectives

1. Persist and recover the complete immutable generation request and execution
   profile before any application acknowledgement.
2. Expose bounded public job, artifact, policy, and owner-lifecycle operations
   without leaking engine internals or filesystem paths.
3. Make routing, preference resolution, policy enforcement, managed research,
   notification semantics, and GPT-5.6 selection deterministic and testable.
4. Publish one documented application facade plus real and deterministic
   factories for the shell.

---

## Prerequisites

- Phase 00 completed and validated.
- The engine's existing 223-test deterministic baseline remains green.
- The shell/package boundary in `docs/TXT2CRS_FOLDER_ARCHITECTURE.md` remains
  authoritative.

---

## Planning Assumptions And Resolutions

### Working Assumptions

- The package remains independently testable from the FastAPI shell: the
  master PRD, adopted architecture, and Phase 00 considerations all establish
  this boundary, so every Phase 01 deliverable belongs under
  `backend/packages/txt2crs`.
- Phase-local session IDs start at `phase01-session01` even though the source
  implementation plan labels the suggested work packages S02 and S03 in a
  global sequence. Apex Spec state and directory conventions use phase-local
  numbering, so this naming change is safe and does not change scope.

### Conflict Resolutions

- The master PRD and implementation plan suggested two Phase 01 sessions, but
  those two work packages combine fourteen substantial engine gaps. The Apex
  Spec hard limit requires one objective, 12-25 tasks, and 2-4 hours per
  session. Five dependency-ordered sessions preserve all required work while
  giving every gap a bounded implementation home. The master PRD session
  count is updated from two to five in this phasebuild run.
- Older master-PRD prose said Phase 00 was still in progress, while state,
  validation, and phase-transition artifacts prove it complete. The validated
  artifacts are authoritative, and the stale prose is corrected in this run.

---

## Technical Considerations

### Architecture

The engine SQLite store remains the single source of truth for generation
jobs. Public package projections must be allowlists rather than serialized
internal records. Artifact access remains owner-scoped and path-free. The
shell may translate typed settings and errors, but it may not import private
engine modules or reconstruct provider and executor graphs.

The preparation stage must finish bounded ingestion and post-ingestion policy
before Tavily, the research MCP server, or Codex starts. Recovery reuses the
stored request, execution profile, prepared document, and accepted
checkpoints rather than applying current defaults or fetching input again.

### Technologies

- Python 3.14, Pydantic v2, and strict immutable package contracts
- Tenant-scoped SQLite migrations and transactional repositories
- Context-managed filesystem artifact streaming with integrity verification
- Official Codex SDK, GPT-5.6 discovery, and loopback FastMCP lifecycle
- pytest, mypy strict mode, Ruff, uv build, and credential-gated live tests

### Risks

- Request-schema drift could make accepted work unrecoverable: persist schema
  and contract versions, canonicalize every generation-affecting field, and
  fail closed on incompatible profiles.
- Public projections or artifacts could leak private content: use explicit
  allowlists, owner-scoped queries, same-response missing-owner behavior, and
  one validated file descriptor without exposing paths.
- Binary or fetched content could reach providers before policy review:
  checkpoint a provider-free preparation stage and test that all provider
  fakes remain untouched on rejection.
- Runtime resources could leak ports or credentials: use one managed lifecycle
  with bounded readiness, ordered close, and success/failure/cancellation
  cleanup tests.
- Provider availability may not permit the live GPT-5.6 gate: deterministic
  tests must still enforce discovery and no-fallback behavior, while the
  credential-gated live test remains an explicit release requirement.

### Relevant Considerations

- [P00-backend+backend/packages/txt2crs] **One process is mandatory**:
  discovery and recovery APIs must preserve the serial-worker topology.
- [P00-backend+backend/packages/txt2crs] **Private state needs lifecycle
  coverage**: request, checkpoint, delivery, artifact, and owner purge
  operations must remain confined to the owner-only state boundary.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  every operation needed by later routes must be public package behavior.
- [P00] **Layer static and runtime contracts**: pair schema and protocol tests
  with SQLite restart, artifact integrity, listener cleanup, and live-gated
  model checks.
- [P00-backend/packages/txt2crs] **Run engine tools from its package root**:
  Phase 01 uses the engine's independent Ruff, mypy, pytest, and build
  configuration.

---

## Success Criteria

Phase complete when:

- [ ] All 5 sessions completed.
- [ ] A strict versioned request and immutable execution profile are committed
  atomically with idempotency and recovered without reinterpretation.
- [ ] Runnable jobs are discovered deterministically and public job snapshots
  expose only bounded allowlisted state.
- [ ] Owner-scoped manifest and artifact reads verify confinement, size, and
  integrity without returning filesystem paths.
- [ ] URL routing, preference resolution, course-shape validation, and
  two-stage policy behavior are deterministic and checkpointed.
- [ ] No research or Codex work occurs before post-ingestion policy acceptance.
- [ ] Managed research MCP and Codex resources close without leaked listeners
  on success, failure, cancellation, or shutdown.
- [ ] Notification-disabled completion, idempotent owner purge, GPT-5.6
  no-fallback selection, and fresh per-job budgets are proven.
- [ ] The complete shell-needed lifecycle is reachable through documented
  public package methods and real/deterministic factories.
- [ ] Engine Ruff, mypy, pytest, build, and explicit live-gated compatibility
  checks pass at the phase exit gate.

---

## Dependencies

### Depends On

- Phase 00: Application Baseline

### Enables

- Phase 02: Composition and Readiness
- Phase 03: Durable Jobs API
