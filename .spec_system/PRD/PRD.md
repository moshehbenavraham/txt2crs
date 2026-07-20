# txt2crs - Product Requirements Document

## Overview

txt2crs is an OpenAI and Devpost Education Hackathon application for learners
who want to turn a topic or bounded source into a complete, source-grounded
learning package. One authenticated submission produces a deeply researched
course, comprehensive review material, a student assessment, and a separate
instructor answer key in private publication formats.

The reusable `txt2crs` engine owns generation, research, validation,
persistence, recovery, policy, artifacts, and rendering. The FastAPI shell
owns HTTP, identity, configuration, lifecycle, and safe error translation.
The React application presents the durable learner journey without exposing
provider internals or filesystem paths.

## Goals

1. Deliver one durable input-to-four-publications learner journey backed by
   real research and explicit GPT-5.6 execution.
2. Preserve exact requests, execution profiles, accepted checkpoints, and
   private artifacts across refreshes and process or container replacement.
3. Keep authorization, content policy, input bounds, artifact integrity, and
   provider isolation enforceable at the owning package boundaries.
4. Provide a polished, accessible, responsive "research atelier" interface
   that clearly explains intake, progress, sources, results, and failures.
5. Ship a reproducible, judge-ready release with deterministic validation,
   one representative live proof, and complete submission evidence.

## Non-Goals

- Reconstruct Make.com, Airtable, Paperform, or Google Drive workflows.
- Add payments, subscriptions, service tiers, commerce, or public file links.
- Add LMS export, course editing, collaboration, automatic grading, or a quiz
  player before the submission gate.
- Add multiple concurrent Codex workers, a queue platform, or horizontal
  backend replicas.
- Add a general model or provider selector.
- Add hosted deployment, platform-specific CD, public domains, or remote
  environment operations within the current project scope.
- Add image, audio, or video ingestion before each capability has bounded
  deployment dependencies and representative tests.

## Users and Use Cases

### Primary Users

- **Learner**: Submits a topic, text, URL, YouTube URL, PDF, DOCX, or PPTX and
  receives a private, complete learning package.
- **Instructor or reviewer**: Uses the separate answer key, source disclosure,
  and conflict notes to review assessment quality and course provenance.
- **System operator**: Connects one dedicated ChatGPT identity, inspects safe
  readiness, provisions judge access, and runs the release proof.
- **Hackathon judge**: Evaluates the product story, real workflow, generated
  artifacts, documented AI usage, privacy boundaries, and reproducibility.

### Key Use Cases

1. A learner submits one bounded source and safely retries transport without
   creating a duplicate paid job.
2. A learner refreshes or reconnects to the same durable progress URL and
   continues from checkpoint-derived state.
3. A learner previews or downloads the four deliverables in available private
   formats after integrity-checked delivery.
4. An operator completes dedicated ChatGPT device-code setup and sees truthful
   readiness without exposing credentials or private provider details.
5. The application recovers a non-terminal job from its exact stored request,
   execution profile, resolved preferences, and latest accepted checkpoint.
6. A user account deletion removes engine requests, checkpoints, delivery
   rows, and artifacts before deleting the PostgreSQL identity.

## Requirements

### MVP Requirements

- An authenticated learner can submit one prompt, text, supported URL,
  YouTube URL, PDF, DOCX, or PPTX using strict bounded inputs and an
  owner-scoped idempotency key.
- An authenticated learner can receive `202 Accepted` only after the complete
  generation-affecting request and admission reservation are durably
  committed.
- An authenticated learner can inspect a bounded, monotonic, public-safe job
  projection without seeing prompts, source text, evidence excerpts, provider
  identifiers, token data, paths, or checkpoint JSON.
- An authenticated learner can retrieve an owner-scoped artifact manifest and
  one integrity-checked artifact by stable identifiers without receiving a
  filesystem path.
- A learner can distinguish queued, ingesting, researching, drafting,
  validating, rendering, delivering, completed, failed, review-required,
  reconnecting, and cancelled presentation states.
- A learner can access four distinct deliverables - course, review pack,
  student assessment, and instructor answer key - with HTML, Markdown, PDF,
  and DOCX artifacts when rendering completes.
- A learner can see bounded source summaries and unresolved-conflict
  disclosures in completed results.
- A system operator can connect one dedicated ChatGPT subscription identity
  through a superuser-only browser flow with a documented CLI recovery path.
- A system operator can inspect coarse readiness for authentication,
  discovered GPT-5.6, research, storage, worker health, enabled inputs, and
  admission without triggering destructive or provider work per browser poll.
- The application can recover accepted and active work from the exact
  immutable request and latest accepted checkpoint after restart.
- The engine can reject content after bounded ingestion and before research or
  Codex work when binary or fetched content violates policy.
- The application can delete one owner's engine data idempotently before
  deleting the corresponding PostgreSQL user.
- A signed-out visitor can understand the product and reach sign-in from a
  public landing page; an authenticated learner can create and revisit work
  on product-specific routes.
- A hackathon judge can run the documented Docker deployment, deterministic
  suites, representative sample, and release proof from the tested revision.

### Deferred Requirements

- A learner can browse a paginated job library and reopen retained jobs.
- A learner can cancel an accepted or active job through an owner-scoped API.
- A learner can delete one job through coordinated request, checkpoint,
  delivery, and artifact retention.
- A learner can receive non-blocking completion email through a durable outbox.
- A learner can select additional language, duration, tone, assessment, and
  accessibility preferences after deterministic enforcement exists.
- An operator can enable image, audio, or video inputs after deployment
  dependencies, limits, readiness, and representative tests are complete.
- An operator can inspect private diagnostics and aggregate-only evaluation
  results outside learner-facing product surfaces.

## Non-Functional Requirements

- **Performance**: Public job polling uses 1.5-second visible and 10-second
  hidden intervals, backs transient network failures off to at most 30
  seconds, and stops on terminal state.
- **Input bounds**: One upload is at most 20 MiB, normalized input is at most
  200,000 characters, PDF input is at most 200 pages, and the complete
  artifact bundle is at most 100 MiB.
- **Reliability**: Every accepted request is durable before `202`; startup
  scans and two-second polling recover non-terminal jobs without requiring an
  in-memory event.
- **Topology**: P0 runs exactly one non-root Uvicorn process, one serial
  generation worker, one active job at most, and one persistent private state
  volume.
- **Security**: Wrong-owner job and artifact access returns the same 404 as a
  missing resource; status and artifact responses are private/no-store and
  downloads are nosniff.
- **Privacy**: Logs and HTTP responses contain no email, source content,
  prompts, evidence excerpts, tokens, provider payloads, artifact bytes, or
  filesystem paths.
- **Model policy**: Readiness and execution require a discovered GPT-5.6
  family model and fail closed instead of falling back to an older or first
  available model.
- **Accessibility**: Learner surfaces meet WCAG 2.2 AA contrast, keyboard,
  semantic landmark, focus, status announcement, and reduced-motion
  requirements at 390, 768, 1024, and 1440 pixel target widths.
- **Testing**: Default CI and deterministic suites require no network or
  credentials; only the explicit live compatibility gate may require them.
- **Resource safety**: Every job-scoped Codex, MCP, HTTP, and temporary
  resource closes on success, failure, cancellation, and application
  shutdown, leaving no loopback listener.

## Constraints and Dependencies

- Submission deadline: 2026-07-22 00:00 UTC (03:00 Asia/Jerusalem).
- P0 feature freeze: 2026-07-21 15:00 Asia/Jerusalem; live proof and release
  evidence target: 2026-07-21 21:00 Asia/Jerusalem.
- Runtime generation uses one dedicated operator-controlled ChatGPT
  subscription identity through the official packaged Codex runtime.
- Research uses the package-owned two-tool Tavily MCP boundary on loopback.
- PostgreSQL owns users; tenant-scoped engine SQLite is the only generation
  job source of truth; the private filesystem owns immutable artifacts.
- Secrets remain in `.env` or deployment secret storage and are never
  committed.
- FastAPI routes call the public engine facade and must not duplicate engine
  generation, research, validation, persistence, policy, or rendering logic.
- PostgreSQL schema changes use Alembic; generated frontend client files are
  updated only through the repository client-generation script.
- Repository-root Docker Compose is the only deployment target in scope.
  Runtime `staging` and `production` profiles do not imply a hosted
  environment, and any future hosting choice requires explicit owner approval
  and a new ADR.
- External credentials may be absent during build and OpenAPI generation, but
  readiness must then reject new generation work truthfully.

## Phases

This system delivers the product via phases. Each phase is implemented through
2-4 hour sessions containing 12-25 atomic tasks.

| Phase | Name | Sessions | Status |
|-------|------|----------|--------|
| 00 | Application Baseline | 1 | Complete |
| 01 | Engine Application Boundary | 5 | Complete |
| 02 | Composition and Readiness | 5 | Complete |
| 03 | Durable Jobs API | 3 | Complete |
| 04 | Learner Experience | 2 | Complete |
| 05 | Hardening and Submission | 2 | Not Started |

## Phase 00: Application Baseline

### Objectives

1. Make the imported shell a truthful, reproducible base for engine
   composition.
2. Correct production container workspace installation and enforce the
   single-worker topology.
3. Add typed, confined private engine state paths and persistent volume
   wiring while preserving existing shell behavior.
4. Keep engine, backend, frontend, Compose, and production image checks green.

### Sessions

- **S01 - Baseline Container and State**: Correct the workspace-aware
  production image, enforce one non-root backend process, add typed confined
  private engine-state paths and persistent storage, and preserve existing
  shell smoke behavior.

## Phase 02: Composition and Readiness

### Objectives

1. Compose one public engine facade for the complete FastAPI lifespan.
2. Recover and execute runnable work through one serial worker supervisor.
3. Maintain truthful, side-effect-free cached readiness and safe
   observability.
4. Expose authenticated readiness and superuser-only device authentication.
5. Provide an accessible operator setup experience with CLI recovery.

### Sessions

- **S01 - Engine Composition Lifecycle**: Translate typed shell settings into
  package configuration and own one facade with deterministic cleanup.
- **S02 - Serial Worker Supervisor**: Recover and execute one job at a time
  through public handles with bounded cancellation and shutdown.
- **S03 - Cached Readiness and Observability**: Compose safe cached dependency
  state, serialize runtime ownership, sanitize logs, and translate errors.
- **S04 - System Readiness and Auth API**: Add strict readiness and privileged
  device-auth routes, then regenerate the OpenAPI client.
- **S05 - Operator Setup Experience**: Build the responsive, accessible
  superuser setup and device-login workflow.

## Phase 03: Durable Jobs API

### Objectives

1. Accept strict JSON and multipart learner inputs only after bounded
   transport validation, readiness, admission, and durable idempotent commit.
2. Expose owner-scoped safe job, result, manifest, and integrity-checked
   artifact reads with polling and private-delivery headers.
3. Prove exact restart and delivery replay behavior through application
   acceptance tests.
4. Coordinate engine owner purge before PostgreSQL account deletion.
5. Retire the donor `items` domain through a reversible schema migration and
   regenerate the frontend API client.

### Sessions

- **S01 - Durable Job Submission and Admission**: Add tests-first JSON and
  multipart intake, bounded streaming validation, canonical idempotency,
  readiness/admission mapping, rate limits, and durable `202` semantics.
- **S02 - Owner-Scoped Job Results and Recovery**: Add safe status, result,
  manifest, and artifact routes plus ownership, headers, stream cleanup,
  restart, checkpoint, and delivery-replay acceptance coverage.
- **S03 - Account Purge and Donor Retirement**: Coordinate cross-store account
  erasure, drop the donor item table through Alembic, remove item code and
  admin tools, and regenerate the frontend contract.

## Technical Stack

- Python 3.14, FastAPI, SQLModel, Pydantic v2, PostgreSQL 18, Alembic, pytest,
  mypy, Ruff, and uv for the application shell.
- Python 3.14, Pydantic v2, tenant-scoped SQLite, the official Codex SDK
  runtime, deterministic renderers, pytest, mypy, Ruff, and uv for the
  reusable engine.
- React 19, TypeScript, Vite, TanStack Router and Query, React Hook Form, Zod,
  Tailwind CSS 4, shadcn/Radix, Biome, and Playwright for the frontend.
- Docker Compose, Traefik, non-root containers, persistent volumes, and
  OpenTelemetry for local production-like operation.

## Package Map

| Package | Path | Stack | Purpose |
|---------|------|-------|---------|
| backend-shell | `backend` | Python/FastAPI/PostgreSQL | HTTP, identity, settings, lifespan, error translation, and application tests |
| txt2crs-engine | `backend/packages/txt2crs` | Python/Pydantic/SQLite | Reusable education engine, Codex runtime, research, policy, recovery, artifacts, and rendering |
| frontend | `frontend` | React/TypeScript/Vite | Public and authenticated learner, operator, and results experiences |

## Success Criteria

- [ ] Phase 00 through Phase 05 exit gates pass.
- [ ] Every enabled input mode is reported truthfully by readiness and covered
  by deterministic tests.
- [ ] New requests are durably committed before `202` and recover from exact
  stored execution state.
- [ ] GPT-5.6 is explicitly selected, discovered, and exercised without
  silent fallback.
- [ ] Binary content passes post-ingestion policy before research or Codex.
- [ ] One completed job exposes four deliverables and exactly 16 private,
  owner-scoped, integrity-checked artifacts.
- [ ] The donor `items` domain and table are removed through a verified
  Alembic migration after job acceptance coverage passes.
- [ ] Desktop, mobile, keyboard, contrast, and reduced-motion checks pass.
- [ ] Engine, backend, frontend, acceptance, Compose, and production Docker
  validation are green.
- [ ] The then-current exact SemVer release is synchronized, built, tested,
  tagged, pushed, and supported by one inspected live GPT-5.6 plus Tavily
  course.
- [ ] Judge-ready README, license/access, public demo video, Codex feedback
  Session ID, Education-category fields, and Devpost submission are complete.

## Risks

- **Deadline compression**: Preserve durability, GPT-5.6, policy, owner
  authorization, artifact integrity, four deliverables, and submission
  evidence; drop hosting, extra samples, and nonessential motion first.
- **Runtime compatibility**: Gate SDK or CLI upgrades behind protocol fixture
  review and the full engine contract suite.
- **Cross-store consistency**: Keep engine SQLite authoritative for jobs and
  purge engine data before PostgreSQL identity deletion.
- **Duplicate runtime ownership**: Reject multiple backend workers or replicas
  and serialize readiness, authentication, and job execution.
- **Untrusted content**: Apply bounded transport and ingestion checks, URL and
  OOXML protections, two-stage policy, deterministic rendering, and sandboxed
  previews.
- **External credential availability**: Keep deterministic validation
  credential-free and fail readiness safely until ChatGPT and Tavily are
  configured.

## Assumptions

- **Local Docker is the complete deployment scope**: Repository-root Docker
  Compose is the release, demonstration, and judge path. Phase planning must
  not add hosted automation or assume a future platform.
- **The repository is a three-package workspace**: Root and side-specific
  agent guidance, the uv workspace, nested engine package, and independent
  React manifest establish distinct backend shell, engine, and frontend
  ownership even though the generic detector does not recognize this mixed
  uv/npm layout.

### Conflict Resolutions

- **Phase progress**: Validated session and phase-transition evidence is
  authoritative. Phases 00 through 04 are complete; Phase 05 remains
  unfinished.
- **Phase 01 session count**: The implementation plan suggested two sessions,
  but those sessions combined fourteen substantial package gaps and exceeded
  the Apex Spec 12-25 task and 2-4 hour limits. Phase 01 therefore uses five
  dependency-ordered sessions without changing the phase scope.
- **Phase 03 session count**: The implementation plan suggested two sessions,
  but transport hardening, durable admission, safe reads and delivery,
  restart replay, cross-store erasure, donor removal, migration verification,
  and generated-client regeneration do not fit two bounded sessions. Phase 03
  therefore uses three dependency-ordered sessions without changing scope.
