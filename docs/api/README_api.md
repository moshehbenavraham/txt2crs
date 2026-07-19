# txt2crs API

The current FastAPI shell exposes authentication, user administration,
durable course-job submission, cached course-system readiness, privileged
device authentication, temporary item CRUD, email testing, and health.

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

Both routes require an owner-scoped retry key:

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
budgets, policy reasoning, or filesystem details. The status URL is reserved
for the owner-scoped job-read route delivered in Phase 03 Session 02.

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
