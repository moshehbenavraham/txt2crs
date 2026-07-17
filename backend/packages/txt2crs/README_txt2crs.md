# txt2crs Python Library

`txt2crs` is the reusable course-generation engine for the txt2crs education
application. It is designed to transform a topic or source into:

- a deeply researched course;
- comprehensive review materials;
- a complete assessment; and
- an answer key.

The package deliberately does not own React components, HTTP routing,
authentication, or FastAPI application startup. A future backend application
will import this package and adapt its services at the web boundary.

## Package layout

```text
txt2crs/
├── pyproject.toml
├── LICENSE
├── README_txt2crs.md
├── docs/
├── src/
│   └── txt2crs/
│       ├── domain/
│       ├── application/
│       ├── adapters/
│       ├── security/
│       ├── observability/
│       └── evals/
└── tests/
    ├── unit/
    ├── contract/
    └── integration/
```

The package uses the standard Python `src` layout. Tests are created before the
behavior they specify, and implementation folders remain placeholders until
their first tested behavior is introduced.

## Develop and test

From this package directory:

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy
```

## Build an exportable distribution

```bash
uv build
```

The command creates a source distribution and wheel under `dist/`. Those
artifacts contain the library and its package license without requiring the
future FastAPI or React applications.

Architecture and implementation research are indexed in
[`docs/README_txt2crs_docs.md`](docs/README_txt2crs_docs.md).
