# txt2crs API

The current FastAPI shell exposes authentication, user administration,
cached course-system readiness, privileged device authentication, temporary
item CRUD, email testing, and health. Course-generation and jobs routes are
not implemented yet.

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

Obtain a token with `POST /api/v1/login/access-token`. Login, signup, password
recovery/reset, OpenAPI, and health are public; administration and test-email
operations enforce their route-specific authorization.

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
and 500 safe internal failure.

## Generate the Frontend Client

```bash
./scripts/generate-client.sh
git diff -- frontend/openapi.json frontend/src/client
```

Generated files are formatter-owned and must not be edited manually.
