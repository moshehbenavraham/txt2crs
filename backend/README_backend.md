# txt2crs Backend

The backend is one `uv` workspace containing two responsibilities:

```text
backend/
├── pyproject.toml            # Application-shell project + workspace root
├── uv.lock
├── app/                      # FastAPI application shell (routes, auth, DB)
├── alembic.ini               # Application database migrations
├── scripts/                  # Backend test/lint/format scripts
├── packages/
│   └── txt2crs/              # Independently installable education engine
└── tests/                    # Application tests (+ acceptance/)
```

The application shell owns HTTP routes, user authentication, SQLModel
application tables, and Alembic migrations. The txt2crs engine in
[`packages/txt2crs/`](packages/txt2crs/) owns AI, research, ingestion,
validation, rendering, durable jobs, safety, and evaluation behavior; the
shell consumes it as a workspace dependency and must not duplicate it.

## Development commands

From `backend/`:

```bash
uv sync --all-packages                 # Install shell + engine
uv run pytest tests/ -v                # Application tests
uv run mypy app                        # Type-check the shell
uv run ruff check app                  # Lint the shell
uv run --package txt2crs pytest        # Engine test suite
uv build --package txt2crs             # Build the engine distribution
```

Engine-specific instructions are in
[`packages/txt2crs/README_txt2crs.md`](packages/txt2crs/README_txt2crs.md).

## API endpoints (current shell)

All endpoints require JWT authentication (except login/signup).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/login/access-token` | POST | Get JWT token |
| `/api/v1/login/test-token` | POST | Validate token |
| `/api/v1/password-recovery/{email}` | POST | Password reset request |
| `/api/v1/users/` | GET | List users (admin) |
| `/api/v1/users/me` | GET/PATCH/DELETE | Current user |
| `/api/v1/users/signup` | POST | User registration |
| `/api/v1/items/` | GET/POST | Boilerplate demo domain (donor for jobs) |
| `/api/v1/items/{id}` | GET/PUT/DELETE | Boilerplate demo domain (donor for jobs) |

The `items` routes are the boilerplate demo domain kept as the donor for the
course-generation `jobs` domain; see
[`../docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md`](../docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md).

## Key files

| File | Purpose |
|------|---------|
| `app/api/routes/` | Endpoint handlers |
| `app/schemas/` | Pydantic request/response models |
| `app/models.py` | SQLModel database models |
| `app/core/config.py` | Settings and configuration |
| `app/core/security.py` | JWT and password handling |
| `app/api/deps.py` | Dependency injection |

## Dedicated-system authentication

The engine exposes a framework-independent Codex device-code authentication
service (`DedicatedSystemAuthenticator`) and a temporary
`txt2crs-system-auth` console entry point. Both launch the app-server binary
bundled by the Python dependency; neither requires a developer or end user to
install/configure Codex.

The console entry point remains only until the FastAPI setup routes exist.
Those routes will call the same service, and the frontend will display the
verification URL, user code, and safe status.

## Docker Compose

Start the local development environment with Docker Compose following
[`../docs/development.md`](../docs/development.md). The backend Dockerfile
copies `packages/` before installing the workspace so the engine is available
inside the image.

During development, `docker-compose.override.yml` provides volume mounts for
live reloading and `fastapi run --reload`. To access the container:

```bash
docker compose exec backend bash
```

## Tests in Docker

```bash
bash ./scripts/test.sh                             # Full stack test run
docker compose exec backend bash scripts/tests-start.sh    # Running stack
docker compose exec backend bash scripts/tests-start.sh -x # Extra pytest args
```

After tests run, open `htmlcov/index.html` for the coverage report.

## Migrations

With the container running (`docker compose exec backend bash`):

```bash
alembic revision --autogenerate -m "Add column to User model"
alembic upgrade head
```

## Email templates

Email templates are in `app/email-templates/`:

- `src/` - MJML source files
- `build/` - Compiled HTML templates

Use the [MJML VS Code extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml)
to convert `.mjml` files to HTML.
