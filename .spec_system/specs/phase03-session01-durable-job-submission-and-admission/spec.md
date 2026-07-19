# Session Specification

**Session ID**: `phase03-session01-durable-job-submission-and-admission`
**Phase**: 03 - Durable Jobs API
**Status**: Complete
**Created**: 2026-07-19
**Base Commit**: 3dfbd01cf771a67d94b783fdfe269dcb9d357161
**Package**: backend
**Package Stack**: Python 3.14, FastAPI, Pydantic v2, public txt2crs
contracts, SQLite through the engine facade, and generated TypeScript client

---

## 1. Session Overview

This session creates the first authenticated learner course-job write path. It
accepts strict JSON for prompt, text, URL, and YouTube intent plus strict
multipart metadata and one PDF, DOCX, or PPTX upload. HTTP framing, finite
streaming, safe file metadata, signature agreement, and OOXML expansion are
validated before the package receives the request.

The shell maps validated transport values into the existing immutable engine
request/profile contracts, checks the cached readiness gate, and calls the
public application facade. The package remains authoritative for policy,
canonical hashing, owner-scoped idempotency, admission, and the durable job
commit. Only after that call returns may FastAPI answer `202 Accepted` and
nudge the serial worker.

Session 01 is the necessary dependency for every later status, artifact,
restart, erasure, and learner-UI session. It establishes deterministic
application acceptance fixtures that later Phase 03 sessions can extend.

---

## 2. Objectives

1. Reject malformed, unknown, oversize, mismatched, corrupt, or
   expansion-unsafe JSON/multipart input before provider work or persistence.
2. Build one exact package `GenerationRequest` from authenticated owner
   context and reviewed server defaults without copying engine policy or
   persistence logic into a route.
3. Enforce synchronous package preflight policy, cached readiness, canonical
   owner-scoped idempotency, and atomic admission before `202`.
4. Return a strict safe accepted-job projection with stable status location,
   revision, and private/no-store headers, then wake the worker as a
   latency-only hint.
5. Add an explicit local-only public-signup switch, finite job submission rate
   limits, registered RFC 9457 errors, and generated API contracts.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase02-session01-engine-composition-lifecycle` - provides the
  settings-to-profile translation and lifespan-owned public facade.
- [x] `phase02-session02-serial-worker-supervisor` - provides durable
  discovery and the post-commit `notify_runnable()` hint.
- [x] `phase02-session03-cached-readiness-and-observability` - provides the
  immutable admission gate and safe error/event boundaries.
- [x] `phase02-session04-system-readiness-and-auth-api` - proves authenticated
  dependencies and generated-client ownership.

### Required Tools Or Knowledge

- FastAPI discriminated JSON models, `Form`, `UploadFile`, and pure ASGI
  receive wrapping.
- Pydantic v2 strict/frozen models and the public `txt2crs` request, quota, and
  policy contracts.
- ZIP central-directory inspection and OOXML content-type structure.
- slowapi, RFC 9457 exception handling, and OpenAPI generation.

### Environment Requirements

- Default tests remain deterministic, credential-free, and network-free.
- Focused package tests run from `backend/packages/txt2crs/`.
- Full shell tests use isolated PostgreSQL; acceptance engine state uses
  temporary SQLite/artifact roots.
- OpenAPI generation must not start a lifespan, provider, MCP listener, or
  worker.

---

## 4. Scope

### In Scope (MVP)

- An authenticated learner can submit one prompt, pasted text, public URL, or
  YouTube URL through strict JSON - the shell validates shape and `https`
  syntax while package URL safety and routing remain authoritative.
- An authenticated learner can submit one PDF, DOCX, or PPTX with strict JSON
  metadata plus exactly one bounded upload - the shell streams finite bytes
  and validates transport structure before creating a package input payload.
- A retry with the same owner, key, and canonical request receives the
  original job; reuse with different work returns a registered `409`.
- A request receives `202` only after package preflight, admission reservation,
  and immutable request/job commit succeed.
- A disabled/unready system, policy refusal, quota refusal, unsupported media,
  oversize body, or invalid request returns a stable RFC 9457 error and creates
  no job.
- Local public registration works only when the explicit setting is enabled;
  the judge/demo environment example keeps it disabled.

### Out Of Scope (Deferred)

- Job status/result reads and polling - Reason: Session 02 owns safe
  projections and restart behavior.
- Artifact manifests/downloads - Reason: Session 02 owns integrity-checked
  response streaming and cleanup.
- Account erasure and donor item removal - Reason: Session 03 depends on green
  jobs acceptance coverage.
- Job lists, cancellation, or per-job deletion - Reason: explicitly deferred
  P1 scope.
- Learner intake UI - Reason: Phase 04 consumes the generated contract.
- URL host/DNS/redirect/extraction policy or document text extraction -
  Reason: these remain authoritative inside the reusable engine.

---

## 5. Technical Approach

### Architecture

Add strict external contracts in `app/schemas/jobs.py`. JSON uses a
discriminated input union with separate finite prompt/text/URL bounds. Upload
metadata reuses the same preferences, consent, and age contract without
accepting owner, model, budget, policy flags, or file paths. The
`Idempotency-Key` header is a shared annotated pattern-limited type.

Add a pure ASGI request-size middleware around the `/api/v1/jobs/upload`
request body. It rejects a declared oversize body before multipart parsing and
wraps `receive` so a missing or dishonest content length cannot exceed the
finite file, metadata, and framing allowance. The route still reads the
`UploadFile` in bounded chunks into a finite byte buffer because the engine's
immutable request must persist the exact bytes. Cleanup closes the framework
spool in `finally`.

Add `txt2crs_uploads.py` to validate safe display basename, extension,
declared media type, PDF/ZIP magic, OOXML entry count, total expanded bytes,
encrypted entries, traversal names, active/macro content, and expected
`[Content_Types].xml` markers. It returns only a reviewed `InputPayload`; it
does not extract learner content.

Add `txt2crs_submission.py` as the thin composition adapter. It builds the
immutable execution profile from shell settings, normalized learning
preference intent, input payload, and finite package admission reservation.
The package facade performs preflight policy before calling `JobService.submit`
so no shell consumer can bypass consent/content policy. The service checks the
cached `accepting_jobs` value, submits under the current UUID string, then
calls `worker.notify_runnable()` only after durable success.

The JSON and upload handlers share this service, error translation, headers,
and response construction. Their logs contain only opaque user/job identity,
input category, state, and stable reason/error code.

### Design Patterns

- Transport/domain separation: FastAPI validates HTTP framing; the package
  owns content interpretation and durable course behavior.
- Tests-first contract slices: schema, middleware, upload, service, route, and
  acceptance failures precede implementation.
- Public facade policy gate: preflight becomes part of package submission
  rather than a shell-side policy import.
- Write-through idempotency: one package transaction decides replay,
  conflict, reservation, and durable job identity.
- Fail-closed readiness: new work uses the immutable cache and never triggers
  provider/storage probes from the request.
- Post-commit wake hint: the event reduces latency but durable polling remains
  recovery-authoritative.
- Generated contract ownership: OpenAPI and TypeScript are regenerated by the
  repository script only.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/app/schemas/jobs.py` | Strict JSON, multipart metadata, idempotency, and accepted-job HTTP contracts | ~320 |
| `backend/app/services/txt2crs_uploads.py` | Bounded upload reading and PDF/OOXML transport validation | ~360 |
| `backend/app/services/txt2crs_submission.py` | Readiness, request construction, facade submit, and worker nudge boundary | ~300 |
| `backend/app/api/routes/jobs.py` | Authenticated JSON and upload submission endpoints | ~260 |
| `backend/tests/schemas/test_job_schemas.py` | Strict field, union, bounds, URL, preference, consent, age, and response tests | ~380 |
| `backend/tests/services/test_txt2crs_uploads.py` | Streaming, filename, MIME, magic, ZIP/OOXML, expansion, and cleanup tests | ~520 |
| `backend/tests/services/test_txt2crs_submission.py` | Request mapping, readiness, preflight, idempotency, admission, nudge, and privacy tests | ~460 |
| `backend/tests/api/routes/test_jobs_submission.py` | Auth, request/header, JSON/upload, errors, headers, and rate-limit tests | ~520 |
| `backend/tests/acceptance/conftest.py` | Reusable deterministic facade/application fixtures for Phase 03 | ~260 |
| `backend/tests/acceptance/test_job_submission.py` | Durable commit, duplicate/conflict, quota, two-owner, and no-provider-work scenarios | ~440 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/application/facade.py` | Make package preflight an authoritative part of submission | ~45 |
| `backend/packages/txt2crs/src/txt2crs/application/factories.py` | Compose the default preflight evaluator and shared reservation factory | ~35 |
| `backend/packages/txt2crs/src/txt2crs/application/__init__.py` and `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Export only shell-needed policy/reservation contracts | ~20 |
| `backend/packages/txt2crs/tests/unit/test_application_facade.py` and `backend/packages/txt2crs/tests/contract/test_application_factories.py` | Protect preflight ordering, refusal, and configured defaults | ~120 |
| `backend/app/core/config.py`, `.env.example`, and `backend/.env.example` | Add local-only public-signup configuration and examples | ~20 |
| `backend/app/core/constants.py` and `backend/app/core/txt2crs_errors.py` | Add payload/media/policy status and safe package mappings while preserving shipped code ranges | ~35 |
| `backend/app/core/middleware.py` and `backend/app/main.py` | Enforce upload ingress bounds before multipart parsing | ~100 |
| `backend/app/core/rate_limit.py` | Add a finite job submission rate | ~5 |
| `backend/app/api/deps.py`, `backend/app/api/main.py`, and `backend/app/services/__init__.py` | Expose course-system services and register the jobs router | ~70 |
| `backend/app/api/routes/users.py` | Reject public signup unless explicitly enabled in local mode | ~25 |
| Existing shell core/settings/middleware/error/signup tests | Protect new settings, body cap, codes, and registration behavior | ~180 |
| `backend/tests/scripts/test_generate_client_contract.py` | Protect submission route/auth/schema/header contract | ~60 |
| `frontend/openapi.json` and `frontend/src/client/` | Generated and formatted submission API contract | generated |
| `docs/api/README_api.md`, `docs/CONFIGURATION.md`, and `docs/environments.md` | Document submission safety, errors, and local signup mode | ~100 |

---

## 7. Success Criteria

### Functional Requirements

- [ ] JSON input is strict and accepts only reviewed prompt, text, URL, or
  YouTube shapes with the documented finite preferences.
- [ ] Multipart accepts exactly one metadata object and one PDF, DOCX, or PPTX
  while rejecting extra form fields or files.
- [ ] Declared and actual body size, extension, MIME, magic, safe filename, ZIP
  entries, expanded bytes, encryption, traversal, active content, and OOXML
  structure are validated before package submission.
- [ ] Package preflight refuses missing consent, prohibited content, and
  high-risk review before durable commit or worker/provider work.
- [ ] Same-owner/same-key/same-request replay returns the original job;
  changed work returns `JOB_IDEMPOTENCY_CONFLICT`.
- [ ] Readiness and quota refusal create no job and do not notify the worker.
- [ ] A new or replayed durable job returns `202`, a stable status URL and
  `Location`, `Cache-Control: private, no-store`, and no private request data.
- [ ] Worker notification occurs after, never before, successful facade
  submission.
- [ ] Public signup is enabled only by an explicit local setting and disabled
  in the root judge/demo example.

### Testing Requirements

- [ ] Tests are written and observed failing before implementation.
- [ ] Focused engine facade/factory and shell schema/middleware/service/route
  tests pass.
- [ ] Deterministic application acceptance proves durable replay, conflict,
  capacity, two-owner namespace isolation, and no provider work on rejection.
- [ ] Complete engine and backend shell suites pass.
- [ ] Generated OpenAPI/client contract tests and frontend type/lint checks
  pass.

### Non-Functional Requirements

- [ ] Route handlers never import engine stores, adapters, policy
  implementations, pipelines, renderers, or provider clients.
- [ ] All reads, loops, collection sizes, decompression totals, and messages
  use explicit finite bounds.
- [ ] Upload spool and package resources close on success, rejection,
  disconnect, cancellation, and exception.
- [ ] Structured events exclude email, key, source text, URLs, filenames,
  archive names, hashes, provider details, and exception content.
- [ ] Submission is deterministic, credential-free in tests, and creates no
  background provider work inside the request.

### Quality Gates

- [ ] All files ASCII-encoded
- [ ] Unix LF line endings
- [ ] Code follows project conventions
- [ ] Intern-friendly comments explain framing bounds, package ownership,
  transaction/idempotency order, and cleanup
- [ ] Ruff format/check, strict mypy, ty, generated-client drift, frontend
  checks, and repository pre-commit pass

---

## 8. Implementation Notes

### Working Assumptions

- YouTube intent maps to the package `url` input type without shell host
  inspection. The real package `RoutingUrlAdapter` remains responsible for
  recognizing approved YouTube hosts, which preserves the strict boundary.
- A bounded upload is collected into memory only after the pure ASGI body cap
  and chunk counter pass because the current immutable engine request stores
  exact bytes in SQLite. The 20 MiB limit makes this finite; object/external
  input storage remains out of P0 scope.
- The application settings-to-profile function from Phase 02 remains the
  source of reviewed execution defaults. The package supplies the matching
  finite admission reservation so readiness and submission cannot drift.
- The root `.env.example` represents judge/demo Compose and disables signup;
  `backend/.env.example` represents host developer mode and enables it.

### Conflict Resolutions

- The system plan's historical error table assigns system values in 7xxx and
  job values in 6xxx, but Phase 02 already released system 6xxx and job 7xxx
  codes and documents those ranges. This session preserves shipped codes and
  adds missing job meanings inside the 7xxx range.
- The plan says to run synchronous package preflight before durable commit,
  while the current facade performs policy only inside worker preparation.
  Submission will add preflight to the public facade itself; FastAPI will not
  instantiate or duplicate `ContentPolicy`.
- The plan says to enforce the file cap before multipart spooling and to
  retain a streaming counter. A route-level `UploadFile` loop alone is too
  late, so a route-scoped pure ASGI receive wrapper supplies the ingress bound
  and the upload service supplies the exact file bound.
- The master plan says P0 does not use ETag/304. The accepted response exposes
  the stable initial revision/location, but conditional polling remains
  Session 02 and will use `Cache-Control: private, no-store` without ETag.

### Key Considerations

- Pydantic validation errors can retain learner values in exception context.
  Shell translation must raise safe outer errors after leaving caught
  exception scopes.
- Multipart metadata is untrusted JSON and must reject duplicate/unknown
  generation-affecting fields instead of silently dropping them.
- ZIP validation reads central-directory metadata only after raw byte bounds
  and rejects traversal, encryption, macros/active content, excessive entries,
  and excessive expanded totals without extracting files.
- Idempotency keys are private transport metadata and must not be logged or
  returned.
- The worker event is never proof of queue state; durable store polling remains
  authoritative after restart or a missed notification.

### Potential Challenges

- FastAPI parses multipart dependencies before route code. A pure ASGI wrapper
  must preserve normal receive semantics while terminating oversize requests
  with the registered 413 response.
- Replayed submissions return an existing job, so notification is harmless
  but unnecessary. The service should nudge only when the public package
  result indicates runnable work without trying to infer private transaction
  state.
- Deterministic factory input capabilities currently omit real URL/document
  adapters. Acceptance can prove submission durability with prompt/text while
  transport unit/route tests prove other modes without opening providers.

### Relevant Considerations

- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  submission calls only public contracts and keeps domain policy in the
  package.
- [P02-backend+backend/packages/txt2crs] **Admission and recovery use public
  handles**: commit through the facade before nudging the worker.
- [P00-backend+backend/packages/txt2crs] **One process is mandatory**: no
  queue, replica, or parallel worker is introduced.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**:
  generation and formatting remain script-owned.
- [P01-backend/packages/txt2crs] **Persist exact accepted identity**: the
  complete request/profile and canonical hash drive retries and restart.
- [P01-backend/packages/txt2crs] **Construct public allowlists**: accepted
  response fields are created explicitly rather than filtered.
- [P02-backend] **Operational logs use field allowlists**: route events contain
  finite codes and opaque identity only.

### Behavioral Quality Focus

Checklist active: Yes
Top behavioral risks for this session:

- Duplicate clicks or transport retries accidentally reserve or execute paid
  work twice.
- Oversize or malicious multipart input reaches framework spooling, archive
  expansion, persistence, or provider work before rejection.
- Unready, policy-refused, quota-refused, or exception paths leak learner
  values or leave open spool/resources.

---

## 9. Testing Strategy

### Unit Tests

- Strict request/response models cover every boundary, discriminant,
  unknown-field, normalization, URL scheme, consent, age, and
  idempotency-key case.
- Body middleware covers declared length, chunk overflow, disconnect, normal
  pass-through, unrelated routes, and RFC 9457 response shape.
- Upload tests use synthetic minimal PDF/ZIP bytes for valid structure,
  signature mismatch, unsafe name, traversal, encryption, macro, missing
  content type, too many entries, expanded-byte overflow, truncation, and
  exact-limit behavior.
- Submission tests use recording public facade/readiness/worker protocols to
  assert request mapping, call order, safe translation, and no early nudge.
- Engine tests prove allowed policy calls the durable service and refused
  policy calls it zero times.

### Integration Tests

- Route tests exercise real authentication dependencies plus injected
  course-system services for both media routes, authorization ordering,
  headers, errors, and rate limits.
- Acceptance uses temporary real deterministic engine SQLite/artifact state
  to prove exact durable request persistence, replay, conflict, quota, and
  owner-scoped key namespaces.
- Client-contract tests inspect OpenAPI security, schema discriminants,
  multipart form, header pattern, 202 response, and stable operation IDs.

### Runtime Verification

- Start an isolated local TestClient with a deterministic facade, submit a
  prompt, reopen the underlying job state through a replacement facade, and
  confirm the same key returns the original job.
- Submit safe synthetic PDF/DOCX/PPTX samples at the HTTP boundary and confirm
  accepted bytes match the package request while the framework spool is
  closed.
- Disable cached readiness and public signup separately and confirm no durable
  job/user write occurs.

### Edge Cases

- Content-Length absent, invalid, duplicated, or smaller than actual chunks.
- Exactly-at-limit input, one-byte-over input, whitespace-only strings,
  repeated learning goals, Unicode byte/character differences, and URL
  fragments/credentials.
- Same key across two users, same key with normalized-equivalent whitespace,
  and same key with one preference/file byte changed.
- ZIP64-like large declared sizes, duplicate archive members, nested paths,
  compression ratio abuse, encrypted flags, macro-enabled types, and corrupt
  central directory.
- Readiness changes after validation, worker closes after commit, client
  disconnects during upload, and package exceptions with private context.

---

## 10. Dependencies

### Other Sessions

- Depends on: all five completed Phase 02 sessions and the Phase 01 public
  engine boundary.
- Depended by: `phase03-session02-owner-scoped-job-results-and-recovery`,
  `phase03-session03-account-purge-and-donor-retirement`, and all Phase 04
  learner sessions.

---

## Next Steps

Run the `implement` workflow step to begin implementation.
