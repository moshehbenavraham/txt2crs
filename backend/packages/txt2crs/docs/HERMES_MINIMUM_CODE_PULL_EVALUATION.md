# Hermes Minimum Code-Pull Evaluation

> **Historical design study:** this document records the constraints selected
> while the engine was first extracted for Build Week. Its subscription-only,
> API-key rejection, model-family, and local-deployment statements are no
> longer product requirements. Current behavior is defined by
> `IMPLEMENTATION_COMPLIANCE.md`, the package README, and ADR-0009.
>
> Status: implemented as a bounded local package. Materially adapted Hermes
> behavior retains MIT provenance in `THIRD_PARTY_NOTICES.md`; the donor
> checkout is not a build or runtime dependency.
>
> Evaluated target: `txt2crs`
>
> Evaluated donor: Hermes at commit `0f102fa4dc04b7dfdab048169aaaa640d09d7523`

## Implementation result

The selected boundary is now implemented under `src/txt2crs/` with strict
contracts, shared budgets, two research tools, the official pinned Codex SDK,
immutable evidence, deterministic education validation and rendering, durable
SQLite jobs, private evaluation replay, and donor-absence tests. Generated
protocol fixtures for Codex app-server `0.144.4` are committed under
`docs/fixtures/`. A default credential-free suite and an explicitly enabled
live ChatGPT/MCP acceptance test cover the final architecture.
>
> Review date: 2026-07-17

Paths beginning with `src/txt2crs/` are relative to the independently
installable package root at `backend/packages/txt2crs/`.

## Executive conclusion

The minimum viable pull is **not** just a web-search provider. Fulfilling
[`AI_USAGE_NEEDS.md`](./AI_USAGE_NEEDS.md) requires all of the following to live
inside `txt2crs`:

1. a subscription-authenticated OpenAI Codex runtime;
2. a small, bounded local agent kernel;
3. a tightly allowlisted research tool service;
4. evidence, citation, and structured-output contracts;
5. staged course, review-material, and assessment generation;
6. resumable job control, safety, usage accounting, and quality gates.

The recommended runtime is the official Python `openai-codex` SDK, which controls
the local Codex app-server protocol and reuses Codex's ChatGPT sign-in. It should
be pinned to an exact version and wrapped behind a small local interface. Do
**not** extract Hermes's direct ChatGPT OAuth/Responses implementation. The
official integration avoids copying an OAuth client identifier, handling refresh
tokens, calling an undocumented backend directly, or maintaining a large
Responses-event compatibility layer.

Hermes remains a **source donor only**. Selected logic is copied or adapted into
ordinary `txt2crs` modules with provenance notices. The completed application
must run and pass its tests after `/home/aiwithapex/projects/hermes` is deleted.
It must never import Hermes, launch Hermes, call a Hermes service, share Hermes
state, or read Hermes credentials.

The estimated source-code scope is:

| Scope | Estimated non-test LOC |
|---|---:|
| Hermes-derived, locally adapted logic | 940-1,355 |
| New `txt2crs` implementation | 2,900-4,400 |
| **Total** | **3,840-5,755** |

These are planning estimates, not implementation quotas. Tests, fixtures,
generated protocol schemas, migrations, and documentation are excluded.

## Decision

Proceed with a **Python backend** and this combination:

- official `openai-codex` SDK and its pinned Codex app-server runtime;
- managed ChatGPT browser or device-code sign-in;
- a local `txt2crs` orchestration kernel around Codex turns;
- a local MCP server exposing only typed `research_search` and
  `research_extract` tools initially;
- Tavily search/extract behavior adapted from Hermes;
- fail-closed URL and redirect safety adapted from Hermes;
- locally owned Pydantic contracts, evidence ledger, citations, budgets,
  checkpoints, rendering, and education-quality checks.

Python is the smallest coherent choice because the relevant donor logic and the
official SDK are Python. The target repository currently declares no conflicting
stack. If the project later commits to a TypeScript-only backend, this decision
must be revisited before extraction.

## Baseline from the Make.com scenarios

The three exported scenarios establish the product baseline, not the target
architecture:

- Scenario 1 accepts a plain-text request and stores customer/job data.
- Scenario 2 creates or updates the customer and Drive-folder records.
- Scenario 3 performs four serial model calls: course generation, filename
  generation, HTML rendering, and a 5-10-question short-answer quiz.
- The scenarios contain no web research, retrieval, evidence ledger, citation
  verification, comprehensive review pack, assessment blueprint, durable job
  state machine, or structured course contract.

The extraction must therefore replace--not reproduce--the one-shot model chain.
Filename generation and HTML/PDF formatting should become deterministic code.
The model budget saved there is better spent on explicit research, staged
writing, and validation.

## Non-negotiable extraction boundary

The following boundary applies to every implementation phase.

### Allowed

- Read Hermes source and tests during the extraction.
- Copy a small, identified function or algorithm into `txt2crs`.
- Adapt copied logic to local types and local configuration.
- Preserve the Hermes MIT notice and add source-path/commit provenance.
- Use upstream third-party packages directly when `txt2crs` declares them.

### Forbidden in the finished application

- Python imports from `hermes`, `hermes_cli`, or any Hermes package.
- Filesystem references to the Hermes checkout or `~/.hermes`.
- Hermes CLI or subprocess execution.
- Hermes services, sidecars, APIs, RPC, MCP servers, or plugin registry.
- Git submodules, editable installs, path dependencies, or copied virtual
  environments pointing to Hermes.
- Hermes configuration keys, runtime state, token stores, or credentials.
- A deployment or build step that clones or mounts Hermes.
- Compatibility shims whose purpose is to locate Hermes at runtime.

The final proof is a clean build and acceptance run with the donor directory
renamed or removed, plus static scans for executable references.

## Requirement-to-capability matrix

| AI need | Required local capability | Hermes evidence | Pull or build | Codex role |
|---|---|---|---|---|
| Any input | Input classification, safe extraction, normalization, source record | PDF and YouTube helpers | Adapt two helpers; build the dispatcher and other adapters | Interpret normalized input |
| Deep research | Search, extract, query planning, source diversity, conflict checks | Tavily provider, URL safety, tool-loop behavior | Adapt provider and safety; build research planning and evidence models | Select queries and evidence needs |
| Grounding and provenance | Immutable sources, excerpts, claim links, citation verification | Not a coherent Hermes subsystem | Build locally | Produce claims against supplied evidence |
| Structured contracts | Versioned schemas and strict validation | App-server output schema support; Hermes structured-output patterns | Use official output schema; build Pydantic models and validation | Generate schema-constrained artifacts |
| Untrusted input/model output | URL safety, content limits, prompt boundary, output validation | URL safety and guardrails | Adapt safety/guardrail logic; build policy boundary | Never receives unrestricted tools |
| Content/identity/spend controls | Age/domain policy, identity, quotas, subscription usage | Session usage capture and auth classification | Adapt small behavior; build policy and accounting | Report turn usage/account type |
| Recoverability/idempotency | Durable stage state, retries, cancellation, checkpoints | Backoff, watchdog, interrupt patterns | Adapt generic behavior; build job state machine | Interrupt individual turns |
| Course planning/writing/verification | Staged generation with evidence and validators | General agent-loop concepts only | Build education-specific pipeline | Plan, draft, revise |
| Review pack | Derive summaries, objectives, flashcards, study guide from canonical course | No specific Hermes feature | Build locally | Generate from approved course/evidence |
| Assessment and answer sheet | Blueprint, questions, answers, rationales, difficulty and leakage checks | No specific Hermes feature | Build locally | Generate and revise against blueprint |
| Quality/evals/observability | Rubrics, deterministic checks, event and usage records | Event projection and usage behavior | Adapt event semantics; build evaluators and logs | Emit streamed progress and usage |
| Accessibility/i18n/personalization | Reading level, locale, accommodations, alternate formats | No coherent donor feature | Build locally | Transform approved artifacts |
| Research feature absent from Make scenarios | Research planning, browser-safe retrieval, evidence ledger, citations | Tavily, URL safety, optional PDF/YouTube helpers | Adapt selected pieces; build the rest | Operate through allowlisted research tools |

The matrix makes the important architectural distinction: Codex is the model
runtime, while `txt2crs` owns the product workflow, data contracts, safety
enforcement, and final artifacts.

### Requirements coverage cross-check

This cross-check prevents lower-visibility requirements in
`AI_USAGE_NEEDS.md` from disappearing behind the larger runtime decision.

| Requirement group | Planned fulfillment |
|---|---|
| Real research | Pre-draft research plan; bounded search/extract; primary/authoritative-source preference; metadata, excerpts, conflicts, visible citations, bibliography, and honestly labeled unavailable/inconclusive states |
| Structured handoffs | Versioned Pydantic/JSON Schema contracts; stable objective, module, section, source, evidence, and assessment IDs; validation before every checkpoint; deterministic rendering |
| Untrusted user/retrieved/model content | Highest-priority invariant instructions; explicit data delimiters; prompt-injection segmentation; output schemas; HTML allowlist; URL validation; policy checks; high-risk human review |
| Identity, privacy, and spend | Signed/timestamped internal requests, replay protection, per-user authorization and quotas, consent records, private artifacts, retention/deletion policy, redacted logs, and stable idempotency |
| Recoverability | Explicit job states, validated checkpoints, bounded retries, cancellation, actionable failures, manual retry, and exactly-once delivery side effects |
| Any input | Typed adapters for prompt/text/URL/PDF/document/slides/image/audio/video; OCR/transcription where required; language/type/quality detection; page/timestamp preservation; useful unsupported/empty errors; chunk retrieval for long inputs |
| Planning, writing, verification | Learning-contract capture, user-correctable inferred settings, outline approval for costly jobs, module-by-module drafting, terminology state, per-stage token limits, and coverage/duplication/prerequisite/cross-reference checks |
| Complete review pack | Objective-linked study guide, glossary, takeaways, misconceptions, flashcards, worked examples, exercises, section/cumulative summaries, spaced-review plan, and source links |
| Full assessment | Blueprint; varied item types; student/instructor forms; objective, section, difficulty, skill, evidence, answer, rationale, points, passing criteria, rubric, ambiguity, duplicate, clue, and leakage checks |
| Cost and latency | Deterministic filename/rendering, scoped prompts, research cache subject to policy, configurable model, per-stage usage/latency/retry accounting, and subscription quota reporting |
| Quality and observability | Fixed multilingual/noisy/conflicting/injection/specialist evaluation set; deterministic checks first; independent evidence or evaluator for judgment; user correction reasons; versioned prompts/schemas/templates/models/evals |
| Personalization/accessibility/i18n | Audience, knowledge, goals, time, language, tone, assessment and accessibility settings; consistent reading level; semantic headings; image text alternatives; accessible tables/PDF; RTL and multilingual generation/evaluation |

An evaluator must not simply grade the same response that produced an artifact.
Deterministic evidence and contract checks run first; any model-based judgment
uses a separately identified evaluation turn and preserved supporting evidence.

## Absolute Hermes implementation reference index

All paths in this section are absolute and use the donor root requested for this
evaluation:

```text
/home/aiwithapex/projects/hermes
```

The classifications mean:

- **Full-pull candidate:** the file or class is sufficiently isolated to copy
  into `txt2crs`, after preserving the license/provenance notice and replacing
  Hermes-oriented names or documentation.
- **Selected-logic pull:** copy only the named pure functions/classes, then
  replace imports and data types with `txt2crs` equivalents.
- **Reference implementation:** use the control flow and tests to design the
  local implementation, but do not copy the coupled module.
- **Reject/exclude:** useful for understanding the alternative, but must not
  enter the selected implementation.

"Full-pull candidate" never means retaining a runtime import or path to this
directory. Every copied file becomes a locally owned `txt2crs` file.

### Agent kernel, budgets, tools, and recovery

| Requirement | Absolute Hermes implementation example | Relevant region | Use |
|---|---|---|---|
| Thread-safe iteration budget | [`/home/aiwithapex/projects/hermes/agent/iteration_budget.py:17`](/home/aiwithapex/projects/hermes/agent/iteration_budget.py:17) | `IterationBudget` | **Full-pull candidate.** Copy the small standard-library-only class, remove Hermes/subagent configuration language, and extend it through local composite budgets rather than modifying its counter semantics. |
| Model/tool/final loop | [`/home/aiwithapex/projects/hermes/agent/conversation_loop.py:537`](/home/aiwithapex/projects/hermes/agent/conversation_loop.py:537) | `run_conversation` | **Reference implementation.** Study turn execution, streaming, tool dispatch, retry, and finalization; implement the much smaller stage loop described in this report. Do not copy the 5,000+ line module. |
| Turn context and preflight | [`/home/aiwithapex/projects/hermes/agent/turn_context.py:93`](/home/aiwithapex/projects/hermes/agent/turn_context.py:93) | `TurnContext`, `build_turn_context` | **Reference implementation.** Use its separation of preflight/context accounting as guidance for a local immutable `TurnRequest`. |
| Safe finalization | [`/home/aiwithapex/projects/hermes/agent/turn_finalizer.py:30`](/home/aiwithapex/projects/hermes/agent/turn_finalizer.py:30) | `finalize_turn` | **Reference implementation.** Reproduce the invariant that cleanup and a terminal result occur once, using local checkpoint/job types. |
| Repeated-tool detection | [`/home/aiwithapex/projects/hermes/agent/tool_guardrails.py:64`](/home/aiwithapex/projects/hermes/agent/tool_guardrails.py:64) and [`/home/aiwithapex/projects/hermes/agent/tool_guardrails.py:224`](/home/aiwithapex/projects/hermes/agent/tool_guardrails.py:224) | Guardrail configuration, canonical signatures, controller | **Selected-logic pull.** Keep canonicalization and repeat/failure counters; replace all Hermes tool/result assumptions. |
| Tool schema collection and dispatch | [`/home/aiwithapex/projects/hermes/model_tools.py:279`](/home/aiwithapex/projects/hermes/model_tools.py:279) and [`/home/aiwithapex/projects/hermes/model_tools.py:1025`](/home/aiwithapex/projects/hermes/model_tools.py:1025) | `get_tool_definitions`, `handle_function_call` | **Reference implementation.** It demonstrates schema-based dispatch and post-call observation, but its registry and complete tool ecosystem are intentionally excluded. |
| Explicit Codex MCP exposure | [`/home/aiwithapex/projects/hermes/agent/transports/hermes_tools_mcp_server.py:152`](/home/aiwithapex/projects/hermes/agent/transports/hermes_tools_mcp_server.py:152) | `_build_server` | **Reference implementation.** Rebuild locally with only `research_search` and `research_extract`; do not import the Hermes registry. |
| Structured model output | [`/home/aiwithapex/projects/hermes/agent/plugin_llm.py:374`](/home/aiwithapex/projects/hermes/agent/plugin_llm.py:374), [`/home/aiwithapex/projects/hermes/agent/plugin_llm.py:456`](/home/aiwithapex/projects/hermes/agent/plugin_llm.py:456), and [`/home/aiwithapex/projects/hermes/agent/plugin_llm.py:598`](/home/aiwithapex/projects/hermes/agent/plugin_llm.py:598) | Structured prompt construction, parsing, `PluginLlm` | **Reference implementation.** Use Codex `output_schema` plus mandatory local Pydantic validation instead of copying the plugin/trust framework. |
| Bounded retry | [`/home/aiwithapex/projects/hermes/agent/retry_utils.py:36`](/home/aiwithapex/projects/hermes/agent/retry_utils.py:36) | `jittered_backoff` | **Selected-logic pull.** Copy this function and its minimal thread-safe jitter state; exclude the adjacent Z.AI-specific policies. |
| Error taxonomy | [`/home/aiwithapex/projects/hermes/agent/error_classifier.py:78`](/home/aiwithapex/projects/hermes/agent/error_classifier.py:78) and [`/home/aiwithapex/projects/hermes/agent/error_classifier.py:534`](/home/aiwithapex/projects/hermes/agent/error_classifier.py:534) | `ClassifiedError`, `classify_api_error` | **Reference implementation.** Rebuild only the seven local error classes listed in this report; the donor classifier spans many irrelevant providers. |
| Secret-safe logging | [`/home/aiwithapex/projects/hermes/agent/redact.py:491`](/home/aiwithapex/projects/hermes/agent/redact.py:491) and [`/home/aiwithapex/projects/hermes/agent/redact.py:803`](/home/aiwithapex/projects/hermes/agent/redact.py:803) | `redact_sensitive_text`, `RedactingFormatter` | **Reference implementation.** Build a focused structured redactor for Codex/Tavily/job data rather than pulling the broad terminal/browser redactor. |

Useful donor tests for those behaviors:

- [`/home/aiwithapex/projects/hermes/tests/run_agent/test_iteration_budget_race.py`](/home/aiwithapex/projects/hermes/tests/run_agent/test_iteration_budget_race.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_tool_guardrails.py`](/home/aiwithapex/projects/hermes/tests/agent/test_tool_guardrails.py)
- [`/home/aiwithapex/projects/hermes/tests/run_agent/test_tool_call_guardrail_runtime.py`](/home/aiwithapex/projects/hermes/tests/run_agent/test_tool_call_guardrail_runtime.py)
- [`/home/aiwithapex/projects/hermes/tests/test_model_tools.py`](/home/aiwithapex/projects/hermes/tests/test_model_tools.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_plugin_llm.py`](/home/aiwithapex/projects/hermes/tests/agent/test_plugin_llm.py)
- [`/home/aiwithapex/projects/hermes/tests/test_retry_utils.py`](/home/aiwithapex/projects/hermes/tests/test_retry_utils.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_error_classifier.py`](/home/aiwithapex/projects/hermes/tests/agent/test_error_classifier.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_redact.py`](/home/aiwithapex/projects/hermes/tests/agent/test_redact.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_turn_context.py`](/home/aiwithapex/projects/hermes/tests/agent/test_turn_context.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_turn_finalizer_iteration_limit_exit.py`](/home/aiwithapex/projects/hermes/tests/agent/test_turn_finalizer_iteration_limit_exit.py)

### Codex subscription authentication and execution

| Requirement | Absolute Hermes implementation example | Relevant region | Use |
|---|---|---|---|
| Official app-server process/protocol lifecycle | [`/home/aiwithapex/projects/hermes/agent/transports/codex_app_server.py:54`](/home/aiwithapex/projects/hermes/agent/transports/codex_app_server.py:54) | `CodexAppServerClient` | **Reference implementation.** The official `openai-codex` SDK replaces this raw JSON-RPC/subprocess client. |
| Turn lifecycle, cancellation, timeout, auth failure, usage | [`/home/aiwithapex/projects/hermes/agent/transports/codex_app_server_session.py:192`](/home/aiwithapex/projects/hermes/agent/transports/codex_app_server_session.py:192) | `CodexAppServerSession` | **Reference implementation plus selected behavior.** Recreate the local timeout/interrupt/error/usage wrapper; let the SDK own transport and refresh. |
| Stable streamed events/tool IDs | [`/home/aiwithapex/projects/hermes/agent/transports/codex_event_projector.py:69`](/home/aiwithapex/projects/hermes/agent/transports/codex_event_projector.py:69) | `CodexEventProjector` | **Selected-logic pull.** Adapt only assistant progress, MCP/dynamic tool events, deterministic call identity, and terminal usage. Exclude shell/file/reasoning projection. |
| Progress and token accounting | [`/home/aiwithapex/projects/hermes/agent/codex_runtime.py:28`](/home/aiwithapex/projects/hermes/agent/codex_runtime.py:28) and [`/home/aiwithapex/projects/hermes/agent/codex_runtime.py:98`](/home/aiwithapex/projects/hermes/agent/codex_runtime.py:98) | `_codex_note_to_tool_progress`, `_record_codex_app_server_usage` | **Selected-logic pull.** Translate into local event and `RuntimeUsage` types. |
| Subscription provider declaration | [`/home/aiwithapex/projects/hermes/plugins/model-providers/openai-codex/__init__.py:6`](/home/aiwithapex/projects/hermes/plugins/model-providers/openai-codex/__init__.py:6) and [`/home/aiwithapex/projects/hermes/plugins/model-providers/openai-codex/plugin.yaml`](/home/aiwithapex/projects/hermes/plugins/model-providers/openai-codex/plugin.yaml) | OAuth provider profile | **Reject/exclude.** It proves the donor's direct subscription route exists, but the private backend/profile registry must not be copied. |
| OAuth storage/import/expiry/refresh races | [`/home/aiwithapex/projects/hermes/hermes_cli/auth.py:3319`](/home/aiwithapex/projects/hermes/hermes_cli/auth.py:3319) through [`/home/aiwithapex/projects/hermes/hermes_cli/auth.py:3725`](/home/aiwithapex/projects/hermes/hermes_cli/auth.py:3725) | Token read/sync/save/recovery/refresh/credential resolution | **Reject/exclude.** Use this only to understand failure cases. The SDK/Codex credential store owns these responsibilities. |
| Model discovery and validation | [`/home/aiwithapex/projects/hermes/hermes_cli/codex_models.py:191`](/home/aiwithapex/projects/hermes/hermes_cli/codex_models.py:191) | `get_codex_model_ids` and its cache/fallback helpers | **Reject/exclude.** Call the official SDK/app-server model-list operation; do not copy synthesized model fallbacks. |
| Direct Responses message/tool adaptation | [`/home/aiwithapex/projects/hermes/agent/codex_responses_adapter.py:313`](/home/aiwithapex/projects/hermes/agent/codex_responses_adapter.py:313) and [`/home/aiwithapex/projects/hermes/agent/codex_responses_adapter.py:1109`](/home/aiwithapex/projects/hermes/agent/codex_responses_adapter.py:1109) | Input conversion and response normalization | **Reject/exclude.** Reference only to understand tool-call IDs, encrypted reasoning state, and protocol burden avoided by app server. |
| Direct subscription transport | [`/home/aiwithapex/projects/hermes/agent/transports/codex.py:49`](/home/aiwithapex/projects/hermes/agent/transports/codex.py:49) | `ResponsesApiTransport` | **Reject/exclude.** Do not construct bearer requests to the private backend; the official runtime is selected. |

Useful donor tests for the Codex wrapper and the rejected alternative:

- [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_session.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_session.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_runtime.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_runtime.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_event_projector.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_event_projector.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_hermes_tools_mcp_server.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_hermes_tools_mcp_server.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_codex_ttfb_watchdog.py`](/home/aiwithapex/projects/hermes/tests/agent/test_codex_ttfb_watchdog.py)
- [`/home/aiwithapex/projects/hermes/tests/hermes_cli/test_auth_codex_provider.py`](/home/aiwithapex/projects/hermes/tests/hermes_cli/test_auth_codex_provider.py)
- [`/home/aiwithapex/projects/hermes/tests/hermes_cli/test_auth_codex_self_heal.py`](/home/aiwithapex/projects/hermes/tests/hermes_cli/test_auth_codex_self_heal.py)
- [`/home/aiwithapex/projects/hermes/tests/hermes_cli/test_codex_models.py`](/home/aiwithapex/projects/hermes/tests/hermes_cli/test_codex_models.py)
- [`/home/aiwithapex/projects/hermes/tests/agent/test_codex_responses_adapter.py`](/home/aiwithapex/projects/hermes/tests/agent/test_codex_responses_adapter.py)
- [`/home/aiwithapex/projects/hermes/tests/run_agent/test_run_agent_codex_responses.py`](/home/aiwithapex/projects/hermes/tests/run_agent/test_run_agent_codex_responses.py)

### Research, source extraction, and ingestion

| Requirement | Absolute Hermes implementation example | Relevant region | Use |
|---|---|---|---|
| Tavily HTTP client | [`/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:35`](/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:35) | `_tavily_request` | **Selected-logic pull.** Adapt timeout/request/error behavior to injected local settings and `httpx`. |
| Search/extract normalization | [`/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:64`](/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:64) and [`/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:79`](/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:79) | Result/document normalizers | **Selected-logic pull.** Return rich local source and extracted-document contracts instead of Hermes provider payloads. |
| Provider-level search/extract API | [`/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:130`](/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py:130) | `TavilyWebSearchProvider` | **Reference implementation.** Rebuild without the provider registry or environment globals. |
| Generic web tool behavior | [`/home/aiwithapex/projects/hermes/tools/web_tools.py:619`](/home/aiwithapex/projects/hermes/tools/web_tools.py:619) and [`/home/aiwithapex/projects/hermes/tools/web_tools.py:743`](/home/aiwithapex/projects/hermes/tools/web_tools.py:743) | `web_search_tool`, `web_extract_tool` | **Reference implementation.** It shows orchestration, truncation, redirect, and backend behavior, but the multi-provider registry/cache/output format is too coupled. |
| URL normalization and synchronous safety | [`/home/aiwithapex/projects/hermes/tools/url_safety.py:40`](/home/aiwithapex/projects/hermes/tools/url_safety.py:40) and [`/home/aiwithapex/projects/hermes/tools/url_safety.py:384`](/home/aiwithapex/projects/hermes/tools/url_safety.py:384) | `normalize_url_for_request`, `is_safe_url` | **Selected-logic pull.** Keep public HTTP(S), credential, host, IP, and sensitive-query validation; remove provider exceptions. |
| DNS and redirect safety | [`/home/aiwithapex/projects/hermes/tools/url_safety.py:470`](/home/aiwithapex/projects/hermes/tools/url_safety.py:470) and [`/home/aiwithapex/projects/hermes/tools/url_safety.py:479`](/home/aiwithapex/projects/hermes/tools/url_safety.py:479) | `async_is_safe_url`, `redirect_target_from_response` | **Selected-logic pull.** Make all redirects re-enter fail-closed DNS/URL validation. |
| YouTube URL/transcript input | [`/home/aiwithapex/projects/hermes/skills/media/youtube-content/scripts/fetch_transcript.py:26`](/home/aiwithapex/projects/hermes/skills/media/youtube-content/scripts/fetch_transcript.py:26) and [`/home/aiwithapex/projects/hermes/skills/media/youtube-content/scripts/fetch_transcript.py:50`](/home/aiwithapex/projects/hermes/skills/media/youtube-content/scripts/fetch_transcript.py:50) | `extract_video_id`, `fetch_transcript` | **Selected-logic pull.** Return typed timestamped segments; drop the script CLI and printing. |
| PDF page/metadata extraction | [`/home/aiwithapex/projects/hermes/skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py:15`](/home/aiwithapex/projects/hermes/skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py:15) and [`/home/aiwithapex/projects/hermes/skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py:56`](/home/aiwithapex/projects/hermes/skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py:56) | `extract_text`, `show_metadata` | **Selected-logic pull.** Return bounded typed page records and metadata; drop CLI, printing, arbitrary output paths, and image dumping. |

Useful donor research tests:

- [`/home/aiwithapex/projects/hermes/tests/tools/test_web_tools_tavily.py`](/home/aiwithapex/projects/hermes/tests/tools/test_web_tools_tavily.py)
- [`/home/aiwithapex/projects/hermes/tests/tools/test_url_safety.py`](/home/aiwithapex/projects/hermes/tests/tools/test_url_safety.py)
- [`/home/aiwithapex/projects/hermes/tests/integration/test_web_tools.py`](/home/aiwithapex/projects/hermes/tests/integration/test_web_tools.py)
- [`/home/aiwithapex/projects/hermes/tests/tools/test_web_tools_truncate.py`](/home/aiwithapex/projects/hermes/tests/tools/test_web_tools_truncate.py)

Hermes does not contain a coherent implementation of the required course
schemas, evidence ledger, claim-citation graph, curriculum planner, review pack,
assessment blueprint, accessible renderer, per-user job state, or delivery
idempotency. Those requirements remain local builds; the paths above are agent,
runtime, retrieval, and ingestion implementation examples--not substitutes for
the education-specific system.

## Minimum coherent extraction

### Selected Hermes-derived logic

| Area | Classification | Estimated adapted LOC |
|---|---|---:|
| Iteration budget | Mostly copy | 35-50 |
| Tool-loop guardrails | Pure logic adapted | 180-260 |
| Generic retry/backoff | Mostly copy | 35-55 |
| Tavily client and normalization | Pure logic adapted | 140-190 |
| URL/DNS/redirect safety | Pure logic adapted | 220-300 |
| Codex event, usage, timeout, and auth-error behavior | Pure behavior reimplemented | 150-220 |
| Local MCP server wiring | Behavior reimplemented | 70-110 |
| YouTube transcript helper | Pure logic adapted | 60-90 |
| PDF extraction helper | Pure logic adapted | 50-80 |
| **Total** |  | **940-1,355** |

"Mostly copy" still means changing imports, types, names, comments, and tests so
the result is a normal local module. "Reimplemented" means the Hermes behavior is
useful evidence, but copying the source would import too much coupling or
duplicate an official SDK feature.

### New local implementation

| Area | Estimated non-test LOC |
|---|---:|
| Domain schemas and artifact validation | 500-750 |
| Bounded workflow kernel, job state, cancellation, checkpoints | 350-500 |
| Research service, evidence ledger, citation validation | 500-750 |
| Education generation stages and quality checks | 500-750 |
| Remaining document/media ingestion | 300-500 |
| Request identity, webhook, authorization, idempotency | 250-400 |
| Deterministic render/delivery layer | 300-450 |
| Policy, focused redaction, observability | 200-300 |
| **Total** | **2,900-4,400** |

## Source and symbol inventory

All donor links below are relative source references for extraction review. They
must not become runtime paths.

### Iteration and tool-call control

#### Iteration budget

- Source:
  [`/home/aiwithapex/projects/hermes/agent/iteration_budget.py`](/home/aiwithapex/projects/hermes/agent/iteration_budget.py)
- Symbols: `IterationBudget`, `consume`, `refund`, `used`, `remaining`.
- Why: dependency-light, concurrency-safe iteration accounting is directly
  useful to a bounded local kernel.
- Extract: the lock-protected consume/refund counter and remaining-budget
  calculation.
- Remove: Hermes-specific naming and any assumption that a single model loop is
  the entire job.
- Destination: `src/txt2crs/ai/budgets.py`.
- Estimate: 35-50 adapted LOC.
- Tests to port conceptually:
  [`/home/aiwithapex/projects/hermes/tests/run_agent/test_iteration_budget_race.py`](/home/aiwithapex/projects/hermes/tests/run_agent/test_iteration_budget_race.py).

The local version must become a composite `RunBudget` that also limits elapsed
time, total/per-tool calls, tokens, retries, sources, fetched bytes, and
subscription quota.

#### Repeated-call guardrails

- Source:
  [`/home/aiwithapex/projects/hermes/agent/tool_guardrails.py`](/home/aiwithapex/projects/hermes/agent/tool_guardrails.py)
- Symbols: `ToolCallGuardrailConfig`, `ToolCallSignature`,
  `ToolGuardrailDecision`, `canonical_tool_args`,
  `ToolCallGuardrailController`.
- Why: canonical argument signatures and repeated-call detection prevent
  expensive or stuck research loops.
- Extract: deterministic argument canonicalization, exact-repeat and
  failure-repeat accounting, and explicit allow/deny decisions.
- Remove: Hermes tool-name conventions, result classifiers, registry access,
  and generic function-call payloads.
- Destination: `src/txt2crs/ai/tool_guardrails.py`.
- Estimate: 180-260 adapted LOC.
- Tests to adapt:
  [`/home/aiwithapex/projects/hermes/tests/agent/test_tool_guardrails.py`](/home/aiwithapex/projects/hermes/tests/agent/test_tool_guardrails.py)
  and
  [`/home/aiwithapex/projects/hermes/tests/run_agent/test_tool_call_guardrail_runtime.py`](/home/aiwithapex/projects/hermes/tests/run_agent/test_tool_call_guardrail_runtime.py).

The local controller sees only typed `research_search` and `research_extract`
calls. Tool failures are classified from local result types rather than parsed
from arbitrary text.

#### Generic retry

- Source:
  [`/home/aiwithapex/projects/hermes/agent/retry_utils.py`](/home/aiwithapex/projects/hermes/agent/retry_utils.py)
- Symbol: `jittered_backoff`.
- Why: small, dependency-free exponential delay behavior.
- Extract: bounded exponential backoff with injected randomness for tests.
- Remove: provider-specific retry branches.
- Destination: `src/txt2crs/ai/retry.py`.
- Estimate: 35-55 adapted LOC.
- Tests to adapt:
  [`/home/aiwithapex/projects/hermes/tests/test_retry_utils.py`](/home/aiwithapex/projects/hermes/tests/test_retry_utils.py).

### Codex runtime behavior

#### Official app-server client: replace rather than copy

- Sources:
  [`/home/aiwithapex/projects/hermes/agent/transports/codex_app_server.py`](/home/aiwithapex/projects/hermes/agent/transports/codex_app_server.py)
  and
  [`/home/aiwithapex/projects/hermes/agent/transports/codex_app_server_session.py`](/home/aiwithapex/projects/hermes/agent/transports/codex_app_server_session.py).
- Useful symbols/behavior: `CodexAppServerClient`, `CodexAppServerSession`,
  `TurnResult`, `_classify_oauth_failure`, turn watchdog, interrupt,
  `_apply_token_usage_notification`.
- Why: they demonstrate the required lifecycle and failure cases.
- Extract: no raw JSON-RPC client. Reimplement only the small local error,
  timeout, cancellation, and usage behavior around the official SDK.
- Remove: raw subprocess framing, reader threads, Hermes subprocess
  environment, Hermes redaction, approval routing, and Hermes run-agent types.
- Destination: `src/txt2crs/ai/codex_runtime.py`,
  `src/txt2crs/ai/errors.py`, and `src/txt2crs/ai/usage.py`.
- Estimate: included in the 150-220 LOC Codex behavior allocation.
- Tests to translate:
  [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_session.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_session.py),
  [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_runtime.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_app_server_runtime.py),
  and
  [`/home/aiwithapex/projects/hermes/tests/agent/test_codex_ttfb_watchdog.py`](/home/aiwithapex/projects/hermes/tests/agent/test_codex_ttfb_watchdog.py).

#### Stream/event projection

- Sources:
  [`/home/aiwithapex/projects/hermes/agent/transports/codex_event_projector.py`](/home/aiwithapex/projects/hermes/agent/transports/codex_event_projector.py)
  and
  [`/home/aiwithapex/projects/hermes/agent/codex_runtime.py`](/home/aiwithapex/projects/hermes/agent/codex_runtime.py).
- Useful symbols: `_deterministic_call_id`, `ProjectionResult`,
  `CodexEventProjector`, `_codex_note_to_tool_progress`,
  `_record_codex_app_server_usage`.
- Why: stable tool-call identity, progress projection, and token capture are
  needed for retries and user-visible job progress.
- Extract: stable IDs and the idea of projecting SDK events into a small local
  event vocabulary.
- Remove: shell-command/file-edit projection, Hermes message format, hidden
  reasoning display, `AIAgent` coupling, and Responses-API fallback.
- Destination: `src/txt2crs/ai/events.py` and
  `src/txt2crs/ai/usage.py`.
- Estimate: included in the 150-220 LOC Codex behavior allocation.
- Tests to translate:
  [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_event_projector.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_codex_event_projector.py).

The local event vocabulary should be limited to `turn_started`,
`assistant_progress`, `tool_started`, `tool_completed`, `usage_updated`,
`turn_completed`, `turn_failed`, and `turn_cancelled`. Do not store or expose
private chain-of-thought.

#### Local tool server

- Source:
  [`/home/aiwithapex/projects/hermes/agent/transports/hermes_tools_mcp_server.py`](/home/aiwithapex/projects/hermes/agent/transports/hermes_tools_mcp_server.py).
- Useful symbols: `_signature_from_schema`, `_build_server`.
- Why: it shows how Hermes exposes Python tools to the Codex app server.
- Extract: no source verbatim unless it remains dependency-free. Reimplement a
  much smaller server with static registrations.
- Remove: Hermes tool registry, `handle_function_call`, environment plumbing,
  tool discovery, and all unrelated tools.
- Destination: `src/txt2crs/research/mcp_server.py`.
- Estimate: 70-110 LOC.
- Tests to translate:
  [`/home/aiwithapex/projects/hermes/tests/agent/transports/test_hermes_tools_mcp_server.py`](/home/aiwithapex/projects/hermes/tests/agent/transports/test_hermes_tools_mcp_server.py).

### Research

#### Tavily search and extract

- Source:
  [`/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py`](/home/aiwithapex/projects/hermes/plugins/web/tavily/provider.py).
- Symbols: `_tavily_request`, `_normalize_tavily_search_results`,
  `_normalize_tavily_documents`, `TavilyWebSearchProvider`.
- Why: it provides the smallest search-plus-page-extraction path already
  represented in Hermes.
- Extract: request construction, timeouts, result normalization, and the
  search/extract split.
- Remove: Hermes provider base classes, environment lookup, interruption
  globals, provider registry, and arbitrary base-URL configuration.
- Destination: `src/txt2crs/research/tavily.py`.
- Estimate: 140-190 adapted LOC.
- Tests to adapt:
  [`/home/aiwithapex/projects/hermes/tests/tools/test_web_tools_tavily.py`](/home/aiwithapex/projects/hermes/tests/tools/test_web_tools_tavily.py).

The local client receives its secret through dependency injection, fixes the
approved HTTPS origin in production, returns typed `SearchHit` and
`ExtractedDocument` values, and never includes the secret in errors or logs.

#### URL, DNS, and redirect safety

- Source:
  [`/home/aiwithapex/projects/hermes/tools/url_safety.py`](/home/aiwithapex/projects/hermes/tools/url_safety.py).
- Symbols: `normalize_url_for_request`, `sensitive_query_param_name`,
  `_is_blocked_ip`, `is_always_blocked_url`, `is_safe_url`,
  `async_is_safe_url`, `redirect_target_from_response`.
- Why: research extraction creates a direct SSRF and credential-leak boundary.
- Extract: scheme/authority normalization, hostname and DNS validation,
  blocked-address rules, sensitive query checks, and redirect target handling.
- Remove: Hermes feature flags, provider exceptions, QQ-specific behavior,
  compatibility utilities, and fail-open modes.
- Destination: `src/txt2crs/security/url_safety.py`.
- Estimate: 220-300 adapted LOC.
- Tests to adapt:
  [`/home/aiwithapex/projects/hermes/tests/tools/test_url_safety.py`](/home/aiwithapex/projects/hermes/tests/tools/test_url_safety.py).

The local implementation must be fail-closed. It rejects credentials in URLs,
non-HTTP(S) schemes, localhost, private/loopback/link-local/reserved/multicast/
unspecified addresses, carrier-grade NAT, cloud metadata endpoints, DNS answers
that resolve to blocked addresses, and redirects that have not been revalidated.
It must cap redirects, response bytes, decompression, and total fetch time.

#### PDF and YouTube inputs

- Sources:
  [`/home/aiwithapex/projects/hermes/skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py`](/home/aiwithapex/projects/hermes/skills/productivity/ocr-and-documents/scripts/extract_pymupdf.py)
  and
  [`/home/aiwithapex/projects/hermes/skills/media/youtube-content/scripts/fetch_transcript.py`](/home/aiwithapex/projects/hermes/skills/media/youtube-content/scripts/fetch_transcript.py).
- Useful symbols: PDF extraction/metadata helpers; `extract_video_id`,
  `format_timestamp`, `fetch_transcript`.
- Why: they cover two high-value "any input" forms without importing a large
  ingestion framework.
- Extract: text/metadata extraction and video-ID/timestamp/transcript logic.
- Remove: command-line interfaces, file-output behavior, global environment
  reads, and free-form string returns.
- Destination: `src/txt2crs/ingestion/pdf.py` and
  `src/txt2crs/ingestion/youtube.py`.
- Estimate: 110-170 adapted LOC combined.
- Tests: create local fixtures for malformed PDFs, encrypted PDFs, empty pages,
  transcript absence, alternate YouTube URL forms, timestamps, language
  selection, and maximum size/duration.

DOCX, PPTX, plain text, images, audio, and general web-page adapters should use
their maintained libraries directly. They do not justify extracting large
Hermes media/transcription subsystems.

## Explicit exclusions

### Direct ChatGPT OAuth and Responses transport

Do not copy:

- [`/home/aiwithapex/projects/hermes/hermes_cli/auth.py`](/home/aiwithapex/projects/hermes/hermes_cli/auth.py),
  including
  `_read_codex_tokens`, `_save_codex_tokens`,
  `_recover_codex_tokens_from_cli`, `refresh_codex_oauth_pure`,
  `_refresh_codex_auth_tokens`, `_import_codex_cli_tokens`, and
  `resolve_codex_runtime_credentials`;
- [`/home/aiwithapex/projects/hermes/hermes_cli/codex_models.py`](/home/aiwithapex/projects/hermes/hermes_cli/codex_models.py);
- [`/home/aiwithapex/projects/hermes/agent/codex_responses_adapter.py`](/home/aiwithapex/projects/hermes/agent/codex_responses_adapter.py);
- [`/home/aiwithapex/projects/hermes/agent/transports/codex.py`](/home/aiwithapex/projects/hermes/agent/transports/codex.py);
- direct Responses streaming in
  [`/home/aiwithapex/projects/hermes/agent/codex_runtime.py`](/home/aiwithapex/projects/hermes/agent/codex_runtime.py);
- the OpenAI-Codex Hermes provider plugin.

That path calls a ChatGPT backend directly, owns OAuth token import/storage/
refresh, translates messages and tools into Responses input items, preserves
tool-call identifiers and encrypted reasoning items, normalizes streaming
events, discovers models, and recovers from refresh-token races. It is thousands
of lines of security- and protocol-sensitive code. It also relies on details
that are not the documented third-party product-integration contract.

The official SDK/app server already owns authentication, refresh, protocol
framing, event types, tool-call identity, model discovery, and output schemas.
Duplicating those responsibilities would increase risk without satisfying an
additional product requirement.

### Hermes's general conversation loop

Do not copy `agent/conversation_loop.py`. It is large, provider-neutral,
interactive-agent infrastructure with many tool, terminal, memory, approval,
fallback, and compatibility concerns that `txt2crs` does not need. Its useful
ideas are represented by the much smaller budget, retry, and guardrail slices.

### Generic Hermes registries and structured-output wrappers

Do not copy `agent/model_tools.py` or `agent/plugin_llm.py`. Build an explicit
two-tool allowlist and local Pydantic validation. Codex's `outputSchema` is a
generation constraint, not a replacement for validation.

### General error classifier and redactor

Do not copy the large Hermes-wide error classifier or redaction module. Build a
focused local taxonomy:

- reauthentication required;
- subscription quota/rate limit;
- retryable transport/overload;
- cancellation/timeout;
- tool-policy rejection;
- schema/quality rejection;
- permanent provider error.

Build a small structured redactor for authorization headers, access/refresh
tokens, query-string secrets, account identifiers, and provider response bodies.
Never log raw authentication objects or hidden reasoning.

### Broad tool and browser systems

Do not extract shell execution, file editing, arbitrary HTTP fetch, browser
automation, computer use, memory, terminal, plugin discovery, or unrestricted
MCP. They are unnecessary for the first product and materially expand the attack
surface.

## Bounded local agent kernel

The product needs an agent, but it needs a deliberately small one.

### Ownership boundary

```text
txt2crs job controller
  -> validates identity, input, policy, and budget
  -> starts/resumes one pipeline stage
  -> asks Codex for a schema-constrained result
       -> Codex may call only the local research MCP tools
       -> MCP service independently validates and budgets each call
  -> validates result, evidence, citations, and quality
  -> checkpoints the accepted artifact
  -> advances or performs a bounded repair turn
```

Codex owns the inner model/tool interaction for a turn. The local kernel owns
the durable workflow and all hard limits. This avoids rebuilding a streaming
model protocol while preserving local control.

### Minimum kernel interface

```python
class ModelRuntime(Protocol):
    async def account(self) -> RuntimeAccount: ...
    async def list_models(self) -> list[RuntimeModel]: ...
    async def run_turn(
        self,
        request: TurnRequest,
        output_schema: dict[str, object],
        cancellation: CancellationToken,
    ) -> TurnResult: ...


class ResearchToolService(Protocol):
    async def search(self, request: SearchRequest) -> SearchResult: ...
    async def extract(self, request: ExtractRequest) -> ExtractResult: ...
```

The production implementation is `CodexSubscriptionRuntime`; tests use a
deterministic fake. Domain and pipeline code must not depend on SDK event
classes.

### Turn and tool loop

For every stage:

1. Load the last accepted checkpoint and remaining `RunBudget`.
2. Build a prompt from trusted instructions, versioned task data, and bounded
   evidence--not raw application secrets or unrelated job content.
3. Start or resume an isolated Codex thread.
4. Stream typed events into a local progress ledger.
5. Allow only registered research tools.
6. Enforce tool input schemas, URL policy, call counts, repeat signatures,
   source/byte limits, and cancellation inside the MCP service.
7. Receive schema-constrained output.
8. Validate it again with Pydantic and deterministic invariants.
9. Verify every citation and evidence identifier.
10. Accept and checkpoint, or run a bounded repair turn with explicit errors.
11. Stop on success, budget exhaustion, cancellation, permanent error, or
    subscription quota exhaustion.

No failure path may silently return a partial artifact as complete.

### Hard budgets

`RunBudget` should include:

- maximum turns per stage and across the job;
- maximum research calls overall and per tool;
- maximum exact and equivalent repeated calls;
- maximum sources, extracted bytes, and per-document bytes;
- maximum input and output tokens when reported;
- maximum wall-clock time per turn, stage, and job;
- maximum retry attempts and repair attempts;
- maximum concurrent fetches;
- current subscription rate-limit window/remaining allowance when available.

Subscription usage does not have a reliable dollar cost per request. Store
`billing_source="chatgpt_subscription"` and `estimated_api_cost=null`; do not
misreport the cost as zero. Preserve a provider-neutral optional cost field for
a future API-key runtime.

### Retry, cancellation, and recovery

- Retry only idempotent work after transient transport errors, overload, and
  eligible rate limits.
- Honor server retry hints, add jitter, and cap delay and attempts.
- Do not retry authentication rejection, unsafe URLs, policy failures, or
  invalid schemas without a corrective action.
- Let Codex manage token refresh. After a refresh-related SDK failure, permit at
  most one clean retry; then require user reauthentication.
- Send `turn.interrupt` through the SDK on user cancellation or deadline.
- Check cancellation before each retry, research request, validation pass, and
  checkpoint.
- Write checkpoints only after schema and citation validation.
- Use stage idempotency keys and compare-and-swap state transitions so duplicate
  webhooks or workers do not duplicate work.
- Resume from the last accepted stage, never from unvalidated streamed text.

## Codex subscription runtime

### Why the official app-server/SDK path wins

OpenAI documents the Codex app server as the interface for deep product
integration including authentication, conversation history, approvals, and
streamed events. It uses JSON-RPC over local stdio and exposes thread, turn,
interrupt, account, model, rate-limit, and usage operations. The official Python
SDK controls that app server and ships with a pinned CLI runtime.

References:

- [Codex app-server integration](https://learn.chatgpt.com/docs/app-server)
- [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)
- [Codex authentication](https://developers.openai.com/codex/auth)
- [Codex pricing and plan availability](https://developers.openai.com/codex/pricing)

The SDK is currently beta, and the app-server surface can evolve. Pin the exact
SDK and runtime versions, generate and commit the matching protocol schemas, and
run contract tests before every upgrade.

The reviewed package now pins `openai-codex==0.144.4` (Python 3.10+) with its
matching `openai-codex-cli-bin==0.144.4` runtime. The locally installed Codex
CLI used for a separate schema inspection was `0.144.6`; its schema includes turn output
schemas, account/rate-limit/usage messages, model listing, token usage, and
dynamic/MCP tool-call events. These observations are a versioned snapshot, not
permission to mix CLI and SDK versions. Implementation should pin one tested SDK
bundle and regenerate its schemas.

### Direct OAuth/Responses versus app server

| Criterion | Hermes direct OAuth + Responses | Hermes raw app-server client | Official SDK + app server |
|---|---|---|---|
| Subscription sign-in | Yes, but app owns copied OAuth details and tokens | Yes | Yes, managed by Codex |
| Documented integration surface | Weak for direct backend use | Stronger protocol surface | **Official recommended integration** |
| Token storage/refresh | Application responsibility | Codex responsibility | Codex responsibility |
| Protocol/event maintenance | Large custom Responses adapter | Raw JSON-RPC client/session | SDK typed API and pinned runtime |
| Model discovery | Custom cache/fallback logic | RPC | SDK/app-server model list |
| Structured output | Custom adapter/validation | `outputSchema` | `output_schema` plus local validation |
| Tool identity/encrypted reasoning | Application must preserve wire semantics | Server owns semantics | Server/SDK owns semantics |
| Estimated runtime-specific local code | Roughly 1,900-2,900 adapted LOC | Roughly 1,200-1,800 adapted LOC | **Roughly 220-330 wrapper/MCP LOC** |
| Security burden | Highest | Medium | **Lowest** |
| Decision | Reject | Reject as redundant | **Select** |

The direct path is not "more independent"; it makes `txt2crs` dependent on
private protocol behavior. The app-server SDK is an external declared
dependency, not a Hermes dependency, and is the smallest supportable path.

### Credential and account design

1. Launch Codex through the pinned SDK in an isolated worker.
2. Support SDK-managed ChatGPT browser login and device-code login.
3. Let Codex store and refresh its own credentials. `txt2crs` must not parse,
   copy, serialize, or refresh `auth.json`.
   An existing Codex CLI login may be reused only by pointing the SDK-managed
   runtime at that same user's isolated `CODEX_HOME`; this is credential reuse
   by Codex, not an application-level import.
4. Prefer the OS credential store for a local desktop/operator deployment. If a
   file store is unavoidable, use a per-user `CODEX_HOME`, `0700` directories,
   `0600` files, encrypted storage, and no shared mounts.
5. Remove `OPENAI_API_KEY`, `CODEX_API_KEY`, and unrelated credentials from the
   child process environment for subscription-only mode.
6. After login, call the account endpoint and require the account type to be
   ChatGPT. Reject an API-key account in subscription-only mode.
7. Isolate threads, credential storage, logs, and job data per authenticated
   application user.
8. Never place access tokens in the database, events, analytics, exception
   telemetry, prompts, or research tools.
9. Surface "reauthentication required" without echoing provider response bodies.

Codex stores login details in its configured credential store and automatically
refreshes them; file-based credentials must be treated like passwords. The
application should rely on that contract rather than duplicating Hermes's token
pool and recovery code.

### Model, schema, event, and usage handling

- Discover eligible models through the SDK/app-server model list. Do not
  synthesize speculative model identifiers.
- Pin a configured default only after confirming it is in the discovered list.
- Pass the versioned JSON Schema for each artifact to the SDK turn.
- Validate the returned object again with the exact local Pydantic model.
- Preserve SDK tool-call identifiers in the event ledger and result records.
- Do not parse or replay encrypted reasoning items; the server owns them.
- Record input/output/cached/reasoning token values made available by the SDK,
  model ID, turn/thread ID, latency, stage, retry count, and result status.
- Read account/rate-limit/usage information where the pinned public SDK exposes
  it. If a needed operation requires a lower-level request API, wrap it behind
  a version-pinned adapter and contract test it; do not silently depend on an
  undocumented field.
- Expose progress summaries, not chain-of-thought.

### Subscription accounting

The acceptance proof for subscription mode is:

- API environment variables are absent;
- the runtime account is reported as ChatGPT rather than API-key;
- a turn completes and reports model/token usage;
- a permitted research tool is called with a stable identifier;
- rate-limit or usage-window data is recorded when available;
- expired credentials refresh through Codex without application token handling;
- API-key login is rejected by the subscription-only policy.

ChatGPT plans include Codex subject to plan limits and credits. Those limits are
not equivalent to Platform API token billing, so dashboards must distinguish
subscription allowance, purchased credits, and API cost.

## Deployment and account constraints

### Supported first deployment

The lowest-risk hackathon deployment is a local or single-operator backend where
the operator signs into their own eligible ChatGPT subscription. A hosted
version may use per-user sign-in only if each user has their own eligible
account, credentials and worker state are strongly isolated, and OpenAI confirms
the intended integration model.

### What is not allowed as an assumption

A founder's personal ChatGPT subscription is not a shared model-API credential
for every visitor to a public application. OpenAI's account-sharing guidance
says an account is intended for the individual who created it, and the Terms of
Use prohibit sharing credentials or making an account available to others:

- [OpenAI account sharing policy](https://help.openai.com/en/articles/10471989-openai-account-sharing-policy)
- [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/)
- [Using Codex with a ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chat)

Business, Enterprise, and Edu deployments have workspace membership, seat,
administrator, and policy considerations:

- [OpenAI Service Terms](https://openai.com/policies/service-terms/)

Before a multi-user public or commercial launch:

- obtain OpenAI confirmation for the product integration and known-client
  requirements;
- define whether users bring their own eligible ChatGPT account or receive
  managed workspace seats;
- verify tenant isolation, admin control, retention, privacy, and regional
  requirements;
- prohibit account pooling and credential sharing;
- keep an API-based provider as a future architectural option if hosted service
  requirements cannot be met, while retaining subscription mode as the required
  initial runtime.

The SDK is described as a coding-focused Codex runtime. Educational generation
quality and policy suitability therefore require an explicit evaluation gate;
the subscription requirement alone does not establish product fit.

### Worker isolation

Codex is capable of coding-agent actions, so an untrusted public prompt must not
receive an unrestricted local environment. Each worker should have:

- an ephemeral, non-privileged workspace;
- no repository, home-directory, SSH, cloud, or deployment credentials;
- no shell/file-edit tools exposed to the education turn;
- no ambient network access except the local allowlisted MCP endpoint;
- resource and process limits;
- per-user `CODEX_HOME`;
- structured, redacted logs;
- guaranteed cleanup after completion.

Use local stdio for the app server. Do not base the first deployment on an
experimental remote WebSocket transport.

## Research and evidence architecture

### Research stages

1. Convert the user's input into a normalized `InputDocument`.
2. Ask Codex for a schema-constrained research plan containing questions,
   preferred source types, recency needs, and stop conditions.
3. Execute bounded searches through `research_search`.
4. Rank candidates by relevance, authority, diversity, and freshness.
5. Validate and extract selected public URLs through `research_extract`.
6. Store normalized sources and immutable evidence excerpts.
7. Ask for gap/conflict analysis; permit a bounded follow-up round.
8. Freeze an evidence set for the course version.
9. Generate course claims against evidence identifiers.
10. Verify citations mechanically and semantically before acceptance.
11. Generate review materials and the assessment from the same approved course
    and evidence version.

### Required data contracts

At minimum:

- `InputDocument`: media type, normalized text, metadata, content hash, warnings.
- `ResearchPlan`: questions, source constraints, freshness, stop criteria.
- `SourceRecord`: canonical URL, title, publisher/author, publication and
  retrieval dates, content hash, source type, authority signals.
- `EvidenceExcerpt`: source ID, exact bounded excerpt or faithful structured
  extract, location, content hash, retrieval method.
- `ClaimCitation`: artifact location, claim text/hash, evidence IDs, support
  verdict, verifier version.
- `Course`: title, audience, prerequisites, objectives, modules, lessons,
  activities, references, glossary.
- `ReviewPack`: objective map, summaries, study guide, flashcards, practice.
- `Assessment`: blueprint, questions, answers, rationales, scoring, difficulty,
  objective and evidence links.
- `JobCheckpoint`: state, artifact version, schema version, evidence version,
  budget snapshot, idempotency key.
- `RuntimeUsage`: account type, billing source, model, token values, latency,
  rate-limit snapshot, retries, result.

Every contract must be versioned and reject unknown or invalid critical fields.

### Citation acceptance

A citation is valid only when:

- its source and evidence IDs exist in the frozen evidence set;
- the stored excerpt still matches its content hash;
- the artifact claim is actually supported by the excerpt;
- the source location is displayable to the user;
- the cited source is not merely a search-result snippet when the page was
  available;
- conflicts and material uncertainty are disclosed;
- high-risk claims meet the configured source-authority policy.

URL presence alone is not evidence. Citation verification should combine
deterministic existence/hash checks with a schema-constrained support judgment
and sampled human/evaluation review.

### Research security

- Search terms are data, not instructions.
- Extracted pages are untrusted content and cannot alter system rules, tool
  access, budgets, or artifact schemas.
- Strip active markup and hidden content that is not instructionally relevant.
- Keep quoted evidence separate from trusted prompts.
- Revalidate every redirect and DNS result.
- Disallow arbitrary headers, cookies, proxies, alternate base URLs, and
  authenticated/private resources in the first release.
- Limit documents, bytes, decompression ratio, redirects, and processing time.
- Record retrieval failures without leaking secrets.
- Treat prompt-injection indicators as warnings and segmentation signals, not a
  blanket reason to reject legitimate educational security material.

## Education pipeline

The minimum end-to-end pipeline remains staged rather than a single giant turn:

1. `ingest_input`
2. `classify_and_scope`
3. `plan_research`
4. `collect_evidence`
5. `resolve_gaps_and_conflicts`
6. `design_course`
7. `write_lessons`
8. `verify_course`
9. `generate_review_pack`
10. `generate_assessment_and_answer_sheet`
11. `cross_validate_artifacts`
12. `render_and_deliver`

Each AI stage receives the smallest necessary trusted state and produces one
versioned contract. Deterministic code performs schema checks, objective
coverage, citation existence, duplicate-question detection, answer-key
alignment, scoring totals, and rendering. A bounded repair turn receives only
the validation errors it is permitted to fix.

The canonical approved `Course` is the source for both review materials and the
assessment. This prevents the three deliverables from drifting into independent
and contradictory model outputs.

## Proposed destination modules

```text
src/txt2crs/
  ai/
    budgets.py
    codex_runtime.py
    errors.py
    events.py
    kernel.py
    retry.py
    tool_guardrails.py
    usage.py
  domain/
    models.py
    validation.py
  generation/
    pipeline.py
    prompts.py
    quality.py
  ingestion/
    service.py
    pdf.py
    youtube.py
    documents.py
    media.py
  jobs/
    service.py
    store.py
  research/
    evidence.py
    mcp_server.py
    service.py
    tavily.py
  rendering/
    course.py
    review_pack.py
    assessment.py
  security/
    policy.py
    redaction.py
    url_safety.py
```

This is a responsibility map, not a demand for one class per file. Closely
related modules can remain small. Avoid introducing a plugin framework, message
bus, or provider abstraction beyond the one `ModelRuntime` boundary until a
second implementation actually exists.

## Dependency plan

### Declare directly in `txt2crs`

- a pinned `openai-codex` Python SDK version and its pinned runtime;
- Pydantic for versioned data contracts;
- `httpx` for bounded Tavily requests where the SDK does not own transport;
- FastMCP or the SDK-compatible MCP package used by the local tool server;
- maintained libraries selected for PDF, documents, and media;
- libraries required by independently useful persistence adapters, preferably
  behind optional dependency groups when they are not part of the core runtime.

The FastAPI framework, application authentication, web-only database models,
and Alembic integration belong to the future `backend/app/` shell rather than
this exportable library.

Do not copy third-party package source out of the Hermes environment. Declare
and lock each dependency directly.

### Protocol/version control

- Commit the exact SDK/runtime versions.
- Generate JSON Schema from the pinned Codex app server in CI or during an
  explicit upgrade task.
- Compare generated schemas against committed fixtures.
- Fail upgrades on incompatible account, model, turn, tool, event, output
  schema, usage, or interrupt changes.
- Keep SDK-specific objects inside `codex_runtime.py`.

### Transitive dependency disposition

No selected source is considered extracted until every import has one of the
following explicit dispositions:

| Selected behavior | Hermes transitive dependencies found | Local disposition |
|---|---|---|
| `IterationBudget` | Standard-library threading only | Use the Python standard library; replace all run-agent types with local `RunBudget` |
| Tool guardrails | Hermes tool-result classification and tool-name conventions | Keep only canonicalization/counters/decisions; use local Pydantic tool inputs and typed local result status |
| `jittered_backoff` | Standard library randomness/math/time concepts; provider branches nearby | Keep the pure delay calculation; inject clock/sleeper/randomness; exclude provider branches |
| Tavily provider | Hermes provider base class, environment helpers, interruption state, shared web-tool models | Replace with direct `httpx`, injected `TavilySettings`, local research models, and local cancellation |
| URL safety | Hermes config toggles, utility helpers, provider-specific exceptions | Replace with standard-library URL/IP/DNS handling plus local policy; no compatibility toggle or fail-open mode |
| Codex session/event behavior | Hermes subprocess environment, redaction, run-agent messages, raw JSON-RPC client | Replace transport entirely with pinned `openai-codex`; use local errors/events/usage/redaction |
| MCP server wiring | Hermes registry, schema adapter, `handle_function_call`, all installed tools | Replace with a directly declared MCP package and two static local tool registrations |
| YouTube helper | Script CLI, environment reads, transcript library | Declare the maintained transcript library directly; return local typed segments; exclude CLI |
| PDF helper | Script CLI/file output and PyMuPDF | Declare the maintained PDF library directly; return local page records; exclude CLI/output paths |

Before merging any extracted file, use an import graph plus string/AST scan to
prove that its closure ends at `txt2crs`, the Python standard library, or a
locked direct dependency. A familiar function name or copied test fixture does
not waive this check.

## License and provenance

Hermes is MIT-licensed. Before copying source:

1. retain the Hermes copyright and MIT license text in the distribution;
2. create a third-party notices file identifying Hermes and the pinned commit;
3. add a short provenance comment to each materially adapted source file,
   including the original relative path and commit;
4. retain relevant inline notices;
5. document substantial local modifications;
6. verify the license of each direct third-party dependency and any copied
   fixtures separately.

Provenance comments are permitted. They are not runtime dependencies. Static
scans must distinguish reviewed attribution text from executable imports, paths,
commands, configuration, and state access.

## Test-first implementation plan

The repository rule is tests before code. Implement each slice only after its
failing tests exist.

### Phase 1: contracts and budgets

Write:

- schema round-trip and rejection tests for every domain model;
- unknown-field, version, size, and cross-reference tests;
- concurrent budget reservation tests;
- exact/equivalent repeated tool-call tests;
- total/per-tool/time/token/source/byte exhaustion tests.

Then implement domain models, budgets, and guardrails.

### Phase 2: Codex runtime contract

Write SDK-fake tests for:

- subscription-only account acceptance and API-key rejection;
- API-key environment stripping;
- model discovery and invalid-model rejection;
- JSON Schema transmission and mandatory local validation;
- event projection and stable tool-call IDs;
- token/usage capture;
- timeout, interrupt, transient retry, quota exhaustion, and reauthentication;
- redaction of credentials and provider bodies.

Then implement the runtime wrapper. Add a separately marked live test that uses
a dedicated test account and is skipped unless explicitly enabled.

### Phase 3: research safety and provider

Write tests for:

- Tavily request/response normalization and safe error handling;
- timeouts, 429s, retries, malformed responses, and secret redaction;
- URL credentials, alternate IP encodings, IPv4/IPv6 blocked ranges, DNS
  rebinding defenses, metadata hosts, redirects, decompression, and byte caps;
- MCP tool schemas, allowlist rejection, cancellation, repeated calls, and
  budget enforcement.

Then implement URL safety, Tavily, and the local MCP service.

### Phase 4: evidence and citations

Write tests for:

- source canonicalization, hashes, excerpt locations, retrieval dates;
- source diversity/freshness rules;
- claim-to-evidence existence and support;
- changed/missing evidence rejection;
- conflicting evidence and uncertainty;
- prompt-injection isolation.

Then implement the research service and evidence ledger.

### Phase 5: ingestion

Write fixture-driven tests for every supported input, including corrupt,
oversized, encrypted, empty, unsupported, and mixed-language content. Then
implement the dispatcher and adapters.

### Phase 6: education artifacts

Write contract and invariant tests for:

- objective/module/lesson coverage;
- citations for factual claims;
- review-pack traceability to the approved course;
- assessment blueprint coverage and difficulty distribution;
- single- and multi-answer correctness;
- answer/rationale alignment;
- point totals, duplicate questions, leakage, and ambiguity;
- accessibility, locale, and reading-level settings.

Then implement staged generation, repair, and deterministic rendering.

### Phase 7: jobs and application boundary

Write tests for:

- request authentication/authorization;
- idempotent submission and duplicate webhooks;
- checkpoint compare-and-swap;
- crash/restart/resume;
- cancellation races;
- tenant isolation;
- partial-result non-delivery;
- progress and usage reporting.

Then implement the job service and delivery boundary.

### Phase 8: donor-absence acceptance

In a clean environment:

1. unset `OPENAI_API_KEY` and all other Platform API credentials;
2. use an isolated `CODEX_HOME`;
3. complete managed ChatGPT subscription login;
4. confirm the runtime reports a ChatGPT account;
5. run a turn that invokes one allowed research tool;
6. confirm structured output, local validation, stable tool identity, and usage;
7. exercise automatic credential refresh or its controlled test double;
8. confirm API-key accounts are rejected in subscription-only mode;
9. generate a course, review pack, assessment, and answer sheet from one input;
10. verify evidence and citations;
11. rename/remove the Hermes checkout;
12. rebuild, test, and repeat the offline/donor-absent suite;
13. scan source, manifests, scripts, images, and deployment files for forbidden
    Hermes imports, commands, paths, configuration keys, and runtime references.

## Acceptance criteria

The extraction is complete only when all of the following are true.

### Independence

- Hermes is absent and `txt2crs` builds, tests, starts, and completes jobs.
- Dependency locks contain no Hermes package, VCS/path reference, or submodule.
- No executable source launches, imports, calls, locates, or reads Hermes.
- No configuration or deployment artifact mounts Hermes or `~/.hermes`.
- Any remaining word "Hermes" is limited to reviewed documentation, license, or
  provenance comments.

### Subscription runtime

- Platform API credentials are unset.
- The authenticated account is verified as ChatGPT.
- API-key authentication is rejected in subscription-only mode.
- A Codex turn streams progress and returns schema-valid output.
- An allowlisted research tool executes and preserves its stable call ID.
- Token usage and billing source are recorded.
- Rate-limit/usage-window information is captured when exposed by the pinned
  public runtime.
- Expiry/refresh succeeds through Codex, and persistent failure becomes a
  redacted reauthentication state.
- Cancellation interrupts the active turn.

### Agent governance

- Every stage and tool call is bounded.
- Repeated equivalent calls terminate safely.
- Only explicitly registered research tools are visible.
- Invalid model output never becomes a checkpoint.
- Retry categories and maximum attempts are deterministic.
- A job resumes only from a valid durable checkpoint.
- Partial failure is visible and cannot masquerade as success.

### Research and product output

- Research is performed for claims that require grounding.
- All sources and excerpts have immutable IDs and metadata.
- Citations resolve to evidence and pass support checks.
- Conflicts/uncertainty are represented.
- The course covers its stated objectives.
- Review materials trace to the approved course.
- The assessment and answer sheet trace to the blueprint, course, and evidence.
- Size, accessibility, locale, safety, and high-risk-domain policies are
  enforced.

### Operational safety

- Credentials and hidden reasoning are absent from prompts, tools, logs, events,
  and stored artifacts.
- SSRF and redirect tests cover public/private boundary cases.
- User/tenant runtime state is isolated.
- A single personal subscription is never pooled across application users.
- Multi-user deployment remains gated on an approved account/workspace model.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| SDK/app-server beta changes | Runtime breakage | Exact pin, generated schema fixtures, contract tests, deliberate upgrades |
| Coding-focused model underperforms on education | Product-quality failure | Education eval set, rubric gates, human review for high-risk domains |
| Subscription quotas interrupt long jobs | Partial output | Stage checkpoints, usage windows, budget preflight, resumable status |
| Personal account used as shared backend | Terms/security violation | Per-user accounts or managed seats; OpenAI confirmation before multi-user launch |
| Credential leakage | Account compromise | SDK-owned store, isolation, no token parsing, focused redaction, minimal child environment |
| Codex tool overreach | Host compromise | Only local research MCP tools, ephemeral worker, no shell/files, minimal network |
| Web research prompt injection | Corrupted output/tool abuse | Untrusted-content boundary, typed tools, allowlist, evidence segmentation, validation |
| SSRF or oversized extraction | Internal access/resource exhaustion | Fail-closed DNS/URL/redirect validation and strict byte/time limits |
| Hallucinated citations | Untrustworthy course | Frozen evidence IDs, excerpt hashes, deterministic resolution, support verifier |
| Artifact drift | Review/test contradict course | One approved canonical course and cross-artifact validation |
| Over-extraction from Hermes | Maintenance burden | Enforce the named source inventory and LOC review before each pull |
| License notice omitted | Compliance issue | Third-party notices, per-file provenance, release checklist |

## Final recommendation

Extract only the small budget, guardrail, retry, Tavily, URL-safety, ingestion,
and event-semantics slices identified above. Build the education-specific
workflow, evidence system, contracts, and validation locally. Use the official
`openai-codex` SDK/app-server path for ChatGPT subscription authentication and
model execution.

Do **not** extract Hermes's direct OAuth/Responses transport, general
conversation loop, provider registry, token store, CLI, or runtime client.
Those components are larger, more coupled, and less supportable than the
official runtime.

This is the smallest code pull that can fulfill the complete AI needs while
honoring the hard rule that Hermes disappears after extraction: approximately
**940-1,355 adapted donor LOC**, **2,900-4,400 new local LOC**, and no Hermes
runtime dependency of any kind.
