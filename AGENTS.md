# AGENTS.md - Coding Agent's Instructions / Rules

## Project

This is an education product that originated during OpenAI Build Week.
The goal is to provide a solution with a beautiful interface
that accepts any input and will deliver: 1) A full deep-researched course
based on the input, 2) Create comprehensive review materials on that generated
course, and 3) Generate a full test with answer sheet.

The current product requirements and completed phase plan are
[`.spec_system/PRD/PRD.md`](.spec_system/PRD/PRD.md).
The reusable AI engine lives in `backend/packages/txt2crs/`; the
FastAPI/React application shell (adapted from the AIwithApex
`python-react-boilerplate`) composes it and must not duplicate its logic.

## Critical Rules

In no particular order.

- Add generous code-comments as if a 1st year Computer-Science intern has to
  navigate / work in the code.
- Use descriptive variable names and function names that clearly explain their
  purpose.
- README.md filename is reserved for the root README file. All other
  appropriate / relevant project folders should have a README named in the
  form of README_<appropriate-name>.md - example: docs/ has README_docs.md.
- Avoid over-engineering while still following best practices and industry
  standards.
- Create the tests before the code.
- Record completed tracked work under the appropriate release section in
  `docs/CHANGELOG.md`.
- Once `docs/CHANGELOG.md` gets roughly 20+ entries, archive it to
  `docs/archive/CHANGELOG_YYYYMMDD.md` and create a new empty
  `docs/CHANGELOG.md`.
- Follow `docs/VERSIONING.md` and keep `VERSION` synchronized with each release.
- Application database changes require Alembic migrations.
- Environment variables go in `.env` (never commit secrets).
- Use error codes from `app.core.constants.ErrorCode` for all shell errors.
- All log events follow the naming pattern `{domain}.{action}_{state}`.
- Route handlers call the txt2crs package boundary; never reimplement
  generation, research, validation, persistence, or rendering in the shell.

## Tech Stack

- **Backend**: Python 3.14, FastAPI, SQLModel, Pydantic v2, PostgreSQL 18
  (application) + tenant-scoped SQLite (engine job store)
- **Engine**: `txt2crs` workspace package - OpenAI subscription (Codex)
  runtime, research MCP, deterministic rendering
- **Frontend**: React 19, TypeScript 7, TanStack Router/Query, Tailwind CSS 4,
  Zod, shadcn/ui
- **Tools**: uv, Docker Compose, Traefik, Alembic, pytest, Playwright

## Directory Structure

```
|-- backend/
|   |-- app/              # FastAPI application shell
|   |   |-- api/routes/   # API endpoint handlers
|   |   |-- core/         # Config, security, DB setup, logging, errors
|   |   |-- mcp/          # Admin MCP server (AI agent tools)
|   |   |-- schemas/      # Pydantic request/response models
|   |   |-- models.py     # SQLModel database models
|   |   `-- crud.py       # Database operations
|   |-- packages/txt2crs/ # Education engine (own docs, tests, license)
|   `-- tests/            # Application tests (+ acceptance/)
|-- frontend/src/
|   |-- routes/           # File-based routing (TanStack Router)
|   |-- components/       # React components
|   |-- client/           # Generated OpenAPI client (DO NOT EDIT)
|   |-- hooks/            # Custom React hooks
|   `-- lib/              # Shared utilities
|       |-- schemas/      # Centralized Zod validation schemas
|       `-- types/        # Branded types (UserId, ItemId, Email)
|-- examples/             # Curated code examples (few-shot learning)
|-- scripts/              # Development and validation scripts
|-- docs/                 # Documentation (see docs/README_docs.md)
`-- make-scenarios/       # Legacy Make.com reconstruction (reference)
```

Detailed per-side guidance: [`backend/AGENTS.md`](backend/AGENTS.md) and
[`frontend/AGENTS.md`](frontend/AGENTS.md).

## Build & Test Commands

```bash
# Backend shell (from backend/)
uv sync --all-packages                         # Install shell + engine
POSTGRES_DB=app_test uv run pytest tests/ -v   # Pre-provisioned test DB only
uv run mypy app                                # Type check
uv run ruff check app                          # Lint
uv run ruff format app                         # Format
uv run alembic upgrade head                    # Run migrations

# Engine (from backend/packages/txt2crs/ -- the engine's own pyproject
# config must apply; backend/pyproject.toml excludes packages/)
uv run --package txt2crs pytest                # Engine test suite
uv run --package txt2crs ruff check .
uv run --package txt2crs mypy

# Frontend (from frontend/)
npm run dev                                    # Development server
npm run build                                  # Production build
npm run lint                                   # Lint with Biome
npm run typecheck                              # TypeScript type check
npm run generate-client                        # Regenerate API client
npx playwright test                            # E2E tests

# Docker (preferred for the full stack)
docker compose up -d                           # Start all services
./scripts/validate-changes.sh                  # Credential-free fast gate
```

The full backend suite deletes application-owned rows during fixture cleanup.
It refuses ordinary database names; provision and migrate a database whose
name starts with `test_` or ends with `_test` before running it.

## Coding Conventions

### Backend (Python)

- Use type hints everywhere; mypy strict mode is enforced
- Use `Annotated` types for FastAPI dependencies
- Pydantic models for all request/response bodies
- SQLModel for database models (combines SQLAlchemy + Pydantic)
- Use UUID for all primary keys
- Rate limiting via slowapi (disabled in local env)
- Use constants from `app.core.constants` (never hardcode error codes, HTTP
  status, etc.)
- Raise `AppException` with `ErrorCode` for structured errors (RFC 9457)
- Use structured logging via `app.core.logging.get_logger()`

### Frontend (TypeScript)

- File-based routing with TanStack Router
- TanStack Query for server state (use suspense queries)
- Zod schemas for runtime validation
- React Hook Form for form handling
- shadcn/ui + Tailwind for styling
- Never edit files in `src/client/` - they're auto-generated
- Use `handleApiError()` utility for consistent error handling

## Type Safety Patterns

### Backend: Strict Pydantic Models

All API request models use strict validation to reject unknown fields:

```python
from app.models import _STRICT_REQUEST_CONFIG

class MyRequestModel(SQLModel):
    """Request models reject extra fields."""
    model_config = _STRICT_REQUEST_CONFIG  # type: ignore[assignment]

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
```

Strict config: `extra="forbid"`, `validate_default=True`,
`str_strip_whitespace=True`. Apply to all `Create`, `Update`, and input
models; response (`Public`) models do not need it.

### Frontend: Centralized Zod Schemas

Validation schemas live in `frontend/src/lib/schemas/` and mirror backend
Pydantic rules exactly. Field schema naming: `{fieldName}Field` for required,
`{fieldName}FieldOptional` for optional.

### Frontend: Branded Types

Branded types in `frontend/src/lib/types/` prevent mixing up similar ID
types (`UserId`, `ItemId`, `Email`). Factory functions
(`createUserId()`, ...) validate and throw; `as*()` casts are for trusted API
responses only.

## Error Handling

Backend: raise `AppException` with an `ErrorCode`; all API errors follow RFC
9457 Problem Details with a `trace_id`. Frontend: global handling in
`src/main.tsx` (auth errors redirect to `/login`); component-level handling
uses `try/catch` with toast notifications.

## Logging Standards

Structured JSON logging with trace ID correlation:

```python
logger.info("user.registration_completed", extra={"user_id": str(user.id)})
```

Event states: `_started`, `_completed`, `_failed`, `_validated`, `_rejected`,
`_retrying`.

## Distributed Tracing (OpenTelemetry)

```bash
OTEL_ENABLED=true docker compose up -d   # Traces at http://localhost:16689
```

Traced: FastAPI HTTP requests, SQLAlchemy queries, HTTPX calls. Trace IDs
appear in logs and error responses.

## MCP Servers (two separate boundaries)

- The **admin MCP server** (`backend/app/mcp/`) exposes read-only database
  and validation tools for AI coding agents. Run standalone:
  `cd backend && uv run python -m app.mcp.server`. Keep it disabled in
  deployment.
- The engine's **research MCP server** (loopback, inside
  `packages/txt2crs/`) is a runtime security boundary for course generation.
  Never merge or cross-wire the two.

## Context Profiles

`.context-profiles.yaml` defines task-specific context profiles
(frontend-feature, backend-api, database-migration, testing-backend, ...) to
reduce token overhead. Reference a profile in your prompt when useful.

## Key Files Reference

| Purpose | File Location |
|---------|---------------|
| Error codes | `backend/app/core/constants.py` |
| Structured logging | `backend/app/core/logging.py` |
| Custom exceptions | `backend/app/core/exceptions.py` |
| App configuration | `backend/app/core/config.py` |
| Database models | `backend/app/models.py` |
| CRUD operations | `backend/app/crud.py` |
| API routes | `backend/app/api/routes/` |
| Engine public docs | `backend/packages/txt2crs/README_txt2crs.md` |
| Generated API client | `frontend/src/client/` (DO NOT EDIT) |
| Zod schemas (FE) | `frontend/src/lib/schemas/` |
| Branded types (FE) | `frontend/src/lib/types/` |
| Admin MCP server | `backend/app/mcp/server.py` |
| Context profiles | `.context-profiles.yaml` |

## Architecture Decisions

See `docs/adr/` for boilerplate Architecture Decision Records and
`docs/TXT2CRS_FOLDER_ARCHITECTURE.md` for the workspace/dependency rules.
