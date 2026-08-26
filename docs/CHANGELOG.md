# Changelog

All notable changes to txt2crs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Archived entries are stored in [`archive/`](archive/).

## [Unreleased]

### Added

- Added `scripts/ci-create-env-files.sh`, which recreates the git-ignored
  `.env` and `backend/.env` from their committed templates so continuous
  integration jobs have a complete, secret-free configuration.

### Changed

- Migrated both MCP servers to MCP SDK 2.0, where `FastMCP` is renamed
  `MCPServer` and every transport setting moves off the constructor onto the
  call that starts a transport. `ResearchMcpApplication` now owns
  `create_streamable_http_application()`, so the loopback host, the `/mcp`
  path, and `stateless_http` are declared in exactly one place instead of
  being reached through the managed listener.

### Deprecated

### Removed

### Fixed

- Fixed every pull-request workflow, which had been failing before running any
  real check. Docker Compose could not interpolate `${POSTGRES_PASSWORD}` and
  `${FRONTEND_HOST}`, and importing `app.main` raised a Pydantic
  `ValidationError` for `ENVIRONMENT`, `PROJECT_NAME`, `POSTGRES_SERVER`,
  `POSTGRES_USER`, and `FIRST_SUPERUSER`, because neither `.env` file exists in
  a fresh checkout.
- Fixed a `tsc` failure in `frontend/tests/course-library.spec.ts`, where the
  throwing placeholder made TypeScript infer `() => never` for the library
  response gate and reject the later `resolve` assignment.
- Corrected the `actions/setup-python` pin comments across the workflows. The
  pinned commit is `v6.3.0`, not the `v6.0.0` the comments claimed, which the
  zizmor `ref-version-mismatch` audit reported as a finding.

### Security

- Restored `cryptography` to a patched release in `backend/uv.lock`. The
  python-packages group lock was resolved before the standalone `cryptography`
  security bump landed, so merging it reverted the pin to 49.0.0 and brought
  PYSEC-2026-3552 back. Re-resolved to 50.0.1.
- Allowlisted two historical gitleaks findings for synthetic `SECRET_KEY`
  fixtures in `backend/tests/scripts/test_start_local_script.py`. The values
  never authenticated anything and no longer appear in the current file, but
  the scan walks the full commit history.

## [1.2.5] - 2026-07-21

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

- Overrode the OpenAPI generator's development-only `js-yaml` dependency to
  patched version `4.3.0`, resolving the public repository's high-severity
  quadratic-CPU advisory without changing the shipped application runtime.

## [1.2.4] - 2026-07-21

### Added

### Changed

- Published the judge-facing repository, synchronized the immutable release
  identity and links, and completed the GitHub, YouTube, and Devpost field
  handoff from the repository's reviewed submission evidence.

### Deprecated

### Removed

### Fixed

### Security

- Audited the complete Git history before publication and enabled GitHub secret
  scanning, push protection, vulnerability alerts, and automated security
  updates for the public repository.

The complete dated release history through `1.2.3` is preserved in
[`archive/CHANGELOG_20260721.md`](archive/CHANGELOG_20260721.md).
