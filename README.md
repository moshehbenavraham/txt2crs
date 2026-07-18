# txt2crs

txt2crs is an OpenAI + Devpost Education Hackathon project that turns a topic or
source material into a complete learning package:

- A deeply researched, source-grounded course
- Comprehensive review materials
- A full assessment with an answer key

## Origin Story

Two days after I joined OpenAI Build Week, my Zimbabwean wife asked me a simple,
powerful question: **“How can we bring AI to Africa?”**

Her question took me back to studying for my IBM AI Developer certification, when I
built a Make.com workflow to expand learning material, create study guides, and
generate review questions. Badda bing, badda boom—the question and that old experiment
clicked together, becoming the catalyst for txt2crs: a way to make rich, structured
learning experiences from almost any source material.

The application uses Python, FastAPI, a React frontend, an OpenAI subscription
runtime, and SQLite/PostgreSQL. Its workflow normalizes the learner's input,
researches and verifies reliable sources, builds the course, derives aligned
study materials and assessments, and delivers polished learning artifacts
through a clear, accessible interface.

## Current Status

The independently installable Python library under
[`backend/packages/txt2crs/`](backend/packages/txt2crs/) implements the
complete reusable education engine: bounded multi-input ingestion, deep
research and evidence, subscription-only Codex execution, per-module course
generation, aligned review and assessment artifacts, deterministic
HTML/Markdown/PDF/DOCX rendering, durable resume, private storage, spend
admission, and offline evaluation. It also includes an app-owned ChatGPT
device-code authentication service and temporary bootstrap entry point, so the
dedicated hackathon identity can be connected through the bundled runtime
without installing or configuring Codex separately.

The full-stack application shell (adapted from the AIwithApex
`python-react-boilerplate`, v0.1.41) is now merged into the repository:
FastAPI application under [`backend/app/`](backend/app/), React 19 frontend
under [`frontend/`](frontend/), and Docker Compose for local development. The
shell currently provides authentication, user management, and the boilerplate
demo domain; wiring the engine into course-generation routes and the learner
experience follows the
[input-to-course system plan](docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md).

The repository also contains the original Make.com proof-of-concept workflows
and their
[complete legacy-system reconstruction](make-scenarios/README_make.md), plus the
[product and architecture documentation](docs/).

## Quick Start

```bash
# Start the full stack with Docker Compose
docker compose up -d
```

Configuration comes from `.env` (copy [`.env.example`](.env.example) and set
`SECRET_KEY`, `POSTGRES_PASSWORD`, and `FIRST_SUPERUSER_PASSWORD`).

Backend and frontend development commands are documented in
[`backend/README_backend.md`](backend/README_backend.md) and
[`frontend/README_frontend.md`](frontend/README_frontend.md); the local
Docker workflow is in [`docs/development.md`](docs/development.md).

## Repository Layout

```text
txt2crs/
├── backend/
│   ├── app/                  # FastAPI application shell
│   ├── packages/
│   │   └── txt2crs/          # Independently installable education engine
│   └── tests/                # Application tests (+ acceptance/)
├── frontend/                 # React 19 + TypeScript frontend
├── examples/                 # Curated code examples (few-shot learning)
├── scripts/                  # Development and validation scripts
├── docs/                     # Project documentation
├── make-scenarios/           # Original Make.com proof of concept
├── docker-compose.yml
├── VERSION
└── README.md
```

Engine development and build commands are documented in
[`backend/packages/txt2crs/README_txt2crs.md`](backend/packages/txt2crs/README_txt2crs.md).

## Versioning

txt2crs follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The current version is stored in [`VERSION`](VERSION), and the release process
is documented in
[`docs/VERSIONING.md`](docs/VERSIONING.md).

## License

Licensing is scoped; see [`LICENSE`](LICENSE) for the repository-wide terms,
the boilerplate/upstream provenance notices, and the dedicated license of
`backend/packages/txt2crs/`.
