# Session Specification

**Session ID**: `phase01-session02-safe-queries-and-artifact-access`
**Phase**: 01 - Engine Application Boundary
**Status**: Validated
**Created**: 2026-07-19
**Base Commit**: 2944662447bcea279705e3b06fba17216267e72d
**Package**: backend/packages/txt2crs
**Package Stack**: Python 3.14, Pydantic v2, SQLite

---

## 1. Session Overview

This session gives the application shell owner-safe read operations for durable
generation jobs and rendered artifacts. Public job state is projected into new
allowlisted contracts; callers never receive the stored generation request,
checkpoint JSON, normalized input, evidence excerpts, provider records,
budget counters, or filesystem paths.

It follows durable request recovery because safe projections need one coherent
owner-scoped job/request/checkpoint snapshot. It precedes the final facade
session because that facade must compose established query and streaming
contracts rather than reach into SQLite or the private artifact layout.

The existing filesystem artifact store remains the only production storage
path. It gains metadata-only manifest reads and a context-managed artifact
stream that opens, bounds, hashes, rewinds, and serves one regular file through
the same descriptor. Existing whole-bundle recovery remains compatible.

---

## 2. Objectives

1. Define bounded public job, progress, input, source, conflict, failure, and
   artifact-availability contracts.
2. Project one owner-scoped durable snapshot without serializing private
   request, checkpoint, provider, usage, evidence, or path data.
3. Return a verified metadata-only artifact manifest with stable artifact IDs,
   deliverable kinds, formats, safe names, media types, sizes, and hashes.
4. Stream one authorized artifact in bounded chunks from the same verified
   descriptor with deterministic cleanup on every exit path.

---

## 3. Prerequisites

### Required Sessions

- [x] `phase01-session01-durable-requests-and-recovery` - Provides atomic
  request/job admission, exact owner recovery, and lock-scoped latest
  checkpoint snapshots.

### Required Tools Or Knowledge

- Existing `SqliteJobStore`, `JobService`, cumulative `PipelineCheckpoint`,
  and private filesystem artifact-store behavior.
- Pydantic v2 allowlist contracts, context managers, `os.open`,
  `O_NOFOLLOW`, `fstat`, bounded hashing, and descriptor lifecycle.
- Existing rendering names for course, review-pack, assessment, and answer-key
  artifacts in HTML, Markdown, PDF, and DOCX.

### Environment Requirements

- Run package commands from `backend/packages/txt2crs/`.
- Default verification is credential-free, network-free, and shell-free.
- A POSIX filesystem is available for symlink and descriptor integrity tests.

---

## 4. Scope

### In Scope (MVP)

- An authorized caller can read one `PublicJobSnapshot` - the package loads a
  coherent owner-scoped resume state and creates a new explicit allowlist
  object.
- A snapshot can show bounded job status/timestamps, accepted stage and units,
  safe input display data, extraction warnings, a safe failure, course title,
  public source summaries, conflict summaries, and artifact availability.
- A caller can read one owner-scoped `ArtifactManifest` without opening or
  loading all artifact bodies.
- A caller can select one stable canonical artifact ID and receive bounded
  chunks only inside a package-owned context manager.
- Manifest and stream reads validate owner scope, directory confinement,
  regular-file type, symlink rejection, safe metadata, total/item byte limits,
  exact size, SHA-256 integrity, and the expected directory contents.
- Missing jobs, missing artifact sets, missing artifact IDs, and wrong owners
  use one typed not-found boundary without revealing which condition occurred.
- Existing whole-bundle `get`, idempotent `save`, delete, and retention purge
  behavior remains supported.

### Out Of Scope (Deferred)

- FastAPI response objects, HTTP headers, content disposition, range requests,
  and disconnect plumbing - Phase 03 owns HTTP delivery.
- Browser result cards, downloads, previews, and learner-facing progress UI -
  Phase 04 owns those product surfaces.
- Input routing, preference resolution, and post-ingestion policy - Session 03
  owns preparation behavior.
- Final application facade/factories and owner-wide purge - Session 05 owns
  lifecycle composition.

---

## 5. Technical Approach

### Architecture

Add `txt2crs.jobs.public_queries` as the public projection boundary. Its strict
contracts contain only fields explicitly permitted by implementation-plan
section 5.3. `project_public_job_snapshot` receives the internal resume state
and optional public artifact manifest, validates the cumulative checkpoint as
a `PipelineCheckpoint`, and copies only safe derived values into new models.
Any incompatible checkpoint becomes a context-free typed projection error.

Progress uses the accepted checkpoint sequence and the existing pipeline rule
of eight fixed checkpoints plus one checkpoint per planned module. Counts are
clamped to the existing checkpoint contract maximum of 108. Accepted jobs
without checkpoints start at zero; terminal completion reports the known total
only when the final accepted checkpoint exists.

Input display never copies raw input. File-based requests use only a sanitized
basename; prompt/text inputs use a fixed label. Extraction warnings, titles,
publisher names, and conflicts pass through the existing public-text sanitizer
and fixed list/item limits. Source URLs accept only parseable HTTP(S) URLs
without user information and omit query strings and fragments so tokens cannot
be reflected. Safe failures use a package-owned code/message map; unknown
private codes collapse to `generation_failed`.

Extend `FilesystemPrivateArtifactStore` with public artifact metadata
contracts, `get_manifest`, and `open_artifact`. Keep the public contracts in
`artifact_queries`, confined descriptor reads in `artifact_reader`, and atomic
write/retention lifecycle in `artifact_store` so each module remains cohesive.
The metadata-only path parses the bounded manifest, validates every descriptor
and expected directory entry, but does not open artifact bodies. Canonical
renderer artifact IDs map through an exact allowlist to deliverable and format
enums.

`open_artifact` resolves one validated descriptor, opens it once with
`O_NOFOLLOW` when available, verifies a regular file and the declared size,
hashes bounded bytes, rechecks descriptor identity/stat data, seeks that same
descriptor to zero, and yields fixed-size chunks. `try/finally` closes the
descriptor after normal exhaustion, early context exit, consumer error, or
integrity failure. The package never returns a path.

`JobService` remains the application boundary. Its public snapshot method
authorizes the durable job before treating a missing artifact set as
unavailable. Manifest and stream methods delegate to the artifact store, whose
owner/job hash lookup is the boundary closest to the bytes. The in-memory
store implements the same protocol for deterministic facade tests.

### Design Patterns

- Allowlist projection: Construct a new public contract instead of filtering
  serialized private state.
- Repository/service boundary: Keep SQLite and filesystem ownership checks
  behind package methods.
- Stable identifier map: Translate only the renderer's canonical artifact
  names into public deliverable and format metadata.
- Metadata/body separation: Parse and verify manifests without eagerly loading
  artifact bodies.
- Scoped resource: Use a context manager and one descriptor for validation,
  rewind, streaming, and cleanup.
- Indistinguishable not found: Reuse one typed error for missing and
  unauthorized resource selection.

---

## 6. Deliverables

### Files To Create

| File | Purpose | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/jobs/public_queries.py` | Strict public snapshot models, bounded projection, safe failure mapping, and URL/text sanitization | ~300 |
| `backend/packages/txt2crs/src/txt2crs/jobs/artifact_queries.py` | Strict path-free artifact metadata contracts, stable artifact-ID mapping, and deterministic manifest projection | ~200 |
| `backend/packages/txt2crs/src/txt2crs/jobs/artifact_reader.py` | Confined metadata-only manifest validation and one-descriptor streaming | ~480 |
| `backend/packages/txt2crs/tests/unit/test_public_job_queries.py` | Projection allowlist, bounds, malformed checkpoint, safe URL/failure, and privacy tests | ~300 |
| `backend/packages/txt2crs/tests/integration/test_public_job_query_service.py` | Real SQLite plus artifact-store owner snapshot/manifest/stream tests | ~260 |

### Files To Modify

| File | Changes | Est. Lines |
|------|---------|------------|
| `backend/packages/txt2crs/src/txt2crs/jobs/artifact_store.py` | Delegate verified reads while retaining atomic save, delete, retention, and private directory lifecycle | ~100 |
| `backend/packages/txt2crs/src/txt2crs/jobs/service.py` | Extend the artifact protocol/in-memory store and expose owner-safe query methods | ~130 |
| `backend/packages/txt2crs/src/txt2crs/jobs/__init__.py` | Export supported public job and artifact query contracts | ~25 |
| `backend/packages/txt2crs/tests/factories.py` | Add a reusable cumulative checkpoint fixture for projection tests | ~100 |
| `backend/packages/txt2crs/tests/unit/test_filesystem_artifact_store.py` | Add manifest, streaming, mutation, symlink, corruption, cleanup, and compatibility coverage | ~320 |
| `backend/packages/txt2crs/tests/unit/test_job_service.py` | Add in-memory public snapshot and artifact query delegation coverage | ~140 |

---

## 7. Success Criteria

### Functional Requirements

- [x] Public snapshot JSON contains no raw request value, normalized input,
  evidence excerpt, prompt, provider/thread/turn ID, usage/token data, private
  diagnostic, request hash, checkpoint JSON, or filesystem path.
- [x] Progress, warning, source, conflict, title, file-name, and failure fields
  are bounded and derived only from accepted allowlisted state.
- [x] Unknown failure codes and malformed private checkpoints produce generic,
  context-free package results rather than reflecting private values.
- [x] Manifest reads return canonical metadata for every stored artifact
  without opening all artifact body files.
- [x] Stream reads open one authorized regular file, verify exact size/hash,
  rewind the same descriptor, emit chunks no larger than the package limit,
  and close on exhaustion, early exit, or consumer error.
- [x] Symlinks, traversal metadata, extra/missing files, descriptor swaps,
  mid-validation mutation, oversized data, bad hashes, and unsafe media/file
  metadata fail closed.
- [x] Missing and wrong-owner job/artifact/ID requests raise the same public
  not-found type and message.
- [x] Existing full-bundle restore, save replay, delete, and retention tests
  remain green.

### Testing Requirements

- [x] Failing projection, filesystem, and service integration tests are
  written and observed before production implementation.
- [x] Focused query/artifact/service tests pass without credentials or network.
- [x] The complete engine suite passes with the explicit live Codex test still
  gated.
- [x] The built wheel contains the new public query module and artifact
  contracts.

### Non-Functional Requirements

- [x] No SQLite row, checkpoint dictionary, raw request, `Path`, open file
  object, or filesystem descriptor escapes the supported package contract.
- [x] Manifest and stream work is bounded by configured job bytes, fixed list
  limits, and fixed chunk size.
- [x] Owner authorization occurs at the durable job and private byte
  boundaries; missing and unauthorized states remain indistinguishable.
- [x] Every opened file is closed through deterministic context management.

### Quality Gates

- [x] All session-authored files are ASCII-encoded.
- [x] Unix LF line endings are preserved.
- [x] Code has complete types, descriptive names, and intern-friendly comments
  around allowlists, path confinement, hashing, and descriptor cleanup.
- [x] Ruff formatting/lint, strict mypy, pytest, and package build pass from
  the engine package root.

---

## 8. Implementation Notes

### Working Assumptions

- Public artifact IDs are the existing canonical renderer dictionary keys:
  the renderer already emits the complete deliverable/format matrix and the
  filesystem manifest persists those keys, so no new database ID is needed.
- Snapshot source summaries come from the latest accepted cumulative
  checkpoint's frozen evidence set (or approved course when present): those
  records are the canonical public source metadata and avoid unaccepted
  streamed provider data.
- Artifact availability is false when an authorized durable job has no
  published manifest. Authorization is checked first, so this does not turn a
  wrong-owner request into an existence oracle.

### Conflict Resolutions

- The existing `PrivateArtifactStore` protocol exposes only `save`, while its
  concrete stores have ad hoc whole-bundle `get` methods. The adopted plan
  requires manifest and single-artifact reads through the package boundary, so
  this session expands the protocol and both implementations instead of
  letting the shell depend on a concrete store.
- Existing manifest hashes are unlabeled hexadecimal strings, while public
  domain hashes use `sha256:<hex>`. Disk compatibility wins for the immutable
  manifest schema; the public metadata projection adds the algorithm label
  without rewriting stored manifests.
- Source URLs may contain private query values even when a source is otherwise
  displayable. The privacy requirement wins over exact URL round-trip in the
  snapshot, so public projection strips queries/fragments and rejects
  credential-bearing or non-HTTP(S) URLs.

### Key Considerations

- Verify a job owner before probing artifact availability in snapshots.
- Do not catch an artifact integrity error and silently report unavailable;
  only a genuine not-found result means no published artifact set.
- Validate complete manifest topology without opening artifact bodies, then
  validate only the selected body for streaming.
- Keep the descriptor open between hashing, rewind, and every yielded chunk.

### Potential Challenges

- Checkpoint artifacts contain deeply nested private data: validate once, then
  copy only typed leaf values into fresh public contracts.
- File replacement races can target path-based validation: open once and use
  `fstat`, hashing, rewind, and reads on that descriptor.
- The filesystem store is already moderately sized: keep public job projection
  in its own module and keep artifact-specific validation cohesive in the
  storage module.

### Relevant Considerations

- [P00-backend+backend/packages/txt2crs] **Private state needs lifecycle
  coverage**: owner-scoped metadata and streams remain inside the same private
  state root and do not expose paths.
- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  all job and artifact reads are package methods; later routes do not query
  SQLite or open files.
- [P00] **Layer static and runtime contracts**: pair serialized allowlist tests
  with real SQLite restart and filesystem descriptor/security tests.
- [P00-backend/packages/txt2crs] **Run engine tools from its package root**:
  use the package's independent Ruff, mypy, pytest, and build configuration.

### Behavioral Quality Focus

Checklist active: Yes

Top behavioral risks for this session:

- A convenient model dump could expose private checkpoint or request content.
- A wrong-owner or missing-artifact branch could become a resource-existence
  oracle.
- A stream could validate one path and serve a replaced file, exceed bounds,
  or leak a descriptor after early exit.

---

## 9. Testing Strategy

### Unit Tests

- Construct private checkpoints containing raw input, excerpts, provider IDs,
  token usage, secret-shaped URLs, paths, long warnings, conflicts, and
  arbitrary failure codes; assert the serialized public snapshot contains only
  expected bounded values.
- Exercise accepted/no-checkpoint, each meaningful checkpoint family, failed,
  cancelled, completed, and incompatible-checkpoint projections.
- Verify manifest metadata, canonical artifact mapping, no-body manifest reads,
  hash/size checks, chunk bounds, same-descriptor replacement behavior, and
  cleanup after partial consumption and raised exceptions.

### Integration Tests

- Submit and checkpoint a request in real SQLite, publish real filesystem
  artifacts, close/reopen the job store, and query the snapshot, manifest, and
  streamed bytes through `JobService`.
- Repeat job, manifest, and stream queries with a foreign owner and missing IDs
  to prove indistinguishable not-found behavior.

### Runtime Verification

- Build the wheel and import the new public contracts from an installed
  distribution.
- Run the complete deterministic engine validation script and verify the live
  Codex compatibility test remains explicitly skipped without credentials.

### Edge Cases

- Empty artifact sets, unknown stored artifact IDs, duplicate safe file names,
  unsafe basenames/media types, invalid timestamps, and oversized manifests.
- Symlinked job directories, manifests, or artifact files; non-regular files;
  extra/missing files; bytes changed before or during verification.
- Query strings containing tokens, URL user information, private diagnostic
  strings, overlong warnings/conflicts, and unknown failure codes.

---

## 10. Dependencies

### Other Sessions

- Depends on: `phase01-session01-durable-requests-and-recovery`
- Depended by: `phase01-session05-public-facade-and-owner-lifecycle`, Phase 03
  durable job/artifact APIs, and Phase 04 learner results/progress UI.

---

## Next Steps

Run the `implement` workflow step to begin implementation.
