# Phase 02 Transition Tooling Audit

**Date:** 2026-07-19
**Result:** PASS
**Selected bundle:** none - validation only
**Scope:** `backend-shell`, `txt2crs-engine`, `frontend`, and repository root

## Detection

`bash .spec_system/scripts/analyze-project.sh --json` reported a monorepo with
three registered packages, Phase 02 complete at 5/5 sessions, and no active
session. All seven recommended local-development bundles were already
configured, so this run validated the existing tools instead of installing a
second implementation.

The known-issues registry was loaded before validation. It contains three
ignored paths, three exact rule entries, no known failing test, nine
billing-blocked remote workflows, and no skipped infrastructure.

## Package Results

| Package | Formatting | Linting | Types | Tests |
|---------|------------|---------|-------|-------|
| `backend` | Ruff PASS, 89 files unchanged | Ruff and typos PASS | mypy PASS across 43 source files; ty PASS | 296 passed; 83% measured coverage |
| `backend/packages/txt2crs` | Ruff PASS, 138 files unchanged | Ruff and typos PASS | mypy PASS across 138 source files | 464 passed; 1 explicitly live-gated skip |
| `frontend` | Biome PASS, 138 files and no fixes | Biome and typos PASS | TypeScript PASS | 33 Vitest and 76 Playwright tests passed; production build PASS |
| repository root | EOF, whitespace, TOML, YAML, case, size, typos, generated-client, and Zizmor hooks PASS | pre-commit PASS | N/A | Isolated database, migration, API health, Vite startup, and browser flow PASS |

## Fixes Applied

The hook found one documentation-only spelling false positive in the completed
Session 05 validation ledger. The image-file label was replaced with the clearer ASCII phrase
`image captures`. No implementation, configuration, dependency, generated
client, or schema file changed.

## Evidence Ledger

| Bundle | Package | Command | Result | Fixes Applied | Remaining / Blocker |
|--------|---------|---------|--------|---------------|---------------------|
| Formatting | backend | `uv run ruff format app tests` | PASS: 89 unchanged | None | None |
| Formatting | engine | `uv run --package txt2crs ruff format .` | PASS: 138 unchanged | None | None |
| Formatting / Linting | frontend | `npm run lint` | PASS: 138 checked, no fixes | None | None |
| Linting | backend | `uv run ruff check app tests --fix` | PASS | None | None |
| Linting | engine | `uv run --package txt2crs ruff check . --fix` | PASS | None | None |
| Type Safety | backend | `uv run mypy app --strict`; `uv run ty check app` | PASS: 43 mypy files; ty clean | None | None |
| Type Safety | engine | `uv run --package txt2crs mypy` | PASS: 138 files | None | None |
| Type Safety | frontend | `npm run typecheck` | PASS | None | None |
| Testing | backend | isolated PostgreSQL 18.4 plus `coverage run -m pytest tests/ -q`; `coverage report --fail-under=78` | PASS: 296; 83% | None | None |
| Testing | engine | `uv run --package txt2crs pytest -q` | PASS: 464; SKIP: 1 explicit live subscription test | None | Credentialed provider proof remains intentionally live-gated |
| Testing | frontend | `npm run test:unit`; `npm run build` | PASS: 33; 2,204 modules built | None | None |
| Testing | frontend | `npx playwright test --reporter=line` against isolated API, Vite, PostgreSQL, and Mailcatcher | PASS: 76 | Used allowed `localhost` origin and reseeded the disposable database after shell cleanup | None |
| Observability | backend | focused logging tests in the shell suite | PASS: private JSON capture shape, directory mode `0700`, file mode `0600` | None | None |
| Git Hooks | root | `uvx pre-commit run --all-files` | PASS: every hook | Reworded one spelling false positive | None |
| Database | backend | Alembic `upgrade head`, `downgrade -1`, `upgrade head`, and `check` on PostgreSQL 18.4 | PASS | None | None |
| Database | backend | `python -m app.initial_data` twice | PASS: idempotent | None | None |
| Dev Server | root | `docker compose config --quiet`; backend health request; Playwright-managed Vite startup | PASS | None | None |

## Validation Notes

- The ordinary local ports were already owned by the user's separate
  `python-react-boilerplate` stack. The audit did not stop or mutate it.
  Disposable containers and alternate localhost ports kept audit data isolated.
- A full historical Alembic downgrade stopped at the repository's intentional
  UUID-to-integer rollback guard. The supported head revision completed its
  `downgrade -1` and `upgrade head` round trip, and `alembic check` found no
  drift.
- A first container-only shell run omitted the approved repository contract
  mounts; a second proved 294 tests but still lacked two files that are not
  mounted in the runtime image. The authoritative host suite against the same
  isolated PostgreSQL instance passed all 296 tests at 83% coverage.
- Browser authentication first used `127.0.0.1`, which is intentionally absent
  from the configured CORS allowlist. The final run used the supported
  `localhost` origin and passed all 76 tests.
- Every audit-created container, volume, process, network, and temporary state
  directory was removed. Existing developer services were left untouched.

## Known Issues Loaded

- Ignored paths: 3
- Ignored rule entries: 3
- Known failing tests: 0
- Skipped workflows: 9, all blocked by GitHub Actions billing and covered by
  local equivalents where possible
- Skipped infrastructure: 0

No new exception was added, and no repository-fixable audit failure remains.

## Handoff

`audit -> pipeline` is the required Phase Transition handoff. `infra` follows
only after `pipeline`; the next implementation session is not planned until
Phase 03 is created through `phasebuild`.

**Next command:** `pipeline`
**Reason:** all seven configured bundles pass across every applicable package.
