# Versioning txt2crs

txt2crs follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The repository version is stored in the root `VERSION` file. The Python
distribution version is stored in
`backend/packages/txt2crs/pyproject.toml` using the equivalent normalized
[PEP 440](https://peps.python.org/pep-0440/) spelling.

## Current stage

The current repository and Python package release is `0.3.4`. Versions below
`1.0.0` represent initial development, so the public API may still change. The
first stable public API will be released as `1.0.0`.

## Choosing the next version

- **PATCH** (`0.1.0` → `0.1.1`): backward-compatible fixes.
- **MINOR** (`0.1.0` → `0.2.0`): backward-compatible features. Before `1.0.0`,
  use a minor bump for intentional breaking changes and explain them in the
  changelog.
- **MAJOR** (`1.0.0` → `2.0.0`): breaking public-API changes after `1.0.0`.
- **Pre-release** (`0.1.0-alpha.1`, `0.1.0-beta.1`, or `0.1.0-rc.1`): builds
  that are not yet stable.

## Release checklist

1. Confirm the intended version follows the rules above.
2. Replace the value in `VERSION` with the release version.
3. Update `backend/packages/txt2crs/pyproject.toml` to the PEP 440 equivalent,
   regenerate `backend/uv.lock`, and verify that the built distribution reports
   that version.
4. Move relevant entries from `Unreleased` in `CHANGELOG.md` to a dated release
   heading such as `## [0.1.0] - 2026-07-17`.
5. Run the complete test suite and required quality checks.
6. Build both the wheel and source distribution and inspect their contents.
7. Commit the release changes.
8. Create an annotated Git tag named `v<version>`, such as `v0.1.0`.
9. Push the commit and tag, then add changelog comparison links if needed.

Released version numbers are immutable. Any subsequent change receives a new
version.
