#!/usr/bin/env bash
#
# Authenticate the dedicated txt2crs ChatGPT identity with one short command.
#
# The packaged Python entry point owns the actual device-code flow. This helper
# only resolves repository paths, protects the ignored credential directory,
# and forwards optional CLI flags such as --no-browser.
#
# Usage:
#   ./scripts/auth-codex.sh [txt2crs-system-auth options]
#

set -euo pipefail
umask 077

SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPOSITORY_ROOT="$(dirname -- "$SCRIPT_DIRECTORY")"
BACKEND_DIRECTORY="$REPOSITORY_ROOT/backend"
STATE_DIRECTORY="$REPOSITORY_ROOT/.txt2crs-system"

if ! command -v uv >/dev/null 2>&1; then
    echo "Required command is unavailable: uv" >&2
    exit 127
fi
if [[ ! -d "$BACKEND_DIRECTORY" ]]; then
    echo "Backend directory is missing: $BACKEND_DIRECTORY" >&2
    exit 1
fi

# Device credentials must remain owner-only even if the operator's default
# shell umask is permissive. The packaged CLI separately protects its worker
# and CODEX_HOME children.
mkdir -p -- "$STATE_DIRECTORY"
chmod 700 -- "$STATE_DIRECTORY"

cd -- "$BACKEND_DIRECTORY"
exec uv run --package txt2crs txt2crs-system-auth \
    --state-directory "$STATE_DIRECTORY" \
    "$@"
