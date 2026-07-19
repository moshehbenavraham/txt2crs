# Implementation Notes

**Session ID**: `phase02-session04-system-readiness-and-auth-api`
**Package**: backend
**Started**: 2026-07-19 21:19
**Last Updated**: 2026-07-19 21:34

---

## Session Progress

| Metric | Value |
|--------|-------|
| Tasks Completed | 25 / 25 |
| Estimated Remaining | 0 minutes |
| Blockers | 0 |

---

## Outcome

FastAPI now exposes three generated system operations:

- Authenticated `GET /api/v1/system/readiness`.
- Superuser-only `POST /api/v1/system/auth/start`.
- Superuser-only `GET /api/v1/system/auth/status`.

Both GET routes are cache-only. They do not call the package facade, acquire
runtime ownership, refresh credentials, start Codex or MCP, or run database/
artifact probes. Device start retains the shared authentication lease across
the package's background ceremony, and one finite monitor releases it only
after authenticated, failed, start-error, or shutdown state.

The response contracts expose only coarse readiness dimensions or the
validated OpenAI verification URL, bounded user code, finite auth state, and
safe message. Authorization, rate limits, semantic RFC 9457 errors, generated
OpenAPI/TypeScript types, and CLI recovery documentation are complete.

---

## Tests-First Evidence

The new focused test set was written before production modules. Initial
collection failed because the public authentication exports, shell
coordinator, strict schemas, app-state dependencies, system router, settings,
and error code did not exist. After implementation, the focused session slice
passes 79 tests.

The host PostgreSQL port remains occupied by an unrelated container. No
container was changed. Shell tests used the project database at
`172.19.0.2:5432`.

---

## Task Log

| Task Range | Result | Evidence |
|------------|--------|----------|
| T001-T002 | Complete | Public authenticator, cache/gate, authorization, rate, error, and client seams inspected |
| T003-T004 | Complete | Public export and exact finite setting regressions added |
| T005-T006 | Complete | Initial refresh, replay, exclusivity, terminal release, failure, and close tests added |
| T007 | Complete | Readiness/auth schema allowlist, time, URL, code, cross-state, and extra-field tests added |
| T008-T009 | Complete | Authenticated readiness, superuser auth, side-effect, error, and rate tests added |
| T010-T011 | Complete | Lifespan ordering and generated OpenAPI contract tests added |
| T012-T021 | Complete | Public exports, coordinator, schemas, dependencies, routes, errors, lifecycle, docs, and client implemented |
| T022 | Complete | 79 focused shell/engine session tests passed |
| T023 | Complete | 294 shell and 464 engine deterministic tests passed |
| T024 | Complete | Client generation, Ruff, mypy, ty, frontend, and repository hooks passed |
| T025 | Complete | Public imports, route/log/error fields, cache reads, generated state, and diff integrity verified |

---

## Files Created

| File | Purpose |
|------|---------|
| `backend/app/services/txt2crs_authentication.py` | Cached auth state, retained runtime lease, finite monitor, and safe lifecycle |
| `backend/app/schemas/system.py` | Strict readiness and device-auth HTTP projections |
| `backend/app/api/routes/system.py` | Protected readiness/start/status routes |
| `backend/tests/services/test_txt2crs_authentication.py` | Coordinator lifecycle and concurrency regressions |
| `backend/tests/schemas/test_system_schemas.py` | Response allowlist and cross-field regressions |
| `backend/tests/api/routes/test_system.py` | Authentication, authorization, response, error, and rate regressions |

## Files Modified

| File or Area | Change |
|--------------|--------|
| Public `txt2crs.application` exports | Exposed safe authentication state, snapshot, and error contracts |
| Shell settings and `.env.example` | Added finite monitor poll and shutdown bounds |
| Error codes, translator, and rate limits | Added `SYSTEM_AUTH_FAILED` and explicit system endpoint limits |
| API dependencies/router registry | Added fail-closed lifespan service resolution and system router |
| FastAPI lifespan/service exports | Added auth cache startup/state and safe teardown ordering |
| Engine/shell focused tests | Protected exports, settings, translation, lifecycle, routes, and generated contract |
| `frontend/src/client/` | Regenerated system schemas, types, and SDK operations |
| Backend/API documentation | Documented route authorization, cache behavior, safe fields, and CLI recovery |
| Apex artifacts/state | Planned and recorded Session 04 |

---

## Key Implementation Decisions

1. **HTTP GETs are pure cache reads**: Persisted-account refresh happens once
   in the lifespan; browser polling cannot create an app-server.
2. **The lease follows the ceremony**: The POST response does not release
   runtime ownership while the package completion thread remains active.
3. **The monitor reads memory only**: Every active sample uses
   `refresh=False`; no second credential/provider graph can start.
4. **Auth starts before readiness**: Startup order is authentication cache,
   readiness cache, worker. Teardown is worker, readiness, authentication,
   gate, facade, preventing maintenance from acquiring a just-released auth
   lease before package cancellation.
5. **No fabricated expiry**: The pinned public SDK exposes no device-code
   deadline and the master safe response allowlist omits it.
6. **Errors cross outside catch scope**: Translated package errors are raised
   only after the caught exception scope ends, preventing Python from
   reattaching private `__context__`.
7. **Generated files remain script-owned**: OpenAPI and TypeScript are
   regenerated/formatted together and never patched manually.

---

## Verification

### Focused Tests

- Public application export tests: 4 passed.
- Combined service/schema/route/settings/error/lifespan/client slice:
  77 passed before two final service regressions; 79 current focused cases.

### Complete Deterministic Suites

- `uv run --package txt2crs pytest -q`
  - PASS: 464 passed; 1 explicit live Codex/Tavily test skipped.
- `POSTGRES_SERVER=172.19.0.2 POSTGRES_PORT=5432 uv run pytest tests/ -q`
  - PASS: 294 passed; 71 short-test-key warnings.

### Static And Repository Gates

- Shell Ruff, strict mypy, and ty: PASS.
- Engine public export test and complete suite: PASS.
- OpenAPI/client generation, frontend Biome and TypeScript: PASS.
- Repository pre-commit: PASS.
- `git diff --check`: PASS.

---

## Deviations And Blockers

- The session PRD mentioned device-code expiry. The pinned official SDK does
  not expose one, so the API truthfully omits it rather than inventing a
  deadline.
- One shell static command was issued from the engine package root and one
  client script invocation from `backend/`; both produced only path-context
  errors. The same commands passed from their documented working directories.
- No dependency, PostgreSQL schema, Alembic migration, hand-edited generated
  client, logout route, learner route, or frontend setup screen was added.
- The credentialed live GPT-5.6/Tavily proof remains release-gated.

---

## Self-Review Repairs

Initial implementation started readiness before the auth cache and closed auth
before readiness. Review found that releasing an active authentication lease
could let the still-live readiness thread start a provider probe before facade
cleanup cancelled the package ceremony. Startup/teardown ordering was reversed
at the cache layer, and a lifespan regression now protects the safe sequence.

Formal review also found that a direct authentication call before lifecycle
startup could retain a lease without a monitor, while initial runtime
contention left the default cache looking definitively signed out. The service
now rejects pre-start calls before gate/package access and publishes an
explicit safe failed snapshot when its initial refresh cannot acquire the
runtime. Focused regressions protect both paths.

---

## Next Step

Run `validate` against the repaired base-to-head surface.
