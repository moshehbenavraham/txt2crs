# txt2crs Workspace Architecture

> Status: adopted library-first monorepo with a FastAPI/React application
> shell.

## Goal

Keep the education engine independently installable while the FastAPI and
React application provide authentication, delivery, and product UI. The shell
composes the engine; it does not duplicate engine behavior.

## Current Structure

```text
backend/
|-- app/                            FastAPI application shell
|-- packages/txt2crs/
|   |-- src/txt2crs/
|   |   |-- domain/                 Models and deterministic invariants
|   |   |-- application/            Use cases, ports, and orchestration
|   |   |-- adapters/               External runtime implementations
|   |   |-- ai/                     Codex subscription runtime
|   |   |-- ingestion/              Input normalization
|   |   |-- jobs/                   Job state and persistence
|   |   |-- research/               Evidence collection and citation policy
|   |   |-- rendering/              Deterministic deliverables
|   |   |-- security/               Untrusted-input and path boundaries
|   |   |-- observability/          Private and public events
|   |   `-- evals/                  Versioned quality cases
|   `-- tests/
|       |-- unit/
|       |-- contract/
|       |-- integration/
|       `-- acceptance/
`-- tests/                           Shell and product acceptance tests
```

The package has its own `pyproject.toml`, documentation, license, tests, and
build metadata. `backend/pyproject.toml` declares it as a uv workspace member
and application dependency.

## Dependency Direction

```text
React client
    |
    | HTTP
    v
FastAPI application shell
    |
    | public txt2crs package API
    v
txt2crs application services
    |
    v
txt2crs domain
    ^
    | protocols implemented by adapters
```

- The engine does not import `backend/app`.
- Domain code does not import FastAPI, SQLite, Codex, or provider SDK events.
- Application services depend on protocols, not concrete adapters.
- FastAPI owns users, authorization, public schemas, SQLModel sessions,
  Alembic migrations, shell error codes, and HTTP delivery.
- The engine owns generation, research, validation, engine job persistence,
  rendering, and evaluation.
- The administrative MCP server and engine research MCP boundary remain
  separate.

Authenticated course-generation submission, status, manifest, and artifact
routes are exposed through the FastAPI shell. They invoke only the public
package facade and query handles; transport code does not recreate generation,
research, validation, persistence, recovery, or rendering behavior.

## State and Authentication

PostgreSQL stores application users and shell records. Tenant-scoped engine
jobs use SQLite under `/var/lib/txt2crs/jobs.sqlite3`; rendered artifacts and
the isolated Codex home are sibling children of `/var/lib/txt2crs`. Temporary
worker files stay under `/tmp/txt2crs-worker`.

Codex performs ChatGPT device-code authentication and stores credentials only
in the application-owned Codex home. The public UI may receive a verification
URL, short code, and safe state, but never raw credentials or provider event
payloads.

## Test and Build Boundaries

Tests are written before implementation:

- engine unit tests cover pure invariants and helpers;
- engine contract tests cover ports, schemas, and events;
- engine integration tests cover SQLite and deterministic provider fakes;
- backend tests cover shell behavior and authenticated API composition;
- frontend unit and Playwright tests cover product behavior.

Run package commands from `backend/packages/txt2crs/` so its strict tool
configuration applies:

```bash
uv run --package txt2crs pytest
uv run --package txt2crs ruff check .
uv run --package txt2crs mypy
uv build --package txt2crs
```

The root `VERSION` is the repository SemVer source. Release changes synchronize
the package version and follow [Versioning](VERSIONING.md).
