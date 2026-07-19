# Session Specification

**Session ID**: `phase02-session01-engine-composition-lifecycle`
**Phase**: 02 - Composition and Readiness
**Status**: Not Started
**Created**: 2026-07-19
**Base Commit**: 0c779c910445e636db01a7bca284a72532ef57b6
**Package**: backend
**Package Stack**: Python 3.14, FastAPI, SQLModel, PostgreSQL

---

## 1. Session Overview

This session gives the FastAPI shell one explicit composition boundary for the
public `txt2crs` application facade. It translates finite shell settings into
the package's strict `RealApplicationConfig`, constructs at most one facade
for a configured application lifespan, exposes that lifecycle to later worker
and readiness services, and closes all acquired resources exactly once.

It is the first Phase 02 session because every later supervisor, readiness,
authentication, and setup surface depends on a stable application-owned
facade. Tests will establish configuration, injection, partial-startup, and
shutdown behavior before the composition code is added.

---

## 2. Objectives

1. Add bounded typed settings for the complete P0 execution, admission,
   storage, research, MCP, model, and artifact profile consumed by the engine
   public configuration.
2. Translate one validated `Settings` instance into one immutable
   `RealApplicationConfig` without importing private engine modules.
3. Provide an injectable application lifecycle that creates no facade when
   external research configuration is absent and exactly one facade when
   configured.
4. Integrate the lifecycle with FastAPI startup and shutdown while preserving
   OpenAPI generation, existing routes, and safe structured events.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase01-session05-public-facade-and-owner-lifecycle` - Provides the
  public `RealApplicationConfig`, `RealApplicationFactory`, and
  `Txt2CrsApplication` lifecycle contracts.
- [x] `phase00-session01-baseline-container-and-state` - Provides validated
  private paths and the one-process container topology.

### Required Tools Or Knowledge

- FastAPI lifespan context managers and application state.
- Pydantic Settings v2 validators and immutable package configuration.
- Public imports from `txt2crs.application`.
- pytest monkeypatching and injected recording factories.

### Environment Requirements

- Backend dependencies installed with `uv sync --all-packages`.
- Deterministic tests run without Tavily, network access, or Codex
  credentials.
- Temporary test paths replace `/var/lib/txt2crs` for lifecycle cases.

---

## 4. Scope

### In Scope (MVP)

- An application operator can configure one finite P0 engine profile through
  validated environment settings - shell translation constructs only public
  package contracts.
- The FastAPI process can start without external provider configuration -
  composition records a safe unconfigured state and leaves OpenAPI plus later
  setup routes available.
- A configured FastAPI lifespan owns one engine facade - an injected
  `ApplicationFactory` creates it once and lifecycle cleanup closes it once.
- A developer can test composition without real credentials - factory and
  facade protocols are injected at the shell boundary.
- Application startup and shutdown are observable - events use
  `{domain}.{action}_{state}` and include only coarse configuration state.

### Out Of Scope (Deferred)

- Serial runnable-job discovery and execution - Reason: Session 02 owns the
  worker supervisor.
- Composite readiness probes and caching - Reason: Session 03 owns side-effect
  scheduling and safe snapshots.
- System readiness and device-authentication routes - Reason: Session 04 owns
  strict HTTP contracts and authorization.
- Learner job routes and artifact delivery - Reason: Phase 03 owns the durable
  jobs API.
- PostgreSQL or engine SQLite schema changes - Reason: Composition consumes
  existing persistence contracts without changing stored shape.

---

## 5. Technical Approach

### Architecture

Add `app.services.txt2crs_application` as the only shell module that translates
`Settings` into `ApplicationStorageConfig`, `ApplicationAdmissionConfig`,
`ExecutionProfile`, and `RealApplicationConfig`. It may import documented
public contracts from `txt2crs.application` and `txt2crs.jobs`, but it must not
import engine stores, ingestion, research, provider, pipeline, or renderer
implementations.

The service exposes a small lifecycle object with a nullable facade and a
coarse configured/unconfigured state. A callable factory builder is injected
for tests; the production builder wraps `RealApplicationFactory`. Missing
`TAVILY_API_KEY` returns the unconfigured state before a
`RealApplicationConfig` is constructed. Invalid paths, bounds, topology, or
model values continue to fail settings construction or application startup.

FastAPI receives an async lifespan context manager that starts the lifecycle,
stores only the shell service on `app.state`, yields to existing HTTP
behavior, and closes the service in `finally`. If construction fails after a
facade is acquired, the same owner closes it before re-raising. Cleanup is
idempotent so nested failure handling cannot close a child twice.

### Design Patterns

- **Composition root**: One shell module translates configuration and delegates
  the complete engine graph to the package factory.
- **Dependency inversion**: Tests inject a recording `ApplicationFactory`
  instead of constructing provider resources.
- **Explicit optional capability**: Missing external configuration yields a
  typed unconfigured lifecycle state rather than a fake secret or partial
  private graph.
- **Scoped ownership**: Lifespan `try/finally` and idempotent close make the
  resource owner visible and testable.
- **Strict immutable configuration**: Pydantic validates finite bounds once,
  and the package receives detached public values.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/app/services/txt2crs_application.py` | Public package configuration translation and application-owned facade lifecycle | ~300 |
| `backend/tests/services/__init__.py` | Backend services test package marker | ~1 |
| `backend/tests/services/test_txt2crs_application.py` | Tests-first translation, factory injection, unconfigured, cleanup, and import-boundary coverage | ~450 |
| `backend/tests/test_txt2crs_lifespan.py` | FastAPI startup, shutdown, partial failure, and existing-route regression tests | ~220 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/app/core/config.py` | Add bounded P0 engine, research, model, execution, admission, and retention settings | ~170 |
| `backend/app/main.py` | Register the injectable txt2crs lifespan without changing route or middleware behavior | ~55 |
| `backend/app/services/__init__.py` | Document the shell composition boundary | ~8 |
| `backend/tests/core/test_txt2crs_settings.py` | Cover finite defaults, unsafe overrides, GPT-5.6 policy, and optional external secret behavior | ~180 |
| `backend/.env.example` | Document all operator-configurable composition settings without secrets | ~45 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] The shell constructs a public `RealApplicationConfig` containing the
  exact conservative P0 limits from the implementation plan.
- [ ] The configured FastAPI lifespan creates one facade and makes the owning
  lifecycle available to later services.
- [ ] A missing Tavily secret starts in a safe unconfigured state without
  constructing `RealApplicationFactory` or a provider graph.
- [ ] Normal shutdown and partial startup failure close every acquired facade
  exactly once.
- [ ] Existing health, authentication, and donor item routes retain their
  behavior.

### Testing Requirements

- [ ] Tests are written and observed failing before implementation.
- [ ] Settings unit tests cover defaults, minimum/maximum bounds, invalid
  GPT-5.6 identifiers, inherited environment isolation, and optional secret
  absence.
- [ ] Service tests prove exact translation, public-only imports, factory
  injection, idempotent close, and failure cleanup.
- [ ] Lifespan tests prove configured and unconfigured startup plus cleanup.
- [ ] The complete backend suite passes without network or credentials.

### Non-Functional Requirements

- [ ] No shell module reconstructs generation, research, persistence,
  rendering, or managed-provider internals.
- [ ] Startup and shutdown events follow `{domain}.{action}_{state}` and omit
  secrets, paths, learner content, provider payloads, and exception text.
- [ ] Configuration bounds fail at settings construction, while absent
  external credentials do not prevent OpenAPI generation.
- [ ] The implementation preserves the mandatory one-process topology.

### Quality Gates

- [ ] All files ASCII-encoded.
- [ ] Unix LF line endings.
- [ ] Code follows project conventions and includes intern-friendly comments.
- [ ] Ruff, mypy, ty, focused pytest, full backend pytest, and backend
  validation pass.

---

## 8. Implementation Notes

### Working Assumptions

- A missing `TAVILY_API_KEY` means the real application facade is not composed
  for that lifespan. `RealApplicationConfig` intentionally rejects empty
  secrets, while the system plan explicitly requires OpenAPI and operator
  setup to load without external credentials. Treating absence as a shell
  capability state preserves both contracts without inventing a credential.
- The existing package factory remains the sole owner of its reviewed Tavily
  declaration, ingestion adapters, authenticator, provider graph, stores, and
  renderer. Current public factory code already constructs those resources
  lazily or with scoped cleanup, so the shell only supplies finite public
  configuration.
- The existing path-specific shell fields remain validated even though the
  public application factory receives the common private state root and Codex
  home. The engine derives its SQLite and artifact locations internally; the
  explicit shell child paths remain deployment and recovery invariants.

### Conflict Resolutions

- The phase objective says one facade is owned for the FastAPI lifespan, while
  the deployment requirements allow absent external credentials. The
  configured interpretation creates exactly one facade; the unconfigured
  interpretation creates none and exposes a safe lifecycle state for later
  readiness/setup sessions. This is the only interpretation supported by both
  the strict package config and credential-free startup requirement.

### Key Considerations

- Build the `ExecutionProfile` from named settings in one function so request
  identity never depends on mutable current defaults after submission.
- Do not store `SecretStr` values, paths, exceptions, or serialized package
  configuration in logs or app state.
- The lifecycle service, not route handlers, owns the facade reference and
  close operation.
- Test `Settings` with inherited txt2crs and Tavily variables cleared because
  `_env_file=None` does not isolate process environment.

### Potential Challenges

- **Large finite profile**: Group settings and translation helpers by storage,
  retry, input, run, and admission concepts, with descriptive comments.
- **Global app construction**: Keep the exported `app` contract while moving
  resource acquisition into FastAPI lifespan so imports stay side-effect free.
- **Partial construction failure**: Assign ownership only after factory
  success and close any returned facade inside a guarded `finally`.
- **Test isolation**: Use per-test app instances or injected lifecycle
  factories so global `app.state` cannot leak between tests.

### Relevant Considerations

- [P00-backend+backend/packages/txt2crs] **One process is mandatory**: The
  service composes one process-owned facade and adds no parallel worker.
- [P00-backend] **Readiness still needs engine composition**: This session
  supplies the stable lifecycle state consumed by Sessions 02-04.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  Import tests reject private engine modules from shell composition code.
- [P00-backend] **Fail unsafe paths at settings construction**: Existing
  canonical private path validation remains authoritative.
- [P00-backend] **Do not assume Pydantic ignores process environment**:
  Focused tests clear every environment variable they own.
- [P01-backend/packages/txt2crs] **One context owns provider resources**: The
  shell owns only the facade, while the package retains job-scoped resources.

### Behavioral Quality Focus

Checklist active: Yes
Top behavioral risks for this session:

- Partial startup acquires a facade and then leaks it when a later step fails.
- Missing provider configuration accidentally creates a synthetic credential
  or prevents the shell and OpenAPI from starting.
- Duplicate lifespan or close calls create two application graphs or close
  the same child more than once.

---

## 9. Testing Strategy

### Unit Tests

- Assert every P0 setting default and representative invalid lower/upper
  bounds.
- Assert exact nested public config translation, including GPT-5.6, retry,
  input, run, storage, research timeout, MCP loopback, and admission values.
- Assert missing Tavily configuration does not call the injected factory.
- Assert repeated lifecycle close is harmless and factory/config failures do
  not leave a retained facade.

### Integration Tests

- Start a focused FastAPI test application with an injected recording factory,
  make an existing health request, and prove one create/one close.
- Start without a Tavily secret and prove the application imports, OpenAPI is
  available, existing endpoints respond, and no engine factory is invoked.
- Force a failure after facade creation and prove cleanup precedes the
  propagated startup failure.

### Runtime Verification

- Run the backend with temporary private paths and no external credentials;
  request `/api/v1/openapi.json` and liveness, then stop cleanly.
- Run focused deterministic lifecycle tests with a recording facade instead of
  network or provider resources.

### Edge Cases

- Empty or whitespace-only Tavily values.
- Invalid or non-GPT-5.6 model identifiers.
- Non-loopback MCP host or invalid port and timeout bounds.
- Overlapping, relative, or symlinked state paths.
- Factory raises before returning, facade close raises, and close is called
  more than once.
- Two TestClient lifespans run sequentially without sharing a stale facade.

---

## 10. Dependencies

### Other Sessions

- Depends on: `phase01-session05-public-facade-and-owner-lifecycle`
- Depended by: `phase02-session02-serial-worker-supervisor`,
  `phase02-session03-cached-readiness-and-observability`,
  `phase02-session04-system-readiness-and-auth-api`

---

## Next Steps

Run the `implement` workflow step to begin implementation.
