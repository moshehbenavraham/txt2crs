# Session Specification

**Session ID**: `phase02-session04-system-readiness-and-auth-api`
**Phase**: 02 - Composition and Readiness
**Status**: Validated
**Created**: 2026-07-19
**Base Commit**: 470b2609dc9701c9eae28a5db8cfe30c1f2faef8
**Package**: backend
**Package Stack**: Python 3.14, FastAPI, Pydantic v2, public txt2crs contracts,
and generated TypeScript client

---

## 1. Session Overview

This session publishes the system API over the lifecycle and cache completed
in Sessions 01-03. Any authenticated user can read the coarse cached
readiness projection. Only a current superuser can start or inspect the
dedicated ChatGPT device-code ceremony.

A lifecycle-owned system-authentication coordinator retains the shared
`authentication` runtime lease from challenge creation until the package's
background completion reaches a terminal safe state. Its monitor reads only
the package's in-memory snapshot with `refresh=False`; HTTP status polling
reads only the shell cache and never starts Codex, probes credentials, or
competes with job execution.

The new routes use strict explicit API schemas, registered `ErrorCode`
values, RFC 9457 errors, safe route events, bounded rate limits, and the
generated OpenAPI client.

---

## 2. Objectives

1. Expose cached readiness to authenticated callers without adding any
   synchronous provider or storage side effect.
2. Expose device-code start/status only to active superusers and return only
   the package's validated OpenAI URL, short code, finite state, and safe
   message.
3. Hold one authentication runtime lease for the complete background ceremony
   and release it automatically on authenticated, failed, close, or start
   failure.
4. Map unavailable, busy, closed, and package failures to stable shell errors
   without provider exception context.
5. Regenerate and verify the OpenAPI/TypeScript contract without editing
   generated client files manually.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase02-session01-engine-composition-lifecycle` - owns one real public
  application facade including the package authenticator.
- [x] `phase02-session02-serial-worker-supervisor` - respects the shared
  runtime ownership coordinator during execution.
- [x] `phase02-session03-cached-readiness-and-observability` - supplies the
  immutable readiness cache, public error translation, and finite runtime
  owner.

### Required Tools Or Knowledge

- FastAPI dependencies and route authorization.
- slowapi endpoint limits and RFC 9457 exception handling.
- Pydantic v2 strict response construction.
- Public `txt2crs.application` authentication contracts.
- OpenAPI export and generated TypeScript client workflow.

### Environment Requirements

- Deterministic tests require no Codex login, Tavily key, MCP listener, or
  network access.
- Complete shell tests use the isolated project PostgreSQL container.
- OpenAPI generation runs with absent external credentials and must not start
  a provider runtime.

---

## 4. Scope

### In Scope (MVP)

- Public package export of safe authentication state, snapshot, and safe
  package error types already used by the facade.
- A shell authentication coordinator with immutable cached state, one finite
  monitor thread, shared runtime ownership, idempotent lifecycle, and safe
  event fields.
- Bounded authentication monitor and shutdown settings.
- Strict public system readiness and device-auth response schemas.
- Authenticated `GET /api/v1/system/readiness`.
- Superuser-only `POST /api/v1/system/auth/start`.
- Superuser-only `GET /api/v1/system/auth/status`.
- Distinct readiness and authentication endpoint rate limits.
- FastAPI dependencies over lifespan-owned services.
- Semantic `SYSTEM_AUTH_FAILED` translation.
- OpenAPI export, frontend client regeneration, and route/API documentation.

### Out Of Scope (Deferred)

- Device-auth logout, which remains the documented P1 route.
- Learner job submission, status, cancellation, and artifacts.
- The frontend `/setup` screen, owned by Session 05.
- OAuth tokens, account email/identity, provider payloads, `CODEX_HOME`, paths,
  ports, or private exception text.
- Hosted authentication, identity-provider changes, or remote deployment.

---

## 5. Technical Approach

### Architecture

Add `SystemAuthenticationCoordinator` under `backend/app/services/`. Its
`start()` performs one lifecycle-owned persisted-account refresh under the
shared authentication lease, caches the public package snapshot, and starts
one finite monitor thread. This initial refresh happens before readiness and
the worker are started and never runs during OpenAPI import.

`start_authentication()` returns the existing cached terminal or waiting state
when replay is safe. Otherwise it attempts the shared authentication lease
without blocking. A busy execution/readiness owner produces a stable
`SYSTEM_NOT_READY` error. A successful waiting challenge retains the lease.
The monitor periodically calls only
`get_system_authentication_status(refresh=False)`, updates the immutable
cache, and releases the lease on `authenticated` or `failed`.

`snapshot()` reads only locked cached state. The GET status route therefore
does not touch the facade, provider, credential store, or runtime gate.
Shutdown stops the worker and readiness maintenance before it joins the auth
monitor and releases any retained lease. Later facade cleanup cancels any
still-active package ceremony and closes its app-server.

Add `app/schemas/system.py` as the explicit HTTP projection. Readiness uses
finite enums, reviewed input modes, bounded warnings/actions, and a
timezone-aware check time. Device auth enforces cross-field state validity:
only `waiting_for_user` may contain the exact validated OpenAI HTTPS URL and
bounded short user code; terminal states contain neither.

Add state dependencies in `app/api/deps.py` and a `system` router. The router
uses existing JWT/superuser dependencies, slowapi limits, `AppException`,
semantic `ErrorCode`, and the central public-package translator.

### Design Patterns

- Lifecycle cache: HTTP GET operations read detached state only.
- Lease across asynchronous work: ownership ends when the background
  ceremony, not the POST handler, reaches a terminal state.
- Public contract adapter: route schemas copy only approved package/shell
  fields.
- Replay-safe action: repeated start while waiting or already authenticated
  returns the current safe state without launching a second runtime.
- Fail-closed service dependency: absent or closed lifespan services return
  `SYSTEM_NOT_READY`.
- Generated contract ownership: the script regenerates and formats OpenAPI
  and TypeScript together.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/app/services/txt2crs_authentication.py` | Cached system-auth lifecycle, runtime lease, and finite monitor | ~360 |
| `backend/app/schemas/system.py` | Strict readiness and authentication HTTP projections | ~260 |
| `backend/app/api/routes/system.py` | Authenticated readiness and privileged auth endpoints | ~240 |
| `backend/tests/services/test_txt2crs_authentication.py` | Lifecycle, concurrency, replay, release, cleanup, and privacy tests | ~500 |
| `backend/tests/schemas/test_system_schemas.py` | Strict allowlist and cross-field response tests | ~260 |
| `backend/tests/api/routes/test_system.py` | Authentication, authorization, response, errors, side effects, and rate limits | ~520 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/application/__init__.py` | Export the facade's browser-safe authentication contracts | ~10 |
| `backend/packages/txt2crs/tests/unit/test_public_package_exports.py` | Protect the public authentication export surface | ~20 |
| `backend/app/core/config.py` and `backend/.env.example` | Add finite auth monitor and shutdown settings | ~20 |
| `backend/app/core/constants.py` | Add `SYSTEM_AUTH_FAILED` and HTTP mapping | ~8 |
| `backend/app/core/rate_limit.py` | Add explicit readiness/start/status limits | ~8 |
| `backend/app/core/txt2crs_errors.py` | Translate the public authentication error safely | ~12 |
| `backend/app/api/deps.py` | Resolve lifespan-owned readiness and authentication services | ~70 |
| `backend/app/api/main.py` | Register the system router | ~4 |
| `backend/app/main.py` | Construct/start/expose/close authentication in dependency order | ~100 |
| `backend/app/services/__init__.py` | Export the authentication coordinator | ~10 |
| `backend/tests/core/test_txt2crs_settings.py` | Verify exact finite settings and bounds | ~30 |
| `backend/tests/core/test_txt2crs_errors.py` | Verify semantic auth translation and cleared context | ~20 |
| `backend/tests/test_txt2crs_lifespan.py` | Verify service state and startup/cleanup ordering | ~120 |
| `frontend/openapi.json` and `frontend/src/client/` | Generated and formatted API contract | generated |
| Public engine/backend documentation | Describe route safety, authorization, caching, and CLI recovery | ~80 |

---

## 7. Success Criteria

### Functional Requirements

- [x] Authenticated users receive the exact coarse cached readiness projection
  without triggering a refresh or package call.
- [x] Missing, invalid, or inactive authentication receives existing semantic
  RFC 9457 errors before a system service is accessed.
- [x] Non-superusers receive `AUTH_INSUFFICIENT_PERMISSIONS` for both
  device-auth routes and cannot infer challenge state.
- [x] A superuser can start one device-code attempt and poll a cached safe
  snapshot until it reaches `authenticated` or `failed`.
- [x] Repeated start while waiting or authenticated returns current state and
  never creates another provider runtime.
- [x] Execution or readiness ownership refuses a new auth start with
  `SYSTEM_NOT_READY`; status polling remains side-effect free.
- [x] An active ceremony retains authentication ownership until terminal
  status, start failure, or lifecycle close.
- [x] Unconfigured/closed services fail with generic stable codes and no
  provider, credential, path, port, or exception detail.
- [x] Every API response excludes account identity, OAuth tokens, quota,
  provider payloads, paths, and private exception context.

### Testing Requirements

- [x] Tests are written and observed failing before implementation.
- [x] Focused service, schema, route, dependency, settings, error, and lifespan
  tests pass.
- [x] Complete deterministic backend shell and engine suites pass.
- [x] OpenAPI generation and generated-client verification pass.

### Non-Functional Requirements

- [x] Monitor polling and shutdown are finite and bounded by typed settings.
- [x] Route reads are low-latency cache copies and do not wait on the provider.
- [x] Authentication/start/status logs use only finite state and reason codes.
- [x] Cleanup is idempotent, reverse ordered, and cannot mask an earlier
  startup or request failure.

### Quality Gates

- [x] All files are ASCII-encoded with Unix LF line endings.
- [x] Code includes intern-friendly comments for leases, cache side effects,
  authorization, and cleanup.
- [x] Ruff format/check, strict mypy, ty, frontend checks, and repository
  pre-commit pass.

---

## 8. Implementation Notes

### Working Assumptions

- The facade already owns the complete package authenticator. Session 04
  needs only public export of its existing safe response/error contracts, not
  a second authenticator or direct Codex import.
- `get_system_authentication_status(refresh=False)` reads package memory and
  does not construct an app-server. It is safe for the lifecycle monitor while
  the already-started ceremony owns the runtime.
- The status endpoint reads the shell cache only. Persisted-account refresh
  happens once in the FastAPI lifespan before worker startup.
- Readiness remains available to any active authenticated user because it
  contains only the already-reviewed coarse system projection.

### Conflict Resolutions

- The Session 04 PRD mentioned an expiry field, but the pinned public Codex SDK
  `DeviceCodeLoginHandle` exposes only `login_id`, `verification_url`, and
  `user_code`. The master system plan's safe response allowlist also omits
  expiry. The API will not fabricate a misleading provider deadline.
- The package ceremony completes in its own background thread. Releasing the
  runtime lease when the POST returns would violate the single app-server
  contract. A shell monitor therefore holds the lease across requests and
  observes only the public in-memory status.
- A GET status call could use `refresh=True` to inspect persisted credentials,
  but that would start a new app-server from browser polling. The lifecycle
  performs exactly one initial refresh; route polling stays cache-only.

### Key Considerations

- The monitor must release exactly the lease it acquired even when route
  calls, terminal completion, shutdown, or errors race.
- The package authentication snapshot is strict but the HTTP projection must
  add state-dependent URL/code validation so generated clients cannot receive
  malformed combinations.
- The runtime gate contains no user identity. Superuser authorization remains
  at the HTTP boundary and logs never include the caller's email or ID.
- Authentication cannot be composed when the real application is
  unconfigured. Routes must still load and return safe readiness/setup
  responses without a Tavily secret or Codex credentials.

### Potential Challenges

- The active package completion thread may finish between a replayed start and
  the monitor's next sample. Exact-once lease release and detached cached
  models prevent inconsistent ownership.
- slowapi requires a `Request` argument on decorated handlers. Tests must
  prove both the project RFC 9457 rate response and normal dependency
  authorization ordering.
- Client generation imports `app.main` without lifespan startup. No route
  dependency or schema import may access app state or external credentials at
  import time.

### Relevant Considerations

- [P02-backend] **Browser readiness reads only the cache**.
- [P02-backend] **Operational logs use field allowlists**.
- [P00-backend+backend/packages/txt2crs] **One process is mandatory**.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**.
- [P01-backend/packages/txt2crs] **One context owns provider resources**.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**.
- [P00] **Client generation is formatter-owning**.

---

## 9. Validation Plan

1. Run focused public export, settings, error translation, coordinator,
   schema, route, dependency, and lifespan tests.
2. Prove readiness/status GET requests do not call the application, gate,
   provider, or refresh scheduler.
3. Prove start retains/replays/releases the authentication lease across
   terminal, error, busy, close, and concurrency paths.
4. Run complete deterministic engine and shell pytest suites.
5. Regenerate OpenAPI/client and run frontend Biome and TypeScript gates.
6. Run Ruff format/check, strict mypy, ty, and repository pre-commit.
7. Verify public imports, route/error/log allowlists, no dependency/schema
   drift, ASCII/LF, and clean generated state.
