#!/usr/bin/env bash
#
# Compatibility entrypoint for the retired donor-era clean rebuild helper.
#
# The canonical local deployment command is now start-local.sh. The old helper
# used hardcoded boilerplate resource names and globally pruned Docker state,
# so it has been replaced with this safe delegating wrapper.
#

set -Eeuo pipefail

SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
FORWARDED_ARGUMENTS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-cache)
            # start-local.sh uses Docker's normal cache by default, so the old
            # option is now equivalent to the default behavior.
            ;;
        --nuclear)
            printf '%s\n' \
                "Destructive reset mode was removed from this judge-safe command." \
                "Use the documented manual reset only when data loss is intended." >&2
            exit 2
            ;;
        *)
            FORWARDED_ARGUMENTS+=("$1")
            ;;
    esac
    shift
done

printf '%s\n' \
    "Notice: deploy-local-clean.sh now delegates to scripts/start-local.sh." >&2
exec "$SCRIPT_DIRECTORY/start-local.sh" "${FORWARDED_ARGUMENTS[@]}"
