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
- Deterministic cross-artifact quality gates and a shared publication design
  system for responsive/print HTML, portable Markdown, searchable outlined A4
  PDF, and styled native DOCX across all four deliverables (16 private
  artifacts).
- HMAC request verification, replay protection, consent/content policy,
  high-risk review gates, tenant-scoped SQLite state, cumulative per-stage and
  per-module checkpoints, restored budgets, and explicit durable
  notification-disabled state.
- Atomic filesystem delivery with non-identifying tenant paths, integrity
  manifests, owner-only modes, explicit deletion, and retention purging.
- A fixed 13-category private evaluation corpus, dry-run planning, atomic
  snapshots, private learner ratings and correction-review fields, and
  aggregate-only publication.

## Architecture

```text
authorized request
  -> consent and request preflight
  -> bounded input ingestion
  -> normalized-content policy
  -> durable preparation checkpoint
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
  -> atomic private delivery and durable notification-disabled state
```

The canonical `Course` is the only source for downstream review and assessment
generation. Rendering never asks a model to rewrite an artifact.

## Quality acceptance boundaries

Model output is a candidate, never the acceptance authority. Before the
evidence set is frozen, the host validates structured authoritative-source and
education/assessment-source floors, gives remaining research questions a fair
share of the source budget, and counts only successfully extracted documents
toward accepted capacity. Canonical URL and high-overlap text deduplication run
before ranking. Community platforms are classified explicitly, capped at one
selected source, and cannot satisfy high-risk authority requirements alone.

Before each module checkpoint, deterministic host validation requires an
applied example, explicit misconception guidance, complete factual-block
citations, known evidence identifiers, and independent text support for every
citation claim. The host recomputes each `claim_hash` from accepted claim text
instead of trusting a model-supplied digest. Duplicate or non-measurable
learning objectives are rejected during plan alignment. A rejected stage gets
at most one bounded repair turn; an invalid repair fails the job instead of
committing degraded content.

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

## System authentication and CLI recovery

The package does **not** require a separately installed Codex CLI and does not
expect an end user to prepare `~/.codex`. The official Codex app-server binary
is already pinned as a Python dependency. The FastAPI shell and protected
frontend `/setup` route expose the normal operator device-code flow. If that
browser path is unavailable, the packaged command starts the same app-owned
flow as a CLI recovery path:

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
`DedicatedSystemAuthenticator`. The shell calls `start_device_code_login()`,
returns its browser-safe snapshot, and polls `current_status()`; the frontend
owns the URL/code ceremony. This follows the official
[Codex app-server device-code contract](https://learn.chatgpt.com/docs/app-server#3b-log-in-with-chatgpt-device-code-flow).

This dedicated identity is a temporary, operator-controlled hackathon/demo
configuration. It must not become an unreviewed multi-tenant pool of one
personal ChatGPT subscription.

## Application assembly

Application shells use the public `RealApplicationFactory`; they do not import
or assemble stores, ingestion adapters, research tools, MCP servers, model
runtimes, pipelines, or renderers themselves. The package factory owns those
details and returns one framework-independent `Txt2CrsApplication` facade.

```python
from pathlib import Path

from pydantic import SecretStr
from txt2crs.application import (
    ApplicationAdmissionConfig,
    ApplicationStorageConfig,
    RealApplicationConfig,
    RealApplicationFactory,
)

# The shell translates validated environment settings exactly once. The
# execution profile is a strict package contract stored with every job.
application = RealApplicationFactory(
    RealApplicationConfig(
        storage=ApplicationStorageConfig(
            state_directory=Path("/private/txt2crs-state"),
            maximum_artifact_job_bytes=100_000_000,
            artifact_retention_days=30,
        ),
        admission=ApplicationAdmissionConfig(
            window_seconds=3_600,
            maximum_jobs_per_user=10,
            maximum_jobs_global=100,
            maximum_reserved_tokens_per_user=2_000_000,
            maximum_reserved_tokens_global=20_000_000,
            maximum_research_cost_microusd_per_user=1_000_000,
            maximum_research_cost_microusd_global=10_000_000,
        ),
        default_execution_profile=validated_execution_profile,
        codex_home=Path("/private/txt2crs-codex-home"),
        tavily_api_key=SecretStr(validated_tavily_api_key),
    )
).create()

try:
    submitted_job = application.submit(
        user_id=authenticated_user_id,
        idempotency_key=request_idempotency_key,
        generation_request=generation_request,
        admission_reservation=admission_reservation,
    )
    # The serial worker creates a fresh, owner/job-bound, one-shot executor.
    with application.create_executor(
        job_id=submitted_job.job_id,
        user_id=authenticated_user_id,
    ) as executor:
        completed_job = executor.execute()
finally:
    application.close()
```

Application shells may also call `application.list_public_jobs(...)` for one
owner-scoped, newest-first page of bounded public summaries. The facade owns
opaque cursor validation, stable ordering, safe projection, and artifact
availability; shells must not query the package SQLite store or reconstruct
private resume state.

`application.inspect_application_readiness()` is the complete safe integration
probe. It returns coarse authentication, exact-model, reviewed research,
SQLite, private-artifact, input-capability, and admission states without
exposing paths, ports, credentials, provider payloads, or exception details.
Because the real probe briefly starts the same managed provider/MCP graph used
by a job and performs rollback/cleanup storage checks, application shells must
run it only at startup and a bounded maintenance interval. Browser requests
read the shell's last cached snapshot; they never call this method directly.

`DeterministicApplicationFactory` exposes the same facade for offline tests. It
uses scripted provider results while retaining production SQLite, preparation,
pipeline, rendering, artifact, recovery, and owner-purge behavior. The
executable public-boundary example is
[`tests/integration/test_application_lifecycle.py`](tests/integration/test_application_lifecycle.py).

Important deployment rules:

- The worker must use an explicitly selected ChatGPT/Codex identity. The
  temporary hackathon bootstrap owns one dedicated demo identity; a production
  multi-tenant policy must not pool one personal subscription across unrelated
  users. Pass the exact absolute `codex_home` to `RealApplicationConfig`.
- The MCP HTTP listener must remain on loopback. Tavily credentials stay in the
  application-owned research process and are not inherited by the Codex
  worker.
- Consent, `learner_age_group`, and any qualified high-risk review approval
  belong in the strict `GenerationRequest`; the facade stores that exact
  request.
- Every new job submission must declare a finite `AdmissionReservation`
  matching its configured run/research limits.
- The included `FilesystemPrivateArtifactStore` is suitable for the current
  private local, single-operator scope. If the owner explicitly approves a
  future hosted scope, any replacement `PrivateArtifactStore` must preserve
  owner checks, idempotency, integrity, deletion, and retention behavior.
- FastAPI authentication and authorization must establish `user_id` before
  calling the facade. Identifiers alone are never authorization.

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

The package pins `openai-codex==0.144.4` and
`openai-codex-cli-bin==0.144.4`. Matching generated app-server JSON Schemas
are committed under `docs/fixtures/`; upgrades must regenerate and review the
fixture before changing either pin.

Trusted stage guidance is passed as Codex `developer_instructions`, not as a
replacement base instruction set. This preserves the selected model's
app-server metadata while keeping untrusted learner/provider content in the
turn prompt. Protocol fixture review must cover that distinction during SDK
upgrades.

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
