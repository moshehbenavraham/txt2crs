#! /usr/bin/env bash

set -euo pipefail

SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPOSITORY_ROOT="$(dirname -- "$SCRIPT_DIRECTORY")"
OPENAPI_DOCUMENT="$REPOSITORY_ROOT/frontend/openapi.json"

# Write beside the final document so ``mv`` performs one atomic rename on the
# same filesystem. Contract tests and editor tooling may read this ignored
# intermediate while generation runs; they must see either the previous
# complete JSON document or the next complete document, never a truncated one.
TEMPORARY_OPENAPI_DOCUMENT="$(
    mktemp "$REPOSITORY_ROOT/frontend/.openapi.json.XXXXXX"
)"

cleanup_temporary_openapi_document() {
    if [[ -f "$TEMPORARY_OPENAPI_DOCUMENT" ]]; then
        unlink -- "$TEMPORARY_OPENAPI_DOCUMENT"
    fi
}
trap cleanup_temporary_openapi_document EXIT

cd -- "$REPOSITORY_ROOT"
set -x

uv run --directory backend python -c "import logging; logging.disable(logging.CRITICAL); import app.main; import json; print(json.dumps(app.main.app.openapi()))" > "$TEMPORARY_OPENAPI_DOCUMENT"
mv -- "$TEMPORARY_OPENAPI_DOCUMENT" "$OPENAPI_DOCUMENT"
trap - EXIT
# The internal frontend command owns formatting and ASCII normalization. The
# public npm command delegates back to this wrapper first so a clean checkout
# also receives a fresh server-owned OpenAPI document.
npm --prefix frontend run generate-client:codegen
