# Phase Transition Tooling Audit

**Date:** 2026-07-19
**Result:** PASS
**Selected bundle:** none - validation only
**Scope:** `backend-shell`, `txt2crs-engine`, `frontend`, and repository root

## Detection

`bash .spec_system/scripts/analyze-project.sh --json` reported a monorepo with
three registered packages and no active session. All seven recommended bundles
already existed, so the audit adopted and validated the current tools instead
of installing a new bundle. No known-issues registry existed at detection
time.

## Package Results

| Package | Formatting | Linting | Types | Tests |
|---------|------------|---------|-------|-------|
| `backend` | Ruff PASS, 65 initially unchanged | Ruff PASS; typos PASS | mypy PASS; ty PASS after one SQLModel repair | 184 passed; 78% coverage |
| `backend/packages/txt2crs` | Ruff PASS, 16 files normalized | Ruff PASS; typos PASS with recorded fixture/regex exceptions | mypy PASS across 103 source files | 223 passed, 1 explicitly live-gated skip |
| `frontend` | Biome PASS, 124 files and no fixes | Biome PASS; typos PASS | TypeScript PASS | 18 Vitest and 70 Playwright tests passed |
| repository root | EOF, whitespace, TOML, YAML, case, size, typos, and Zizmor hooks PASS | pre-commit PASS | N/A | Compose startup PASS |

## Fixes Applied

1. Replaced an invalid SQLModel `sa_type=String(50)` instance with an explicit
   SQLAlchemy column. The database remains `VARCHAR(50)`, and both mypy and ty
   now pass without an ignore.
2. Added explicit private local error capture with a tested JSON schema,
   owner-only `0700` directory, and `0600` capture files.
3. Scoped EOF and spelling hooks away from generated Codex protocol fixtures,
   legacy Make.com exports, and deliberately noisy OCR input. Three ignored
   paths and two line-specific spelling exceptions are documented in
   `known-issues.md`; there are no ignored failing tests.
4. Normalized 16 previously unformatted engine files and verified the complete
   engine suite afterward.
5. Fixed the base Compose topology so container clients use PostgreSQL's
   internal port `5432` rather than the host mapping. A static regression test
   failed before the change and now passes.
6. Preserved Markdown hard breaks with explicit `<br>` elements while allowing
   the repository whitespace hook to remain deterministic.
7. Made client generation format `openapi.json` and `src/client` together, so
   the generate-client hook cannot leave a later Biome gate dirty.

## Evidence Ledger

| Bundle | Package | Command | Result | Fixes Applied | Remaining / Blocker |
|--------|---------|---------|--------|---------------|---------------------|
| Formatting | backend | `uv run ruff format app tests` | PASS | No files changed initially; one new test formatted later | None |
| Formatting | engine | `uv run --package txt2crs ruff format .` | PASS | 16 files normalized | None |
| Formatting / Linting | frontend | `npm run lint` | PASS | No fixes across 124 files | None |
| Linting | backend | `uv run ruff check --fix app tests` | PASS | None | None |
| Linting | engine | `uv run --package txt2crs ruff check --fix .` | PASS | None | None |
| Type Safety | backend | `uv run mypy app` | PASS | None | None |
| Type Safety | backend | `uv run ty check app` | PASS | Corrected the `content_type` SQLModel column | None |
| Type Safety | engine | `uv run --package txt2crs mypy` | PASS | None | None |
| Type Safety | frontend | `npm run typecheck` | PASS | None | None |
| Testing | backend | `uv run coverage run -m pytest tests/ -q` | PASS: 184; 78% | Added 2 error-capture tests, 1 Compose contract, and 1 generation contract | None |
| Testing | engine | `uv run --package txt2crs pytest` | PASS: 223, SKIP: 1 live provider test | None | None |
| Testing | frontend | `npm run test:unit` | PASS: 18 | None | None |
| Testing | frontend | `npx playwright test --reporter=line` with isolated service URLs | PASS: 70 | None | None |
| Observability | backend | `uv run pytest --confcutdir=tests/core tests/core/test_logging.py -q` | PASS: 2 | Added explicit local capture | None |
| Observability | backend | Trigger `write_last_error(...)`, then validate with `jq` | PASS | Created valid private capture | None |
| Git Hooks | root | `uv run pre-commit run --all-files` from `backend/` | PASS: all hooks | Repaired generated/reference exclusions and precise spelling exceptions | None |
| Database | backend | `uv run alembic upgrade head`, `check`, `downgrade -1`, `upgrade head`, `check` | PASS on PostgreSQL 18.4 | None | None |
| Database | backend | `uv run python app/initial_data.py` twice | PASS: one user after both runs | Confirmed idempotency | None |
| Dev Server | root | `docker compose config --quiet` | PASS | None | None |
| Dev Server | backend/frontend | `uv run fastapi run app/main.py --host 127.0.0.1 --port 18012` and `npm run dev -- --host 127.0.0.1 --port 15183 --strictPort` | PASS: health 0.3.3, login 200, title `txt2crs` | None | None |
| Dev Server | root | Isolated `docker compose up --detach`, health/import checks, then `docker compose down --volumes` | PASS: UID 1001, engine import, backend and frontend HTTP | Fixed internal PostgreSQL port | None |

## Known Issues Loaded

- Ignored paths: 3
- Ignored rules: 2
- Known failing tests: 0
- Skipped workflows: 0
- Skipped infrastructure: 0

All exceptions preserve generated/reference/evaluation semantics and satisfy
the audit no-deferral policy. No repository-fixable issue remains.

## Handoff

`audit -> pipeline` is the required Phase Transition handoff. `infra` follows
only after `pipeline`; the next implementation session is not planned until
the next phase is created through `phasebuild`.

**Next command:** `pipeline`
**Reason:** all seven configured bundles pass across every applicable package.
