#!/usr/bin/env bash

set -e
set -x

uv run mypy app
uv run ty check app

# The backend pyproject excludes the independently configured workspace package,
# so these commands cover only shell source and shell tests. The engine runs its
# own checks from packages/txt2crs in CI, where its own pyproject applies.
uv run ruff check app tests
uv run ruff format app tests --check
