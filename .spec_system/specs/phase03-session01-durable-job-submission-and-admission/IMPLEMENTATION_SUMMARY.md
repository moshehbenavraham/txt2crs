# Implementation Summary

**Session ID**: `phase03-session01-durable-job-submission-and-admission`
**Package**: `backend`
**Completed**: 2026-07-20
**Duration**: 1.1 hours

---

## Overview

Session 01 opened the authenticated learner write path for durable course
jobs. Strict JSON accepts prompt, pasted text, URL, and YouTube intent.
Strict multipart accepts one bounded PDF, DOCX, or PPTX plus reviewed metadata.
The shell validates HTTP framing and upload structure, maps only reviewed
values into public engine contracts, checks cached readiness, and delegates
policy, canonical hashing, idempotency, admission, and persistence to the
`txt2crs` facade.

A successful request returns a private `202 Accepted` acknowledgement only
after the exact request and reservation are durable. Exact retries reuse the
original job; changed requests conflict. The serial worker receives only a
post-commit, non-terminal latency hint. Local public signup is now an explicit
disabled-by-default opt-in.

---

## Deliverables

### Files Created

| File or Area | Purpose | Lines |
|--------------|---------|-------|
| `backend/app/api/routes/jobs.py` | Authenticated JSON and multipart submission routes | 201 |
| `backend/app/schemas/jobs.py` | Strict request, metadata, retry-key, and accepted-response contracts | 268 |
| `backend/app/services/txt2crs_submission.py` | Thin readiness/facade/worker composition boundary | 257 |
| `backend/app/services/txt2crs_uploads.py` | Bounded PDF and OOXML transport validation | 330 |
| Seven new shell and acceptance test modules | Schema, framing, upload, service, route, dependency, and durable acceptance coverage | 1,948 |
| Phase 03 PRD set | Reconciled three-session durable API delivery plan | 461 |
| Session workflow artifacts | Spec, tasks, implementation notes, review, security, validation, and summary | 2,119 before this summary |

### Files Modified

| Area | Changes |
|------|---------|
| Engine facade/factories/exports | Made package preflight authoritative and exposed the shared finite admission reservation |
| Shell configuration/composition/errors | Added local signup policy, upload body middleware, rate limit, error mappings, dependencies, and jobs router |
| Existing engine/shell tests | Protected preflight ordering, exports, settings, framing, errors, signup, and generated contracts |
| Generated frontend client | Added strict authenticated job submission operations through the repository generator |
| Public documentation | Documented inputs, limits, errors, cleanup, privacy, signup mode, architecture, and current status |
| Apex state and Phase 03 PRD | Marked Session 01 complete and Phase 03 at 1/3 |
| `backend/pyproject.toml` and `backend/uv.lock` | Advanced the backend shell package from 0.3.3 to 0.3.4 |

---

## Technical Decisions

1. **Pure ASGI framing guard**: reject malformed or declared-oversize
   multipart requests before framework parsing while still counting actual
   chunks for missing or dishonest lengths.
2. **Transport/domain separation**: validate filename, MIME, magic, PDF, and
   OOXML container safety in the shell; keep extraction, URL policy, content
   policy, generation, and persistence in the engine.
3. **Package-owned preflight**: enforce consent and content policy inside the
   public facade so no shell caller can bypass it.
4. **Atomic package admission**: reuse canonical owner/key/request hashing and
   one SQLite transaction for replay, conflict, quota, reservation, and
   durable identity.
5. **Stable POST acknowledgement**: return the initial accepted revision even
   when an idempotent replay finds a terminal job; Session 02 owns current
   status reads.
6. **Post-commit worker hint**: never wake before durable success and skip
   completed, failed, or cancelled replays.
7. **Generated client ownership**: update TypeScript only through the checked
   in OpenAPI generation script and require byte-stable regeneration.

---

## Test Results

| Metric | Value |
|--------|-------|
| Engine | 467 passed; 1 live-gated skip |
| Backend shell and acceptance | 429 passed |
| Complete deterministic passed | 896 |
| Failed | 0 |
| Frontend lint/type/build | PASS; 2,204 modules built |
| Engine/shell static types and format | PASS |
| Generated client contract | 5 passed; byte-stable regeneration |
| Repository pre-commit | PASS |
| Coverage | Not enabled by authoritative project commands |

---

## Code Review Repairs

Formal review resolved five Medium and two Low findings:

1. Enforced the decimal-only HTTP `Content-Length` grammar.
2. Translated invalid metadata Unicode to a context-free validation failure.
3. Rejected terminal dot traversal segments in OOXML entry names.
4. Stopped worker wakeups for terminal idempotent replays.
5. Kept replayed POST acknowledgements internally consistent at revision 0.
6. Synchronized signup OpenAPI and public Phase 03 status documentation.
7. Replaced a private acceptance import and imprecise helper return type.

All repairs have focused red-then-green regressions or contract checks.

---

## Security And Privacy

- Authentication precedes learner-body processing and every accepted response
  uses an explicit field allowlist with private/no-store headers.
- Reads, body chunks, upload bytes, PDF pages, archive entries, expansion
  totals, metadata, names, and messages are finite.
- Source content, URLs, retry keys, hashes, filenames, archive names, provider
  details, and paths are absent from responses and structured events.
- Provider processing requires literal consent and package preflight before
  persistence or worker/provider execution.
- The engine already owns `purge_owner`; Session 03 will coordinate that
  operation with both PostgreSQL account-deletion routes.

---

## Lessons Learned

1. Python's integer grammar is too permissive for HTTP framing; validate the
   protocol grammar before conversion.
2. OOXML safety must cover terminal as well as intermediate path segments.
3. Idempotent replay can return a later durable state, so POST
   acknowledgement and worker notification semantics must be explicit.
4. A route-level `UploadFile` loop cannot enforce a pre-multipart body cap;
   the ASGI receive boundary is the correct enforcement point.

---

## Future Considerations

1. Session 02 should expose owner-scoped current job/result projections,
   artifact manifests, and integrity-checked streaming without private paths.
2. Restart acceptance should prove accepted and active checkpoints resume from
   stored identity and delivery replay does not repeat model work.
3. Session 03 must establish a worker barrier and purge engine state before
   either PostgreSQL identity deletion path.
4. The temporary Items domain remains until Session 03 removes its API,
   model, CRUD, tests, docs, MCP tools, migration schema, and generated client.

---

## Session Statistics

- **Tasks**: 25 completed
- **Files Created**: 22 including workflow reports and this summary
- **Files Modified**: 53
- **Tests Added**: 136 deterministic cases relative to the prior session
- **Blockers**: 1 resolved (isolated PostgreSQL replaced an occupied host port)
