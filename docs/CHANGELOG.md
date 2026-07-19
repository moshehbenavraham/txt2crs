# Changelog

All notable changes to txt2crs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Archived entries are stored in [`archive/`](archive/).

## [Unreleased]

### Added

- Added owner-only local backup and restore commands that capture PostgreSQL
  plus complete private engine state in one checksum-validated bundle.

### Changed

- Documented complete local recovery, retention, destructive confirmation, and
  encrypted off-host storage responsibilities.
- Synchronized the project overview, architecture, engine guide, master PRD,
  and system plan with the completed Phase 01 application facade.

### Deprecated

### Removed

### Fixed

### Security

- Reject symbolic links, traversal paths, duplicate archive paths, and special
  files before private engine state is replaced during restore.

## [0.5.0] - 2026-07-19

### Added

- Added the public `Txt2CrsApplication` facade for durable submission,
  recovery, runnable discovery, public job/artifact access, safe readiness and
  authentication, owner/job-bound execution, owner erasure, and application
  shutdown.
- Added strict real and deterministic application configurations plus one
  shared factory protocol. Real composition owns the production ingestion,
  policy, persistence, Tavily, managed MCP, exact GPT-5.6 Codex, pipeline,
  rendering, readiness, and authentication graph.
- Added a credential-free deterministic factory that preserves production
  persistence, preparation, pipeline, rendering, artifact, recovery, and
  purge behavior and proves the complete 16-artifact public lifecycle.
- Added artifact-first, retry-safe owner purge across private files and all
  SQLite job, request, admission, checkpoint, and delivery rows.

### Changed

- Changed package assembly guidance to require the supported application
  factory/facade boundary instead of manual private-module composition.
- Added lazy top-level facade/factory discovery without eagerly loading
  optional ingestion or provider dependencies for metadata-only imports.
- Synchronized facade calls, executor cancellation, owner purge, and
  application cleanup so active work settles before resources or owner data
  are removed.

### Fixed

- Rolled back SQLite owner deletion when commit fails and rejected claimed
  success when database triggers suppress parent-row deletion.
- Prevented active delivery from recreating artifacts after owner purge and
  stopped retaining completed executor graphs for the process lifetime.
- Rejected invalid direct deterministic JSON, impossible purge counts,
  symlinked or overlapping private roots, and non-loopback MCP hosts before
  runtime work.
- Removed a coarse-filesystem timestamp assumption from the artifact mutation
  race regression.

### Security

- Kept Tavily secrets, Codex credentials, private paths, owner hashes, raw
  requests, SQL details, provider discovery, and internal errors out of public
  configuration serialization and lifecycle responses.
- Confined owner deletion to hashed private paths, stopped tracked owner work
  before erasure, and made every artifact/database/commit/count failure
  explicit and safe to retry.

## [0.4.0] - 2026-07-19

### Added

- Added a package-owned managed Uvicorn/FastMCP lifecycle that pre-binds an
  explicit numeric loopback listener, verifies the exact two-tool registry,
  publishes only after readiness, and releases the listener on every exit.
- Added an immutable GPT-5.6 model policy for exactly four reviewed family
  slugs, with exact discovery, requested-model, and returned-model checks.
- Added fresh per-job budget/cancellation resources and one managed provider
  session for temporary storage, HTTP, research MCP, and the Codex app-server.
- Added versioned P0 notification state with durable
  `disabled` / `not_applicable` semantics and SQLite migration 004.

### Changed

- Changed the provider-backed pipeline factory to a context-managed boundary
  that remains open through final checkpoint acceptance and result extraction.
- Changed `CodexSubscriptionRuntime` to require the reviewed model policy and
  fail closed when the authenticated account cannot discover the exact target.
- Made package SQLite migration application serialized and atomic with each
  migration-version record.

### Removed

- Removed nullable notification-sink behavior from P0 completion; course
  delivery no longer depends on or calls an email/notification provider.

### Fixed

- Preserved primary generation failures when Codex or external provider
  resource cleanup also fails.
- Prevented transient server readiness, registry failures, shutdown timeouts,
  and unexpected server exits from leaving a published or connectable MCP
  endpoint.
- Kept managed provider resources alive until all returned pipeline values are
  accepted and extracted.

### Security

- Restricted managed research publication to numeric loopback IPs, stripped
  API keys from the Codex child environment, and kept credentials, raw
  provider errors, discovery lists, ports, paths, payloads, and thread details
  out of public readiness and lifecycle errors.
