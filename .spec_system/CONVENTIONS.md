# CONVENTIONS.md

## Guiding Principles

- Optimize for readability over cleverness
- Code is written once, read many times
- Consistency beats personal preference
- If it can be automated, automate it
- When writing code: Make NO assumptions. Do not be lazy. Pattern match precisely. Do not skim when you need detailed info from documents. Validate systematically.

## Naming

- Python modules, variables, and functions use `snake_case`; classes and
  Pydantic or SQLModel contracts use `PascalCase`.
- TypeScript variables and functions use `camelCase`; React components and
  exported types use `PascalCase`; route files follow TanStack conventions.
- Booleans read as questions, such as `is_active`, `hasPermission`, or
  `should_retry`.
- Prefer descriptive domain names; only universally understood abbreviations
  such as `id`, `url`, and `config` are acceptable.

## Files & Structure

- Keep reusable engine logic under `backend/packages/txt2crs/`; the FastAPI
  shell must not reimplement it.
- Put shell routes under `backend/app/api/routes/`, schemas under
  `backend/app/schemas/`, and composition services under
  `backend/app/services/`.
- Put frontend routes under `frontend/src/routes/`, centralized Zod schemas
  under `frontend/src/lib/schemas/`, and branded types under
  `frontend/src/lib/types/`.
- Never edit `frontend/src/client/` manually; regenerate it from OpenAPI.
- Reserve `README.md` for the repository root; use descriptive
  `README_<subject>.md` names elsewhere.

## Functions & Modules

- Add complete Python type annotations and keep mypy strict checks green.
- Use `Annotated` FastAPI dependencies and strict Pydantic request contracts.
- Keep functions cohesive and make resource ownership, transactions, and
  side effects explicit.
- Prefer moderately sized modules; split files that accumulate unrelated
  responsibilities or grow beyond roughly 400-600 lines.

## Comments

- Add generous comments that help a first-year computer-science intern follow
  non-obvious control flow, boundaries, and security decisions.
- Explain why a constraint or decision exists; descriptive names should carry
  the obvious what.
- Delete commented-out code and keep comments synchronized with behavior.
- TODOs include context, ownership, and a specification or issue when one
  exists.

## Error Handling

- Shell errors use `AppException` plus an `app.core.constants.ErrorCode` and
  RFC 9457 Problem Details with trace IDs.
- Engine errors remain typed at the public package boundary; the shell maps
  them centrally without exposing provider or filesystem details.
- Never swallow failures; preserve cleanup and transaction guarantees before
  translating errors.
- All structured log events use `{domain}.{action}_{state}` and exclude
  secrets, PII, input content, provider payloads, artifact bytes, and paths.

## Database Layer

### Connection
- Connection string source: `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`; never hardcode credentials
- Application, migrations, and tests use explicit environment-driven connection settings

### Migrations
- Tool: Alembic | Location: `backend/app/alembic/versions/` | Naming: descriptive revision modules
- Never modify a migration already applied to shared environments
- Every migration must implement both upgrade and downgrade behavior

### Models / Schema
- Location: `backend/app/models.py` | Naming: SQLModel domain names and snake_case SQL tables

### Queries
- Use parameterized SQLModel/SQLAlchemy queries only
- Keep transaction boundaries explicit for multi-step writes

### Seeding
- Initial superuser seeding lives in `backend/app/initial_data.py` and must be idempotent

### Testing
- Application tests use isolated fixtures under `backend/tests/`; engine persistence tests use tenant-scoped SQLite stores

## Testing

- Create failing tests before implementation code and name tests for observable
  scenarios and expectations.
- Engine tests run from `backend/packages/txt2crs/` so the package's own
  pyproject configuration applies.
- Backend tests run from `backend/`; frontend behavior uses Playwright under
  `frontend/tests/`.
- Default validation is deterministic, credential-free, and network-free;
  live Codex checks require an explicit environment gate.
- Flaky tests are fixed or removed, never ignored.

## Python

- Use Ruff for formatting and linting and keep imports automatically ordered.
- Use Pydantic v2 models for external contracts and `extra="forbid"` on
  create, update, and other input models.
- Use UUID primary keys for PostgreSQL application models.
- Use context managers or `try/finally` for every acquired process, listener,
  stream, file, and temporary resource.

## TypeScript and React

- Keep `strict` TypeScript checks green and validate untrusted runtime data
  with centralized Zod schemas.
- Use TanStack Query for server state and suspense queries where repository
  patterns call for them.
- Use React Hook Form with Zod resolvers for forms and `handleApiError()` for
  consistent API failure handling.
- Use shadcn/Radix primitives and Tailwind CSS 4 while preserving semantic
  HTML, visible focus, keyboard support, reduced motion, and responsive
  behavior.
- Do not expose implementation diagnostics on learner-facing routes.

## Git & Version Control

- Commit messages: imperative mood, concise (`Add user validation` not `Added some validation stuff`)
- One logical change per commit
- Branch names: `type/short-description` (for example, `feat/user-auth`)
- Keep commits atomic enough to revert safely

## Pull Requests

- Small PRs get better reviews
- Descriptions explain the what and why
- Link relevant tickets or specifications
- Review changes locally before requesting review

## CI/CD

Platform: GitHub Actions. Workflows use least-privilege job permissions,
immutable third-party action commits, path-aware triggers where useful, and
concurrency cancellation for repeated branch validation.

| Bundle | Status | Workflows | Strategy |
|--------|--------|-----------|----------|
| Code Quality | Configured | `quality.yml` | Ruff, mypy, ty, Biome, TypeScript, backend tests, and the reusable engine suite feed one required quality gate. |
| Build & Test | Configured | `quality.yml`, `test-backend.yml`, `test-docker-compose.yml`, `playwright.yml`, `generate-client.yml` | Test the shell, engine, generated contract, production Compose topology, and browser behavior. |
| Security | Configured | `security.yml`, `zizmor.yml`, `guard-dependencies.yml` | Scan Git history, CodeQL languages, pull-request dependencies, Python/JavaScript advisories, and workflow supply-chain safety. |
| Integration | Configured | `playwright.yml`, `test-docker-compose.yml`, `detect-conflicts.yml` | Exercise service boundaries and browser flows, then flag merge conflicts without checking out untrusted pull-request code. |
| Operations | Configured | `deploy-coolify.yml`, `deploy-staging.yml`, `deploy-production.yml`, `backup-db.yml` | Separate environment deployments from scheduled/manual PostgreSQL backups. |

### CI Secrets

No secret values belong in source control. The repository currently has no
configured Actions secrets; operators provision only the names required by
the workflow they enable.

| Workflow | Required secret names |
|----------|-----------------------|
| `backup-db.yml` | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` |
| `deploy-coolify.yml` | `COOLIFY_API_TOKEN`, `COOLIFY_API_URL`, `BACKEND_APP_UUID`, `FRONTEND_APP_UUID` |
| `deploy-staging.yml` | `DOMAIN_STAGING`, `STACK_NAME_STAGING`, `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`, `POSTGRES_PASSWORD`, `SENTRY_DSN` |
| `deploy-production.yml` | `DOMAIN_PRODUCTION`, `STACK_NAME_PRODUCTION`, `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`, `POSTGRES_PASSWORD`, `SENTRY_DSN` |
| `generate-client.yml` | `FULL_STACK_FASTAPI_TEMPLATE_REPO_TOKEN` for its optional upstream-template push |

`GITHUB_TOKEN` in `security.yml` is the automatic per-run token and is not a
manually provisioned repository secret. Current GitHub-hosted execution is
recorded under `.spec_system/audit/known-issues.md` until Actions billing is
restored; local equivalents remain mandatory before publishing.

## Code Review

- Critique code, not people; raise concrete concerns
- Approve when the change meets requirements; label optional suggestions

## Dependencies

- Manage Python dependencies with uv and JavaScript dependencies with npm.
- Keep `backend/uv.lock` and `frontend/package-lock.json` synchronized with
  their manifests.
- Prefer focused, maintained dependencies and document why each addition is
  necessary.

## Local Dev Tools

| Category | Tool | Config |
|----------|------|--------|
| Formatter | Ruff and Biome | `backend/pyproject.toml`, `frontend/biome.json` |
| Linter | Ruff, Biome, and typos | `backend/pyproject.toml`, `frontend/biome.json`, `_typos.toml` |
| Type Safety | mypy, ty, and TypeScript | `backend/pyproject.toml`, `frontend/tsconfig.json` |
| Testing | pytest, coverage, Vitest, and Playwright | `backend/pyproject.toml`, `frontend/package.json`, `frontend/playwright.config.ts` |
| Observability | Structured logging, private local error capture, and OpenTelemetry | `backend/app/core/logging.py`, `backend/app/core/telemetry.py`, `logs/.gitignore` |
| Git Hooks | pre-commit | `.pre-commit-config.yaml` |
| Database | PostgreSQL, SQLite, Alembic | `docker-compose.yml`, `backend/alembic.ini` |
| Dev Server | Docker Compose | `docker compose up -d` using `docker-compose.yml` and `docker-compose.override.yml` |

## Workspace Structure

| Package | Path | Stack | Formatter | Linter | Types | Tests |
|---------|------|-------|-----------|--------|-------|-------|
| backend-shell | `backend` | Python 3.14, FastAPI, SQLModel, PostgreSQL | Ruff | Ruff and typos | mypy and ty | pytest and coverage |
| txt2crs-engine | `backend/packages/txt2crs` | Python 3.14, Pydantic v2, SQLite | Ruff | Ruff and typos | mypy | pytest |
| frontend | `frontend` | React 19, TypeScript, Vite, Tailwind CSS | Biome | Biome and typos | TypeScript | Vitest and Playwright |

### Cross-Package Rules

- The FastAPI shell depends on the public `txt2crs` package facade; it never
  imports private engine modules or rebuilds the executor graph.
- The generated OpenAPI client is the frontend contract; regenerate it after
  backend API changes instead of hand-writing a parallel client.
- Each package owns its unit tests; cross-boundary acceptance tests live under
  `backend/tests/acceptance/` and browser E2E tests under `frontend/tests/`.
- Cross-package sessions name the primary package and justify every secondary
  package file in implementation notes.

### Database Ownership

| Database | Owner Package | Type | Shared By |
|----------|---------------|------|-----------|
| Application users | `backend` | PostgreSQL 18 | FastAPI shell only |
| Generation jobs | `backend/packages/txt2crs` | Tenant-scoped SQLite | Public engine facade |

- Alembic migrations live in `backend/app/alembic/versions/`.
- Engine SQLite migrations live in the engine package and are never
  reconstructed by the FastAPI shell.
- PostgreSQL does not shadow the P0 generation job state machine.

## When In Doubt

- Decide from repository evidence and document the assumption
- Leave it better than you found it
- Ship, learn, iterate
