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
| `backup-db.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; workflow syntax and action pins were validated locally, but no backup was requested or run. | 2026-07-19 |
| `deploy-coolify.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; workflow syntax and action pins were validated locally. | 2026-07-19 |
| `deploy-production.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; workflow syntax and action pins were validated locally, but no production deployment was requested or run. | 2026-07-19 |
| `deploy-staging.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; workflow syntax and action pins were validated locally. | 2026-07-19 |
| `detect-conflicts.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; workflow syntax, immutable action pin, and current no-PR state were validated locally. | 2026-07-19 |
| `generate-client.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; deterministic generation and a clean generated-client diff were validated locally. | 2026-07-19 |
| `guard-dependencies.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; workflow syntax and immutable action pin were validated locally. | 2026-07-19 |
| `playwright.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; all 70 browser tests passed against isolated local services. | 2026-07-19 |
| `quality.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; backend, engine, and frontend equivalents passed locally. | 2026-07-19 |
| `security.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; Gitleaks and both dependency audits passed locally, while CodeQL remains remote-only. | 2026-07-19 |
| `test-backend.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; all 184 backend tests passed at the measured 78% coverage baseline. | 2026-07-19 |
| `test-docker-compose.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; an isolated full-stack Compose build and HTTP smoke test passed locally. | 2026-07-19 |
| `zizmor.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; local Zizmor validation passed for every workflow. | 2026-07-19 |

## Skipped Infra

| Item | Reason | Added |
|------|--------|-------|
