# Changelog

All notable changes to txt2crs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Archived entries are stored in [`archive/`](archive/).

## [Unreleased]

### Added

- Added authenticated, rate-limited JSON and PDF/DOCX/PPTX course-job
  submission APIs with strict schemas, bounded upload validation, atomic
  admission, idempotent replay, and generated frontend client contracts.

### Changed

- Synchronized Phase 02 operator, architecture, configuration, security, and
  recovery documentation with the released composition and readiness system.
- Made public signup an explicit local-only opt-in and documented its disabled
  response in OpenAPI.

### Deprecated

### Removed

### Fixed

### Security

- Hardened upload framing, metadata Unicode handling, OOXML archive path
  validation, and terminal idempotent replay behavior.
