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

## [0.3.6] - 2026-07-19

### Added

- Added canonical package-owned routing between supported YouTube transcript
  ingestion and general public URL ingestion.
- Added immutable P0 learning defaults, curriculum limits, prepared preference
  intent, and resolved learning-contract validation.
- Added provider-free two-stage policy preparation with durable sequence-one
  checkpoints and comprehensive routing, policy, preference, and restart tests.

### Changed

- Refactored generation and execution to start from the exact stored request,
  reuse accepted preparation, and construct provider-backed pipelines lazily.
- Extended cumulative checkpoints and public job projection for resolved
  preferences and safe preparation-only progress.

### Fixed

- Rejected transplanted or future-filled checkpoints and settled ordinary
  pipeline-factory failures instead of leaving jobs runnable.
- Aligned custom objective limits and rejected non-string URL normalizer output
  before adapter delegation.

### Security

- Enforced consent and age-group-aware policy before ingestion plus normalized
  content policy before any research or Codex work.
- Kept normalized text, request hashes, policy internals, preferences, provider
  values, and checkpoint dictionaries outside public output and safe errors.

## [0.3.5] - 2026-07-19

### Added

- Added immutable, bounded public job snapshots with safe progress, input,
  failure, source, conflict, and artifact-availability projections.
- Added canonical artifact manifest contracts and owner-scoped,
  context-managed single-artifact streaming from one verified descriptor.
- Added real SQLite/filesystem restart integration coverage plus privacy,
  topology, mutation, cleanup, and deterministic-store regression tests.

### Changed

- Split artifact metadata contracts, confined reads, and atomic lifecycle into
  cohesive query, reader, and store modules.
- Extended `JobService` and its deterministic artifact store with public
  snapshot, manifest, and bounded stream operations.

### Fixed

- Prevented metadata queries from reporting stale body sizes and prevented
  writers from publishing manifests or metadata their readers cannot consume.
- Made in-memory artifact writes atomic across timestamp failures and kept
  failed/cancelled public state internally consistent.

### Security

- Kept raw requests, checkpoint payloads, evidence excerpts, provider data,
  token accounting, filesystem paths, and descriptors outside public output
  and context-free errors.
- Rejected traversal, symlinks, unsafe topology, file/media control
  characters, secret-shaped URL paths, content mutation, and wrong-owner
  artifact access at the package boundary.
