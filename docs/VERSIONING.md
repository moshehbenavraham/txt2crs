# Versioning txt2crs

txt2crs follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The current version is stored in the root `VERSION` file.

## Current stage

The current pre-release version is `0.1.1-dev.0`. Versions below `1.0.0`
represent initial development, so the public API may still change. The first
stable public API will be released as `1.0.0`.

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
3. Move relevant entries from `Unreleased` in `CHANGELOG.md` to a dated release
   heading such as `## [0.1.0] - 2026-07-17`.
4. Run the complete test suite and required quality checks.
5. Commit the release changes.
6. Create an annotated Git tag named `v<version>`, such as `v0.1.0`.
7. Push the commit and tag, then add changelog comparison links if needed.

Released version numbers are immutable. Any subsequent change receives a new
version.
