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
