# txt2crs API

The current FastAPI shell exposes authentication, user administration,
durable course-job submission and owner-scoped results, cached course-system
readiness, privileged device authentication, temporary item CRUD, email
testing, and health.

## OpenAPI

- Swagger UI: <http://localhost:8012/docs>
- ReDoc: <http://localhost:8012/redoc>
- JSON: <http://localhost:8012/api/v1/openapi.json>

The OpenAPI document is the endpoint source of truth and generates the
frontend client through `./scripts/generate-client.sh`.

## Authentication

Protected endpoints require:

```http
Authorization: Bearer <token>
```

Obtain a token with `POST /api/v1/login/access-token`. Login, password
recovery/reset, OpenAPI, and health are public. Signup is public only when its
local-development flag is enabled; administration, course jobs, and
test-email operations enforce their route-specific authorization.

## Endpoint Groups

### Authentication

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/login/access-token` | Exchange credentials for an access token |
| POST | `/api/v1/login/test-token` | Validate the current token |
| POST | `/api/v1/password-recovery` | Request password recovery |
| POST | `/api/v1/password-recovery-html-content/{email}` | Superuser recovery-email preview |
| POST | `/api/v1/reset-password/` | Reset a password with a recovery token |

### Users

| Method | Path | Purpose |
|--------|------|---------|
| GET, POST | `/api/v1/users/` | List/create users as a superuser |
| GET, PATCH, DELETE | `/api/v1/users/me` | Read/update/delete the current account |
| PATCH | `/api/v1/users/me/password` | Change the current password |
| POST | `/api/v1/users/signup` | Register a user when public signup is enabled |
| GET, PATCH, DELETE | `/api/v1/users/{user_id}` | Superuser user administration |

### Temporary Items

| Method | Path | Purpose |
|--------|------|---------|
| GET, POST | `/api/v1/items/` | List/create current-user items |
| GET, PUT, DELETE | `/api/v1/items/{id}` | Read/update/delete one owned item |

The donor domain remains only until durable jobs acceptance coverage protects
its Phase 03 replacement.

### Course Jobs

| Method | Path | Authorization | Purpose |
|--------|------|---------------|---------|
| POST | `/api/v1/jobs` | Authenticated | Durably accept one prompt, pasted-text, URL, or YouTube course request |
| POST | `/api/v1/jobs/upload` | Authenticated | Durably accept one PDF, DOCX, or PPTX course request |
| GET | `/api/v1/jobs/{job_id}` | Authenticated owner | Read one bounded, revisioned status/result projection |
| GET | `/api/v1/jobs/{job_id}/artifacts` | Authenticated owner | Read the verified, path-free artifact manifest |
| GET | `/api/v1/jobs/{job_id}/artifacts/{artifact_id}` | Authenticated owner | Download one reauthorized and integrity-verified artifact |

Both submission routes require an owner-scoped retry key:

```http
Idempotency-Key: course-request-018
```

The key must contain 1-128 ASCII letters, digits, periods, underscores,
colons, or hyphens. Reuse it only for the same exact request. An exact replay
returns the existing durable result; reusing it with different request
content returns `JOB_7003`.

The JSON route accepts exactly one discriminated input and the shared learner
preferences. Unknown fields and coercive values are rejected:

```json
{
  "input": {
    "type": "prompt",
    "value": "Teach me the foundations of marine biology"
  },
  "preferences": {
    "level": "beginner",
    "audience": "Curious adult learners",
    "prior_knowledge": null,
    "learning_goals": [
      "Explain how marine food webs transfer energy"
    ],
    "language": "English"
  },
  "consent_to_ai_processing": true,
  "learner_age_group": "adult"
}
```

`input.type` is exactly `prompt`, `text`, `url`, or `youtube`. Prompt values
are 3-10,000 characters, pasted text is 1-200,000 characters, and URL values
are 9-2,048 characters. URLs must be absolute HTTPS without embedded
credentials or fragments; the reusable engine performs the authoritative
host and DNS safety checks. Learning level is `auto`, `beginner`,
`intermediate`, `advanced`, or `mixed`; age group is `minor`, `adult`, or
`not_provided`. Consent must be the JSON boolean `true`. A request can include
at most 10 unique learning goals.

The upload route requires `multipart/form-data` with exactly two parts:

- `metadata`: at most 262,144 UTF-8 bytes of strict JSON containing
  `preferences`, `consent_to_ai_processing`, and `learner_age_group`.
- `file`: one `.pdf`, `.docx`, or `.pptx` whose declared media type, filename,
  magic bytes, and container structure agree.

The default file limit is 20 MiB and the route-level framed-body cap is
21,299,200 bytes. PDFs must be readable, unencrypted, and no more than 200
pages. OOXML archives may contain at most 10,000 entries and 50 MiB of
expanded content; duplicate/traversal entries, encryption, macros, ActiveX,
embeddings, external links, and malformed required parts are rejected.
Uploads are read in bounded 64 KiB chunks and closed on every success,
validation, cancellation, and failure path. The shell does not extract course
content; validated bytes cross the package boundary for canonical processing.

Success is returned only after package policy, admission, and durable commit:

```http
HTTP/1.1 202 Accepted
Location: /api/v1/jobs/job_018
Cache-Control: private, no-store
Pragma: no-cache
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
```

```json
{
  "schema_version": "1.0",
  "job_id": "job_018",
  "status": "accepted",
  "revision": 0,
  "status_url": "/api/v1/jobs/job_018"
}
```

The response never includes the owner, retry key, input, provider, model,
budgets, policy reasoning, or filesystem details.

#### Status and result polling

`GET /api/v1/jobs/{job_id}` returns the current durable revision and a strict
allowlist. Clients should poll the `status_url` from the accepted response and
compare `revision` values; this P0 contract deliberately has no ETag,
conditional request, or `304 Not Modified` behavior. Every successful read
uses `Cache-Control: private, no-store`, `Pragma: no-cache`,
`X-Content-Type-Options: nosniff`, and `Referrer-Policy: no-referrer`.

The response contains:

- one of the nine durable statuses and fixed browser-safe progress copy;
- `completed_units` and a nullable `total_units`, each bounded to 0-108. The
  total remains `null` until the accepted course plan establishes it;
- input type, a safe display name, exact UTF-8/source byte count, at most 20
  extraction warnings, and an explicit warning-truncation flag; never the
  source body or URL;
- either a complete result summary or `null`. A summary has a bounded title,
  resolved audience/level/language, 1-100 objectives, 1-100 modules, at most
  12 bibliographic sources, at most 20 conflicts, and explicit truncation
  flags;
- a safe failure code/message or `null`; and
- artifact availability, a 0-16 count, and the manifest URL only after
  private publication succeeds.

The owner check happens inside the package query. A nonexistent job and a job
owned by another user both return the same `JOB_7001` `404` Problem Details
response, so the route cannot be used as an ownership oracle. Path
identifiers are 1-128 characters and permit only ASCII letters, digits,
periods, underscores, colons, and hyphens after an alphanumeric first
character.

#### Artifact manifest and downloads

`GET /api/v1/jobs/{job_id}/artifacts` verifies the private artifact topology
and stored metadata before returning it. The manifest groups the four
canonical educational products (`course`, `review_pack`, `assessment`, and
`answer_key`) in stable order. Each group contains up to four canonical
formats: `html`, `markdown`, `pdf`, and `docx`.

Each artifact entry contains only:

- its stable identifier and format;
- a safe display filename and media type;
- byte length and `sha256:<64 lowercase hex digits>` content hash; and
- an owner-scoped download URL.

Private storage paths never cross the API boundary. The manifest is also
private/no-store and has no ETag behavior.

The download route independently reauthorizes both the job and artifact, then
opens and integrity-verifies the existing private descriptor before sending
headers. Its response includes the artifact's exact `Content-Type` and
`Content-Length`, an ASCII RFC 5987 `Content-Disposition: attachment` value,
and the same no-store/privacy headers. The response owns the entered stream
and closes it exactly once on completion, client disconnect, iterator error,
send error, or construction failure. Generated clients expose HTML and
Markdown downloads as text and PDF and DOCX downloads as binary `Blob | File`
content, matching their exact response media types. Missing artifact IDs use
the same `JOB_7001` response as missing or foreign jobs.

An integrity or projection inconsistency fails closed as `SYSTEM_6002` with a
safe `500` Problem Details response; no filename, hash, source value, artifact
bytes, private path, or underlying exception is returned.

#### Restart and replay behavior

The serial worker discovers previously accepted jobs when a replacement
process starts; it does not depend on an in-memory wake event. Active work
resumes from the last accepted package checkpoint using the exact durable
request and execution profile. A replacement after final validation replays
only deterministic rendering, and a replacement during delivery
deterministically rerenders and republishes the final validated bundle without
another model turn. Completed manifests and bytes remain identical after the
application is reopened.

### Operations

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/utils/health/` | Readiness with PostgreSQL status and version |
| GET | `/api/v1/utils/health-check/` | Process liveness |
| POST | `/api/v1/utils/test-email/` | Superuser email-delivery test |

### Course System

| Method | Path | Authorization | Purpose |
|--------|------|---------------|---------|
| GET | `/api/v1/system/readiness` | Authenticated | Read the latest coarse cached dependency/worker/admission state |
| POST | `/api/v1/system/auth/start` | Superuser | Start or replay one runtime-exclusive ChatGPT device-code attempt |
| GET | `/api/v1/system/auth/status` | Superuser | Poll the cached browser-safe challenge or terminal state |

Readiness and authentication-status GET requests are cache reads. They do not
start Codex, MCP, credential refresh, SQLite, artifact, or provider work.
Device start returns only the validated `auth.openai.com` HTTPS URL, bounded
short code, finite state, and safe message. It never returns OAuth tokens,
account identity, provider payloads, `CODEX_HOME`, paths, or ports.

If browser setup is unavailable, an operator can run the package-owned CLI
recovery command from `backend/packages/txt2crs/`:

```bash
uv run --package txt2crs txt2crs-system-auth
```

The separately deployed frontend exposes Nginx `GET /health`; it is not part
of FastAPI OpenAPI.

## Error Contract

Application errors use RFC 9457 Problem Details with content type
`application/problem+json`. Stable fields include:

```json
{
  "type": "https://txt2crs.dev/problems/example",
  "title": "Example error",
  "status": 400,
  "detail": "Safe user-facing detail",
  "code": "STABLE_ERROR_CODE",
  "trace_id": "correlation-id"
}
```

Route code raises `AppException` with an `app.core.constants.ErrorCode`.
Validation failures and rate-limit failures are normalized through the same
central handler family. Do not expose provider payloads, stack traces, source
content, tokens, or filesystem paths in errors.

Common HTTP statuses include 200/201/202 success, 400 invalid request, 401
authentication required, 403 authorization denied, 404 missing or
owner-hidden resource, 409 conflict, 422 validation failure, 429 rate limit,
and 500 safe internal failure. Submission-specific stable errors are:

| Code | HTTP | Meaning |
|------|------|---------|
| `SYSTEM_6002` | 500 | A private engine result failed safe projection or integrity validation |
| `JOB_7001` | 404 | The requested job or owner-visible artifact was not found |
| `SYSTEM_6001` | 503 | Cached course-system readiness does not permit admission |
| `JOB_7002` | 429 | Owner or global admission capacity is exhausted |
| `JOB_7003` | 409 | The retry key was reused for different request content |
| `JOB_7004` | 409 | The durable job conflicts with its expected state |
| `JOB_7005` | 413 | The upload or framed request exceeds a configured bound |
| `JOB_7006` | 415 | The uploaded media type or container is unsupported |
| `JOB_7007` | 422 | Package-owned preparation policy rejected the request |

Malformed bodies use the shared `VALIDATION_4001` contract and finite endpoint
rate limiting uses `RATE_5001`. Authentication errors are returned before job
submission work. Rejections do not start provider or worker execution, and
safe errors never echo source content, filenames, URLs, policy internals, or
provider payloads.

## Generate the Frontend Client

```bash
./scripts/generate-client.sh
git diff -- frontend/openapi.json frontend/src/client
```

Generated files are formatter-owned and must not be edited manually.
