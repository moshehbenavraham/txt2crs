# Course Generation Logging Quality Plan

> **Status:** Proposed
> **Priority:** P1 - High
> **Last reviewed:** 2026-07-21
> **Estimated delivery:** Five focused sessions, approximately 12-18 hours
> **Primary owners:** Engine, backend shell, and operations

## Objective

Make one course-generation run diagnosable from structured logs and optional
OpenTelemetry traces without exposing learner content, prompts, evidence,
provider payloads, token data, credentials, artifact bytes, or filesystem
paths.

The finished system must let an operator answer these questions quickly:

1. Which job and execution attempt failed?
2. Which accepted or in-progress stage was involved?
3. Did the failure occur in ingestion, research, a model turn, local
   validation, checkpoint persistence, rendering, or delivery?
4. Was the operation retried or repaired, and how many bounded attempts ran?
5. What was the last durable checkpoint before the failure?
6. How long did the job, stage, and relevant external operation take?
7. Is the same safe failure fingerprint recurring across jobs?
8. Can the job resume safely, or is it terminal?

## Current-State Assessment

Course-generation logging currently provides useful application lifecycle and
HTTP information, but it is too sparse for root-cause debugging.

| Area | Current behavior | Debugging gap |
|------|------------------|---------------|
| Submission | Logs start, completion, input type, user ID, job ID, and revision | The request trace ends before background execution begins |
| Worker | Logs execution start, completion, and generic failure | No job ID, run ID, stage, duration, checkpoint, or safe failure category |
| Pipeline | Persists detailed accepted checkpoints | Checkpoint and stage transitions are not emitted to operator logs |
| Codex runtime | Defines safe turn, tool, and usage event types | The real factory does not connect the optional event sink |
| Research | Third-party HTTP and MCP loggers emit infrastructure chatter | No first-party search/extract operation summary or failure classification |
| Failure handling | Terminal failure becomes `execution_failed` or `generation_failed` | Raw exceptions are safely omitted, but no safe replacement detail exists |
| Local diagnostics | `write_last_error()` can write an explicit private file | It is not connected to generation and currently retains unsafe messages and absolute traceback paths |
| Tracing | FastAPI, SQLAlchemy, and HTTPX can be auto-instrumented | The background job, stages, retries, repairs, and checkpoints have no custom spans |
| User progress | Exposes coarse safe stages and monotonic accepted work units | Correctly unsuitable as an operator diagnostic stream |

The target is not "more text." The target is a bounded, typed, correlated
operational record with low noise and strong privacy guarantees.

## Requirements and Constraints

### Required Outcomes

- Every background execution has a new `run_id` and background `trace_id`.
- `job_id` links submission, execution attempts, checkpoints, and terminal
  state across process restarts.
- Every major engine stage emits bounded start and terminal events.
- Every durable checkpoint emits a completion event only after persistence
  succeeds.
- Retry and repair events identify the safe reason code, attempt number, and
  configured maximum.
- Failures include the stage, operation, stable failure code, retryability,
  last checkpoint sequence, duration, and safe error fingerprint.
- Successful terminal events include duration, accepted stage count, retry
  count, repair count, research call count, and artifact count.
- INFO output is useful without DEBUG output.
- DEBUG output adds safe model-turn and research-operation boundaries, never
  content or provider response data.
- Logging, tracing, or diagnostic-handler failure never changes job state or
  prevents recovery.
- Existing public job-status and artifact APIs remain unchanged.

### Non-Negotiable Privacy Rules

Routine logs and trace attributes must never contain:

- email addresses, learner input, normalized source text, or upload bytes;
- trusted instructions, prompts, model output, or assistant reasoning;
- evidence excerpts, source bodies, research queries, or provider payloads;
- token counts or other per-job token data;
- credentials, authorization headers, cookies, device codes, or secrets;
- provider request, thread, turn, or account identifiers;
- artifact bodies, private filenames, hashes, or filesystem paths;
- raw exception messages or arbitrary exception `repr()` output; or
- arbitrary dictionaries serialized with `default=str`.

The engine already retains private durable state needed for recovery. Logging
must not duplicate that state.

### Reliability and Compatibility

- Observer callbacks are best-effort and exception-isolated.
- Event order is monotonic within one `run_id`.
- A restarted job keeps the same `job_id` and receives a new `run_id`.
- A completed, failed, or cancelled attempt emits exactly one terminal
  execution event.
- No application PostgreSQL schema or Alembic migration is expected.
- No engine SQLite schema change is expected; correlation uses existing
  `job_id`, revision, checkpoint sequence, and an ephemeral attempt `run_id`.
- No generated OpenAPI client change is expected.

## Target Architecture

```text
HTTP submission
  -> durable job commit
  -> job.submission_completed(job_id, request trace_id)

Serial worker claims job
  -> creates background trace_id and run_id
  -> binds job logging context for this thread
  -> invokes package executor with a SafeGenerationObserver

Engine executor, pipeline, runtime, and research services
  -> emit typed allowlisted SafeGenerationEvent objects
  -> never import shell logging or OpenTelemetry

Shell observer adapter
  -> validates event schema and field allowlist
  -> adds bound correlation fields
  -> emits structured application log
  -> annotates optional OpenTelemetry spans
  -> isolates observer failures from generation

Operator output
  -> concise INFO lifecycle and stage records
  -> optional safe DEBUG sub-operation records
  -> optional Jaeger stage timing and failure visualization
```

The package boundary remains authoritative for generation semantics. The shell
formats and exports safe events; it does not infer stages from private engine
objects or reimplement pipeline behavior.

## Structured Event Contract

Add a frozen, strict, versioned package event model rather than passing
arbitrary logging dictionaries.

### Common Fields

These fields apply to package-owned `SafeGenerationEvent` records. Existing
shell-owned submission events occur before a job or run exists and therefore
keep their narrower reviewed field sets.

| Field | Requirement |
|-------|-------------|
| `schema_version` | Fixed event schema version, initially `1.0` |
| `event_id` | Stable bounded event identifier generated by the package |
| `event_name` | Allowlisted `{domain}.{action}_{state}` name |
| `occurred_at` | UTC timestamp |
| `level` | Allowlisted `debug`, `info`, `warning`, or `error` |
| `job_id` | Existing opaque durable job identifier |
| `run_id` | New random identifier for one worker execution attempt |
| `job_revision` | Durable job revision observed at the event boundary |
| `stage` | Allowlisted pipeline stage or `none` |
| `stage_sequence` | Accepted stage sequence when known |
| `duration_ms` | Monotonic elapsed duration, rounded and bounded |
| `failure_code` | Stable allowlisted code, never exception text |
| `failure_category` | Coarse bounded subsystem category |
| `error_fingerprint` | Hash of safe structural data, excluding the message |
| `attempt` | Current bounded transport or operation attempt |
| `maximum_attempts` | Configured finite maximum |
| `retry_count` | Bounded retry count for the current run |
| `repair_count` | Bounded validation-repair count for the current run |
| `checkpoint_sequence` | Last successfully persisted checkpoint sequence |
| `operation_count` | Safe count appropriate to the named operation |

Fields that do not apply must be absent or `null`. Event-specific Pydantic
validation must reject contradictory combinations, unknown fields, negative
durations, unbounded strings, and unrecognized event names.

### Context Rules

- `job_id` is the durable correlation key across submission and restarts.
- `run_id` separates retries caused by worker or process replacement.
- `trace_id` remains formatter-owned. A worker attempt starts a new background
  trace instead of pretending to continue an ended HTTP request span.
- `user_id` is omitted from generator lifecycle events because `job_id` is
  sufficient for operational correlation.
- `stage` values come from a package enum, not free-form provider text.
- Module work uses a safe ordinal and total count. Do not log a generated
  module title or content-derived identifier.

## Event Catalog

### INFO Events

| Event | Required safe detail |
|-------|----------------------|
| `job.submission_started` | Request trace, input type |
| `job.submission_completed` | Job ID, input type, initial revision |
| `txt2crs.execution_started` | Job ID, run ID, starting revision, resume flag, last checkpoint sequence |
| `txt2crs.stage_started` | Stage, stage sequence, module ordinal when applicable |
| `txt2crs.stage_completed` | Stage, duration, retry count, repair count |
| `txt2crs.checkpoint_completed` | Stage, checkpoint sequence, new revision, persistence duration |
| `txt2crs.stage_retrying` | Stage, safe failure code, next attempt, maximum attempts, bounded delay |
| `txt2crs.stage_repairing` | Stage, safe local validation code, repair number, maximum repairs |
| `txt2crs.execution_completed` | Total duration, accepted stage count, retries, repairs, research calls, artifact count |
| `txt2crs.execution_cancelled` | Duration, cancellation reason code, last checkpoint sequence |
| `txt2crs.execution_failed` | Duration, stage, operation, failure category/code, retryability, fingerprint, last checkpoint sequence |

### DEBUG Events

| Event | Required safe detail |
|-------|----------------------|
| `txt2crs.model_turn_started` | Stage, attempt, model policy identifier, prompt version |
| `txt2crs.model_turn_completed` | Stage, attempt, duration, schema accepted boolean |
| `txt2crs.research_call_started` | Search or extract kind, safe ordinal, attempt |
| `txt2crs.research_call_completed` | Kind, duration, fetched count, accepted count |
| `txt2crs.render_started` | Format count |
| `txt2crs.render_completed` | Format count, artifact count, duration |

Do not emit heartbeat events on every pulse. The durable
`runtime_activity_at` value already proves liveness, and repeated heartbeat
logs would bury useful stage transitions.

### ERROR Events

ERROR events reuse the catalog above with a stable `failure_code`. Do not use
`logger.exception()` or `exc_info=True` on course-generation paths until the
global formatter has been changed to prevent raw exception messages and paths.

## Failure Taxonomy

Create one package-owned failure taxonomy that shell logs and public failure
translation can consume without exposing provider text.

| Category | Example codes |
|----------|---------------|
| Input | `input_preparation_failed`, `input_policy_rejected` |
| Authentication | `provider_authentication_failed`, `provider_entitlement_missing` |
| Provider transport | `provider_unavailable`, `provider_timeout`, `provider_rate_limited` |
| Research | `research_search_failed`, `research_extract_failed`, `research_requirements_failed` |
| Model output | `model_output_invalid`, `model_schema_repair_failed` |
| Local validation | `course_validation_failed`, `citation_validation_failed`, `assessment_validation_failed` |
| Budget | `turn_budget_exhausted`, `research_budget_exhausted`, `elapsed_budget_exhausted` |
| Persistence | `checkpoint_persist_failed`, `job_transition_failed` |
| Rendering | `artifact_render_failed`, `artifact_validation_failed` |
| Delivery | `artifact_publish_failed`, `manifest_publish_failed` |
| Lifecycle | `application_shutdown`, `worker_cleanup_failed` |
| Internal | `unexpected_internal_error` |

The classifier must select a code from exception type and the operation that
caught it. It must never hash or inspect the raw exception message for logging.
The safe error fingerprint should hash only:

- failure code;
- exception class name;
- package module and function names with no absolute paths; and
- the current engine, prompt, and policy versions.

## Log-Level and Noise Policy

### INFO

INFO is the default and must show the complete job, stage, checkpoint, retry,
repair, and terminal timeline. A normal four-module successful job should emit
no more than 80 first-party course-generation INFO records.

### DEBUG

DEBUG adds bounded model-turn, research-call, and render-operation timing. It
uses the same field allowlist and is safe to retain. DEBUG must not enable SDK
payload logging or HTTP body logging.

### WARNING and ERROR

WARNING represents degraded but continuing behavior. ERROR represents a
failed stage, execution, cleanup, or observer export. Duplicate logs for the
same failure boundary are forbidden unless one is the stage failure and one is
the single execution terminal summary.

### Third-Party Noise

At the normal INFO setting, configure `httpx`, MCP SDK, Codex SDK, Uvicorn, and
SQLAlchemy loggers to WARNING unless a reviewed integration requires otherwise.
First-party events and optional OpenTelemetry spans replace uncorrelated
"request succeeded" chatter. A local DEBUG setting may re-enable third-party
diagnostics explicitly, but never bodies or headers.

## Safe Diagnostic Capture

The existing `write_last_error()` helper must not be connected to generation
in its current form because it stores raw exception messages and absolute
traceback paths.

Before any automatic local diagnostic capture is enabled:

1. Replace raw exception messages with stable failure codes.
2. Store normalized package module, function, and line frames without absolute
   paths.
3. Apply the same typed context allowlist used by routine events.
4. Use exclusive owner-only `0700` directories and `0600` files.
5. Add bounded retention by count and age.
6. Restrict automatic capture to `ENVIRONMENT=local` behind an explicit
   `TXT2CRS_SAFE_DIAGNOSTICS_ENABLED` setting that defaults to false.
7. Emit only a random diagnostic reference in routine logs.
8. Prove through malicious sentinel tests that input, prompts, evidence,
   tokens, secrets, provider payloads, and paths cannot enter the file.

This diagnostic file is optional. High-quality routine logs must remain useful
when it is disabled.

## OpenTelemetry Plan

Extend the existing opt-in tracing instead of adding another observability
vendor.

Create these custom spans when OpenTelemetry is enabled:

- `txt2crs.job.execute` for one `run_id`;
- `txt2crs.stage.<stage>` for each pipeline stage;
- `txt2crs.model_turn` for one bounded model attempt;
- `txt2crs.research_call` for search or extract;
- `txt2crs.checkpoint.persist` for durable acceptance;
- `txt2crs.artifact.render`; and
- `txt2crs.artifact.publish`.

Allowed span attributes mirror the safe log schema. Exclude user ID, token
data, source URLs, content-derived titles, provider IDs, exception messages,
and stack traces. Set span status and `failure.code` on errors. Logs must still
work exactly when tracing is disabled or export fails.

## Implementation Sessions

Each session has one objective, starts with tests, and should fit a 2-4 hour
implementation window.

### Session 1 - Safe Event and Correlation Contract

**Objective:** Establish the package-to-shell observability boundary and prove
that it cannot leak private data.

- [ ] T001 Write package contract tests for valid lifecycle, stage, checkpoint, retry, repair, and terminal events (`backend/packages/txt2crs/tests/unit/test_observability_events.py`).
- [ ] T002 Write malicious sentinel tests covering prompts, inputs, evidence, credentials, provider payloads, token fields, absolute paths, and arbitrary nested dictionaries (`backend/packages/txt2crs/tests/unit/test_observability_events.py`).
- [ ] T003 Write shell adapter tests for allowed fields, event levels, naming, and best-effort handler failure (`backend/tests/services/test_txt2crs_observability.py`).
- [ ] T004 Write logging-context tests proving `job_id`, `run_id`, and background `trace_id` are present during one execution and cleared between jobs (`backend/tests/core/test_logging.py`).
- [ ] T005 Write formatter tests proving `exc_info`, arbitrary extras, and `default=str` cannot leak raw exception messages or private objects (`backend/tests/core/test_logging.py`).
- [ ] T006 Define strict event-name, stage, subsystem, and failure-code enums (`backend/packages/txt2crs/src/txt2crs/observability/events.py`).
- [ ] T007 Define the frozen `SafeGenerationEvent` union with event-specific validation (`backend/packages/txt2crs/src/txt2crs/observability/events.py`).
- [ ] T008 Define a narrow `SafeGenerationObserver` protocol and no-op implementation (`backend/packages/txt2crs/src/txt2crs/observability/observer.py`).
- [ ] T009 Add a best-effort composite observer so logging and tracing observers cannot affect generation (`backend/packages/txt2crs/src/txt2crs/observability/observer.py`).
- [ ] T010 Add shell context binding for job ID, run ID, and background trace ID (`backend/app/core/logging.py`).
- [ ] T011 Add a shell observer adapter that maps only typed event fields to the application logger (`backend/app/services/txt2crs_observability.py`).
- [ ] T012 Harden structured and text formatters against arbitrary course-generation extras and unsafe exception rendering (`backend/app/core/logging.py`).
- [ ] T013 Export the new public package contracts without exposing private store or checkpoint implementations (`backend/packages/txt2crs/src/txt2crs/observability/__init__.py`).
- [ ] T014 Run focused package and shell observability tests and record the baseline event schema (`backend/packages/txt2crs/`, `backend/`).

### Session 2 - Job, Stage, and Checkpoint Timeline

**Objective:** Produce a complete correlated INFO timeline for success,
failure, cancellation, and resume.

- [ ] T015 Write executor tests for exactly one started and one terminal event on success, failure, cancellation, and application shutdown (`backend/packages/txt2crs/tests/integration/test_generation_job_executor.py`).
- [ ] T016 Write pipeline tests for stage start/completion order, module ordinals, durations, and no duplicate events after resume (`backend/packages/txt2crs/tests/integration/test_generation_pipeline.py`).
- [ ] T017 Write checkpoint tests proving completion is logged only after the durable checkpoint commit succeeds (`backend/packages/txt2crs/tests/integration/test_sqlite_job_store.py`).
- [ ] T018 Write worker tests for new run IDs after replacement, stable job correlation, context cleanup, and observer failure isolation (`backend/tests/services/test_txt2crs_worker.py`).
- [ ] T019 Add a monotonic timing helper that returns bounded millisecond durations (`backend/packages/txt2crs/src/txt2crs/observability/timing.py`).
- [ ] T020 Bind one observer and run ID when the shell worker creates an executor (`backend/app/services/txt2crs_worker.py`, `backend/app/services/txt2crs_application.py`).
- [ ] T021 Emit execution start and terminal events from the engine executor where job semantics are authoritative (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`).
- [ ] T022 Emit stage start and completion events from the generation pipeline (`backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`).
- [ ] T023 Emit safe module ordinal and total count instead of content-derived module identity (`backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`).
- [ ] T024 Emit checkpoint completion after `checkpoint_stage()` returns successfully (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`).
- [ ] T025 Include revision, checkpoint sequence, resume flag, and last accepted stage enum in safe events (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`).
- [ ] T026 Classify cancellation separately from execution failure and retain restart-safe application-shutdown behavior (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`).
- [ ] T027 Replace duplicate worker failure logging with one worker health event plus one authoritative execution terminal event (`backend/app/services/txt2crs_worker.py`).
- [ ] T028 Verify a deterministic successful job and one injected stage failure produce complete, ordered, bounded INFO timelines (`backend/packages/txt2crs/tests/`, `backend/tests/`).

### Session 3 - Retry, Repair, Runtime, and Research Detail

**Objective:** Add safe DEBUG sub-operation detail and actionable INFO retry
and repair events.

- [ ] T029 Write retry-controller tests for attempt number, maximum attempts, safe code, bounded delay, and terminal exhaustion (`backend/packages/txt2crs/tests/unit/test_retry_errors_and_events.py`).
- [ ] T030 Write pipeline repair tests for schema rejection, local validation code, repair start, repair success, and repair failure (`backend/packages/txt2crs/tests/integration/test_generation_pipeline.py`).
- [ ] T031 Write real-factory contract tests proving the official Codex adapter receives the safe observer sink (`backend/packages/txt2crs/tests/contract/test_application_factories.py`).
- [ ] T032 Write runtime projection tests proving provider IDs, assistant text, final schema output, and token counts never reach logs (`backend/packages/txt2crs/tests/contract/test_official_codex_adapter.py`).
- [ ] T033 Write research tests for search/extract ordinals, durations, result counts, retries, and safe failures (`backend/packages/txt2crs/tests/integration/test_research_coordinator.py`).
- [ ] T034 Add observer hooks to `RetryController` without coupling it to logging (`backend/packages/txt2crs/src/txt2crs/ai/retry.py`).
- [ ] T035 Emit INFO retry events with classified safe failure codes and bounded retry delay (`backend/packages/txt2crs/src/txt2crs/ai/retry.py`).
- [ ] T036 Emit INFO repair events from the pipeline around the one allowed validation repair (`backend/packages/txt2crs/src/txt2crs/generation/pipeline.py`).
- [ ] T037 Connect the existing official Codex event sink in the real application factory (`backend/packages/txt2crs/src/txt2crs/application/factories.py`).
- [ ] T038 Project runtime turn and research-tool events into the strict safe event model (`backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py`).
- [ ] T039 Discard runtime `input_tokens` and `output_tokens` at the logging projection boundary while preserving private usage accounting (`backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py`).
- [ ] T040 Emit first-party research search/extract boundaries from the coordinator and tool service (`backend/packages/txt2crs/src/txt2crs/research/coordinator.py`, `backend/packages/txt2crs/src/txt2crs/research/service.py`).
- [ ] T041 Add render-operation timing and safe artifact-count summaries (`backend/packages/txt2crs/src/txt2crs/rendering/artifacts.py`, `backend/packages/txt2crs/src/txt2crs/jobs/executor.py`).
- [ ] T042 Configure noisy third-party loggers to WARNING at normal INFO operation (`backend/app/core/logging.py`).
- [ ] T043 Verify standard INFO and DEBUG event-volume budgets with a representative four-module deterministic course (`backend/packages/txt2crs/tests/integration/test_generation_pipeline.py`).

### Session 4 - Failure Diagnostics, Configuration, and Tracing

**Objective:** Make failures actionable and provide optional span-level timing
without weakening privacy.

- [ ] T044 Write exhaustive failure-classification tests for input, authentication, transport, research, model, validation, budget, persistence, rendering, delivery, lifecycle, and internal errors (`backend/packages/txt2crs/tests/unit/test_failure_classification.py`).
- [ ] T045 Write safe-fingerprint tests proving raw messages and paths do not influence or appear in the fingerprint (`backend/packages/txt2crs/tests/unit/test_failure_classification.py`).
- [ ] T046 Write tracing tests for disabled mode, enabled mode, export failure, span nesting, safe attributes, and error status (`backend/tests/core/test_telemetry.py`).
- [ ] T047 Write settings tests for log level, format selection, and local-only safe diagnostic capture (`backend/tests/core/test_config.py`).
- [ ] T048 Write diagnostic-file sentinel and retention tests before changing the helper (`backend/tests/core/test_logging.py`).
- [ ] T049 Implement package-owned failure classification with stable codes and retryability (`backend/packages/txt2crs/src/txt2crs/observability/failures.py`).
- [ ] T050 Implement the structural safe error fingerprint (`backend/packages/txt2crs/src/txt2crs/observability/failures.py`).
- [ ] T051 Attach failure category, code, retryability, fingerprint, stage, operation, and last checkpoint to terminal events (`backend/packages/txt2crs/src/txt2crs/jobs/executor.py`).
- [ ] T052 Add validated `LOG_LEVEL` and `LOG_FORMAT` settings with current behavior as defaults (`backend/app/core/config.py`, `backend/app/main.py`).
- [ ] T053 Add a shell telemetry observer with job, stage, model-turn, research, checkpoint, render, and publish spans (`backend/app/services/txt2crs_observability.py`, `backend/app/core/telemetry.py`).
- [ ] T054 Ensure background traces receive new trace IDs and logs carry the active OpenTelemetry ID when enabled (`backend/app/services/txt2crs_worker.py`, `backend/app/core/logging.py`).
- [ ] T055 Redesign `write_last_error()` as safe structured diagnostic capture or leave automatic capture disabled if the sentinel contract cannot be proven (`backend/app/core/logging.py`).
- [ ] T056 Add local-only enablement and bounded retention for safe diagnostic files (`backend/app/core/config.py`, `backend/app/core/logging.py`).
- [ ] T057 Verify logging and tracing handler failures cannot change a successful or recoverable job result (`backend/tests/services/test_txt2crs_observability.py`).

### Session 5 - End-to-End Validation, Operations, and Rollout

**Objective:** Prove the complete debugging workflow and make it usable by an
operator.

- [ ] T058 Add deterministic fault injection at preparation, research, model output, local validation, checkpoint, rendering, and delivery boundaries (`backend/packages/txt2crs/tests/acceptance/test_observability_failures.py`).
- [ ] T059 Add shell acceptance coverage that correlates submission, worker attempt, stage, checkpoint, and terminal logs for one job (`backend/tests/acceptance/test_course_generation_observability.py`).
- [ ] T060 Add a malicious synthetic course run and assert sentinel absence across captured logs and trace attributes (`backend/tests/acceptance/test_course_generation_observability.py`).
- [ ] T061 Add a restart/resume acceptance test proving the same job ID and distinct run IDs produce an understandable timeline (`backend/tests/acceptance/test_job_results_and_recovery.py`).
- [ ] T062 Add a log-volume and formatter-overhead test with a representative four-module job (`backend/tests/acceptance/test_course_generation_observability.py`).
- [ ] T063 Add a credential-free validation script that checks event schema, event order, forbidden fields, and JSON parseability (`scripts/validate-course-generation-logging.sh`).
- [ ] T064 Add the focused validation script to `scripts/validate-changes.sh` without requiring providers or credentials (`scripts/validate-changes.sh`).
- [ ] T065 Run package unit, integration, contract, and acceptance tests (`backend/packages/txt2crs/`).
- [ ] T066 Run shell logging, worker, telemetry, configuration, and acceptance tests against a safe test database (`backend/`).
- [ ] T067 Run Ruff, mypy, the credential-free change gate, and Docker Compose smoke checks (`backend/`, repository root).
- [ ] T068 Perform one optional credentialed synthetic run and retain only redacted event names, safe fields, and timing evidence (`backend/packages/txt2crs/tests/acceptance/`).
- [ ] T069 Update the structured-logging and OpenTelemetry ADRs with the background-job event contract (`docs/adr/0003-structured-json-logging.md`, `docs/adr/0005-opentelemetry-distributed-tracing.md`).
- [ ] T070 Update configuration, architecture, security, development, and incident-response documentation (`docs/CONFIGURATION.md`, `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/development.md`, `docs/runbooks/incident-response.md`).
- [ ] T071 Add operator examples for filtering one job, comparing run attempts, locating the last checkpoint, and grouping safe failure fingerprints (`docs/runbooks/incident-response.md`).
- [ ] T072 Record completed work in `docs/CHANGELOG.md`, apply the required SemVer release process, and synchronize `VERSION` and the package version only when releasing (`docs/CHANGELOG.md`, `docs/VERSIONING.md`, `VERSION`, `backend/packages/txt2crs/pyproject.toml`).

## Test Matrix

| Scenario | Required evidence |
|----------|-------------------|
| Successful new job | Submission, one run, ordered stages, checkpoints, rendering, delivery, one terminal completion |
| Successful resume | Same job ID, new run ID, resume flag, last checkpoint, no replayed accepted-stage events |
| Provider retry succeeds | Retry event with bounded attempt and delay, stage completion, no raw provider error |
| Repair succeeds | Local rejection code, one repair event, accepted stage, repair count in terminal summary |
| Repair fails | Stage and execution failure with stable code, fingerprint, and last checkpoint |
| Research fails | Search/extract operation kind and safe code without query, URL, or response body |
| Checkpoint fails | Stage may complete, checkpoint does not; failure identifies persistence boundary |
| Rendering fails | Validated checkpoint remains clear; render failure is distinct from model failure |
| Application shutdown | Cancellation reason is `application_shutdown`; job remains restart-recoverable |
| User cancellation | Exactly one cancellation terminal event and matching durable status |
| Observer throws | Job result and recovery behavior are unchanged |
| Trace exporter fails | Logs remain complete and execution is unchanged |
| Malicious error text | Every private sentinel is absent from logs, diagnostics, and trace attributes |
| Two sequential jobs | No job, run, stage, or trace context leaks from the first job to the second |

## Operational Acceptance Queries

The final log shape must support these conceptual queries without parsing
human prose:

```text
all events where job_id = <job>
all execution attempts where job_id = <job>, ordered by occurred_at
all failures grouped by failure_code and error_fingerprint
all stage durations for stage = collect_evidence
all retries where failure_code = provider_timeout
all jobs whose last checkpoint precedes their failed stage
```

## Performance and Volume Budgets

- Formatter and observer overhead should remain below 1 percent of a
  deterministic generation run or 50 milliseconds total, whichever is easier
  to measure reliably in CI.
- A normal four-module successful run should emit no more than 80 first-party
  INFO course-generation records.
- DEBUG event volume must be bounded by the existing turn, research-call,
  retry, and repair budgets.
- No event may contain a string longer than 500 characters.
- No arbitrary nested mapping may be accepted as a log field.
- Heartbeat persistence must not generate recurring INFO logs.

## Rollout Strategy

1. Land the safe event schema, observer, and sentinel tests with no producers.
2. Enable job, stage, and checkpoint INFO events in deterministic mode.
3. Connect retry, repair, runtime, research, and rendering producers.
4. Suppress redundant third-party INFO noise after equivalent first-party
   events are verified.
5. Add optional custom OpenTelemetry spans.
6. Run the complete deterministic and shell acceptance matrix.
7. Inspect one local credentialed synthetic run if credentials are available.
8. Update operator documentation and release through the normal versioning
   process.

Do not hide the new timeline behind a temporary feature flag. The event model
and INFO policy are compatibility contracts. Optional DEBUG output, tracing,
and safe diagnostic files remain configuration-controlled.

## Definition of Done

- A failed run can be localized to one job, run, stage, operation, and last
  checkpoint using routine INFO logs alone.
- Retry, repair, cancellation, restart, rendering, and delivery failures are
  distinguishable by stable codes.
- Successful runs provide stage and end-to-end timings without content or
  token data.
- The real Codex and research paths emit safe bounded events through the public
  package observer boundary.
- Worker log context is present during execution and cannot leak across jobs.
- Optional traces visualize the same timeline and use only approved
  attributes.
- Malicious sentinel tests prove that every forbidden data class stays out of
  logs, diagnostics, and traces.
- First-party INFO output is more useful and less noisy than current HTTPX and
  MCP infrastructure chatter.
- Observer, formatter, file, and trace-export failures never affect durable
  generation behavior.
- Documentation, changelog, version, and validation evidence are synchronized
  for the release that ships the implementation.

## File Ownership Map

| Responsibility | Primary files |
|----------------|---------------|
| Safe engine event contract | `backend/packages/txt2crs/src/txt2crs/observability/` |
| Job and checkpoint lifecycle | `backend/packages/txt2crs/src/txt2crs/jobs/executor.py` |
| Pipeline stages and repairs | `backend/packages/txt2crs/src/txt2crs/generation/pipeline.py` |
| Runtime and tool projection | `backend/packages/txt2crs/src/txt2crs/ai/codex_runtime.py` |
| Retry events | `backend/packages/txt2crs/src/txt2crs/ai/retry.py` |
| Research events | `backend/packages/txt2crs/src/txt2crs/research/` |
| Shell observer and worker correlation | `backend/app/services/txt2crs_observability.py`, `backend/app/services/txt2crs_worker.py` |
| Formatting and context | `backend/app/core/logging.py` |
| Trace export | `backend/app/core/telemetry.py` |
| Settings | `backend/app/core/config.py`, `backend/app/main.py` |
| Operator guidance | `docs/runbooks/incident-response.md`, `docs/CONFIGURATION.md` |

## Explicitly Out of Scope

- Logging chain-of-thought, model output, prompts, research queries, evidence,
  or artifact content.
- Returning private diagnostics through learner-facing APIs.
- Exposing exact package checkpoint labels in the browser progress contract.
- Adding a new external log aggregation vendor.
- Adding Prometheus or another metrics stack solely for this project.
- Persisting request trace IDs in the engine job database.
- Replacing the durable job store or changing recovery semantics.
- Editing the generated frontend API client when no HTTP contract changes.
