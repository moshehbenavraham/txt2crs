# Environment-Specific Behavior

> How the application behaves differently across environments

## Environment Detection

The environment is determined by the `ENVIRONMENT` variable:

```env
ENVIRONMENT=local    # Local development
ENABLE_PRIVATE_DEV_ROUTES=false  # Opt in to /private/* test routes
ENVIRONMENT=staging  # Staging/testing
ENVIRONMENT=production  # Production
```

Access in code:
```python
from app.core.config import settings

if settings.ENVIRONMENT == "local":
    # Local-only behavior
```

## Feature Matrix

| Feature | Local | Staging | Production |
|---------|-------|---------|------------|
| Rate Limiting | Off | On | On (stricter) |
| Private Dev Routes (`/private/*`) | Off by default (opt-in) | Off | Off |
| Sentry Error Tracking | Off | On | On |
| Secret Key Validation | Off | On | On |
| Email Sending | Optional | Required | Required |
| Detailed Error Messages | Yes | Limited | No |
| Debug Mode | Yes | No | No |
| CORS Strictness | Relaxed | Moderate | Strict |
| Password Complexity | Enforced | Enforced | Enforced |
| JWT Token Expiry | 8 days | 8 days | 8 days |
| Database Migrations | Manual | Manual | CI/CD |
| DB Pool Pre-Ping | On | On | On |
| DB Pool Size Default | 5 | 10 | 10 |
| DB Pool Max Overflow Default | 10 | 20 | 20 |

## Detailed Behavior

### Rate Limiting

**Local**: Disabled to allow rapid development and testing.

**Staging/Production**: Enabled with the following limits:

| Endpoint Category | Limit |
|-------------------|-------|
| General API | 100 req/minute |
| Authentication | 5 req/minute |
| Registration | 10 req/minute |
| Password Reset | 3 req/minute |

### Error Responses

**Local**:
```json
{
  "detail": "User with email 'test@example.com' not found",
  "code": "USER_2001",
  "trace_id": "abc123",
  "stack_trace": "..."
}
```

**Production**:
```json
{
  "detail": "User not found",
  "code": "USER_2001",
  "trace_id": "abc123"
}
```

### Sentry Integration

**Local**: Disabled. Errors are logged to console only.

**Staging/Production**: Enabled when `SENTRY_DSN` is set.

Captured data:
- Unhandled exceptions
- Performance traces
- User context (anonymized)
- Request metadata

### Email Configuration

**Local**:
- Email functions return early if SMTP not configured
- Emails are logged to console instead of sent
- Password reset and verification flows still work (token logged)

**Staging/Production**:
- SMTP configuration is required
- Email failures are logged and reported to Sentry
- Retry logic is enabled for transient failures

### Logging

**Local**:
```python
LOG_LEVEL = "DEBUG"
LOG_FORMAT = "text"  # Human-readable
```

**Staging**:
```python
LOG_LEVEL = "INFO"
LOG_FORMAT = "json"  # Structured for aggregation
```

**Production**:
```python
LOG_LEVEL = "WARNING"
LOG_FORMAT = "json"
```

### Database

**Local**:
- Uses Docker Compose PostgreSQL
- Port 5447 (non-standard to avoid conflicts)
- No SSL required
- Connection pool defaults: size `5`, max overflow `10`, timeout `30s`, recycle `1800s`

**Staging/Production**:
- Managed PostgreSQL recommended
- SSL connections required
- Connection pooling enabled
- Connection pool defaults: size `10`, max overflow `20`, timeout `30s`, recycle `1800s`

### CORS Policy

**Local**:
```python
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:5183",
    "http://localhost:5184",
    "http://localhost:8012",
    # ... various local ports
]
```

**Production**:
```python
ALLOWED_ORIGINS = [
    "https://example.com",
    "https://www.example.com",
]
```

## Configuration Validation

The application validates configuration at startup based on environment:

### Local (Relaxed)
- No validation of SECRET_KEY
- No validation of POSTGRES_PASSWORD
- Missing SMTP config is allowed

### Staging/Production (Strict)
- SECRET_KEY must not be "changethis"
- POSTGRES_PASSWORD must not be "changethis"
- SENTRY_DSN should be configured (warning if missing)

## Testing in Different Environments

### Simulating Production Locally

```bash
# Set production-like environment
ENVIRONMENT=production \
SECRET_KEY=$(openssl rand -hex 32) \
SENTRY_DSN="" \
docker compose up
```

### Running Integration Tests

```bash
# Use staging-like settings for integration tests
ENVIRONMENT=staging \
pytest tests/integration/
```

## CI/CD Considerations

### GitHub Actions

```yaml
# Different jobs for different environments
jobs:
  test:
    env:
      ENVIRONMENT: local
      # ... test configuration

  deploy-staging:
    env:
      ENVIRONMENT: staging
      # ... staging configuration

  deploy-production:
    env:
      ENVIRONMENT: production
      # ... production configuration
```

### Environment-Specific Secrets

Use GitHub Secrets or your CI/CD platform's secret management:

```yaml
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY_PRODUCTION }}
  SENTRY_DSN: ${{ secrets.SENTRY_DSN_PRODUCTION }}
```

## Adding Environment-Specific Behavior

When adding new features that behave differently per environment:

1. Add check in code:
```python
from app.core.config import settings

def my_feature():
    if settings.ENVIRONMENT == "local":
        # Development behavior
        return mock_response()
    else:
        # Production behavior
        return real_api_call()
```

2. Document in this file
3. Update the feature matrix table
4. Add tests for each environment behavior
