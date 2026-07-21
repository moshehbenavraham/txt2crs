# Course Library and Job Navigation Investigation

## Report status

- Investigation date: 2026-07-21
- Status: Complete
- Scope: Read-only product, browser, route, API, and planning review
- Investigation application code changed: No
- Job used for route verification:
  `job-dc80a8c30f994603a3e525f0eb2f80c6`

## Implementation workspace

- Implementation status: Complete
- Latest implementation session: 2026-07-21
- Workflow: Apex Spec `qimpl`

### Completed in the latest session

- Added test-first coverage for owner isolation, deterministic newest-first
  ordering, stable cursor continuation, malformed pagination, the private HTTP
  collection contract, exhaustive frontend statuses, and collection polling.
- Added the package-owned `SqliteJobStore.list_resume_states` query. It requires
  the owner at the storage boundary and uses `created_at DESC, job_id DESC` as
  its stable order.
- Added bounded public job-summary/page contracts and opaque cursor encoding in
  the engine public-query boundary.
- Added `JobService.list_public_jobs` and `Txt2CrsApplication.list_public_jobs`;
  the shell does not query engine SQLite or rebuild projections.
- Added the authenticated `GET /api/v1/jobs` shell route, response models,
  private/no-store headers, page-size validation, and safe package-error
  translation.
- Regenerated the OpenAPI frontend client and added the protected `/library`
  route with a persistent `My courses` destination on desktop and mobile.
- Added visibility-aware collection polling, accessible loading, empty, error,
  and pagination states, exhaustive active/ready/failed/cancelled presentation,
  and direct links back to each existing private job route.
- Added browser coverage for keyboard operation, mobile navigation, opaque
  pagination, safe error recovery, light/dark rendering, the 500-character
  public title maximum, touch targets, and browser/runtime error health.
- Visually inspected the populated 1440x900 light theme and 375x812 dark theme.
  The first inspection exposed a mobile intrinsic-width clipping defect; a
  test-first card-grid correction now wraps the maximum title inside the
  viewport.

### Verification evidence

- `uv run --package txt2crs pytest -q` - passed, 493 tests; 2 explicit live
  provider acceptance tests skipped.
- `uv run --package txt2crs ruff check .` - passed.
- `uv run --package txt2crs mypy` - passed for 138 source files.
- `uv run pytest tests/ -q` with the active Compose PostgreSQL credentials -
  passed, 541 tests.
- `uv run ruff check app` - passed.
- `uv run mypy app` - passed for 47 source files.
- `npm run test:unit` - passed, 146 tests in 22 files.
- `npm run typecheck`, `npm run lint`, and `npm run build` - passed.
- Full provider-free Playwright run using `playwright.jobs.config.ts` - passed,
  20 tests with 1 intentional skip, including setup, the existing course
  journey, the library, and cleanup. The library checks observed no console
  error, page error, or framework error overlay.

### Work remaining

- None for the accepted course-library scope. Deletion and retention-management
  controls remain separate lifecycle work and were not part of this setup.

## Executive summary

At investigation time, the application did not provide a tab, sidebar item,
page, or API for browsing already-created courses or in-progress
course-generation jobs. This was not a hidden control, permission problem,
responsive-layout bug, or failed frontend render. The capability had been
deliberately deferred from the P0 release as the P1 "job library" requirement.

An authenticated learner can see a job only when the browser is already on its
exact private route, `/jobs/$jobId`. Submitting a course navigates directly to
that route, and revisiting the full route works. After navigating away, however,
the application provides no in-product way to rediscover the job. Browser
history, a separately saved URL, or manual route reconstruction from a copied
job ID were required.

That baseline gap is now resolved by the implemented owner-scoped `/library`
feature. The observations and evidence below remain as the historical rationale
for the cross-stack implementation.

## What was observed in the running application

The authenticated application was inspected at desktop and mobile widths using
both the course-creation route and the exact route for the job above.

### Desktop navigation

The sidebar showed only:

- `Create course`
- `System setup` for a superuser
- `Admin` for a superuser

There was no `Courses`, `My courses`, `Library`, `History`, or `In progress`
destination. The exact job route rendered normally when opened directly.

### Mobile navigation

The mobile navigation drawer exposed the same destinations as the desktop
sidebar. No course-library destination was hidden behind a responsive-only
control or an overflow menu.

### Exact job route behavior

The route `/jobs/job-dc80a8c30f994603a3e525f0eb2f80c6` loaded the private job
page successfully. At the time of inspection, it presented the terminal failed
state for that job and offered actions such as copying the job reference and
creating another course.

The sidebar highlighted `Create course` while on the job page because the
sidebar intentionally treats `/jobs/` as one of that item's active prefixes.
Selecting `Create course` navigated to `/create`. Once there, no navigation
control led back to the previous job.

No console error, page error, blank route, or framework error overlay was
observed. These results rule out a frontend rendering failure as the reason the
course-library controls were absent.

## Frontend evidence

### The sidebar has no library item

[`AppSidebar.tsx`](../../frontend/src/components/Sidebar/AppSidebar.tsx) defines
only `Create course` in the base authenticated navigation. `System setup` and
`Admin` are conditionally added for superusers. The `Create course` item also
declares `/jobs/` as an active prefix, which explains why it appears selected on
an individual job route.

Relevant source: lines 15-37.

### There is no collection route

The authenticated route tree contains:

- `/create`
- `/jobs/$jobId`
- `/setup`
- `/admin`
- `/settings`

It does not contain `/jobs`, `/courses`, `/library`, or `/history`. The only
learner job route is
[`jobs.$jobId.tsx`](../../frontend/src/routes/_layout/jobs.$jobId.tsx), which
requires a known job ID.

### Submission is the only automatic entry into a job page

[`useCourseSubmission.ts`](../../frontend/src/hooks/useCourseSubmission.ts)
navigates a successful submission directly to `/jobs/$jobId` using the newly
accepted job ID. This creates a valid path into one job at submission time, but
does not retain or expose a browsable set of jobs.

Relevant source: lines 198-207.

### Progress reads only one known job

[`queries.ts`](../../frontend/src/components/CourseProgress/queries.ts) calls
`JobsService.readJob` with one route-supplied `job_id`. It supports polling and
refresh-safe reads for that one known job, but has no job-collection query.

Relevant source: lines 115-148.

### The recovery wording overstates in-product rediscovery

[`CourseProgressPage.tsx`](../../frontend/src/components/CourseProgress/CourseProgressPage.tsx)
says that the private page is safe to revisit and that the learner can close the
page and return to the same private job. Technically, the durable route remains
valid, but the product does not provide a way to find that route again.

The same page's copy action places only the opaque job ID on the clipboard, not
the complete private URL. As a result, the current claim depends on one of the
following external recovery mechanisms:

- The learner uses browser history.
- The learner separately saves the complete URL.
- The learner copies the job ID and manually reconstructs the route.

No job ID or course-history collection is persisted in local storage or session
storage. The existing browser storage is used for concerns such as the intake
draft and authentication session, not durable job discovery.

Relevant source: lines 67-77, 387-395, and 528-558.

## API and engine evidence

The generated frontend client exposes:

- `POST /api/v1/jobs`
- `POST /api/v1/jobs/upload`
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/jobs/{job_id}/artifacts`
- `GET /api/v1/jobs/{job_id}/artifacts/{artifact_id}`

It does not expose a `GET /api/v1/jobs` collection operation. See
[`sdk.gen.ts`](../../frontend/src/client/sdk.gen.ts), beginning with the jobs
service around line 754.

The shell's [`jobs.py`](../../backend/app/api/routes/jobs.py) reads one exact
job through the package facade with both `job_id` and the authenticated
`user_id`. The engine's
[`facade.py`](../../backend/packages/txt2crs/src/txt2crs/application/facade.py)
similarly exposes `get_public_job` for one exact owner-authorized job. Neither
boundary currently exposes an owner-scoped paginated list.

The engine store does contain `next_runnable_job`, but that is a private worker
query. It returns at most one recovery-first work item and deliberately selects
the owner from stored data. It is not an owner-facing history endpoint and
must not be repurposed as one.

The application shell must not work around the missing package contract by
querying the engine SQLite database directly. Project architecture requires
route handlers to call the `txt2crs` package boundary for engine persistence
and queries.

## Product and planning evidence

The missing capability is explicitly documented as deferred:

- The master [PRD](../../.spec_system/PRD/PRD.md) lists "A learner can browse a
  paginated job library and reopen retained jobs" under Deferred Requirements
  at line 115.
- The system
  [build plan](./INPUT_TO_COURSE_SYSTEM_PLAN.md) defines `/library` as an owner
  P1 route for job history, reopening, deletion, and retention state at lines
  936-946.
- The archived Phase 03 backend
  [session](../../.spec_system/archive/phases/phase_03/session_02_owner_scoped_job_results_and_recovery.md)
  explicitly places job list/history out of scope at lines 33-38.
- The detailed Phase 03
  [specification](../../.spec_system/archive/sessions/phase03-session02-owner-scoped-job-results-and-recovery/spec.md)
  identifies job list/history as deferred P1 lifecycle scope at lines 117-120.
- The Phase 04 learner-experience
  [specification](../../.spec_system/specs/phase04-session01-public-landing-intake-and-progress/spec.md)
  defers the job library because Phase 03 supplied no collection API, at lines
  118-124.
- The dashboard [design notes](../dashboard-design.md) explicitly prohibit the
  existing page from implying job history, counts, or recency that the API does
  not provide, at lines 973-979.

All phases recorded in `.spec_system/state.json` are complete and
`current_session` is `null`. No currently scheduled implementation session owns
this P1 requirement.

## Historical classification at investigation time

| Question | Finding |
|---|---|
| Is there a hidden course-history tab? | No |
| Is the control limited to superusers? | No; it is absent for all roles |
| Is it hidden only on mobile or desktop? | No; both navigation variants match |
| Is an existing route failing to render? | No |
| Can an exact known job URL be reopened? | Yes, subject to normal owner authorization and retention |
| Can the app list or rediscover a user's jobs? | No |
| Was this behavior planned? | Yes; the job library was explicitly deferred to P1 |
| Is the current gap still user-visible? | Yes; leaving a job page removes the only in-app path back |

## User impact before implementation

The gap affects both active and completed work:

- A learner cannot see all in-progress generation jobs.
- A learner cannot reopen a completed course from an in-product list.
- A learner cannot rediscover a failed or interrupted job for diagnosis or
  retry context.
- Cross-device recovery is impractical unless the complete URL was saved.
- Clearing history or losing the tab can make a retained job effectively
  undiscoverable even though its durable backend record still exists.
- The job-page recovery wording can create an expectation the navigation does
  not currently fulfill.

## Implemented solution shape

The durable server-owned job library should be implemented as one coherent
cross-stack feature, not as a browser-storage shortcut.

1. Add an owner-scoped paginated job-summary query to the `txt2crs` engine
   store, service, and public application facade.
2. Return only a bounded allowlisted summary: job ID, safe course title or
   topic, status, progress summary, created/updated time, terminal outcome, and
   whether results are available.
3. Expose that package contract through `GET /api/v1/jobs` in the FastAPI shell.
   Sharing the path with the existing `POST /api/v1/jobs` is valid because the
   HTTP methods differ.
4. Preserve exact owner isolation, private/no-store response headers, stable
   ordering, bounded page size, and an opaque continuation mechanism.
5. Regenerate the frontend OpenAPI client rather than editing generated files.
6. Add an authenticated `/library` route and a persistent `My courses` or
   `Courses` sidebar destination on desktop and mobile.
7. Present, at minimum, `In progress`, `Ready`, and terminal jobs with a direct
   reopen action for `/jobs/$jobId`.
8. Poll the collection conservatively only while a visible page contains
   non-terminal jobs; keep individual job polling on the existing detail route.
9. Add empty, loading, error, pagination, long-title, mobile, keyboard, and
   owner-isolation tests before implementation, following the repository's
   test-first rule.

A local-storage-only list is not recommended. It would omit jobs created on
another device, disappear when browser data is cleared, fail to reflect server
retention, and potentially drift from the authoritative job state.

## Suggested acceptance criteria

- Every authenticated learner sees a persistent course-library navigation item
  on desktop and mobile.
- The library returns only jobs owned by the authenticated user.
- Active, completed, failed, and cancelled jobs have clear, exhaustive visual
  states.
- Selecting any retained job opens its existing `/jobs/$jobId` page.
- The list has deterministic newest-first ordering with stable pagination.
- A refresh, sign-out/sign-in cycle, or different browser can recover retained
  jobs from the server.
- Empty, loading, transient-error, permanent-error, and pagination states are
  accessible and responsive.
- Collection polling stops when no listed job is active or when the page is not
  visible.
- No engine database query is duplicated in the FastAPI or React shell.
- The generated API client remains generated and unedited by hand.

## Final finding

The reported absence was confirmed and has been resolved. The application now
supports both durable single-job routes and a server-owned, discoverable course
collection. The completed P1 `/library` feature begins with a package-owned,
owner-scoped paginated query, crosses the authenticated generated API client,
and ends with a persistent desktop/mobile navigation destination whose rows
reopen the existing private job pages.
