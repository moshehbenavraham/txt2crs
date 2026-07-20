# Phase 04 Transition Tooling Audit

**Date:** 2026-07-20
**Revision:** `dac60fea7b5209022fce3b393f1fbb29663e57b7`
**Result:** PASS
**Selected bundle:** none - validation only
**Scope:** `backend-shell`, `txt2crs-engine`, `frontend`, and repository root

## Detection

`bash .spec_system/scripts/analyze-project.sh --json` reported a mixed-stack
monorepo with three registered packages, Phase 04 complete at 2/2 sessions,
no active session, and all 16 sessions complete through the learner
experience. `.spec_system/CONVENTIONS.md` already records all seven recommended
tooling bundles, so this run added no new tool and validated every configured
tool in the current committed state.

The known-issues registry was loaded before validation. It contains three
ignored paths, three exact ignored-rule entries, no known failing test, nine
billing-blocked remote workflows, and no skipped infrastructure.

## Configured Bundle Matrix

| Bundle | Backend Shell | Engine | Frontend | Root |
|--------|---------------|--------|----------|------|
| Formatting | Ruff format | Ruff format | Biome | EOF/whitespace hooks |
| Linting | Ruff and typos | Ruff and typos | Biome and typos | Pre-commit routing |
| Type Safety | mypy and ty | mypy | TypeScript | N/A |
| Testing | pytest and coverage support | pytest | Vitest and Playwright | deterministic cross-package validation |
| Observability | structured logging, private capture, OpenTelemetry | safe facade events | product-safe error handling | ignored private `logs/` captures |
| Git Hooks | pre-commit package hooks | pre-commit package hooks | pre-commit package hooks | installed repository hook |
| Database | Alembic, SQLModel, PostgreSQL seed/tests | tenant-scoped SQLite tests | N/A | isolated PostgreSQL fixture |

## Package Results

| Package | Formatting / Linting | Types | Tests / Build |
|---------|----------------------|-------|---------------|
| `backend` | Ruff and repository hooks PASS | mypy strict and ty PASS | 479 pytest tests PASS; deterministic app 5/5 PASS |
| `backend/packages/txt2crs` | package Ruff and repository hooks PASS | mypy PASS | 470 pytest tests PASS; 1 explicit live-provider skip; 0.7.0 metadata 2/2 PASS |
| `frontend` | Biome PASS | TypeScript PASS | 132 Vitest PASS; 69 broad Playwright PASS with 11 fixture skips; completed/failed job scenarios 16 PASS each; production build PASS |
| repository root | large-file, case, TOML, YAML, EOF, whitespace, typos, generated-client, and Zizmor hooks PASS | N/A | 9/9 repository validation steps, Compose config, release build, and service startup PASS |

## Repairs Applied

No repository repair or new tooling was required.

Two command-context corrections were made during validation:

- The focused logging test was rerun with the explicit isolated PostgreSQL
  environment used by the complete backend suite; both tests then passed.
- The standalone backend startup supplied all explicitly configured private
  state child paths under the isolated state root; liveness, database health,
  and graceful engine shutdown then passed.

Neither correction changed source, configuration, tracked state, or a user
service. No exception was added to `known-issues.md`.

## Evidence Ledger

| Bundle | Package | Command / Check | Result | Fixes Applied | Remaining / Blocker |
|--------|---------|-----------------|--------|---------------|---------------------|
| Detection | root | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | None | None |
| Formatting / Linting | all | `pre-commit run --all-files` | PASS | None | None |
| Formatting / Linting | all | `./scripts/validate-changes.sh --json` | PASS: 9/9 | None | None |
| Type Safety | backend | `uv run mypy app`; `uv run ty check app` through repository validation/hooks | PASS | None | None |
| Type Safety | engine | `uv run --package txt2crs mypy` through repository validation | PASS | None | None |
| Type Safety | frontend | `npm run typecheck` through direct closeout and all-file hook | PASS | None | None |
| Testing | backend | isolated PostgreSQL plus `uv run pytest tests/ -q` | PASS: 479 | None | None |
| Testing | engine | `cd backend/packages/txt2crs && uv run --package txt2crs pytest -q` | PASS: 470; SKIP: 1 explicit live gate | None | None |
| Testing | frontend | `npm run test:unit`; `npm run build` | PASS: 132 tests; 2,215 modules | None | None |
| Testing | frontend | documented broad `npx playwright test` environment | PASS: 69; SKIP: 11 job-fixture-only | None | None |
| Testing | frontend | `TXT2CRS_BROWSER_SCENARIO=complete` and `failed` job Playwright configurations | PASS: 16 each; one opposite-scenario skip each | None | None |
| Release | engine | `uv build --package txt2crs` plus wheel/sdist metadata and contents inspection | PASS: 0.7.0 wheel and source distribution | None | None |
| Observability | backend | isolated DB plus `uv run pytest tests/core/test_logging.py -q`; inspect `logs/.gitignore` | PASS: 2 tests; private captures remain ignored | Command environment corrected | None |
| Git Hooks | root | `pre-commit install`; executable-hook check; `pre-commit run --all-files` | PASS | Hook installed in `.git/hooks` | None |
| Database | backend | isolated `alembic current`, `downgrade -1`, `upgrade head`, `check`, `current` | PASS: `a7d9c2e4f601` at head, no drift | None | None |
| Database | backend | isolated `python -m app.initial_data` twice | PASS: both idempotent runs completed | None | None |
| Compose | root | `docker compose config --quiet` | PASS | None | Only the intentionally unset local `CI` warning |
| Dev Server | backend | isolated Uvicorn on 8015; `curl` liveness and database health; Ctrl-C shutdown | PASS: 200/healthy and managed engine shutdown | Explicit private child paths supplied | None |
| Dev Server | frontend | Vite strict port 5186; `curl` root mount point; Ctrl-C shutdown | PASS | None | None |
| Resource Cleanup | root | listener checks and process shutdown output | PASS | Temporary servers stopped | None |

## Database And Startup Notes

- The real PostgreSQL head completed `head -> -1 -> head`, `alembic check`
  reported no new operation, and the seed was idempotent.
- The standalone backend started in truthful unconfigured-research mode,
  returned `true` from liveness and a healthy PostgreSQL readiness response,
  and closed authentication and engine resources during shutdown.
- Vite served the current React mount point on an isolated strict port.
- Existing user Compose services and ordinary project ports were not stopped,
  rebuilt, or mutated.

## Known Issues Loaded

- Ignored paths: 3
- Ignored rule entries: 3
- Known failing tests: 0
- Skipped workflows: 9, all externally blocked by GitHub Actions billing and
  covered locally where a local equivalent exists
- Skipped infrastructure: 0

No new exception was added, and no repository-fixable tooling failure remains.

## Handoff

`audit -> pipeline` is the required Phase Transition handoff. `infra` follows
only after `pipeline`; Phase 05 planning follows the remaining transition
workflow.

**Next command:** `pipeline`

**Reason:** all seven configured bundles pass across every applicable package.
