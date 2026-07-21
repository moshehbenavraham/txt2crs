# Onboarding

Use this checklist for a clean local setup.

## Prerequisites

- [ ] Git with SSH access to the repository
- [ ] Bash (Git Bash is sufficient on Windows)
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
`FIRST_SUPERUSER_PASSWORD`. Set `TAVILY_API_KEY` for the default
research-enabled judge journey. Generate independent values:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Never commit `.env`.

### 3. Start the full stack

```bash
./scripts/start-local.sh
```

The command validates the environment, Docker runtime, Compose topology, and
published ports before it builds and starts PostgreSQL, database
migrations/seed, one backend process, the Nginx frontend, Mailcatcher, and
local support services. It delegates startup and health waiting to the
repository-root Docker Compose topology.

### 4. Verify

```bash
./scripts/start-local.sh --status
curl --fail http://localhost:8016/api/v1/utils/health/
curl --fail http://localhost:5195/health
```

- Frontend: <http://localhost:5195>
- Backend docs: <http://localhost:8016/docs>
- Mailcatcher: <http://localhost:1084>
- PostgreSQL for host tools: `localhost:5450`

Log in with `FIRST_SUPERUSER` and the configured
`FIRST_SUPERUSER_PASSWORD`.

### 5. Complete course-system setup

Open <http://localhost:5195/setup> as the initial superuser. The protected
workspace shows the latest cached storage, worker, research, model, input, and
admission checks. Use its ChatGPT connection action to authenticate the
dedicated application identity. Configure `TAVILY_API_KEY` in `.env` when
research should be ready, then restart the backend so it reads the new secret.

If browser device authentication is unavailable, use the short host recovery
helper shown on the setup page:

```bash
./scripts/auth-codex.sh --no-browser
```

The backend accepts authenticated course submissions and owner-scoped
result/artifact reads. The public `/` route explains the four generated
publications.
Authenticated learners create a request at `/create` and can refresh or
directly reopen the owner-scoped `/jobs/{job_id}` progress URL. Completed
jobs transform that same URL into four private publication folios for the
course, review pack, assessment, and separate instructor answer key. Each
publication offers PDF plus HTML, Markdown, and DOCX downloads from the
generated authenticated client.

HTML previews are limited by the non-secret
`VITE_HTML_PREVIEW_MAX_BYTES` build setting (default `5242880`, or 5 MiB).
Eligible HTML is verified, sanitized, and supplied as iframe `srcdoc` in an
empty-capability sandbox with a restrictive preview-only CSP. No object URL is
created. The frontend value controls presentation only; backend authorization,
integrity, and delivery limits remain authoritative.

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
POSTGRES_DB=app_test uv run pytest tests/ -v
```

Provision and migrate `app_test` separately first. The suite deletes
application-owned fixture rows and refuses the normal local `app` database.

For browser tests against the running stack:

```bash
cd frontend
npx playwright test
```

For the isolated provider-free course journey, use the dedicated
configuration. It creates run-owned SQLite stores and does not use the local
PostgreSQL database:

```bash
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
lsof -i :5195
lsof -i :8016
lsof -i :5450
```

Stop only the conflicting project or change the local published port. Do not
delete unrelated containers or volumes.

### PostgreSQL is unavailable

```bash
docker compose up -d db
docker compose logs db
```

Containers use `db:5432`; the host-only port `5450` must not be passed to
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
