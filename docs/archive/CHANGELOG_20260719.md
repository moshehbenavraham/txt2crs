# Changelog Archive - 2026-07-19

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

## [0.5.1] - 2026-07-19

### Added

- Added owner-only local backup and restore commands that capture PostgreSQL
  plus complete private engine state in one checksum-validated bundle.
- Added bounded shell settings and one FastAPI-owned composition lifecycle for
  the public `txt2crs` application facade.
- Added credential-free configured/unconfigured lifespan tests, exact public
  configuration translation, and exceptional cleanup regressions.

### Changed

- Documented complete local recovery, retention, destructive confirmation, and
  encrypted off-host storage responsibilities.
- Synchronized the project overview, architecture, engine guide, master PRD,
  and system plan with the completed Phase 01 application facade.
- Changed the public engine factory to honor exact confined SQLite/artifact
  paths and keep both job and authentication Codex cwd under the configured
  ephemeral worker root.

### Fixed

- Closed facades acquired before a late startup failure and prevented logging
  failures from skipping shutdown cleanup or masking the primary error.

### Security

- Rejected symbolic links, traversal paths, duplicate archive paths, and
  special files before private engine state is replaced during restore.
- Kept the research MCP numeric-loopback-only, provider secrets redacted, and
  Codex working directories out of durable state and backup bundles.

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

## [0.3.2] - 2026-07-19

### Changed

- Reviewed `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` against the
  repository state: repaired relative links broken by the move into
  `docs/ongoing-projects/`, updated the header status from Proposed to
  Adopted, and recorded per-phase progress (Phase 1 complete;
  Phases 2–4 not started).
- Extended `scripts/validate-changes.sh` with an engine section (ruff, mypy,
  and the credential-free pytest suite for the `txt2crs` package, plus an
  `engine` selector argument), closing the final open Phase 1 step of the
  input-to-course plan.
- Corrected the documented engine validation commands in `AGENTS.md` and
  `backend/packages/txt2crs/README_txt2crs.md` to run from
  `backend/packages/txt2crs/`: run from `backend/`, they resolved the
  application shell's pyproject configuration, whose mypy `exclude` of
  `packages/` silently checked zero engine files.

### Fixed

- Fixed a pre-existing argument-parsing bug in `scripts/validate-changes.sh`
  where passing two section selectors (for example `backend frontend`)
  disabled every section and the script reported success while running zero
  checks; selectors now combine, running exactly the named sections.
- Fixed two mypy 2.3 `comparison-overlap` errors in the engine, in the
  executor's post-generation status re-check and the system authenticator's
  post-refresh state re-check: both compare state that is legitimately
  mutated out-of-band (a nonlocal checkpoint callback and a background
  thread), so the stale-narrowed enum reads are now cast back to their full
  enum types. No behavior change; the 223-test engine suite still passes.

## [0.3.1] - 2026-07-19

### Changed

- Consolidated the implemented dashboard design system into
  `docs/dashboard-design.md` and refreshed the repository-local React visual
  and motion guidance to match the shipped workspace-index interface,
  responsive layouts, semantic motion roles, and reduced-motion behavior.
- Renamed the examples guide to `examples/README_examples.md`, updated its
  context-profile and directory-tree references, clarified root agent
  guidance, and recorded the completed boilerplate adoption decision.
- Organized active planning material, Build Week requirements, the TODO list,
  and the project image under `docs/ongoing-projects/`, updating repository,
  backend, documentation-index, and Make.com plan links to their new paths.

### Removed

- Removed the superseded dashboard design plan and the seven unreferenced
  FastAPI template images from the repository root.

## [0.3.0] - 2026-07-18

### Added

- Added a comprehensive, module-complete reconstruction of the original
  Make.com “Text to Course” system, including its architecture, data contracts,
  prompts, integrations, risks, migration decisions, and a prioritized
  hackathon feature/submission plan.
- Added the input-to-course system plan
  (`docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md`): phased adoption of a custom
  python-react-boilerplate shell, engine wiring, the P0 learner journey with
  a required idempotent completion email and first-class visual-experience
  requirements, and P1 delivery polish.
- Imported the conflict-free application-shell files from
  python-react-boilerplate v0.1.41 (`backend/app/`, `frontend/`, Docker
  Compose files, CI/tooling configuration, examples, scripts, and reference
  docs). Files conflicting with existing repository paths remain unmerged in
  the gitignored `boilerplate/` snapshot.

### Changed

- Merged the remaining boilerplate conflict files: `backend/pyproject.toml`
  is now the application-shell project ("app") and uv workspace root with
  `txt2crs` as a workspace dependency (lockfile regenerated); the root
  README, AGENTS.md, backend README, `.gitignore`, and scoped LICENSE (now
  including boilerplate 0BSD and upstream FastAPI Full Stack Template MIT
  provenance) were combined; root `CLAUDE.md`/`GEMINI.md` symlinks to
  `AGENTS.md` were restored.

## [0.2.1] - 2026-07-17

### Added

- Added app-owned ChatGPT device-code authentication for one dedicated
  hackathon system identity, backed by the packaged official Codex SDK/runtime
  rather than a preinstalled CLI, plus a temporary `txt2crs-system-auth`
  bootstrap entry point for use before the FastAPI setup screen exists.

### Security

- Isolated dedicated-system credentials under an explicit owner-only
  `CODEX_HOME`, forced ChatGPT/file-store authentication, blanked inherited
  API/research keys at the SDK process boundary, validated the OpenAI
  verification origin, and kept provider errors and token material out of
  frontend status.

## [0.2.0] - 2026-07-17

### Added

- Added a separately approved assessment blueprint, module-sized lesson
  contracts, evidence-backed instructor answers, and deterministic assessment
  support checks.
- Added real DOCX output for the course, review pack, student assessment, and
  instructor answer key, bringing private delivery to 16 rendered artifacts.
- Added cumulative per-stage and per-module checkpoints with restored hard
  budgets and worker-replacement resume that skips accepted work.
- Added an atomic private filesystem artifact store with hashed tenant paths,
  integrity manifests, owner-only modes, deletion, and retention purging.
- Added atomic rolling per-user and global admission limits for job count,
  reserved model tokens, and paid research allowance.
- Added a requirement-to-evidence package compliance matrix.
- Added a distinct noisy-extraction case to the fixed private evaluation
  corpus.
- Added private learner-rating, correction-reason, and human-review fields to
  evaluation snapshots while keeping public evaluation output aggregate-only.

### Changed

- Lesson writing now runs one bounded schema turn per approved module and
  assembles the canonical course from the plan and frozen evidence.
- Codex workers now require an explicit isolated `CODEX_HOME`, delegate
  credential refresh through the public SDK, preflight prompt-token capacity,
  and expose safe account/model/quota readiness.

### Security

- Prevented worker credential-directory inheritance, case-variant API-key
  inheritance, cross-tenant artifact paths, symlink reads, quota-reset restarts,
  and oversized prompt side effects.

## [0.3.4] - 2026-07-19

### Added

- Added a strict, versioned `GenerationRequest` and immutable
  `ExecutionProfile` covering exact input, learner intent, policy context,
  supported contract/model versions, retries, and finite execution bounds.
- Added packaged SQLite migration 003 for owner-linked canonical request
  envelopes plus deterministic recovery-first runnable discovery.
- Added atomic request/job/admission persistence, exact restart recovery,
  concurrent idempotency coverage, and lock-scoped resume snapshots.
- Added a stable frontend `/health` JSON endpoint, Docker image health check,
  and static local deployment scope contracts.
- Added ADR-0008 to establish repository-root Docker Compose as the only
  current deployment target.

### Changed

- Replaced caller-supplied input hashes with complete canonical requests across
  the engine store, service, quota, executor, and shared test fixtures.
- Reconciled root, architecture, API, environment, package, onboarding,
  development, deployment, security, and runbook documentation with the
  completed Phase 00 implementation.
- Clarified that `staging` and `production` are inactive runtime validation
  profiles, not deployed environments.

### Deprecated

- Superseded the inherited Coolify architecture decision with the local-only
  deployment decision.

### Removed

- Removed inherited hosted deployment and scheduled remote-backup workflows,
  the Coolify deployment script, and platform-specific example variables.

### Fixed

- Corrected the frontend Docker build argument so local BuildKit validation no
  longer reports an undefined self-reference.
- Normalized request identity before hashing, bounded finite JSON metadata,
  rejected token under-reservation and invalid durable identifiers before
  writes, and made compatibility errors context-free.

### Security

- Documented request-log privacy risk, complete local backup/restore gaps, and
  the missing private vulnerability-reporting channel without inventing
  external owners or infrastructure.
- Kept raw learner input in owner-private engine SQLite, removed validation
  cause/context exposure, enforced owner-scoped recovery, and preserved the
  planned idempotent erasure path.

## [0.3.3] - 2026-07-19

### Added

- Added typed, normalized, and confined txt2crs state, SQLite, artifact,
  isolated Codex home, and worker path settings with 19 deterministic tests.
- Added static container/Compose contracts and a real production-image smoke
  for workspace import, non-root identity, private modes, and persistent state
  reopen.
- Initialized the Apex specification system and completed, reviewed, and
  validated Phase 00: Application Baseline.

### Changed

- Corrected both backend image targets to install the workspace engine before
  synchronization and run one FastAPI process as fixed UID/GID 1001.
- Added a separate image-owned txt2crs state volume to Compose while keeping
  the research MCP port unpublished.
- Replaced donor product identity in public metadata, routes, logo assets, and
  the footer with shared txt2crs branding.
- Removed learner-visible TanStack devtool launchers and their unused direct
  dependencies.

### Fixed

- Pinned container state paths to the image-owned mount point so a fresh named
  volume remains writable by the non-root runtime.
- Isolated Settings tests from inherited txt2crs path variables and expanded
  repository validation to lint, format, and execute the baseline contracts.
- Taught the project-local prerequisite script to recognize the nested uv
  workspace and registered package stack hints.

### Security

- Enforced owner-only private state and worker directories, rejected relative,
  escaping, overlapping, and existing-symlink path layouts, and verified that
  no credentials are required by deterministic validation.
