# PostgreSQL Rendered Artifact Storage Plan

> **Status:** Proposed for future consideration
> **Priority:** P2 - Architecture evolution
> **Last reviewed:** 2026-07-21
> **Estimated delivery:** To be split into focused sessions after approval
> **Primary owners:** Education engine, backend shell, database, and operations

## Objective

Evaluate and, only if the evidence supports it, migrate rendered course
artifacts from the private filesystem into PostgreSQL while preserving the
existing owner-private download contract, deterministic recovery, integrity
checks, deletion semantics, and reusable `txt2crs` package boundary.

The artifacts in scope are the sixteen immutable files produced by each
completed job:

- course, review pack, student assessment, and instructor answer key;
- HTML, Markdown, PDF, and DOCX for each deliverable; and
- the metadata currently held in the private artifact manifest.

This plan is not an approval to change the current storage architecture. The
current filesystem store remains authoritative until an Architecture Decision
Record (ADR), measurements, migrations, and rollback procedure are approved.

Related current sources of truth:

- [Architecture](../ARCHITECTURE.md)
- [Database schema](../database/SCHEMA.md)
- [Deliverable system](../DELIVERABLE_SYSTEM.md)
- [Local-only deployment ADR](../adr/0008-local-only-deployment-scope.md)

## Current Baseline

The application currently has three persistence boundaries:

| Boundary | Current responsibility |
|----------|------------------------|
| PostgreSQL | Shell-owned user identity and authentication data |
| Engine SQLite | Generation requests, jobs, checkpoints, lifecycle events, and delivery state |
| Private filesystem | Immutable rendered artifact bytes and integrity manifests |

Repository-root Docker Compose persists the SQLite database, artifact tree,
and isolated Codex home in the `txt2crs-state` volume. The default complete-job
artifact limit is 100 MiB.

The filesystem store already provides important behavior that a PostgreSQL
implementation must retain:

- non-identifying owner and job storage keys;
- owner-only access;
- complete-set validation before publication;
- immutable, idempotent publication;
- exact byte counts and SHA-256 hashes;
- fail-closed integrity verification on manifest and byte reads;
- bounded streaming without exposing storage locations;
- owner and job deletion; and
- retention purging.

## Why Consider PostgreSQL Storage

PostgreSQL artifact storage may become useful if future requirements include:

- a hosted or multi-replica backend that cannot share one local filesystem;
- one managed backup and disaster-recovery boundary for application records
  and generated publications;
- database-level retention, auditing, and owner-deletion workflows;
- simpler environment replacement without a separate artifact volume; or
- an operator preference for PostgreSQL instead of external object storage.

These are possible benefits, not established facts. For a hosted or
high-volume product, shared object storage may remain more appropriate than
either a local filesystem or PostgreSQL binary storage.

## Decision Gates

Complete these gates before implementation begins.

### 1. Measure Real Artifact Workloads

Record representative and worst-case values for:

- individual HTML, Markdown, PDF, and DOCX sizes;
- complete sixteen-artifact bundle size;
- completed jobs per day and expected retention period;
- concurrent publishes and downloads;
- download throughput and time to first byte;
- PostgreSQL write-ahead log growth;
- backup size, backup duration, and restore duration; and
- memory use when publishing and streaming artifacts.

Use generated test fixtures or owner-approved private samples. Do not commit
learner artifacts or live provider output as benchmark fixtures.

### 2. Compare Storage Representations

Evaluate at least these PostgreSQL representations:

| Option | Advantages | Risks |
|--------|------------|-------|
| `BYTEA` per artifact | Simple transactional rows, ordinary backup tools, direct metadata relationship | Large values can increase WAL, backup size, memory pressure, and database I/O |
| PostgreSQL large objects | Supports incremental access through PostgreSQL APIs | More complex lifecycle, authorization, cleanup, tooling, and connection handling |
| Chunk rows | Bounded application reads and writes without large-object APIs | More rows, more ordering rules, and more complicated integrity and deletion logic |

Compare those choices against the existing filesystem and a future private
object-storage adapter. The ADR must document why the selected representation
wins for the measured workload.

### 3. Choose Migration Scope

Decide between two architectural scopes:

1. **Artifact-only migration:** Keep jobs and checkpoints in engine SQLite,
   but store rendered artifact rows in PostgreSQL. This is the smaller code
   change but creates an intentional cross-database completion workflow.
2. **Unified engine-state migration:** Move engine jobs, checkpoints,
   deliveries, and artifacts into a package-owned PostgreSQL persistence
   implementation. This is substantially larger but can provide a single
   transaction boundary and a clearer path to multiple workers.

Artifact-only migration must not proceed until its crash recovery and
reconciliation rules are demonstrated. A PostgreSQL artifact commit and a
SQLite job-status commit cannot share one ordinary database transaction.

### 4. Approve Operational Limits

Define explicit limits for:

- maximum individual artifact bytes;
- maximum complete-job artifact bytes;
- maximum retained bytes per owner and globally;
- retention duration;
- statement, lock, and streaming timeouts;
- backup and restore objectives; and
- cleanup behavior when capacity is exhausted.

## Proposed Target Contract

The current package and HTTP behavior should remain stable even if the storage
adapter changes.

```text
ArtifactRenderer
  -> validated map of sixteen RenderedArtifact values
  -> package-owned PrivateArtifactStore protocol
  -> PostgreSQL artifact adapter
  -> owner-authorized manifest and byte reader
  -> unchanged FastAPI manifest, preview, and download routes
```

The `txt2crs` package must continue to own artifact validation, immutable
publication, integrity, and lifecycle semantics. FastAPI route handlers must
not execute artifact SQL or reimplement those rules.

The PostgreSQL adapter may be supplied through application composition, but it
must implement a package-owned protocol and return only package-owned
contracts. This keeps storage choice out of the domain and rendering layers.

## Candidate Schema

The final table and column names require an ADR and detailed session spec. A
candidate relational shape is:

### `course_artifact_sets`

One row represents a complete publication set for one owner and job.

| Field | Purpose |
|-------|---------|
| `id` | UUID primary key generated by the application |
| `job_id` | Opaque engine job identifier with a unique constraint |
| `owner_id` | PostgreSQL user UUID used for owner-scoped lookup |
| `schema_version` | Version of the stored manifest contract |
| `status` | Bounded `publishing` or `published` lifecycle state if staged rows are required |
| `artifact_count` | Expected and verified artifact count |
| `total_size_bytes` | Bounded complete-set size |
| `payload_hash` | Hash binding the complete set to durable delivery state |
| `created_at` | UTC creation time |
| `retention_until` | Optional indexed expiry time |

Recommended constraints include uniqueness on `(owner_id, job_id)`, positive
bounded sizes, and a foreign key policy that agrees with coordinated owner
purge. Do not rely on a database cascade as the only owner-erasure mechanism.

### `course_artifacts`

One row represents one immutable deliverable-format pair.

| Field | Purpose |
|-------|---------|
| `id` | UUID primary key |
| `artifact_set_id` | Foreign key to `course_artifact_sets` |
| `artifact_id` | Stable value such as `course_pdf` |
| `deliverable` | Course, review pack, assessment, or answer key |
| `format` | HTML, Markdown, PDF, or DOCX |
| `safe_file_name` | Validated download filename |
| `media_type` | Allowlisted response content type |
| `size_bytes` | Exact payload size |
| `content_hash` | `sha256:` integrity value |
| `content` or storage locator | Selected `BYTEA`, large-object, or chunk representation |
| `created_at` | UTC creation time |

Require uniqueness on `(artifact_set_id, artifact_id)` and
`(artifact_set_id, safe_file_name)`. Application validation must still require
the exact sixteen-artifact topology before a set becomes readable.

## Publication and Recovery Flow

For an artifact-only migration, use an idempotent recovery flow:

1. Persist the final canonical engine checkpoint in SQLite.
2. Move the job to `delivering` in SQLite.
3. Render and validate all sixteen artifacts.
4. Begin a PostgreSQL transaction.
5. Insert the owner-scoped artifact set and all artifact rows.
6. Recheck count, total size, names, media types, and hashes.
7. Mark the artifact set published and commit PostgreSQL.
8. Record the same stable payload hash in the SQLite delivery row.
9. Move the SQLite job to `completed`.

Recovery must handle both partial-order failures:

- If SQLite says `delivering` and PostgreSQL has no published set, rerun the
  deterministic render and publication operation.
- If PostgreSQL contains the identical published set but SQLite is still
  `delivering`, verify the payload hash, reuse the set, and finish the SQLite
  delivery transition.
- If the stored identity, topology, or hashes differ, fail closed and require
  reconciliation. Never overwrite a different published set.

Manifest and download reads must authorize the PostgreSQL user before looking
up artifact metadata or bytes. Wrong-owner and missing-artifact behavior must
remain indistinguishable.

## High-Level Delivery Phases

### Phase 0: Evidence and ADR

- Benchmark representative artifact workloads and operational costs.
- Compare `BYTEA`, large objects, chunk rows, filesystem, and object storage.
- Choose artifact-only or unified engine-state scope.
- Record the accepted decision, constraints, and rejected alternatives in a
  new ADR.

Exit criterion: owner approval of the ADR and measured capacity envelope.

### Phase 1: Contracts, Tests, and Schema

- Write failing package contract tests for PostgreSQL publication, replay,
  reads, integrity failures, deletion, and retention.
- Write failing shell integration tests for owner isolation and streaming.
- Add SQLModel or SQLAlchemy models in the correct persistence adapter.
- Add an Alembic migration with reviewed upgrade and downgrade behavior.
- Add indexes and constraints proven by query plans and integration tests.

Exit criterion: the schema and red tests define behavior without changing the
active filesystem store.

### Phase 2: PostgreSQL Adapter

- Implement the package-owned artifact-store and reader protocols.
- Preserve complete-set atomicity and idempotent replay.
- Stream artifact bodies in bounded chunks without loading unrelated rows.
- Verify size and SHA-256 integrity before serving bytes.
- Implement job deletion, owner purge, and retention cleanup.

Exit criterion: the adapter passes the same behavioral contract as the
filesystem implementation plus PostgreSQL-specific failure tests.

### Phase 3: Application Composition and Readiness

- Add a validated storage-mode configuration with filesystem as the initial
  default.
- Compose the PostgreSQL adapter once during FastAPI lifespan.
- Extend readiness with bounded artifact-table connectivity and permission
  checks that do not create learner-shaped records.
- Preserve existing API schemas, URLs, privacy headers, and error codes.
- Add safe structured events using the required `{domain}.{action}_{state}`
  naming pattern without logging artifact data or database details.

Exit criterion: new jobs can use either store in isolated tests without route
or frontend changes.

### Phase 4: Existing Artifact Migration and Cutover

- Build an idempotent migration utility that reads only verified filesystem
  manifests and files.
- Import in bounded batches and compare every artifact hash and byte count.
- Produce aggregate migration counts without logging owner identity, filenames,
  hashes, paths, or artifact content.
- Choose one documented cutover method:
  - pause submissions and workers for a final bounded delta migration; or
  - use temporary dual writes with one explicitly authoritative store and a
    reconciliation queue.
- Switch reads only after every expected set is verified in PostgreSQL.
- Keep the filesystem copy read-only for a bounded rollback window.

Exit criterion: all migrated sets match exactly and new publications use
PostgreSQL as the declared source of truth.

### Phase 5: Operations, Security, and Cleanup

- Extend complete backups and restores to include artifact tables or large
  objects, then test full restoration.
- Measure WAL, database growth, vacuum behavior, connection use, and download
  performance under expected load.
- Test owner deletion, retention, concurrent download, database interruption,
  and process replacement.
- Document incident response, capacity alerts, and repair procedures.
- Remove filesystem artifacts only after the rollback window and an explicit,
  recoverable cleanup decision.

Exit criterion: restore, rollback, privacy, capacity, and deletion evidence is
recorded before filesystem retirement.

## Testing and Validation

The implementation should include tests for:

- exact sixteen-artifact publication in one committed set;
- rejection of partial, duplicate, oversized, or malformed sets;
- byte-for-byte HTML, Markdown, PDF, and DOCX round trips;
- tampered metadata, size, hash, or payload detection;
- idempotent retry after PostgreSQL or process failure;
- the PostgreSQL-committed/SQLite-incomplete recovery case;
- owner isolation and indistinguishable missing/foreign reads;
- bounded memory and connection cleanup on successful, cancelled, and failed
  downloads;
- concurrent publish/read/delete behavior;
- retention and coordinated account deletion;
- Alembic upgrade, downgrade, and re-upgrade on disposable PostgreSQL;
- complete backup and restore; and
- existing frontend preview and download behavior without API changes.

At minimum, run the backend test suite against a disposable database whose name
starts with `test_` or ends with `_test`. Never run destructive migration or
cleanup tests against a normal development database.

## Rollback Strategy

Before cutover, PostgreSQL mode can be disabled because the filesystem remains
authoritative.

After cutover, rollback requires all of the following:

1. Stop new publication work.
2. Verify that the retained filesystem copy covers every job created before
   cutover.
3. Export and verify any PostgreSQL-only artifact sets back to the filesystem.
4. Switch the configured reader and writer together.
5. Resume work only after manifest, download, owner-purge, and restart checks
   pass.

Do not downgrade the database schema while PostgreSQL remains the only copy of
any artifact. Schema cleanup belongs in a later release after rollback data is
verified and retention obligations are satisfied.

## Primary Risks

| Risk | Required mitigation |
|------|---------------------|
| PostgreSQL and SQLite disagree about completion | Stable payload hashes, idempotent publication, startup reconciliation, and fail-closed mismatch handling |
| Artifact traffic affects authentication queries | Capacity measurements, connection-pool separation where justified, statement timeouts, and load tests |
| WAL and backups grow unexpectedly | Workload forecast, compression decision, retention limits, monitoring, and restore drills |
| Downloads hold database resources too long | Bounded chunks, cancellation-safe cleanup, timeouts, and concurrency tests |
| Database rows are deleted without engine coordination | Package-owned owner purge plus explicit foreign-key and retry policy |
| The shell duplicates engine persistence rules | Package-owned protocols, contracts, and adapter semantics |
| Migration exposes private data | Owner-scoped reads, aggregate-only logs, encrypted backups, and restricted database roles |

## Open Questions

1. Is the goal local backup simplification, hosted scaling, operator preference,
   or a requirement to keep all user data in one database?
2. What are the measured median, p95, and maximum artifact sizes?
3. How many completed jobs and retained bytes are expected per day?
4. Must downloads support HTTP range requests in the future?
5. Is a short maintenance-window cutover acceptable?
6. Should artifact migration happen independently, or only as part of replacing
   the SQLite job store for multi-worker operation?
7. What recovery-point and recovery-time objectives apply to generated files?
8. Would managed private object storage satisfy the future requirement with
   lower PostgreSQL operational risk?

## Recommendation

Keep the current filesystem implementation for the present local-only scope.
Revisit this plan when hosted deployment, multiple backend replicas, or a
single-database operational requirement becomes concrete.

If PostgreSQL remains the preferred future destination, begin with Phase 0.
Do not select `BYTEA`, large objects, or chunk rows without workload evidence,
and do not implement an artifact-only move without explicit cross-store
recovery semantics.
