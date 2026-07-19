#!/usr/bin/env bash
#
# Build and exercise the backend production image without external credentials.
#
# This smoke test complements the fast static contract tests. It proves the
# actual built image can import the workspace engine, starts as the fixed
# non-root user, creates owner-only private files, and can reopen state from a
# replacement container using the same named volume.

set -euo pipefail

SCRIPT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIRECTORY
PROJECT_ROOT="$(dirname "$SCRIPT_DIRECTORY")"
readonly PROJECT_ROOT
readonly IMAGE_NAME="${TXT2CRS_BASELINE_IMAGE:-txt2crs-baseline:local}"
RESOURCE_SUFFIX="$(id -u)-$$"
readonly RESOURCE_SUFFIX
readonly STATE_VOLUME_NAME="txt2crs-baseline-state-${RESOURCE_SUFFIX}"
readonly WRITER_CONTAINER_NAME="txt2crs-baseline-writer-${RESOURCE_SUFFIX}"
readonly READER_CONTAINER_NAME="txt2crs-baseline-reader-${RESOURCE_SUFFIX}"
readonly EXPECTED_IMAGE_COMMAND='["fastapi","run","app/main.py"]'

cleanup() {
    # Cleanup is deliberately idempotent because the trap also runs after an
    # assertion failure. Suppress only cleanup errors, never test failures.
    docker rm --force \
        "$WRITER_CONTAINER_NAME" \
        "$READER_CONTAINER_NAME" >/dev/null 2>&1 || true
    docker volume rm --force "$STATE_VOLUME_NAME" >/dev/null 2>&1 || true
}

trap cleanup EXIT INT TERM

echo "[baseline] Building production backend image: ${IMAGE_NAME}"
docker build \
    --target production \
    --tag "$IMAGE_NAME" \
    "$PROJECT_ROOT/backend"

configured_user="$(docker image inspect --format '{{.Config.User}}' "$IMAGE_NAME")"
if [[ "$configured_user" != "appuser" ]]; then
    echo "[baseline] Expected image user appuser, found: ${configured_user}" >&2
    exit 1
fi

configured_command="$(docker image inspect --format '{{json .Config.Cmd}}' "$IMAGE_NAME")"
if [[ "$configured_command" != "$EXPECTED_IMAGE_COMMAND" ]]; then
    echo "[baseline] Expected one-process command ${EXPECTED_IMAGE_COMMAND}" >&2
    echo "[baseline] Found command: ${configured_command}" >&2
    exit 1
fi

echo "[baseline] Verifying workspace engine import"
docker run \
    --rm \
    --entrypoint python \
    "$IMAGE_NAME" \
    -c "import txt2crs; print(txt2crs.__name__)"

docker volume create "$STATE_VOLUME_NAME" >/dev/null

echo "[baseline] Writing private state as the image runtime user"
docker run \
    --name "$WRITER_CONTAINER_NAME" \
    --volume "${STATE_VOLUME_NAME}:/var/lib/txt2crs" \
    --entrypoint sh \
    "$IMAGE_NAME" \
    -eu -c '
        test "$(id -u)" = "1001"
        test "$(stat -c %a /var/lib/txt2crs)" = "700"
        umask 077
        printf "txt2crs-baseline-ok\n" > /var/lib/txt2crs/baseline-marker
        test "$(stat -c %a /var/lib/txt2crs/baseline-marker)" = "600"
    '
docker rm "$WRITER_CONTAINER_NAME" >/dev/null

echo "[baseline] Reopening state from a replacement container"
docker run \
    --name "$READER_CONTAINER_NAME" \
    --volume "${STATE_VOLUME_NAME}:/var/lib/txt2crs" \
    --entrypoint sh \
    "$IMAGE_NAME" \
    -eu -c '
        test "$(id -u)" = "1001"
        test "$(cat /var/lib/txt2crs/baseline-marker)" = "txt2crs-baseline-ok"
    '
docker rm "$READER_CONTAINER_NAME" >/dev/null

echo "[baseline] PASS - import, one process, non-root state, and reopen verified"
