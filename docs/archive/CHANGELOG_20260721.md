# Changelog Archive - 2026-07-21

All notable changes to txt2crs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Earlier archived entries are stored alongside this file in [`./`](./).

## [1.2.3] - 2026-07-21

### Added

- Added an implementation-ready course-generation logging quality plan covering
  safe event contracts, background correlation, stage and checkpoint timelines,
  failure taxonomy, retry and repair diagnostics, OpenTelemetry spans, privacy
  tests, operational validation, and rollout.
- Added a future PostgreSQL rendered-artifact storage plan covering workload
  decision gates, candidate schemas, cross-store recovery, migration and
  cutover phases, integrity validation, operations, and rollback.

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.2.2] - 2026-07-21

### Added

### Changed

- Made research queries explicitly pursue university, government, standards,
  academic, learning-science, and assessment evidence while the accepted
  research plan's corresponding evidence floor remains unmet.

### Deprecated

### Removed

### Fixed

- Prevented valid course requests from failing after successful Tavily
  collection when relevant research misses a planned authority or education
  source target; generation now continues and discloses the bounded research
  coverage warning in the finished course.
- Prevented detailed model-generated research questions from exceeding the
  provider query contract and failing a job before its first Tavily call.
- Classified regulated international academic and government suffixes
  consistently with their US counterparts.

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

## [1.1.3] - 2026-07-21

### Added

### Changed

### Deprecated

### Removed

### Fixed

- Kept idle worker queue scans from appearing as unavailable runtime ownership
  on the System setup page while preserving busy admission during claimed and
  active course execution.

### Security

## [1.1.2] - 2026-07-21

### Added

### Changed

- Synchronized the repository and reusable Python package release metadata for
  the latest published project snapshot.

### Deprecated

### Removed

### Fixed

### Security

## [1.1.1] - 2026-07-21

### Added

### Changed

- Enforced structured authoritative and education-research source floors before
  freezing evidence, balanced source capacity across every research question,
  classified community and authoritative domains explicitly, and rejected
  canonical or near-mirror duplicates.
- Kept Codex model metadata intact by placing trusted stage policy in developer
  instructions, selected file-backed MCP OAuth state for headless workers, and
  installed system `bubblewrap` in the backend image.

### Deprecated

### Removed

### Fixed

- Canonicalized citation hashes in host code and ran independent citation
  support validation inside each module boundary so invalid drafts are repaired
  before later modules consume time or a checkpoint is committed.
- Rejected duplicated or non-observable learning objectives and required every
  generated module to include an applied example plus explicit misconception
  guidance before course assembly.

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
[`CHANGELOG_20260720.md`](CHANGELOG_20260720.md).
