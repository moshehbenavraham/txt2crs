# AIOS Runtime Supplemental Findings and Implementation References

> Status: supplemental architecture/reference evaluation only; no AIOS code has
> been copied.
>
> Target project: `/home/aiwithapex/projects/txt2crs`
>
> Reference project: `/home/aiwithapex/projects/aios`
>
> AIOS revision inspected: `493c5abc99e7ba1311e23339bd3cf50242f26d72`
>
> Review date: 2026-07-17

## Executive determination

AIOS contains **additional material worth preserving as a supplement** to
[`HERMES_MINIMUM_CODE_PULL_EVALUATION.md`](./HERMES_MINIMUM_CODE_PULL_EVALUATION.md).
It does not improve on the selected Codex transport itself: AIOS implements the
same direct ChatGPT OAuth/Responses approach that the primary evaluation
rejects in favor of the official `openai-codex` SDK/app-server. Its additional
value is instead in the operational layer around an AI workflow:

1. a typed distinction between provider readiness and job execution;
2. deterministic mock/disabled providers for credential-free testing;
3. an accepted/degraded/failed stage-result pattern with one bounded repair;
4. separate private diagnostic artifacts and bounded user-facing progress;
5. reviewed-source declarations and fail-closed source-compliance gates;
6. deterministic evidence-quality scoring, stable ordering, and low-quality
   source caps;
7. truthful exact/estimated/unavailable/no-charge usage states;
8. path-confined evidence assets with stable manifests and symlink checks;
9. deterministic rendered-output privacy and structure QA;
10. versioned snapshots and historical replay/backtest patterns.

These patterns refine the local modules already proposed in the Hermes
evaluation. They do **not** expand the minimum Hermes extraction, change the
Python recommendation, or create an AIOS runtime dependency.

## Evidence reviewed

- [`/home/aiwithapex/projects/aios/docs/ai-runtime-setup.md`](/home/aiwithapex/projects/aios/docs/ai-runtime-setup.md)
- [`/home/aiwithapex/projects/aios/docs/openai-subscription-runtime.md`](/home/aiwithapex/projects/aios/docs/openai-subscription-runtime.md)
- [`/home/aiwithapex/projects/aios/AGENTS.md`](/home/aiwithapex/projects/aios/AGENTS.md)
- the implementation and tests linked throughout this document.

The code, not the overview document alone, was used to verify each finding.

## Stack and extraction boundary

The selected txt2crs backend is Python, while these AIOS modules are
TypeScript/JavaScript. Most value is therefore **reference and reimplementation**
rather than literal file copying. Small isolated algorithms can still be
translated and adapted where the implementation index marks them `Pull/adapt`.

As with Hermes, the finished application must own every selected implementation:

- copied or adapted behavior lives under `txt2crs` modules;
- AIOS imports, filesystem paths, subprocesses, services, configuration, state,
  credentials, build steps, and deployment dependencies are forbidden;
- third-party packages used by an adapted implementation are declared directly
  by txt2crs;
- the application must continue to work after the AIOS repository is absent.

## Delta from the Hermes evaluation

| Area | Already established by Hermes evaluation | Additional AIOS value |
|---|---|---|
| Codex model transport | Official SDK/app-server selected; direct OAuth rejected | No transport change. AIOS reinforces why owning OAuth/SSE is a large separate subsystem |
| Runtime errors | Small local error taxonomy proposed | Explicit readiness, credential, warning, recovery, and result contracts kept separate from execution |
| Testing | Runtime fake and live-gated test proposed | Working deterministic `mock` and `disabled` provider pattern with dependency injection |
| Stage validation | Validate, bounded repair, checkpoint or fail | Explicit accepted/degraded result algebra, one repair, cancellation ownership, safe progress narration |
| Progress and logs | Typed events and redacted logs proposed | Two-view design: private diagnostics versus bounded browser-safe trace/manifest |
| Source selection | Authority, freshness, diversity, conflicts required | Reviewed/restricted/disabled source declarations, source roles, quality tiers, per-source caps, deterministic tie-breakers |
| Evidence | Source ledger and claim citations required | Optional confined evidence-asset manifest and low-quality evidence caps |
| Spend/usage | Tokens, subscription billing source, API cost `null` | Explicit exact/estimated/unavailable/no-charge states and pre-run estimate confidence |
| Output QA | Deterministic renderer and HTML allowlist required | Concrete privacy scan, section markers, manifest drift, and media-embed QA patterns |
| Evaluations | Fixed evaluation set and versioning required | Private snapshots, dry-run planning, windowed replay, bounded published aggregate |

## Full-path implementation reference index

The use labels mean:

- **Pull/adapt:** small or generic logic worth translating into a local
  txt2crs implementation.
- **Inspire a clean implementation:** reproduce the architectural behavior in
  local Python without bringing irrelevant AIOS coupling.
- **Reference tests:** use the tested failure cases to design new txt2crs
  tests and adapt only the cases relevant to local contracts.
- **Exclude:** do not use in the selected architecture.

### Runtime contract, readiness, and deterministic providers

| Requirement | Full-path implementation reference | Relevant region | Recommended use |
|---|---|---|---|
| Provider/readiness contract | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/contract.ts:14`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/contract.ts:14) | Runtime status, credential status, warnings, recovery, usage, typed errors, runtime interface | **Inspire a clean implementation.** Create equivalent local Pydantic enums/models, but narrow providers to subscription Codex and a deterministic fake. |
| Safe readiness construction | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:69`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:69) | `createReadiness` | **Pull/adapt.** Sanitize the readiness object at construction time instead of expecting every UI/API consumer to redact it. |
| Readiness-to-error mapping | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:90`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:90) and [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:154`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:154) | `createUnavailableRuntimeError`, `statusToErrorCode` | **Inspire a clean implementation.** Keep “can the provider run?” separate from a failed course job. |
| Focused path/text redaction | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:121`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:121) and [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:130`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:130) | `redactPath`, `redactSensitiveText` | **Reference only.** Use the threat cases to improve the local structured redactor; do not rely on regex alone for secrets. |
| Deterministic disabled provider | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:208`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:208) | `createDisabledAiRuntime` | **Inspire a clean implementation.** Useful for explicit configuration and recovery UX, but a disabled provider cannot satisfy a requested job. |
| Deterministic fake provider | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:237`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:237) | `createMockAiRuntime` | **Inspire a clean implementation.** The txt2crs fake should return fixture-selected schema-valid course/review/assessment values and scripted events/errors. |
| Provider dependency injection | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:17`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/providers.ts:17) | `AiRuntimeProviderDependencies` | **Inspire a clean implementation.** Inject clock, runtime client, credential/readiness probe, and sleeper so tests never need real auth or time. |

Reference tests:

- [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/providers.test.ts:150`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/providers.test.ts:150)
  verifies disabled and mock selection, sanitized readiness, automatic-refresh
  states, injected transport, typed input errors, and raw-body redaction.
- [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/config.test.ts`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/config.test.ts)
  covers invalid/placeholder configuration and defaults.

### Stage validation, repair, degradation, and cancellation

| Requirement | Full-path implementation reference | Relevant region | Recommended use |
|---|---|---|---|
| Accepted/degraded result algebra | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:30`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:30) | `StageValidationAcceptedResult`, `StageValidationDegradedResult`, `StageValidationOutcome` | **Inspire a clean implementation.** Use a discriminated local stage result rather than `None`, strings, or exceptions as workflow state. |
| One bounded repair | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:267`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:267) | `runStageValidation` | **Pull/adapt.** Preserve one explicit retry followed by a typed terminal outcome while replacing Trend Finder types. |
| Abort ownership | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:83`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:83) | `runWithAbortOwnership` | **Inspire a clean implementation.** Cancellation must settle the stage even when a lower-level operation ignores cancellation. |
| Safe public narration | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:161`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:161) and [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:204`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/stage-validation.ts:204) | Message sanitization and narration building | **Inspire a clean implementation.** Public progress carries stage/status/issue/retry/degradation labels, never raw provider errors or prompts. |

Reference tests:

- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/stage-validation.test.ts:10`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/stage-validation.test.ts:10)
  covers first-pass success, exactly one retry, explicit degradation, pre-abort,
  ignored in-flight aborts, unsafe messages, and retry-count clamping.

For txt2crs, degradation must be stricter than AIOS Trend Finder:

- Required course, review-pack, assessment, and answer-key stages may not
  substitute deterministic placeholder content and still report `completed`.
- An optional enrichment can end as `degraded` if the user sees the limitation.
- Research failure may produce an explicitly labeled
  `research_unavailable` result only if product policy allows an ungrounded
  course; it must never be labeled “deep researched.”
- Any fallback artifact still requires its own schema, safety, and citation
  validation before checkpointing.

### Private diagnostics and browser-safe progress

| Requirement | Full-path implementation reference | Relevant region | Recommended use |
|---|---|---|---|
| Structured per-run JSONL logging | [`/home/aiwithapex/projects/aios/scripts/lib/aggregate-run-logger.ts:125`](/home/aiwithapex/projects/aios/scripts/lib/aggregate-run-logger.ts:125) | `createAggregateRunLogger` | **Inspire a clean implementation.** Use typed records, a run ID, restricted permissions, and centralized recursive sanitization. Avoid copying console monkey-patching. |
| Recursive log sanitization | [`/home/aiwithapex/projects/aios/scripts/lib/aggregate-run-logger.ts:69`](/home/aiwithapex/projects/aios/scripts/lib/aggregate-run-logger.ts:69) | `sanitizeLogValue` | **Reference only.** Preserve the key-aware/circular/error cases in local tests, but prefer allowlisted event schemas over arbitrary recursive objects. |
| Bounded public trace | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/engine-trace.ts:1562`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/engine-trace.ts:1562) | `buildSanitizedEngineTrace` | **Inspire a clean implementation.** Project private events into a small user-safe progress model; do not copy the 1,600+ line trend-specific mapper. |
| Trace recorder | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/engine-trace.ts:1517`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/engine-trace.ts:1517) | `createEngineTraceRecorder` | **Reference only.** The local kernel already has a smaller typed event plan. |
| Private diagnostic artifacts | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/private-diagnostics.ts:473`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/private-diagnostics.ts:473) | `writeTrendPrivateDiagnostics` | **Inspire a clean implementation.** Persist approved diagnostic summaries separately from browser/user data, atomically and under retention limits. |
| Browser-safe diagnostic projection | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/private-diagnostics.ts:451`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/private-diagnostics.ts:451) | `slimTrendFinderBrowserDiagnostics` | **Inspire a clean implementation.** Expose counts/statuses/manifest IDs, not private paths or raw rows. |

Reference tests:

- [`/home/aiwithapex/projects/aios/scripts/lib/__tests__/aggregate-run-logger.test.ts:30`](/home/aiwithapex/projects/aios/scripts/lib/__tests__/aggregate-run-logger.test.ts:30)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/engine-trace.test.ts:180`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/engine-trace.test.ts:180)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/private-diagnostics.test.ts:188`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/private-diagnostics.test.ts:188)

The important pattern is not “log everything privately.” txt2crs should still
avoid storing raw prompts, full user content, credentials, chain-of-thought,
and provider bodies unless a narrowly defined, consented diagnostic mode
requires specific fields. Private storage reduces exposure; it does not make
unnecessary collection safe.

### Research-source governance and evidence selection

| Requirement | Full-path implementation reference | Relevant region | Recommended use |
|---|---|---|---|
| Source roles, quality, and compliance states | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/types.ts:23`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/types.ts:23) | Source-role, quality-tier, and compliance-status enums | **Inspire a clean implementation.** Define education-oriented source classes and domain policy rather than copying trend roles or weights. |
| Fail-closed reviewed-source gate | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-compliance.ts:15`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-compliance.ts:15) and [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-compliance.ts:57`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-compliance.ts:57) | `isReviewedSource`, `applySourceComplianceGate` | **Pull/adapt.** Unreviewed/restricted providers must remain disabled regardless of runtime configuration. |
| Reviewed source declaration schema | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts:64`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts:64) and [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts:1045`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts:1045) | Metadata schema and declaration validation | **Reference only.** Build a smaller local `ResearchSourcePolicy` with allowed origin/provider, authority class, domains, freshness, content/byte/time/cost caps, and review status. |
| Per-source caps and reviewed fields | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts:208`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts:208) | `sourceSetup` | **Inspire a clean implementation.** Only reviewed query/input fields should be model-controlled; all other provider parameters remain fixed. |
| Evidence-quality components | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:35`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:35) and [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:201`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:201) | Component weights and `calculateEvidenceQualityScore` | **Reference only.** The trend-specific source-local/recency formula is not appropriate for education; adopt explainable components and version the rubric. |
| Stable evidence ordering | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:231`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:231) | `compareEvidenceForScoring` | **Pull/adapt.** Use quality, relevance, freshness, source ID, and evidence ID as deterministic tie-breakers. |
| Low-quality evidence caps | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:246`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/source-quality.ts:246) | `selectEvidenceForScoring` | **Inspire a clean implementation.** Cap community/low-authority evidence per claim/topic and require authoritative corroboration for high-risk claims. |

Reference tests:

- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/__tests__/apify-source-config.test.ts:41`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/__tests__/apify-source-config.test.ts:41)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/__tests__/source-quality.test.ts:67`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/__tests__/source-quality.test.ts:67)

The most useful new rule is to make source approval separate from source
availability. A configured credential or reachable endpoint does not make a
source approved. A source policy should be reviewed independently and fail
closed.

### Optional curated source adapters

AIOS includes direct source adapters that may inspire future curated research
paths:

- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/arxiv-adapter.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/arxiv-adapter.ts)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/rss-adapter.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/rss-adapter.ts)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/google-news-adapter.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/google-news-adapter.ts)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/github-adapter.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/github-adapter.ts)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/huggingface-adapter.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/huggingface-adapter.ts)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/hn-adapter.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/hn-adapter.ts)

They are **not part of the minimum txt2crs implementation**. Tavily search and
safe extraction remain the smallest general research path. Add a curated
adapter only when an evaluation proves that it materially improves a named
course domain, and then use the maintained upstream API/library directly
rather than importing AIOS.

### Usage and spend truthfulness

| Requirement | Full-path implementation reference | Relevant region | Recommended use |
|---|---|---|---|
| Exact/estimated/unavailable spend states | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:1`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:1) | Spend/provider/cadence/pre-run state enums | **Inspire a clean implementation.** Model confidence/state explicitly instead of coercing missing data to zero. |
| Source-level usage summary | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:166`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:166) | `buildSourceSpendSummary` | **Reference only.** Create local model/research-stage usage records; do not reuse trend-specific USD rules. |
| Pre-run estimate | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:303`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:303) | `buildPreRunSpendEstimate` | **Inspire a clean implementation.** Preflight subscription quota, expected turns/tools/sources, and separately priced research calls before a long job. |
| Aggregate accounting | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:355`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/spend-accounting.ts:355) | `aggregateSpendSummaries` | **Reference only.** Preserve mixed states rather than claiming aggregate precision when one stage is unknown. |

Reference tests:

- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/spend-accounting.test.ts:12`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/spend-accounting.test.ts:12)

For subscription Codex turns, use:

```text
billing_source = "chatgpt_subscription"
token_usage_state = "reported" | "unavailable"
subscription_quota_state = "available" | "limited" | "exhausted" | "unknown"
estimated_api_cost = null
```

For paid research tools, track exact billed cost, configured cap, or
unavailable status independently. “Subscription-included” and “no dollar value
reported” are not the same as “free.”

### Evidence assets, deterministic rendering, and output QA

| Requirement | Full-path implementation reference | Relevant region | Recommended use |
|---|---|---|---|
| Stable evidence-asset IDs | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:153`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:153) | `deriveEvidenceAssetId` | **Inspire a clean implementation.** Use content/source hashes and safe IDs for locally retained diagrams/images/page captures. |
| Confined asset paths | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:174`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:174) | `resolveEvidenceAssetPath` | **Pull/adapt** with `pathlib`; reject traversal and paths outside the per-job root. |
| File identity, bounded reads, symlink defense | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:213`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:213) through [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:298`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:298) | Confined inspection/read/write helpers | **Inspire a clean implementation.** Verify file identity before/after bounded reads and never publish a symlink escape. |
| Evidence manifest verify/copy | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:606`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/evidence-assets.ts:606) | `verifyEvidenceAssetFile`, `copyVerifiedEvidenceAssetFile` | **Reference only.** Relevant only if txt2crs retains non-text evidence assets. |
| HTML escaping and inline JSON | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-renderer.ts:24`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-renderer.ts:24) | `escapeHtml`, `escapeAttribute`, `serializeInlineJson` | **Inspire a clean implementation.** Prefer the chosen Python templating engine's autoescaping; test every non-text context separately. |
| Rendered privacy/structure QA | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-qa.ts:286`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-qa.ts:286) and [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-qa.ts:794`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-qa.ts:794) | Privacy issue collection and final QA result | **Inspire a clean implementation.** Check required sections, private-field leaks, unsafe external/media embeds, manifest drift, and bounded issue reporting after rendering. |

Reference tests:

- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/evidence-assets.test.ts:67`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/evidence-assets.test.ts:67)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/static-brief-qa.test.ts:93`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/static-brief-qa.test.ts:93)
- [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/static-brief-renderer.test.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/__tests__/static-brief-renderer.test.ts)

### Versioned snapshots and replayable evaluations

| Requirement | Full-path implementation reference | Relevant region | Recommended use |
|---|---|---|---|
| Versioned private snapshots | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:80`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:80) | Strict snapshot schema | **Inspire a clean implementation.** Store versioned evaluation inputs, outputs, evidence hashes, prompts, schemas, model/runtime versions, and scores. |
| Atomic/path-confined snapshot writes | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:417`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:417) and [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:771`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:771) | Snapshot write and atomic helper | **Reference only.** Implement with local job/evaluation storage and path confinement. |
| Deterministic comparisons | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:576`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts:576) | `compareTrendSnapshots` | **Reference only.** Compare txt2crs rubric dimensions and artifact invariants, not trend movement. |
| Dry-run backtest plan | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts:406`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts:406) | `createBacktestPlan` | **Inspire a clean implementation.** A course-eval runner should show cases/models/budgets before spending subscription allowance or research credits. |
| Private replay and bounded publish | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts:457`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts:457) and [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts:733`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts:733) | Backtest run and bounded aggregate publishing | **Inspire a clean implementation.** Keep case-level content/evidence private; publish only aggregate metrics after explicit action. |

Reference tests:

- [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/snapshots.test.ts:157`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/snapshots.test.ts:157)
- [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/backtests.test.ts:106`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/backtests.test.ts:106)

For txt2crs, replay cases should cover the evaluation set already required by
`AI_USAGE_NEEDS.md`: short prompts, long transcripts, malformed/empty inputs,
conflicting evidence, prompt injection, inaccessible sources, multilingual/RTL
content, specialist/high-risk topics, quota exhaustion, cancellation, invalid
schemas, and citation failures.

## Direct OAuth/Responses code: inspect but do not select

AIOS contains a complete direct subscription transport:

- [`/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/oauth.mjs:18`](/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/oauth.mjs:18)
  — PKCE browser login, token exchange, refresh, loopback callback.
- [`/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/storage.mjs:86`](/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/storage.mjs:86)
  — storage lock, load/save/status, refresh, atomic record writing.
- [`/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/codex-transport.mjs:63`](/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/codex-transport.mjs:63)
  — Responses request body and headers.
- [`/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/codex-transport.mjs:133`](/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/codex-transport.mjs:133)
  — streamed response event collection.
- [`/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/codex-transport.mjs:430`](/home/aiwithapex/projects/aios/scripts/lib/openai-account-auth/codex-transport.mjs:430)
  — retry behavior.
- [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/openai-codex-provider.ts:46`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/openai-codex-provider.ts:46)
  — provider readiness, refresh, result normalization, and error mapping.

This does not alter the primary decision. Do not pull these files because:

1. the official SDK/app server owns sign-in, credential storage, refresh,
   account state, model discovery, transport framing, and streaming;
2. AIOS calls the ChatGPT Codex backend directly and must maintain OAuth,
   bearer headers, SSE parsing, event reconstruction, retries, and error
   mappings;
3. its documentation limits the transport to local script use and explicitly
   defers hosted production;
4. the selected Python architecture cannot use these JavaScript modules
   directly.

The source and its regression scripts are still useful evidence of the
complexity being avoided:

- [`/home/aiwithapex/projects/aios/scripts/test-openai-account-auth.mjs`](/home/aiwithapex/projects/aios/scripts/test-openai-account-auth.mjs)
- [`/home/aiwithapex/projects/aios/scripts/test-openai-codex-transport.mjs`](/home/aiwithapex/projects/aios/scripts/test-openai-codex-transport.mjs)
- [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/providers.test.ts:241`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/__tests__/providers.test.ts:241)

## Other AIOS components not worth pulling

| Component | Full path | Decision |
|---|---|---|
| Trend scoring and forecasting | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/scoring.ts`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/scoring.ts) and neighboring trend modules | Exclude. Relevance/novelty/creator-potential formulas do not measure pedagogy, factuality, or assessment validity. |
| Full engine trace mapper | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/engine-trace.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/engine-trace.ts) | Reference the private/public boundary only; do not copy the trend-specific schema and 1,600+ line projection. |
| Full source declaration catalog | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/sources/apify-source-config.ts) | Reference validation ideas only. The actors, keywords, roles, and compliance decisions are for AI trend collection, not arbitrary educational research. |
| Apify client stack | [`/home/aiwithapex/projects/aios/scripts/lib/apify/`](/home/aiwithapex/projects/aios/scripts/lib/apify/) | Exclude from the minimum. Tavily already supplies the smaller general search/extract path. |
| Full static brief renderer | [`/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-renderer.ts`](/home/aiwithapex/projects/aios/scripts/extensions/trend-finder/static-brief-renderer.ts) | Reference escaping/QA ideas only. Build accessible course/review/assessment templates for txt2crs. |
| Trend snapshots/backtest implementation | [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/snapshots.ts) and [`/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts`](/home/aiwithapex/projects/aios/scripts/lib/ai-runtime/backtests.ts) | Reference architecture only. Domain types and most algorithms are trend-specific. |
| Dashboard and local control-plane code | [`/home/aiwithapex/projects/aios/src/`](/home/aiwithapex/projects/aios/src/) | Exclude. It does not fulfill the txt2crs generation/research backend needs. |

## Recommended local refinements

These recommendations fit inside the destination modules already proposed by
the Hermes evaluation; they are not a second runtime architecture.

### `src/txt2crs/ai/runtime_status.py`

Add:

- `RuntimeReadinessStatus`
- `CredentialStatus`
- `RuntimeWarning`
- `RuntimeRecovery`
- `RuntimeReadiness`
- `RuntimeErrorCode`

Keep readiness separate from `JobStatus`. A ready runtime may still fail a job,
and valid stored authentication does not prove that a requested model is
entitled or has remaining quota.

### `src/txt2crs/ai/fake_runtime.py`

Provide a deterministic test runtime with scripted:

- models and account types;
- schema-valid stage artifacts;
- streamed event sequences and stable call IDs;
- tool requests;
- token usage;
- transient/permanent/auth/quota errors;
- hangs and cancellation races.

It must not become a production fallback that fabricates a “researched” course.

### `src/txt2crs/jobs/stage_result.py`

Use a discriminated result:

```text
accepted  -> valid artifact, checkpoint permitted
degraded  -> valid limited artifact, explicit limitation, policy decides continuation
failed    -> no usable artifact, checkpoint forbidden
cancelled -> terminal cancellation, checkpoint only prior accepted state
```

Record issue code, repair count, safe public message, private diagnostic
reference, and degradation path. Required deliverables cannot be silently
downgraded.

### `src/txt2crs/observability/`

Maintain two explicitly different contracts:

- `PrivateRunEvent`: tightly access-controlled operational diagnostics with
  retention/deletion rules;
- `PublicProgressEvent`: bounded status, counts, timings, usage state, and
  recovery guidance suitable for the job owner.

Projection from private to public is an allowlist transformation. Never return
the private object and try to remove a few fields at the edge.

### `src/txt2crs/research/source_policy.py`

Add a static reviewed-source/provider policy with:

- policy version and reviewer/date;
- enabled/restricted/disabled status;
- allowed origin or provider;
- source class and authority tier;
- safe model-controlled query fields;
- per-request and per-job item/byte/time/cost caps;
- freshness policy;
- authentication/privacy/retention notes;
- allowed course domains and high-risk restrictions.

Configuration cannot promote an unknown source to reviewed status.

### `src/txt2crs/research/quality.py`

Make evidence ranking explainable and versioned. Candidate components include:

- authority/source tier;
- directness/primary-source status;
- relevance to the research question;
- freshness relative to the claim;
- corroboration and source diversity;
- extraction completeness;
- stable canonical URL and publication metadata;
- conflict/uncertainty penalties.

Do not copy AIOS trend weights. Determine education weights through evaluation,
and retain the component breakdown with each selection decision.

### `src/txt2crs/ai/usage.py`

Represent:

- reported versus unavailable tokens;
- ChatGPT subscription versus API versus research-provider billing source;
- subscription quota available/limited/exhausted/unknown;
- exact/estimated/capped/unavailable paid research cost;
- mixed aggregate confidence.

### `src/txt2crs/evals/`

Add:

- versioned private evaluation cases;
- dry-run plan output before live provider use;
- immutable evidence/input hashes;
- prompt/schema/model/runtime/template versions;
- deterministic artifact-invariant results;
- rubric results and human-review fields;
- private per-case output;
- explicitly published aggregate summaries only.

## Test-first supplemental sequence

These tests refine the phases already listed in the Hermes evaluation.

1. Write readiness tests proving provider readiness, authentication state,
   model entitlement, and job completion are distinct facts.
2. Write fake-runtime fixtures for every streamed event, tool call, usage,
   retry, quota, cancellation, and invalid-schema path.
3. Write stage-result tests proving one repair maximum, abort settlement,
   accepted-only checkpointing, and required-stage degradation rejection.
4. Write public-progress projection tests with malicious keys/values, private
   paths, prompts, credentials, provider bodies, request IDs, and oversized
   arrays.
5. Write source-policy tests proving an environment/config value cannot
   promote an unknown or restricted provider to reviewed status.
6. Write evidence-ranking tests for explainable components, stable
   tie-breakers, authoritative-source preference, diversity, community caps,
   missing metadata, and conflicting evidence.
7. Write mixed usage-accounting tests proving `null`/unknown values never
   become zero or exact totals.
8. If evidence files are retained, write traversal, symlink, changed-file,
   oversized-file, content-type, cancellation, and pruning tests.
9. Write rendered-output tests for missing sections, citation/manifest drift,
   private data, scripts, handlers, iframes, remote media, unsafe links, and
   inaccessible document structure.
10. Write evaluation-replay tests for dry-run/no-network behavior, case
    versioning, path confinement, private output, and bounded aggregate
    publication.

## Supplemental acceptance criteria

The adopted refinements are complete when:

- runtime readiness can be displayed without implying a course job succeeded;
- credential-valid and model-entitled/quota-available states are separate;
- deterministic fake-runtime tests need no credentials or network;
- every stage terminates as accepted, degraded, failed, or cancelled;
- only accepted required artifacts can advance/checkpoint;
- a lower-level operation that ignores cancellation cannot leave the stage
  pending forever;
- public progress contains no prompt, raw input, evidence excerpts, private
  path, token, account ID, provider body, chain-of-thought, or private request
  identifier;
- only reviewed research providers/origins and reviewed model-controlled fields
  can execute;
- evidence selection records a versioned component breakdown and stable
  ordering;
- low-authority evidence cannot dominate a topic or high-risk claim;
- unknown subscription token/quota/cost fields remain explicitly unknown;
- retained evidence assets cannot traverse or symlink outside their job root;
- rendered artifacts pass deterministic structure, citation, privacy,
  accessibility, and active-content QA;
- evaluation dry-runs perform no live calls and per-case artifacts remain
  private unless explicitly published;
- no AIOS import, path, subprocess, service, state, credential, build, or
  runtime dependency exists in txt2crs.

## Final recommendation

Use AIOS as a **supplemental operational reference**, not as a second donor
runtime:

- adopt clean local versions of its readiness/result-state separation,
  deterministic fake provider, stage outcome algebra, private/public trace
  split, source policy, evidence selection explanations, truthful usage states,
  output QA, and replayable evaluation patterns;
- continue using the official `openai-codex` SDK/app-server path selected in
  the Hermes evaluation;
- do not copy AIOS direct OAuth/Responses code;
- do not add Apify or domain-specific trend machinery to the minimum.

This is genuine additional value, but it primarily improves reliability,
governance, privacy, and evaluation. It does not reduce the core Hermes
extraction or replace the education-specific implementation still required in
txt2crs.
