# txt2crs Development

## One-Command Stack

```bash
docker compose up -d --wait
```

Use `docker compose watch` when you want Compose file-watch rebuild/sync
behavior. Stop the stack without deleting application data:

```bash
docker compose down
```

## Local Service Endpoints

Host tools use published ports. Containers use service names and internal
ports.

| Service | Host address | Container address |
|---------|--------------|-------------------|
| Frontend | <http://localhost:5183> | `frontend:80` |
| Frontend health | <http://localhost:5183/health> | `frontend:80/health` |
| Backend API | <http://localhost:8012> | `backend:8000` |
| Backend readiness | <http://localhost:8012/api/v1/utils/health/> | `backend:8000/api/v1/utils/health/` |
| Swagger UI | <http://localhost:8012/docs> | `backend:8000/docs` |
| PostgreSQL | `localhost:5447` | `db:5432` |
| Adminer | <http://localhost:8096> | `adminer:8080` |
| Mailcatcher UI | <http://localhost:1081> | `mailcatcher:1080` |
| Mailcatcher SMTP | `localhost:1026` | `mailcatcher:1025` |
| Traefik dashboard | <http://localhost:8095> | `proxy:8080` |
| Jaeger UI | <http://localhost:16686> | `jaeger:16686` |

The local proxy dashboard is available, but the Docker provider is disabled
in `docker-compose.override.yml`. Use the published localhost ports above
instead of expecting `*.localhost.tiangolo.com` routing.

## Logs and Health

```bash
docker compose ps
docker compose logs backend
curl --fail http://localhost:8012/api/v1/utils/health/
curl --fail http://localhost:5183/health
```

The backend readiness response includes PostgreSQL health and release version.
The frontend response proves Nginx is serving without loading React.

## Develop One Service on the Host

Stop only the service you want to replace.

### Backend

```bash
docker compose stop backend
cd backend
uv sync --all-packages
uv run fastapi dev app/main.py
```

The host backend reads `backend/.env`; it reaches PostgreSQL through
`localhost:5447`.

### Frontend

```bash
docker compose stop frontend
cd frontend
npm ci
npm run dev
```

The dev server uses the port configured in `frontend/vite.config.ts`.

## Private Engine State

The container backend mounts one named volume at `/var/lib/txt2crs`:

```text
/var/lib/txt2crs/
|-- jobs.sqlite3
|-- artifacts/
`-- codex-home/
```

The runtime user owns these paths with private modes. Worker scratch data is
ephemeral under `/tmp/txt2crs-worker`. The research MCP port is not published.
Do not add replicas or multiple FastAPI workers while this serial SQLite
topology remains.

Complete backup and restore commands are documented in
[Local deployment](local-deploy.md#backup-and-restore). The backup briefly
stops the backend writer and captures PostgreSQL plus all durable private
engine state. It omits only Codex's regenerable `codex-home/tmp` process
scratch; the legacy `scripts/backup-db.sh` is not sufficient by itself.

## Mailcatcher

Local Compose routes application email to `mailcatcher:1025`. View captured
messages at <http://localhost:1081>; no external email is sent.

## Validation

Run the credential-free fast gate from the repository root:

```bash
./scripts/validate-changes.sh
```

Selectors can narrow feedback:

```bash
./scripts/validate-changes.sh backend
./scripts/validate-changes.sh engine
./scripts/validate-changes.sh frontend
./scripts/validate-changes.sh --json
```

### Backend shell

```bash
cd backend
uv run pytest tests/ -v
uv run mypy app
uv run ty check app
uv run ruff check app tests
uv run ruff format --check app tests
```

The full suite needs PostgreSQL. Start `db` first or run it inside the
full-stack Compose environment.

### Reusable engine

Run from the engine package directory so its own `pyproject.toml` applies:

```bash
cd backend/packages/txt2crs
uv run --package txt2crs pytest
uv run --package txt2crs ruff check .
uv run --package txt2crs mypy
```

The default suite is network-free. The live Codex acceptance check requires
the explicit `TXT2CRS_RUN_LIVE_CODEX=1` gate.

### Frontend

```bash
cd frontend
npm run test:unit
npm run typecheck
npm run lint
npm run build
npx playwright test
```

### Containers

```bash
docker compose config --quiet
./scripts/verify-production-baseline.sh
```

The production-like local baseline smoke builds the backend target, imports
the engine as UID 1001, checks private modes, and reopens state through a
replacement container.

## Pre-commit

Pre-commit is installed in the backend development environment:

```bash
cd backend
uv run pre-commit install
uv run pre-commit run --all-files
```

The hooks cover file hygiene, spelling, Python lint/format/types, frontend
Biome/TypeScript, deterministic client generation, and workflow security.

## Generated Client

After backend API changes:

```bash
./scripts/generate-client.sh
git diff -- frontend/openapi.json frontend/src/client
```

The script exports OpenAPI and formats both generated surfaces. Never edit
`frontend/src/client/` manually.

## Environment and Deployment

- [Configuration catalog](CONFIGURATION.md)
- [Environment behavior](environments.md)
- [Deployment policy](deployment-policy.md)
- [Local deployment](deployment.md)
