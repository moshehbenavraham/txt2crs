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
