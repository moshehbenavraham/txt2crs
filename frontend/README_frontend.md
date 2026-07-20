# txt2crs Frontend

The frontend is a React 19, TypeScript, Vite, TanStack Router/Query, Tailwind
CSS 4, and shadcn/Radix application. It currently presents authentication,
users, settings, administration, a superuser course-system setup workspace,
and the learner journey from public product explanation through multimode
course intake and owner-scoped live progress.

## Current Routes

| Route | Purpose |
|-------|---------|
| `/` | Public one-source-to-four-publications product story |
| `/login` | Login |
| `/signup` | Configured-access information or local registration |
| `/recover-password` | Password recovery |
| `/reset-password` | Password reset |
| `/create` | Authenticated prompt, text, URL, YouTube, or file intake |
| `/jobs/$jobId` | Authenticated owner-scoped progress and terminal handoff |
| `/settings` | User settings |
| `/setup` | Superuser course-system readiness, device login, and CLI recovery |
| `/admin` | Superuser administration |

Page titles and accessible product names use the shared
`src/lib/branding.ts` helper.

## Public Access Configuration

`VITE_ENABLE_PUBLIC_SIGNUP` controls only whether a build displays local
account-creation actions. It defaults to `false`. Compose derives that public
build value from the root `ENABLE_PUBLIC_SIGNUP` setting.

The frontend setting is not authorization. The backend remains authoritative
for every signup request and can reject disabled or revoked access even when a
previously built page still shows the action. Do not put secrets in any
`VITE_*` value because Vite embeds those values in browser assets.

## Course Intake and Progress

The `/create` workbench accepts exactly one source mode and optional learning
intent. Its centralized Zod schema mirrors the generated backend contract,
removes inactive fields, requires explicit AI/research-processing consent,
and never parses an uploaded document in the browser.

`src/hooks/useCourseSubmission.ts` owns canonical retry identity, duplicate
submission prevention, generated-client JSON/multipart calls, safe error copy,
and navigation from the accepted opaque job ID. Components must compose that
hook rather than rebuilding its logic.

`/jobs/$jobId` reads only the authenticated owner's generated status
projection. Active jobs use a visibility-aware polling policy; terminal jobs
stop polling. Refreshing or directly reopening the private URL revalidates the
server state. Missing and foreign-owned jobs deliberately share one recovery
surface.

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

The Compose frontend is available at <http://localhost:5183>. Common checks:

```bash
npm run test:unit
npm run typecheck
npm run lint
npm run build
npx playwright test
```

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
finite deterministic scenario:

```bash
docker compose up -d --wait db
cd frontend
npx playwright test --config playwright.jobs.config.ts
TXT2CRS_BROWSER_SCENARIO=failed \
  npx playwright test --config playwright.jobs.config.ts
```

Each dedicated run creates private engine state and a fresh normal user,
starts and stops its own backend and Vite processes, and cleans package
resources at application shutdown. It is test composition only; the
test-application factory fails closed unless its explicit test environment
flag is present.

Playwright output is written to ignored report/result directories. Stop the
stack with `docker compose down`; add `--volumes` only when intentionally
discarding local data.
