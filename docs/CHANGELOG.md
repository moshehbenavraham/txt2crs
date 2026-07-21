# Changelog

All notable changes to txt2crs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Archived entries are stored in [`archive/`](archive/).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.1.0] - 2026-07-21

### Added

- Added an authenticated `My courses` library with owner-scoped, stable cursor
  pagination; exhaustive active, ready, failed, and cancelled states; direct
  job reopening; persistent desktop/mobile navigation; visibility-aware
  polling; and accessible loading, empty, error, and pagination recovery.
- Added the package-owned bounded job-summary query and `GET /api/v1/jobs`
  shell contract with owner isolation, opaque cursors, private/no-store
  responses, generated frontend client support, and cross-stack regression
  coverage.

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.0.5] - 2026-07-21

### Added

- Added a read-only monitoring record for the observed course-building job,
  including its durable checkpoint timeline, terminal outcome, and suggested
  validation follow-up.

### Changed

### Deprecated

### Removed

### Fixed

- Kept the reviewed Codex device-auth URL visible and clickable in the
  Dedicated identity setup card across signed-out, waiting, authenticated,
  and failed authentication states.
- Added live backend checkpoint visibility to active course jobs, including a
  confirmed-progress meter, one-second elapsed time, latest checkpoint and
  polling freshness, and a clearly labeled pace-based completion estimate.

### Security

## [1.0.4] - 2026-07-21

### Added

### Changed

### Deprecated

### Removed

### Fixed

- Kept the public system-readiness input-mode contract synchronized with the
  engine's optional image, audio, and video adapters so an enabled media
  source no longer turns the System setup workspace into an HTTP 500/CORS
  fallback, and added complete setup labels for those capabilities.

### Security

## [1.0.3] - 2026-07-21

### Added

### Changed

### Deprecated

### Removed

### Fixed

- Reconciled PostgreSQL role passwords with the current local `.env` during
  judge startup so preserved database volumes no longer leave `prestart`
  retrying authentication for five minutes; the recovery preserves records and
  does not print the configured secret.
- Moved the one-shot Playwright container behind its explicit `test` profile so
  a successful test-runner exit no longer makes ordinary Compose health waiting
  report a healthy deployment as failed.

### Security

## [1.0.2] - 2026-07-21

### Added

### Changed

- Registered and synchronized all 18 txt2crs host-bound ports across the
  central workstation map, Compose, host development, browser tests, startup
  validation, and operator documentation.

### Deprecated

### Removed

### Fixed

### Security

## [1.0.1] - 2026-07-20

### Added

- Added a judge-facing `scripts/start-local.sh` assistant with ASCII branding,
  inert `.env` validation, Docker and Compose preflights, foreign port
  detection, health-waiting startup, bounded failure diagnostics, status and
  stop modes, and exact setup handoff instructions.

### Changed

- Replaced the donor-era clean rebuild helper with a safe compatibility wrapper
  and made the startup assistant the primary README, onboarding, and local
  deployment path.
- Clarified and cross-linked the canonical Docker/judge, host-backend, and
  host-frontend environment templates so each workflow names its source of
  truth and intended copy location.

### Deprecated

### Removed

- Removed judge-path global Docker cache pruning, hardcoded donor container and
  volume names, destructive reset mode, and fixed sleeps.

### Fixed

### Security

- The startup assistant never sources `.env`, prints configured secrets,
  deletes persistent volumes, or prunes unrelated Docker state.

## [1.0.0] - 2026-07-20

The complete dated release history is preserved in
[`archive/CHANGELOG_20260720.md`](archive/CHANGELOG_20260720.md).
