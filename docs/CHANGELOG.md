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
