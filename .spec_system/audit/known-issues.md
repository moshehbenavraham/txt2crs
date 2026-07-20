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
| `detect-conflicts.yml` | Run 29742715755 failed with zero steps because Actions billing is disabled; the current no-open-PR state, actionlint, and pedantic Zizmor checks pass locally. | 2026-07-19 |
| `generate-client.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; current deterministic generation passes through the all-file hook with a clean client diff. | 2026-07-19 |
| `guard-dependencies.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; actionlint, pedantic Zizmor, immutable pins, and the no-open-PR state pass locally. | 2026-07-19 |
| `playwright.yml` | Run 29742715684 failed with zero steps because Actions billing is disabled; all 69 broad browser cases and both 16-test deterministic job scenarios pass locally. | 2026-07-19 |
| `quality.yml` | Run 29742715635 failed with zero steps because Actions billing is disabled; 517 backend, 489 engine, and 132 frontend tests plus lint, types, and build pass locally. | 2026-07-19 |
| `security.yml` | Run 29742715611 failed with zero steps because Actions billing is disabled; 77-commit Gitleaks and both dependency audits pass locally, while CodeQL remains remote-only. | 2026-07-19 |
| `test-backend.yml` | Run 29742715633 failed with zero steps because Actions billing is disabled; all 517 backend tests pass against isolated PostgreSQL 18 at 88% coverage. | 2026-07-19 |
| `test-docker-compose.yml` | Run 29742715687 failed with zero steps because Actions billing is disabled; isolated 1.0.0 images, migrations, health, one-process topology, and durable private state pass locally. | 2026-07-19 |
| `zizmor.yml` | Run 29742715700 failed with zero steps because Actions billing is disabled; actionlint and pedantic Zizmor pass with no finding across all ten workflows. | 2026-07-19 |
| `release.yml` | GitHub-hosted jobs cannot start while Actions billing is disabled; 1.0.0 identity, distributions, images, tests, actionlint, and pedantic Zizmor pass locally. | 2026-07-20 |

## Skipped Infra

None. Repository-root Docker Compose is the complete deployment scope, and
both deployable images passed isolated local health validation on 2026-07-19.
