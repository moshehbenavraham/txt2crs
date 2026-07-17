# txt2crs Folder Architecture

> Status: adopted library-first backend workspace.
>
> The local `python-react-boilerplate` remains a compatibility reference rather
> than a dependency. Its application shell can be added later without moving
> the txt2crs library.

## Goal

Build txt2crs as an independently installable Python distribution while placing
it inside the future backend's Docker and dependency boundary. The library can
therefore be tested, built, tagged, and exported on its own or consumed by a
React/FastAPI application in the same repository.

## Adopted structure

```text
txt2crs/
├── backend/
│   ├── pyproject.toml                  # Virtual uv workspace today
│   ├── uv.lock                         # Reproducible workspace environment
│   ├── README_backend.md
│   ├── packages/
│   │   ├── README_packages.md
│   │   └── txt2crs/
│   │       ├── pyproject.toml          # Independent distribution metadata
│   │       ├── README_txt2crs.md
│   │       ├── LICENSE
│   │       ├── docs/
│   │       │   └── README_txt2crs_docs.md
│   │       ├── src/
│   │       │   └── txt2crs/
│   │       │       ├── domain/
│   │       │       ├── application/
│   │       │       ├── adapters/
│   │       │       │   ├── ai/
│   │       │       │   ├── ingestion/
│   │       │       │   ├── persistence/
│   │       │       │   ├── research/
│   │       │       │   └── rendering/
│   │       │       ├── observability/
│   │       │       ├── security/
│   │       │       └── evals/
│   │       └── tests/
│   │           ├── unit/
│   │           ├── contract/
│   │           └── integration/
│   └── tests/
│       └── acceptance/                 # Future product-level tests
├── docs/
├── make-scenarios/
├── VERSION
└── README.md
```

The future `backend/app/`, application migrations, and `frontend/` directories
will be created only when the full-stack boilerplate is adopted. The tree is a
responsibility map, not permission to add untested placeholder behavior.

## Library responsibilities

| Folder | Owns |
|---|---|
| `domain/` | Versioned models and deterministic invariants for inputs, evidence, courses, review packs, assessments, and jobs |
| `application/` | Framework-independent use cases, staged orchestration, budgets, checkpoints, and provider/repository protocols |
| `adapters/ai/` | Codex subscription runtime, deterministic fake runtime, event projection, retries, and usage capture |
| `adapters/research/` | Research tools, evidence collection, source policy, and citation verification |
| `adapters/ingestion/` | Plain text, URL, PDF, document, audio, and video normalization |
| `adapters/persistence/` | Independently useful repository implementations, such as local SQLite |
| `adapters/rendering/` | Deterministic course, review-pack, assessment, and answer-sheet rendering |
| `security/` | URL safety, policy enforcement, redaction, path confinement, and untrusted-content boundaries |
| `observability/` | Private diagnostic events and safe public progress-event contracts |
| `evals/` | Versioned evaluation cases, replay, deterministic checks, and rubric results |

## Dependency rule

```text
Future React client
        ↓ HTTP
Future FastAPI application shell
        ↓
txt2crs application services
        ↓
txt2crs domain
        ↑
txt2crs adapters implement application ports
```

- `domain/` must not import FastAPI, SQLite, Codex, Tavily, or SDK event types.
- `application/` depends on local protocols rather than concrete adapters.
- The library must not import the future `backend/app/` package.
- FastAPI requests, authentication, application database sessions, public API
  errors, and Alembic migrations stop at the application-shell boundary.
- The future application composition root selects concrete txt2crs adapters
  and supplies authenticated ownership context.
- Live-provider tests remain explicitly gated; default tests use deterministic
  fakes.

## Interim authentication boundary

The full FastAPI/frontend shell does not exist yet, but subscription
authentication cannot depend on a developer's preinstalled Codex environment.
The adopted interim boundary is therefore:

```text
temporary packaged bootstrap (future: FastAPI setup page)
        ↓ URL + user code + safe status
txt2crs DedicatedSystemAuthenticator
        ↓ public Python SDK
bundled Codex app-server
        ↓ device-code authentication
dedicated ChatGPT hackathon identity
```

- The app starts `chatgptDeviceCode`; it never implements OpenAI token exchange.
- The UI receives only the verification URL, short user code, and safe state.
- Codex alone stores and refreshes credentials in an application-owned
  `CODEX_HOME`.
- ChatGPT login is forced, API-key environment values are blanked for the child,
  and the credential store is pinned to the isolated filesystem directory.
- The temporary console entry point is replaced by setup routes/UI when
  `backend/app/` is adopted; the library service remains reusable.

## Future boilerplate integration

When `python-react-boilerplate` is selected:

1. Merge its backend project metadata into `backend/pyproject.toml` while
   retaining `[tool.uv.workspace]`.
2. Declare `txt2crs` as a workspace dependency of the backend application.
3. Add the boilerplate's FastAPI code under `backend/app/`.
4. Register course-generation routes from `backend/app/api/main.py`.
5. Keep user authentication, system-authentication HTTP routes, SQLModel
   application tables, and Alembic migrations under the application shell;
   those routes call the framework-independent `DedicatedSystemAuthenticator`.
6. Update the backend Dockerfile to copy `packages/` before workspace
   installation. Its existing `./backend` build context can remain unchanged.
7. Add the React application under the repository-root `frontend/` directory
   and regenerate its API client from the combined OpenAPI contract.

The expected local dependency direction is:

```text
backend/app/api/routes/courses.py
                ↓ imports
backend/packages/txt2crs/src/txt2crs/
```

The boilerplate's administrative MCP server and the txt2crs research-tool
adapter remain separate security boundaries.

## Test placement

Tests are written before implementation:

- package `unit/`: domain invariants, budgets, ranking, rendering, and safety
  helpers;
- package `contract/`: runtime, repository, research-tool, schema, and event
  contracts;
- package `integration/`: SQLite, Codex SDK fakes, research HTTP fakes, and
  other independently useful adapter integrations;
- backend `acceptance/`: future authenticated API, resumable end-to-end
  generation, delivery, and frontend-facing behavior.

## Packaging, versions, and export

`backend/packages/txt2crs/pyproject.toml` builds the independent wheel and source
distribution. From `backend/`, use:

```bash
uv sync --all-packages
uv run --package txt2crs pytest
uv build --package txt2crs
```

The root `VERSION` remains the repository's Semantic Versioning source. The
package metadata uses the equivalent normalized PEP 440 spelling. The current
repository and package release is `0.2.1`.

An immutable annotated Git tag plus the built wheel and source distribution
preserve a standalone-library milestone before full-stack integration begins.
