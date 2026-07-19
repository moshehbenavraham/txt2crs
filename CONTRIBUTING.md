# Contributing

## Start Here

Follow the root [`AGENTS.md`](AGENTS.md) and the package-specific guidance in
[`backend/AGENTS.md`](backend/AGENTS.md) or
[`frontend/AGENTS.md`](frontend/AGENTS.md). The architecture boundary is
strict: the shell calls the public `txt2crs` package facade and does not
duplicate engine behavior.

## Branch and Commit Conventions

- Branches use `type/short-description`, for example
  `feat/job-submission`.
- Commit subjects use concise imperative language, for example
  `Add job submission validation`.
- Keep commits focused enough to review and revert safely.

## Required Workflow

1. Create tests before implementation.
2. Make the smallest source-backed change.
3. Run the repository fast gate:

   ```bash
   ./scripts/validate-changes.sh
   ```

4. Run the relevant database, browser, or container checks from
   [`docs/development.md`](docs/development.md).
5. Regenerate the OpenAPI client through `./scripts/generate-client.sh` after
   backend API changes. Never edit `frontend/src/client/` manually.
6. Update the applicable documentation and changelog/TODO records.
7. Open a focused pull request explaining what changed, why, and how it was
   validated.

## Package Commands

```bash
# Backend shell
cd backend
uv sync --all-packages
uv run pytest tests/ -v
uv run mypy app
uv run ruff check app tests

# Reusable engine (run from its package directory)
cd packages/txt2crs
uv run --package txt2crs pytest
uv run --package txt2crs ruff check .
uv run --package txt2crs mypy

# Frontend
cd ../../../frontend
npm ci
npm run test:unit
npm run lint
npm run typecheck
```

## Dependency Changes

Dependency manifests and lockfiles change together:

- Python: `backend/pyproject.toml`, engine `pyproject.toml`, and
  `backend/uv.lock`
- JavaScript: `frontend/package.json` and `frontend/package-lock.json`

Do not hand-edit lockfiles. Explain why a dependency is necessary, its
maintenance/security posture, and its runtime or bundle cost.

## Pull Request and Review Norms

- Keep the scope small and preserve unrelated worktree changes.
- Include tests for observable behavior and negative paths.
- Document security, privacy, migration, or deployment tradeoffs.
- Address actionable review feedback and keep generated files deterministic.
- Review code, not people; distinguish required fixes from optional ideas.
