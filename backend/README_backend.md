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
<http://localhost:8016/api/v1/openapi.json>.

| Area | Current endpoints |
|------|-------------------|
| Authentication | `/api/v1/login/access-token`, `/api/v1/login/test-token`, `/api/v1/password-recovery`, `/api/v1/reset-password/` |
| Users | `/api/v1/users/`, `/api/v1/users/me`, `/api/v1/users/me/password`, `/api/v1/users/signup`, `/api/v1/users/{user_id}` |
| Course jobs | `/api/v1/jobs`, `/api/v1/jobs/upload`, `/api/v1/jobs/{job_id}`, `/api/v1/jobs/{job_id}/artifacts`, `/api/v1/jobs/{job_id}/artifacts/{artifact_id}` |
| System | `/api/v1/system/readiness`, `/api/v1/system/auth/start`, `/api/v1/system/auth/status` |
| Operations | `/api/v1/utils/health/`, `/api/v1/utils/health-check/`, `/api/v1/utils/test-email/` |

Course requests are accepted into the engine's durable tenant-scoped job
store. Status, result, manifest, and artifact reads are owner-scoped and
served through the public package facade.

Self-service and administrator account deletion call the engine's owner purge
before deleting the PostgreSQL user. Purge cancels and joins matching work,
removes private artifacts, and deletes engine job state. A purge failure
returns `USER_2007` and leaves the user row intact so the operation can be
retried safely.

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

- Database health: `GET /api/v1/utils/health/` checks PostgreSQL and returns version.
- Liveness: `GET /api/v1/utils/health-check/` proves the process responds.
- Course readiness: authenticated `GET /api/v1/system/readiness` returns only
  the latest cached provider/research/storage/worker/input/admission state.
  Browser reads never run the underlying probes.

## Dedicated-System Authentication

The engine provides `DedicatedSystemAuthenticator` and the temporary
`txt2crs-system-auth` command. Both use the app-server binary bundled by the
pinned Python dependency; no separate Codex installation is required.

Superusers can call `POST /api/v1/system/auth/start` and poll
`GET /api/v1/system/auth/status`. The browser receives only the validated
OpenAI verification URL, short user code, finite state, and safe recovery
message. The temporary CLI remains the recovery path:

```bash
cd backend/packages/txt2crs
uv run --package txt2crs txt2crs-system-auth
```

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
Revision `a7d9c2e4f601` removed the retired donor table; its downgrade restores
only that historical table schema because deleted donor rows are
irrecoverable.

## Email Templates

MJML sources live under `app/email-templates/src/`; generated HTML lives under
`app/email-templates/build/`.
