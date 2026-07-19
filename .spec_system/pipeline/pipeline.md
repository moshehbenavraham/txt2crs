# Phase Transition CI/CD Pipeline Report

**Date:** 2026-07-19
**Result:** PASS with local fallback
**Selected bundle:** Security
**Platform:** GitHub Actions
**Scope:** all repository workflows and all three registered packages

## Detection

The repository is a Python/TypeScript monorepo with a FastAPI shell, the
independently configured `txt2crs` Python workspace package, and a React
frontend. Code-quality, build/test, integration, and operations workflows
already existed. Security had workflow-supply-chain and dependency-change
guards, but no history secret scan, CodeQL analysis, or language dependency
audits, so Security was the highest incomplete bundle.

There were no open pull requests or review threads. GitHub-hosted Actions jobs
from commit `4091b8eae6df8cd6f6a6a9e4f6883babe5f71ae2` were rejected before a
runner or step started because repository Actions billing is unavailable.
The affected workflows are recorded in `../audit/known-issues.md`; the current
transition therefore uses the pipeline workflow's allowed local-fallback path.

## Changes

1. Added `security.yml` with weekly, push, pull-request, and manual triggers.
   It performs full-history Gitleaks scanning, CodeQL for Python and
   JavaScript/TypeScript, high-severity dependency review, `pip-audit`, and
   `npm audit`.
2. Pinned every new third-party action to an immutable 40-character commit and
   granted only per-job read/security-event permissions.
3. Added four exact Gitleaks fingerprints for known example/synthetic values.
   No path, rule, or repository-wide secret-scan exclusion was added.
4. Added the reusable engine's Ruff, mypy, and 223-test suite to the unified
   quality gate.
5. Expanded backend linting to authored tests and corrected two pre-existing
   coverage gates from unsupported 85%/90% claims to the measured 78%
   regression baseline.
6. Added static workflow contracts to the fast repository validator.
7. Documented workflow ownership and secret names in `CONVENTIONS.md`.

## Workflow Inventory

| Bundle | Workflows | Local result | Remote result |
|--------|-----------|--------------|---------------|
| Code Quality | `quality.yml` | PASS | Runner rejected by billing |
| Build & Test | `quality.yml`, `test-backend.yml`, `test-docker-compose.yml`, `playwright.yml`, `generate-client.yml` | PASS | Runner rejected by billing |
| Security | `security.yml`, `zizmor.yml`, `guard-dependencies.yml` | PASS for history/dependency/workflow scanners; CodeQL definition validated | Runner unavailable; CodeQL is remote-only |
| Integration | `playwright.yml`, `test-docker-compose.yml`, `detect-conflicts.yml` | PASS; no open PRs | Runner rejected by billing |
| Operations | `deploy-coolify.yml`, `deploy-staging.yml`, `deploy-production.yml`, `backup-db.yml` | Syntax and supply-chain validation PASS | Deploy/backup side effects not requested; runners unavailable |

## Evidence Ledger

| Check | Command / evidence | Result |
|-------|--------------------|--------|
| Workflow syntax | `actionlint .github/workflows/*.yml` | PASS |
| Workflow security | `uv run zizmor ../.github/workflows` from `backend/` | PASS, no findings |
| Security contracts | `pytest --confcutdir=tests/scripts tests/scripts/test_security_workflow_contract.py` | PASS: 3 |
| Quality contracts | `pytest --confcutdir=tests/scripts tests/scripts/test_quality_workflow_contract.py` | PASS: 3 |
| Secret history | Gitleaks 8.30.1 Docker scan over all 14 commits | PASS, no leaks |
| Python dependencies | `uv run --with pip-audit pip-audit --progress-spinner=off` | PASS, no known vulnerabilities; two local packages skipped |
| JavaScript dependencies | `npm audit --audit-level=high` | PASS, 0 vulnerabilities |
| Backend lint/types | `backend/scripts/lint.sh` | PASS: mypy, ty, Ruff lint/format |
| Backend application | Full PostgreSQL-backed suite | PASS: 184 at 78% coverage |
| Engine | Ruff, mypy, and credential-free pytest suite | PASS: 223; 1 explicitly live-gated skip |
| Frontend unit | Vitest | PASS: 18 |
| Frontend browser | Playwright against isolated services | PASS: 70 |
| Generated client | `scripts/generate-client.sh` followed by clean generated diff | PASS |
| Full stack | Isolated production Compose build, health/import/HTTP smoke checks, teardown | PASS |
| GitHub runner evidence | Runs `29677594896`, `29677594908`, `29677594895`, `29677594894`, `29677594888`, `29677594859`, `29677594915` | Not scheduled: account billing/spending limit |

## Required Secrets

The connected repository currently reports no configured Actions secrets.
Required names are documented in `CONVENTIONS.md`; no values were created,
printed, or committed. Security analysis needs only GitHub's automatic
`GITHUB_TOKEN`. Deployment and backup workflows remain operator-triggered
capabilities until their environment-specific secrets are provisioned.

## Known Issues Loaded

- Ignored paths: 3
- Ignored rules: 3, including one four-fingerprint Gitleaks exception
- Known failing tests: 0
- Skipped workflows: 13, all due the same external Actions billing condition
- Skipped infrastructure: 0

No repository-fixable pipeline failure remains. Restoring GitHub Actions
billing and provisioning only the intended environment secrets will re-enable
remote verification without another code change.

## Handoff

`pipeline -> infra` is the required Phase Transition handoff. Infrastructure
readiness must validate deployment configuration and external prerequisites
before `phasebuild` creates the next implementation phase.

**Next command:** `infra`
