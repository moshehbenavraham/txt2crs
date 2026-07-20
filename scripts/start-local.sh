#!/usr/bin/env bash
#
# start-local.sh - Safe, judge-friendly txt2crs local deployment
#
# This command is the human-friendly wrapper around the repository's
# authoritative Docker Compose deployment. It validates configuration and
# local prerequisites before building, then lets Compose wait for the declared
# database, backend, and frontend health checks.
#
# The script is intentionally non-destructive:
# - it never sources .env as executable shell code;
# - it never prints configured secret values;
# - it never prunes Docker images or build cache; and
# - it never deletes named volumes.
#
# Usage:
#   ./scripts/start-local.sh
#   ./scripts/start-local.sh --no-build
#   ./scripts/start-local.sh --status
#   ./scripts/start-local.sh --stop
#

set -Eeuo pipefail

SCRIPT_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIRECTORY="$(dirname -- "$SCRIPT_DIRECTORY")"
ENVIRONMENT_FILE="$PROJECT_DIRECTORY/.env"

FRONTEND_URL=""
BACKEND_DOCUMENTATION_URL=""
SYSTEM_SETUP_URL=""

ACTION="start"
BUILD_IMAGES=true
SHOW_HELP=false
COLOR_ENABLED=true

# Compose references CI for the optional Playwright service. Exporting an
# explicit empty value avoids a distracting warning during judge startup.
export CI="${CI:-}"

show_usage() {
    cat <<'EOF'
Usage: ./scripts/start-local.sh [OPTION]

Build and start the complete local txt2crs application with Docker Compose.

Options:
  --no-build   Start with existing images instead of rebuilding them.
  --status     Show the current Compose service status without changing it.
  --stop       Stop the stack while preserving databases and generated files.
  --no-color   Disable ANSI terminal colors.
  --help, -h   Show this help message.

The command is safe to run repeatedly. It never prunes Docker state and never
deletes the PostgreSQL or txt2crs state volumes.
EOF
}

# Parse arguments before color setup so --no-color applies to every message.
while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-build)
            BUILD_IMAGES=false
            ;;
        --status)
            ACTION="status"
            ;;
        --stop)
            ACTION="stop"
            ;;
        --no-color)
            COLOR_ENABLED=false
            ;;
        --help|-h)
            SHOW_HELP=true
            ;;
        *)
            printf 'Unknown option: %s\n\n' "$1" >&2
            show_usage >&2
            exit 2
            ;;
    esac
    shift
done

if [[ ! -t 1 || -n "${NO_COLOR:-}" || "$COLOR_ENABLED" != true ]]; then
    RED=""
    GREEN=""
    YELLOW=""
    BLUE=""
    CYAN=""
    BOLD=""
    RESET=""
else
    RED=$'\033[31m'
    GREEN=$'\033[32m'
    YELLOW=$'\033[33m'
    BLUE=$'\033[34m'
    CYAN=$'\033[36m'
    BOLD=$'\033[1m'
    RESET=$'\033[0m'
fi

print_banner() {
    printf '%s' "$CYAN"
    cat <<'EOF'

  TTTTT X   X TTTTT  2222    CCCC RRRR   SSSS
    T    X X    T       2   C     R   R S
    T     X     T    222    C     RRRR   SSS
    T    X X    T    2      C     R  R      S
    T   X   X   T    22222   CCCC R   R SSSS

EOF
    printf '%s' "$RESET"
    printf '%s\n' \
        "${BOLD}+--------------------------------------------------------------+${RESET}" \
        "${BOLD}|       INPUT TO COURSE - LOCAL JUDGE DEPLOYMENT               |${RESET}" \
        "${BOLD}+--------------------------------------------------------------+${RESET}"
}

print_section() {
    local section_title="$1"
    printf '\n%s%s%s\n' "$BLUE" "--------------------------------------------------------------" "$RESET"
    printf '%s%s%s\n' "$BOLD" "$section_title" "$RESET"
    printf '%s%s%s\n' "$BLUE" "--------------------------------------------------------------" "$RESET"
}

print_error_heading() {
    local heading="$1"
    printf '\n%s%s+--------------------------------------------------------------+%s\n' \
        "$RED" "$BOLD" "$RESET" >&2
    printf '%s%s| %-60s |%s\n' "$RED" "$BOLD" "$heading" "$RESET" >&2
    printf '%s%s+--------------------------------------------------------------+%s\n' \
        "$RED" "$BOLD" "$RESET" >&2
}

print_success_line() {
    printf '%s[OK]%s %s\n' "$GREEN" "$RESET" "$1"
}

print_info_line() {
    printf '%s[INFO]%s %s\n' "$CYAN" "$RESET" "$1"
}

print_warning_line() {
    printf '%s[WARN]%s %s\n' "$YELLOW" "$RESET" "$1"
}

print_banner

if [[ "$SHOW_HELP" == true ]]; then
    printf '\n'
    show_usage
    exit 0
fi

print_missing_environment_instructions() {
    print_error_heading "CONFIGURATION REQUIRED"
    cat >&2 <<'EOF'

The repository-root .env file does not exist.

From the repository root:

  1. cp .env.example .env
  2. Open .env in a text editor.
  3. Replace the values for:
       SECRET_KEY
       POSTGRES_PASSWORD
       FIRST_SUPERUSER_PASSWORD
       TAVILY_API_KEY
  4. Run ./scripts/start-local.sh again.

Do not commit .env. It contains local credentials.
EOF
}

# Configuration is checked before Docker so a fresh-clone judge gets the most
# useful instruction first, even when Docker Desktop is not running yet.
if [[ ! -f "$ENVIRONMENT_FILE" ]]; then
    print_missing_environment_instructions
    exit 2
fi

# Read one dotenv value as inert text. Sourcing .env would allow shell syntax in
# that file to execute, which is unnecessary and unsafe for a setup helper.
read_environment_value() {
    local setting_name="$1"
    local environment_line
    local raw_value
    local trimmed_value
    local first_character
    local last_character
    local selected_value=""
    local setting_was_found=false

    while IFS= read -r environment_line || [[ -n "$environment_line" ]]; do
        environment_line="${environment_line%$'\r'}"
        if [[ "$environment_line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        if [[ "$environment_line" =~ ^[[:space:]]*${setting_name}[[:space:]]*=(.*)$ ]]; then
            raw_value="${BASH_REMATCH[1]}"

            # Remove surrounding whitespace while preserving spaces inside a
            # quoted or unquoted value.
            trimmed_value="${raw_value#"${raw_value%%[![:space:]]*}"}"
            trimmed_value="${trimmed_value%"${trimmed_value##*[![:space:]]}"}"

            if [[ ${#trimmed_value} -ge 2 ]]; then
                first_character="${trimmed_value:0:1}"
                last_character="${trimmed_value: -1}"
                if [[ "$first_character" == '"' && "$last_character" == '"' ]] ||
                    [[ "$first_character" == "'" && "$last_character" == "'" ]]; then
                    trimmed_value="${trimmed_value:1:${#trimmed_value}-2}"
                fi
            fi

            # Docker Compose uses the final assignment when a dotenv key is
            # repeated. Keep scanning so validation sees that same value.
            selected_value="$trimmed_value"
            setting_was_found=true
        fi
    done < "$ENVIRONMENT_FILE"

    if [[ "$setting_was_found" == true ]]; then
        printf '%s' "$selected_value"
        return 0
    fi

    return 1
}

CONFIGURATION_ERRORS=""
CONFIGURED_HOST_PORT_NAMES=()
CONFIGURED_HOST_PORT_VALUES=()

add_configuration_error() {
    CONFIGURATION_ERRORS="${CONFIGURATION_ERRORS}- $1"$'\n'
}

validate_required_setting() {
    local setting_name="$1"
    local setting_value

    if ! setting_value="$(read_environment_value "$setting_name")" ||
        [[ -z "$setting_value" ]]; then
        add_configuration_error "$setting_name is missing or empty."
    fi
}

validate_secret_setting() {
    local setting_name="$1"
    local setting_value
    local normalized_value

    if ! setting_value="$(read_environment_value "$setting_name")" ||
        [[ -z "$setting_value" ]]; then
        add_configuration_error "$setting_name is missing or empty."
        return
    fi

    normalized_value="$(printf '%s' "$setting_value" | tr '[:upper:]' '[:lower:]')"
    case "$normalized_value" in
        changethis|change-me|replace-me|password|secret)
            add_configuration_error \
                "$setting_name must be replaced with a unique local value."
            ;;
    esac
}

# Validate one host port without opening a socket. Compose performs the live
# collision check later, while this pass catches malformed or duplicate values
# before Docker is required. Indexed arrays keep the script compatible with
# the older Bash shipped by common macOS installations.
validate_host_port_setting() {
    local setting_name="$1"
    local setting_value
    local numeric_port
    local existing_index

    if ! setting_value="$(read_environment_value "$setting_name")" ||
        [[ -z "$setting_value" ]]; then
        add_configuration_error "$setting_name is missing or empty."
        return
    fi

    if [[ ! "$setting_value" =~ ^[0-9]+$ ]]; then
        add_configuration_error "$setting_name must be an integer from 1 to 65535."
        return
    fi

    numeric_port=$((10#$setting_value))
    if ((numeric_port < 1 || numeric_port > 65535)); then
        add_configuration_error "$setting_name must be an integer from 1 to 65535."
        return
    fi

    for existing_index in "${!CONFIGURED_HOST_PORT_VALUES[@]}"; do
        if [[ "${CONFIGURED_HOST_PORT_VALUES[$existing_index]}" == "$numeric_port" ]]; then
            add_configuration_error \
                "$setting_name and ${CONFIGURED_HOST_PORT_NAMES[$existing_index]} must use unique host ports."
            return
        fi
    done

    CONFIGURED_HOST_PORT_NAMES+=("$setting_name")
    CONFIGURED_HOST_PORT_VALUES+=("$numeric_port")
}

validate_environment_configuration() {
    local research_enabled
    local normalized_research_enabled
    local configured_model
    local host_port_setting
    local frontend_host_port
    local backend_host_port
    local configured_frontend_host
    local expected_frontend_host

    print_section "[1/4] Validating local configuration"

    validate_required_setting "DOCKER_IMAGE_BACKEND"
    validate_required_setting "DOCKER_IMAGE_FRONTEND"
    validate_required_setting "FRONTEND_HOST"
    validate_required_setting "FIRST_SUPERUSER"
    validate_required_setting "POSTGRES_DB"
    validate_required_setting "POSTGRES_USER"
    validate_secret_setting "SECRET_KEY"
    validate_secret_setting "POSTGRES_PASSWORD"
    validate_secret_setting "FIRST_SUPERUSER_PASSWORD"

    for host_port_setting in \
        TRAEFIK_HTTP_PORT \
        TRAEFIK_HTTPS_PORT \
        TRAEFIK_DASHBOARD_PORT \
        POSTGRES_PORT \
        BACKEND_PORT \
        FRONTEND_PORT \
        ADMINER_PORT \
        MAILCATCHER_SMTP_PORT \
        MAILCATCHER_WEB_PORT \
        JAEGER_UI_PORT \
        OTLP_GRPC_PORT \
        OTLP_HTTP_PORT \
        PLAYWRIGHT_REPORT_PORT; do
        validate_host_port_setting "$host_port_setting"
    done

    if frontend_host_port="$(read_environment_value "FRONTEND_PORT")" &&
        configured_frontend_host="$(read_environment_value "FRONTEND_HOST")"; then
        expected_frontend_host="http://localhost:${frontend_host_port}"
        if [[ "$configured_frontend_host" != "$expected_frontend_host" ]]; then
            add_configuration_error \
                "FRONTEND_HOST must match FRONTEND_PORT at $expected_frontend_host."
        fi
    fi

    if ! configured_model="$(read_environment_value "TXT2CRS_MODEL_ID")"; then
        configured_model=""
    fi
    case "$configured_model" in
        gpt-5.6-sol|gpt-5.6-terra|gpt-5.6-luna)
            ;;
        *)
            add_configuration_error \
                "TXT2CRS_MODEL_ID must select an exact reviewed GPT-5.6 model."
            ;;
    esac

    if ! research_enabled="$(read_environment_value "TXT2CRS_RESEARCH_ENABLED")"; then
        research_enabled="true"
    fi
    normalized_research_enabled="$(
        printf '%s' "$research_enabled" | tr '[:upper:]' '[:lower:]'
    )"
    case "$normalized_research_enabled" in
        false|0|no|off)
            print_warning_line \
                "Research is disabled; generated courses will not use Tavily."
            ;;
        *)
            validate_secret_setting "TAVILY_API_KEY"
            ;;
    esac

    if [[ -n "$CONFIGURATION_ERRORS" ]]; then
        print_error_heading "CONFIGURATION NEEDS ATTENTION"
        printf '\n%s' "$CONFIGURATION_ERRORS" >&2
        cat >&2 <<'EOF'

Edit .env and run ./scripts/start-local.sh again.
Configured secret values were not printed.
EOF
        return 2
    fi

    frontend_host_port="$(read_environment_value "FRONTEND_PORT")"
    backend_host_port="$(read_environment_value "BACKEND_PORT")"
    FRONTEND_URL="http://localhost:${frontend_host_port}"
    BACKEND_DOCUMENTATION_URL="http://localhost:${backend_host_port}/docs"
    SYSTEM_SETUP_URL="${FRONTEND_URL}/setup"

    print_success_line ".env contains the required judge deployment settings."
}

if validate_environment_configuration; then
    :
else
    configuration_exit_code=$?
    exit "$configuration_exit_code"
fi

require_docker_runtime() {
    print_section "[2/4] Checking Docker and Compose"

    if ! command -v docker >/dev/null 2>&1; then
        print_error_heading "DOCKER IS NOT INSTALLED"
        cat >&2 <<'EOF'

Install Docker Desktop or Docker Engine with Compose v2, then run:

  ./scripts/start-local.sh
EOF
        return 3
    fi

    if ! docker compose version >/dev/null 2>&1; then
        print_error_heading "DOCKER COMPOSE V2 IS REQUIRED"
        cat >&2 <<'EOF'

The docker command exists, but "docker compose" is unavailable.
Install the Compose v2 plugin or update Docker Desktop.
EOF
        return 3
    fi

    if ! docker info >/dev/null 2>&1; then
        print_error_heading "DOCKER IS NOT RUNNING"
        cat >&2 <<'EOF'

Start Docker Desktop or the Docker daemon, then run:

  ./scripts/start-local.sh
EOF
        return 3
    fi

    print_success_line "Docker is running and Compose v2 is available."
}

if require_docker_runtime; then
    :
else
    docker_exit_code=$?
    exit "$docker_exit_code"
fi

COMPOSE_COMMAND=(
    docker compose
    --env-file "$ENVIRONMENT_FILE"
    --project-directory "$PROJECT_DIRECTORY"
)

validate_compose_configuration() {
    print_section "[3/4] Validating the Docker Compose topology"

    if ! "${COMPOSE_COMMAND[@]}" config --quiet; then
        print_error_heading "COMPOSE CONFIGURATION IS INVALID"
        cat >&2 <<'EOF'

Review the Compose error above and the values in .env.
No containers were changed.
EOF
        return 2
    fi

    print_success_line "Docker Compose accepted the complete local topology."
}

if validate_compose_configuration; then
    :
else
    compose_exit_code=$?
    exit "$compose_exit_code"
fi

show_application_urls() {
    printf '\n'
    printf '  Application:  %s\n' "$FRONTEND_URL"
    printf '  API docs:     %s\n' "$BACKEND_DOCUMENTATION_URL"
    printf '  System setup: %s\n' "$SYSTEM_SETUP_URL"
}

if [[ "$ACTION" == "status" ]]; then
    print_section "[4/4] Current txt2crs service status"
    "${COMPOSE_COMMAND[@]}" ps --all
    show_application_urls
    exit 0
fi

if [[ "$ACTION" == "stop" ]]; then
    print_section "[4/4] Stopping txt2crs safely"
    if ! "${COMPOSE_COMMAND[@]}" down --remove-orphans; then
        print_error_heading "STOP FAILED"
        printf '\nRun docker compose ps and review the Docker error above.\n' >&2
        exit 1
    fi
    print_success_line \
        "Services stopped. PostgreSQL and private txt2crs volumes were preserved."
    exit 0
fi

# Discover published ports from Compose instead of hardcoding every optional
# local support service. A running container from this same Compose project is
# allowed because the command is intentionally safe to rerun.
check_for_foreign_port_conflicts() {
    local normalized_compose_configuration
    local published_ports
    local current_container_ids
    local running_container_lines
    local published_port
    local container_line
    local container_id
    local container_name
    local container_ports

    if ! normalized_compose_configuration="$("${COMPOSE_COMMAND[@]}" config)"; then
        print_error_heading "COMPOSE CONFIGURATION COULD NOT BE INSPECTED"
        return 2
    fi

    published_ports="$(
        printf '%s\n' "$normalized_compose_configuration" |
            sed -n 's/^[[:space:]]*published: "\{0,1\}\([0-9][0-9]*\)"\{0,1\}[[:space:]]*$/\1/p' |
            sort -nu
    )"
    current_container_ids="$("${COMPOSE_COMMAND[@]}" ps -q 2>/dev/null || true)"
    # Compose returns full container IDs. Ask Docker for full IDs too so a
    # harmless rerun recognizes this project's own published ports.
    running_container_lines="$(
        docker ps --no-trunc --format '{{.ID}}|{{.Names}}|{{.Ports}}'
    )"

    while IFS= read -r published_port; do
        [[ -z "$published_port" ]] && continue

        while IFS= read -r container_line; do
            [[ -z "$container_line" ]] && continue
            IFS='|' read -r container_id container_name container_ports <<EOF
$container_line
EOF
            case "$container_ports" in
                *":${published_port}->"*)
                    if ! printf '%s\n' "$current_container_ids" |
                        grep -Fqx "$container_id"; then
                        print_error_heading "PORT CONFLICT"
                        cat >&2 <<EOF

Host port $published_port is already used by Docker container:

  $container_name

Stop that container or change the corresponding local port mapping, then run:

  ./scripts/start-local.sh
EOF
                        return 3
                    fi
                    ;;
            esac
        done <<EOF
$running_container_lines
EOF
    done <<EOF
$published_ports
EOF

    print_success_line "Required host ports are available."
}

print_section "[4/4] Checking ports and starting txt2crs"

if check_for_foreign_port_conflicts; then
    :
else
    port_exit_code=$?
    exit "$port_exit_code"
fi

print_info_line "Compose will preserve existing named volumes."

# PostgreSQL reads POSTGRES_PASSWORD only while initializing an empty data
# directory. A judge may reasonably change .env and rerun this safe command
# while keeping the named volume. Start only the database first so we can test
# the password over its non-loopback address, which exercises the same SCRAM
# authentication rule used by the backend container.
verify_local_database_password() {
    "${COMPOSE_COMMAND[@]}" exec -T db bash -ceu '
        PGPASSWORD="$POSTGRES_PASSWORD" psql \
            --host "$HOSTNAME" \
            --username "$POSTGRES_USER" \
            --dbname "$POSTGRES_DB" \
            --no-psqlrc \
            --tuples-only \
            --no-align \
            --command "SELECT 1;" >/dev/null
    '
}

# The official PostgreSQL image trusts local Unix-socket connections inside
# the database container. Use that narrow local recovery path to make the
# current .env password authoritative without dropping the volume or exposing
# the secret in terminal output or the host process arguments.
synchronize_local_database_password() {
    print_warning_line \
        "The existing database volume uses an older password; synchronizing it."

    if ! "${COMPOSE_COMMAND[@]}" exec -T db bash -ceu '
        escaped_database_role="$(
            printf "%s" "$POSTGRES_USER" | sed "s/\"/\"\"/g"
        )"
        escaped_database_password="$(
            printf "%s" "$POSTGRES_PASSWORD" | sed "s/'"'"'/'"'"''"'"'/g"
        )"
        printf "ALTER ROLE \"%s\" WITH PASSWORD '\''%s'\'';\n" \
            "$escaped_database_role" "$escaped_database_password" |
            psql \
                --username "$POSTGRES_USER" \
                --dbname "$POSTGRES_DB" \
                --no-psqlrc \
                --set ON_ERROR_STOP=1 >/dev/null
    '; then
        print_error_heading "DATABASE PASSWORD SYNC FAILED"
        cat >&2 <<'EOF'

The existing PostgreSQL volume could not adopt the credentials from .env.
No volume was deleted. Review the database log and configured role name.
EOF
        "${COMPOSE_COMMAND[@]}" logs --no-color --tail 40 db || true
        return 1
    fi

    if ! verify_local_database_password 2>/dev/null; then
        print_error_heading "DATABASE PASSWORD VERIFICATION FAILED"
        cat >&2 <<'EOF'

PostgreSQL accepted the password update but remote authentication still fails.
No volume was deleted. Review the database authentication configuration.
EOF
        return 1
    fi

    print_success_line "Database password matches the current .env configuration."
}

prepare_local_database() {
    print_info_line "Starting PostgreSQL and validating persisted credentials."
    if ! "${COMPOSE_COMMAND[@]}" up --detach --wait db; then
        print_error_heading "DATABASE START FAILED"
        cat >&2 <<'EOF'

PostgreSQL did not reach its declared healthy state.
No volume was deleted. The last 40 database log lines follow.
EOF
        "${COMPOSE_COMMAND[@]}" logs --no-color --tail 40 db || true
        return 1
    fi

    if verify_local_database_password 2>/dev/null; then
        print_success_line "Database password matches the current .env configuration."
        return 0
    fi

    synchronize_local_database_password
}

if prepare_local_database; then
    :
else
    database_preparation_exit_code=$?
    exit "$database_preparation_exit_code"
fi

if [[ "$BUILD_IMAGES" == true ]]; then
    print_info_line "Building current backend and frontend images."
    if "${COMPOSE_COMMAND[@]}" up --detach --build --wait; then
        :
    else
        startup_exit_code=$?
        print_error_heading "DEPLOYMENT FAILED"
        cat >&2 <<'EOF'

The stack did not reach its declared healthy state.
Current service status and the last 80 relevant log lines follow.
EOF
        "${COMPOSE_COMMAND[@]}" ps --all || true
        "${COMPOSE_COMMAND[@]}" logs --no-color --tail 80 \
            db prestart backend frontend || true
        exit "$startup_exit_code"
    fi
else
    print_info_line "Starting with existing images because --no-build was selected."
    if "${COMPOSE_COMMAND[@]}" up --detach --wait; then
        :
    else
        startup_exit_code=$?
        print_error_heading "DEPLOYMENT FAILED"
        cat >&2 <<'EOF'

The stack did not reach its declared healthy state.
Current service status and the last 80 relevant log lines follow.
EOF
        "${COMPOSE_COMMAND[@]}" ps --all || true
        "${COMPOSE_COMMAND[@]}" logs --no-color --tail 80 \
            db prestart backend frontend || true
        exit "$startup_exit_code"
    fi
fi

printf '\n'
"${COMPOSE_COMMAND[@]}" ps --all

printf '\n%s%s+--------------------------------------------------------------+%s\n' \
    "$GREEN" "$BOLD" "$RESET"
printf '%s%s| %-60s |%s\n' "$GREEN" "$BOLD" "TXT2CRS IS READY" "$RESET"
printf '%s%s+--------------------------------------------------------------+%s\n' \
    "$GREEN" "$BOLD" "$RESET"
show_application_urls

cat <<'EOF'

Next steps:

  1. Sign in with FIRST_SUPERUSER and FIRST_SUPERUSER_PASSWORD.
  2. Open System setup.
  3. Complete the ChatGPT device login.
  4. Confirm every readiness check passes.
  5. Create a course from the learner workspace.

Useful commands:

  ./scripts/start-local.sh --status
  ./scripts/start-local.sh --stop
  docker compose logs --follow backend
EOF
