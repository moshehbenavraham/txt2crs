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

## [1.2.5] - 2026-07-21

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

- Overrode the OpenAPI generator's development-only `js-yaml` dependency to
  patched version `4.3.0`, resolving the public repository's high-severity
  quadratic-CPU advisory without changing the shipped application runtime.

## [1.2.4] - 2026-07-21

### Added

### Changed

- Published the judge-facing repository, synchronized the immutable release
  identity and links, and completed the GitHub, YouTube, and Devpost field
  handoff from the repository's reviewed submission evidence.

### Deprecated

### Removed

### Fixed

### Security

- Audited the complete Git history before publication and enabled GitHub secret
  scanning, push protection, vulnerability alerts, and automated security
  updates for the public repository.

The complete dated release history through `1.2.3` is preserved in
[`archive/CHANGELOG_20260721.md`](archive/CHANGELOG_20260721.md).
