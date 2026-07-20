# txt2crs Frontend

The frontend is a React 19, TypeScript, Vite, TanStack Router/Query, Tailwind
CSS 4, and shadcn/Radix application. It currently presents authentication,
users, settings, administration, a superuser course-system setup workspace,
and a learner-facing course workspace that explains the four-part generated
learning package. Submission and live progress routes arrive in Phase 04.

## Current Routes

| Route | Purpose |
|-------|---------|
| `/` | Authenticated course workspace |
| `/login` | Login |
| `/signup` | Registration |
| `/recover-password` | Password recovery |
| `/reset-password` | Password reset |
| `/settings` | User settings |
| `/setup` | Superuser course-system readiness, device login, and CLI recovery |
| `/admin` | Superuser administration |

Page titles and accessible product names use the shared
`src/lib/branding.ts` helper.

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
manually.

## Source Structure

```text
frontend/src/
|-- client/          # Generated OpenAPI client
|-- components/      # Product and shadcn/Radix components
|-- hooks/           # Application hooks
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

Playwright output is written to ignored report/result directories. Stop the
stack with `docker compose down`; add `--volumes` only when intentionally
discarding local data.
