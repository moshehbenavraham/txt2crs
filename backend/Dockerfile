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

# The backend project declares txt2crs as a uv workspace dependency. uv must
# see the workspace member before the first sync; otherwise a host install can
# work while the production image fails because `packages/txt2crs` is absent.
COPY ./packages /app/packages

# =============================================================================
# Stage 2: production-like image used by local release validation
# Target with: docker build --target production
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

# Create the same fixed-UID runtime identity used by local Compose. The private
# mount points are seeded with owner-only permissions so a fresh named volume
# keeps the correct ownership when Docker initializes it from the image.
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser && \
    install -d -m 0700 -o appuser -g appuser \
        /var/lib/txt2crs \
        /var/lib/txt2crs/artifacts \
        /var/lib/txt2crs/codex-home \
        /tmp/txt2crs-worker && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check using Python stdlib (no curl needed in production image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import json, urllib.request; response = urllib.request.urlopen('http://localhost:8000/api/v1/utils/health/', timeout=5); data = json.load(response); raise SystemExit(0 if data.get('status') == 'healthy' else 1)" || exit 1

# P0 owns one serial engine worker in-process, so the ASGI server must also
# remain a single process. Horizontal scaling requires a future queue design.
CMD ["fastapi", "run", "app/main.py"]

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

# Development runs application code as the same non-root identity as
# production. Tests that truly need another identity must use a dedicated test
# target instead of weakening the application image.
RUN groupadd --gid 1001 appuser && \
    useradd --uid 1001 --gid appuser --no-create-home --shell /usr/sbin/nologin appuser && \
    install -d -m 0700 -o appuser -g appuser \
        /var/lib/txt2crs \
        /var/lib/txt2crs/artifacts \
        /var/lib/txt2crs/codex-home \
        /tmp/txt2crs-worker && \
    chown -R appuser:appuser /app

USER appuser

CMD ["fastapi", "run", "app/main.py"]
