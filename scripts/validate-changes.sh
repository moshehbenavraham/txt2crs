#!/usr/bin/env bash
#
# AI Agent Self-Validation Script
# ================================
# Run this script before committing to verify all changes pass quality gates.
# Designed for fast feedback loops during AI-assisted development.
#
# Usage:
#   ./scripts/validate-changes.sh          # Run all checks (human-readable)
#   ./scripts/validate-changes.sh backend  # Backend shell only
#   ./scripts/validate-changes.sh engine   # txt2crs engine package only
#   ./scripts/validate-changes.sh frontend # Frontend only
#   ./scripts/validate-changes.sh backend engine # Selectors combine
#   ./scripts/validate-changes.sh --json   # Output structured JSON for AI parsing
#
# Expected execution times:
#   - Full validation: ~45-60 seconds
#   - Backend only: ~15-20 seconds
#   - Engine only: ~15-20 seconds
#   - Frontend only: ~10-15 seconds
#

set -e

# Get script directory for reliable path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# The txt2crs engine package's mypy and pytest must run with this directory
# as the working directory so the engine's own pyproject.toml configuration
# applies (backend/pyproject.toml excludes packages/ from its own checks).
ENGINE_DIR="$PROJECT_ROOT/backend/packages/txt2crs"

# Parse arguments.
# With no section selectors, every section runs. The first selector switches
# to opt-in mode (all sections off), then each selector turns its own section
# back on -- so selectors combine: "backend engine" runs those two sections.
RUN_BACKEND=true
RUN_ENGINE=true
RUN_FRONTEND=true
OUTPUT_JSON=false
SECTIONS_SELECTED=false

for arg in "$@"; do
    case $arg in
        backend|engine|frontend)
            if [ "$SECTIONS_SELECTED" = false ]; then
                SECTIONS_SELECTED=true
                RUN_BACKEND=false
                RUN_ENGINE=false
                RUN_FRONTEND=false
            fi
            case $arg in
                backend) RUN_BACKEND=true ;;
                engine) RUN_ENGINE=true ;;
                frontend) RUN_FRONTEND=true ;;
            esac
            ;;
        --json)
            OUTPUT_JSON=true
            ;;
    esac
done

# JSON output mode
if [ "$OUTPUT_JSON" = true ]; then
    # Structured JSON output for AI agent parsing
    RESULTS='{"steps": [], "success": true, "summary": {}}'

    run_json_check() {
        local name="$1"
        local command="$2"
        local dir="$3"
        local start_time
        local end_time
        local duration
        local output
        local status

        start_time=$(date +%s.%N 2>/dev/null || date +%s)

        if output=$(cd "$dir" && eval "$command" 2>&1); then
            status="passed"
        else
            status="failed"
            RESULTS=$(echo "$RESULTS" | jq '.success = false')
        fi

        end_time=$(date +%s.%N 2>/dev/null || date +%s)
        duration=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")

        # Add result to steps array
        if [ "$status" = "failed" ]; then
            # Escape output for JSON and truncate if too long
            escaped_output=$(echo "$output" | head -c 2000 | jq -Rs '.')
            RESULTS=$(echo "$RESULTS" | jq \
                --arg n "$name" \
                --arg s "$status" \
                --arg d "$duration" \
                --argjson o "$escaped_output" \
                '.steps += [{"name": $n, "status": $s, "duration_seconds": ($d | tonumber), "output": $o}]')
        else
            RESULTS=$(echo "$RESULTS" | jq \
                --arg n "$name" \
                --arg s "$status" \
                --arg d "$duration" \
                '.steps += [{"name": $n, "status": $s, "duration_seconds": ($d | tonumber)}]')
        fi
    }

    # Run backend checks
    if [ "$RUN_BACKEND" = true ]; then
        run_json_check "backend-lint" \
            "uv run ruff check app ../scripts/local_state_archive.py tests/core/test_logging.py tests/core/test_txt2crs_settings.py tests/scripts/test_container_contract.py tests/scripts/test_generate_client_contract.py tests/scripts/test_local_backup_contract.py tests/scripts/test_quality_workflow_contract.py tests/scripts/test_security_workflow_contract.py tests/scripts/test_start_local_script.py" \
            "$PROJECT_ROOT/backend"
        run_json_check "backend-format" \
            "uv run ruff format --check app ../scripts/local_state_archive.py tests/core/test_logging.py tests/core/test_txt2crs_settings.py tests/scripts/test_container_contract.py tests/scripts/test_generate_client_contract.py tests/scripts/test_local_backup_contract.py tests/scripts/test_quality_workflow_contract.py tests/scripts/test_security_workflow_contract.py tests/scripts/test_start_local_script.py" \
            "$PROJECT_ROOT/backend"
        run_json_check "backend-typecheck" "uv run mypy app --strict" "$PROJECT_ROOT/backend"
        # These two focused suites intentionally bypass the application-wide,
        # database-owning conftest. They validate pure settings and deployment
        # files and must remain runnable without PostgreSQL.
        run_json_check "backend-baseline-tests" \
            "uv run pytest --confcutdir=tests/core tests/core/test_logging.py tests/core/test_txt2crs_settings.py -q && uv run pytest --confcutdir=tests/scripts tests/scripts/test_container_contract.py tests/scripts/test_generate_client_contract.py tests/scripts/test_local_backup_contract.py tests/scripts/test_quality_workflow_contract.py tests/scripts/test_security_workflow_contract.py tests/scripts/test_start_local_script.py -q" \
            "$PROJECT_ROOT/backend"
    fi

    # Run engine checks (txt2crs workspace package; credential-free suite)
    if [ "$RUN_ENGINE" = true ]; then
        run_json_check "engine-lint" "uv run --package txt2crs ruff check ." "$ENGINE_DIR"
        run_json_check "engine-typecheck" "uv run --package txt2crs mypy" "$ENGINE_DIR"
        run_json_check "engine-tests" "uv run --package txt2crs pytest -q" "$ENGINE_DIR"
    fi

    # Run frontend checks
    if [ "$RUN_FRONTEND" = true ]; then
        run_json_check "frontend-lint" "npx biome check --no-errors-on-unmatched --files-ignore-unknown=true ./" "$PROJECT_ROOT/frontend"
        run_json_check "frontend-typecheck" "npx tsc -p tsconfig.build.json --noEmit" "$PROJECT_ROOT/frontend"
    fi

    # Add summary
    total_steps=$(echo "$RESULTS" | jq '.steps | length')
    passed_steps=$(echo "$RESULTS" | jq '[.steps[] | select(.status == "passed")] | length')
    failed_steps=$(echo "$RESULTS" | jq '[.steps[] | select(.status == "failed")] | length')

    RESULTS=$(echo "$RESULTS" | jq \
        --arg total "$total_steps" \
        --arg passed "$passed_steps" \
        --arg failed "$failed_steps" \
        '.summary = {"total": ($total | tonumber), "passed": ($passed | tonumber), "failed": ($failed | tonumber)}')

    # Output final JSON
    echo "$RESULTS" | jq .

    # Exit with appropriate code
    if echo "$RESULTS" | jq -e '.success' > /dev/null; then
        exit 0
    else
        exit 1
    fi
fi

# Human-readable output mode (default)
# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Agent Validation Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Track overall status
FAILED=false

# Function to run a check and report status
run_check() {
    local name="$1"
    local command="$2"
    local dir="$3"

    echo -e "${YELLOW}[RUNNING]${NC} $name..."

    if (cd "$dir" && eval "$command" > /dev/null 2>&1); then
        echo -e "${GREEN}[PASSED]${NC}  $name"
        return 0
    else
        echo -e "${RED}[FAILED]${NC}  $name"
        echo -e "${RED}         Re-running to show errors:${NC}"
        (cd "$dir" && eval "$command") || true
        FAILED=true
        return 1
    fi
}

# Backend validation
if [ "$RUN_BACKEND" = true ]; then
    echo -e "${BLUE}--- Backend Checks ---${NC}"

    # Type checking with mypy
    run_check "Backend: Type checking (mypy)" "uv run mypy app --strict" "$PROJECT_ROOT/backend"

    # Linting with ruff
    run_check "Backend: Linting (ruff check)" \
        "uv run ruff check app ../scripts/local_state_archive.py tests/core/test_logging.py tests/core/test_txt2crs_settings.py tests/scripts/test_container_contract.py tests/scripts/test_generate_client_contract.py tests/scripts/test_local_backup_contract.py tests/scripts/test_quality_workflow_contract.py tests/scripts/test_security_workflow_contract.py tests/scripts/test_start_local_script.py" \
        "$PROJECT_ROOT/backend"

    # Format checking with ruff (check only, don't modify)
    run_check "Backend: Format check (ruff format)" \
        "uv run ruff format --check app ../scripts/local_state_archive.py tests/core/test_logging.py tests/core/test_txt2crs_settings.py tests/scripts/test_container_contract.py tests/scripts/test_generate_client_contract.py tests/scripts/test_local_backup_contract.py tests/scripts/test_quality_workflow_contract.py tests/scripts/test_security_workflow_contract.py tests/scripts/test_start_local_script.py" \
        "$PROJECT_ROOT/backend"

    # Run the credential-free and database-free shell baseline regressions.
    # Full route tests still use the Compose PostgreSQL service below.
    run_check "Backend: Baseline contract tests" \
        "uv run pytest --confcutdir=tests/core tests/core/test_logging.py tests/core/test_txt2crs_settings.py -q && uv run pytest --confcutdir=tests/scripts tests/scripts/test_container_contract.py tests/scripts/test_generate_client_contract.py tests/scripts/test_local_backup_contract.py tests/scripts/test_quality_workflow_contract.py tests/scripts/test_security_workflow_contract.py tests/scripts/test_start_local_script.py -q" \
        "$PROJECT_ROOT/backend"

    # Unit tests (fast subset, no integration tests requiring DB)
    # Note: Full test suite requires database, run separately with docker compose
    if [ -f "$PROJECT_ROOT/backend/tests/conftest.py" ]; then
        echo -e "${YELLOW}[INFO]${NC}    Backend unit tests require database. Skipping in standalone mode."
        echo -e "${YELLOW}[INFO]${NC}    Run 'docker compose exec backend bash scripts/test.sh' for full tests."
    fi

    echo ""
fi

# Engine validation (txt2crs workspace package)
if [ "$RUN_ENGINE" = true ]; then
    echo -e "${BLUE}--- Engine Checks (txt2crs) ---${NC}"

    # Linting with ruff (engine's own ruff config)
    run_check "Engine: Linting (ruff check)" "uv run --package txt2crs ruff check ." "$ENGINE_DIR"

    # Type checking with mypy (engine's own strict config via files = src, tests)
    run_check "Engine: Type checking (mypy)" "uv run --package txt2crs mypy" "$ENGINE_DIR"

    # Full engine test suite (credential-free and network-free by default;
    # the live subscription test stays skipped without TXT2CRS_RUN_LIVE_CODEX=1)
    run_check "Engine: Test suite (pytest)" "uv run --package txt2crs pytest -q" "$ENGINE_DIR"

    echo ""
fi

# Frontend validation
if [ "$RUN_FRONTEND" = true ]; then
    echo -e "${BLUE}--- Frontend Checks ---${NC}"

    # Type checking with TypeScript compiler
    run_check "Frontend: Type checking (tsc)" "npx tsc -p tsconfig.build.json --noEmit" "$PROJECT_ROOT/frontend"

    # Linting with Biome (check only, don't modify)
    run_check "Frontend: Linting (biome)" "npx biome check --no-errors-on-unmatched --files-ignore-unknown=true ./" "$PROJECT_ROOT/frontend"

    echo ""
fi

# Final summary
echo -e "${BLUE}========================================${NC}"
if [ "$FAILED" = true ]; then
    echo -e "${RED}  VALIDATION FAILED${NC}"
    echo -e "${RED}  Fix the issues above before committing${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo -e "${YELLOW}AI AGENT HINT:${NC} Run the specific failing command to see detailed errors."
    echo -e "${YELLOW}AI AGENT HINT:${NC} Use --json flag for structured output: ./scripts/validate-changes.sh --json"
    exit 1
else
    echo -e "${GREEN}  ALL CHECKS PASSED${NC}"
    echo -e "${GREEN}  Ready to commit${NC}"
    echo -e "${BLUE}========================================${NC}"
    exit 0
fi
