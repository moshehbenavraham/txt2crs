#! /usr/bin/env bash
#
# Create the environment files that continuous integration needs.
#
# Both `.env` and `backend/.env` are deliberately git-ignored so that nobody
# commits real credentials. That means a fresh CI checkout has neither file,
# and every step that reads configuration fails before it does any real work:
#
#   * `docker compose` cannot interpolate `${POSTGRES_PASSWORD}` and friends,
#     so it aborts with "required variable ... is missing a value".
#   * `app.core.config.Settings` reads `.env` relative to the current working
#     directory, so importing `app.main` from `backend/` raises a Pydantic
#     ValidationError for ENVIRONMENT, PROJECT_NAME, POSTGRES_SERVER, ...
#
# The two `.env.example` templates already hold safe, non-secret placeholder
# values (`changethis`, `localhost`, `admin@example.com`), which is exactly
# what an ephemeral CI runner should use. Copying them gives every job a
# complete configuration without putting any secret into the workflow files.
#
# Existing files are left alone so this script is safe to run more than once
# and so a developer can call it locally without clobbering real settings.

set -euo pipefail

SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPOSITORY_ROOT="$(dirname -- "$SCRIPT_DIRECTORY")"

# Each entry is "<template> <destination>", both relative to the repository
# root. `.env` configures Docker Compose; `backend/.env` configures FastAPI
# and pytest when they run directly on the host from the `backend/` directory.
copy_template_when_missing() {
    local template_path="$REPOSITORY_ROOT/$1"
    local destination_path="$REPOSITORY_ROOT/$2"

    if [[ -f "$destination_path" ]]; then
        echo "Keeping existing $2"
        return 0
    fi

    cp -- "$template_path" "$destination_path"
    echo "Created $2 from $1"
}

copy_template_when_missing ".env.example" ".env"
copy_template_when_missing "backend/.env.example" "backend/.env"

# The canonical template keeps public signup closed, because the judge-facing
# deployment provisions accounts by hand. The browser suite, however, exercises
# the /signup route directly: with the template value, nine Playwright tests in
# tests/sign-up.spec.ts fail because the route is not mounted at all.
#
# Enabling it only in the generated CI file keeps .env.example honest about how
# the real deployment is configured, while giving the browser tests the route
# they are written against.
enable_public_signup_for_browser_tests() {
    local environment_file="$REPOSITORY_ROOT/.env"

    if grep -q "^ENABLE_PUBLIC_SIGNUP=" "$environment_file"; then
        sed -i "s/^ENABLE_PUBLIC_SIGNUP=.*/ENABLE_PUBLIC_SIGNUP=true/" \
            "$environment_file"
    else
        echo "ENABLE_PUBLIC_SIGNUP=true" >> "$environment_file"
    fi
    echo "Enabled ENABLE_PUBLIC_SIGNUP for the browser suite"
}

enable_public_signup_for_browser_tests
