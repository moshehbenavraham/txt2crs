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

## Next Reading

- [Development commands](development.md)
- [Architecture](ARCHITECTURE.md)
- [Environment behavior](environments.md)
- [Product requirements](../.spec_system/PRD/PRD.md)
