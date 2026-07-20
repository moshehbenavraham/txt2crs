# Known Issues

Intentional exceptions to automated checks. Every entry records why it is
exempt and when it was added. Remove entries that no longer apply.

## Ignored Paths

| Pattern | Reason | Added |
|---------|--------|-------|
| `backend/packages/txt2crs/docs/fixtures/**` | Generated, version-pinned Codex protocol fixtures must retain their source bytes. | 2026-07-19 |
| `make-scenarios/**` | Legacy Make.com blueprints are preserved reference exports, not authored source. | 2026-07-19 |
| `backend/packages/txt2crs/src/txt2crs/evals/fixtures/noisy_extraction.txt` | Deliberately corrupted OCR text is the input to a recovery evaluation. | 2026-07-19 |

## Ignored Rules

| Tool | Rule | Scope | Reason | Added |
|------|------|-------|--------|-------|
| typos | spelling | `backend/app/crud.py` dummy bcrypt hash line | Encoded hash bytes contain a coincidental substring flagged by the spell checker. | 2026-07-19 |
| typos | spelling | `backend/packages/txt2crs/src/txt2crs/research/coordinator.py` conflict regex | An intentional abbreviated regex stem matches supersede variants. | 2026-07-19 |
| Gitleaks | `generic-api-key`, `jwt` | Four commit/path/rule/line fingerprints in `.gitleaksignore` | One example response and three synthetic authentication fixtures match secret shapes; exact fingerprints preserve scanning everywhere else. | 2026-07-19 |

## Known Failing Tests

| Test | Reason | Added |
|------|--------|-------|

## Skipped Workflows

| Workflow | Reason | Added |
|----------|--------|-------|
| `detect-conflicts.yml` | Run 29718958932 failed before any step because Actions billing is disabled; current workflow safety and the no-open-PR state passed locally on 2026-07-20. | 2026-07-19 |
| `generate-client.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; deterministic generation produced a clean OpenAPI/client diff locally on 2026-07-20. | 2026-07-19 |
| `guard-dependencies.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; actionlint, immutable action-pin validation, and the current no-open-PR state passed locally on 2026-07-20. | 2026-07-19 |
| `playwright.yml` | Run 29718958918 failed before any step because Actions billing is disabled; 69 broad browser tests and both 16-test deterministic job scenarios passed locally on 2026-07-20. | 2026-07-19 |
| `quality.yml` | Run 29718958907 failed before any step because Actions billing is disabled; 479 backend, 470 engine, and 132 frontend tests plus lint/types/build passed locally on 2026-07-20. | 2026-07-19 |
| `security.yml` | Run 29718958870 failed before any step because Actions billing is disabled; Gitleaks and both dependency audits passed locally on 2026-07-20, while CodeQL remains remote-only. | 2026-07-19 |
| `test-backend.yml` | Run 29718958897 failed before any step because Actions billing is disabled; all 479 backend tests passed against isolated PostgreSQL at 88% coverage on 2026-07-20. | 2026-07-19 |
| `test-docker-compose.yml` | Run 29718958903 failed before any step because Actions billing is disabled; isolated 0.7.0 backend/frontend images, PostgreSQL, migrations, health checks, one-worker topology, and private volume passed locally on 2026-07-20. | 2026-07-19 |
| `zizmor.yml` | Run 29718958923 failed before any step because Actions billing is disabled; local Zizmor and actionlint validation passed for all ten workflows on 2026-07-20. | 2026-07-19 |
| `release.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; tag/version checks, 0.7.0 distributions and checksums, unit/build gates, production images, actionlint, and Zizmor passed locally on 2026-07-20. | 2026-07-20 |

## Skipped Infra

None. Repository-root Docker Compose is the complete deployment scope, and
both deployable images passed isolated local health validation on 2026-07-19.
