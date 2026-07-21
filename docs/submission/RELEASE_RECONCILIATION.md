# Release Reconciliation

**Version**: `1.2.5`
**Release tag**: `v1.2.5`
**Repository**: <https://github.com/moshehbenavraham/txt2crs>
**Repository visibility**: Public
**Immutable release**:
<https://github.com/moshehbenavraham/txt2crs/tree/v1.2.5>
**Historical live revision**:
`a80700863e99cdd34bed757873d969236cdf36fa`

## Identity Boundary

The release evidence intentionally separates:

1. the historical paid provider proof;
2. the later reviewed release-candidate work; and
3. the final public commit preserved by `v1.2.5`.

The live proof used exact `gpt-5.6-sol` and Tavily research from revision
`a80700863e99cdd34bed757873d969236cdf36fa`. Later documentation, media, and
release repairs do not relabel that historical execution.

The supporting records are:

- [candidate ledger](../release/RELEASE_CANDIDATE_1_0_0.json);
- [sixteen-artifact inspection](../release/ARTIFACT_INSPECTION_1_0_0.md); and
- [deterministic sample](../release/DETERMINISTIC_SAMPLE_1_0_0.md).

## Repository And License

The repository is Public. Anonymous GitHub requests must return the repository
and its `v1.2.5` tag without account access.

The root `LICENSE` defines the repository's scoped provenance. The reusable
engine retains its dedicated license and Hermes Agent attribution under
`backend/packages/txt2crs/LICENSE`.

## Human Release Boundary

GitHub publication, security settings, branch publication, and the immutable
tag are complete. The human operator still:

1. publishes and verifies the demo video;
2. submits the Education entry on Devpost; and
3. keeps platform confirmation details outside the tagged tree.

Exact instructions are in
[`HUMAN_PUBLISHING_HANDOFF.md`](HUMAN_PUBLISHING_HANDOFF.md).

Any tracked change after `v1.2.5` requires a new SemVer release rather than
moving the tag.
