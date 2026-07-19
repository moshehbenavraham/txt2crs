# Phase 02 Transition CI/CD Pipeline Report

**Date:** 2026-07-19
**Result:** PASS with local fallback
**Selected bundle:** none - validation only
**Platform:** GitHub Actions
**Scope:** all repository workflows and all three registered packages

## Detection

The repository remains a mixed Python/TypeScript monorepo with no task runner:

- `backend-shell` owns FastAPI, PostgreSQL, and Alembic;
- `txt2crs-engine` is a separately configured Python workspace package
  consumed by the shell;
- `frontend` owns React, TypeScript, Vitest, and Playwright.

The existing job-oriented strategy is appropriate. Language-specific jobs run
their own package tools, while shared backend or engine changes trigger the
combined quality and integration workflows. All five pipeline bundles remain
configured for the accepted local-only deployment scope, so this phase
selected no new bundle and validated every existing workflow.

`gh pr list --state open` returned no pull requests, failing PR checks,
requested changes, or review threads.

## Remote CI Status

Commit `3dfbd01cf771a67d94b783fdfe269dcb9d357161` triggered every
push-enabled workflow. GitHub rejected every job before any step started.
Current check annotations state that recent account payments failed or the
spending limit must be increased. This confirms the documented external
billing condition rather than a source, workflow, or test failure.

| Workflow | Run ID | Remote result |
|----------|--------|---------------|
| `quality.yml` | `29701210498` | Rejected before runner; zero-step jobs |
| `test-backend.yml` | `29701210575` | Rejected before runner; zero-step job |
| `test-docker-compose.yml` | `29701210507` | Rejected before runner; zero-step job |
| `playwright.yml` | `29701210495` | Rejected before runner; zero-step gate job |
| `security.yml` | `29701210520` | Rejected before runner; CodeQL and other jobs have zero steps |
| `zizmor.yml` | `29701210546` | Rejected before runner; zero-step job |
| `detect-conflicts.yml` | `29701210488` | Rejected before runner; zero-step job |

`generate-client.yml` and `guard-dependencies.yml` are pull-request-only
workflows. With no open pull request, no current run applies; their definitions
and executable local equivalents were validated.

## Workflow Inventory

| Bundle | Workflows | Local result | Remote result |
|--------|-----------|--------------|---------------|
| Code Quality | `quality.yml` | PASS for shell, engine, and frontend | Run `29701210498` rejected before runner |
| Build & Test | `quality.yml`, `test-backend.yml`, `test-docker-compose.yml`, `playwright.yml`, `generate-client.yml` | PASS: builds, 296 backend, 464 engine, 33 unit, 76 browser, deterministic client | Push runs rejected before runner; PR-only client workflow not applicable |
| Security | `security.yml`, `zizmor.yml`, `guard-dependencies.yml` | PASS for history, dependencies, syntax, and workflow scanners | Runs rejected before runner; CodeQL remains remote-only |
| Integration | `playwright.yml`, `test-docker-compose.yml`, `detect-conflicts.yml` | PASS: browser, database, migration, health, and no open PR | Push runs rejected before runner |
| Operations | Dependabot plus local release/tag policy; no hosted deploy workflow | PASS for intentional local-only policy | GitHub Actions intentionally does not deploy |

## Evidence Ledger

| Workflow | Run / local fallback | Result | Fixes Applied | Remaining / Blocker |
|----------|----------------------|--------|---------------|---------------------|
| `quality.yml` | Run `29701210498`; backend Ruff/mypy/ty/pytest; engine Ruff/mypy/pytest; frontend Biome/tsc/Vitest/build | PASS (local fallback): 296 shell, 464 engine plus 1 live skip, 33 frontend unit tests | None | GitHub Actions billing |
| `test-backend.yml` | Run `29701210575`; fresh PostgreSQL, Alembic, pytest, and coverage | PASS (local fallback): 296 at 83% | None | GitHub Actions billing |
| `test-docker-compose.yml` | Run `29701210507`; `docker compose config --quiet`; isolated database, migrations, backend health, and Vite startup | PASS (local fallback) | None | GitHub Actions billing |
| `playwright.yml` | Run `29701210495`; isolated API/Vite/PostgreSQL/Mailcatcher `npx playwright test --reporter=line` | PASS (local fallback): 76 | None | GitHub Actions billing |
| `security.yml` | Run `29701210520`; `gitleaks detect --source . --redact --no-banner`; Python and npm audits | PASS (local fallback): 49 commits, no leaks, no known dependency vulnerability | None | GitHub Actions billing; CodeQL execution is remote-only |
| `zizmor.yml` | Run `29701210546`; `actionlint .github/workflows/*.yml`; `uv run --project backend zizmor .github/workflows` | PASS (local fallback): no finding | None | GitHub Actions billing |
| `detect-conflicts.yml` | Run `29701210488`; `gh pr list --state open`; Actionlint and Zizmor | PASS (local fallback): no open PR | None | GitHub Actions billing |
| `generate-client.yml` | PR-only; `bash scripts/generate-client.sh` followed by clean `frontend/openapi.json` and `frontend/src/client` diff | PASS (local fallback) | None | No open PR; GitHub Actions billing remains recorded |
| `guard-dependencies.yml` | PR-only; Actionlint, Zizmor, author-policy inspection, Python and npm audits | PASS (local fallback) | None | No dependency PR; GitHub Actions billing remains recorded |

## Required Secrets

No secret value was created, printed, or committed.

- Normal quality, test, security, and integration jobs require no manually
  configured secret.
- Security analysis uses GitHub's automatic `GITHUB_TOKEN`.
- Same-repository generated-client pull request pushes reference
  `FULL_STACK_FASTAPI_TEMPLATE_REPO_TOKEN`; the name remains documented, and
  fork drift checks do not require it.
- There is no deploy or hosted-backup secret because hosted operations are
  outside the approved scope.

## Known Issues

The nine workflow billing entries remain in
`.spec_system/audit/known-issues.md` because the external condition still
applies. Their local evidence is current:

- ignored paths: 3;
- ignored rule entries: 3;
- known failing tests: 0;
- skipped workflows: 9;
- skipped infrastructure: 0.

No new exception was added. No repository-fixable pipeline failure or review
item remains.

## Handoff

`pipeline -> infra` is the required Phase Transition handoff. `carryforward`
comes only after `infra`, and implementation-session planning resumes only
after `phasebuild` creates Phase 03.

**Next command:** `infra`
**Reason:** all configured workflows pass their exact local fallbacks; remote
execution remains blocked only by the documented external billing condition.
