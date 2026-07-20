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
