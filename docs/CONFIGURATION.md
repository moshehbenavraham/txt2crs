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
| `STACK_NAME` | `python-react-boilerplate` | Docker stack identifier |
| `ENABLE_PRIVATE_DEV_ROUTES` | `False` | Register `/private/*` routes; accepted only in `local` |

#### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_HOST` | `http://localhost:5181` | Frontend URL for CORS and email links; `.env.example` sets `http://localhost:5183` for Docker |

#### Backend CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_CORS_ORIGINS` | Empty list | Comma-separated or JSON-array additional origins |

The effective allowlist is `FRONTEND_HOST` plus `BACKEND_CORS_ORIGINS`.
`.env.example` supplies these additional local origins:

```
http://localhost,http://localhost:5183,http://localhost:5184,http://localhost:8012,https://localhost,https://localhost:5183,https://localhost:5184
```

#### Database Configuration

| Variable | Runtime default | Description |
|----------|-----------------|-------------|
| `POSTGRES_PORT` | `5441` | Database server port; local Compose overrides the container connection to `5432` and publishes it on host port `5447` |
| `POSTGRES_DB` | Empty string | Database name; Docker Compose requires a value |
| `POSTGRES_PASSWORD` | Empty string | Database password; Docker Compose requires a value and non-local deployments must not use `changethis` |

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
| `DOCKER_IMAGE_BACKEND` | `python-react-boilerplate-backend` | Backend Docker image name |
| `DOCKER_IMAGE_FRONTEND` | `python-react-boilerplate-frontend` | Frontend Docker image name |
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

#### Deployment (Coolify)

| Variable | Description |
|----------|-------------|
| `COOLIFY_API_TOKEN` | API token for Coolify deployment |
| `COOLIFY_API_URL` | Coolify API base URL |
| `GITHUB_REPO` | GitHub repository URL |
| `GITHUB_BRANCH` | Branch to deploy |
| `APP_NAME` | Application name in Coolify |
| `APP_DOMAIN` | Production domain |
| `BACKEND_APP_UUID` | Backend app UUID (set after `coolify-deploy.sh --create`) |
| `FRONTEND_APP_UUID` | Frontend app UUID (set after `coolify-deploy.sh --create`) |

## Environment-Specific Settings

### Local Development

```env
ENVIRONMENT=local
ENABLE_PRIVATE_DEV_ROUTES=false
DOMAIN=localhost
FRONTEND_HOST=http://localhost:5183
POSTGRES_SERVER=db
POSTGRES_PORT=5447
SECRET_KEY=development-secret-key-change-in-production
```

Behaviors in local:

- Rate limiting is disabled.
- Local-only `/private/*` routes are disabled unless
  `ENABLE_PRIVATE_DEV_ROUTES=true`.
- Sentry is disabled even when a DSN is present.
- Logs use level `INFO` and human-readable text.
- Local Docker Compose routes email to Mailcatcher.

### Staging

```env
ENVIRONMENT=staging
DOMAIN=staging.example.com
FRONTEND_HOST=https://staging.example.com
POSTGRES_SERVER=staging-db.example.com
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

### Production

```env
ENVIRONMENT=production
DOMAIN=example.com
FRONTEND_HOST=https://example.com
POSTGRES_SERVER=prod-db.example.com
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

See [Environment-specific behavior](ENVIRONMENTS.md) for the source-backed
runtime matrix.

## Security Notes

### SECRET_KEY

- **Must be unique per environment**
- Generate with: `openssl rand -hex 32`
- Never reuse between environments
- Rotate periodically in production
- If compromised, all JWTs become invalid

### Database Credentials

- Use different credentials per environment
- Use managed database services in production
- Enable SSL for database connections in production
- Restrict database network access

### CORS Origins

- Only include necessary origins
- Never use `*` in production
- Include both HTTP and HTTPS if supporting both
- Include all frontend deployment URLs

## Validation

The application validates configuration on startup:

1. Required base variables must be present and valid.
2. Staging and production require an explicit, non-blank `SECRET_KEY`.
3. Non-local environments reject `changethis` for `SECRET_KEY`,
   `POSTGRES_PASSWORD`, and `FIRST_SUPERUSER_PASSWORD`.
4. Private development routes cannot be enabled outside `local`.
5. CORS origins must be valid URLs.

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
