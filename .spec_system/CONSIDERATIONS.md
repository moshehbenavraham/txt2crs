# Considerations

> Institutional memory for AI assistants. Updated between phases via carryforward.
> **Line budget**: 600 max | **Last updated**: Phase 00 (2026-07-19)

---

## Active Concerns

Items requiring attention in upcoming phases. Review before each session.

### Technical Debt

- [P00-backend+frontend] **Donor items remain temporary**: Keep the existing
  item routes and UI only until durable jobs acceptance coverage exists; Phase
  03 must remove the domain without breaking authentication.
- [P00-backend] **Request logs expose raw request metadata**: The logger writes
  paths, query strings, and client IPs; password-recovery paths can contain an
  email. Sanitize to route templates and define retention before public use.

### External Dependencies

- [P00] **GitHub Actions billing is disabled**: Nine validation workflows cannot
  reach a runner. Local fallbacks pass, but CodeQL remains remote-only and
  every Skipped Workflows entry must be rechecked when billing is restored.
- [P00] **Deployment is intentionally local-only**: Docker Compose is the only
  project target. Do not add hosted deployment automation or assume a future
  platform without an explicit owner-approved scope change and new ADR.
- [P00] **Complete local backups are not proven**: PostgreSQL dump tooling
  exists, but recovery must also cover the private engine-state volume and be
  tested while no writer is active.

### Performance / Security

- [P00-backend+backend/packages/txt2crs] **One process is mandatory**: The P0
  serial worker and SQLite store cannot safely run under multiple FastAPI
  workers. Preserve the container contract until a real queue architecture
  replaces it.
- [P00-backend/packages/txt2crs] **Private state needs lifecycle coverage**:
  SQLite jobs, artifacts, and Codex credentials share one owner-only volume;
  future retention, deletion, and backup work must preserve this boundary.
- [P00-backend] **Readiness is still shell-only**: Current readiness proves
  PostgreSQL and version health. Phase 02 must add truthful engine, worker,
  storage, research, and provider capability readiness before job admission.

### Architecture

- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  Routes and lifecycle code call the public `txt2crs` facade; generation,
  research, validation, persistence, and rendering remain package-owned.
- [P00-backend] **Container state path is fixed by image ownership**:
  Compose mounts `/var/lib/txt2crs`; arbitrary fresh mount targets would be
  root-owned and violate the non-root runtime contract.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**:
  Regenerate and format `openapi.json` plus `src/client` together after API
  changes; never patch generated frontend files by hand.

---

## Lessons Learned

Proven patterns and anti-patterns. Reference during implementation.

### What Worked

- [P00] **Layer static and runtime contracts**: Fast file-shape tests catch
  topology drift early, while isolated image/Compose smokes prove ownership,
  imports, persistence, health, and cleanup under real processes.
- [P00-backend] **Fail unsafe paths at settings construction**: Normalize
  absolute paths, reject symlinks and overlaps, and pass only canonical private
  boundaries into engine factories.
- [P00-frontend] **Rendered QA complements source checks**: Browser inspection
  caught learner-visible devtools that title and branding tests could not.
- [P00] **Local CI fallback needs exact evidence**: Billing failures are
  distinguishable from code failures only when each workflow has an exact
  local command, result, and known-issues entry.
- [P00] **Tests-first works for deployment files**: Static contracts for
  Dockerfiles, Compose, workflow YAML, and generation scripts made each
  infrastructure repair observable before implementation.

### What to Avoid

- [P00-backend] **Do not trust host-only workspace imports**: Copy workspace
  package sources before the first image `uv sync` and prove the import inside
  the built container.
- [P00-backend] **Do not leak host ports into service networks**: Containers
  reach PostgreSQL on port 5432 even when local tools use a different published
  host port.
- [P00-backend] **Do not assume Pydantic ignores process environment**:
  `_env_file=None` does not isolate inherited variables; tests must clear or
  override every environment key they own.
- [P00] **Do not set aspirational coverage gates**: CI thresholds must start
  at measured coverage and rise only with tests, or the workflow is knowingly
  red.
- [P00] **Do not run generic whitespace fixes on source-byte fixtures**:
  Versioned protocol captures, legacy exports, and noisy OCR evaluations need
  precise documented exclusions.

### Tool/Library Notes

- [P00-backend/packages/txt2crs] **Run engine tools from its package root**:
  Its Ruff, mypy, and pytest configuration is independent of the backend
  workspace root.
- [P00] **Pre-commit does not inspect untracked files with `--all-files`**:
  Stage new reports before the final hook pass or check them explicitly first.
- [P00-frontend] **Nginx includes curl in the pinned image**: The frontend
  image can use a direct internal `/health` probe without adding a package
  layer.
- [P00] **Client generation is formatter-owning**: The generation script must
  format both the OpenAPI document and generated client before later hooks.

---

## Resolved

Recently closed items (buffer - rotates out after 2 phases).

| Phase | Item | Resolution |
|-------|------|------------|
| P00 | Host/container engine parity | Both backend image targets install and import the workspace package. |
| P00 | Unsafe multi-worker runtime | Development and production-like image targets run one non-root FastAPI process. |
| P00 | Unconfined private state | Typed settings, owner-only paths, and one persistent state volume now fail closed and pass runtime smokes. |
| P00 | Frontend health gap | Nginx exposes stable JSON and participates in local Docker health probing. |

---

*Auto-generated by carryforward. Direct edits allowed but may be overwritten.*
