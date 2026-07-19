# Changelog

All notable changes to txt2crs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Archived entries are stored in [`archive/`](archive/).

## [Unreleased]

### Added

- Added a stable frontend `/health` JSON endpoint, Docker image health check,
  and static local deployment scope contracts.
- Added ADR-0008 to establish repository-root Docker Compose as the only
  current deployment target.

### Changed

- Reconciled root, architecture, API, environment, package, onboarding,
  development, deployment, security, and runbook documentation with the
  completed Phase 00 implementation.
- Clarified that `staging` and `production` are inactive runtime validation
  profiles, not deployed environments.

### Deprecated

- Superseded the inherited Coolify architecture decision with the local-only
  deployment decision.

### Removed

- Removed inherited hosted deployment and scheduled remote-backup workflows,
  the Coolify deployment script, and platform-specific example variables.

### Fixed

- Corrected the frontend Docker build argument so local BuildKit validation no
  longer reports an undefined self-reference.

### Security

- Documented request-log privacy risk, complete local backup/restore gaps, and
  the missing private vulnerability-reporting channel without inventing
  external owners or infrastructure.

## [0.3.3] - 2026-07-19

### Added

- Added typed, normalized, and confined txt2crs state, SQLite, artifact,
  isolated Codex home, and worker path settings with 19 deterministic tests.
- Added static container/Compose contracts and a real production-image smoke
  for workspace import, non-root identity, private modes, and persistent state
  reopen.
- Initialized the Apex specification system and completed, reviewed, and
  validated Phase 00: Application Baseline.

### Changed

- Corrected both backend image targets to install the workspace engine before
  synchronization and run one FastAPI process as fixed UID/GID 1001.
- Added a separate image-owned txt2crs state volume to Compose while keeping
  the research MCP port unpublished.
- Replaced donor product identity in public metadata, routes, logo assets, and
  the footer with shared txt2crs branding.
- Removed learner-visible TanStack devtool launchers and their unused direct
  dependencies.

### Fixed

- Pinned container state paths to the image-owned mount point so a fresh named
  volume remains writable by the non-root runtime.
- Isolated Settings tests from inherited txt2crs path variables and expanded
  repository validation to lint, format, and execute the baseline contracts.
- Taught the project-local prerequisite script to recognize the nested uv
  workspace and registered package stack hints.

### Security

- Enforced owner-only private state and worker directories, rejected relative,
  escaping, overlapping, and existing-symlink path layouts, and verified that
  no credentials are required by deterministic validation.
