#!/usr/bin/env bash
#
# coolify-deploy.sh - Coolify API deployment script for Python React Boilerplate
#
# Manages backend and frontend applications on a Coolify instance via its REST API.
# Supports first-time setup, redeployments, and status checks.
#
# Usage: ./scripts/coolify-deploy.sh [MODE] [OPTIONS]
#
# Modes:
#   --create       First-time setup: discover resources, create apps, configure, deploy
#   --redeploy     (default) Trigger deploy of existing apps via UUID
#   --status       Check current deployment status
#   --dry-run      Show what would happen without making API calls
#
# Options:
#   --backend-only   Target only the backend application
#   --frontend-only  Target only the frontend application
#   --env-file FILE  Override env file (default: .env)
#   --help           Show this help message
#
# Required env vars (all modes):
#   COOLIFY_API_TOKEN  - API token with read/write/deploy permissions
#   COOLIFY_API_URL    - Base URL (e.g., https://coolify.domain.com/api/v1)
#
# Required env vars (--create):
#   GITHUB_REPO    - Repository (e.g., user/repo)
#   GITHUB_BRANCH  - Branch to deploy (e.g., main)
#   APP_NAME       - Application name prefix
#   APP_DOMAIN     - Production domain
#
# Required env vars (--redeploy):
#   BACKEND_APP_UUID   - Coolify UUID for the backend app
#   FRONTEND_APP_UUID  - Coolify UUID for the frontend app
#
# Author: Python React Boilerplate Team
# Date: 2026-02-19
#

set -euo pipefail

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_DIR}/.env"

# Defaults
MODE="redeploy"
DRY_RUN=false
BACKEND_ONLY=false
FRONTEND_ONLY=false
DEPLOY_BACKEND=true
DEPLOY_FRONTEND=true

# Monitoring
POLL_ATTEMPTS=30
POLL_INTERVAL=10

# =============================================================================
# COLORS & FORMATTING
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'
BOLD='\033[1m'

# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

log_step() {
    local step_num=$1
    local total_steps=$2
    local message=$3
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}  [${step_num}/${total_steps}] ${BOLD}${message}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

log_info() {
    echo -e "${CYAN}  i  ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}  +  ${1}${NC}"
}

log_warning() {
    echo -e "${YELLOW}  !  ${1}${NC}"
}

log_error() {
    echo -e "${RED}  x  ${1}${NC}"
}

log_detail() {
    echo -e "${GRAY}      ${1}${NC}"
}

log_dry() {
    echo -e "${YELLOW}  [DRY-RUN]  ${1}${NC}"
}

# =============================================================================
# BANNER
# =============================================================================

print_banner() {
    echo -e "${CYAN}"
    cat << 'BANNER'

   ██████╗ ██████╗  ██████╗ ██╗     ██╗███████╗██╗   ██╗
  ██╔════╝██╔═══██╗██╔═══██╗██║     ██║██╔════╝╚██╗ ██╔╝
  ██║     ██║   ██║██║   ██║██║     ██║█████╗   ╚████╔╝
  ██║     ██║   ██║██║   ██║██║     ██║██╔══╝    ╚██╔╝
  ╚██████╗╚██████╔╝╚██████╔╝███████╗██║██║        ██║
   ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝        ╚═╝

BANNER
    echo -e "${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}        COOLIFY DEPLOYMENT - Python React Boilerplate${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# =============================================================================
# HELP
# =============================================================================

show_help() {
    cat << 'USAGE'
Usage: coolify-deploy.sh [MODE] [OPTIONS]

Modes:
  --create         First-time setup: discover resources, create both apps,
                   configure env vars, and trigger initial deploy
  --redeploy       (default) Trigger deploy of existing apps via saved UUIDs
  --status         Check current deployment status of apps
  --dry-run        Show planned actions without making any API calls

Options:
  --backend-only   Target only the backend application
  --frontend-only  Target only the frontend application
  --env-file FILE  Override env file path (default: .env)
  --help           Show this help message

Examples:
  # First-time setup (creates both apps)
  ./scripts/coolify-deploy.sh --create

  # Preview what --create would do
  ./scripts/coolify-deploy.sh --create --dry-run

  # Redeploy both apps (default mode)
  ./scripts/coolify-deploy.sh

  # Redeploy backend only
  ./scripts/coolify-deploy.sh --backend-only

  # Check deployment status
  ./scripts/coolify-deploy.sh --status

Environment Variables:
  See .env.example for the full list of required variables.
USAGE
}

# =============================================================================
# COOLIFY API HELPER
# =============================================================================

# coolify_api METHOD ENDPOINT [DATA]
# Returns: response body on stdout, exits on HTTP error
coolify_api() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"

    if [ "$DRY_RUN" = true ]; then
        log_dry "${method} ${COOLIFY_API_URL}${endpoint}" >&2
        if [ -n "$data" ]; then
            log_dry "  Body: $(echo "$data" | head -c 200)..." >&2
        fi
        echo '{"uuid":"dry-run-uuid","status":"dry-run"}'
        return 0
    fi

    local http_code
    local response
    local tmpfile
    tmpfile=$(mktemp)

    if [ -n "$data" ]; then
        http_code=$(curl -s -o "$tmpfile" -w "%{http_code}" \
            -X "$method" \
            -H "Authorization: Bearer ${COOLIFY_API_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${COOLIFY_API_URL}${endpoint}")
    else
        http_code=$(curl -s -o "$tmpfile" -w "%{http_code}" \
            -X "$method" \
            -H "Authorization: Bearer ${COOLIFY_API_TOKEN}" \
            -H "Content-Type: application/json" \
            "${COOLIFY_API_URL}${endpoint}")
    fi

    response=$(cat "$tmpfile")
    rm -f "$tmpfile"

    if [ "$http_code" -ge 400 ]; then
        log_error "API error (HTTP ${http_code}): ${method} ${endpoint}" >&2
        log_detail "Response: ${response}" >&2
        return 1
    fi

    echo "$response"
}

# =============================================================================
# PREREQUISITE CHECKS
# =============================================================================

validate_prerequisites() {
    local errors=0

    # Check required commands
    for cmd in curl jq; do
        if ! command -v "$cmd" &>/dev/null; then
            log_error "Required command not found: ${cmd}"
            errors=$((errors + 1))
        fi
    done

    # Check required env vars (all modes)
    if [ -z "${COOLIFY_API_TOKEN:-}" ]; then
        log_error "COOLIFY_API_TOKEN is not set"
        errors=$((errors + 1))
    fi

    if [ -z "${COOLIFY_API_URL:-}" ]; then
        log_error "COOLIFY_API_URL is not set"
        errors=$((errors + 1))
    fi

    # Mode-specific checks
    if [ "$MODE" = "create" ]; then
        for var in GITHUB_REPO GITHUB_BRANCH APP_NAME APP_DOMAIN; do
            if [ -z "${!var:-}" ]; then
                log_error "${var} is required for --create mode"
                errors=$((errors + 1))
            fi
        done
    fi

    if [ "$MODE" = "redeploy" ]; then
        if [ "$DEPLOY_BACKEND" = true ] && [ -z "${BACKEND_APP_UUID:-}" ]; then
            log_error "BACKEND_APP_UUID is required for --redeploy (or use --frontend-only)"
            errors=$((errors + 1))
        fi
        if [ "$DEPLOY_FRONTEND" = true ] && [ -z "${FRONTEND_APP_UUID:-}" ]; then
            log_error "FRONTEND_APP_UUID is required for --redeploy (or use --backend-only)"
            errors=$((errors + 1))
        fi
    fi

    if [ "$MODE" = "status" ]; then
        if [ "$DEPLOY_BACKEND" = true ] && [ -z "${BACKEND_APP_UUID:-}" ]; then
            log_error "BACKEND_APP_UUID is required for --status (or use --frontend-only)"
            errors=$((errors + 1))
        fi
        if [ "$DEPLOY_FRONTEND" = true ] && [ -z "${FRONTEND_APP_UUID:-}" ]; then
            log_error "FRONTEND_APP_UUID is required for --status (or use --backend-only)"
            errors=$((errors + 1))
        fi
    fi

    if [ "$errors" -gt 0 ]; then
        log_error "Found ${errors} error(s). Fix the issues above and try again."
        exit 1
    fi

    # Test API connectivity (skip in dry-run)
    if [ "$DRY_RUN" = false ]; then
        log_info "Testing Coolify API connectivity..."
        if coolify_api GET "/teams" > /dev/null 2>&1; then
            log_success "Coolify API is reachable"
        else
            log_error "Cannot reach Coolify API at ${COOLIFY_API_URL}"
            log_detail "Check COOLIFY_API_URL and COOLIFY_API_TOKEN"
            exit 1
        fi
    else
        log_dry "Would test API connectivity to ${COOLIFY_API_URL}"
    fi
}

# =============================================================================
# RESOURCE DISCOVERY (--create mode)
# =============================================================================

discover_resources() {
    log_info "Discovering Coolify resources..."

    if [ "$DRY_RUN" = true ]; then
        log_dry "Would fetch servers, projects, and GitHub apps"
        SERVER_UUID="dry-run-server-uuid"
        PROJECT_UUID="dry-run-project-uuid"
        GITHUB_APP_UUID="dry-run-github-app-uuid"
        return 0
    fi

    # Discover server
    local servers
    servers=$(coolify_api GET "/servers")
    SERVER_UUID=$(echo "$servers" | jq -r '.[0].uuid // empty')
    if [ -z "$SERVER_UUID" ]; then
        log_error "No servers found in Coolify instance"
        exit 1
    fi
    log_success "Server UUID: ${SERVER_UUID}"

    # Discover project
    local projects
    projects=$(coolify_api GET "/projects")
    PROJECT_UUID=$(echo "$projects" | jq -r '.[0].uuid // empty')
    if [ -z "$PROJECT_UUID" ]; then
        log_error "No projects found in Coolify instance"
        exit 1
    fi
    log_success "Project UUID: ${PROJECT_UUID}"

    # Discover GitHub app
    local github_apps
    github_apps=$(coolify_api GET "/github-apps")
    GITHUB_APP_UUID=$(echo "$github_apps" | jq -r '.[0].uuid // empty')
    if [ -z "$GITHUB_APP_UUID" ]; then
        log_error "No GitHub apps found. Configure a GitHub App in Coolify first."
        exit 1
    fi
    log_success "GitHub App UUID: ${GITHUB_APP_UUID}"
}

# =============================================================================
# CREATE BACKEND APP
# =============================================================================

create_backend_app() {
    log_info "Creating backend application: ${APP_NAME}-backend"

    local payload
    payload=$(cat <<EOF
{
    "project_uuid": "${PROJECT_UUID}",
    "server_uuid": "${SERVER_UUID}",
    "github_app_uuid": "${GITHUB_APP_UUID}",
    "type": "dockerfile",
    "name": "${APP_NAME}-backend",
    "git_repository": "${GITHUB_REPO}",
    "git_branch": "${GITHUB_BRANCH}",
    "ports_exposes": "8000",
    "dockerfile_location": "/backend/Dockerfile",
    "build_path": "/backend"
}
EOF
    )

    local response
    response=$(coolify_api POST "/applications/private-github-app" "$payload")
    BACKEND_APP_UUID=$(echo "$response" | jq -r '.uuid // empty')

    if [ -z "$BACKEND_APP_UUID" ] || [ "$BACKEND_APP_UUID" = "dry-run-uuid" ]; then
        if [ "$DRY_RUN" = true ]; then
            BACKEND_APP_UUID="dry-run-backend-uuid"
            log_dry "Would create backend app"
            return 0
        fi
        log_error "Failed to create backend application"
        exit 1
    fi

    log_success "Backend app created: ${BACKEND_APP_UUID}"
}

# =============================================================================
# CONFIGURE BACKEND APP
# =============================================================================

configure_backend_app() {
    log_info "Configuring backend application..."

    local payload
    payload=$(cat <<EOF
{
    "domains": "https://api.${APP_DOMAIN}",
    "dockerfile_location": "/backend/Dockerfile",
    "dockerfile_target_build": "production",
    "build_path": "/backend",
    "health_check_enabled": true,
    "health_check_path": "/api/v1/utils/health/",
    "health_check_port": "8000",
    "health_check_interval": 30,
    "health_check_timeout": 10,
    "health_check_retries": 3,
    "health_check_start_period": 60,
    "limits_memory": "2048",
    "limits_cpus": "2"
}
EOF
    )

    coolify_api PATCH "/applications/${BACKEND_APP_UUID}" "$payload" > /dev/null
    log_success "Backend configured: api.${APP_DOMAIN}"
}

# =============================================================================
# SET BACKEND ENVIRONMENT VARIABLES
# =============================================================================

set_backend_envs() {
    log_info "Setting backend environment variables..."

    # Build env var array - secrets marked with is_secret: true
    local payload
    payload=$(cat <<EOF
{"data": [
    {"key": "ENVIRONMENT", "value": "production", "is_preview": false},
    {"key": "DOMAIN", "value": "${APP_DOMAIN}", "is_preview": false},
    {"key": "FRONTEND_HOST", "value": "https://${APP_DOMAIN}", "is_preview": false},
    {"key": "SECRET_KEY", "value": "${SECRET_KEY:-changethis}", "is_secret": true, "is_preview": false},
    {"key": "POSTGRES_SERVER", "value": "${POSTGRES_SERVER:-db}", "is_preview": false},
    {"key": "POSTGRES_PORT", "value": "${POSTGRES_PORT:-5432}", "is_preview": false},
    {"key": "POSTGRES_DB", "value": "${POSTGRES_DB:-app}", "is_preview": false},
    {"key": "POSTGRES_USER", "value": "${POSTGRES_USER:-postgres}", "is_secret": true, "is_preview": false},
    {"key": "POSTGRES_PASSWORD", "value": "${POSTGRES_PASSWORD:-changethis}", "is_secret": true, "is_preview": false},
    {"key": "FIRST_SUPERUSER", "value": "${FIRST_SUPERUSER:-admin@example.com}", "is_preview": false},
    {"key": "FIRST_SUPERUSER_PASSWORD", "value": "${FIRST_SUPERUSER_PASSWORD:-changethis}", "is_secret": true, "is_preview": false},
    {"key": "SMTP_HOST", "value": "${SMTP_HOST:-}", "is_preview": false},
    {"key": "SMTP_USER", "value": "${SMTP_USER:-}", "is_preview": false},
    {"key": "SMTP_PASSWORD", "value": "${SMTP_PASSWORD:-}", "is_secret": true, "is_preview": false},
    {"key": "EMAILS_FROM_EMAIL", "value": "${EMAILS_FROM_EMAIL:-info@example.com}", "is_preview": false},
    {"key": "SMTP_TLS", "value": "${SMTP_TLS:-True}", "is_preview": false},
    {"key": "SMTP_SSL", "value": "${SMTP_SSL:-False}", "is_preview": false},
    {"key": "SMTP_PORT", "value": "${SMTP_PORT:-587}", "is_preview": false},
    {"key": "BACKEND_CORS_ORIGINS", "value": "https://${APP_DOMAIN},https://api.${APP_DOMAIN}", "is_preview": false},
    {"key": "SENTRY_DSN", "value": "${SENTRY_DSN:-}", "is_preview": false}
]}
EOF
    )

    coolify_api POST "/applications/${BACKEND_APP_UUID}/envs/bulk" "$payload" > /dev/null
    log_success "Backend env vars configured (secrets encrypted)"
}

# =============================================================================
# CREATE FRONTEND APP
# =============================================================================

create_frontend_app() {
    log_info "Creating frontend application: ${APP_NAME}-frontend"

    local payload
    payload=$(cat <<EOF
{
    "project_uuid": "${PROJECT_UUID}",
    "server_uuid": "${SERVER_UUID}",
    "github_app_uuid": "${GITHUB_APP_UUID}",
    "type": "dockerfile",
    "name": "${APP_NAME}-frontend",
    "git_repository": "${GITHUB_REPO}",
    "git_branch": "${GITHUB_BRANCH}",
    "ports_exposes": "80",
    "dockerfile_location": "/frontend/Dockerfile",
    "build_path": "/frontend"
}
EOF
    )

    local response
    response=$(coolify_api POST "/applications/private-github-app" "$payload")
    FRONTEND_APP_UUID=$(echo "$response" | jq -r '.uuid // empty')

    if [ -z "$FRONTEND_APP_UUID" ] || [ "$FRONTEND_APP_UUID" = "dry-run-uuid" ]; then
        if [ "$DRY_RUN" = true ]; then
            FRONTEND_APP_UUID="dry-run-frontend-uuid"
            log_dry "Would create frontend app"
            return 0
        fi
        log_error "Failed to create frontend application"
        exit 1
    fi

    log_success "Frontend app created: ${FRONTEND_APP_UUID}"
}

# =============================================================================
# CONFIGURE FRONTEND APP
# =============================================================================

configure_frontend_app() {
    log_info "Configuring frontend application..."

    local payload
    payload=$(cat <<EOF
{
    "domains": "https://${APP_DOMAIN}",
    "dockerfile_location": "/frontend/Dockerfile",
    "build_path": "/frontend",
    "health_check_enabled": true,
    "health_check_path": "/",
    "health_check_port": "80",
    "limits_memory": "1024",
    "limits_cpus": "1"
}
EOF
    )

    coolify_api PATCH "/applications/${FRONTEND_APP_UUID}" "$payload" > /dev/null
    log_success "Frontend configured: ${APP_DOMAIN}"
}

# =============================================================================
# SET FRONTEND BUILD ARGS
# =============================================================================

set_frontend_envs() {
    log_info "Setting frontend build arguments..."

    local payload
    payload=$(cat <<EOF
{"data": [
    {"key": "VITE_API_URL", "value": "https://api.${APP_DOMAIN}", "is_build_time": true, "is_preview": false}
]}
EOF
    )

    coolify_api POST "/applications/${FRONTEND_APP_UUID}/envs/bulk" "$payload" > /dev/null
    log_success "Frontend VITE_API_URL set to https://api.${APP_DOMAIN}"
}

# =============================================================================
# DEPLOY APP
# =============================================================================

deploy_app() {
    local uuid="$1"
    local name="$2"

    log_info "Triggering deployment for ${name}..."

    coolify_api GET "/applications/${uuid}/start?force=false&instant_deploy=true" > /dev/null
    log_success "${name} deployment triggered"
}

# =============================================================================
# MONITOR DEPLOYMENT
# =============================================================================

monitor_deployment() {
    local uuid="$1"
    local name="$2"

    if [ "$DRY_RUN" = true ]; then
        log_dry "Would poll ${name} status until running (${POLL_ATTEMPTS} attempts, ${POLL_INTERVAL}s interval)"
        return 0
    fi

    log_info "Monitoring ${name} deployment (timeout: $((POLL_ATTEMPTS * POLL_INTERVAL))s)..."

    local attempt=0
    while [ "$attempt" -lt "$POLL_ATTEMPTS" ]; do
        local response
        response=$(coolify_api GET "/applications/${uuid}" 2>/dev/null || echo '{}')
        local status
        status=$(echo "$response" | jq -r '.status // "unknown"')

        attempt=$((attempt + 1))
        printf "${CYAN}  ...  ${name}: ${status} (${attempt}/${POLL_ATTEMPTS})${NC}\r"

        if [ "$status" = "running" ]; then
            echo ""
            log_success "${name} is running"
            return 0
        fi

        if [ "$status" = "exited" ] || [ "$status" = "error" ]; then
            echo ""
            log_error "${name} deployment failed (status: ${status})"
            return 1
        fi

        sleep "$POLL_INTERVAL"
    done

    echo ""
    log_warning "${name} deployment timed out - check Coolify dashboard"
    return 1
}

# =============================================================================
# STATUS CHECK
# =============================================================================

check_status() {
    echo ""
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  DEPLOYMENT STATUS${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    if [ "$DEPLOY_BACKEND" = true ]; then
        local be_response
        be_response=$(coolify_api GET "/applications/${BACKEND_APP_UUID}" 2>/dev/null || echo '{}')
        local be_status be_fqdn
        be_status=$(echo "$be_response" | jq -r '.status // "unknown"')
        be_fqdn=$(echo "$be_response" | jq -r '.fqdn // "N/A"')

        local be_color="${YELLOW}"
        [ "$be_status" = "running" ] && be_color="${GREEN}"
        [ "$be_status" = "exited" ] || [ "$be_status" = "error" ] && be_color="${RED}"

        echo -e "  ${WHITE}Backend${NC}"
        echo -e "    UUID:   ${GRAY}${BACKEND_APP_UUID}${NC}"
        echo -e "    Status: ${be_color}${be_status}${NC}"
        echo -e "    Domain: ${GRAY}${be_fqdn}${NC}"
        echo ""
    fi

    if [ "$DEPLOY_FRONTEND" = true ]; then
        local fe_response
        fe_response=$(coolify_api GET "/applications/${FRONTEND_APP_UUID}" 2>/dev/null || echo '{}')
        local fe_status fe_fqdn
        fe_status=$(echo "$fe_response" | jq -r '.status // "unknown"')
        fe_fqdn=$(echo "$fe_response" | jq -r '.fqdn // "N/A"')

        local fe_color="${YELLOW}"
        [ "$fe_status" = "running" ] && fe_color="${GREEN}"
        [ "$fe_status" = "exited" ] || [ "$fe_status" = "error" ] && fe_color="${RED}"

        echo -e "  ${WHITE}Frontend${NC}"
        echo -e "    UUID:   ${GRAY}${FRONTEND_APP_UUID}${NC}"
        echo -e "    Status: ${fe_color}${fe_status}${NC}"
        echo -e "    Domain: ${GRAY}${fe_fqdn}${NC}"
        echo ""
    fi
}

# =============================================================================
# SUMMARY
# =============================================================================

print_summary() {
    local elapsed=$1

    echo ""
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  DEPLOYMENT SUMMARY${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    echo -e "  ${GRAY}┌──────────────┬──────────────────────────────────────────┐${NC}"
    echo -e "  ${GRAY}│${NC} ${WHITE}Property${NC}     ${GRAY}│${NC} ${WHITE}Value${NC}                                    ${GRAY}│${NC}"
    echo -e "  ${GRAY}├──────────────┼──────────────────────────────────────────┤${NC}"
    printf "  ${GRAY}│${NC} Mode         ${GRAY}│${NC} %-40s ${GRAY}│${NC}\n" "${MODE}"
    printf "  ${GRAY}│${NC} Duration     ${GRAY}│${NC} %-40s ${GRAY}│${NC}\n" "${elapsed}s"

    if [ "$DEPLOY_BACKEND" = true ]; then
        printf "  ${GRAY}│${NC} Backend UUID ${GRAY}│${NC} %-40s ${GRAY}│${NC}\n" "${BACKEND_APP_UUID:-N/A}"
        if [ "$MODE" = "create" ]; then
            printf "  ${GRAY}│${NC} Backend URL  ${GRAY}│${NC} %-40s ${GRAY}│${NC}\n" "https://api.${APP_DOMAIN}"
        fi
    fi

    if [ "$DEPLOY_FRONTEND" = true ]; then
        printf "  ${GRAY}│${NC} Frontend UUID${GRAY}│${NC} %-40s ${GRAY}│${NC}\n" "${FRONTEND_APP_UUID:-N/A}"
        if [ "$MODE" = "create" ]; then
            printf "  ${GRAY}│${NC} Frontend URL ${GRAY}│${NC} %-40s ${GRAY}│${NC}\n" "https://${APP_DOMAIN}"
        fi
    fi

    echo -e "  ${GRAY}└──────────────┴──────────────────────────────────────────┘${NC}"
    echo ""

    if [ "$MODE" = "create" ]; then
        echo -e "${GREEN}  Add these to your .env file for future redeployments:${NC}"
        echo ""
        if [ "$DEPLOY_BACKEND" = true ]; then
            echo -e "    BACKEND_APP_UUID=${BACKEND_APP_UUID}"
        fi
        if [ "$DEPLOY_FRONTEND" = true ]; then
            echo -e "    FRONTEND_APP_UUID=${FRONTEND_APP_UUID}"
        fi
        echo ""
    fi
}

# =============================================================================
# PARSE ARGUMENTS
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --create)
            MODE="create"
            shift
            ;;
        --redeploy)
            MODE="redeploy"
            shift
            ;;
        --status)
            MODE="status"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --backend-only)
            BACKEND_ONLY=true
            DEPLOY_FRONTEND=false
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            DEPLOY_BACKEND=false
            shift
            ;;
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# Validate exclusive flags
if [ "$BACKEND_ONLY" = true ] && [ "$FRONTEND_ONLY" = true ]; then
    log_error "Cannot use --backend-only and --frontend-only together"
    exit 1
fi

# =============================================================================
# LOAD ENVIRONMENT
# =============================================================================

if [ -f "$ENV_FILE" ]; then
    log_info "Loading environment from ${ENV_FILE}"
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
else
    if [ "$MODE" != "status" ]; then
        log_warning "Env file not found: ${ENV_FILE}"
        log_detail "Using existing environment variables"
    fi
fi

# =============================================================================
# MAIN EXECUTION
# =============================================================================

START_TIME=$(date +%s)
print_banner

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}  [DRY-RUN MODE] No API calls will be made${NC}"
    echo ""
fi

# ----- STATUS MODE -----
if [ "$MODE" = "status" ]; then
    validate_prerequisites
    check_status
    exit 0
fi

# ----- CREATE MODE -----
if [ "$MODE" = "create" ]; then
    TOTAL_STEPS=0
    [ "$DEPLOY_BACKEND" = true ] && TOTAL_STEPS=$((TOTAL_STEPS + 3))
    [ "$DEPLOY_FRONTEND" = true ] && TOTAL_STEPS=$((TOTAL_STEPS + 3))
    TOTAL_STEPS=$((TOTAL_STEPS + 2))  # prerequisites + discovery

    STEP=1

    log_step $STEP $TOTAL_STEPS "Validating prerequisites"
    validate_prerequisites
    STEP=$((STEP + 1))

    log_step $STEP $TOTAL_STEPS "Discovering Coolify resources"
    discover_resources
    STEP=$((STEP + 1))

    if [ "$DEPLOY_BACKEND" = true ]; then
        log_step $STEP $TOTAL_STEPS "Creating backend application"
        create_backend_app
        configure_backend_app
        set_backend_envs
        STEP=$((STEP + 1))

        log_step $STEP $TOTAL_STEPS "Deploying backend"
        deploy_app "$BACKEND_APP_UUID" "Backend"
        STEP=$((STEP + 1))

        log_step $STEP $TOTAL_STEPS "Monitoring backend deployment"
        monitor_deployment "$BACKEND_APP_UUID" "Backend" || true
        STEP=$((STEP + 1))
    fi

    if [ "$DEPLOY_FRONTEND" = true ]; then
        log_step $STEP $TOTAL_STEPS "Creating frontend application"
        create_frontend_app
        configure_frontend_app
        set_frontend_envs
        STEP=$((STEP + 1))

        log_step $STEP $TOTAL_STEPS "Deploying frontend"
        deploy_app "$FRONTEND_APP_UUID" "Frontend"
        STEP=$((STEP + 1))

        log_step $STEP $TOTAL_STEPS "Monitoring frontend deployment"
        monitor_deployment "$FRONTEND_APP_UUID" "Frontend" || true
        STEP=$((STEP + 1))
    fi

    END_TIME=$(date +%s)
    print_summary $((END_TIME - START_TIME))
    exit 0
fi

# ----- REDEPLOY MODE (default) -----
if [ "$MODE" = "redeploy" ]; then
    TOTAL_STEPS=1  # prerequisites
    [ "$DEPLOY_BACKEND" = true ] && TOTAL_STEPS=$((TOTAL_STEPS + 2))
    [ "$DEPLOY_FRONTEND" = true ] && TOTAL_STEPS=$((TOTAL_STEPS + 2))

    STEP=1

    log_step $STEP $TOTAL_STEPS "Validating prerequisites"
    validate_prerequisites
    STEP=$((STEP + 1))

    if [ "$DEPLOY_BACKEND" = true ]; then
        log_step $STEP $TOTAL_STEPS "Redeploying backend"
        deploy_app "$BACKEND_APP_UUID" "Backend"
        STEP=$((STEP + 1))

        log_step $STEP $TOTAL_STEPS "Monitoring backend deployment"
        monitor_deployment "$BACKEND_APP_UUID" "Backend" || true
        STEP=$((STEP + 1))
    fi

    if [ "$DEPLOY_FRONTEND" = true ]; then
        log_step $STEP $TOTAL_STEPS "Redeploying frontend"
        deploy_app "$FRONTEND_APP_UUID" "Frontend"
        STEP=$((STEP + 1))

        log_step $STEP $TOTAL_STEPS "Monitoring frontend deployment"
        monitor_deployment "$FRONTEND_APP_UUID" "Frontend" || true
        STEP=$((STEP + 1))
    fi

    END_TIME=$(date +%s)
    print_summary $((END_TIME - START_TIME))
    exit 0
fi
