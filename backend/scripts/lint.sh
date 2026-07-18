#!/usr/bin/env bash

set -e
set -x

uv run mypy app
uv run ty check app
uv run ruff check app
uv run ruff format app --check
