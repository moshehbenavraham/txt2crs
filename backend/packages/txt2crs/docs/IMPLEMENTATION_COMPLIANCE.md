# txt2crs Package Implementation Compliance

This document maps the package requirements in
[`AI_USAGE_NEEDS.md`](AI_USAGE_NEEDS.md),
[`HERMES_MINIMUM_CODE_PULL_EVALUATION.md`](HERMES_MINIMUM_CODE_PULL_EVALUATION.md),
and [`AIOS_RUNTIME_SUPPLEMENT.md`](AIOS_RUNTIME_SUPPLEMENT.md) to executable
implementation evidence.

## Package boundary

The independently installable `txt2crs` package owns:

- subscription-only Codex execution and safe runtime readiness;
- bounded ingestion, research, evidence, generation, validation, and rendering;
- durable owner-scoped jobs, quota admission, checkpoints, private artifacts,
  retention, and idempotent delivery;
- deterministic evaluation, progress, security, and provenance contracts.

The FastAPI application shell owns browser sessions, user
authentication, payment/entitlement lookup, HTTP routes, UI approval/editing,
deployment-specific email, and any Google Drive or Google Docs integration.
Those responsibilities consume the package's signed-request, owner-scoped job,
private-artifact, and notification interfaces; they do not belong in this
reusable library.

## Requirement evidence

| Requirement | Package implementation | Primary executable evidence |
|---|---|---|
| Deep research before drafting | Finite research plans, reviewed source policy, two-tool MCP server, bounded Tavily search/extract, immutable ranked evidence | `test_research_coordinator.py`, `test_research_mcp_server.py`, `test_evidence_quality.py` |
| Citation and provenance integrity | Stable source/evidence IDs and hashes, frozen evidence versions, claim references, conflict disclosure, independent text support, high-risk authority gate | `test_evidence_ledger.py`, `test_generation_quality.py` |
| Strict structured artifacts | Pydantic contracts reject extra fields, unsupported versions, broken IDs, missing coverage, and cross-artifact drift | `test_domain_models.py`, `test_stage_validation.py` |
| Untrusted input and output safety | Trusted instructions are separated from delimited data; HTML is escaped and rejects active content, unsafe links, remote media, and private data | `test_runtime.py`, `test_rendering.py`, `test_url_safety.py` |
| Subscription-only OpenAI use | Exact official SDK/runtime pins, explicit isolated `CODEX_HOME`, delegated credential refresh, ChatGPT account check, API-key rejection, model discovery, schema turns, cancellation, and safe event projection | `test_official_codex_adapter.py`, `test_runtime.py`, live acceptance test |
| Hard spend and iteration bounds | Thread-safe per-job limits, prompt-token preflight, finite retries/repairs, repeated-tool guardrails, and atomic per-user/global job, token, and paid-research admission | `test_budgets.py`, `test_tool_guardrails.py`, `test_admission_quotas.py` |
| Any supported input | Prompt, text, URL, PDF, DOCX, PPTX, image OCR, audio/video transcription, and YouTube transcript adapters with byte/character/page/timestamp boundaries | ingestion unit tests |
| Staged education generation | Separate research plan, course plan, one turn per module, review pack, assessment blueprint, and assessment/answer-key stages | `test_generation_pipeline.py` |
| Complete review material | Objective study guide, glossary, misconceptions, flashcards, worked examples, practice, section summaries, cumulative summary, and review sequence | domain and rendering tests |
| Full validated assessment | Blueprint precedes item writing; items map to objectives, sections, evidence, difficulty, skill, points, and rubrics; answers are separate and support-checked | `test_domain_models.py`, `test_generation_quality.py` |
| Deterministic multi-format output | Each of the four deliverables renders to semantic HTML, Markdown, searchable PDF, and real DOCX, for 16 private artifacts | `test_rendering.py`, generation-job integration test |
| Crash-safe recovery | Every accepted cumulative stage is atomically checkpointed with budget state; module and research work resume without replay; final delivery uses an idempotent outbox | `test_generation_pipeline.py`, `test_generation_job_executor.py`, `test_sqlite_job_store.py` |
| Private retention and deletion | Hashed tenant paths, `0700` directories, `0600` files, atomic publish, integrity manifests, owner reads/deletes, and expiry purge | `test_filesystem_artifact_store.py` |
| Safe progress and readiness | Private-to-public allowlist projection; provider/account/model/quota state remains distinct from job completion | `test_progress_projection.py`, `test_runtime_status_and_usage.py`, `test_runtime.py` |
| Evaluation governance | Fixed 13-category private corpus including noisy extraction, no-network dry run, immutable hashes, private learner ratings/correction-review fields, private snapshots, and bounded aggregate publication | evaluation unit tests |
| Donor independence | No executable Hermes or AIOS import, path, process, service, configuration, or lock dependency; adapted behavior retains provenance | `test_provenance.py`, package build/install smoke checks |

## Public SDK telemetry boundary

The pinned `openai-codex==0.1.0b3` public `Codex` API exposes account state,
model discovery, streamed per-turn token usage, and managed refresh. The pinned
app-server protocol contains a rate-limit request, but that operation is not
exposed by the public high-level Python API. The package therefore reports
subscription quota as `unknown` instead of calling SDK internals or inventing
remaining allowance. Generated matching protocol schemas remain committed
under `docs/fixtures/` so a future pinned SDK upgrade can add the operation
through a reviewed contract.

## Verification gates

From `backend/`:

```bash
uv run --package txt2crs ruff check packages/txt2crs
uv run --package txt2crs mypy \
  packages/txt2crs/src packages/txt2crs/tests
uv run --package txt2crs pytest packages/txt2crs/tests
uv build --package txt2crs
```

The default suite is credential-free and network-free. The separately gated
live test requires an authenticated, isolated ChatGPT `CODEX_HOME`; it verifies
the real pinned SDK/app-server turn, structured result, allowlisted MCP call,
safe progress events, and subscription usage.
