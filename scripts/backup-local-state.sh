#!/usr/bin/env bash
#
# Create one owner-only backup bundle for every durable local deployment store.
#
# The backend is briefly stopped so SQLite/WAL files, generated artifacts, and
# Codex credentials in /var/lib/txt2crs are captured at a stable point.  The
# PostgreSQL custom-format dump and engine-state archive are checksum protected
# in the same timestamped directory.
#
# Usage:
#   ./scripts/backup-local-state.sh [output_directory]
#
# Optional:
#   BACKUP_RETENTION_DAYS=7  Remove older complete backup bundle directories.
#

set -euo pipefail
umask 077

SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(dirname "$SCRIPT_DIRECTORY")"
ARCHIVE_HELPER="$SCRIPT_DIRECTORY/local_state_archive.py"
OUTPUT_DIRECTORY="${1:-$REPOSITORY_ROOT/backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
BACKUP_TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
BUNDLE_NAME="txt2crs_backup_${BACKUP_TIMESTAMP}"
HOST_USER_ID="$(id -u)"
HOST_GROUP_ID="$(id -g)"

# Keeping this literal command in one array preserves caller-supplied Compose
# variables such as COMPOSE_FILE and COMPOSE_PROJECT_NAME.
COMPOSE_COMMAND=(docker compose)

if ! [[ "$BACKUP_RETENTION_DAYS" =~ ^[0-9]+$ ]]; then
    echo "BACKUP_RETENTION_DAYS must be a non-negative integer." >&2
    exit 2
fi
for required_command in docker sha256sum python3; do
    if ! command -v "$required_command" >/dev/null 2>&1; then
        echo "Required command is unavailable: $required_command" >&2
        exit 2
    fi
done
if [[ ! -f "$ARCHIVE_HELPER" ]]; then
    echo "Archive helper is missing: $ARCHIVE_HELPER" >&2
    exit 2
fi

mkdir -p "$OUTPUT_DIRECTORY"
chmod 700 "$OUTPUT_DIRECTORY"
OUTPUT_DIRECTORY="$(cd "$OUTPUT_DIRECTORY" && pwd -P)"
BUNDLE_DIRECTORY="$OUTPUT_DIRECTORY/$BUNDLE_NAME"
mkdir "$BUNDLE_DIRECTORY"
chmod 700 "$BUNDLE_DIRECTORY"

BACKEND_CONTAINER_ID="$("${COMPOSE_COMMAND[@]}" ps -aq backend)"
if [[ -z "$BACKEND_CONTAINER_ID" ]]; then
    echo "The backend container does not exist. Run 'docker compose up -d --wait' first." >&2
    exit 1
fi

# Discover the concrete Compose-prefixed volume instead of guessing its name.
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
BACKEND_WAS_RUNNING="$(
    docker inspect "$BACKEND_CONTAINER_ID" --format '{{.State.Running}}'
)"

restart_backend_after_backup() {
    # A failed dump must not accidentally leave a previously healthy local
    # deployment offline after the maintenance command exits.
    if [[ "$BACKEND_WAS_RUNNING" == "true" ]]; then
        "${COMPOSE_COMMAND[@]}" up -d --wait backend >/dev/null || true
    fi
}
trap restart_backend_after_backup EXIT

if [[ "$BACKEND_WAS_RUNNING" == "true" ]]; then
    echo "Stopping the backend writer for a consistent engine-state snapshot..."
    "${COMPOSE_COMMAND[@]}" stop backend >/dev/null
fi

echo "Creating PostgreSQL custom-format dump..."
"${COMPOSE_COMMAND[@]}" exec -T db sh -ec \
    'exec pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' \
    >"$BUNDLE_DIRECTORY/postgres.dump"
chmod 600 "$BUNDLE_DIRECTORY/postgres.dump"

# Use the already-running backend image as the Python runtime.  Root is needed
# only inside this short-lived maintenance container so private owner-only
# files can be read and their numeric ownership can be recorded.
echo "Creating private engine-state archive..."
docker run --rm --user 0:0 \
    --volume "$ENGINE_VOLUME_NAME:/state:ro" \
    --volume "$BUNDLE_DIRECTORY:/backup" \
    --volume "$ARCHIVE_HELPER:/opt/txt2crs/local_state_archive.py:ro" \
    "$BACKEND_IMAGE" \
    sh -ec '
        python /opt/txt2crs/local_state_archive.py create \
            /state /backup/engine-state.tar.gz
        chown "$1:$2" /backup/engine-state.tar.gz
    ' maintenance "$HOST_USER_ID" "$HOST_GROUP_ID"

docker run --rm --user 0:0 \
    --volume "$BUNDLE_DIRECTORY:/backup:ro" \
    --volume "$ARCHIVE_HELPER:/opt/txt2crs/local_state_archive.py:ro" \
    "$BACKEND_IMAGE" \
    python /opt/txt2crs/local_state_archive.py validate \
    /backup/engine-state.tar.gz

# pg_restore --list parses the complete custom-format catalog without writing.
"${COMPOSE_COMMAND[@]}" exec -T db pg_restore --list \
    <"$BUNDLE_DIRECTORY/postgres.dump" >/dev/null

python3 - "$BUNDLE_DIRECTORY/manifest.json" "$BACKUP_TIMESTAMP" <<'PYTHON'
"""Write machine-readable bundle metadata without exposing environment secrets."""
import json
import os
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
manifest = {
    "format_version": 1,
    "created_at_utc": sys.argv[2],
    "compose_project": os.getenv("COMPOSE_PROJECT_NAME", "default"),
    "files": ["postgres.dump", "engine-state.tar.gz"],
}
manifest_path.write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
PYTHON
chmod 600 "$BUNDLE_DIRECTORY/manifest.json"

(
    cd "$BUNDLE_DIRECTORY"
    sha256sum postgres.dump engine-state.tar.gz manifest.json >SHA256SUMS
)
chmod 600 "$BUNDLE_DIRECTORY/SHA256SUMS"

if [[ "$BACKUP_RETENTION_DAYS" -gt 0 ]]; then
    find "$OUTPUT_DIRECTORY" \
        -mindepth 1 -maxdepth 1 -type d \
        -name 'txt2crs_backup_*' \
        ! -path "$BUNDLE_DIRECTORY" \
        -mtime +"$BACKUP_RETENTION_DAYS" \
        -exec rm -rf -- {} +
fi

if [[ "$BACKEND_WAS_RUNNING" == "true" ]]; then
    "${COMPOSE_COMMAND[@]}" up -d --wait backend >/dev/null
fi
trap - EXIT

echo "Backup completed: $BUNDLE_DIRECTORY"
echo "Store this directory securely; it contains learner data and Codex credentials."
