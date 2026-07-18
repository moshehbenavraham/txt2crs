# Contributing

## Branch Conventions

- `main` - Production-ready code
- `master` - Legacy default branch (synced with main)
- `feature/*` - New features
- `fix/*` - Bug fixes

## Commit Style

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add pagination to items endpoint
```

## Pull Request Process

1. Create feature branch from `main`
2. Make changes with clear commits
3. Run tests: `cd backend && bash scripts/test.sh`
4. Run backend checks: `cd backend && bash scripts/lint.sh`
5. Run frontend checks: `cd frontend && npm run lint && npm run typecheck`
6. Update documentation if needed
7. Open PR with description
8. Address review feedback
9. Squash and merge

Keep pull requests focused. Add or update tests whenever behavior changes, and
explain architectural or security tradeoffs in the pull request description.

## Dependency Changes

Changes to dependency manifests and lockfiles are restricted to repository
members and approved dependency bots. This includes:

- `backend/pyproject.toml` and `backend/uv.lock`
- `frontend/package.json` and `frontend/package-lock.json`

This policy limits software supply-chain risk and keeps dependency review
intentional. If you need a new dependency, open an issue first. Describe the
capability it provides, why existing dependencies are insufficient, its
maintenance and security posture, and the expected runtime or bundle cost.

Do not hand-edit lockfiles. Use `uv` for backend dependency changes and `npm`
for frontend dependency changes, then include the resulting lockfile update.

## Development Setup

```bash
# Backend
cd backend
uv sync
source .venv/bin/activate
fastapi dev app/main.py

# Frontend
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
# Backend unit tests
cd backend && bash scripts/test.sh

# Frontend e2e tests
cd frontend && npm run test:e2e
```

## Automated and AI-Assisted Contributions

Automation and AI tools are welcome when they support careful engineering.
The contributor remains responsible for every submitted line and must:

- Review generated changes for correctness, security, licensing, and scope.
- Run the relevant tests, linters, type checks, and generated-client check.
- Remove fabricated claims, stale assumptions, and unrelated generated edits.
- Explain the problem and important design decisions in their own words.
- Keep the review burden proportionate to the value of the change.

Do not submit unattended, bulk-generated, or speculative changes. Repeated
automated pull requests or comments that shift excessive verification work to
maintainers may be closed without review.

## Code Review Norms

- Review within 24 hours
- Be constructive and specific
- Approve when ready, request changes when not
- Use suggestions for minor changes
