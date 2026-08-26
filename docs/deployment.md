# Deployment

## Reference Target

The complete txt2crs project deploys locally with Docker Compose. This is the
reference topology for development, release validation, and portable hosted
container deployments.

```bash
cp .env.example .env
# Replace SECRET_KEY, POSTGRES_PASSWORD, FIRST_SUPERUSER_PASSWORD, and
# TAVILY_API_KEY.
./scripts/start-local.sh
```

See [deployment policy](deployment-policy.md) and
[ADR-0009](adr/0009-portable-container-deployment.md).

## Verify the Running Application

```bash
./scripts/start-local.sh --status
curl --fail http://localhost:8016/api/v1/utils/health/
curl --fail http://localhost:5195/health
```

Open:

- Frontend: <http://localhost:5195>
- API documentation: <http://localhost:8016/docs>
- Mailcatcher: <http://localhost:1084>

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
./scripts/start-local.sh --stop
```

Rebuild the complete tested topology:

```bash
./scripts/start-local.sh
```

Deleting volumes is destructive and not part of a normal deployment:

```bash
docker compose down --remove-orphans --volumes
```

That command permanently removes both application databases, artifacts, and
local Codex credentials.

## Backup and State Recovery

Create a checksum-protected backup of PostgreSQL and private engine state:

```bash
./scripts/backup-local-state.sh
```

Restore both stores only with the explicit destructive confirmation:

```bash
TXT2CRS_RESTORE_CONFIRM=replace-local-state \
  ./scripts/restore-local-state.sh \
  ./backups/txt2crs_backup_<UTC timestamp>
```

The backup command briefly stops the backend writer so engine SQLite/WAL files,
artifacts, and Codex credentials are internally consistent. See
[Local deployment](local-deploy.md#backup-and-restore) for bundle contents,
retention, permissions, validation, and secure-storage responsibilities.

## Release Validation

Run the repository gate:

```bash
./scripts/validate-changes.sh
docker compose config --quiet
./scripts/verify-production-baseline.sh
```

The baseline script builds and validates the production images locally before
they are used by any deployment target.

Tag pushes matching `v*` and manual dispatches also select
`.github/workflows/release.yml`. That read-only workflow:

- requires the tag, root `VERSION`, and engine package version to agree;
- runs the complete reusable-engine suite and builds its wheel and source
  distribution;
- inspects distribution metadata and writes SHA-256 checksums;
- runs frontend unit, type, and production-build gates;
- builds and inspects both production images; and
- retains the inspected artifacts for 14 days.

The workflow validates release artifacts but does not select or deploy to a
hosting vendor.

For an end-to-end stack smoke:

```bash
./scripts/start-local.sh
./scripts/deploy-smoke-check.sh \
  http://localhost:8016/api/v1/utils/health/ \
  http://localhost:5195/health
```

## Rollback

For an uncommitted local change, stop the stack, restore the intended source
revision through normal version control, and rebuild. Preserve named volumes
unless the target revision has an incompatible migration and a reviewed
restore plan exists.

If previous local image IDs were captured before a rebuild,
`scripts/deploy-rollback.sh` can retag and recreate the backend and frontend.
It does not roll back PostgreSQL or engine SQLite schemas. Use a reviewed
complete backup bundle when data rollback is required.

## Hosted Deployments

The repository does not select a vendor, but hosted deployment is supported
when an operator preserves the portable contract in
[the deployment policy](deployment-policy.md). Before accepting learner data,
document the platform's domain and TLS setup, secret storage, persistent volume,
PostgreSQL, backup/restore, rollout, health, and rollback configuration.
