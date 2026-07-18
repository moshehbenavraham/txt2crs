#! /usr/bin/env bash

set -e
set -x

uv run --directory backend python -c "import logging; logging.disable(logging.CRITICAL); import app.main; import json; print(json.dumps(app.main.app.openapi()))" > frontend/openapi.json
npm --prefix frontend run generate-client
(
    cd frontend
    npm exec -- biome check --write --unsafe --no-errors-on-unmatched --files-ignore-unknown=true src/client
)
