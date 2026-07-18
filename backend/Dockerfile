# =============================================================================
# Stage 1: base - shared dependency installation
# =============================================================================
FROM python:3.14.6 AS base

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#installing-uv
COPY --from=ghcr.io/astral-sh/uv:0.11.29 /uv /uvx /bin/

# Place executables in the environment at the front of the path
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#using-the-environment
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#compiling-bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy

ENV PYTHONPATH=/app

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

# =============================================================================
# Stage 2: production - optimized for Coolify deployment
# Target with: docker build --target production
# Coolify uses: dockerfile_target_build = "production"
# =============================================================================
FROM base AS production

# Install production dependencies only (no dev/test packages)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY ./scripts /app/scripts
COPY ./app /app/app

# Sync the project (production deps only)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Create non-root user for security
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check using Python stdlib (no curl needed in production image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import json, urllib.request; response = urllib.request.urlopen('http://localhost:8000/api/v1/utils/health/', timeout=5); data = json.load(response); raise SystemExit(0 if data.get('status') == 'healthy' else 1)" || exit 1

CMD ["fastapi", "run", "--workers", "4"]

# =============================================================================
# Stage 3: development - local dev with tests (default when no target specified)
# Used by: docker compose build
# =============================================================================
FROM base AS development

# Install ALL dependencies (including dev)
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY ./scripts /app/scripts
COPY ./app /app/app
COPY ./tests /app/tests

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["fastapi", "run", "--workers", "4"]
