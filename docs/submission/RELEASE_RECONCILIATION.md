# Release Reconciliation

**Version**: `1.0.4`
**Intended tag**: `v1.0.4`
**Repository**: <https://github.com/moshehbenavraham/txt2crs>
**Repository visibility**: Private
**Intended release**:
<https://github.com/moshehbenavraham/txt2crs/tree/v1.0.4>
**Historical live revision**:
`a80700863e99cdd34bed757873d969236cdf36fa`

## Identity Boundary

The release evidence intentionally separates:

1. the historical paid provider proof;
2. the later reviewed release-candidate work; and
3. the final commit that the human operator will tag as `v1.0.4`.

The live proof used exact `gpt-5.6-sol` and Tavily research from revision
`a80700863e99cdd34bed757873d969236cdf36fa`. Later documentation, media, and
release repairs do not relabel that historical execution.

The supporting records are:

- [candidate ledger](../release/RELEASE_CANDIDATE_1_0_0.json);
- [sixteen-artifact inspection](../release/ARTIFACT_INSPECTION_1_0_0.md); and
- [deterministic sample](../release/DETERMINISTIC_SAMPLE_1_0_0.md).

## Repository And License

The repository remains Private. Anonymous GitHub requests returning 404 are
expected; judges require explicit private reviewer access from the human
operator.

The root `LICENSE` defines the repository's scoped provenance. The reusable
engine retains its dedicated license and Hermes Agent attribution under
`backend/packages/txt2crs/LICENSE`.

## Human Release Boundary

No GitHub visibility change, reviewer invitation, branch push, tag creation,
tag push, YouTube upload, or Devpost submission is part of agent execution.

After the final local release checks pass, the human operator:

1. reviews the complete local release commit;
2. grants both event reviewers private repository access;
3. creates annotated tag `v1.0.4` on that exact commit;
4. pushes the branch and tag;
5. publishes and verifies the demo video;
6. submits the Education entry on Devpost; and
7. keeps platform confirmation details outside the tagged tree.

Exact instructions are in
[`HUMAN_PUBLISHING_HANDOFF.md`](HUMAN_PUBLISHING_HANDOFF.md).

Any tracked change after `v1.0.4` requires a new SemVer release rather than
moving the tag.
