# txt2crs

txt2crs is an OpenAI + Devpost Education Hackathon project that turns one
topic or bounded source into a complete learning package:

- A deeply researched, source-grounded course
- Comprehensive review materials
- A student assessment
- A separate instructor answer key

## Origin Story

Two days after I joined OpenAI Build Week, my Zimbabwean wife asked me a
simple, powerful question: **"How can we bring AI to Africa?"**

Her question brought me back to an IBM AI Developer certification project: a
Make.com workflow that expanded learning material, created study guides, and
generated review questions. That experiment became the catalyst for txt2crs,
a way to make rich, structured learning experiences from almost any bounded
source.

## Current Status

Phases 00 and 01 are complete. The backend images install the workspace-owned
engine, run one non-root FastAPI process, and persist private SQLite job state,
artifacts, and Codex-managed credentials under one owner-only state root. The
frontend and backend have independent container health probes.

The independently installable engine at
[`backend/packages/txt2crs/`](backend/packages/txt2crs/) already owns bounded
ingestion, research, Codex execution, course generation, review and assessment
creation, deterministic rendering, durable recovery, policy, private
artifacts, owner erasure, and evaluation. Its public application facade now
supports strict real and deterministic factories, durable submission and
recovery, safe job/artifact reads, exact GPT-5.6 policy, managed provider
lifecycles, and owner purge. The FastAPI shell currently exposes
authentication, users, health, and the temporary donor `items` domain;
course-generation HTTP routes do not exist yet.

See the
[input-to-course system plan](docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md)
and the [product requirements](.spec_system/PRD/PRD.md) for the verified
delivery sequence.

## Quick Start

```bash
cp .env.example .env
# Replace SECRET_KEY, POSTGRES_PASSWORD, and FIRST_SUPERUSER_PASSWORD.
docker compose up --detach --build --wait
```

The frontend is available at <http://localhost:5183> and the backend API at
<http://localhost:8012>. Stop the stack without deleting persistent volumes:

```bash
docker compose down
```

Detailed setup and validation are in
[`docs/onboarding.md`](docs/onboarding.md) and
[`docs/development.md`](docs/development.md).

## Repository Layout

```text
txt2crs/
|-- backend/
|   |-- app/                    # FastAPI application shell
|   |-- packages/txt2crs/       # Reusable education engine
|   `-- tests/                  # Shell and acceptance tests
|-- frontend/                   # React 19 + TypeScript application
|-- examples/                   # Curated few-shot examples
|-- scripts/                    # Development and validation commands
|-- docs/                       # Project and delivery documentation
|-- make-scenarios/             # Legacy Make.com proof of concept
|-- docker-compose.yml
|-- VERSION
`-- README.md
```

## Packages

| Package | Path | Purpose |
|---------|------|---------|
| backend-shell | [`backend/`](backend/) | HTTP, identity, PostgreSQL, configuration, lifecycle, and error translation |
| txt2crs-engine | [`backend/packages/txt2crs/`](backend/packages/txt2crs/) | Generation, research, policy, jobs, recovery, artifacts, and rendering |
| frontend | [`frontend/`](frontend/) | Public and authenticated learner/operator experience |

Package commands are documented in
[`backend/README_backend.md`](backend/README_backend.md),
[`backend/packages/txt2crs/README_txt2crs.md`](backend/packages/txt2crs/README_txt2crs.md),
and [`frontend/README_frontend.md`](frontend/README_frontend.md).

## Validate Changes

```bash
./scripts/validate-changes.sh
```

This credential-free fast gate covers backend and engine lint, types, focused
shell contracts, the complete engine suite, and frontend lint/types. Database,
browser, image, and full-stack commands are listed in the development guide.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Configuration](docs/CONFIGURATION.md)
- [Environment behavior](docs/environments.md)
- [Deployment policy](docs/deployment-policy.md)
- [API](docs/api/README_api.md)
- [Contributing](CONTRIBUTING.md)

## Versioning and License

The current release is stored in [`VERSION`](VERSION) and follows
[Semantic Versioning](docs/VERSIONING.md). Licensing is scoped; see
[`LICENSE`](LICENSE) and the engine package's dedicated license and notices.
