# txt2crs Frontend

The frontend is a React 19, TypeScript, Vite, TanStack Router/Query, Tailwind
CSS 4, and shadcn/Radix application. It currently presents authentication,
users, settings, administration, a superuser course-system setup workspace,
and the learner journey from public product explanation through multimode
course intake, owner-scoped live progress, and private completed publications.

## Current Routes

| Route | Purpose |
|-------|---------|
| `/` | Public one-source-to-four-publications product story |
| `/login` | Login |
| `/signup` | Configured-access information or local registration |
| `/recover-password` | Password recovery |
| `/reset-password` | Password reset |
| `/create` | Authenticated prompt, text, URL, YouTube, or file intake |
| `/library` | Authenticated owner-scoped retained course library |
| `/jobs/$jobId` | Authenticated owner-scoped progress and completed publications |
| `/settings` | User settings |
| `/setup` | Superuser course-system readiness, device login, and CLI recovery |
| `/admin` | Superuser administration |

Page titles and accessible product names use the shared
`src/lib/branding.ts` helper.

## Public Access Configuration

`VITE_ENABLE_PUBLIC_SIGNUP` controls only whether a build displays local
account-creation actions. It defaults to `false`. Compose derives that public
build value from the root `ENABLE_PUBLIC_SIGNUP` setting.

`VITE_HTML_PREVIEW_MAX_BYTES` controls whether a manifest-declared HTML
artifact is offered for in-browser preview. It accepts a strict positive
integer and defaults to `5242880` (5 MiB). It is a public presentation limit,
not an upload, authorization, or artifact-delivery boundary; the backend
remains authoritative.

The frontend setting is not authorization. The backend remains authoritative
for every signup request and can reject disabled or revoked access even when a
previously built page still shows the action. Do not put secrets in any
`VITE_*` value because Vite embeds those values in browser assets.

## Course Intake, Library, and Progress

The `/create` workbench accepts exactly one source mode and optional learning
intent. Its centralized Zod schema mirrors the generated backend contract,
removes inactive fields, requires explicit AI/research-processing consent,
and never parses an uploaded document in the browser.

`src/hooks/useCourseSubmission.ts` owns canonical retry identity, duplicate
submission prevention, generated-client JSON/multipart calls, safe error copy,
and navigation from the accepted opaque job ID. Components must compose that
hook rather than rebuilding its logic.

`/library` reads the generated owner-scoped job collection with stable
newest-first cursor pagination. It provides accessible loading, empty, error,
and pagination states and maps every active, completed, failed, and cancelled
status to an existing `/jobs/$jobId` route. Collection polling runs only while
the page is visible and at least one loaded job is non-terminal. The persistent
`My courses` navigation item covers the library and job-detail routes on
desktop and mobile.

`/jobs/$jobId` reads only the authenticated owner's generated status
projection. Active jobs use a visibility-aware polling policy; terminal jobs
and permanent owner/validation read errors stop interval polling. Transient
failures receive bounded backoff. Refreshing or directly reopening the private
URL revalidates the server state. Missing and foreign-owned jobs deliberately
share one recovery surface. A content-free runtime heartbeat is evidence of
current worker activity only and remains distinct from checkpoint revision and
progress.

When a job completes, the same route reads its generated owner-scoped manifest
once and presents course, review pack, assessment, and instructor answer key
folios. Each folio has one primary PDF action plus an accessible menu for
HTML, Markdown, PDF, and DOCX. The answer-key files remain collapsed until the
owner explicitly opens them.

All file bodies use the generated authenticated artifact client. HTML preview
is lazy-loaded, byte/media verified, parsed into a preview-only document, and
provided as sanitized iframe `srcdoc` in an empty-capability sandbox with a
restrictive CSP and no-referrer policy. No object URL is created and no
artifact HTML is injected into the React document. Source and conflict
disclosures use only the bounded completed-job projection.

The browser keeps only a bounded prompt handoff in `sessionStorage`; source
content is not placed in URLs or `localStorage`. These implementation choices
are not a promise about server retention, regulatory compliance, or external
AI/research-provider policies.

## Setup and Commands

```bash
cd frontend
npm ci
npm run dev
```

The Compose frontend is available at <http://localhost:5195>. Common checks:

```bash
npm run test:unit
npm run typecheck
npm run lint
npm run build
npx playwright test
```

The default Playwright configuration reads the repository-root `.env` as the
reference-stack source of truth; host-only `frontend/.env` values do not redirect
its API client. The credential-free learner journey uses
`playwright.jobs.config.ts`, one fresh run-owned state directory, and a
run-owned SQLite account database. It exercises production routes, auth,
worker, package facade, persistence, and delivery without connecting to local
PostgreSQL or exposing test-only HTTP controls.

## Generated API Client

Run generation from the repository root:

```bash
./scripts/generate-client.sh
```

The script exports `frontend/openapi.json`, regenerates
`frontend/src/client/`, and formats both. Never edit generated client files
manually. Route generation is also tool-owned: run `npm run build` (or Vite)
after route changes and never hand-edit `src/routeTree.gen.ts`.

## Source Structure

```text
frontend/src/
|-- client/          # Generated OpenAPI client
|-- components/      # Product and shadcn/Radix components
|-- hooks/           # Auth and canonical course-submission composition
|-- lib/             # Branding, schemas, types, and utilities
|-- routes/          # TanStack file-based routes
`-- routeTree.gen.ts # Generated route tree
```

Centralized Zod schemas under `src/lib/schemas/` mirror backend validation.
Branded types under `src/lib/types/` prevent ID and email mixups. Server state
belongs in TanStack Query.

## Production-Like Local Image

The Dockerfile builds the Vite application and serves it from Nginx. Nginx
adds browser security headers and exposes:

```json
{"status":"healthy","service":"frontend"}
```

at `GET /health`. The image health check calls that endpoint internally every
30 seconds so Compose can reject an unresponsive serving process.

## Browser Tests

Against the Compose stack:

```bash
docker compose up -d --wait backend frontend mailcatcher
cd frontend
npx playwright test
```

The course-generation journey has a dedicated provider-free test application.
It uses the normal FastAPI routes, authentication, serial worker, generated
frontend client, and owner checks while replacing external generation with a
finite deterministic scenario. The completed story verifies all 16 manifest
entries, exact displayed sizes, format-menu keyboard behavior, real PDF and
HTML transfers, sandbox/CSP isolation, hostile preview stripping, URL cleanup,
direct refresh, and minimum-width reflow. The same configuration also verifies
course-library loading, empty and error recovery, exhaustive statuses, opaque
pagination, keyboard/touch navigation, light/dark responsive rendering, and
the maximum public title length:

```bash
docker compose up -d --wait db
cd frontend
npx playwright test --config playwright.jobs.config.ts
PLAYWRIGHT_PRODUCTION_FRONTEND=1 \
  npx playwright test --config playwright.jobs.config.ts
TXT2CRS_BROWSER_SCENARIO=failed \
  npx playwright test --config playwright.jobs.config.ts
```

Each dedicated run creates private engine state and a fresh normal user,
starts and stops its own backend and frontend processes, and cleans package
resources at application shutdown. The production option builds the frontend
and serves it through the real Nginx security headers so preview CSP behavior
is exercised in Chromium. It is test composition only; the
test-application factory fails closed unless its explicit test environment
flag is present.

Playwright output is written to ignored report/result directories. Stop the
stack with `docker compose down`; add `--volumes` only when intentionally
discarding local data.
