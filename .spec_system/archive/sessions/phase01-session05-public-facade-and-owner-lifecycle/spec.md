# Session Specification

**Session ID**: `phase01-session05-public-facade-and-owner-lifecycle`
**Phase**: 01 - Engine Application Boundary
**Status**: Planned
**Created**: 2026-07-19
**Base Commit**: 2e2c022265d802e127893fb9d328a4e0ba60211e
**Package**: backend/packages/txt2crs
**Package Stack**: Python 3.14, Pydantic v2, SQLite

---

## 1. Session Overview

This session publishes the engine composition root that the FastAPI shell can
use without importing private generation, research, persistence, or rendering
modules. One `Txt2CrsApplication` facade will delegate submission, recovery,
public query, artifact access, runnable discovery, safe readiness and
authentication state, executor creation, owner purge, and application close.

The facade does not become a second implementation of engine behavior.
`JobService`, `SqliteJobStore`, the artifact store, authentication service,
and `GenerationJobExecutor` remain authoritative. The new application layer
only owns typed composition, closed-state enforcement, and job-scoped
resource handles.

Real composition will build every existing package implementation behind a
typed `RealApplicationConfig`: SQLite, private filesystem artifacts, bounded
ingestion adapters, two-stage policy, reviewed Tavily research, managed
loopback MCP, exact GPT-5.6 Codex runtime, generation pipeline, deterministic
renderer, and dedicated system authentication. Provider resources remain lazy
and open only inside one executor run after durable preparation.

Deterministic composition will satisfy the same public factory and facade
contracts with scripted model/research values, local input, SQLite, and private
filesystem artifacts. It must execute a complete course lifecycle without
FastAPI, PostgreSQL, network access, credentials, or private-module imports in
its integration test.

Finally, one owner-lifecycle service will purge all engine-owned state. It
removes the owner artifact tree before deleting the SQLite owner rows in one
transaction. An artifact failure therefore leaves database recovery identity
intact. A later database failure is still retryable because artifact purge is
idempotent. No partial path returns a success result.

---

## 2. Objective

1. Publish one documented, framework-independent application facade with real
   and deterministic factories and a retry-safe owner-wide purge.

---

## 3. Prerequisites

### Required Sessions

- [x] Session 01 - exact durable requests, recovery, and runnable discovery.
- [x] Session 02 - public snapshots and owner-scoped artifact reads.
- [x] Session 03 - provider-free preparation and preference/policy gates.
- [x] Session 04 - managed provider lifecycle, exact GPT-5.6 policy, fresh job
  resources, and disabled notification state.

### Environment Requirements

- Package commands run from `backend/packages/txt2crs`.
- Deterministic tests are credential-free and external-network-free.
- The live GPT-5.6/Tavily test remains behind `TXT2CRS_RUN_LIVE_CODEX=1`.
- No application-shell or frontend file is changed by this session.

---

## 4. Scope

### In Scope

- A public `txt2crs.application` package.
- A `Txt2CrsApplication` facade with:
  - submit and exact owner-scoped recovery;
  - public job snapshot, artifact manifest, and artifact stream;
  - safe runtime readiness and system-authentication operations;
  - deterministic runnable-job discovery;
  - fresh owner/job-bound executor-handle creation;
  - idempotent owner-wide purge; and
  - idempotent application close plus closed-state rejection.
- A public executor handle that owns one fresh `RunBudget` and
  `CancellationToken`, runs exactly its bound owner/job, supports cancellation,
  and cannot execute after close.
- Strict immutable real and deterministic application configurations.
- One shared public application-factory protocol.
- A real factory that owns concrete ingestion, policy, store, filesystem,
  Tavily, managed MCP, Codex, pipeline, renderer, authentication, and
  readiness composition.
- A deterministic factory that owns local scripted runtime/research
  composition and produces the same facade/executor contracts.
- An idempotent owner-purge result and coordinator.
- SQLite owner deletion through the parent `jobs` rows with foreign-key
  cascades for requests, admissions, checkpoints, and delivery rows.
- Filesystem and in-memory owner-artifact purge operations.
- Tests for active jobs, completed jobs, already-purged owners, artifact
  failure, database failure, retry, close, wrong-owner access, and fresh graphs.
- Public package exports and package README application-assembly guidance.

### Out Of Scope

- FastAPI settings conversion, routes, dependencies, lifespan, worker threads,
  HTTP errors, and PostgreSQL deletion coordination.
- Frontend or generated client changes.
- Hosted MCP, multiple worker processes, SMTP/outbox delivery, or UI model
  selection.
- Individual-job deletion and time-based artifact retention changes.
- Credentialed live execution in the default deterministic suite.

---

## 5. Technical Approach

### Public Facade

`Txt2CrsApplication` receives narrow services rather than paths or provider
credentials. Every method first checks one locked open/closed state and then
delegates to the existing package authority. Artifact streams remain
context-managed; the facade never reads their bytes eagerly.

The facade exposes system authentication by delegating to a small protocol
matching `DedicatedSystemAuthenticator`. Runtime readiness uses an injected
safe inspector. The real inspector opens the same reviewed provider graph as
generation for one finite probe and closes it before returning. The
deterministic inspector returns a strict safe fixture.

`create_executor(job_id, user_id)` first performs an owner-authorized resume,
derives fresh runtime resources from the exact stored execution profile, and
asks the configured executor factory for a handle. The handle binds the owner,
job, executor, and cancellation token. It rejects a second execution or use
after close; close requests cancellation and is idempotent.

### Real Factory

`RealApplicationConfig` contains only strict values: private state paths,
admission/artifact/input limits, reviewed model identity, retry and research
policy values, Tavily secret, Codex home, and finite lifecycle timeouts. Paths
must be absolute, distinct where required, and free of symlink ambiguity.

The factory constructs long-lived SQLite, filesystem artifact, content-policy,
renderer, and authentication services once. It constructs the real ingestion
service from the concrete PDF/DOCX/PPTX/OCR/transcription/URL/YouTube adapters.
Local prompt/text work requires no remote dependency.

Each executor handle receives new budget, cancellation, retry, guardrail,
Tavily/research, MCP, Codex, coordinator, and pipeline objects. HTTP, temporary
worker, MCP, and Codex resources use the managed Session 04 context. The
pipeline context verifies the request profile/model identity before opening
provider resources.

### Deterministic Factory

`DeterministicApplicationConfig` holds private state paths, admission limits,
an exact execution profile, strict scripted turn outputs, and strict scripted
research results. Each executor graph copies that scenario into a fresh
`FakeRuntime`, deterministic research provider, budget, cancellation, retry,
pipeline, and renderer. No global mutable fake is shared across jobs.

The deterministic factory uses the production SQLite store, filesystem
artifact store, `JobService`, preparation, pipeline, renderer, facade, and
purge coordinator. Its end-to-end test therefore proves the public boundary
without weakening persistence or artifact behavior.

### Owner Purge

`OwnerPurgeCoordinator.purge_owner`:

1. validates the owner identifier without retaining raw validation context;
2. calls `artifact_store.purge_owner`, which is idempotent and confines the
   hashed owner path;
3. calls `SqliteJobStore.purge_owner` under `BEGIN IMMEDIATE`;
4. relies on `ON DELETE CASCADE` for request, admission, checkpoint, and
   delivery rows; and
5. returns a strict `OwnerPurgeResult` only after both stores succeed.

Artifact-first ordering prevents a failed filesystem deletion from erasing
the durable list of jobs. If SQLite fails after artifact success, the caller
receives a typed failure; retry sees an empty artifact tree and completes the
database deletion. Existing/active jobs are removed alike because account
erasure must not retain an executing owner's data.

---

## 6. Deliverables

### Files To Create

| File | Purpose |
|------|---------|
| `src/txt2crs/application/__init__.py` | Supported public application exports |
| `src/txt2crs/application/config.py` | Strict real/deterministic configuration contracts |
| `src/txt2crs/application/facade.py` | Facade and one-shot executor handle |
| `src/txt2crs/application/factories.py` | Shared protocol plus real/deterministic composition |
| `src/txt2crs/application/owner_lifecycle.py` | Typed retry-safe owner purge |
| `tests/unit/test_owner_lifecycle.py` | Store/artifact/partial-failure purge coverage |
| `tests/unit/test_application_facade.py` | Delegation, ownership, executor, close coverage |
| `tests/contract/test_application_factories.py` | Config/protocol/fresh-graph/real-composition coverage |
| `tests/integration/test_application_lifecycle.py` | Complete deterministic public-boundary lifecycle |

### Files To Modify

| File | Changes |
|------|---------|
| `src/txt2crs/jobs/store.py` | Atomic owner row purge and owner validation |
| `src/txt2crs/jobs/service.py` | Artifact purge protocol/implementations and service delegation |
| `src/txt2crs/jobs/artifact_store.py` | Confined idempotent filesystem owner purge |
| `src/txt2crs/jobs/__init__.py` | Export only newly supported lifecycle contracts if needed |
| `src/txt2crs/ingestion/__init__.py` | Export concrete adapters needed by public factory boundaries |
| `src/txt2crs/security/__init__.py` | Export safe resolver/policy factory dependencies if needed |
| `src/txt2crs/__init__.py` | Expose the documented facade/factory entrypoints without eager optional imports |
| `tests/factories.py` | Add canonical deterministic scenario/application config fixtures |
| `tests/integration/test_sqlite_job_store.py` | Real cascade and active-owner purge coverage |
| `tests/unit/test_filesystem_artifact_store.py` | Owner-tree purge confinement/idempotency coverage |
| `tests/unit/test_public_package_exports.py` | Clean-process public application import coverage |
| `README_txt2crs.md` | Replace manual assembly prose with facade/factory usage |

---

## 7. Success Criteria

### Functional Requirements

- [ ] Every shell-needed operation is reachable through documented public
  `txt2crs.application` methods without private imports.
- [ ] Submission, recovery, runnable discovery, public snapshot, manifest, and
  single-artifact stream delegate to existing owner-safe services.
- [ ] System authentication and runtime readiness expose only existing strict
  browser-safe contracts.
- [ ] Every executor handle is bound to one owner/job, owns fresh budget and
  cancellation state, and is one-shot/closeable.
- [ ] The real factory composes all enabled ingestion, policy, store,
  research, managed MCP, exact GPT-5.6 Codex, pipeline, renderer, and
  authentication implementations.
- [ ] The deterministic factory shares the public protocol and builds a fresh
  credential-free graph per job.
- [ ] One deterministic lifecycle submits, discovers, executes, queries, reads
  exactly 16 artifacts, recovers completion, and closes through only public
  package imports.
- [ ] Owner purge deletes artifacts and all owner jobs, requests, admissions,
  checkpoints, and deliveries, including active jobs.
- [ ] Partial purge never returns success; artifact/database failure remains
  safe to retry, and already-purged owners succeed idempotently.
- [ ] Application/executor close is idempotent and every later mutation or
  execution fails with one context-free closed error.

### Testing Requirements

- [ ] Facade, purge, factory, and end-to-end tests are written and observed
  failing before production implementation.
- [ ] Real SQLite/filesystem tests prove owner cascade, confinement,
  active-owner deletion, partial failure, retry, and already-purged behavior.
- [ ] Recording factories prove one fresh budget/cancellation/provider graph
  per executor and zero provider construction during submission/query/purge.
- [ ] Deterministic integration uses no FastAPI, PostgreSQL, network,
  credential, or private-module import.
- [ ] The complete credential-free engine suite passes with the live
  GPT-5.6/Tavily compatibility test explicitly gated.
- [ ] Wheel and sdist contain the complete application package and updated
  public documentation.

### Non-Functional Requirements

- [ ] Public contracts and safe errors expose no owner hash, request content,
  SQLite query, filesystem path, provider secret, discovered model, or
  internal component type.
- [ ] Factory configuration is strict/immutable, validates absolute confined
  paths and finite limits, and never serializes a secret value.
- [ ] Purge and close are thread-safe, finite, idempotent, and do not claim
  cross-store atomicity.
- [ ] No shell, application PostgreSQL, frontend, hosted deployment, SMTP, or
  new external provider enters the package session.

### Quality Gates

- [ ] All session-authored files are ASCII with Unix LF endings.
- [ ] Complete types, descriptive names, and intern-oriented comments explain
  facade delegation, graph freshness, provider laziness, purge ordering, and
  partial-failure recovery.
- [ ] Ruff format/lint, strict mypy, pytest, build/archive inspection,
  repository engine validation, code review, and validation pass.

---

## 8. Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Facade duplicates engine logic | Critical | Delegate only; tests compare facade results with authoritative services |
| Factory opens providers before accepted preparation | Critical | Bind provider construction to `DurablePipelineFactory.open` after the stored preparation gate |
| Purge deletes database first and orphans artifacts | High | Artifact-first ordering; no success result until SQLite commits |
| Purge partially deletes artifacts | High | Keep DB state, surface a typed failure, and make owner-tree deletion retryable |
| Executor shares mutable counters/cancellation | High | Build and identity-test fresh resources from the exact stored request |
| Real factory leaks credentials into Codex | Critical | Reuse Session 04 child-environment stripping and managed adapter creation |
| Deterministic factory drifts from production | Medium | Share facade, store, preparation, pipeline, renderer, artifacts, and purge; vary only provider implementations |
| Public imports become cyclic/eager | Medium | Keep a cohesive `application` package and clean-process import/build tests |

---

## 9. References

- `.spec_system/PRD/phase_01/session_05_public_facade_and_owner_lifecycle.md`
- `.spec_system/specs/phase01-session04-managed-runtime-and-model-policy/IMPLEMENTATION_SUMMARY.md`
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` sections 5.9, 5.11,
  6, 7, and Phase 1 work items 12-13
- `backend/packages/txt2crs/README_txt2crs.md`
- `backend/packages/txt2crs/src/txt2crs/jobs/service.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/store.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py`
- `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`
- `backend/packages/txt2crs/src/txt2crs/ai/job_runtime.py`
- `backend/packages/txt2crs/src/txt2crs/research/managed_mcp.py`

---

## 10. Dependencies

### Depends On

- `phase01-session01-durable-requests-and-recovery`
- `phase01-session02-safe-queries-and-artifact-access`
- `phase01-session03-input-preferences-and-policy-gate`
- `phase01-session04-managed-runtime-and-model-policy`

### Enables

- Phase 01 exit validation.
- Phase 02 shell lifespan, readiness, authentication routes, and serial worker.
- Phase 03 thin job/status/artifact route adapters.
- Phase 04 account deletion coordination.
