#!/usr/bin/env bash
#
# deploy-local-clean.sh - Safe local rebuild script for Python React Boilerplate
#
# This script performs a SAFE rebuild that PRESERVES your database data.
# It rebuilds all Docker images from scratch while keeping your volumes intact.
#
# Usage: ./scripts/deploy-local-clean.sh [OPTIONS]
#
# Options:
#   --stop       Stop all services without rebuilding (preserves data)
#   --nuclear    DANGER: Also removes volumes (destroys all database data)
#   --skip-cache Skip cleaning build cache (faster but less thorough)
#   --help       Show this help message
#
# Author: Python React Boilerplate Team
# Date: 2025-12-22
#

set -e  # Exit on error

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
IMAGES=(
    "python-react-boilerplate-backend:latest"
    "python-react-boilerplate-frontend:latest"
    "python-react-boilerplate-playwright:latest"
)
VOLUME_NAME="python-react-boilerplate_app-db-data"

# =============================================================================
# COLORS & FORMATTING
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color
BOLD='\033[1m'
DIM='\033[2m'

# =============================================================================
# ASCII ART
# =============================================================================

print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'

  ██████╗  ██████╗ ██╗██╗     ███████╗██████╗ ██████╗ ██╗      █████╗ ████████╗███████╗
  ██╔══██╗██╔═══██╗██║██║     ██╔════╝██╔══██╗██╔══██╗██║     ██╔══██╗╚══██╔══╝██╔════╝
  ██████╔╝██║   ██║██║██║     █████╗  ██████╔╝██████╔╝██║     ███████║   ██║   █████╗
  ██╔══██╗██║   ██║██║██║     ██╔══╝  ██╔══██╗██╔═══╝ ██║     ██╔══██║   ██║   ██╔══╝
  ██████╔╝╚██████╔╝██║███████╗███████╗██║  ██║██║     ███████╗██║  ██║   ██║   ███████╗
  ╚═════╝  ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝

EOF
    echo -e "${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}        ☁️  LOCAL DEPLOYMENT - CLEAN REBUILD  ☁️${NC}"
    echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_safe_mode() {
    echo -e "${GREEN}"
    cat << 'EOF'
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🛡️  SAFE MODE - Your database will be PRESERVED  🛡️     ║
    ║                                                           ║
    ║   ✓ All user accounts will remain                         ║
    ║   ✓ All application data will remain                      ║
    ║   ✓ Volume: python-react-boilerplate_app-db-data is protected            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_nuclear_warning() {
    echo -e "${RED}"
    cat << 'EOF'
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ☢️  NUCLEAR MODE - ALL DATA WILL BE DESTROYED  ☢️       ║
    ║                                                           ║
    ║   ✗ All user accounts will be DELETED                    ║
    ║   ✗ All application data will be DELETED                 ║
    ║   ✗ Volume: python-react-boilerplate_app-db-data will be REMOVED        ║
    ║                                                           ║
    ║              THIS CANNOT BE UNDONE!                       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_stop_mode() {
    echo -e "${YELLOW}"
    cat << 'EOF'
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🛑  STOP MODE - Shutting down services  🛑              ║
    ║                                                           ║
    ║   ✓ All containers will be stopped                        ║
    ║   ✓ All application data will remain                      ║
    ║   ✓ Volume: python-react-boilerplate_app-db-data is protected            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}"
    echo ""
    echo "    ╔═══════════════════════════════════════════════════════════╗"
    echo "    ║                                                           ║"
    echo "    ║   ✅  DEPLOYMENT COMPLETE - ALL SYSTEMS GO!  ✅           ║"
    echo "    ║                                                           ║"
    echo "    ╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "       🌐 Frontend:    http://localhost:${PORT_FRONTEND:-unknown}"
    echo "       🔌 Backend API: http://localhost:${PORT_BACKEND:-unknown}/docs"
    echo "       🗄️  Adminer:     http://localhost:${PORT_ADMINER:-unknown}"
    echo "       📧 Mailcatcher: http://localhost:${PORT_MAILCATCHER:-unknown}"
    echo "       🚦 Traefik:     http://localhost:${PORT_TRAEFIK:-unknown}"
    echo ""
    echo -e "${NC}"
}

print_failure() {
    echo -e "${RED}"
    cat << 'EOF'

    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ❌  DEPLOYMENT FAILED  ❌                               ║
    ║                                                           ║
    ║   Check the error messages above for details.             ║
    ║   Run 'docker compose logs' for more information.         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝

EOF
    echo -e "${NC}"
}

# =============================================================================
# HELPER FUNCTIONS
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
    echo -e "${CYAN}  ℹ️  ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}  ✓  ${1}${NC}"
}

log_warning() {
    echo -e "${YELLOW}  ⚠️  ${1}${NC}"
}

log_error() {
    echo -e "${RED}  ✗  ${1}${NC}"
}

log_detail() {
    echo -e "${GRAY}      ${1}${NC}"
}

# Get the host port for a container's internal port
# Usage: get_container_port <container_name> <internal_port>
# Example: get_container_port python-react-boilerplate-backend-1 8000
get_container_port() {
    local container=$1
    local internal_port=$2
    docker port "$container" "$internal_port" 2>/dev/null | head -1 | cut -d: -f2 || echo "unknown"
}

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf "${CYAN}  %c  ${NC}" "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b"
    done
    printf "     \b\b\b\b\b"
}

confirm_nuclear() {
    echo ""
    echo -e "${RED}${BOLD}  Are you ABSOLUTELY sure you want to destroy all data?${NC}"
    echo -e "${YELLOW}  Type 'DESTROY' to confirm: ${NC}"
    read -r confirmation
    if [ "$confirmation" != "DESTROY" ]; then
        echo ""
        log_info "Cancelled. No changes made."
        exit 0
    fi
}

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Safe local rebuild script for Python React Boilerplate"
    echo ""
    echo "Options:"
    echo "  --stop        Stop all services without rebuilding (preserves data)"
    echo "  --nuclear     DANGER: Also removes volumes (destroys all database data)"
    echo "  --skip-cache  Skip cleaning build cache (faster but less thorough)"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Safe rebuild, preserves database"
    echo "  $0 --stop       # Stop services only, no rebuild"
    echo "  $0 --skip-cache # Quick rebuild without cache cleaning"
    echo "  $0 --nuclear    # Full reset including database (DESTRUCTIVE)"
    echo ""
}

# =============================================================================
# PARSE ARGUMENTS
# =============================================================================

NUCLEAR_MODE=false
SKIP_CACHE=false
STOP_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --stop)
            STOP_ONLY=true
            shift
            ;;
        --nuclear)
            NUCLEAR_MODE=true
            shift
            ;;
        --skip-cache)
            SKIP_CACHE=true
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# =============================================================================
# MAIN SCRIPT
# =============================================================================

cd "$PROJECT_DIR"

# Determine total steps based on options
if [ "$SKIP_CACHE" = true ]; then
    TOTAL_STEPS=6
else
    TOTAL_STEPS=7
fi

# Print banner
clear
print_banner

# Show mode
if [ "$STOP_ONLY" = true ]; then
    print_stop_mode
elif [ "$NUCLEAR_MODE" = true ]; then
    print_nuclear_warning
    confirm_nuclear
else
    print_safe_mode
fi

sleep 1

# Handle --stop mode: just stop services and exit
if [ "$STOP_ONLY" = true ]; then
    log_step 1 1 "Stopping all services"

    docker compose down --remove-orphans 2>&1 | while read line; do
        log_detail "$line"
    done

    log_success "All containers and networks stopped (volumes preserved)"

    echo ""
    echo -e "${GREEN}  🛑  All services have been stopped${NC}"
    echo -e "${GRAY}  Run './scripts/deploy-local-clean.sh' to rebuild and start${NC}"
    echo -e "${GRAY}  Run 'docker compose up -d' to start without rebuilding${NC}"
    echo ""
    exit 0
fi

# Track timing
START_TIME=$(date +%s)

# -----------------------------------------------------------------------------
# STEP 1: Survey Current State
# -----------------------------------------------------------------------------
log_step 1 $TOTAL_STEPS "Surveying current state"

CONTAINER_COUNT=$(docker ps -a --filter "name=python-react-boilerplate" --format "{{.Names}}" 2>/dev/null | wc -l || echo "0")
VOLUME_EXISTS=$(docker volume ls --filter "name=$VOLUME_NAME" --format "{{.Name}}" 2>/dev/null | grep -c "$VOLUME_NAME" || echo "0")
IMAGE_COUNT=$(docker images --filter "reference=python-react-boilerplate*" --format "{{.Repository}}" 2>/dev/null | wc -l || echo "0")

log_detail "Containers found: $CONTAINER_COUNT"
log_detail "Database volume exists: $([ "$VOLUME_EXISTS" -gt 0 ] && echo 'YES' || echo 'NO')"
log_detail "Images found: $IMAGE_COUNT"

if [ "$VOLUME_EXISTS" -gt 0 ]; then
    log_success "Database volume detected - your data exists"
else
    log_warning "No database volume found - starting fresh"
fi

# -----------------------------------------------------------------------------
# STEP 2: Stop All Services
# -----------------------------------------------------------------------------
log_step 2 $TOTAL_STEPS "Stopping all services"

if [ "$NUCLEAR_MODE" = true ]; then
    log_warning "Nuclear mode: removing volumes too!"
    docker compose down --remove-orphans -v 2>&1 | while read line; do
        log_detail "$line"
    done
    log_success "All containers, networks, and volumes removed"
else
    docker compose down --remove-orphans 2>&1 | while read line; do
        log_detail "$line"
    done
    log_success "All containers and networks removed (volumes preserved)"
fi

# -----------------------------------------------------------------------------
# STEP 3: Verify Volume Status
# -----------------------------------------------------------------------------
log_step 3 $TOTAL_STEPS "Verifying data integrity"

VOLUME_EXISTS_NOW=$(docker volume ls --filter "name=$VOLUME_NAME" --format "{{.Name}}" 2>/dev/null | grep -c "$VOLUME_NAME" || echo "0")

if [ "$NUCLEAR_MODE" = true ]; then
    if [ "$VOLUME_EXISTS_NOW" -eq 0 ]; then
        log_success "Volume successfully removed (nuclear mode)"
    else
        log_warning "Volume still exists - may need manual removal"
    fi
else
    if [ "$VOLUME_EXISTS_NOW" -gt 0 ]; then
        log_success "Database volume intact - your data is safe!"
    else
        log_info "No volume found - will be created fresh"
    fi
fi

# -----------------------------------------------------------------------------
# STEP 4: Remove Old Images
# -----------------------------------------------------------------------------
log_step 4 $TOTAL_STEPS "Removing old Docker images"

for image in "${IMAGES[@]}"; do
    if docker image inspect "$image" &> /dev/null; then
        docker rmi "$image" 2>/dev/null && log_success "Removed: $image" || log_detail "Could not remove: $image"
    else
        log_detail "Not found: $image"
    fi
done

# -----------------------------------------------------------------------------
# STEP 5: Clean Build Cache (optional)
# -----------------------------------------------------------------------------
CURRENT_STEP=5

if [ "$SKIP_CACHE" = false ]; then
    log_step $CURRENT_STEP $TOTAL_STEPS "Cleaning Docker build cache"

    log_info "Pruning build cache..."
    CACHE_FREED=$(docker builder prune -af 2>&1 | tail -1)
    log_detail "$CACHE_FREED"

    log_info "Removing dangling images..."
    docker image prune -f > /dev/null 2>&1
    log_success "Build cache cleaned"

    CURRENT_STEP=$((CURRENT_STEP + 1))
fi

# -----------------------------------------------------------------------------
# STEP 6: Rebuild All Images
# -----------------------------------------------------------------------------
log_step $CURRENT_STEP $TOTAL_STEPS "Building fresh Docker images"

log_info "This may take 3-5 minutes..."
echo ""

BUILD_START=$(date +%s)

if docker compose build --no-cache --pull 2>&1 | while read line; do
    # Show only key build progress
    if [[ "$line" == *"Building"* ]] || [[ "$line" == *"built"* ]] || [[ "$line" == *"DONE"* ]] || [[ "$line" == *"ERROR"* ]]; then
        log_detail "$line"
    fi
done; then
    BUILD_END=$(date +%s)
    BUILD_TIME=$((BUILD_END - BUILD_START))
    log_success "All images built successfully in ${BUILD_TIME}s"
else
    log_error "Build failed!"
    print_failure
    exit 1
fi

CURRENT_STEP=$((CURRENT_STEP + 1))

# -----------------------------------------------------------------------------
# STEP 7: Start All Services
# -----------------------------------------------------------------------------
log_step $CURRENT_STEP $TOTAL_STEPS "Starting all services"

docker compose up -d 2>&1 | while read line; do
    log_detail "$line"
done

log_info "Waiting for services to become healthy..."
sleep 5

# Check health
MAX_ATTEMPTS=30
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    BACKEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' python-react-boilerplate-backend-1 2>/dev/null || echo "unknown")
    DB_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' python-react-boilerplate-db-1 2>/dev/null || echo "unknown")

    if [ "$BACKEND_HEALTH" = "healthy" ] && [ "$DB_HEALTH" = "healthy" ]; then
        break
    fi

    ATTEMPT=$((ATTEMPT + 1))
    printf "${CYAN}  ⏳ Waiting for health checks... (${ATTEMPT}/${MAX_ATTEMPTS})${NC}\r"
    sleep 2
done
echo ""

# Final status check
BACKEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' python-react-boilerplate-backend-1 2>/dev/null || echo "unknown")
DB_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' python-react-boilerplate-db-1 2>/dev/null || echo "unknown")
FRONTEND_STATUS=$(docker inspect --format='{{.State.Status}}' python-react-boilerplate-frontend-1 2>/dev/null || echo "unknown")

if [ "$BACKEND_HEALTH" = "healthy" ] && [ "$DB_HEALTH" = "healthy" ] && [ "$FRONTEND_STATUS" = "running" ]; then
    log_success "Database:  healthy"
    log_success "Backend:   healthy"
    log_success "Frontend:  running"
else
    log_warning "Some services may not be fully ready"
    log_detail "Database: $DB_HEALTH"
    log_detail "Backend: $BACKEND_HEALTH"
    log_detail "Frontend: $FRONTEND_STATUS"
fi

# Get dynamic ports from running containers
PORT_DB=$(get_container_port python-react-boilerplate-db-1 5432)
PORT_BACKEND=$(get_container_port python-react-boilerplate-backend-1 8000)
PORT_FRONTEND=$(get_container_port python-react-boilerplate-frontend-1 80)
PORT_ADMINER=$(get_container_port python-react-boilerplate-adminer-1 8080)
PORT_MAILCATCHER=$(get_container_port python-react-boilerplate-mailcatcher-1 1080)
PORT_TRAEFIK=$(get_container_port python-react-boilerplate-proxy-1 8080)

# -----------------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------------
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo ""
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  📊 DEPLOYMENT SUMMARY${NC}"
echo -e "${WHITE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GRAY}Mode:${NC}           $([ "$NUCLEAR_MODE" = true ] && echo -e "${RED}Nuclear (data destroyed)${NC}" || echo -e "${GREEN}Safe (data preserved)${NC}")"
echo -e "  ${GRAY}Total time:${NC}     ${TOTAL_TIME} seconds"
echo -e "  ${GRAY}Build time:${NC}     ${BUILD_TIME} seconds"
echo ""

# Final service table (using dynamic ports)
echo -e "  ${GRAY}┌─────────────────┬────────────┬─────────────────────────┐${NC}"
echo -e "  ${GRAY}│${NC} ${WHITE}Service${NC}         ${GRAY}│${NC} ${WHITE}Status${NC}     ${GRAY}│${NC} ${WHITE}URL${NC}                     ${GRAY}│${NC}"
echo -e "  ${GRAY}├─────────────────┼────────────┼─────────────────────────┤${NC}"
printf "  ${GRAY}│${NC} Database        ${GRAY}│${NC} %s ${GRAY}│${NC} %-23s ${GRAY}│${NC}\n" \
    "$([ "$DB_HEALTH" = "healthy" ] && echo -e "${GREEN}● healthy${NC}" || echo -e "${YELLOW}● $DB_HEALTH${NC}")" \
    "localhost:${PORT_DB}"
printf "  ${GRAY}│${NC} Backend         ${GRAY}│${NC} %s ${GRAY}│${NC} %-23s ${GRAY}│${NC}\n" \
    "$([ "$BACKEND_HEALTH" = "healthy" ] && echo -e "${GREEN}● healthy${NC}" || echo -e "${YELLOW}● $BACKEND_HEALTH${NC}")" \
    "localhost:${PORT_BACKEND}/docs"
printf "  ${GRAY}│${NC} Frontend        ${GRAY}│${NC} %s ${GRAY}│${NC} %-23s ${GRAY}│${NC}\n" \
    "$([ "$FRONTEND_STATUS" = "running" ] && echo -e "${GREEN}● running${NC}" || echo -e "${YELLOW}● $FRONTEND_STATUS${NC}")" \
    "localhost:${PORT_FRONTEND}"
printf "  ${GRAY}│${NC} Adminer         ${GRAY}│${NC} ${GREEN}● running${NC}  ${GRAY}│${NC} %-23s ${GRAY}│${NC}\n" "localhost:${PORT_ADMINER}"
printf "  ${GRAY}│${NC} Mailcatcher     ${GRAY}│${NC} ${GREEN}● running${NC}  ${GRAY}│${NC} %-23s ${GRAY}│${NC}\n" "localhost:${PORT_MAILCATCHER}"
echo -e "  ${GRAY}└─────────────────┴────────────┴─────────────────────────┘${NC}"
echo ""

# Data status
if [ "$NUCLEAR_MODE" = true ]; then
    echo -e "  ${RED}⚠️  Database was reset - all previous data has been removed${NC}"
else
    VOLUME_FINAL=$(docker volume ls --filter "name=$VOLUME_NAME" --format "{{.Name}}" 2>/dev/null | grep -c "$VOLUME_NAME" || echo "0")
    if [ "$VOLUME_FINAL" -gt 0 ]; then
        echo -e "  ${GREEN}🛡️  Database volume intact - your data has been preserved${NC}"
    fi
fi

print_success

echo -e "${GRAY}  Run 'docker compose logs -f' to view logs${NC}"
echo -e "${GRAY}  Run 'docker compose ps' to check status${NC}"
echo ""
