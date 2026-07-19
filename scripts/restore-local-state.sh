#!/usr/bin/env bash
#
# Replace every durable local deployment store from one verified backup bundle.
#
# This operation is intentionally destructive and fails closed unless the
# caller supplies the exact confirmation value documented below.  Checksums,
# the PostgreSQL dump catalog, and every engine archive member are validated
# before the backend is stopped or current data is replaced.
#
# Usage:
#   TXT2CRS_RESTORE_CONFIRM=replace-local-state \
#     ./scripts/restore-local-state.sh ./backups/txt2crs_backup_<timestamp>
#

set -euo pipefail
umask 077

SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE_HELPER="$SCRIPT_DIRECTORY/local_state_archive.py"
BUNDLE_DIRECTORY="${1:-}"
COMPOSE_COMMAND=(docker compose)

if [[ "${TXT2CRS_RESTORE_CONFIRM:-}" != "replace-local-state" ]]; then
    echo "Restore refused. Set TXT2CRS_RESTORE_CONFIRM=replace-local-state." >&2
    exit 2
fi
if [[ -z "$BUNDLE_DIRECTORY" ]]; then
    echo "Usage: restore-local-state.sh <backup_bundle_directory>" >&2
    exit 2
fi
if [[ ! -d "$BUNDLE_DIRECTORY" || -L "$BUNDLE_DIRECTORY" ]]; then
    echo "Backup bundle must be a real directory: $BUNDLE_DIRECTORY" >&2
    exit 2
fi
BUNDLE_DIRECTORY="$(cd "$BUNDLE_DIRECTORY" && pwd -P)"

for required_file in SHA256SUMS postgres.dump engine-state.tar.gz manifest.json; do
    if [[ ! -f "$BUNDLE_DIRECTORY/$required_file" || -L "$BUNDLE_DIRECTORY/$required_file" ]]; then
        echo "Backup bundle file is missing or unsafe: $required_file" >&2
        exit 2
    fi
done

echo "Checking bundle hashes..."
(
    cd "$BUNDLE_DIRECTORY"
    sha256sum --check SHA256SUMS
)

BACKEND_CONTAINER_ID="$("${COMPOSE_COMMAND[@]}" ps -aq backend)"
if [[ -z "$BACKEND_CONTAINER_ID" ]]; then
    echo "The backend container does not exist. Run 'docker compose up -d --wait' first." >&2
    exit 1
fi
ENGINE_VOLUME_NAME="$(
    docker inspect "$BACKEND_CONTAINER_ID" \
        --format '{{range .Mounts}}{{if eq .Destination "/var/lib/txt2crs"}}{{.Name}}{{end}}{{end}}'
)"
if [[ -z "$ENGINE_VOLUME_NAME" ]]; then
    echo "The backend has no named volume mounted at /var/lib/txt2crs." >&2
    exit 1
fi
BACKEND_IMAGE="${LOCAL_STATE_ARCHIVE_IMAGE:-$(
    docker inspect "$BACKEND_CONTAINER_ID" --format '{{.Config.Image}}'
)}"

# Both parsers run before dropdb or the state-replacement command.  A corrupt
# or traversal-bearing bundle therefore leaves the current deployment intact.
"${COMPOSE_COMMAND[@]}" exec -T db pg_restore --list \
    <"$BUNDLE_DIRECTORY/postgres.dump" >/dev/null
docker run --rm --user 0:0 \
    --volume "$BUNDLE_DIRECTORY:/backup:ro" \
    --volume "$ARCHIVE_HELPER:/opt/txt2crs/local_state_archive.py:ro" \
    "$BACKEND_IMAGE" \
    python /opt/txt2crs/local_state_archive.py validate \
    /backup/engine-state.tar.gz

BACKEND_WAS_RUNNING="$(
    docker inspect "$BACKEND_CONTAINER_ID" --format '{{.State.Running}}'
)"
RESTORE_COMPLETED=false

restart_backend_after_restore() {
    # Even when a later restore command fails, return a previously running
    # service to the operator so its health and logs can expose the problem.
    if [[ "$BACKEND_WAS_RUNNING" == "true" && "$RESTORE_COMPLETED" != "true" ]]; then
        "${COMPOSE_COMMAND[@]}" up -d backend >/dev/null || true
    fi
}
trap restart_backend_after_restore EXIT

if [[ "$BACKEND_WAS_RUNNING" == "true" ]]; then
    echo "Stopping the backend writer before replacing local state..."
    "${COMPOSE_COMMAND[@]}" stop backend >/dev/null
fi

echo "Replacing the PostgreSQL database..."
"${COMPOSE_COMMAND[@]}" exec -T db sh -ec \
    'dropdb --if-exists --force -U "$POSTGRES_USER" "$POSTGRES_DB"
     createdb -U "$POSTGRES_USER" "$POSTGRES_DB"'
"${COMPOSE_COMMAND[@]}" exec -T db sh -ec \
    'exec pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --exit-on-error --no-owner --no-acl' \
    <"$BUNDLE_DIRECTORY/postgres.dump"

echo "Replacing private engine state..."
docker run --rm --user 0:0 \
    --volume "$ENGINE_VOLUME_NAME:/state" \
    --volume "$BUNDLE_DIRECTORY:/backup:ro" \
    --volume "$ARCHIVE_HELPER:/opt/txt2crs/local_state_archive.py:ro" \
    "$BACKEND_IMAGE" \
    python /opt/txt2crs/local_state_archive.py restore \
    /backup/engine-state.tar.gz /state

if [[ "$BACKEND_WAS_RUNNING" == "true" ]]; then
    "${COMPOSE_COMMAND[@]}" up -d --wait backend >/dev/null
fi
RESTORE_COMPLETED=true
trap - EXIT

echo "Restore completed from: $BUNDLE_DIRECTORY"
