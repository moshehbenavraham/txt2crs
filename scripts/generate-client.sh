#! /usr/bin/env bash

set -e
set -x

uv run --directory backend python -c "import logging; logging.disable(logging.CRITICAL); import app.main; import json; print(json.dumps(app.main.app.openapi()))" > frontend/openapi.json
npm --prefix frontend run generate-client
(
    cd frontend
    # The OpenAPI export is emitted as one compact JSON line. Format it in the
    # same step as the generated client so this script cannot leave a later
    # Biome hook or validation run dirty.
    npm exec -- biome check --write --unsafe --no-errors-on-unmatched --files-ignore-unknown=true openapi.json src/client
)
