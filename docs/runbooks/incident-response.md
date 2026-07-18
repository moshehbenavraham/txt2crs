# Incident Response

Primary deployment path: Coolify (`.github/workflows/deploy-coolify.yml`).
Legacy compose workflows are break-glass fallback only (see `docs/deployment-policy.md`).

## Severity Levels

| Level | Description | Response |
|-------|-------------|----------|
| P0 | Complete outage | Immediate |
| P1 | Major feature broken | < 1 hour |
| P2 | Minor feature broken | < 4 hours |
| P3 | Cosmetic/minor | Next business day |

## Common Incidents

### Database Connection Refused

**Symptoms**: 500 errors on all authenticated endpoints

**Resolution**:
1. Check PostgreSQL container status: `docker compose ps db`
2. View logs: `docker compose logs db`
3. Restart if needed: `docker compose restart db`
4. Verify connection string in `.env`

### Frontend Build Failure

**Symptoms**: Blank page or old version showing

**Resolution**:
1. Clear browser cache
2. Check frontend container: `docker compose logs frontend`
3. Verify OpenAPI client is in sync: `./scripts/generate-client.sh`
4. Rebuild: `docker compose up -d --build frontend`

### JWT Authentication Failures

**Symptoms**: Users cannot log in, 401 errors

**Resolution**:
1. Verify SECRET_KEY is set in environment
2. Check token expiration settings
3. Clear user's browser session (`sessionStorage`) and retry
4. Check backend logs for specific error

### Alembic Migration Failed

**Symptoms**: Backend won't start, database schema errors

**Resolution**:
1. Check migration status: `docker compose exec backend alembic current`
2. View history: `docker compose exec backend alembic history`
3. If stuck, downgrade: `docker compose exec backend alembic downgrade -1`
4. Fix migration file and retry: `docker compose exec backend alembic upgrade head`

## Rollback Procedures

### 1) Primary path rollback (Coolify)

Use this for normal incident recovery when Coolify is available.

1. Identify the last known-good ref (release tag or commit SHA).
2. Re-run `Deploy via Coolify` from GitHub Actions on that ref (workflow dispatch, target `all` or scoped component).
3. Confirm Coolify shows both apps as healthy.
4. Run verification checks from the checklist below.

### 2) Legacy fallback rollback (compose workflows)

Use only when primary-path automation is unavailable/degraded.

```bash
# Export values captured by deployment workflow logs
export STACK_NAME=<stack-name>
export BACKEND_PREV_IMAGE_ID=<previous-backend-image-id>
export FRONTEND_PREV_IMAGE_ID=<previous-frontend-image-id>

# Run deterministic compose rollback to previous backend/frontend images
bash scripts/deploy-rollback.sh
```

### 3) Database rollback

```bash
# Downgrade one migration
docker compose exec backend alembic downgrade -1

# Or downgrade to specific revision
docker compose exec backend alembic downgrade <revision_id>
```

## Monitoring Checklist

- [ ] Backend readiness is healthy: `curl -fsS http://localhost:8012/api/v1/utils/health/`
- [ ] Backend liveness responds: `curl -fsS http://localhost:8012/api/v1/utils/health-check/`
- [ ] Frontend loading: `curl http://localhost:5183`
- [ ] Database connected: Check backend logs for connection success
- [ ] API docs accessible: http://localhost:8012/docs
