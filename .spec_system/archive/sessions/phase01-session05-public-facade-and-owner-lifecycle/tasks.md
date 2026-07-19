# Session Tasks

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Package**: `backend/packages/txt2crs`
**Total Tasks**: 24
**Status**: Ready for Review

---

## Preparation And Tests First (6 tasks)

- [x] T001 [S0105] Verify the clean Session 04 release baseline, analyzer,
  package prereqs, public import/build contract, and exact existing
  store/service/executor/provider boundaries.
- [x] T002 [S0105] Add failing SQLite, filesystem, in-memory, active-owner,
  already-purged, partial-failure, and retry owner-lifecycle tests.
- [x] T003 [S0105] Add failing facade tests for submit/recover/query/artifacts,
  readiness/auth, runnable discovery, executor ownership/one-shot close,
  application close, and safe errors.
- [x] T004 [S0105] Add failing strict real/deterministic configuration and
  shared application-factory protocol tests.
- [x] T005 [S0105] Add a failing deterministic integration test that uses only
  public imports to submit, discover, execute, read 16 artifacts, recover,
  purge, and close.
- [x] T006 [S0105] Add failing real-composition contract tests proving complete
  adapter/provider composition, lazy provider startup, exact GPT-5.6, fresh
  graph state, and reverse cleanup.

---

## Core Implementation (13 tasks)

- [x] T007 [S0105] Add strict owner-purge result/error/protocol contracts and
  context-free owner validation.
- [x] T008 [S0105] Implement atomic SQLite owner purge through parent jobs and
  verify every foreign-key cascade plus active-row deletion.
- [x] T009 [S0105] Implement idempotent confined owner purge for filesystem and
  in-memory artifact stores.
- [x] T010 [S0105] Implement artifact-first owner-purge coordination with
  partial-failure propagation and retry semantics.
- [x] T011 [S0105] Add public facade dependency protocols, closed-state error,
  and the owner/job-bound executor handle.
- [x] T012 [S0105] Implement facade delegation for submit, recover, public
  query, artifact access, readiness/auth, runnable discovery, executor
  creation, purge, and close.
- [x] T013 [S0105] Implement strict immutable real and deterministic
  application/scenario configuration with safe path/secret validation.
- [x] T014 [S0105] Implement deterministic application and job-graph factories
  over production persistence, preparation, pipeline, rendering, artifacts,
  and purge.
- [x] T015 [S0105] Implement package-owned real ingestion, URL/YouTube,
  policy, filesystem, store, and authentication composition.
- [x] T016 [S0105] Implement real Tavily/research-tool/coordinator/managed-MCP/
  Codex composition with only job-scoped HTTP/temp/provider resources.
- [x] T017 [S0105] Implement real and deterministic durable pipeline/executor
  factories using exact stored profiles and fresh resource identity.
- [x] T018 [S0105] Implement finite real readiness probing and idempotent
  application/auth/store close without provider leakage.
- [x] T019 [S0105] Publish supported application exports, clean-process import
  behavior, canonical test fixtures, and README facade/factory guidance.

---

## Testing And Completion (5 tasks)

- [x] T020 [S0105] Run and repair all focused owner-lifecycle, facade, factory,
  deterministic lifecycle, store, artifact, executor, and public-import tests.
- [x] T021 [S0105] Run the complete credential-free engine suite and leave the
  real GPT-5.6/Tavily test explicitly gated.
- [x] T022 [S0105] Run Ruff format/lint and strict mypy from the engine package
  root and repair all findings.
- [x] T023 [S0105] Build/inspect wheel and sdist, run repository engine
  validation, and verify public documentation/import members.
- [x] T024 [S0105] Audit every session file for ASCII/LF, strict public
  boundaries, no premature provider work, fresh graphs, confined retry-safe
  purge, safe errors/secrets, and prepare `creview`.

---

## Completion Checklist

- [x] All tasks marked `[x]`
- [x] All tests and checks passing
- [x] All files ASCII-encoded with LF line endings
- [x] `implementation-notes.md` updated
- [x] Ready for `creview`

## Next Steps

Run `implement` for `phase01-session05-public-facade-and-owner-lifecycle`.
