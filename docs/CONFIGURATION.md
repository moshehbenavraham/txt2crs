# Configuration Guide

> Environment variable documentation for the txt2crs application shell.

## Quick Start

1. Copy `.env.example` to `.env`
2. Update values as needed for your environment
3. Never commit `.env` to version control

```bash
cp .env.example .env
```

## Environment Variables

### Required Base Variables

These settings have no application default and must be present:

| Variable | Description | Example |
|----------|-------------|---------|
| `PROJECT_NAME` | Application name used by the API, telemetry, and email | `txt2crs` |
| `ENVIRONMENT` | Runtime profile: `local`, `staging`, or `production` | `local` |
| `POSTGRES_SERVER` | PostgreSQL hostname | `db` or `localhost` |
| `POSTGRES_USER` | Database username | `postgres` |
| `FIRST_SUPERUSER` | Initial admin email | `admin@example.com` |
| `FIRST_SUPERUSER_PASSWORD` | Initial admin password | A unique secret |

The Docker Compose configuration also requires `SECRET_KEY`,
`POSTGRES_PASSWORD`, and `POSTGRES_DB` in `.env`. The settings model can
generate an ephemeral `SECRET_KEY` only for direct local execution. Staging and
production require an explicit non-blank `SECRET_KEY`, and reject
`changethis` for `SECRET_KEY`, `POSTGRES_PASSWORD`, and
`FIRST_SUPERUSER_PASSWORD`.

### Optional Variables

#### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DOMAIN` | `localhost` | Domain for cookie settings and URLs |
| `STACK_NAME` | `.env.example`: `txt2crs` | Docker Compose stack identifier |
| `ENABLE_PRIVATE_DEV_ROUTES` | `False` | Register `/private/*` routes; accepted only in `local` |
| `ENABLE_PUBLIC_SIGNUP` | `False` | Permit unauthenticated `/users/signup`; accepted only in `local` |

#### Docker Host Ports

The root `.env` owns every Docker-published host port. Container-internal
service ports do not change. The full host, container, direct-development, and
test inventory is documented in [Port allocations](PORTS.md).

| Variable | Default | Listener |
|----------|---------|----------|
| `TRAEFIK_HTTP_PORT` | `86` | Traefik HTTP / local proxy |
| `TRAEFIK_HTTPS_PORT` | `8443` | Traefik HTTPS overlay |
| `TRAEFIK_DASHBOARD_PORT` | `8102` | Traefik dashboard |
| `POSTGRES_PORT` | `5450` | PostgreSQL for host tools |
| `BACKEND_PORT` | `8016` | FastAPI backend |
| `FRONTEND_PORT` | `5195` | Docker frontend |
| `ADMINER_PORT` | `8103` | Adminer |
| `MAILCATCHER_SMTP_PORT` | `1029` | Mailcatcher SMTP |
| `MAILCATCHER_WEB_PORT` | `1084` | Mailcatcher web UI |
| `JAEGER_UI_PORT` | `16689` | Jaeger UI |
| `OTLP_GRPC_PORT` | `4324` | OTLP gRPC receiver |
| `OTLP_HTTP_PORT` | `4325` | OTLP HTTP receiver |
| `PLAYWRIGHT_REPORT_PORT` | `9327` | Playwright HTML report |

#### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_HOST` | `http://localhost:5196` | Frontend URL for CORS and email links; `.env.example` sets `http://localhost:5195` for Docker |

#### Backend CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_CORS_ORIGINS` | Empty list | Comma-separated or JSON-array additional origins |

The effective allowlist is `FRONTEND_HOST` plus `BACKEND_CORS_ORIGINS`.
`.env.example` supplies these additional local origins:

```
http://localhost,http://localhost:5195,http://localhost:5196,http://localhost:5197,http://localhost:8016,https://localhost,https://localhost:8443
```

#### Database Configuration

| Variable | Runtime default | Description |
|----------|-----------------|-------------|
| `POSTGRES_PORT` | `5450` | Database server port; local Compose keeps the container connection on `5432` and publishes it on host port `5450` |
| `POSTGRES_DB` | Empty string | Database name; Docker Compose requires a value |
| `POSTGRES_PASSWORD` | Empty string | Database password; Docker Compose requires a value and non-local deployments must not use `changethis` |

#### Course-System Storage and Runtime

Docker Compose fixes the five paths below to image-owned locations. Override
them only for host-only development, keep the database, artifacts, and Codex
home as strict children of the state root, and keep worker scratch outside
that persistent root.

| Variable | Default | Description |
|----------|---------|-------------|
| `TXT2CRS_STATE_ROOT` | `/var/lib/txt2crs` | Private persistent engine-state root |
| `TXT2CRS_JOB_DB_PATH` | `/var/lib/txt2crs/jobs.sqlite3` | Tenant-scoped SQLite job store |
| `TXT2CRS_ARTIFACT_ROOT` | `/var/lib/txt2crs/artifacts` | Private rendered-artifact root |
| `TXT2CRS_CODEX_HOME` | `/var/lib/txt2crs/codex-home` | Isolated dedicated Codex identity home |
| `TXT2CRS_WORKER_ROOT` | `/tmp/txt2crs-worker` | Ephemeral job workspace outside persistent state |
| `TXT2CRS_MODEL_ID` | `gpt-5.6-sol` | Reviewed exact model: `gpt-5.6-sol`, `gpt-5.6-terra`, or `gpt-5.6-luna` |

The shell owns one facade and one serial worker. These intervals bound durable
discovery, graceful shutdown, cached readiness, and the in-memory device-login
monitor:

| Variable | Default | Description |
|----------|---------|-------------|
| `TXT2CRS_WORKER_POLL_SECONDS` | `2` | Durable runnable-job scan interval |
| `TXT2CRS_WORKER_HEARTBEAT_SECONDS` | `5` | Content-free active-job heartbeat interval |
| `TXT2CRS_WORKER_SHUTDOWN_TIMEOUT_SECONDS` | `30` | Maximum graceful worker drain |
| `TXT2CRS_READINESS_REFRESH_SECONDS` | `60` | Interval between real readiness probes |
| `TXT2CRS_READINESS_STALE_AFTER_SECONDS` | `120` | Oldest complete readiness snapshot accepted as current |
| `TXT2CRS_READINESS_SHUTDOWN_TIMEOUT_SECONDS` | `30` | Maximum readiness-thread shutdown wait |
| `TXT2CRS_AUTH_MONITOR_POLL_SECONDS` | `0.5` | Active device-login state observation interval |
| `TXT2CRS_AUTH_SHUTDOWN_TIMEOUT_SECONDS` | `10` | Maximum authentication-monitor shutdown wait |

#### Research

| Variable | Default | Description |
|----------|---------|-------------|
| `TXT2CRS_RESEARCH_ENABLED` | `True` | Disable-only switch for package-owned research |
| `TXT2CRS_RESEARCH_MCP_HOST` | `127.0.0.1` | Numeric loopback address; wildcard, DNS, and external hosts are rejected |
| `TXT2CRS_RESEARCH_MCP_PORT` | `8765` | Private two-tool research MCP port; not published by Compose |
| `TXT2CRS_RESEARCH_MCP_STARTUP_TIMEOUT_SECONDS` | `10` | Maximum bounded startup wait |
| `TXT2CRS_RESEARCH_MCP_SHUTDOWN_TIMEOUT_SECONDS` | `10` | Maximum bounded shutdown wait |
| `TAVILY_API_KEY` | (empty) | Optional local secret; absence reports research as unconfigured |
| `TAVILY_TIMEOUT_SECONDS` | `20` | Timeout per Tavily request |

Secrets remain in `.env`; never commit a real `TAVILY_API_KEY`. Missing
ChatGPT or Tavily authentication does not prevent startup or OpenAPI
generation. It truthfully blocks generation admission in cached readiness.

#### Generation Bounds and Retry Policy

These finite values are copied into the immutable execution profile stored
with each accepted job. Changing a default affects only later submissions.

| Variable | Default | Description |
|----------|---------|-------------|
| `TXT2CRS_MAX_INPUT_BYTES` | `20971520` | Maximum raw input bytes |
| `TXT2CRS_MAX_METADATA_BYTES` | `262144` | Maximum canonical input-metadata bytes |
| `TXT2CRS_MAX_NORMALIZED_CHARACTERS` | `200000` | Maximum normalized text characters |
| `TXT2CRS_MAX_PDF_PAGES` | `200` | Maximum PDF pages |
| `TXT2CRS_ARTIFACT_MAX_JOB_BYTES` | `104857600` | Maximum complete artifact bundle bytes |
| `TXT2CRS_HTML_PREVIEW_MAX_BYTES` | `5242880` | Maximum HTML preview bytes |
| `TXT2CRS_RETRY_MAXIMUM_ATTEMPTS` | `3` | Total attempts allowed by the shared provider retry policy |
| `TXT2CRS_RETRY_BASE_SECONDS` | `1` | Initial retry delay |
| `TXT2CRS_RETRY_MAXIMUM_SECONDS` | `15` | Maximum retry delay |
| `TXT2CRS_RETRY_JITTER_RATIO` | `0.2` | Bounded retry-jitter ratio |

| Variable | Default | Description |
|----------|---------|-------------|
| `TXT2CRS_RUN_MAXIMUM_TURNS` | `20` | Maximum Codex turns |
| `TXT2CRS_RUN_MAXIMUM_RESEARCH_CALLS` | `12` | Maximum combined research calls |
| `TXT2CRS_RUN_MAXIMUM_SEARCH_CALLS` | `6` | Maximum research searches |
| `TXT2CRS_RUN_MAXIMUM_EXTRACT_CALLS` | `6` | Maximum source extractions |
| `TXT2CRS_RUN_MAXIMUM_SOURCES` | `12` | Maximum retained sources |
| `TXT2CRS_RUN_MAXIMUM_EXTRACTED_BYTES` | `2000000` | Maximum extracted research bytes |
| `TXT2CRS_RUN_MAXIMUM_INPUT_TOKENS` | `600000` | Maximum input tokens |
| `TXT2CRS_RUN_MAXIMUM_OUTPUT_TOKENS` | `150000` | Maximum output tokens |
| `TXT2CRS_RUN_MAXIMUM_RETRIES` | `3` | Maximum run-level retries |
| `TXT2CRS_RUN_MAXIMUM_REPAIRS` | `3` | Maximum validation repairs |
| `TXT2CRS_RUN_MAXIMUM_ELAPSED_SECONDS` | `2700` | Maximum job elapsed time |

#### Admission Capacity

The public engine facade reserves rolling-window capacity before it accepts a
job. Research currency is represented as integer micro-US-dollars.

| Variable | Default | Description |
|----------|---------|-------------|
| `TXT2CRS_ADMISSION_WINDOW_SECONDS` | `86400` | Rolling reservation window |
| `TXT2CRS_ADMISSION_MAXIMUM_JOBS_PER_USER` | `4` | Maximum accepted jobs per owner in the window |
| `TXT2CRS_ADMISSION_MAXIMUM_JOBS_GLOBAL` | `10` | Maximum accepted jobs globally in the window |
| `TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_PER_USER` | `3000000` | Per-owner reserved token ceiling |
| `TXT2CRS_ADMISSION_MAXIMUM_RESERVED_TOKENS_GLOBAL` | `7500000` | Global reserved token ceiling |
| `TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_PER_USER` | `4000000` | Per-owner research-cost ceiling |
| `TXT2CRS_ADMISSION_MAXIMUM_RESEARCH_MICROUSD_GLOBAL` | `10000000` | Global research-cost ceiling |

These are conservative production fallbacks and are exactly twice the original
P0 limits. The canonical local `.env.example` deliberately overrides them with
10 jobs per owner and 20 globally, with token and research ceilings scaled to
the same complete-job reservation count for judge and E2E work.

#### Email Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | (empty) | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_USER` | (empty) | SMTP authentication username |
| `SMTP_PASSWORD` | (empty) | SMTP authentication password |
| `SMTP_TLS` | `True` | Enable TLS (STARTTLS) |
| `SMTP_SSL` | `False` | Enable SSL (direct SSL connection) |
| `SMTP_TIMEOUT_SECONDS` | `10` | Timeout per SMTP delivery attempt |
| `SMTP_MAX_ATTEMPTS` | `3` | Maximum bounded send attempts per email |
| `SMTP_RETRY_BACKOFF_SECONDS` | `0.5` | Base exponential retry delay between attempts |
| `EMAILS_FROM_EMAIL` | (empty) | Sender email address; `.env.example` uses `info@example.com` |

Email is optional in every environment. Delivery is enabled only when both
`SMTP_HOST` and `EMAILS_FROM_EMAIL` are set. Local Docker Compose supplies
Mailcatcher values through its override.

#### Database Pool Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_POOL_PRE_PING` | `True` | Verify pooled DB connections are alive before each checkout |
| `DB_POOL_SIZE` | (empty) | Optional override for base pool size |
| `DB_POOL_MAX_OVERFLOW` | (empty) | Optional override for overflow connections above pool size |
| `DB_POOL_TIMEOUT_SECONDS` | (empty) | Optional override for pool checkout timeout |
| `DB_POOL_RECYCLE_SECONDS` | (empty) | Optional override for connection recycle interval |

Effective defaults when override values are empty:
- **Local**: `DB_POOL_SIZE=5`, `DB_POOL_MAX_OVERFLOW=10`
- **Staging/Production**: `DB_POOL_SIZE=10`, `DB_POOL_MAX_OVERFLOW=20`
- **All environments**: `DB_POOL_TIMEOUT_SECONDS=30`, `DB_POOL_RECYCLE_SECONDS=1800`

#### Docker Images

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKER_IMAGE_BACKEND` | `.env.example`: `txt2crs-backend` | Backend Docker image name |
| `DOCKER_IMAGE_FRONTEND` | `.env.example`: `txt2crs-frontend` | Frontend Docker image name |
| `TAG` | `latest` | Docker image tag |

#### Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | (empty) | Sentry DSN for error tracking |
| `OTEL_ENABLED` | `False` | Opt in to OpenTelemetry tracing |
| `OTLP_ENDPOINT` | (empty) | OTLP collector endpoint; required when tracing is enabled |
| `OTEL_SERVICE_NAME` | `PROJECT_NAME` | Service name attached to exported traces |
| `OTEL_TRACES_SAMPLER_ARG` | `1.0` | Trace sampling ratio from `0.0` to `1.0` |

Sentry is disabled locally and is enabled in staging or production only when a
DSN is set. OpenTelemetry is independent of `ENVIRONMENT` and starts only when
both `OTEL_ENABLED=true` and `OTLP_ENDPOINT` are configured.

#### Deployment Scope

No hosted-platform environment variables are supported in the current project
scope. Repository-root Docker Compose reads the local variables above.
`ENVIRONMENT=staging` and `ENVIRONMENT=production` select application runtime
validation behavior; they do not configure or imply a hosted deployment.

## Environment-Specific Settings

### Local Development

```env
ENVIRONMENT=local
ENABLE_PRIVATE_DEV_ROUTES=false
ENABLE_PUBLIC_SIGNUP=true
DOMAIN=localhost
FRONTEND_HOST=http://localhost:5195
POSTGRES_SERVER=db
POSTGRES_PORT=5450
SECRET_KEY=development-secret-key-change-in-production
```

Behaviors in local:

- Rate limiting is disabled.
- Local-only `/private/*` routes are disabled unless
  `ENABLE_PRIVATE_DEV_ROUTES=true`.
- Public signup is disabled by default. The backend-only developer example
  opts in with `ENABLE_PUBLIC_SIGNUP=true`; the root judge/demo example keeps
  it false.
- Sentry is disabled even when a DSN is present.
- Logs use level `INFO` and human-readable text.
- Local Docker Compose routes email to Mailcatcher.

### Staging Runtime Profile (Not Deployed)

```env
ENVIRONMENT=staging
DOMAIN=localhost
FRONTEND_HOST=http://localhost:5195
POSTGRES_SERVER=localhost
SECRET_KEY=<generate-unique-key>
SENTRY_DSN=https://xxx@sentry.io/xxx
```

Behaviors in staging:

- Rate limiting is enabled with the same limits as production.
- Sentry starts only when `SENTRY_DSN` is set.
- Email delivery starts only when SMTP is configured.
- Logs use level `INFO` and structured JSON.
- `SECRET_KEY` must be explicit, and placeholder secrets are rejected.
- `ENABLE_PRIVATE_DEV_ROUTES=true` is rejected during startup.
- `ENABLE_PUBLIC_SIGNUP=true` is rejected during startup.

### Production Runtime Profile (Not Deployed)

```env
ENVIRONMENT=production
DOMAIN=localhost
FRONTEND_HOST=http://localhost:5195
POSTGRES_SERVER=localhost
SECRET_KEY=<generate-unique-key>
SENTRY_DSN=https://xxx@sentry.io/xxx
```

Behaviors in production:

- Rate limiting is enabled with the same limits as staging.
- Sentry starts only when `SENTRY_DSN` is set.
- Email delivery starts only when SMTP is configured.
- Logs use level `INFO` and structured JSON.
- `SECRET_KEY` must be explicit, and placeholder secrets are rejected.
- `ENABLE_PRIVATE_DEV_ROUTES=true` is rejected during startup.
- `ENABLE_PUBLIC_SIGNUP=true` is rejected during startup.

See [Environment-specific behavior](environments.md) for the source-backed
runtime matrix.

## Security Notes

### SECRET_KEY

- **Must be unique per environment**
- Generate with: `openssl rand -hex 32`
- Never reuse between environments
- Rotate according to the operator's local secret policy
- If compromised, all JWTs become invalid

### Database Credentials

- Use different credentials per environment
- Keep the published local database port bound only where needed
- If a future hosted scope is approved, define TLS and network controls before
  selecting a database service

### CORS Origins

- Only include necessary origins
- Never use `*` with credentials
- Include only the local frontend origins actually used

## Validation

The application validates configuration on startup:

1. Required base variables must be present and valid.
2. Staging and production require an explicit, non-blank `SECRET_KEY`.
3. Non-local environments reject `changethis` for `SECRET_KEY`,
   `POSTGRES_PASSWORD`, and `FIRST_SUPERUSER_PASSWORD`.
4. Private development routes cannot be enabled outside `local`.
5. CORS origins must be valid URLs.
6. Course-system state paths must remain confined and non-overlapping.
7. The research MCP host must be a numeric loopback address.
8. Readiness, retry, run-budget, preview, and admission relationships must be
   internally consistent.

## Loading Order

Configuration precedence, from lowest to highest, is:

1. Defaults in `backend/app/core/config.py`.
2. The `.env` file resolved from the backend process working directory.
3. Process environment variables.

Docker Compose reads the repository-root `.env` and injects values through
each service's `env_file` and `environment` sections. Values in a service's
`environment` section take precedence over its `env_file`.

## Troubleshooting

### Common Issues

**"Invalid database URL"**
- Check `POSTGRES_*` variables match your database setup
- Ensure database container is running

**"Invalid CORS origin"**
- Ensure origins are valid URLs (include protocol)
- Check for trailing slashes

**"Secret key validation failed"**
- Change `SECRET_KEY` from default in non-local environments

**"Email sending failed"**
- Verify SMTP credentials
- Check SMTP host is accessible from container network
- Try with `SMTP_TLS=False` if having TLS issues

**"Course system is not ready"**
- Log in as a superuser and inspect `/setup`
- Add `TAVILY_API_KEY` to `.env` when research is enabled
- Complete the ChatGPT device-login flow or use the displayed CLI recovery
  command
- Restart the backend after changing environment variables
