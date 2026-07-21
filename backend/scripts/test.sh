#!/usr/bin/env bash

set -e
set -x

python -m tests.database_safety
coverage run -m pytest tests/
coverage report
coverage html --title "${@-coverage}"
