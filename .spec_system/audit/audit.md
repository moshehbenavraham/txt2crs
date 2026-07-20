# Phase 03 Transition Tooling Audit

**Date:** 2026-07-20
**Result:** PASS
**Selected bundle:** none - validation and repository repair only
**Scope:** `backend-shell`, `txt2crs-engine`, `frontend`, and repository root

## Detection

`bash .spec_system/scripts/analyze-project.sh --json` reported a monorepo with
three registered packages, Phase 03 complete at 3/3 sessions, and no active
session. All configured local-development bundles were already present, so the
audit validated them in place.

The known-issues registry was loaded before validation. It contains three
ignored paths, three exact rule entries, no known failing test, nine
billing-blocked remote workflows, and no skipped infrastructure.

## Package Results

| Package | Formatting / Linting | Types | Tests / Build |
|---------|----------------------|-------|---------------|
| `backend` | Ruff and repository hooks PASS | mypy strict and ty PASS | 473 pytest tests PASS |
| `backend/packages/txt2crs` | Ruff and repository hooks PASS | mypy PASS | 470 pytest tests PASS; 1 explicitly live-gated skip |
| `frontend` | Biome PASS | TypeScript PASS | 33 Vitest and 65 Playwright tests PASS; production build PASS |
| repository root | whitespace, EOF, TOML, YAML, case, size, typos, generated-client, and Zizmor hooks PASS | N/A | isolated PostgreSQL, Alembic, API, Vite, browser, and Compose-config checks PASS |

## Repairs Applied

The initial frontend type check found thirteen references to the donor Item
OpenAPI surface retired in Phase 03. Audit rules require repository-fixable
failures to be repaired rather than deferred, so the following bounded
transition repair was completed:

- Removed the donor `/items` route, dashboard/library components, Item
  components, pending shells, save hook, Zod schema, branded ID, and obsolete
  browser suite.
- Replaced the donor dashboard with a truthful course workspace that describes
  the four generated learning assets without inventing job-list behavior before
  Phase 04.
- Removed donor navigation and regenerated the TanStack route tree.
- Added test-first browser coverage for the workspace, the retired route's
  not-found result, a 390-pixel viewport, 44-pixel mobile actions, and
  reduced-motion navigation.
- Updated shared authentication setup to acquire a token through the API and
  seed the same browser storage migration used by production. Login behavior
  remains covered independently by its own browser tests.
- Updated active frontend guidance, examples, account-deletion copy, session
  tests, and the frontend README to the current course-job contracts.

The React guidance kept the static learning-asset description at module scope,
removed dead donor bundle paths, preserved TanStack Query for server state, and
introduced no render-time data waterfall.

## Evidence Ledger

| Bundle | Package | Command / Check | Result |
|--------|---------|-----------------|--------|
| Formatting / Linting | backend | Ruff format and check across shell sources and tests | PASS |
| Formatting / Linting | engine | package-owned Ruff format and check | PASS |
| Formatting / Linting | frontend | `npm run lint` | PASS: 116 files |
| Type Safety | backend | `uv run mypy app`; `uv run ty check app` | PASS |
| Type Safety | engine | `uv run --package txt2crs mypy` | PASS |
| Type Safety | frontend | `npm run typecheck` | PASS |
| Testing | backend | isolated PostgreSQL plus `uv run pytest tests/ -v` | PASS: 473 |
| Testing | engine | `uv run --package txt2crs pytest` | PASS: 470; SKIP: 1 explicit live provider test |
| Testing | frontend | `npm run test:unit`; `npm run build` | PASS: 33 tests; 2,182 modules built |
| Testing | frontend | Playwright against isolated API, Vite, PostgreSQL, and Mailcatcher | PASS: 65 |
| Rendered UI | frontend | authenticated Playwright inspection at 1440x1000 and 390x844 | PASS: no overflow, console warning, console error, or page error |
| Accessibility / Motion | frontend | semantic heading/action assertions, 44-pixel mobile target, reduced-motion route test | PASS |
| Observability | backend | focused structured-logging tests in shell suite | PASS: private capture and safe event contracts |
| Git Hooks | root | `uvx pre-commit run --all-files` | PASS: every hook, including deterministic generated client and Zizmor |
| Database | backend | Alembic `current`, `downgrade -1`, `upgrade head`, `check`, `current` | PASS: `a7d9c2e4f601` at head with no drift |
| Database | backend | `python -m app.initial_data` twice | PASS: idempotent |
| Dev Server | root | `docker compose config --quiet`; isolated backend liveness request; Vite startup | PASS |
| Integrated Purge | frontend/backend/engine | admin browser deletion through a configured local facade | PASS: engine purge completed before SQL user deletion |

## Validation Notes

- The user's existing `python-react-boilerplate` containers and ordinary ports
  were not stopped, rebuilt, or mutated. Audit services used PostgreSQL on
  `55433`, FastAPI on `8013`, and Vite on `5191`.
- Browser-plugin automation was not available in this environment. The
  repository's JavaScript Playwright installation was used as the documented
  fallback, including authenticated desktop/mobile image inspection.
- The first isolated backend intentionally ran in setup state. Its coordinated
  user-delete request correctly returned the reviewed 503 because no engine
  facade existed. A second isolated run composed the local facade with
  non-production, non-live research configuration; the same deletion flow then
  passed and logged `user.engine_purge_completed`.
- Public signup and password-recovery tests used the existing local Mailcatcher
  through its host-mapped test ports. No external email or provider request was
  made.
- The supported head migration completed a real `downgrade -1` and
  `upgrade head` transaction against disposable PostgreSQL 18.4 data.
- Audit-created processes were stopped after validation. The disposable
  PostgreSQL container is retained only until the remaining transition
  workflows finish and will then be removed.

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
only after `pipeline`; Phase 04 planning follows the remaining transition
workflow.

**Next command:** `pipeline`

**Reason:** every configured bundle passes across all applicable packages.
