# txt2crs Port Allocations

txt2crs uses fixed, project-owned host ports so it never silently falls back
to a port assigned to another local application. These defaults are registered
in `/home/aiwithapex/projects/1-PORT-INVENTORY/PORT-MAP.md`.

The root `.env` controls Docker Compose host mappings. Direct host-development
and deterministic browser-test listeners are fixed in their owning tools so a
collision fails visibly.

## Host-bound ports

| Port | Listener | When used | Source |
|------|----------|-----------|--------|
| 86 | Traefik HTTP / local proxy | Optional proxy and production overlay | `TRAEFIK_HTTP_PORT` |
| 1029 | Mailcatcher SMTP | Docker local support | `MAILCATCHER_SMTP_PORT` |
| 1084 | Mailcatcher web UI | Docker local support | `MAILCATCHER_WEB_PORT` |
| 4177 | Vite preview | Direct frontend preview | `frontend/vite.config.ts` |
| 4324 | Jaeger OTLP gRPC | Docker observability | `OTLP_GRPC_PORT` |
| 4325 | Jaeger OTLP HTTP | Docker observability | `OTLP_HTTP_PORT` |
| 5195 | Frontend application | Docker and default Playwright | `FRONTEND_PORT` |
| 5196 | Vite development server | Direct frontend development | `frontend/vite.config.ts` |
| 5197 | Deterministic frontend | Isolated Playwright journey | `frontend/playwright.jobs.config.ts` |
| 5450 | PostgreSQL | Docker host tools and direct backend development | `POSTGRES_PORT` |
| 8016 | FastAPI backend | Docker and direct backend development | `BACKEND_PORT` |
| 8017 | Deterministic backend | Isolated Playwright journey | `frontend/playwright.jobs.config.ts` |
| 8102 | Traefik dashboard | Docker local support | `TRAEFIK_DASHBOARD_PORT` |
| 8103 | Adminer | Docker local support | `ADMINER_PORT` |
| 8443 | Traefik HTTPS | Optional production overlay | `TRAEFIK_HTTPS_PORT` |
| 8765 | Research MCP | Direct backend development, loopback only | `TXT2CRS_RESEARCH_MCP_PORT` |
| 9327 | Playwright HTML report | Docker Playwright profile | `PLAYWRIGHT_REPORT_PORT` |
| 16689 | Jaeger UI | Docker observability | `JAEGER_UI_PORT` |

The reference local path needs the frontend on 5195 and backend on 8016. Docker
also publishes the support services so diagnostics do not require changing
Compose files.

## Container-internal ports

These ports stay inside the txt2crs Docker networks. They are not host
reservations and may safely match container ports used by other projects.

| Port | Internal service use |
|------|----------------------|
| 80 | Frontend Nginx and Traefik HTTP entrypoint |
| 443 | Traefik HTTPS entrypoint |
| 1025 | Mailcatcher SMTP |
| 1080 | Mailcatcher web UI |
| 4317 | Jaeger OTLP gRPC receiver |
| 4318 | Jaeger OTLP HTTP receiver |
| 5432 | PostgreSQL |
| 8000 | FastAPI backend |
| 8080 | Adminer and Traefik dashboard |
| 9323 | Playwright HTML report |
| 16686 | Jaeger UI |

## Outbound and dynamic ports

- SMTP 587 is an optional outbound provider connection, not a txt2crs
  listener.
- Research MCP port `0` is accepted only when a test deliberately asks the
  operating system for an ephemeral loopback port. The application default is
  the registered fixed port 8765.
- HTTP 80 and HTTPS 443 in URL-safety logic describe standard remote URL
  semantics; they do not publish additional host listeners.

## Overrides

Edit the ignored root `.env` to override a Docker host mapping. Keep every
override unique, update the central port map first, and keep `FRONTEND_HOST`
aligned with `FRONTEND_PORT`. `scripts/start-local.sh` rejects malformed or
duplicate mappings before it invokes Docker and reports conflicts with already
running foreign containers.
