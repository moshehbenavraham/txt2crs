#!/usr/bin/env bash

set -euo pipefail

STACK_NAME="${STACK_NAME:-}"
BACKEND_PREV_IMAGE_ID="${BACKEND_PREV_IMAGE_ID:-}"
FRONTEND_PREV_IMAGE_ID="${FRONTEND_PREV_IMAGE_ID:-}"

if [[ -z "$STACK_NAME" ]]; then
  echo "[rollback] STACK_NAME is required."
  exit 1
fi

if [[ -z "$BACKEND_PREV_IMAGE_ID" || -z "$FRONTEND_PREV_IMAGE_ID" ]]; then
  echo "[rollback] Missing previous image IDs; cannot perform automated rollback."
  exit 1
fi

docker image inspect "$BACKEND_PREV_IMAGE_ID" >/dev/null
docker image inspect "$FRONTEND_PREV_IMAGE_ID" >/dev/null

TAG_SUFFIX="${GITHUB_RUN_ID:-manual}-$(date +%s)"
BACKEND_ROLLBACK_IMAGE="local/rollback-backend:${TAG_SUFFIX}"
FRONTEND_ROLLBACK_IMAGE="local/rollback-frontend:${TAG_SUFFIX}"

echo "[rollback] Tagging previous images for rollback."
docker image tag "$BACKEND_PREV_IMAGE_ID" "$BACKEND_ROLLBACK_IMAGE"
docker image tag "$FRONTEND_PREV_IMAGE_ID" "$FRONTEND_ROLLBACK_IMAGE"

OVERRIDE_FILE="$(mktemp)"
cleanup() {
  rm -f "$OVERRIDE_FILE"
}
trap cleanup EXIT

cat >"$OVERRIDE_FILE" <<EOF
services:
  prestart:
    image: ${BACKEND_ROLLBACK_IMAGE}
  backend:
    image: ${BACKEND_ROLLBACK_IMAGE}
  frontend:
    image: ${FRONTEND_ROLLBACK_IMAGE}
EOF

echo "[rollback] Restoring previous backend/frontend images."
docker compose \
  -f docker-compose.yml \
  -f "$OVERRIDE_FILE" \
  --project-name "$STACK_NAME" \
  up -d --force-recreate prestart backend frontend

echo "[rollback] Rollback command completed."
