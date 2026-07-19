# Environment-Specific Behavior

> Runtime differences selected by the required `ENVIRONMENT` setting.

This page documents behavior that actually changes in application code when
`ENVIRONMENT` is `local`, `staging`, or `production`. Only the `local` profile
is deployed in the current project scope; the other values are hardened
runtime profiles retained for validation and possible future requirements.
For the complete
environment-variable catalog, see [Configuration](CONFIGURATION.md). For local
service addresses and Docker workflow, see [Development](development.md). For
deployment ownership and supported paths, see
[Deployment policy](deployment-policy.md).

## Sources of Truth

When documentation and implementation disagree, use these files as the
authoritative references:

- [`backend/app/core/config.py`](../backend/app/core/config.py) defines allowed
  environments, defaults, computed settings, and startup validation.
- [`backend/app/core/rate_limit.py`](../backend/app/core/rate_limit.py) controls
  rate-limiter activation and limits.
- [`backend/app/main.py`](../backend/app/main.py) configures logging, Sentry,
  middleware, and application startup.
- [`.env.example`](../.env.example) provides the repository's local Docker
  configuration template.
- [`docker-compose.override.yml`](../docker-compose.override.yml) defines local
  host ports and local-only service overrides.

## Selecting an Environment

`ENVIRONMENT` is required and accepts exactly three values:

```env
ENVIRONMENT=local
```

Use one value per application process:

- `local` for the supported developer, demonstration, and judge Docker stack.
- `staging` to exercise non-local validation behavior in tests.
- `production` to exercise the strictest current validation behavior in tests.

The latter two values do not create or imply remote environments.

Private development routes are a separate, opt-in local setting:

```env
ENABLE_PRIVATE_DEV_ROUTES=false
```

Setting `ENABLE_PRIVATE_DEV_ROUTES=true` outside `local` causes startup
validation to fail.

## Runtime Behavior Matrix

| Behavior | Local | Staging | Production |
|----------|-------|---------|------------|
| Rate limiting | Disabled | Enabled | Enabled |
| Private `/private/*` routes | Disabled by default; explicit opt-in allowed | Disabled; opt-in rejected | Disabled; opt-in rejected |
| Sentry | Disabled | Enabled only when `SENTRY_DSN` is set | Enabled only when `SENTRY_DSN` is set |
| Application logs | `INFO`, human-readable text | `INFO`, structured JSON | `INFO`, structured JSON |
| Email delivery | Enabled when SMTP is configured; local Compose supplies Mailcatcher | Enabled when SMTP is configured | Enabled when SMTP is configured |
| Secret validation | Local placeholders are tolerated | Explicit `SECRET_KEY` required; placeholder secrets rejected | Explicit `SECRET_KEY` required; placeholder secrets rejected |
| JWT access-token lifetime | 24 hours | 24 hours | 24 hours |
| Database pool defaults | Size 5, overflow 10 | Size 10, overflow 20 | Size 10, overflow 20 |
| CORS origins | `FRONTEND_HOST` plus `BACKEND_CORS_ORIGINS` | Same rule | Same rule |

The application does not automatically make production rate limits stricter
than staging, require SMTP in non-local environments, or vary error details by
environment. Configure deployment requirements explicitly instead of assuming
that changing `ENVIRONMENT` applies them.

## Detailed Behavior

### Runtime Security Validation

All environments require the base settings needed to construct the
application, including `PROJECT_NAME`, `ENVIRONMENT`, database connection
fields, and initial-superuser fields.

Local development may omit `SECRET_KEY`; the settings model then generates an
ephemeral value. Staging and production must provide a non-blank
`SECRET_KEY`. In non-local environments, these values must not use the
`changethis` placeholder:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `FIRST_SUPERUSER_PASSWORD`

Use explicit unique secrets whenever exercising a non-local profile. Do not
reuse the local placeholders.

### Rate Limiting

Rate limiting is disabled only when `ENVIRONMENT=local`. Staging and
production currently use the same limits:

| Endpoint category | Limit |
|-------------------|-------|
| General API default | 100 requests per minute |
| Authentication and password recovery | 5 requests per minute |
| Registration | 10 requests per minute |

### Private Development Routes

The `/private/*` router is registered only when both conditions are true:

1. `ENVIRONMENT=local`
2. `ENABLE_PRIVATE_DEV_ROUTES=true`

The setting defaults to `false`. Staging and production reject an enabled flag
during startup rather than silently exposing the routes.

### Logging, Sentry, and Tracing

Application logging uses level `INFO` in every environment. Local output is
human-readable text; staging and production use structured JSON.

Sentry initialization requires both a non-local environment and a configured
`SENTRY_DSN`. A DSN does not enable Sentry locally.

OpenTelemetry is independent of `ENVIRONMENT`. It remains opt-in through
`OTEL_ENABLED` and requires an `OTLP_ENDPOINT`; see
[Configuration](CONFIGURATION.md#observability).

### Error Responses

The same RFC 9457 Problem Details contract is used in every environment.
Responses include the stable application error code and trace ID where
applicable. The application does not add stack traces to local API responses
or switch to a separate production error schema.

### Email Delivery

Email is enabled when both `SMTP_HOST` and `EMAILS_FROM_EMAIL` are configured.
SMTP authentication fields remain optional because some servers do not require
them.

Local Docker Compose supplies Mailcatcher automatically. Outside that local
override, configure SMTP only when the deployment needs email. Delivery uses
bounded retries in every environment and records final failure without making
SMTP a startup requirement.

### Database Connections

The application enables pool pre-ping by default. Unless overridden:

| Setting | Local | Staging/Production |
|---------|-------|--------------------|
| Pool size | 5 | 10 |
| Maximum overflow | 10 | 20 |
| Checkout timeout | 30 seconds | 30 seconds |
| Connection recycle | 1800 seconds | 1800 seconds |

Database host, port, credentials, TLS, and managed-service choices come from
deployment configuration. `ENVIRONMENT` does not select or enforce a database
provider or SSL mode.

### Private Engine State

The engine uses one application-owned persistent root in every environment.
The local container deployment intentionally fixes the topology so a
host-provided path
cannot redirect a named volume:

| Purpose | Container path |
|---------|----------------|
| Persistent root | `/var/lib/txt2crs` |
| Tenant job database | `/var/lib/txt2crs/jobs.sqlite3` |
| Rendered artifacts | `/var/lib/txt2crs/artifacts` |
| Isolated Codex credentials | `/var/lib/txt2crs/codex-home` |
| Disposable worker files | `/tmp/txt2crs-worker` |

The job database, artifacts, and Codex home must remain strict children of the
persistent root. The worker root must remain outside it. Docker Compose mounts
the `txt2crs-state` volume only at `/var/lib/txt2crs`. A complete local backup
uses `scripts/backup-local-state.sh`, which briefly stops the backend writer
and packages that volume with PostgreSQL in one checksum-protected bundle.

### CORS

Allowed origins are the configured `FRONTEND_HOST` plus
`BACKEND_CORS_ORIGINS`. There is no separate hard-coded local, staging, or
production allowlist. Set only the origins needed by each deployment and never
use wildcard origins with credentials.

### Request Metadata and Privacy

The current request middleware records the request path, query string, and
client IP address. That metadata can contain personal information, including
an email address in the password-recovery HTML route. Treat application logs
as personal data, restrict access, and do not enable long retention by
default. Redaction and a documented retention policy remain required before a
production privacy review can pass; see
[Security](SECURITY.md#known-security-and-compliance-gaps).

## Local Docker Addresses

The local host ports come from `docker-compose.override.yml`, not from
`ENVIRONMENT` itself. The maintained endpoint table is in
[Development](development.md#local-service-endpoints).

Inside the Docker network, containers use service ports such as `db:5432` and
`mailcatcher:1025`. Host tools use the published ports documented in the
development guide.

## Deployment Responsibilities

Changing `ENVIRONMENT` activates only the application branches documented
above. It does not create a deployment or configure:

- Public domains or frontend URLs
- Remote database hosting, credentials, backups, or TLS
- SMTP credentials
- Sentry or OpenTelemetry destinations
- CORS origins
- Deployment credentials or approvals

The current project does not use a deployment platform. Follow the local-only
[deployment policy](deployment-policy.md).

## Targeted Validation

Runtime environment rules have focused backend tests:

```bash
cd backend
ENVIRONMENT=local \
  PROJECT_NAME="txt2crs tests" \
  POSTGRES_SERVER=localhost \
  POSTGRES_USER=postgres \
  FIRST_SUPERUSER=admin@example.com \
  FIRST_SUPERUSER_PASSWORD=test-superuser-password \
  uv run pytest --confcutdir=tests/core \
  tests/core/test_runtime_security_defaults.py \
  tests/core/test_email_delivery.py -v
```

When adding a new environment-specific branch, update this matrix and add tests
covering every affected environment.
