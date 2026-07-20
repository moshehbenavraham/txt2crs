# Versioning txt2crs

txt2crs follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
The repository version is stored in the root `VERSION` file. The Python
distribution version is stored in
`backend/packages/txt2crs/pyproject.toml` using the equivalent normalized
[PEP 440](https://peps.python.org/pep-0440/) spelling.

## Current stage

The current repository and Python package release is `1.0.3`. It is the third
maintenance release after the stable public API boundary established by
`1.0.0`. Future compatibility decisions follow Semantic Versioning from that
public boundary.

## Choosing the next version

- **PATCH** (`0.1.0` -> `0.1.1`): backward-compatible fixes.
- **MINOR** (`0.1.0` -> `0.2.0`): backward-compatible features. Before `1.0.0`,
  use a minor bump for intentional breaking changes and explain them in the
  changelog.
- **MAJOR** (`1.0.0` -> `2.0.0`): breaking public-API changes after `1.0.0`.
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
7. Complete and commit every tracked release and judge-facing asset.
8. Repeat the immutable version, distribution, image, health, and link checks
   on that exact clean commit.
9. Create an annotated Git tag named `v<version>`, such as `v1.0.0`.
10. Push the exact tested commit and tag, then verify the remote tag resolves
    to the same commit and add changelog comparison links if needed.

Released version numbers and tagged contents are immutable. Any subsequent
tracked change receives a new version.
