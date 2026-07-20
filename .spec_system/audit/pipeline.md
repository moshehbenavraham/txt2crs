# Phase 04 Transition Pipeline Report

**Date:** 2026-07-20
**Base revision:** `dac60fea7b5209022fce3b393f1fbb29663e57b7`
**Result:** PASS (local fallback)
**Selected bundle:** Operations
**Platform:** GitHub Actions

## Detection And Strategy

`bash .spec_system/scripts/analyze-project.sh --json` reported a mixed
Python/TypeScript monorepo with Phase 04 complete and no active session. The
repository has no cross-language task runner, so workflows continue to use
package-specific jobs and path-aware triggers.

The Code Quality, Build & Test, Security, and Integration bundles were already
configured across nine workflows. Operations already had Dependabot and an
explicit local-only deployment policy, but it lacked tag-triggered release
validation. This run added that one missing workflow without adding hosted
deployment, publishing permission, or secrets.

`gh pr list --state open --json number,title,statusCheckRollup,reviewDecision`
returned `[]`; there is no open PR, requested change, review comment, or merge
conflict to address.

## Operations Bundle Added

`.github/workflows/release.yml` now:

- runs on `v*` tags or explicit manual dispatch;
- verifies that the tag, root `VERSION`, and engine package version match;
- runs the complete reusable engine suite from its package directory;
- builds and inspects the wheel and source distribution;
- creates SHA-256 checksums;
- runs frontend unit, type, and production-build gates;
- builds and inspects both production images;
- uploads only the inspected workflow artifacts for 14 days;
- uses read-only repository permission, immutable action pins, no cache on the
  artifact-producing job, and no secret or deployment permission.

`.spec_system/CONVENTIONS.md` now records Operations as configured for release
validation while preserving repository-root Docker Compose as the only
deployment target.

## GitHub Run State

The push of `dac60fe` created seven GitHub runs. Each failed within two to
seven seconds with zero executed job steps, matching the existing repository
billing block:

| Workflow | Run ID | GitHub Result | Job-Step Evidence |
|----------|--------|---------------|-------------------|
| `detect-conflicts.yml` | 29718958932 | FAIL (billing) | 0 steps |
| `zizmor.yml` | 29718958923 | FAIL (billing) | 0 steps |
| `playwright.yml` | 29718958918 | FAIL (billing) | filter and gate jobs had 0 steps; test jobs skipped |
| `quality.yml` | 29718958907 | FAIL (billing) | all runnable jobs had 0 steps |
| `test-docker-compose.yml` | 29718958903 | FAIL (billing) | 0 steps |
| `test-backend.yml` | 29718958897 | FAIL (billing) | 0 steps |
| `security.yml` | 29718958870 | FAIL (billing) | all runnable jobs had 0 steps |

`gh run view <id> --json ...` and `--log-failed` produced the job records
above and no execution log. Per the pipeline billing rule, every executable
equivalent was run locally. The ten affected workflow entries in
`known-issues.md` retain the external billing reason and current local
evidence.

## Evidence Ledger

| Workflow | Run / Local Command | Result | Fixes Applied | Remaining / Blocker |
|----------|---------------------|--------|---------------|---------------------|
| `quality.yml` | run 29718958907; local `./scripts/validate-changes.sh --json`, full package suites, and `pre-commit run --all-files` | PASS (local fallback) | None | GitHub billing only |
| `test-backend.yml` | run 29718958897; isolated DB plus `coverage run -m pytest tests/ -q` and `coverage report --fail-under=78` | PASS: 479, 88% | None | GitHub billing only |
| `playwright.yml` | run 29718958918; documented broad Playwright command plus completed/failed job configurations | PASS: 69 broad; 16 each job scenario | None | GitHub billing only |
| `test-docker-compose.yml` | run 29718958903; isolated image build and base-Compose startup for backend/frontend/DB/prestart | PASS | Created temporary external test network because none existed | GitHub billing only |
| `security.yml` | run 29718958870; `gitleaks git --redact --no-banner --log-opts='--all' .`, `pip-audit`, and `npm audit --audit-level=high` | PASS: 55 commits; 0 known dependency vulnerabilities | None | CodeQL is remote-only; GitHub billing |
| `zizmor.yml` | run 29718958923; `uv run zizmor ../.github/workflows` | PASS: all ten workflows | Disabled release-job caches after a red high-severity cache-poisoning result | GitHub billing only |
| `detect-conflicts.yml` | run 29718958932; `gh pr list ...` and Zizmor/actionlint | PASS: no open PR; workflow safe | None | GitHub billing only |
| `generate-client.yml` | local `bash scripts/generate-client.sh` plus clean generated diff | PASS | None | GitHub billing only |
| `guard-dependencies.yml` | `uvx --from actionlint-py actionlint .github/workflows/*.yml`, Zizmor, immutable-pin inspection, no-open-PR check | PASS | None | GitHub billing only |
| `release.yml` | local tag/version script, engine tests/build, distribution inspection/checksums, frontend tests/build, isolated image build/inspect, actionlint, and Zizmor | PASS | Added bundle; disabled setup-uv/setup-node caches after red Zizmor test | GitHub billing only |

## Local Docker Evidence

The local fallback used isolated names:

- project: `txt2crs-phase04-pipeline`;
- images: `txt2crs-phase04-pipeline-backend:dac60fe` and
  `txt2crs-phase04-pipeline-frontend:dac60fe`;
- volumes: project-scoped PostgreSQL and `txt2crs-state`;
- no published host port.

Backend and frontend became healthy, the API reported healthy PostgreSQL, the
backend ran as UID 1001 with one Python application process, the exact private
state volume was mounted, Nginx served its health response, and the production
bundle contained the 5,242,880-byte preview cap. Existing retained services,
volumes, images, and host ports were not used.

## Security And Secrets

- Gitleaks scanned all 55 commits and found no leak.
- Python and npm lockfile audits found no known vulnerability; the two local
  workspace distributions are correctly skipped as non-PyPI packages.
- Zizmor originally rejected the new release workflow because setup action
  caches can poison runtime artifacts. The caches were explicitly disabled,
  and the complete workflow set then passed.
- The new workflow requires no secret.
- Existing `generate-client.yml` retains its documented optional
  `FULL_STACK_FASTAPI_TEMPLATE_REPO_TOKEN` for same-repository PR writes.

## PR Review Status

No open pull request and no review item.

## Handoff

`pipeline -> infra` is the required Phase Transition handoff. `carryforward`
follows only after infrastructure review.

**Next command:** `infra`

**Reason:** the Operations bundle is configured, all ten workflows pass their
local equivalents, the only remote failure is the documented external Actions
billing condition, and no PR review remains.
