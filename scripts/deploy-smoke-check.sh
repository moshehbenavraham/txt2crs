#!/usr/bin/env bash

set -euo pipefail

BACKEND_URL="${1:-}"
FRONTEND_URL="${2:-}"
RETRIES="${RETRIES:-12}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"
CURL_TIMEOUT="${CURL_TIMEOUT:-10}"

if [[ -z "$BACKEND_URL" || -z "$FRONTEND_URL" ]]; then
  echo "Usage: deploy-smoke-check.sh <backend-url> <frontend-url>"
  exit 1
fi

check_url() {
  local name="$1"
  local url="$2"
  local attempt=1

  while [[ "$attempt" -le "$RETRIES" ]]; do
    if curl --fail --silent --show-error --max-time "$CURL_TIMEOUT" "$url" >/dev/null; then
      echo "[smoke] ${name} OK: ${url}"
      return 0
    fi

    echo "[smoke] ${name} failed (attempt ${attempt}/${RETRIES}): ${url}"
    if [[ "$attempt" -lt "$RETRIES" ]]; then
      sleep "$SLEEP_SECONDS"
    fi
    attempt=$((attempt + 1))
  done

  echo "[smoke] ${name} FAILED after ${RETRIES} attempts: ${url}"
  return 1
}

check_url "backend" "$BACKEND_URL"
check_url "frontend" "$FRONTEND_URL"

echo "[smoke] All deploy smoke checks passed."
