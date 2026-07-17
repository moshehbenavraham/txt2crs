# Changelog Archive — 2026-07-17

All notable changes to txt2crs are documented in this archive.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-dev.0] - 2026-07-17

### Added

- Defined the txt2crs vision: turn almost any source into a researched course,
  review pack, assessment, and answer key.
- Documented the OpenAI Build Week Education-track requirements, deliverables,
  deadline, and submission checklist.
- Preserved the three-stage Make.com proof of concept for intake, customer and
  folder setup, AI content generation, and delivery.
- Designed and scaffolded the standalone Python package, FastAPI boundary,
  adapters, SQLite migrations, observability, security, evaluations, and
  test-first unit, contract, integration, and acceptance suites.
- Derived the target AI pipeline and prioritized requirements for research,
  grounding, structured artifacts, safety, recovery, quality, and accessibility.
- Evaluated the minimum reusable Hermes agent, Codex subscription runtime,
  research, ingestion, citation, and education-pipeline capabilities.
- Added AIOS supplemental guidance for runtime readiness, stage recovery,
  privacy-safe progress, source governance, usage tracking, output QA, and replay.
- Added repository and package documentation indexes, contributor guidance,
  developer notes, project artwork, and TODO/changelog maintenance workflows.
- Added an exportable `txt2crs` Python distribution with package metadata,
  version discovery, build configuration, and a test-first metadata contract.
- Added a virtual backend `uv` workspace that can later host the FastAPI
  boilerplate beside the standalone library.
- Established Semantic Versioning with a machine-readable pre-release version
  and documented release process.
- Released original txt2crs code under MIT-0 while retaining the MIT license
  and required attribution for Hermes-derived portions within
  `backend/packages/txt2crs/`.
- Applied MIT-0 to the rest of the repository with an explicit reference to
  the dedicated `backend/packages/txt2crs/LICENSE` scope.
- Added strict versioned contracts and cross-artifact validation for normalized
  inputs, research plans, evidence, courses, review packs, assessments, and
  answer keys.
- Added prompt, URL, PDF, DOCX, PPTX, image OCR, audio/video transcription, and
  YouTube transcript ingestion with bounded input and source locations.
- Added a subscription-only official Codex SDK adapter with model discovery,
  schema output, cancellation, deadlines, safe streamed events, and truthful
  usage accounting.
- Added a required loopback FastMCP research server with two allowlisted tools,
  a fixed-origin Tavily adapter, URL/DNS/redirect safety, finite retries, and
  repeated-call guardrails.
- Added immutable evidence ledgers, explainable authority/relevance selection,
  prompt-injection segmentation, conflict disclosure, citation hashes, and
  independent lexical grounding checks.
- Added the complete bounded education pipeline with shared run budgets,
  transient retry classification, and exactly one schema-repair turn.
- Added deterministic accessible HTML, Markdown, and searchable PDF output for
  the course, review pack, student assessment, and instructor answer key.
- Added signed-request replay protection, consent and age policy, copyright
  rejection, high-risk review gates, private progress projection, and redaction.
- Added tenant-isolated SQLite jobs, versioned SQL migration resources,
  compare-and-swap checkpoints, crash-resumable private delivery, and an
  idempotent notification outbox.
- Added a fixed 12-category private evaluation corpus, dry-run plans, atomic
  snapshots, path confinement, and aggregate-only result publication.
- Added pinned Codex app-server protocol schemas, deliberate upgrade guards,
  a live ChatGPT/MCP acceptance test, and third-party provenance checks.

### Changed

- Relocated the library source, package documentation, and unit, contract, and
  integration tests under `backend/packages/txt2crs/` so the future backend can
  consume it without sacrificing independent builds or exports.
- Reserved FastAPI routes, application authentication, application database
  models, Alembic migrations, and acceptance tests for the future backend
  application shell.
- Advanced the repository and Python package to `0.2.0-dev.0` /
  `0.2.0.dev0` for the end-to-end library implementation.

### Security

- Removed Platform and research API credentials from Codex worker environments
  and rejected API-key accounts in subscription-only mode.
- Kept source text and generated artifacts private by default, separated
  instructor answers from student forms, and blocked active or remote HTML
  content before delivery.
- Proved the package builds and runs without executable Hermes or AIOS
  dependencies; remaining donor names are attribution or architecture text.
