# Backend Dependencies

The backend targets Python 3.14. `pyproject.toml` defines supported direct
dependency ranges and `uv.lock` records the exact, reproducible environment.

## Runtime Dependencies

| Package | Supported range | Purpose |
|---------|-----------------|---------|
| `fastapi[standard]` | >=0.139.2, <1.0.0 | API framework, server, and CLI |
| `starlette` | >=1.3.1, <2.0.0 | ASGI framework used by FastAPI |
| `python-multipart` | >=0.0.32, <1.0.0 | Form and file upload parsing |
| `email-validator` | >=2.3.0, <3.0.0 | Email address validation |
| `pydantic` | >=2.13.4, <3.0.0 | Request, response, and domain validation |
| `pydantic-settings` | >=2.14.2, <3.0.0 | Typed environment configuration |
| `sqlmodel` | >=0.0.39, <1.0.0 | SQLAlchemy and Pydantic ORM models |
| `psycopg[binary]` | >=3.3.4, <4.0.0 | PostgreSQL driver |
| `alembic` | >=1.18.5, <2.0.0 | Database migrations |
| `pwdlib[argon2,bcrypt]` | >=0.3.0, <1.0.0 | Argon2id password hashing and bcrypt migration compatibility |
| `pyjwt` | >=2.13.0, <3.0.0 | JWT encoding and validation |
| `httpx` | >=0.28.1, <1.0.0 | HTTP client |
| `emails` | >=1.1.2, <2.0.0 | SMTP email construction and delivery |
| `jinja2` | >=3.1.6, <4.0.0 | Email template rendering |
| `tenacity` | >=9.1.4, <10.0.0 | Retry and backoff |
| `slowapi` | >=0.1.10, <1.0.0 | API rate limiting |
| `sentry-sdk[fastapi]` | >=2.66.0, <3.0.0 | Error and performance telemetry |
| `opentelemetry-api` | >=1.44.0, <2.0.0 | Tracing API |
| `opentelemetry-sdk` | >=1.44.0, <2.0.0 | Tracing implementation |
| `opentelemetry-exporter-otlp` | >=1.44.0, <2.0.0 | OTLP trace export |
| `opentelemetry-instrumentation-fastapi` | >=0.65b0, <1.0.0 | FastAPI tracing |
| `opentelemetry-instrumentation-sqlalchemy` | >=0.65b0, <1.0.0 | Database tracing |
| `opentelemetry-instrumentation-httpx` | >=0.65b0, <1.0.0 | Outbound HTTP tracing |
| `mcp` | >=1.28.1, <2.0.0 | Model Context Protocol server |

## Development Dependencies

| Package | Supported range | Purpose |
|---------|-----------------|---------|
| `httpx2` | >=2.7.0, <3.0.0 | Starlette/FastAPI test client transport |
| `pytest` | >=9.1.1, <10.0.0 | Test runner |
| `pytest-cov` | >=7.1.0, <8.0.0 | pytest coverage integration |
| `coverage` | >=7.15.2, <8.0.0 | Coverage collection and reporting |
| `mypy` | >=2.3.0, <3.0.0 | Strict static type checking |
| `ruff` | >=0.15.22, <1.0.0 | Python linting and formatting |
| `pre-commit` | >=4.6.0, <5.0.0 | Git hook orchestration |
| `hypothesis` | >=6.156.6, <7.0.0 | Property-based testing |

The PEP 517 build backend is `hatchling>=1.31.0,<2.0.0`.

## Password Hash Migration

New passwords are hashed with Argon2id through `pwdlib`. The configured bcrypt
hasher remains second in the verification chain so users with hashes created by
the former passlib implementation can still authenticate. A password change or
reset stores the new Argon2id format.

## Updating Dependencies

1. Update the lower bound in `pyproject.toml` to the current supported release.
2. Run `uv lock --upgrade` and `uv sync`.
3. Run `uv run ruff check app tests`, `uv run ruff format --check app tests`,
   `uv run mypy app`, and `uv run pytest`.
4. Update this document when a direct dependency or its role changes.

Upper bounds prevent an unreviewed future major release from silently entering
an environment; the lockfile pins every transitive package exactly.
