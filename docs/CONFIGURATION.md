# Configuration Guide

> Environment variable documentation for the Python React Boilerplate

## Quick Start

1. Copy `.env.example` to `.env`
2. Update values as needed for your environment
3. Never commit `.env` to version control

```bash
cp .env.example .env
```

## Environment Variables

### Required Variables

These must be set for the application to function:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) | `a1b2c3d4...` |
| `POSTGRES_SERVER` | PostgreSQL hostname | `db` or `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | Database name | `app` |
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `changethis` |
| `FIRST_SUPERUSER` | Initial admin email | `admin@example.com` |
| `FIRST_SUPERUSER_PASSWORD` | Initial admin password | `changethis` |

### Optional Variables

#### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Environment name: `local`, `staging`, `production` |
| `PROJECT_NAME` | `Python React Boilerplate` | Application name shown in UI and emails |
| `DOMAIN` | `localhost` | Domain for cookie settings and URLs |
| `STACK_NAME` | `python-react-boilerplate` | Docker stack identifier |

#### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_HOST` | `http://localhost:5183` | Frontend URL for CORS and email links |

#### Backend CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_CORS_ORIGINS` | (see below) | Comma-separated allowed origins |

Default CORS origins:
```
http://localhost,http://localhost:5183,http://localhost:5184,http://localhost:8012,https://localhost,https://localhost:5183,https://localhost:5184
```

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
| `EMAILS_FROM_EMAIL` | `info@example.com` | Sender email address |

**Note**: Email functionality is optional for local development. If SMTP settings are not configured, email operations will be skipped.

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

**Note**: Sentry is disabled if DSN is not set.

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

**Behaviors in local:**
- Rate limiting is disabled
- Local-only `/private/*` routes are disabled unless `ENABLE_PRIVATE_DEV_ROUTES=true`
- Sentry error tracking is disabled
- Email sending is skipped if SMTP not configured
- Detailed error messages are shown

### Staging

```env
ENVIRONMENT=staging
DOMAIN=staging.example.com
FRONTEND_HOST=https://staging.example.com
POSTGRES_SERVER=staging-db.example.com
SECRET_KEY=<generate-unique-key>
SENTRY_DSN=https://xxx@sentry.io/xxx
```

**Behaviors in staging:**
- Rate limiting is enabled
- Sentry error tracking is enabled
- Email functionality is enabled
- Detailed error messages are hidden

### Production

```env
ENVIRONMENT=production
DOMAIN=example.com
FRONTEND_HOST=https://example.com
POSTGRES_SERVER=prod-db.example.com
SECRET_KEY=<generate-unique-key>
SENTRY_DSN=https://xxx@sentry.io/xxx
```

**Behaviors in production:**
- Rate limiting is enabled and stricter
- Sentry error tracking is enabled
- Email functionality is required
- Minimal error details in responses
- Secret key validation is enforced

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

1. **Required variables**: Application fails to start if missing
2. **SECRET_KEY**: Must not be `changethis` in production
3. **POSTGRES_PASSWORD**: Must not be `changethis` in production
4. **CORS origins**: Must be valid URLs

## Loading Order

Configuration is loaded in this order (later overrides earlier):

1. Default values in `app/core/config.py`
2. `.env` file in project root
3. Environment variables from shell
4. Docker Compose environment section

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
