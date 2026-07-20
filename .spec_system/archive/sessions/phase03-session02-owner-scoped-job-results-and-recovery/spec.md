# Session Specification

**Session ID**: `phase03-session02-owner-scoped-job-results-and-recovery`
**Phase**: 03 - Durable Jobs API
**Status**: Complete
**Created**: 2026-07-20
**Base Commit**: d080c4be2fb11e3fd016ca89d7fd495241961356
**Package**: backend
**Package Stack**: Python 3.14, FastAPI, Pydantic v2, public txt2crs
projections/streams, SQLite and private filesystem through the engine facade,
Starlette streaming responses, and generated TypeScript client

---

## 1. Session Overview

This session completes the private read and delivery half of the durable jobs
API created in Session 01. An authenticated owner can poll one safe current
job projection, inspect a path-free manifest grouped by educational
deliverable, and download one integrity-checked artifact through stable
identifiers. Missing and foreign resources share one context-free 404
boundary, while every successful response remains private and non-cacheable.

The existing engine already owns atomic owner queries, safe projections,
manifest verification, and same-descriptor artifact streams. This session
tightens that public projection to the application contract, then translates
only those allowlisted values into strict HTTP schemas. FastAPI never reads
SQLite, checkpoint JSON, artifact paths, or raw rendered files.

Application acceptance also proves process replacement from accepted,
resolved-preference, rendering, and delivery boundaries. The replacement
application uses the exact stored request/profile/checkpoint, and completed
delivery replay reads existing artifacts without repeating accepted model
work.

---

## 2. Objectives

1. Expose bounded, revisioned, owner-scoped job status and result summaries
   without private request, checkpoint, provider, usage, evidence, or path
   data.
2. Expose one verified path-free artifact manifest and one
   integrity-checked download with safe headers and deterministic closure on
   completion, disconnect, and failure.
3. Make missing jobs, wrong owners, missing artifacts, and wrong-owner
   artifacts indistinguishable through one registered 404 response.
4. Prove accepted and active checkpoint recovery plus rendering/delivery
   replay through the public application facade and serial worker boundary.
5. Regenerate and document the exact OpenAPI/client contract without
   hand-editing generated frontend files.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase03-session01-durable-job-submission-and-admission` - supplies
  strict authenticated intake, durable commit, idempotency, admission, and the
  reusable deterministic acceptance harness.
- [x] `phase01-session02-safe-queries-and-artifact-access` - supplies
  owner-scoped package projections, verified manifests, and context-managed
  single-artifact streams.
- [x] `phase01-session05-public-facade-and-owner-lifecycle` - exposes safe
  job, manifest, artifact, recovery, executor, and owner operations through
  one public facade.
- [x] `phase02-session02-serial-worker-supervisor` - supplies startup
  discovery and durable recovery independent of an in-memory wake hint.

### Required Tools Or Knowledge

- Pydantic v2 strict/frozen response contracts and explicit allowlist mapping.
- FastAPI path dependencies, Starlette `StreamingResponse`, ASGI disconnect
  behavior, and deterministic context cleanup.
- Public `txt2crs` job projection, artifact manifest, stream, executor, and
  deterministic factory contracts.
- Existing SQLite/checkpoint and private filesystem recovery invariants.

### Environment Requirements

- Default tests remain credential-free, network-free, and isolated under
  pytest temporary directories.
- Backend tests use the isolated PostgreSQL 18 instance on host port 55433;
  engine job/recovery state remains tenant-scoped SQLite.
- Engine commands run from `backend/packages/txt2crs/`; shell commands run
  from `backend/`.
- OpenAPI generation must not start lifespan resources, providers, workers,
  or listeners.

---

## 4. Scope

### In Scope (MVP)

- An authenticated owner can retrieve one current job/result response whose
  revision is monotonic and whose progress total remains null until the
  accepted course plan establishes its finite module count.
- The job response contains a fixed safe stage/message, bounded input display
  metadata, terminal failure, resolved audience/level/language, objective and
  module counts, at most 12 sources, at most 20 warnings/conflicts, explicit
  truncation flags, and a manifest URL only after verified publication.
- An authenticated owner can retrieve a verified artifact manifest grouped
  across the four canonical deliverables and four formats without body bytes
  or filesystem paths.
- An authenticated owner can download one verified artifact with exact media
  type/length, RFC-safe attachment disposition, private/no-store, nosniff, and
  referrer-policy headers.
- The HTTP stream owns the already-entered package context and closes it
  exactly once after exhaustion, disconnect, send failure, iterator failure,
  or response failure.
- Deterministic acceptance covers two-owner isolation, accepted restart,
  resolved-preference/module restart, render restart, delivery restart, and
  repeated delivery without model regeneration.

### Out Of Scope (Deferred)

- Job list/history, cancellation, or per-job deletion - Reason: deferred P1
  lifecycle scope.
- ETag, `If-None-Match`, and 304 responses - Reason: the master P0 contract
  explicitly chooses small revisioned private/no-store polling responses.
- HTML preview sandboxing - Reason: Phase 04 owns browser preview isolation.
- Account deletion and owner purge integration - Reason: Session 03 owns the
  cross-store worker barrier and partial-failure contract.
- Donor Items removal and Alembic migration - Reason: Session 03 starts only
  after this complete replacement API and acceptance coverage are green.
- Frontend progress/results screens and polling timers - Reason: Phase 04
  consumes the generated contract and owns visible/hidden cadence, backoff,
  announcements, and terminal stop.

---

## 5. Technical Approach

### Architecture

Tighten `txt2crs.jobs.PublicJobSnapshot` before exposing it over HTTP. Add the
durable job revision, nullable pre-plan total, bounded upload/input size,
resolved result leaves and counts, the 12-source cap, and explicit warning,
source, and conflict truncation flags. These values are copied from validated
request/checkpoint objects inside `public_queries.py`; the shell never imports
or parses a private checkpoint.

Extend `app.schemas.jobs` with strict status, progress, input, failure, result,
source, manifest-group, and artifact metadata responses. Mapping classmethods
construct each response field explicitly from public package contracts.
FastAPI uses the existing lifespan-owned `Txt2CrsApplicationDep` and the
central exception translator for every query.

Add an API-owned closing streaming response. The route enters the package
artifact context before sending headers so integrity/not-found failures can
still become Problem Details. The response wraps the verified iterator and
closes the package context in an ASGI `finally` block; cleanup is idempotent so
normal exhaustion, disconnect, send failure, and explicit close cannot race or
double-close.

Extend the Phase 03 deterministic harness with one complete six-turn scenario
and remainder scenarios. Acceptance fault injection interrupts only test
runtime/render/storage boundaries, then reopens the same application state
through public factories. Replacement execution must consume only work after
the latest accepted checkpoint, while delivery replay opens existing artifacts
and consumes no model turn.

### Design Patterns

- Public allowlist projection: copy reviewed leaves into fresh strict package
  and HTTP contracts rather than filtering private serialized state.
- Owner-as-query-input: pass the authenticated UUID to every facade read; do
  not load then authorize.
- Uniform not-found boundary: translate package owner/job/artifact absence to
  the same code, status, and detail.
- Enter-before-headers streaming: verify authorization, metadata, and
  integrity before a response can partially succeed.
- Response-owned cleanup: one idempotent context owner closes on every ASGI
  exit, including disconnect.
- Durable recovery over events: reopen SQLite/filesystem state and let the
  serial worker discover runnable work without relying on a prior wake signal.
- Generated contract ownership: regenerate OpenAPI and TypeScript only through
  `scripts/generate-client.sh`.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/app/api/artifact_response.py` | Idempotent response-owned verified stream cleanup across completion/disconnect/failure | ~170 |
| `backend/tests/api/test_artifact_response.py` | Direct ASGI success, disconnect, send failure, iterator failure, and exact-once cleanup tests | ~260 |
| `backend/tests/api/routes/test_jobs_results.py` | Auth, ownership, status/result, manifest, download, header, integrity, and privacy route contracts | ~520 |
| `backend/tests/acceptance/test_job_results_and_recovery.py` | Public-facade reads plus accepted/active/render/delivery restart and replay proof | ~520 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` | Add revision, nullable pre-plan totals, input size, resolved result/count leaves, 12-source cap, and truncation flags | ~180 |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Export only the added public projection contracts | ~15 |
| `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` | Protect projection bounds, coherence, result leaves, revision, and privacy | ~220 |
| `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py` | Protect restart-safe extended projections and verified delivery metadata | ~100 |
| `backend/app/schemas/jobs.py` | Add strict allowlisted job/result/manifest/artifact HTTP responses and explicit package mappers | ~300 |
| `backend/app/api/routes/jobs.py` | Add owner status, manifest, and artifact routes with private headers and safe streaming | ~220 |
| `backend/app/core/txt2crs_errors.py` | Translate projection/integrity failures without private context | ~20 |
| `backend/tests/core/test_txt2crs_errors.py` | Protect safe public query/integrity mappings | ~30 |
| `backend/tests/acceptance/conftest.py` | Add complete and remainder deterministic scenarios plus reopen helpers | ~260 |
| `backend/tests/scripts/test_generate_client_contract.py` | Protect read/download auth, paths, schemas, headers, and no-ETag contract | ~100 |
| `frontend/openapi.json` and `frontend/src/client/` | Generated status/result/manifest/download contract | generated |
| `docs/api/README_api.md`, `docs/ARCHITECTURE.md`, and `docs/runbooks/incident-response.md` | Document private polling, safe results, artifact delivery, restart, and integrity response | ~120 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] Status responses are owner-scoped, strict, monotonic by durable
  revision, and contain no request value, normalized text, checkpoint,
  provider, usage, evidence excerpt, artifact bytes, or filesystem path.
- [ ] Pre-plan `total_units` is null; accepted course-plan checkpoints produce
  a finite total and completed jobs report the full total.
- [ ] Result summaries expose only a bounded title, resolved
  audience/level/language, objective/module counts, at most 12 safe sources,
  at most 20 conflict summaries, and explicit truncation flags.
- [ ] Input warnings are capped at 20 with explicit truncation, and source
  URLs omit credentials, query strings, fragments, unsafe paths, and tokens.
- [ ] Missing and wrong-owner job, manifest, and artifact requests return the
  same `JOB_NOT_FOUND` Problem Detail without proving resource existence.
- [ ] Manifests group stable canonical IDs by four deliverables and expose
  only format, safe filename, media type, size, and hash metadata.
- [ ] Downloads verify package integrity before headers, use exact safe
  attachment/media/length/privacy headers, and contain no path.
- [ ] Package stream contexts close exactly once on success, early
  disconnect, send error, iterator error, and route/response failure.
- [ ] Accepted and active jobs complete after application replacement from
  stored request/profile/checkpoint identity.
- [ ] Render and delivery replacement plus repeated artifact delivery perform
  no repeated accepted model turn and return identical verified bytes.
- [ ] P0 status responses use revision plus `private, no-store` and do not
  advertise or implement ETag/304.

### Testing Requirements

- [ ] Failing package projection, shell schema, streaming-response, route,
  error, generated-contract, and recovery acceptance tests are observed before
  implementation.
- [ ] Focused engine public-query and shell status/artifact suites pass.
- [ ] Direct ASGI tests prove response cleanup for both modern disconnect
  send errors and iterator failures.
- [ ] Deterministic application acceptance proves two-owner isolation and all
  four required restart/delivery boundaries.
- [ ] Complete engine, backend, generated-client, and frontend static/build
  suites pass.

### Non-Functional Requirements

- [ ] Routes import no private engine store, checkpoint, renderer, path, or
  provider implementation.
- [ ] Response arrays, text, identifiers, progress, content length, and stream
  chunks remain under explicit finite bounds.
- [ ] Streaming does not buffer artifact bodies in FastAPI and retains the
  package's same verified descriptor.
- [ ] Logs and errors exclude learner content, source URLs, filenames,
  artifact IDs, hashes, provider details, exception content, and paths.
- [ ] Default acceptance remains credential-free and creates no network
  listener or provider process.

### Quality Gates

- [ ] All files ASCII-encoded
- [ ] Unix LF line endings
- [ ] Code follows project conventions
- [ ] Intern-friendly comments explain projection ownership, null progress,
  enter-before-headers, disconnect cleanup, and replay boundaries
- [ ] Ruff format/check, strict mypy, ty, generated-client drift, frontend
  checks, and repository pre-commit pass

---

## 8. Implementation Notes

### Working Assumptions

- The candidate stub's "completed-result projection" requires the master
  response fields that the current package snapshot does not yet expose.
  Extending `public_queries.py` is safe and required because private
  checkpoints cannot be parsed in the shell.
- The existing package uses one `JobNotFoundError` for missing owners, jobs,
  manifests, and artifact IDs. Reusing `JOB_NOT_FOUND` preserves the proven
  indistinguishable boundary instead of adding an artifact-specific oracle.
- `Content-Disposition: attachment` remains compatible with Phase 04 HTML
  preview because the browser may fetch verified bytes into a sandboxed blob;
  this session does not render HTML in the application document.
- `frontend/openapi.json`, generated client files, and public documentation
  are required derivative crossings for this backend session; all product UI
  remains out of scope.

### Conflict Resolutions

- The Session 02 stub mentions "conditional response behavior," while the
  master plan explicitly states P0 does not add ETag/304. The explicit master
  decision wins: expose monotonic `revision`, assert no `ETag`, and retain
  `Cache-Control: private, no-store`.
- The current package gives pre-plan jobs a default total of 12, while the
  master API contract requires `total_units=null` until a course plan fixes
  module count. The master public contract wins; completed-unit monotonicity
  remains while the total is unknown.
- The current package permits up to 100 source summaries, while the master API
  caps polling responses at 12 and requires explicit truncation. Tighten the
  public package projection to 12 so every consumer receives the same bound.

### Key Considerations

- Enter the artifact context before response headers so corrupt or missing
  bytes can still become a normal context-free Problem Detail.
- A stock Starlette sync-stream wrapper does not itself promise to close a
  package context after every ASGI send failure; the response must own cleanup
  in `finally`.
- Never derive result fields from request intent after `auto` resolution;
  copy only the accepted `resolved_preferences` and course-plan/course counts.
- Artifact metadata is immutable, but the package reauthorizes and revalidates
  the selected descriptor so a manifest read is never treated as a byte-read
  authorization cache.
- Reopening must use the stored execution profile and request hash; a test
  factory may supply only remaining deterministic outputs but may not replace
  stored identity.

### Potential Challenges

- An integrity failure discovered after headers would be impossible to render
  as Problem Details. Entering and fully validating the package stream before
  constructing the response prevents that partial-success ambiguity.
- Process-interruption acceptance needs precise fault injection without a
  production debug switch. Tests will interrupt deterministic runtime,
  renderer, or artifact-save calls, then interact only through fresh public
  application/worker handles.
- Source and conflict truncation must report whether valid private items were
  omitted after sanitization, not merely whether the original raw list was
  long.

### Relevant Considerations

- [P01-backend+backend/packages/txt2crs] **HTTP artifact delivery owns
  cleanup**: the API response closes the package context on every ASGI exit
  and applies private/no-store, nosniff, and safe attachment headers.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  routes call only the public facade and copy public projection leaves.
- [P02-backend+backend/packages/txt2crs] **Admission and recovery use public
  handles**: replacement workers discover exact durable work without reading
  private stores.
- [P01-backend/packages/txt2crs] **Persist exact accepted identity**:
  restart uses stored request/profile/resolved preferences/checkpoints rather
  than current defaults.
- [P01-backend/packages/txt2crs] **Construct public allowlists**: status,
  result, failure, manifest, and artifact responses are built field by field.
- [P01-backend/packages/txt2crs] **Do not let writer/read bounds drift**:
  manifest and stream reads reuse the package's writer-compatible metadata,
  topology, byte-limit, and integrity validation.
- [P02-backend] **Operational logs use field allowlists**: no source,
  filename, artifact ID/hash, exception, or path value enters new events.
- [P00] **Pre-commit omits untracked files**: check new response, route test,
  acceptance, and report files explicitly before review.

### Behavioral Quality Focus

Checklist active: Yes

Top behavioral risks for this session:

- A wrong-owner response, result mapper, or log becomes a private-resource
  oracle or leaks accepted checkpoint/source/provider state.
- A client disconnects after headers and leaves the verified package file
  descriptor/context open.
- A replacement worker reruns accepted model stages or delivery replay
  regenerates paid work instead of using durable checkpoints/artifacts.

---

## 9. Testing Strategy

### Unit Tests

- Package projection tests cover accepted/no-checkpoint, preparation,
  course-plan, module, completed, failed, cancelled, malformed, bounded,
  truncated, and unsafe URL/private value cases.
- Shell schema tests reject unknown fields and prove package-to-HTTP mapping
  for nullable progress, result presence, source/conflict bounds, failure, and
  grouped artifact metadata.
- Direct response tests call the ASGI response with controlled sends and
  iterators to prove exact-once context exit on exhaustion, disconnect,
  response failure, and iterator failure.
- Error tests prove `JobNotFoundError`, `PublicJobProjectionError`, and
  `ArtifactIntegrityError` translate without private exception context.

### Integration Tests

- Authenticated route tests compare missing and foreign-owner status,
  manifest, and artifact Problem Details; assert strict response bodies,
  privacy/no-ETag headers, safe disposition, exact content length/type, and
  stream cleanup.
- Generated-contract tests require all three GET routes, bearer auth, path
  parameter bounds, response schemas, binary artifact content, and registered
  safe errors.

### Runtime Verification

- Submit, close, reopen, start the serial worker, and poll until completion;
  query the result, 16-item manifest, and selected artifact through public
  facade methods.
- Interrupt after resolved preferences, after the final cross-validation
  checkpoint, and during artifact save; reopen the same state and prove only
  remaining work executes.
- Open the same completed artifact repeatedly after another reopen and prove
  identical hash/bytes with zero model turn or rendering call.

### Edge Cases

- Unknown/malformed identifiers, accepted jobs without checkpoints, unknown
  totals, terminal failures, invalid private checkpoint coherence, and stale
  revisions.
- More than 20 warnings/conflicts, more than 12 sources, sanitized-away
  values, token-bearing URLs, and unsafe filename punctuation.
- Empty/incomplete manifests, missing canonical artifact IDs, corrupt size or
  hash, context-entry failure, partial consumption, disconnect, send error,
  iterator error, and double-close attempts.

---

## 10. Dependencies

### Other Sessions

- Depends on: `phase03-session01-durable-job-submission-and-admission`,
  `phase01-session02-safe-queries-and-artifact-access`,
  `phase01-session05-public-facade-and-owner-lifecycle`, and
  `phase02-session02-serial-worker-supervisor`.
- Depended by: `phase03-session03-account-purge-and-donor-retirement`, both
  Phase 04 learner sessions, and the Phase 05 end-to-end release proof.

---

## Next Steps

Session complete. Run `plansession` for Phase 03 Session 03.
