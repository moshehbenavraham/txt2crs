# Implementation Notes

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Package**: backend/packages/txt2crs
**Started**: 2026-07-19
**Last Updated**: 2026-07-19

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 24 / 24 |
| Estimated Remaining | Code review and validation |
| Blockers | 0 |

---

## Planning Decisions

- The facade delegates to existing package services and never reproduces
  generation, persistence, validation, projection, or rendering behavior.
- One executor handle binds the exact stored owner/job request to fresh
  budget/cancellation state; provider composition remains lazy inside its
  pipeline context.
- Real and deterministic factories share one public protocol. Deterministic
  composition swaps only model/research providers while retaining production
  persistence, preparation, pipeline, rendering, artifact, and purge behavior.
- Owner purge is artifact-first and SQLite-second. It cannot provide
  cross-store atomicity, so it provides explicit no-false-success and
  idempotent retry semantics.
- Account erasure removes active and terminal engine jobs alike; application
  PostgreSQL deletion remains a later shell coordination step.

## Environment Baseline

- Base commit:
  `2e2c022265d802e127893fb9d328a4e0ba60211e`
- Base release/tag: `0.4.0` / `v0.4.0`
- Session 04 validation: 402 passed, 1 explicit live skip; Ruff/mypy/build and
  repository engine validation passed.

## Next Task

Run formal `creview`, repair any findings, then validate the session against
its deliverables and success criteria.

## Tests-First Evidence

- Baseline: analyzer/prerequisites passed at clean release commit
  `2e2c022265d802e127893fb9d328a4e0ba60211e`; 51 focused predecessor tests,
  Ruff, and strict mypy passed.
- Initial red state: the four new facade, owner lifecycle, factory, and
  deterministic integration modules produced four collection errors because
  the application contracts did not exist.
- Factory construction cleanup was also exercised red-first: synthetic
  artifact-store and authentication construction failures initially leaked
  the already-created store/client resources before `ExitStack` ownership was
  implemented.
- The top-level lazy package entrypoint test initially failed with
  `AttributeError` before `txt2crs.__getattr__` was added.

## Implementation Results

- Added strict immutable real/deterministic configuration, one public
  `ApplicationFactory` protocol, the `Txt2CrsApplication` facade, and a
  one-shot owner/job-bound `ApplicationExecutor`.
- Real composition owns production SQLite/filesystem persistence, all enabled
  ingestion adapters, reviewed Tavily research, managed loopback MCP, exact
  GPT-5.6 Codex policy, deterministic rendering, readiness, and dedicated
  system authentication. Provider resources remain lazy until execution or an
  explicit readiness probe.
- Deterministic composition swaps only provider behavior. It retains the
  production store, preparation, pipeline, renderer, artifact delivery,
  recovery, and purge paths, with fresh fake turns, budget, and cancellation
  for every executor.
- Owner purge validates a context-free identifier, serializes cross-store
  coordination, removes the confined hashed artifact tree first, and deletes
  SQLite parent jobs under `BEGIN IMMEDIATE` second. Foreign-key cascades
  remove requests, admissions, checkpoints, and delivery rows; every partial
  failure remains explicit and retryable.
- Factory construction and facade shutdown attempt all owned cleanup without
  leaking private paths, secrets, or internal exception context.
- Replaced manual package assembly documentation with supported real and
  deterministic facade/factory guidance and added lazy top-level discovery.

## Verification

- Focused Session 05 matrix after formal review: 79 passed.
- Full credential-free package suite: 444 passed, 1 live GPT-5.6/Tavily test
  explicitly skipped behind `TXT2CRS_RUN_LIVE_CODEX=1`.
- Repeated artifact descriptor race regression: 20 consecutive passes after
  making the test mutation size-observable on coarse temporary filesystems.
- Ruff format/lint: pass.
- Strict mypy: pass across 136 source files.
- Build: `txt2crs-0.5.0.tar.gz` and
  `txt2crs-0.5.0-py3-none-any.whl` built successfully in the release rerun.
- Distribution inspection: all five application modules ship in wheel and
  sdist; updated README content is present in sdist and wheel metadata.
- Repository validation: `bash scripts/validate-changes.sh engine --json`
  passed engine lint, typecheck, and tests.
- Audit: all changed/untracked session files are ASCII with LF endings;
  `git diff --check` and secret/fallback/sink scans passed.

## Code Review

- Result: `RESOLVED`.
- Reviewed every changed and initially untracked file since base commit
  `2e2c022265d802e127893fb9d328a4e0ba60211e`.
- Repaired 2 High, 4 Medium, and 3 Low findings with red-first regressions:
  active-executor purge recreation, SQLite commit/delete-count integrity,
  facade close races, executor retention, deterministic JSON bypass,
  private-path/MCP configuration, erased return types, invalid purge counts,
  and one coarse-filesystem test race.
- Final evidence is 444 passed with one explicit live-provider skip, 79 focused
  passes, clean Ruff/mypy, inspected distributions, and a green repository
  engine gate.

## Validation

- Result: `PASS`.
- Verified 24/24 tasks, 18/18 applicable specified deliverables plus the
  supporting artifact-reader change, and 23/23 success criteria.
- Security/GDPR validation confirms numeric-loopback-only provider exposure,
  secret masking, parameterized/atomic deletion, confined hashed paths,
  active-owner erasure, no new PII/log path, and explicit separation from the
  future shell's PostgreSQL account deletion.
- Analyzer, prerequisites, lock, full/focused tests, Ruff, strict mypy,
  distributions, repository engine validation, ASCII/LF, and final diff gates
  all pass with no blocker.

## Release Preparation

- Selected `0.5.0` under project SemVer because Session 05 adds the first
  supported application facade/factory and owner-lifecycle feature set.
- Synchronized root `VERSION`, package metadata, `backend/uv.lock`,
  `docs/VERSIONING.md`, and `docs/CHANGELOG.md`.
- Revised the master plan's stale fixed `v0.4.0` final-submission target:
  released versions are immutable, so the eventual submission gate now
  selects and tags the then-current exact SemVer version.
