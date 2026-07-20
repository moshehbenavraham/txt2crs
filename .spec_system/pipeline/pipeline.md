# Phase 03 Transition CI/CD Pipeline Report

**Date:** 2026-07-20
**Result:** PASS with local fallback
**Selected bundle:** none - validation only
**Platform:** GitHub Actions
**Scope:** all repository workflows and all three registered packages

## Detection

The required project analysis reported a mixed Python/TypeScript monorepo with
Phase 03 complete, no active session, and three registered packages:

- `backend-shell` owns FastAPI, PostgreSQL, and Alembic;
- `txt2crs-engine` is the separately configured workspace package consumed by
  the shell;
- `frontend` owns React, TypeScript, Vitest, and Playwright.

No workspace task runner is present. The current job-oriented strategy remains
appropriate: language-specific jobs use package-owned tools, while shared
backend/engine changes trigger combined quality and integration workflows.
All five pipeline bundles are already represented in
`.spec_system/CONVENTIONS.md`, so this phase selected no new bundle and
validated every existing workflow.

`gh pr list --state open` returned no pull requests, failing PR checks,
requested changes, or review threads.

## Remote CI Status

Commit `98c86525eb6fecd0f311cb03ad431fd967584af1` triggered all seven
push-enabled workflows. GitHub rejected every job before any workflow step
started. The check annotation says the jobs were not started because recent
account payments failed or the spending limit must be increased. This
reconfirms the external billing condition recorded in `known-issues.md`.

| Workflow | Run ID | Remote result |
|----------|--------|---------------|
| `quality.yml` | `29708859946` | Rejected before runner; zero-step jobs |
| `test-backend.yml` | `29708859972` | Rejected before runner |
| `test-docker-compose.yml` | `29708859964` | Rejected before runner |
| `playwright.yml` | `29708859956` | Rejected before runner |
| `security.yml` | `29708859962` | Rejected before runner |
| `zizmor.yml` | `29708859958` | Rejected before runner |
| `detect-conflicts.yml` | `29708859989` | Rejected before runner |

`generate-client.yml` and `guard-dependencies.yml` are pull-request-only.
There is no current PR run to inspect; both definitions and their applicable
local equivalents passed.

## Workflow Inventory

| Bundle | Workflows | Local result | Remote result |
|--------|-----------|--------------|---------------|
| Code Quality | `quality.yml` | PASS for shell, engine, and frontend | Run `29708859946` rejected before runner |
| Build & Test | `quality.yml`, `test-backend.yml`, `test-docker-compose.yml`, `playwright.yml`, `generate-client.yml` | PASS: builds, 473 backend, 470 engine, 33 unit, 65 browser, deterministic client | Push runs rejected before runner; PR-only client workflow not applicable |
| Security | `security.yml`, `zizmor.yml`, `guard-dependencies.yml` | PASS: history, dependency, syntax, and workflow scans | Runs rejected before runner; CodeQL remains remote-only |
| Integration | `playwright.yml`, `test-docker-compose.yml`, `detect-conflicts.yml` | PASS: browser, PostgreSQL, migrations, health, production images, and no open PR | Push runs rejected before runner |
| Operations | Dependabot plus local release/tag and deployment policy | PASS for approved local-only operations | GitHub Actions intentionally does not deploy |

## Evidence Ledger

| Workflow | Run / Local Fallback | Result | Fixes Applied | Remaining / Blocker |
|----------|----------------------|--------|---------------|---------------------|
| `quality.yml` | Run `29708859946`; `uv run bash scripts/lint.sh`; package Ruff/mypy/pytest; frontend Biome/tsc/Vitest/build | PASS (local fallback): 473 shell, 470 engine plus 1 live skip, 33 frontend unit tests | Retired stale donor frontend dependencies during audit | GitHub Actions billing |
| `test-backend.yml` | Run `29708859972`; isolated PostgreSQL plus `coverage run -m pytest tests/ -q`; `coverage report --fail-under=78` | PASS (local fallback): 473 tests, 88% coverage | None | GitHub Actions billing |
| `test-docker-compose.yml` | Run `29708859964`; isolated production image build and `up -d --wait` under project `txt2crs-pipeline` | PASS (local fallback): backend, PostgreSQL, and frontend healthy; backend UID 1001 | Created and removed an isolated external network required by production Compose | GitHub Actions billing |
| `playwright.yml` | Run `29708859956`; isolated API/Vite/PostgreSQL/Mailcatcher `npx playwright test --reporter=line` | PASS (local fallback): 65 | Updated donor-era route assertions and deterministic auth setup | GitHub Actions billing |
| `security.yml` | Run `29708859962`; Gitleaks; `pip-audit`; `npm audit --audit-level=high` | PASS (local fallback): 52 commits, no leaks, no known dependency vulnerability | None | GitHub Actions billing; CodeQL execution is remote-only |
| `zizmor.yml` | Run `29708859958`; Actionlint and local Zizmor across all nine workflows | PASS (local fallback): no finding | None | GitHub Actions billing |
| `detect-conflicts.yml` | Run `29708859989`; `gh pr list --state open`; Actionlint; Zizmor | PASS (local fallback): no open PR | None | GitHub Actions billing |
| `generate-client.yml` | PR-only; `bash scripts/generate-client.sh` plus generated-path diff check | PASS (local fallback): deterministic and clean | None | No open PR; billing entry retained for the next applicable run |
| `guard-dependencies.yml` | PR-only; Actionlint, Zizmor, author-policy inspection, Python audit, and npm audit | PASS (local fallback) | None | No dependency PR; billing entry retained for the next applicable run |

## Required Secrets

No secret value was created or committed.

- Normal quality, test, security, and integration jobs require no manually
  configured secret.
- Security analysis uses GitHub's automatic `GITHUB_TOKEN`.
- Same-repository generated-client PR pushes reference the already-documented
  `FULL_STACK_FASTAPI_TEMPLATE_REPO_TOKEN`; fork drift checks do not require
  it.
- There is no deploy or hosted-backup secret because hosted operations remain
  outside the approved deployment scope.

## Known Issues

The nine workflow entries remain in
`.spec_system/audit/known-issues.md` because the external billing condition
still applies. Current counts are:

- ignored paths: 3;
- ignored rule entries: 3;
- known failing tests: 0;
- skipped workflows: 9;
- skipped infrastructure: 0.

No new exception was added. No repository-fixable pipeline failure or review
item remains.

## Cleanup

The isolated pipeline Compose project, containers, volumes, network, and image
tags were removed after validation. The user's running
`python-react-boilerplate` services were neither restarted nor mutated.

## Handoff

`pipeline -> infra` is the required Phase Transition handoff. `carryforward`
comes only after `infra`, and session planning resumes only after
`phasebuild` creates Phase 04.

**Next command:** `infra`

**Reason:** all configured workflows pass exact local fallbacks; remote
execution remains blocked only by the documented external billing condition.
