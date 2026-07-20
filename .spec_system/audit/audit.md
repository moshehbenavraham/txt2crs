# Phase 05 Transition Tooling Audit

**Date:** 2026-07-20
**Revision:** `a8c5dbf76879eb8d87be8b35ea019677e5df31c9`
**Result:** PASS
**Selected bundle:** none - validation only
**Scope:** `backend-shell`, `txt2crs-engine`, `frontend`, and repository root

## Detection

`bash .spec_system/scripts/analyze-project.sh --json` reported a mixed-stack
monorepo with three registered packages, all six phases complete, no active
session, and all 18 sessions complete. `.spec_system/CONVENTIONS.md` already
records all seven recommended tooling bundles, so this run added no new tool
and validated every configured tool in the final committed product state.

The known-issues registry was loaded before validation. It contains three
ignored paths, three exact ignored-rule entries, no known failing test, ten
billing-blocked remote workflows, and no skipped infrastructure.

## Configured Bundle Matrix

| Bundle | Backend Shell | Engine | Frontend | Root |
|--------|---------------|--------|----------|------|
| Formatting | Ruff format | Ruff format | Biome | EOF and whitespace hooks |
| Linting | Ruff and typos | Ruff and typos | Biome and typos | Pre-commit routing |
| Type Safety | mypy and ty | mypy | TypeScript | N/A |
| Testing | pytest and coverage | pytest | Vitest and Playwright | cross-package validation |
| Observability | structured logging, private capture, OpenTelemetry | safe facade events | product-safe error handling | ignored private `logs/` captures |
| Git Hooks | pre-commit hooks | pre-commit hooks | pre-commit hooks | executable repository hook |
| Database | Alembic, SQLModel, PostgreSQL seed/tests | tenant-scoped SQLite tests | N/A | isolated PostgreSQL 18 |

## Package Results

| Package | Formatting And Linting | Types | Tests And Build |
|---------|------------------------|-------|-----------------|
| `backend` | Ruff and repository hooks PASS; 112 files unchanged | mypy strict and ty PASS | 517 pytest tests PASS at 88% coverage |
| `backend/packages/txt2crs` | Ruff and repository hooks PASS; 138 files unchanged | mypy PASS | 489 pytest tests PASS; 2 explicit live-provider skips |
| `frontend` | Biome PASS; 158 files checked with no fix | TypeScript PASS | 132 Vitest PASS; all 69 runnable broad browser cases PASS; complete and failed deterministic journeys pass 16 each; 2,215-module production build PASS |
| repository root | large-file, case, TOML, YAML, EOF, whitespace, typos, generated-client, and Zizmor hooks PASS | N/A | Compose config, isolated service startup, health, database, and resource cleanup PASS |

## Repairs Applied

No repository repair, dependency installation, configuration change, or new
tooling was required.

Four command-context corrections were made:

1. The default Compose startup could not bind port 5447 because an unrelated
   long-running `python-react-boilerplate` stack already owns it. The partial
   new stack was removed, then the current app started as isolated
   `txt2crs-audit` services without disturbing the existing stack.
2. The first broad Playwright attempt targeted that stale long-running stack,
   whose stored superuser password no longer matched current `.env`; its setup
   login was rejected. The suite was moved to a fresh isolated stack.
3. The first isolated broad run omitted the explicit public-signup test flag.
   It passed 57 tests with 11 intended job-fixture skips and failed 12
   sign-up-dependent cases. Enabling the flag in both backend and Vite made
   the complete sign-up/reset group pass 18/18, covering every affected case.
4. PostgreSQL 18 requires the temporary data mount at
   `/var/lib/postgresql`, not `/var/lib/postgresql/data`. The disposable
   database was recreated with the documented PostgreSQL 18 layout before any
   migration or application check ran.

These corrections changed no tracked source, configuration, user service, or
known-issues entry.

## Evidence Ledger

| Bundle | Package | Command Or Check | Result | Fixes Applied | Remaining Or Blocker |
|--------|---------|------------------|--------|---------------|----------------------|
| Detection | root | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | None | None |
| Formatting | backend | `uv run ruff format app tests ../scripts/local_state_archive.py` | PASS: 112 unchanged | None | None |
| Linting | backend | `uv run ruff check --fix app tests ../scripts/local_state_archive.py` | PASS | None | None |
| Type Safety | backend | `uv run mypy app --strict`; `uv run ty check app` | PASS: 47 source files | None | None |
| Testing | backend | isolated PostgreSQL plus `uv run pytest tests/ --cov=app --cov-report=term -q` | PASS: 517, 88% | None | None |
| Formatting | engine | `uv run --package txt2crs ruff format .` | PASS: 138 unchanged | None | None |
| Linting | engine | `uv run --package txt2crs ruff check --fix .` | PASS | None | None |
| Type Safety | engine | `uv run --package txt2crs mypy` | PASS: 138 source files | None | None |
| Testing | engine | `uv run --package txt2crs pytest -q` | PASS: 489; 2 explicit live skips | None | None |
| Formatting And Linting | frontend | `npm run lint` | PASS: 158 checked, no fix | None | None |
| Type Safety | frontend | `npm run typecheck` | PASS | None | None |
| Testing | frontend | `npm run test:unit`; `npm run build` | PASS: 132 tests; 2,215 modules | None | None |
| Testing | frontend | broad Playwright run plus corrected sign-up/reset rerun against isolated services | PASS: all 69 runnable cases; 11 fixture-only skips | Test flags corrected | None |
| Testing | frontend | `TXT2CRS_BROWSER_SCENARIO=complete` and `failed` with `playwright.jobs.config.ts` | PASS: 16 each; one opposite-scenario skip each | None | None |
| Observability | backend | deliberate `write_last_error` call plus JSON and mode inspection | PASS: valid capture, file 0600, directory 0700 | None | None |
| Git Hooks | root | `pre-commit run --all-files`; executable hook check | PASS: all 13 hooks | None | None |
| Database | backend | disposable PostgreSQL 18, `upgrade head`, `current`, `downgrade -1`, `upgrade head`, `current` | PASS: reversible at `a7d9c2e4f601` | Mount point corrected before checks | None |
| Database | backend | `uv run python app/initial_data.py` twice | PASS: both idempotent runs completed | None | None |
| Database Drift | backend | fresh PostgreSQL 18 plus `uv run alembic check` | PASS: no new upgrade operations | None | None |
| Compose | root | `docker compose config --quiet` | PASS | None | Only the harmless unset local `CI` warning |
| Dev Server | root | isolated base Compose `up -d --wait`, backend health, and frontend `/health` through the private network | PASS: all services healthy | Isolated project avoided occupied user ports | None |
| Resource Cleanup | root | isolated Compose `down -v`, disposable database removal, process and Git status checks | PASS | None | None |

## Database And Startup Notes

- The PostgreSQL migration chain completed `head -> -1 -> head`, ended at
  `a7d9c2e4f601`, and reported no schema drift.
- Initial superuser seeding completed twice without duplication or error.
- The isolated production-like backend, frontend, and database all reached
  healthy state. The backend reported application health and fetched the
  frontend health response across the private Compose network.
- Every audit-owned container, network, and volume was removed. Existing
  user containers and their data were left untouched.

## Known Issues Loaded

- Ignored paths: 3
- Ignored rule entries: 3
- Known failing tests: 0
- Skipped workflows: 10, all externally blocked by GitHub Actions billing and
  covered locally where a local equivalent exists
- Skipped infrastructure: 0

No new exception was added, and no repository-fixable tooling failure remains.

## Handoff

`audit -> pipeline` is the required Phase Transition handoff. `infra` follows
only after `pipeline`; returning to `plansession` requires a later
`phasebuild`.

**Next command:** `pipeline`

**Reason:** all seven configured bundles pass across every applicable package.
