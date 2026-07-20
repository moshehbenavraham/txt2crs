# Local Deployment and Rebuilds

The supported local deployment is the repository-root Docker Compose stack.
For service URLs and direct development commands, see
[Development](development.md).

## Start or Rebuild

Create `.env` from the tracked example if it does not exist:

```bash
cp .env.example .env
# Replace the required secret placeholders and set TAVILY_API_KEY.
./scripts/start-local.sh
```

The startup assistant checks `.env`, Docker, Compose, and host ports before
delegating to `docker compose up --detach --build --wait`. Docker reports the
database, backend, and frontend as healthy before the command succeeds. Verify
the public local probes:

```bash
curl --fail http://localhost:8012/api/v1/utils/health/
curl --fail http://localhost:5183/health
```

The backend response includes application, version, and database status. The
frontend response is:

```json
{"status":"healthy","service":"frontend"}
```

## Stop Without Deleting Data

```bash
./scripts/start-local.sh --stop
```

This removes containers and the Compose network but preserves named volumes.
The application currently persists:

- PostgreSQL data in the `app-db-data` volume;
- private engine jobs, artifacts, and Codex credentials in the
  `txt2crs-state` volume.

Volume names are prefixed by the active Compose project name. Inspect the exact
names instead of assuming a hard-coded prefix:

```bash
docker compose config --volumes
docker volume ls
```

## Backup and Restore

Keep the complete stack running, then create one consistent bundle:

```bash
./scripts/backup-local-state.sh
```

The default destination is `./backups/txt2crs_backup_<UTC timestamp>/`.
`BACKUP_RETENTION_DAYS` defaults to seven days and controls cleanup of older
complete bundle directories:

```bash
BACKUP_RETENTION_DAYS=30 ./scripts/backup-local-state.sh
```

Each bundle contains:

- `postgres.dump`, a validated PostgreSQL custom-format dump;
- `engine-state.tar.gz`, containing SQLite jobs, artifacts, and durable
  isolated Codex-home data while the backend writer is stopped; and
- `manifest.json` and `SHA256SUMS`.

The archive omits `codex-home/tmp`. Codex recreates that directory at startup,
and its contents include absolute links to executables in the current image
rather than credentials or durable job state. Symlinks anywhere else in the
private state root still make backup fail closed.

The directory is mode `0700` and its files are mode `0600`. Treat the complete
bundle as a secret: it can contain learner data, generated course content, and
Codex credentials. Git ignores the default `backups/` path, but operators must
still copy required bundles to encrypted, access-controlled storage.

Restore replaces both current stores. It validates every checksum, the
PostgreSQL catalog, and all archive paths before it stops the backend or
deletes current data:

```bash
TXT2CRS_RESTORE_CONFIRM=replace-local-state \
  ./scripts/restore-local-state.sh \
  ./backups/txt2crs_backup_<UTC timestamp>
```

Run the health checks at the top of this guide after restore. The scripts
discover the Compose-prefixed engine volume from the backend container, so the
same commands also work with an explicit `COMPOSE_PROJECT_NAME`.

`scripts/backup-db.sh` is a legacy PostgreSQL-only helper. It does not capture
engine job state, artifacts, or credentials and must not be used as the sole
application backup.

## Destructive Reset

The following command permanently deletes both named volumes:

```bash
docker compose down --remove-orphans --volumes
```

Use it only when a disposable local environment is intended. It deletes users,
application records, engine jobs, rendered artifacts, and locally stored Codex
credentials. The command does not create a backup; run the complete backup
command above first when the state may be needed again.

## Targeted Rebuilds

Rebuild only the affected deployable unit:

```bash
docker compose up --detach --build --wait backend
docker compose up --detach --build --wait frontend
```

Inspect failures with:

```bash
docker compose ps
docker compose logs backend
docker compose logs frontend
docker compose logs db
```

Avoid global Docker prune commands in routine project work because they can
remove unrelated projects' cache, images, or volumes.

## Full Validation

Run the repository gate after a rebuild:

```bash
./scripts/validate-changes.sh
```

This local workflow is the complete deployment scope. See
[Deployment](deployment.md) and
[deployment policy](deployment-policy.md) for the release contract.
