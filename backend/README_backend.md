# txt2crs Backend

The backend is one uv workspace with two intentionally separate
responsibilities:

```text
backend/
|-- app/                    # FastAPI application shell
|-- packages/txt2crs/       # Reusable education engine
|-- tests/                  # Shell and acceptance tests
|-- pyproject.toml          # Shell project and workspace root
|-- uv.lock
`-- alembic.ini
```

The shell owns HTTP, user authentication, SQLModel application data, Alembic,
configuration, lifecycle, observability, and error translation. The engine
owns generation, research, ingestion, policy, validation, durable jobs,
recovery, private artifacts, rendering, and evaluation. Shell routes must call
the public package facade instead of duplicating engine logic.

## Development Commands

Run from `backend/` unless noted:

```bash
uv sync --all-packages
uv run pytest tests/ -v
uv run mypy app
uv run ty check app
uv run ruff check app tests
uv run ruff format --check app tests
```

Run engine checks from `packages/txt2crs/` so its own project configuration
applies:

```bash
cd packages/txt2crs
uv run --package txt2crs pytest
uv run --package txt2crs ruff check .
uv run --package txt2crs mypy
uv build --package txt2crs
```

## Current API

The application OpenAPI document is authoritative:
<http://localhost:8012/api/v1/openapi.json>.

| Area | Current endpoints |
|------|-------------------|
| Authentication | `/api/v1/login/access-token`, `/api/v1/login/test-token`, `/api/v1/password-recovery`, `/api/v1/reset-password/` |
| Users | `/api/v1/users/`, `/api/v1/users/me`, `/api/v1/users/me/password`, `/api/v1/users/signup`, `/api/v1/users/{user_id}` |
| Temporary donor domain | `/api/v1/items/`, `/api/v1/items/{id}` |
| Operations | `/api/v1/utils/health/`, `/api/v1/utils/health-check/`, `/api/v1/utils/test-email/` |

Course-generation routes do not exist yet. The `items` domain remains until
durable jobs acceptance coverage protects the Phase 03 migration.

All shell errors use RFC 9457 Problem Details with stable error codes and trace
IDs. See [`../docs/api/README_api.md`](../docs/api/README_api.md).

## Container and State Topology

Both backend image targets:

- install the workspace-owned `txt2crs` package;
- run one FastAPI process as UID/GID 1001;
- create owner-only state, artifact, Codex-home, and worker directories; and
- keep the research MCP port unpublished.

Compose mounts one backend volume at `/var/lib/txt2crs`:

```text
/var/lib/txt2crs/
|-- jobs.sqlite3
|-- artifacts/
`-- codex-home/
```

This fixed image-owned mount is separate from PostgreSQL. Multiple backend
workers or replicas are unsupported while the serial worker and SQLite
topology remain.

## Health

- Readiness: `GET /api/v1/utils/health/` checks PostgreSQL and returns version.
- Liveness: `GET /api/v1/utils/health-check/` proves the process responds.

Phase 02 will add engine/provider/storage/worker capability readiness before
new generation work can be admitted.

## Dedicated-System Authentication

The engine provides `DedicatedSystemAuthenticator` and the temporary
`txt2crs-system-auth` command. Both use the app-server binary bundled by the
pinned Python dependency; no separate Codex installation is required.

The temporary command is replaced when the FastAPI setup routes and operator
screen call the same package service.

## Docker and Database

```bash
# From the repository root
docker compose up -d --wait
docker compose exec backend bash
```

Migrations:

```bash
cd backend
uv run alembic upgrade head
uv run alembic check
```

Application database changes require a new reversible Alembic revision.

## Email Templates

MJML sources live under `app/email-templates/src/`; generated HTML lives under
`app/email-templates/build/`.
