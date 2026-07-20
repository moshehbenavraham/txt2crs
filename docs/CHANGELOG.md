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
- Added authenticated owner-scoped job/result polling, canonical artifact
  manifests, integrity-verified downloads, and deterministic restart/delivery
  acceptance.
- Added engine-first account erasure for self-service and administrative user
  deletion, including active-work settlement, retryable safe failures, and
  real cross-store acceptance coverage.
- Added a tested Alembic head revision that removes the donor item table and
  recreates its exact empty prior schema on one-revision downgrade.

### Changed

- Synchronized Phase 02 operator, architecture, configuration, security, and
  recovery documentation with the released composition and readiness system.
- Made public signup an explicit local-only opt-in and documented its disabled
  response in OpenAPI.
- Made artifact response media format-accurate in OpenAPI and the generated
  `string | Blob | File` client contract.
- Made account-deletion OpenAPI explicit about retryable purge failures,
  partial progress, and retained log/backup boundaries.
- Kept administrative validation tools read-only and rooted in the current
  backend checkout.

### Deprecated

### Removed

- Removed the temporary Item API, SQLModel/CRUD/error contracts, PostgreSQL
  table, backend tests/guidance, admin MCP item tools, obsolete documentation,
  and generated frontend client operations.

### Fixed

- Preserved primary artifact-stream failures while closing entered package
  contexts exactly once across disconnect, iterator, send, and construction
  failures.

### Security

- Hardened upload framing, metadata Unicode handling, OOXML archive path
  validation, and terminal idempotent replay behavior.
- Enforced indistinguishable missing/foreign-owner job and artifact reads,
  path-free bounded projections, and private/no-store delivery headers.
- Prevented PostgreSQL identity deletion until engine-owned jobs,
  checkpoints, delivery records, artifacts, and active executor work are
  purged through the public package facade.
