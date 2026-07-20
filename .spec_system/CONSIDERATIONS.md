# Considerations

> Institutional memory for AI assistants. Updated between phases via carryforward.
> **Line budget**: 600 max | **Last updated**: Phase 04 (2026-07-20)

---

## Active Concerns

Items requiring attention in upcoming phases. Review before each session.

### Technical Debt

None identified at Phase 04 closeout.

### External Dependencies

- [P00] **GitHub Actions billing is disabled**: Ten validation workflows cannot
  reach a runner. Local fallbacks pass, but CodeQL remains remote-only and
  every Skipped Workflows entry must be rechecked when billing is restored.
- [P00] **Deployment is intentionally local-only**: Docker Compose is the only
  project target. Do not add hosted deployment automation or assume a future
  platform without an explicit owner-approved scope change and new ADR.
- [P01-backend/packages/txt2crs] **Credentialed provider proof is still gated**:
  The deterministic suite proves exact GPT-5.6 and Tavily policy, but the live
  subscription/research acceptance test must run before hackathon submission.

### Performance / Security

- [P00-backend+backend/packages/txt2crs] **One process is mandatory**: The P0
  serial worker and SQLite store cannot safely run under multiple FastAPI
  workers. Preserve the container contract until a real queue replaces it.
- [P01-backend/packages/txt2crs] **Private-state retention is undefined**:
  Coordinated live-store erasure and complete local recovery now work, but
  learner requests, checkpoints, artifacts, logs, provider copies, and backup
  bundles still need explicit retention and encrypted-copy policies before
  release.

### Architecture

- [P00-backend+backend/packages/txt2crs] **Shell/package boundary is strict**:
  Routes and lifecycle code call the public `txt2crs` facade; generation,
  research, validation, persistence, and rendering remain package-owned.
- [P00-backend] **Container state path is fixed by image ownership**:
  Compose mounts `/var/lib/txt2crs`; arbitrary fresh mount targets would be
  root-owned and violate the non-root runtime contract.
- [P00-backend+frontend] **Generated OpenAPI is the cross-package contract**:
  Regenerate and format `openapi.json` plus `src/client` together after API
  changes; never patch generated frontend files by hand or add compatibility
  shims for retired server contracts.
- [P03-backend+backend/packages/txt2crs] **Job HTTP routes use public handles**:
  Submit through the facade and return `202` only after durable admission,
  then nudge the worker. Reads expose constructed public allowlists, hide
  owner mismatches as the same 404, and never reconstruct engine behavior.

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
- [P04-frontend] **Computed rendered QA proves visual safety**: Browser
  inspection, composed color contrast, real breakpoints, and reduced-motion
  checks catch CSP, overflow, and theme failures that source tokens cannot.
- [P00] **Local CI fallback needs exact evidence**: Billing failures are
  distinguishable from code failures only when each workflow has an exact
  local command, result, and known-issues entry.
- [P04-frontend+backend/packages/txt2crs] **Canonical identity spans retries**:
  Persist the exact accepted request/profile in the engine and retain one
  browser idempotency key only for an unchanged canonical draft retry.
- [P03-backend/packages/txt2crs] **Construct public allowlists**: Copy reviewed,
  bounded leaves into public contracts instead of filtering serialized private
  models after the fact; owner-scoped HTTP reads then preserve the same
  complete-or-null and owner-hidden semantics.
- [P01-backend/packages/txt2crs] **Checkpoint before provider construction**:
  Provider-free ingestion, policy, and preference acceptance makes denial and
  restart behavior deterministic and testable.
- [P01-backend/packages/txt2crs] **One context owns provider resources**:
  Enter temporary, HTTP, MCP, and Codex resources in dependency order and
  unwind them in reverse without masking the primary generation error.
- [P03-backend+backend/packages/txt2crs] **Cross-store erasure needs ordered
  ownership**: The engine barrier cancels and waits for owner work, removes
  artifacts before SQLite parents, and the shell calls it before PostgreSQL
  deletion. A purge failure keeps the account and reports safe, retryable
  partial progress.
- [P04-backend+backend/packages/txt2crs+frontend] **Facade browser tests protect
  boundaries**: A fresh test-owned state root and account can exercise real
  auth, admission, execution, recovery, delivery, and purge without provider
  credentials, private imports, or production-only fixture routes.
- [P02-backend] **Cache side effects behind one runtime owner**: Startup and
  finite maintenance refresh may probe the public engine aggregate, while
  browser reads return only immutable cached state and never compete with job
  execution or device authentication.
- [P02-backend] **Operational logs need field allowlists**: Static route names,
  methods, status, duration, finite codes, and attempt counts provide useful
  telemetry without retaining raw request, provider, exception, recipient, or
  infrastructure content.
- [P02-backend] **A lease follows background work, not the request**: Device
  authentication continues after its POST response, so one lifecycle monitor
  retains runtime ownership until terminal state or bounded shutdown.
- [P04-backend+frontend] **Authorization and polling follow server state**:
  Route guards run before feature queries mount; generated caches own server
  state, revisions cannot regress, polling exists only in waiting states, and
  the UI never invents a private provider or checkpoint state.
- [P04-frontend] **Artifact preview needs independent barriers**: Verify job,
  MIME, byte count, and filename before parsing bounded HTML; then strip active
  content, apply supported CSP, use an empty iframe sandbox, and revoke URLs.

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
- [P01-backend/packages/txt2crs] **Do not treat frozen models as deeply frozen**:
  Nested Pydantic values can still mutate; detach snapshots and revalidate
  their canonical identity at persistence boundaries.
- [P01-backend/packages/txt2crs] **Do not retain private exception context**:
  Safe outer text is insufficient when `__cause__` or `__context__` still
  contains learner content, paths, provider values, or SQL details; suppress
  context explicitly at the final safe translation boundary.
- [P01-backend/packages/txt2crs] **Do not let writer/read bounds drift**:
  Artifact state accepted by a writer must remain immediately readable through
  the same shared metadata and topology validation.
- [P01-backend/packages/txt2crs] **Do not use `executescript` for atomic upgrades**:
  Apply fixed statements within the explicit `BEGIN IMMEDIATE` transaction so
  schema changes and migration-version records commit together.
- [P04-frontend] **Do not split query eligibility from loading presentation**:
  Manifest enablement and its pending-state predicate must share the same
  complete result advertisement or inconsistent metadata can hang forever.

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
- [P01-backend/packages/txt2crs] **Use stdlib SQLite when the CLI is absent**:
  Python's `sqlite3` module can apply and inspect packaged migrations in the
  same interpreter environment as the engine.

---

## Resolved

Recently closed items (buffer - rotates out after 2 phases).

| Phase | Item | Resolution |
|-------|------|------------|
| P04 | Learner workspace integration | Public discovery, strict multimode intake, durable progress, four manifest-driven publications, private downloads, and sandboxed preview now use the generated jobs contract end to end. |
| P03 | Donor Item domain | Backend models, CRUD, routes, MCP exposure, generated contracts, learner UI, tests, guidance, and examples were removed or replaced without a stale compatibility shim. |
| P03 | Owner-scoped artifact delivery | Responses verify streams before headers, emit private/no-store/nosniff metadata, and own exactly-once cleanup on completion, failure, and disconnect. |
| P03 | Coordinated account erasure | Self-delete purges engine state before PostgreSQL identity deletion, preserves the account on purge failure, and supports safe idempotent retry. |
| P03 | Documented deploy helpers | Static executable-bit tests now protect the smoke-check and rollback commands documented for direct invocation. |

---

*Auto-generated by carryforward. Direct edits allowed but may be overwritten.*
