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

## [1.2.1] - 2026-07-21

### Added

- Added a cross-format publication design system with branded covers,
  publication-specific accents, responsive and print-aware HTML, searchable A4
  PDFs with outlines and folios, styled native DOCX templates, format-native
  code treatment, and printable assessment fields and response space.
- Added structural design regression coverage and a public-safe `1.2.1`
  inspection record covering browser, PDF page-image, and LibreOffice DOCX
  rendering.

### Changed

- Replaced browser-default HTML, fixed-width text PDF output, and default Word
  templates with offline, deterministic, format-native editorial layouts while
  preserving canonical content, private delivery, and student/instructor
  answer separation.
- Upgraded the deliverable-system reference from a low-fidelity baseline into
  the implemented publication design contract, quality matrix, verification
  evidence, and bounded improvement roadmap.

### Deprecated

### Removed

### Fixed

- Preserved canonical code blocks as fenced Markdown, monospaced PDF blocks,
  and styled Word code paragraphs, and preserved source links as visible print
  targets plus native PDF and DOCX link relationships where supported.

### Security

## [1.1.6] - 2026-07-21

### Added

- Added a permanent deliverable-system reference covering canonical output,
  deterministic rendering, format baselines, private storage, integrity,
  preview isolation, delivery, quality evidence, and future change control.
- Added a fail-closed backend test-database preflight, CI test-database
  selection, a run-owned SQLite account store for deterministic browser tests,
  and regression coverage for database isolation, UUID token subjects, admin
  loading identity, permanent-error polling, artifact downloads, and visible
  previews.

### Changed

- Made the project-root environment canonical for default Playwright runs,
  removed local backend reload from the judge-facing Compose stack, compacted
  the landing hero to retain its action at laptop height, and added an
  immediate accessible loading shell to the admin route.
- Consolidated enduring architecture, API, engine-quality, security,
  operations, testing, and product requirements from the completed
  planning and validation records into primary documentation, without deleting
  those source records pending manual review.

### Deprecated

### Removed

### Fixed

- Replaced temporary object-URL HTML preview navigation with sandboxed
  sanitized `srcdoc`, stopped missing jobs from polling after permanent read
  errors, and normalized JWT subjects to UUID values for cross-dialect account
  queries.

### Security

- Prevented application tests and deterministic browser authentication from
  reusing or destructively cleaning a normal local PostgreSQL database.

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
