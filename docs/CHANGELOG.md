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

## [0.5.4] - 2026-07-19

### Added

- Added authenticated cached readiness and superuser-only device
  authentication start/status routes with strict browser-safe response
  schemas, finite rate limits, semantic RFC 9457 errors, and generated
  TypeScript operations.
- Added a lifecycle-owned authentication coordinator that refreshes persisted
  account state once and retains the shared runtime lease for the complete
  background device ceremony.

### Changed

- FastAPI now starts authentication before readiness and the serial worker,
  then closes the worker, readiness, authentication, runtime gate, and engine
  facade in dependency-safe reverse order.
- Exported the engine facade's existing safe authentication contracts through
  the public application boundary.

### Fixed

- Prevented pre-lifecycle authentication calls from stranding runtime
  ownership without a monitor.
- Reported initial runtime contention as an explicit safe failed auth state
  instead of a misleading signed-out result.
- Removed private provider exception context from translated route failures.

### Security

- Restricted device start and status to current superusers while readiness
  remains available only to active authenticated users.
- Limited authentication responses and events to finite state, the validated
  OpenAI verification URL, bounded user code, safe message, and reason codes;
  account identity, tokens, provider payloads, paths, and exceptions remain
  excluded.

## [0.5.3] - 2026-07-19

### Added

- Added one public aggregate engine-readiness projection for authentication,
  exact GPT-5.6 discovery, managed research, SQLite, artifacts, P0 inputs, and
  conservative admission capacity.
- Added one immutable stale-while-busy shell readiness cache with immediate
  startup inspection, finite maintenance refresh, explicit freshness, and
  side-effect-free reads.
- Added one shared finite runtime owner for readiness, authentication, and
  serial job execution.
- Added semantic system/job error codes and context-free public engine
  exception translation.

### Changed

- FastAPI now starts readiness before the serial worker and closes worker,
  readiness, runtime ownership, and the engine facade in reverse order.
- The serial worker now holds runtime execution ownership from durable
  discovery through executor cleanup.

### Fixed

- Prevented a closed readiness coordinator from relaunching provider work
  during teardown.
- Enforced exact GPT-5.6 identity at readiness-contract construction and
  reported runtime contention as degraded instead of unavailable.

### Security

- Removed raw request paths, queries, client addresses, provider responses,
  exception details, tracebacks, recipient identities, and infrastructure
  locations from reviewed normal shell operational logs.
- Added rollback-only SQLite and confined atomic artifact probes that leave no
  persistent maintenance state.

## [0.5.2] - 2026-07-19

### Added

- Added one FastAPI-owned serial worker that immediately recovers durable
  runnable jobs, polls on a finite interval, accepts latency-only nudges, and
  executes one public owner/job-bound handle at a time.
- Added an immutable content-free worker snapshot for liveness, active work,
  capacity, shutdown, and bounded failure state.
- Added structured worker and execution lifecycle events with fixed names and
  finite reason codes.

### Changed

- Distinguished application-shutdown interruption from learner-requested
  cancellation so checkpointed non-terminal work remains restartable.
- Changed FastAPI cleanup to stop the worker before closing the public engine
  facade while preserving earlier startup and request errors.

### Fixed

- Reset supervisor state after operating-system thread creation fails, making
  partial-startup cleanup idempotent.
- Prevented shutdown races from claiming a second job after discovery or
  executor construction.

### Security

- Kept job IDs, owner IDs, request content, provider details, exception text,
  credentials, and filesystem paths out of worker snapshots and events.
