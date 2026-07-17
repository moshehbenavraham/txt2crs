# txt2crs Backend Workspace

The backend is a `uv` workspace that currently contains the independently
installable txt2crs course-generation library:

```text
backend/
├── pyproject.toml
├── uv.lock
├── packages/
│   └── txt2crs/
└── tests/
    └── acceptance/
```

The library lives in [`packages/txt2crs/`](packages/txt2crs/) so it can be
built, tested, and exported without the future web application.

## Future FastAPI integration

If the selected React/FastAPI boilerplate is adopted, its `backend/app/`
application will be added beside `packages/`. The application will depend on
the local `txt2crs` workspace package and own HTTP routes, authentication,
SQLModel application tables, Alembic migrations, and API-specific tests.

The boilerplate Dockerfile must copy `packages/` before installing the workspace
so the library is available inside the backend image.

## Development commands

Run these commands from `backend/`:

```bash
uv sync --all-packages
uv run --package txt2crs pytest
uv build --package txt2crs
```

Package-specific instructions are in
[`packages/txt2crs/README_txt2crs.md`](packages/txt2crs/README_txt2crs.md).
