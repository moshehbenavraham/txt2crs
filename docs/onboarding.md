# Onboarding

Use this checklist for a clean local setup.

## Prerequisites

- [ ] Git with SSH access to the repository
- [ ] Docker Engine/Desktop with Compose v2
- [ ] Python 3.14 and [uv](https://docs.astral.sh/uv/)
- [ ] Node.js 26.5+ and npm 12

## Setup

### 1. Clone

```bash
git clone git@github.com:moshehbenavraham/txt2crs.git
cd txt2crs
```

### 2. Configure local secrets

```bash
cp .env.example .env
```

Replace at least `SECRET_KEY`, `POSTGRES_PASSWORD`, and
`FIRST_SUPERUSER_PASSWORD`. Generate independent values:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Never commit `.env`.

### 3. Start the full stack

```bash
docker compose up -d --wait
```

The command starts PostgreSQL, database migrations/seed, one backend process,
the Nginx frontend, Mailcatcher, and local support services.

### 4. Verify

```bash
curl --fail http://localhost:8012/api/v1/utils/health/
curl --fail http://localhost:5183/health
```

- Frontend: <http://localhost:5183>
- Backend docs: <http://localhost:8012/docs>
- Mailcatcher: <http://localhost:1081>
- PostgreSQL for host tools: `localhost:5447`

Log in with `FIRST_SUPERUSER` and the configured
`FIRST_SUPERUSER_PASSWORD`.

### 5. Complete course-system setup

Open <http://localhost:5183/setup> as the initial superuser. The protected
workspace shows the latest cached storage, worker, research, model, input, and
admission checks. Use its ChatGPT connection action to authenticate the
dedicated application identity. Configure `TAVILY_API_KEY` in `.env` when
research should be ready, then restart the backend so it reads the new secret.

If browser device authentication is unavailable, use the recovery command
shown on the setup page from `backend/packages/txt2crs/`. The Phase 03 backend
accepts authenticated course submissions and owner-scoped result/artifact
reads. The public `/` route explains the four generated publications.
Authenticated learners create a request at `/create` and can refresh or
directly reopen the owner-scoped `/jobs/{job_id}` progress URL. Completed
jobs transform that same URL into four private publication folios for the
course, review pack, assessment, and separate instructor answer key. Each
publication offers PDF plus HTML, Markdown, and DOCX downloads from the
generated authenticated client.

HTML previews are limited by the non-secret
`VITE_HTML_PREVIEW_MAX_BYTES` build setting (default `5242880`, or 5 MiB).
Eligible HTML is verified and displayed from a revocable Blob URL in an
empty-capability sandboxed iframe with a restrictive preview-only CSP. The
frontend value controls presentation only; backend authorization, integrity,
and delivery limits remain authoritative.

Public account creation is disabled by default. Set
`ENABLE_PUBLIC_SIGNUP=true` only for a local installation that should accept
signup, then rebuild/restart the frontend and backend:

```bash
ENABLE_PUBLIC_SIGNUP=true docker compose up -d --build backend frontend
```

The frontend flag controls visible access copy; the backend still authorizes
the request. Because `VITE_*` values are public browser build data, never put a
secret in them.

## Manual Development

Keep PostgreSQL and Mailcatcher in Docker:

```bash
docker compose up -d db mailcatcher
```

Run the backend:

```bash
cd backend
uv sync --all-packages
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

Run the frontend in another terminal:

```bash
cd frontend
npm ci
npm run dev
```

## Validate the Checkout

```bash
./scripts/validate-changes.sh
```

For the PostgreSQL-backed shell suite:

```bash
cd backend
uv run pytest tests/ -v
```

For browser tests against the running stack:

```bash
cd frontend
npx playwright test
```

For the isolated provider-free course journey, keep PostgreSQL running and use
the dedicated configuration:

```bash
docker compose up -d --wait db
cd frontend
npx playwright test --config playwright.jobs.config.ts
TXT2CRS_BROWSER_SCENARIO=failed \
  npx playwright test --config playwright.jobs.config.ts
```

The dedicated test application uses the normal authentication, job routes,
serial worker, and generated frontend client with a finite deterministic
engine scenario. Its completed run checks all 16 manifest entries, real
artifact transfers, exact size labels, hostile HTML isolation, keyboard and
focus behavior, and responsive reflow. It is unavailable unless its test-only
process flag is explicitly set by the Playwright configuration.

## Common Problems

### A published port is already in use

```bash
docker compose ps
lsof -i :5183
lsof -i :8012
lsof -i :5447
```

Stop only the conflicting project or change the local published port. Do not
delete unrelated containers or volumes.

### PostgreSQL is unavailable

```bash
docker compose up -d db
docker compose logs db
```

Containers use `db:5432`; the host-only port `5447` must not be passed to
container services.

### The generated client is stale

```bash
./scripts/generate-client.sh
git diff -- frontend/openapi.json frontend/src/client
```

Generation owns those files. Do not edit `frontend/src/client/` manually.
TanStack route generation similarly owns `frontend/src/routeTree.gen.ts`; run
the frontend build after route changes.

### A course source appears to be retained in the browser

The intake preview is local and bounded. Uploaded files are not parsed, source
content is not placed in URLs or `localStorage`, and the optional pre-login
prompt handoff uses `sessionStorage`. Do not translate those browser choices
into claims about server retention, third-party provider policy, or regulatory
compliance; consult the deployment's actual policies instead.

## Next Reading

- [Development commands](development.md)
- [Architecture](ARCHITECTURE.md)
- [Environment behavior](environments.md)
- [Product requirements](../.spec_system/PRD/PRD.md)
