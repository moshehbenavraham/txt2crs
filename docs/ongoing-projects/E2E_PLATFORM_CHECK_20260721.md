# E2E Platform Check - 2026-07-21

## Purpose

This document records an end-to-end check of the local txt2crs platform. The
stack is launched with `scripts/start-local.sh`, authentication uses the
project-root `.env` values for `FIRST_SUPERUSER` and
`FIRST_SUPERUSER_PASSWORD`, and all credentials remain redacted from this log.

## Test environment

- Date: 2026-07-21
- Deployment: local Docker Compose stack started by `scripts/start-local.sh`
- Browser: Codex in-app Browser
- User role: configured first superuser
- Frontend URL: `http://localhost:5195`
- Backend URL: `http://localhost:8016`
- Status: original check complete; all eight findings resolved in follow-up

## Check log

| ID | Area | Check | Result | Evidence / notes |
| --- | --- | --- | --- | --- |
| E2E-001 | Startup | Validate `.env`, Docker, Compose topology, ports, database credentials, builds, and health checks | Pass | `scripts/start-local.sh --no-color` exited 0. The database, backend, and frontend reached their declared healthy states; the one-shot `prestart` service exited 0 as designed. Credentials were not printed. |
| E2E-002 | Public landing | Open the public page and inspect the content, navigation, source story, consent copy, and account-access route | Pass | The page title, public navigation, supported source types, four-publication promise, AI disclosure, and sign-in links rendered without browser warnings or errors. |
| E2E-003 | Authentication | Sign in with the configured root `.env` first-superuser credentials | Pass | `POST` to `login_access_token` returned 200, the authenticated user endpoint returned 200, and the browser reached `/create`. No credential was written to this document. |
| E2E-004 | System setup | Read and refresh course-system readiness | Pass | The page reported ChatGPT connected, model `gpt-5.6-sol`, accepting admission, and all eight checks ready. The refresh endpoints returned 200 without browser warnings or errors. See F-002 for the narrower meaning of the admission signal. |
| E2E-005 | Course library | Load retained ready and failed course requests | Pass | `/library` showed two current requests, newest first: one ready course and one terminal failed course. Links opened the corresponding owner-scoped job pages. |
| E2E-006 | Completed course | Inspect progress, publications, formats, answer-key disclosure, and research references | Partial | The completed job showed 13 of 13 steps, four publications with four formats each, ten accepted sources, a working format menu, and explicit instructor-only answer-key disclosure. Live HTML preview failed; see F-001. |
| E2E-007 | HTML preview | Preview the Course and Review pack HTML artifacts | Fail | Both dialogs created a `blob:` iframe with the expected dimensions, but the iframe rendered blank in the in-app Browser. The artifact endpoints returned 200 and the source files were non-empty. See F-001. |
| E2E-008 | Artifact download | Trigger the completed Course PDF download | Inconclusive | The backend served `download_job_artifact` with 200, but the in-app Browser did not emit a download event within 30 seconds and displayed no error. This may share an object-URL compatibility boundary with F-001 or may be a Browser automation limitation. |
| E2E-009 | New course submission | Submit one bounded topic, audience, prior-knowledge statement, learning goal, and explicit AI/research consent | Blocked by policy | The form validated and submitted once. The backend returned HTTP 429 / `JOB_7002` because the current superuser already has two admissions in the 24-hour window, matching the default per-user limit. No duplicate submission was attempted. See F-002. |
| E2E-010 | Failed course recovery | Open a terminal failed job | Pass | The page clearly stated that the job will not restart automatically and offered a route to create another course. It exposed no private failure detail. |
| E2E-011 | Missing job recovery | Open a valid-looking but nonexistent job reference | Pass | The page used the expected non-enumerating copy: the job may not exist or may not belong to the account, with a route back to course creation. |
| E2E-012 | Administration | Open the superuser-only user list | Pass | The user table rendered the configured account with Superuser and Active state. No mutation was performed. |
| E2E-013 | Account settings | Open profile, password, and danger-zone tabs | Pass | All tab panels rendered; no profile, password, or deletion mutation was performed. |
| E2E-014 | Appearance | Switch from Light to Dark and restore Light | Pass | The root theme class changed from `light` to `dark` and back; the missing-job recovery surface remained legible in both modes. |
| E2E-015 | Session security | Log out, request `/admin` while signed out, and sign back in | Pass | Logout reached `/login`; a direct protected-route request redirected to `/login?returnTo=%2Fadmin` without rendering the user table. Re-authentication returned to `/admin`. |
| E2E-016 | Frontend unit regression | Run the Vitest suite | Pass | 24 test files and 156 tests passed. |
| E2E-017 | Default Playwright journey | Run `course-journey.spec.ts` against the launched stack | Partial | With the launched API URL explicitly supplied, 5 tests passed and 12 live-inapplicable tests skipped. Without the override, setup targeted the stale API URL from `frontend/.env` and failed authentication. See F-006. |
| E2E-018 | Deterministic Playwright journey | Run `playwright.jobs.config.ts` | Fail in setup | The isolated browser server started, but user signup returned 500 because the backend process inherited stale PostgreSQL host-port credentials from `backend/.env`. One cleanup test passed; 29 tests did not run. See F-006. |

## Findings

### F-001 - High - Live HTML artifact previews are blank in the in-app Browser

**Reproduction**

1. Sign in as the configured superuser.
2. Open `/library` and the ready `intermediate python` course.
3. Select `Preview` for Course or Review pack.

**Observed:** the dialog replaces its preparation skeleton with a sandboxed
iframe, but the preview canvas is blank. This reproduced for two different
HTML artifacts. The iframe received a `blob:` URL, had a 467 by 675 pixel
content area, and contained no reachable `h1` through the frame locator. The
browser console reported no warning or error.

**Expected:** the iframe should display the generated publication. The source
files are non-empty (`intermediate-python-course.html` is 40,470 bytes and has
an `h1`; the review pack is 52,989 bytes), and each authenticated artifact GET
completed with HTTP 200.

**Likely boundary:** the live path depends on a sandboxed iframe navigating to
a temporary object URL. The existing deterministic Playwright coverage checks
the same shape, so a live artifact/IAB smoke case is needed to catch this
environment-specific failure.

### F-002 - Medium - Operator admission copy does not describe current-user quota

**Reproduction**

1. Open `/setup`; observe `Admission: Accepting course work` and a ready
   Admission capacity check.
2. As the same superuser, submit another valid course request.

**Observed:** submission returns HTTP 429 / `JOB_7002` with `Course job
admission capacity is unavailable.` The user has two admissions in the current
24-hour window, which equals the configured default per-user maximum.

**Analysis:** the readiness probe intentionally checks a synthetic new owner,
so it represents global/new-owner capacity, while submission enforces the
real owner's rolling quota. The policy is working, but the UI presents the
coarse signal as if it applies to the signed-in user.

**Expected improvement:** label the setup value as global/new-owner capacity,
and expose a safe owner-scoped availability or retry-after message on the
creation surface. The generic 429 currently gives no limit dimension or time
when a retry can succeed.

### F-003 - Low - Local backend startup mode is internally inconsistent

The backend announces `Starting FastAPI in production mode` while also running
Uvicorn with `--reload` and a WatchFiles reloader process. For a judge-facing
local deployment, either remove reload or label the mode as local/development
so logs and runtime behavior agree.

### F-004 - Low - The primary landing-page action begins below a common laptop fold

At the observed 1265 by 708 viewport, the oversized hero headline and
publication diagram fill the first screen; the topic draft control is below
the fold. The header sign-in action remains visible, so this is a conversion
and discoverability opportunity rather than a functional failure.

### F-005 - Low - Admin route has a brief blank loading state

Immediately after navigating to `/admin`, the DOM contained only the global
notifications region. The page populated within roughly 750 ms on localhost.
A page skeleton or loading heading would prevent a momentary blank workspace
on slower environments.

### F-006 - Medium - Local E2E configuration is split across conflicting env files

The launched stack uses the project-root ports (`5195` frontend and `8016`
backend), while `frontend/.env` points `VITE_API_URL` to `8012`. Consequently,
the documented default Playwright command fails its authentication setup until
`VITE_API_URL=http://localhost:8016` is supplied explicitly.

The dedicated `playwright.jobs.config.ts` path also fails before the journey:
its backend process loads `backend/.env`, which points PostgreSQL to port
`5447` with credentials that do not match the running root deployment on
`5450`. The signup endpoint therefore returns 500 with a PostgreSQL password
authentication failure. No password value was printed or recorded.

**Expected improvement:** load one canonical, explicit test environment or
start a fully isolated application database as part of the deterministic
Playwright configuration. The test harness should fail preflight with a clear
configuration message instead of surfacing an application 500.

### F-007 - Medium - A permanent missing-job error continues polling every five seconds

Leaving the nonexistent job page open produced repeated `GET read_job` calls
and paired `JOB_7001` warning log entries every five seconds until navigation
away. The page already had the correct terminal recovery copy, so these calls
could not change its outcome.

The query correctly disables retry for non-transient 404 errors, but its
`refetchInterval` still returns the normal visible polling interval whenever
there is no successful snapshot. Stop interval polling for known permanent
errors (such as 404/403/validation failures) to avoid unbounded warning noise
and avoidable backend load.

## Improvement opportunities

1. Add a live artifact-preview smoke test that uses a real served HTML artifact
   and verifies visible iframe content in the supported browser surface.
2. Add a download smoke assertion that proves the browser receives a file and
   verifies its suggested name and non-zero size.
3. Separate global/new-owner readiness from signed-in owner admission state,
   and give quota rejections a safe retry-after explanation.
4. Make the local backend mode and reload behavior agree in both logs and
   Compose configuration.
5. Keep a primary landing-page action visible at common laptop heights and
   provide a stable loading shell for protected data routes.
6. Stop progress polling after a permanent job-read error; retain polling only
   for active jobs and bounded transient recovery.
7. Make the default and deterministic E2E commands consume one explicit,
   self-consistent environment with a preflight database check.

## Final summary

The local stack remains running and healthy. Authentication, protected-route
guards, operator readiness, library navigation, completed and failed job
presentation, publication metadata, answer-key disclosure, administration,
settings, appearance, and recovery routes were exercised through the in-app
Browser. The browser console reported no warnings or errors during the final
authenticated library check.

Seven findings were recorded: one high-severity live in-app Browser preview
failure, three medium-severity issues (admission-scope messaging, split E2E
configuration, and permanent-error polling), and three low-severity UX/runtime
opportunities. A fresh generation could not be admitted because the configured
superuser had already reached the correct two-job rolling limit; the request
was sent once and was not retried.

Automated verification found 156 passing frontend unit tests. The default
Playwright course journey reached 5 passes with 12 tests skipped after pointing
it to the running API. The dedicated deterministic Playwright journey remains
blocked in setup by the conflicting local PostgreSQL environment described in
F-006.

## Follow-up - admission policy and learner capacity UI

This follow-up resolves F-002 and records the regression work requested after
the original two-generation limit blocked the live creation journey.

### Policy outcome

- Production fallback limits are doubled from 2 to 4 jobs per learner and from
  5 to 10 jobs globally in each rolling 24-hour window. Token and research
  budgets were doubled proportionally so a nominal job opening cannot be
  contradicted by an unchanged secondary budget.
- The judge-facing local environment is intentionally more permissive than
  production: 10 jobs per learner and 20 jobs globally, with proportional token
  and research budgets. The rebuilt backend container exposed the expected
  non-secret admission values.
- The engine now exposes a safe, owner-scoped capacity projection. It reports
  the effective number of complete jobs available after job-count, token, and
  research constraints; owner usage; shared availability; the rolling window;
  and the exact next reservation expiry. It does not expose another learner's
  identity or usage.

### Browser verification

| ID | Area | Check | Result | Evidence / notes |
| --- | --- | --- | --- | --- |
| E2E-019 | Rebuild | Restart the edited stack with `scripts/start-local.sh` | Pass | Backend, frontend, database, proxy, Adminer, Mailcatcher, and Jaeger reached their expected healthy/running states; `prestart` exited 0. |
| E2E-020 | Owner capacity | Open `/create` as the configured superuser | Pass | The page reported 8 generations ready, 2 of 10 reservations used, a rolling 24-hour policy, and the exact next expiry (`Jul 22, 2026, 12:02 PM` in the browser locale). |
| E2E-021 | Ownership continuity | Navigate from `/create` to `/library` and back | Pass | The library still showed the ready and failed retained requests, and returning through the sidebar restored the same owner-scoped capacity. The create action remained enabled because capacity was available. |
| E2E-022 | Readiness semantics | Open `/setup` | Pass | The status now says `Platform ready`, describes core services and shared admission capacity, labels admission as `Shared capacity available`, and explicitly directs learner-specific availability to Create course. |
| E2E-023 | Responsive appearance | Inspect the capacity surface in Light and Dark at desktop and at a 375 by 812 mobile viewport | Pass | The editorial capacity strip remained readable, stacked cleanly on mobile, retained visible progress and expiry information, and matched the existing warm paper/forest/gold visual system in both themes. |
| E2E-024 | Browser diagnostics | Inspect warnings and errors after authentication, navigation, theme changes, and responsive checks | Pass | The in-app Browser reported zero warning or error console entries. |

### Automated regression evidence

- Engine package: 511 tests passed and 2 live Codex acceptance tests skipped.
- Engine static checks: Ruff passed; mypy passed across 138 source files.
- Application type checks: mypy passed across 47 source files.
- Frontend: 160 unit tests passed; typecheck, Biome lint, and the production
  build passed.
- Production fallback admission defaults were also asserted in an isolated
  settings process: 4 per learner, 10 shared, with the doubled proportional
  token and research ceilings.
- `git diff --check` passed.

### F-002 resolution

The creation surface now answers the question the original System Setup signal
could not: how many complete generations the signed-in learner can submit and
when the next reservation returns. When availability reaches zero, only the
submission action is disabled; the learner can continue preparing the draft.
The server remains authoritative at submission time.

### F-008 - High - Backend tests can mutate the live Compose database

Running focused backend tests from inside the already-running backend service
reused the live application database. The autouse database fixture removed the
seeded superuser, invalidating the browser session and temporarily orphaning
the shell account from the durable engine jobs. The engine SQLite job and
artifact records were not deleted.

The configured superuser was restored through the application's initialization
path and re-associated with the original owner UUID recovered from the durable
job store. Browser verification then proved that both retained jobs and the two
admission reservations were visible again.

**Expected improvement:** backend test commands must refuse a non-test database
or require an explicit isolated database name before fixtures can perform
destructive cleanup. Do not run the suite inside the live application service
until that guard exists. This is a stricter and more immediate form of the
environment-isolation risk already described in F-006.

### Follow-up summary

F-002 is resolved. The local app remains running at `http://localhost:5195`,
the signed-in learner is left on `/create`, and the visible quota is now both
more permissive and understandable before submission. The remaining new issue
is F-008: a high-severity test-isolation guardrail gap, documented here for a
separate fix.

## Follow-up - remediation completion

This follow-up resolves F-001 and F-003 through F-008. Together with the
earlier F-002 capacity work, all findings from this check are now addressed.
The original check log above is retained as historical evidence of the
failures that prompted these changes.

### Resolution matrix

| Finding | Result | Resolution |
| --- | --- | --- |
| F-001 | Resolved | Authenticated HTML is sanitized and supplied directly to a capability-free sandboxed iframe through `srcDoc`; preview no longer depends on a temporary `blob:` navigation. A live retained course rendered its heading, metadata, prerequisites, and objectives in the rebuilt Compose frontend. |
| F-002 | Resolved | The earlier owner-capacity follow-up added learner-scoped availability, safe expiry information, and clearer shared-capacity wording. |
| F-003 | Resolved | The judge-facing backend no longer starts FastAPI with `--reload`. Container process inspection found one `fastapi run app/main.py` process and the production-mode log now matches runtime behavior. |
| F-004 | Resolved | The landing hero, diagram, prompt, and spacing were compacted. At 1265 by 708, the primary `Build my course` action ended at 683 pixels and remained visible in the first viewport. |
| F-005 | Resolved | The protected admin route now supplies an immediate page-identity loading shell with a user-table skeleton and `aria-busy` state. A route contract test prevents regression to a blank pending DOM. |
| F-006 | Resolved | Default Playwright loads the project-root `.env` explicitly and derives both app ports from that canonical source. Deterministic Playwright no longer imports either side's dotenv file and its browser server owns a run-scoped SQLite account database, so it cannot inherit local PostgreSQL credentials. |
| F-007 | Resolved | Progress interval polling stops when the last job-read error is permanent. A live missing-job route produced one `JOB_7001` response total while left open beyond the old five-second interval. |
| F-008 | Resolved | Backend tests now fail closed unless the configured PostgreSQL database name visibly identifies test isolation (`test_*` or `*_test`). The shell test entrypoint performs the same preflight, deterministic browser auth uses SQLite, and CI integration jobs select `app_test`. |

The SQLite authentication path also exposed a cross-dialect type mismatch that
PostgreSQL had tolerated. JWT subjects are now parsed into `UUID` values before
SQLModel filtering, with valid and malformed-subject regression coverage.

### Post-fix E2E evidence

| ID | Area | Check | Result | Evidence / notes |
| --- | --- | --- | --- | --- |
| E2E-025 | Rebuild | Rebuild and start the complete Compose stack | Pass | `scripts/start-local.sh --no-color` exited 0; database, backend, and frontend were healthy, and `prestart` exited 0. |
| E2E-026 | Live preview | Open a retained Course publication in the rebuilt frontend | Pass | The sandboxed frame contained 38,543 bytes of sanitized `srcdoc` and visibly rendered the retained intermediate-Python course. Browser console and page-error logs remained empty. |
| E2E-027 | Preview and download automation | Exercise publication preview and a real browser download | Pass | Deterministic Chromium asserted visible iframe content, no frame `src`, expected `srcdoc`, suggested filename, an on-disk download path, and a non-zero downloaded file size. Hostile-content sandbox assertions also passed. |
| E2E-028 | Landing fold | Inspect the public landing page at 1265 by 708 | Pass | The primary action was fully inside the viewport; browser console and page-error logs were empty. |
| E2E-029 | Admin pending state | Verify the protected route pending component | Pass | The route wires `AdminPending` at zero pending delay; rendered markup retains the Users heading, skeleton rows, and busy semantics. |
| E2E-030 | Default Playwright environment | Run the default course journey without an API override | Pass | 6 tests passed and 12 live-inapplicable tests skipped. Authentication used the root-configured API rather than stale `frontend/.env` data. |
| E2E-031 | Deterministic Playwright | Run the complete isolated Chromium configuration | Pass | 31 tests passed and 1 cleanup-project prerequisite was intentionally skipped. The focused course journey contributed 18 passes and 1 intentional skip. |
| E2E-032 | Permanent-error polling | Leave a valid-looking missing job route open beyond one old poll interval | Pass | Only the initial backend read occurred; no repeated five-second request or warning was emitted. |
| E2E-033 | Database isolation | Attempt test preflight against the live `app` database, then run the suite against a disposable `*_test` database | Pass | Both host and live-container preflights refused `app` before opening a session. Alembic upgraded the disposable database, 554 application tests passed, and the database was dropped afterward. |
| E2E-034 | Frontend and backend quality gates | Run unit, type, lint, and contract checks | Pass | Frontend: 27 Vitest files and 162 tests passed; TypeScript and Biome passed. Backend: mypy passed for 47 app source files; Ruff and the new container, port, database-safety, deterministic-database, and token-subject tests passed. |

The Codex in-app Browser integration used for the original reproduction was
not installed in this remediation session. The failing object-URL boundary was
removed entirely, and the replacement was verified in both the rebuilt live
Compose app and the fully isolated Chromium journey. This is the only
tool-surface limitation in the follow-up evidence, not an open implementation
issue.

### Final remediation state

All eight findings and all seven listed improvement opportunities are
addressed. The local Compose stack remains running and healthy for inspection.
No live course-generation request or account mutation was needed during the
remediation pass.
