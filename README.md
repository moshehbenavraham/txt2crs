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

The planned application uses Python, FastAPI, an OpenAI subscription runtime, and
SQLite. Its target workflow normalizes the learner's input, researches and verifies
reliable sources, builds the course, derives aligned study materials and assessments,
and delivers polished learning artifacts through a clear, accessible interface.

## Current Status

The independently installable Python library under
[`backend/packages/txt2crs/`](backend/packages/txt2crs/) now implements the
complete reusable education engine: bounded multi-input ingestion, deep
research and evidence, subscription-only Codex execution, per-module course
generation, aligned review and assessment artifacts, deterministic
HTML/Markdown/PDF/DOCX rendering, durable resume, private storage, spend
admission, and offline evaluation. It also includes an app-owned ChatGPT
device-code authentication service and temporary bootstrap entry point, so the
dedicated hackathon identity can be connected through the bundled runtime
without installing or configuring Codex separately.

The repository also contains the original Make.com proof-of-concept workflows
and their
[complete legacy-system reconstruction](make-scenarios/README_make.md), plus the
[product and architecture documentation](docs/). The FastAPI/frontend
application shell remains a separate next stage. It will provide browser
authentication, payment/entitlement checks, HTTP routes, and the user
interface while calling the completed package boundary.

## Repository Layout

```text
txt2crs/
├── backend/
│   ├── packages/
│   │   └── txt2crs/          # Independently installable Python library
│   └── tests/                # Future application-shell acceptance tests
├── docs/                     # Project documentation
├── make-scenarios/           # Original Make.com proof of concept
├── VERSION
└── README.md
```

If the selected React/FastAPI boilerplate is adopted, its backend application
will be added beside the library under `backend/app/`, and its frontend will be
added at the repository root under `frontend/`. The library will not need to
move.

Library development and build commands are documented in
[`backend/packages/txt2crs/README_txt2crs.md`](backend/packages/txt2crs/README_txt2crs.md).

## Versioning

txt2crs follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The current version is stored in [`VERSION`](VERSION), and the release process
is documented in
[`docs/VERSIONING.md`](docs/VERSIONING.md).
