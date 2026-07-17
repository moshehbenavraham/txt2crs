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

The independently installable Python library is scaffolded under
[`backend/packages/txt2crs/`](backend/packages/txt2crs/). It uses a standard
`src` layout and can be developed, tested, and exported without a FastAPI or
React application.

The repository also contains the original
[Make.com proof-of-concept workflows](make-scenarios/) and the
[product and architecture documentation](docs/). The production library
behavior and application shell are the next stages of development.

## Repository Layout

```text
txt2crs/
├── backend/
│   ├── packages/
│   │   └── txt2crs/          # Independently installable Python library
│   └── tests/                # Future product-level acceptance tests
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
The current pre-release version is stored in [`VERSION`](VERSION), and the
release process is documented in
[`docs/VERSIONING.md`](docs/VERSIONING.md).
