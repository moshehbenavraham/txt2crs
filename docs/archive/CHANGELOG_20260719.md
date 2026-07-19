# Changelog Archive - 2026-07-19

All notable changes to txt2crs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Archived entries are stored in [`archive/`](archive/).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.3.2] - 2026-07-19

### Changed

- Reviewed `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` against the
  repository state: repaired relative links broken by the move into
  `docs/ongoing-projects/`, updated the header status from Proposed to
  Adopted, and recorded per-phase progress (Phase 1 complete;
  Phases 2–4 not started).
- Extended `scripts/validate-changes.sh` with an engine section (ruff, mypy,
  and the credential-free pytest suite for the `txt2crs` package, plus an
  `engine` selector argument), closing the final open Phase 1 step of the
  input-to-course plan.
- Corrected the documented engine validation commands in `AGENTS.md` and
  `backend/packages/txt2crs/README_txt2crs.md` to run from
  `backend/packages/txt2crs/`: run from `backend/`, they resolved the
  application shell's pyproject configuration, whose mypy `exclude` of
  `packages/` silently checked zero engine files.

### Fixed

- Fixed a pre-existing argument-parsing bug in `scripts/validate-changes.sh`
  where passing two section selectors (for example `backend frontend`)
  disabled every section and the script reported success while running zero
  checks; selectors now combine, running exactly the named sections.
- Fixed two mypy 2.3 `comparison-overlap` errors in the engine, in the
  executor's post-generation status re-check and the system authenticator's
  post-refresh state re-check: both compare state that is legitimately
  mutated out-of-band (a nonlocal checkpoint callback and a background
  thread), so the stale-narrowed enum reads are now cast back to their full
  enum types. No behavior change; the 223-test engine suite still passes.

## [0.3.1] - 2026-07-19

### Changed

- Consolidated the implemented dashboard design system into
  `docs/dashboard-design.md` and refreshed the repository-local React visual
  and motion guidance to match the shipped workspace-index interface,
  responsive layouts, semantic motion roles, and reduced-motion behavior.
- Renamed the examples guide to `examples/README_examples.md`, updated its
  context-profile and directory-tree references, clarified root agent
  guidance, and recorded the completed boilerplate adoption decision.
- Organized active planning material, Build Week requirements, the TODO list,
  and the project image under `docs/ongoing-projects/`, updating repository,
  backend, documentation-index, and Make.com plan links to their new paths.

### Removed

- Removed the superseded dashboard design plan and the seven unreferenced
  FastAPI template images from the repository root.

## [0.3.0] - 2026-07-18

### Added

- Added a comprehensive, module-complete reconstruction of the original
  Make.com “Text to Course” system, including its architecture, data contracts,
  prompts, integrations, risks, migration decisions, and a prioritized
  hackathon feature/submission plan.
- Added the input-to-course system plan
  (`docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md`): phased adoption of a custom
  python-react-boilerplate shell, engine wiring, the P0 learner journey with
  a required idempotent completion email and first-class visual-experience
  requirements, and P1 delivery polish.
- Imported the conflict-free application-shell files from
  python-react-boilerplate v0.1.41 (`backend/app/`, `frontend/`, Docker
  Compose files, CI/tooling configuration, examples, scripts, and reference
  docs). Files conflicting with existing repository paths remain unmerged in
  the gitignored `boilerplate/` snapshot.

### Changed

- Merged the remaining boilerplate conflict files: `backend/pyproject.toml`
  is now the application-shell project ("app") and uv workspace root with
  `txt2crs` as a workspace dependency (lockfile regenerated); the root
  README, AGENTS.md, backend README, `.gitignore`, and scoped LICENSE (now
  including boilerplate 0BSD and upstream FastAPI Full Stack Template MIT
  provenance) were combined; root `CLAUDE.md`/`GEMINI.md` symlinks to
  `AGENTS.md` were restored.

## [0.2.1] - 2026-07-17

### Added

- Added app-owned ChatGPT device-code authentication for one dedicated
  hackathon system identity, backed by the packaged official Codex SDK/runtime
  rather than a preinstalled CLI, plus a temporary `txt2crs-system-auth`
  bootstrap entry point for use before the FastAPI setup screen exists.

### Security

- Isolated dedicated-system credentials under an explicit owner-only
  `CODEX_HOME`, forced ChatGPT/file-store authentication, blanked inherited
  API/research keys at the SDK process boundary, validated the OpenAI
  verification origin, and kept provider errors and token material out of
  frontend status.

## [0.2.0] - 2026-07-17

### Added

- Added a separately approved assessment blueprint, module-sized lesson
  contracts, evidence-backed instructor answers, and deterministic assessment
  support checks.
- Added real DOCX output for the course, review pack, student assessment, and
  instructor answer key, bringing private delivery to 16 rendered artifacts.
- Added cumulative per-stage and per-module checkpoints with restored hard
  budgets and worker-replacement resume that skips accepted work.
- Added an atomic private filesystem artifact store with hashed tenant paths,
  integrity manifests, owner-only modes, deletion, and retention purging.
- Added atomic rolling per-user and global admission limits for job count,
  reserved model tokens, and paid research allowance.
- Added a requirement-to-evidence package compliance matrix.
- Added a distinct noisy-extraction case to the fixed private evaluation
  corpus.
- Added private learner-rating, correction-reason, and human-review fields to
  evaluation snapshots while keeping public evaluation output aggregate-only.

### Changed

- Lesson writing now runs one bounded schema turn per approved module and
  assembles the canonical course from the plan and frozen evidence.
- Codex workers now require an explicit isolated `CODEX_HOME`, delegate
  credential refresh through the public SDK, preflight prompt-token capacity,
  and expose safe account/model/quota readiness.

### Security

- Prevented worker credential-directory inheritance, case-variant API-key
  inheritance, cross-tenant artifact paths, symlink reads, quota-reset restarts,
  and oversized prompt side effects.
