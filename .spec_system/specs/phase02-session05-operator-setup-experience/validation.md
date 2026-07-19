# Validation Report

**Session ID**: `phase02-session05-operator-setup-experience`
**Package**: frontend
**Validated**: 2026-07-19
**Result**: PASS

## Validation Summary

| Check | Status | Notes |
|-------|--------|-------|
| Code Review | PASS | `code-review.md` records `Result: RESOLVED`; all 4 Medium and 2 Low findings are fixed |
| Tasks Complete | PASS | 25/25 tasks complete |
| Files Exist | PASS | Every declared component, route, test, design, review, and session deliverable exists |
| Source Encoding | PASS | New frontend source/test files are ASCII with Unix LF; existing UTF-8 design typography remains intentional |
| Frontend Tests | PASS | 33 unit and 76 browser tests passed |
| Complete Deterministic Tests | PASS | 869 passed across shell, engine, frontend unit, and frontend E2E; 1 explicit live gate skipped |
| Database/Schema Alignment | PASS | No SQLModel, Alembic, SQLite schema, query, or persisted-shape change |
| Success Criteria | PASS | All functional, testing, non-functional, and quality criteria have evidence |
| Conventions | PASS | Tests-first, generated ownership, route authorization, comments, query boundaries, and protected primitives comply |
| Security & GDPR | PASS | Session minimization and browser security pass; cumulative remote CodeQL limitation remains tracked |
| Rendered Product Quality | PASS | Light/dark, 1440/375/320, keyboard, reduced motion, long values, console, landmarks, and overflow inspected |
| Release | PASS | Repository/package `0.6.0`, lockfile, archived changelog, built wheel/sdist, and phase records agree |

**Overall**: PASS

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence |
|-------|-----------------------|--------|----------|
| Code review | Complete base-to-head review and repaired report | PASS | 0 critical, 0 high, 4 fixed medium, 2 fixed low |
| Task completion | Session task and criterion counts | PASS | 25 tasks; no unchecked session/phase criterion |
| Focused frontend | Vitest plus setup Playwright | PASS | 33 unit; 7 focused browser including auth setup |
| Complete frontend | `npm run test:unit` and `npm run test:e2e` | PASS | 33 + 76 passed |
| Complete shell | Fresh isolated PostgreSQL DB, Alembic head, `uv run pytest tests/ -q` | PASS | 296 passed; 71 existing short test-key warnings |
| Complete engine | `uv run --package txt2crs pytest -q` | PASS | 464 passed; 1 explicit GPT-5.6/Tavily live test skipped |
| Frontend static/build | Biome, TypeScript no-emit, Vite production build | PASS | 138 files; no type error; 2,204 modules built |
| Generated contract | Repository generated-client hook and final diff | PASS | No generated API client drift |
| Real shell | Authenticated `/setup` against current local backend | PASS | Readiness and auth status HTTP 200; truthful unavailable state |
| Rendered QA | Playwright metrics plus inspected PNGs | PASS | One main, zero overflow, no console issues, full message/code/recovery |
| Security scan | Production added-line sinks, auth order, external-link attributes | PASS | No sink/secret marker; superuser guard precedes queries; noreferrer link |
| Dependencies/schema | Base-to-head manifest, lock, primitives, models, migrations | PASS | Only engine version changed in package/lock; no dependency or schema change |
| Package build | `uv build` and archive metadata/content inspection | PASS | Wheel/sdist `0.6.0`; README, license, notices, and pyproject present |
| Repository gate | `pre-commit run --all-files` | PASS | Backend, frontend, generated-client, and workflow hooks pass |
| Encoding/integrity | New-source ASCII, base-to-head CRLF, `git diff --check` | PASS | No new source non-ASCII, no CRLF, no whitespace defect |

## Code Review Gate

### Status: PASS

Formal review found and resolved six issues:

1. Initial authenticated StrictMode mounts performed redundant readiness
   invalidations.
2. Safe backend authentication messages inherited a one-line clamp.
3. The longest allowed device code overflowed at 320px.
4. Terminal announcements retained stale copy feedback.
5. Repeated safe API values could collide as React keys.
6. Readiness/check status columns squeezed mobile descriptions into word
   columns despite zero numeric overflow.

Every repair was observed failing before implementation. The final focused
setup suite passes 7/7 and `code-review.md` records `Result: RESOLVED`.

## Test Results

### Status: PASS

| Layer | Passed | Failed | Skipped |
|-------|-------:|-------:|--------:|
| Backend shell | 296 | 0 | 0 |
| Engine | 464 | 0 | 1 live-gated |
| Frontend unit | 33 | 0 | 0 |
| Frontend browser | 76 | 0 | 0 |
| **Total deterministic** | **869** | **0** | **1 live-gated** |

The first shell run used the browser-test database, where more than 100
created users pushed a test's deliberately old fixtures beyond the default
page. That environment-only run had 295 passes and one pagination-fixture
failure. A fresh isolated database was created, migrated to Alembic head,
tested at 296/296, and removed.

An unscoped engine `ty check` traversed the parent uv workspace and surfaced
known shell-test typing diagnostics outside the engine source gate. The
repository's configured backend `ty` hook passed, and the engine-scoped
`ty check src` passed. Ruff and strict mypy passed across all 138 engine
source/test files.

The live acceptance test remains behind `TXT2CRS_RUN_LIVE_CODEX=1` and
requires real ChatGPT/Tavily credentials. It is not part of the deterministic
credential-free gate.

## Success Criteria

### Functional Requirements

- [x] Only superusers navigate to/load `/setup`; denial occurs before system
  endpoint access.
- [x] Readiness and auth status start in parallel and render only generated
  safe fields.
- [x] Signed-out operators can start one ceremony and use the approved URL,
  bounded code, and safe message.
- [x] Waiting status polls at one second and stops at every terminal state.
- [x] Cache updates avoid duplicate client-side server state.
- [x] Authenticated/failed states remove URL/code and retain stable actions.
- [x] Warnings expose only safe recovery copy and the exact CLI command.
- [x] Refresh reloads both caches without changing auth session or route.

### Testing And Non-Functional Requirements

- [x] Tests and all formal-review regressions failed before implementation.
- [x] Focused and complete frontend suites pass.
- [x] No dependency, generated client, protected primitive, API, or database
  implementation changed.
- [x] Independent requests avoid waterfalls and terminal traffic stops.
- [x] Light/dark desktop, 375px, and 320px states are readable with no
  document overflow.
- [x] Touch, focus, heading, landmark, live status, external link, and reduced
  motion contracts pass.
- [x] Existing tokens/primitives produce one coherent editorial operator
  experience.

### Quality Gates

- [x] New frontend source/test files are ASCII with Unix LF.
- [x] Intern-friendly comments cover authorization, query/cache/polling,
  privacy, list stability, and accessible terminal state.
- [x] Biome, TypeScript, Vite, Playwright, repository hooks, package build,
  and rendered QA pass.

## Rendered Product Validation

### Status: PASS

Inspected screenshots:

- `/tmp/txt2crs-session05-ready-desktop.png`
- `/tmp/txt2crs-session05-waiting-desktop.png`
- `/tmp/txt2crs-session05-unavailable-mobile-dark.png`
- `/tmp/txt2crs-session05-long-code-320.png`
- `/tmp/txt2crs-session05-real-unconfigured.png`

The repaired 320px case measures 230px for readiness description width and
152px for check descriptions. The 64-character code and document both have
zero overflow. All mocked and real cases have one `main`, correct title/H1,
and no console warning/error. The failed auth message reports
`webkitLineClamp: none`.

## Database, Dependency, And Generated Alignment

### Status: PASS

- No application model, Alembic source, engine migration, query, or persisted
  record shape changed.
- No JavaScript/Python dependency specification changed.
- `backend/uv.lock` changed only for the local `txt2crs` version from `0.5.4`
  to `0.6.0`.
- `frontend/src/client/`, `frontend/src/components/ui/`, and dependency
  manifests have no base-to-head diff.
- `frontend/src/routeTree.gen.ts` was generated by the Vite/TanStack route
  plugin and contains only `/setup` registration.

## Security And GDPR

### Status: PASS

See `security-compliance.md`.

| Area | Status | Findings |
|------|--------|----------|
| Session security | PASS | 0 unresolved |
| Authentication/authorization | PASS | Active session plus superuser route gate before system reads |
| Data minimization | PASS | Generated coarse allowlist; transient code only |
| Browser persistence | PASS | No new durable browser write |
| New GDPR processing | N/A | No learner-data collection, storage, transfer, or retention |
| Cumulative known finding | AT RISK | Remote CodeQL remains blocked by GitHub Actions billing |

## Release Validation

### Status: PASS

- Root `VERSION`: `0.6.0`.
- Engine `pyproject.toml`: `0.6.0`.
- Backend lock local package: `0.6.0`.
- `docs/VERSIONING.md` and
  `docs/archive/CHANGELOG_20260719.md`: `0.6.0`.
- Wheel metadata: `Version: 0.6.0`.
- Source archive includes README, license, notices, and pyproject.
- Phase 02 PRD/state/plan: 5/5 complete.

## Validation Result

### PASS

Session 05 satisfies every declared requirement with complete frontend,
cross-package deterministic, static, security, privacy, generated-contract,
rendered, real-shell, package-build, release, and workflow evidence.

### Unresolved Failures And Blockers

None for the session.

## Next Steps

Plan Phase 03 durable jobs API and worker execution before implementation.
