# txt2crs Python Library

`txt2crs` is the reusable education engine for turning one authorized topic or
source into a source-grounded course, a comprehensive review pack, a student
assessment, and a separate instructor answer key.

The library owns the AI, research, ingestion, validation, rendering, durable
job, safety, and evaluation behavior. It deliberately does not own FastAPI
routes, user authentication, payment, or frontend components; those belong in
the application shell.

## Implemented capabilities

- Input normalization for prompts, pasted text, URLs, PDF, DOCX, PPTX, images,
  audio, video, and YouTube transcripts.
- A subscription-only Codex runtime using the exact pinned official Python SDK
  and app-server binary. Each worker receives an explicit isolated
  `CODEX_HOME`; Platform API credentials are removed, refresh stays inside
  Codex, and API-key accounts are rejected.
- A required loopback FastMCP research server exposing only
  `research_search` and `research_extract`, backed by a fixed-origin Tavily
  adapter with URL/DNS/redirect SSRF protection.
- Thread-safe limits for model turns, research calls, sources, extracted bytes,
  tokens, retries, repairs, and elapsed time, plus atomic rolling per-user and
  global admission for jobs, reserved tokens, and paid research.
- Immutable source and evidence IDs, explainable evidence ranking, conflict
  disclosure, citation integrity, and conservative independent text-support
  checks.
- Strict versioned Pydantic contracts for the course plan, module drafts,
  canonical course, review pack, assessment blueprint, student assessment,
  and evidence-backed instructor answer key.
- Five fixed schema-constrained stages plus one bounded lesson-writing turn per
  module, with finite transient retries, prompt-token preflight, and no more
  than one schema-repair turn per invalid stage.
- Deterministic cross-artifact quality gates and safe rendering to HTML,
  Markdown, searchable PDF, and real DOCX for all four deliverables (16
  private artifacts).
- HMAC request verification, replay protection, consent/content policy,
  high-risk review gates, tenant-scoped SQLite state, cumulative per-stage and
  per-module checkpoints, restored budgets, and idempotent notifications.
- Atomic filesystem delivery with non-identifying tenant paths, integrity
  manifests, owner-only modes, explicit deletion, and retention purging.
- A fixed 13-category private evaluation corpus, dry-run planning, atomic
  snapshots, private learner ratings and correction-review fields, and
  aggregate-only publication.

## Architecture

```text
authorized request
  -> content and consent policy
  -> input ingestion
  -> research plan
  -> bounded search and extraction
  -> ranked frozen evidence
  -> course plan
  -> one checkpointed turn per course module
  -> deterministic course assembly and citation checks
  -> review pack
  -> assessment blueprint
  -> assessment and answer key
  -> cross-artifact validation
  -> deterministic rendering
  -> atomic private delivery and one notification
```

The canonical `Course` is the only source for downstream review and assessment
generation. Rendering never asks a model to rewrite an artifact.

## Installation

From the backend workspace:

```bash
uv sync --package txt2crs
```

Local audio/video transcription is optional:

```bash
uv sync --package txt2crs --extra transcription
```

The OCR adapter uses the system Tesseract executable through `pytesseract`.

## Temporary standalone system authentication

The package does **not** require a separately installed Codex CLI and does not
expect an end user to prepare `~/.codex`. The official Codex app-server binary
is already pinned as a Python dependency. Until the FastAPI setup screen exists,
the packaged bootstrap command starts the same app-owned device-code flow that
the finished frontend will render:

```bash
uv run --package txt2crs txt2crs-system-auth
```

The command opens OpenAI's device verification page, displays the short code,
waits for the dedicated ChatGPT account to approve it, and stores Codex-managed
credentials under `./.txt2crs-system/codex-home`. Set
`TXT2CRS_SYSTEM_STATE_DIRECTORY` when that private state must live on a
persistent mounted volume. No OAuth access or refresh token is returned to
txt2crs.

The framework-independent integration point is
`DedicatedSystemAuthenticator`. A future setup route calls
`start_device_code_login()`, returns its browser-safe snapshot, and polls
`current_status()`; the frontend owns the URL/code ceremony. This follows the
official
[Codex app-server device-code contract](https://learn.chatgpt.com/docs/app-server#3b-log-in-with-chatgpt-device-code-flow).

This dedicated identity is a temporary, operator-controlled hackathon/demo
configuration. It must not become an unreviewed multi-tenant pool of one
personal ChatGPT subscription.

## Application assembly

A production application constructs admission limits, one `RunBudget`, reviewed
`SourcePolicyRegistry`, `ResearchToolService`, loopback
`ResearchMcpApplication`, `OfficialCodexSdkAdapter`, ingestion service, course
pipeline, `SqliteJobStore`, `FilesystemPrivateArtifactStore`, and
`GenerationJobExecutor` per isolated subscription worker.

Important deployment rules:

- The worker must use an explicitly selected ChatGPT/Codex identity. The
  temporary hackathon bootstrap owns one dedicated demo identity; a production
  multi-tenant policy must not pool one personal subscription across unrelated
  users. Pass the exact absolute `codex_home` selected by the application to
  `OfficialCodexSdkAdapter.create`.
- The MCP HTTP listener must remain on loopback. Tavily credentials stay in the
  application-owned research process and are not inherited by the Codex
  worker.
- Consent, `learner_age`, and any qualified high-risk review approval must be
  passed explicitly to `GenerationJobExecutor.execute`.
- Every new job submission must declare a finite `AdmissionReservation`
  matching its configured run/research limits.
- The included `FilesystemPrivateArtifactStore` is suitable for the current
  private local, single-operator scope. If the owner explicitly approves a
  future hosted scope, any replacement `PrivateArtifactStore` must preserve
  owner checks, idempotency, integrity, deletion, and retention behavior.
- FastAPI authentication and authorization must establish `user_id` before
  calling `JobService`. Identifiers alone are never authorization.

The executable offline example in
[`tests/integration/test_generation_job_executor.py`](tests/integration/test_generation_job_executor.py)
shows the full submission, generation, checkpoint, crash-resume, rendering, and
private delivery lifecycle with deterministic providers.

## Develop and verify

Run these commands from `backend/packages/txt2crs/`. The working directory
matters: the application shell's `backend/pyproject.toml` excludes
`packages/` from its own mypy configuration and carries its own pytest
settings, so the engine's checks must resolve this package's
`pyproject.toml` instead.

```bash
uv run --package txt2crs pytest
uv run --package txt2crs ruff check .
uv run --package txt2crs mypy
uv build --package txt2crs
```

The repository-level `scripts/validate-changes.sh` runs the same three
checks in its engine section (`./scripts/validate-changes.sh engine`).

The default suite is credential-free and network-free. The separately marked
live subscription acceptance test is skipped unless
`TXT2CRS_RUN_LIVE_CODEX=1` is set.

## Protocol and provenance controls

The package pins `openai-codex==0.1.0b3` and
`openai-codex-cli-bin==0.137.0a4`. Matching generated app-server JSON Schemas
are committed under `docs/fixtures/`; upgrades must regenerate and review the
fixture before changing either pin.

The pinned public Python SDK does not expose the app-server rate-limit read
operation. Runtime readiness therefore reports subscription quota as
`unknown`; it never guesses a remaining allowance or calls SDK internals.

Original code is MIT-0. Materially adapted Hermes behavior remains MIT and is
identified in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) and the
package-scoped [`LICENSE`](LICENSE).

Architecture decisions and acceptance requirements are indexed in
[`docs/README_txt2crs_docs.md`](docs/README_txt2crs_docs.md), with executable
coverage mapped in
[`docs/IMPLEMENTATION_COMPLIANCE.md`](docs/IMPLEMENTATION_COMPLIANCE.md).
