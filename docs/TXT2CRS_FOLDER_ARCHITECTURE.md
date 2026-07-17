# txt2crs Folder Architecture

> Status: proposed standalone structure.
>
> The local `python-react-boilerplate` is a compatibility reference only. It is
> not a dependency and no boilerplate code is included in this structure.

## Goal

Build txt2crs as an installable Python package whose course-generation workflow
can run independently and later be mounted in FastAPI, connected to React, or
adapted to another application shell.

## Proposed structure

```text
txt2crs/
├── pyproject.toml
├── src/
│   └── txt2crs/
│       ├── domain/
│       │   ├── models.py
│       │   └── validation.py
│       ├── application/
│       │   ├── ports.py
│       │   ├── pipeline.py
│       │   └── job_service.py
│       ├── adapters/
│       │   ├── ai/
│       │   ├── ingestion/
│       │   ├── persistence/
│       │   ├── research/
│       │   └── rendering/
│       ├── interfaces/
│       │   └── fastapi/
│       ├── observability/
│       ├── security/
│       ├── evals/
│       └── bootstrap.py
├── tests/
│   ├── unit/
│   ├── contract/
│   ├── integration/
│   └── acceptance/
├── migrations/
└── docs/
```

Create folders only when their first tested behavior is implemented; the tree
is a responsibility map, not a requirement for empty packages.

## Responsibilities

| Folder | Owns |
|---|---|
| `domain/` | Versioned Pydantic models and deterministic invariants for inputs, evidence, courses, review packs, assessments, and jobs |
| `application/` | Use cases, staged orchestration, budgets, checkpoints, and protocols such as `ModelRuntime`, `ResearchToolService`, and `JobRepository` |
| `adapters/ai/` | Codex subscription runtime, fake runtime, event projection, retries, and usage capture |
| `adapters/research/` | Tavily, research MCP tools, evidence collection, source policy, and citation verification |
| `adapters/ingestion/` | Plain text, URL, PDF, document, audio, and video normalization |
| `adapters/persistence/` | SQLite job, checkpoint, artifact, and usage repositories |
| `adapters/rendering/` | Deterministic course, review-pack, assessment, and answer-sheet rendering |
| `interfaces/fastapi/` | Optional routers, API schemas, dependency wiring, and public progress streaming |
| `security/` | URL safety, policy enforcement, redaction, path confinement, and untrusted-content boundaries |
| `observability/` | Separate private diagnostic events and safe public progress events |
| `evals/` | Versioned evaluation cases, replay, deterministic checks, and rubric results |
| `bootstrap.py` | Composition root that selects adapters and constructs application services |

## Dependency rule

```text
FastAPI or another interface
          ↓
      application
          ↓
        domain
          ↑
 adapters implement application ports
```

- `domain/` must not import FastAPI, SQLite, Codex, Tavily, or SDK event types.
- `application/` depends on protocols, not concrete adapters.
- `bootstrap.py` is the only place that selects and wires concrete adapters.
- FastAPI request, authentication, database-session, and error types stop at the
  interface boundary.
- Tests use deterministic fake runtimes and repositories; live-provider tests
  remain explicitly gated.

## Future boilerplate fit

If `python-react-boilerplate` is selected later:

| txt2crs boundary | Boilerplate integration point |
|---|---|
| Installable core package | Added as a backend dependency without changing its internal layout |
| `interfaces/fastapi/` router | Registered from `backend/app/api/main.py` |
| Authentication and ownership | Adapted from boilerplate dependencies at the route boundary |
| Persistence port | SQLite can remain for local use or receive a SQLModel/PostgreSQL adapter |
| Public errors and logs | Mapped to the boilerplate's RFC 9457 errors and structured logging |
| API contracts | Included in OpenAPI and used to regenerate `frontend/src/client/` |
| React feature | Added later under routes, components, and hooks; no frontend code is required now |

The boilerplate's existing MCP server is an administrative developer tool. The
txt2crs research MCP service remains a separate, tightly allowlisted runtime
adapter exposing only approved research operations.

## Test placement

Tests are written before implementation:

- `unit/`: domain invariants, budgets, ranking, rendering, and safety helpers;
- `contract/`: runtime, repository, research-tool, schema, and event contracts;
- `integration/`: SQLite, Codex SDK fakes, Tavily HTTP fakes, and FastAPI;
- `acceptance/`: resumable end-to-end generation and donor-absence checks.

This structure keeps txt2crs independently testable today while preserving a
small, explicit integration surface for whichever application shell is chosen.
