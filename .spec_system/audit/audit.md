# Phase 01 Transition Tooling Audit

**Date:** 2026-07-19
**Result:** PASS
**Selected bundle:** none - validation only
**Scope:** `backend-shell`, `txt2crs-engine`, `frontend`, and repository root

## Detection

`bash .spec_system/scripts/analyze-project.sh --json` reported a monorepo with
three registered packages, Phase 01 complete, and no active session. The
repository already has all seven recommended local-development bundles, so
this run adopted and validated the current tools instead of installing a
second implementation.

The existing known-issues registry was loaded before validation. Its
generated/reference exclusions, exact spelling and Gitleaks fingerprints, and
GitHub Actions billing limitation were honored. No known failing test or
skipped infrastructure item exists.

## Package Results

| Package | Formatting | Linting | Types | Tests |
|---------|------------|---------|-------|-------|
| `backend` | Ruff PASS, 69 files unchanged | Ruff and typos PASS | mypy PASS across 35 source files; ty PASS | 194 passed in the non-root container; 78% coverage |
| `backend/packages/txt2crs` | Ruff PASS, 136 files unchanged | Ruff and typos PASS | mypy PASS across 136 source files | 444 passed; 1 explicitly live-gated skip |
| `frontend` | Biome PASS, 126 files and no fixes | Biome and typos PASS | TypeScript PASS | 22 Vitest and 70 Playwright tests passed; production build PASS |
| repository root | EOF, whitespace, TOML, YAML, case, size, typos, generated-client, and Zizmor hooks PASS | pre-commit PASS | N/A | Compose build/startup/health PASS |

## Fixes Applied

1. Made the documented non-root Docker test path capable of running the
   repository-level static contracts. The development override now mounts only
   the required public contract inputs at `/workspace`, read-only, and passes
   that explicit path to the four contract modules. It does not mount `.env`,
   `.git`, or the whole checkout.
2. Removed the host `backend/htmlcov` bind mount from the development backend.
   A host-created directory is commonly not writable by container UID 1001 and
   caused `coverage html` to fail after all tests passed. Coverage now writes
   inside the development container; host and CI test runs retain their normal
   repository-local report behavior.

## Evidence Ledger

| Bundle | Package | Command | Result | Fixes Applied | Remaining / Blocker |
|--------|---------|---------|--------|---------------|---------------------|
| Formatting | backend | `uv run ruff format app tests` | PASS: 69 unchanged | None | None |
| Formatting | engine | `uv run --package txt2crs ruff format .` | PASS: 136 unchanged | None | None |
| Formatting / Linting | frontend | `npm run lint` | PASS: 126 checked, no fixes | None | None |
| Linting | backend | `uv run ruff check --fix app tests` | PASS | None | None |
| Linting | engine | `uv run --package txt2crs ruff check --fix .` | PASS | None | None |
| Type Safety | backend | `uv run mypy app --strict`; `uv run ty check app` | PASS: 35 mypy files; ty clean | None | None |
| Type Safety | engine | `uv run --package txt2crs mypy` | PASS: 136 files | None | None |
| Type Safety | frontend | `npm run typecheck` | PASS | None | None |
| Testing | backend | isolated PostgreSQL plus `bash scripts/test.sh`; `coverage report --fail-under=78` inside UID 1001 container | PASS: 194; 78% | Repaired read-only contract inputs and coverage destination | None |
| Testing | engine | `uv run --package txt2crs pytest -q` | PASS: 444; SKIP: 1 explicit live subscription test | None | Live provider call remains intentionally credential-gated |
| Testing | frontend | `npm run test:unit`; `npm run build` | PASS: 22; production build PASS | None | None |
| Testing | frontend | `npx playwright test --reporter=line` against isolated API, Vite, PostgreSQL, and Mailcatcher | PASS: 70 | Used the repository's local `SMTP_TLS=false` Mailcatcher policy | None |
| Observability | backend | focused logging/telemetry tests plus `write_last_error(...)` JSON and mode validation | PASS: 5; directory `0700`, capture `0600` | None | None |
| Git Hooks | root | `uv run --project backend pre-commit run --all-files` | PASS: every hook | None | None |
| Database | backend | Alembic `check`, `downgrade -1`, `upgrade head`, `check` on PostgreSQL 18.4 | PASS | None | None |
| Database | backend | `python app/initial_data.py` twice and user-count query | PASS: one user after both runs | None | None |
| Dev Server | root | `docker compose config --quiet`; isolated image build and base Compose `up --detach --wait` | PASS | None | None |
| Dev Server | backend/frontend | internal health probes, backend UID/version/import checks | PASS: both healthy; UID 1001; txt2crs 0.5.0 | None | None |

## Validation Notes

- The ordinary local ports were already owned by the user's separate
  `python-react-boilerplate` development stack. The audit did not stop or
  mutate it. Disposable projects, internal container probes, bridge-network
  addresses, and alternate localhost ports kept audit data isolated.
- A first browser attempt ran after the backend suite had reset the disposable
  database; reseeding corrected the expected authentication failure. A second
  attempt reproduced the required local Mailcatcher `SMTP_TLS=false` setting.
  The final clean run passed all 70 tests.
- Every audit-created container, volume, process, and network was removed.
  Existing developer services were left untouched.

## Known Issues Loaded

- Ignored paths: 3
- Ignored rule entries: 3
- Known failing tests: 0
- Skipped workflows: 9, all blocked by GitHub Actions billing and covered by
  local equivalents
- Skipped infrastructure: 0

No new exception was added, and no repository-fixable audit failure remains.

## Handoff

`audit -> pipeline` is the required Phase Transition handoff. `infra` follows
only after `pipeline`; the next implementation session is not planned until
the next phase is created through `phasebuild`.

**Next command:** `pipeline`
**Reason:** all seven configured bundles pass across every applicable package.
