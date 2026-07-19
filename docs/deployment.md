# Local Deployment

## Supported Target

The complete txt2crs project deploys locally with Docker Compose. This is the
only in-scope release, demonstration, and judge execution target.

```bash
cp .env.example .env
# Replace SECRET_KEY, POSTGRES_PASSWORD, and FIRST_SUPERUSER_PASSWORD.
docker compose up --detach --build --wait
```

See [deployment policy](deployment-policy.md) and
[ADR-0008](adr/0008-local-only-deployment-scope.md).

## Verify the Running Application

```bash
docker compose ps
curl --fail http://localhost:8012/api/v1/utils/health/
curl --fail http://localhost:5183/health
```

Open:

- Frontend: <http://localhost:5183>
- API documentation: <http://localhost:8012/docs>
- Mailcatcher: <http://localhost:1081>

Backend readiness includes PostgreSQL connectivity and the current application
version. Frontend health is served directly by Nginx.

## Deployable Units

| Unit | Build | Runtime | Health |
|------|-------|---------|--------|
| Backend shell + engine | `backend/Dockerfile` | One non-root FastAPI process | `/api/v1/utils/health/` |
| Frontend | `frontend/Dockerfile` | Nginx | `/health` |

The engine is a backend workspace dependency, not a separate service.
PostgreSQL stores application users; `txt2crs-state` stores private engine
SQLite jobs, artifacts, and Codex-managed credentials.

## Stop, Rebuild, and Reset

Stop while preserving data:

```bash
docker compose down --remove-orphans
```

Rebuild the complete tested topology:

```bash
docker compose up --detach --build --wait
```

Deleting volumes is destructive and not part of a normal deployment:

```bash
docker compose down --remove-orphans --volumes
```

That command permanently removes both application databases, artifacts, and
local Codex credentials.

## Release Validation

Run the repository gate:

```bash
./scripts/validate-changes.sh
docker compose config --quiet
./scripts/verify-production-baseline.sh
```

The baseline script's name refers to the production-like image target, not a
hosted environment. It builds and validates that image entirely locally.

For an end-to-end stack smoke:

```bash
docker compose up --detach --build --wait
./scripts/deploy-smoke-check.sh \
  http://localhost:8012/api/v1/utils/health/ \
  http://localhost:5183/health
```

## Rollback

For an uncommitted local change, stop the stack, restore the intended source
revision through normal version control, and rebuild. Preserve named volumes
unless the target revision has an incompatible migration and a reviewed
restore plan exists.

If previous local image IDs were captured before a rebuild,
`scripts/deploy-rollback.sh` can retag and recreate the backend and frontend.
It does not roll back PostgreSQL or engine SQLite schemas.

## Out of Scope

The repository intentionally has no active:

- hosted deployment platform;
- staging or hosted-production workflow;
- domain or TLS automation;
- platform deployment credentials;
- remote rollout or managed rollback path.

Any future hosting decision requires explicit owner approval and a new ADR.
No platform is presumed.
