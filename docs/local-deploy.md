# Local Deployment and Rebuilds

The supported local deployment is the repository-root Docker Compose stack.
For service URLs and direct development commands, see
[Development](development.md).

## Start or Rebuild

Create `.env` from the tracked example if it does not exist:

```bash
cp .env.example .env
docker compose up --detach --build --wait
```

Docker reports the database, backend, and frontend as healthy before the
command succeeds. Verify the public local probes:

```bash
curl --fail http://localhost:8012/health
curl --fail http://localhost:5183/health
```

The backend response includes application, version, and database status. The
frontend response is:

```json
{"status":"healthy","service":"frontend"}
```

## Stop Without Deleting Data

```bash
docker compose down --remove-orphans
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

## Destructive Reset

The following command permanently deletes both named volumes:

```bash
docker compose down --remove-orphans --volumes
```

Use it only when a disposable local environment is intended. It deletes users,
application records, engine jobs, rendered artifacts, and locally stored Codex
credentials. The command does not create a backup.

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
