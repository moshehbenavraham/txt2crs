# Environments

## Environment Overview

| Environment | URL | Purpose |
|-------------|-----|---------|
| Development | http://localhost:5183 | Local development |
| Staging | [configured] | Pre-production testing |
| Production | [configured] | Live system |

## Port Mappings

| Service | Port | URL |
|---------|------|-----|
| Frontend | 5183 | http://localhost:5183 |
| Backend API | 8012 | http://localhost:8012 |
| API Docs | 8012 | http://localhost:8012/docs |
| PostgreSQL | 5447 | localhost:5439 |
| Mailcatcher | 1081 | http://localhost:1080 |

## Environment Variables

### Required in All Environments

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `POSTGRES_PASSWORD` | Database password |
| `FIRST_SUPERUSER_PASSWORD` | Initial admin account password |

### Configuration by Environment

| Variable | Dev | Staging | Prod |
|----------|-----|---------|------|
| `ENVIRONMENT` | local | staging | production |
| `DOMAIN` | localhost | staging.domain.com | domain.com |
| `FRONTEND_HOST` | http://localhost:5183 | https://staging.domain.com | https://domain.com |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | (empty) | Email server hostname |
| `SMTP_USER` | (empty) | Email server username |
| `SMTP_PASSWORD` | (empty) | Email server password |
| `SMTP_TIMEOUT_SECONDS` | `10` | Timeout per SMTP delivery attempt |
| `SMTP_MAX_ATTEMPTS` | `3` | Maximum bounded send attempts per email |
| `SMTP_RETRY_BACKOFF_SECONDS` | `0.5` | Base exponential retry delay between attempts |
| `SENTRY_DSN` | (empty) | Sentry error tracking DSN |

## Docker Configuration

### Development (docker-compose.yml)

Uses `docker-compose.override.yml` for:
- Volume mounts for live code reloading
- Debug mode with `--reload` flag
- Exposed ports for local access
- Mailcatcher for email testing

### Production

Uses `docker-compose.traefik.yml` for:
- Traefik reverse proxy with HTTPS
- Let's Encrypt SSL certificates
- Container health checks
- No exposed ports (Traefik handles routing)

## Switching Environments

Set the `ENVIRONMENT` variable in `.env`:

```bash
# Local development
ENVIRONMENT=local
ENABLE_PRIVATE_DEV_ROUTES=false  # Set true only when local /private routes are needed

# Staging deployment
ENVIRONMENT=staging

# Production deployment
ENVIRONMENT=production
```

Backend behavior changes by environment (from `app/core/config.py`).
