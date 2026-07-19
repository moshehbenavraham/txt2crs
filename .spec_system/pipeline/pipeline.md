# Phase 01 Transition CI/CD Pipeline Report

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

The existing job-oriented strategy is appropriate: language-specific jobs run
their own package tools, while shared backend or engine changes trigger the
combined quality and integration workflows. All five pipeline bundles are
already configured for the current local-only deployment scope, so this phase
selected no new bundle and validated every existing workflow.

`gh pr list --state open` returned no pull requests, failing PR checks,
requested changes, or review threads. `gh secret list --app actions` returned
no configured repository Actions secrets.

## Remote CI Status

Commit `79993410c468dbe3fa84f81554e33baff16d68d6` triggered every
push-enabled workflow. GitHub briefly reported them as queued, then rejected
every job before any step started. Each failed job has `step_count=0`, matching
the existing Actions billing/spending limitation rather than a source,
configuration, or test failure.

| Workflow | Run ID | Remote result |
|----------|--------|---------------|
| `quality.yml` | `29692537654` | Rejected before runner; zero-step jobs |
| `test-backend.yml` | `29692537652` | Rejected before runner; zero-step job |
| `test-docker-compose.yml` | `29692537650` | Rejected before runner; zero-step job |
| `playwright.yml` | `29692537686` | Rejected before runner; zero-step gate job |
| `security.yml` | `29692537667` | Rejected before runner; zero-step jobs; PR review skipped as expected |
| `zizmor.yml` | `29692537676` | Rejected before runner; zero-step job |
| `detect-conflicts.yml` | `29692537663` | Rejected before runner; zero-step job |

`generate-client.yml` and `guard-dependencies.yml` are PR-only workflows. With
no open PR, there is no applicable current run; their complete local
equivalents and workflow definitions were validated.

## Fix Applied

The local workflow inspection found one source-controlled CI defect that the
billing outage had hidden:

- `test-docker-compose.yml` probed frontend port `5181`, while the
  authoritative development mapping is `5183`.
- Its backend smoke command used the compatibility liveness spelling rather
  than the documented PostgreSQL-backed readiness endpoint.

A failing regression was added first. The workflow now uses
`curl --fail http://localhost:8012/api/v1/utils/health/` and
`curl --fail http://localhost:5183/health`. The contract also rejects the old
port. The complete backend suite increased to 195 tests and passes in both
host and non-root container execution.

## Workflow Inventory

| Bundle | Workflows | Local result | Remote result |
|--------|-----------|--------------|---------------|
| Code Quality | `quality.yml` | PASS for shell, engine, and frontend | Run `29692537654` rejected before runner |
| Build & Test | `quality.yml`, `test-backend.yml`, `test-docker-compose.yml`, `playwright.yml`, `generate-client.yml` | PASS: builds, 195 backend, 444 engine, 22 unit, 70 browser, deterministic client | Push runs rejected before runner; PR-only client workflow not applicable |
| Security | `security.yml`, `zizmor.yml`, `guard-dependencies.yml` | PASS for history, dependency, syntax, and workflow scanners | Runs rejected before runner; CodeQL remains remote-only |
| Integration | `playwright.yml`, `test-docker-compose.yml`, `detect-conflicts.yml` | PASS: browser, database, migration, full-stack health; no open PR | Push runs rejected before runner |
| Operations | no hosted deployment workflows | PASS for intentional local-only policy | GitHub Actions intentionally does not deploy |

## Evidence Ledger

| Workflow | Run / local fallback | Result | Fixes Applied | Remaining / Blocker |
|----------|----------------------|--------|---------------|---------------------|
| `quality.yml` | Run `29692537654`; `backend/scripts/lint.sh`; engine Ruff/mypy/pytest; frontend Biome CI/tsc/Vitest/build | PASS (local fallback): shell types/lint clean, engine 444 + 1 live skip, frontend 22 and build | None | GitHub Actions billing |
| `test-backend.yml` | Run `29692537652`; fresh PostgreSQL + Alembic + host pytest/coverage; UID 1001 `scripts/test.sh` | PASS (local fallback): 195 in both modes, 78% | Added current Compose-workflow regression | GitHub Actions billing |
| `test-docker-compose.yml` | Run `29692537650`; `docker compose config --quiet`; isolated build/start/health/import checks; workflow contract | PASS (local fallback) | Corrected backend readiness and frontend health probes | GitHub Actions billing |
| `playwright.yml` | Run `29692537686`; isolated API/Vite/PostgreSQL/Mailcatcher `npx playwright test --reporter=line` | PASS (local fallback): 70 | None | GitHub Actions billing |
| `security.yml` | Run `29692537667`; `gitleaks detect --source . --redact --no-banner`; Python and npm audits | PASS (local fallback): 22 commits, no leaks or known dependency vulnerabilities | None | GitHub Actions billing; CodeQL execution is remote-only |
| `zizmor.yml` | Run `29692537676`; `actionlint .github/workflows/*.yml`; `uv run --project backend zizmor .github/workflows` | PASS (local fallback): no findings | None | GitHub Actions billing |
| `detect-conflicts.yml` | Run `29692537663`; `gh pr list --state open`; actionlint and Zizmor | PASS (local fallback): no open PR to compare | None | GitHub Actions billing |
| `generate-client.yml` | PR-only; `scripts/generate-client.sh` followed by clean `frontend/src/client` and `openapi.json` diff | PASS (local fallback) | None | No open PR; GitHub Actions billing remains recorded |
| `guard-dependencies.yml` | PR-only; actionlint, Zizmor, trigger/permission inspection, both dependency audits | PASS (local fallback) | None | No open dependency PR; GitHub Actions billing remains recorded |

## Required Secrets

No secret value was created, printed, or committed.

- Normal quality, test, security, and integration jobs require no manually
  configured secret.
- Security analysis uses GitHub's automatic `GITHUB_TOKEN`.
- Same-repository generated-client PR pushes reference
  `FULL_STACK_FASTAPI_TEMPLATE_REPO_TOKEN`; the name remains documented, and
  the drift-check path works without it for forks.
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
after `phasebuild` creates the next phase.

**Next command:** `infra`
**Reason:** all configured workflows pass their exact local fallbacks; remote
execution remains blocked only by the documented external billing condition.
