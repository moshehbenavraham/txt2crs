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

## [1.1.5] - 2026-07-21

### Added

- Added an owner-scoped admission-capacity API and course-workbench strip that
  show truthful rolling-window availability from the durable reservation
  ledger, disable submission when no complete reservation is available, and
  preserve a safe retry path when capacity cannot be displayed.

### Changed

- Increased conservative production admission fallbacks to four jobs per
  owner and ten globally, and documented larger local judge and E2E overrides
  that preserve the same complete-job token and research-cost ratios.

### Deprecated

### Removed

### Fixed

### Security

## [1.1.4] - 2026-07-21

### Added

- Added a content-free active-worker heartbeat to durable job state and the
  owner-scoped progress UI, plus explicit fetched, charged, and accepted source
  accounting on completed results.

### Changed

- Reduced non-terminal job polling to five seconds in visible tabs and 30
  seconds in hidden tabs, and aligned library progress wording with the job
  page's course-building-step terminology.

### Deprecated

### Removed

### Fixed

- Allowed the sandboxed HTML artifact preview's narrow `blob:` frame source in
  the production CSP and added production-Nginx browser coverage for rendering
  without CSP console violations.
- Preserved protected job deep links through sign-in with same-origin
  return-path validation, and kept the answer-key download toggle inside its
  card at the 1280-by-577 desktop breakpoint.

### Security

The complete dated release history through `1.1.3` is preserved in
[`archive/CHANGELOG_20260721.md`](archive/CHANGELOG_20260721.md).
