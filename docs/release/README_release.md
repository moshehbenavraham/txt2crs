# txt2crs Release Evidence

This directory indexes bounded, public-safe release evidence for the initial
hackathon release and later inspected improvements. It does not contain raw
learner input, artifact bodies, credentials, provider payloads, prompts,
account identifiers, local paths, or unrestricted private links.

## Current State

The completed release work produced and validated the `1.0.0` candidate. Its
historical live proof is tied to exact source revision
`a80700863e99cdd34bed757873d969236cdf36fa`: a synthetic GPT-5.6 plus Tavily
job completed with exactly sixteen verified artifacts. Every inspection row
passes and the canonical public ledger passes the strict evidence validator.

All tracked judge assets are complete. The final annotated `v1.2.1` tag is
intentionally left to the human release operator after one final review of the
exact current commit. Tag creation and pushing are human-only actions. A
tracked change after the tag requires a new SemVer release.

## Evidence Index

| Evidence | Purpose | Public-safety boundary |
|----------|---------|------------------------|
| [`DETERMINISTIC_SAMPLE_1_0_0.md`](DETERMINISTIC_SAMPLE_1_0_0.md) | Reproducible credential-free input and expected public result shape | Synthetic input and aggregate output facts only |
| [`ARTIFACT_INSPECTION_1_0_0.md`](ARTIFACT_INSPECTION_1_0_0.md) | One review row for every deliverable/format pair | Judgments, sizes, and hashes; never artifact bodies |
| [`PUBLICATION_DESIGN_INSPECTION_1_2_1.md`](PUBLICATION_DESIGN_INSPECTION_1_2_1.md) | Cross-format visual, structural, responsive, print, and office-rendering inspection for the publication design system | Synthetic fixture, dimensions, page counts, and judgments only |
| [`RELEASE_CANDIDATE_1_0_0.json`](RELEASE_CANDIDATE_1_0_0.json) | Canonical revision, version, build, evaluation, live, and artifact ledger | Strictly allowlisted hashes, counts, durations, and judgments only |
| [Session implementation notes](../../.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md) | Exact local commands, counts, known exceptions, and cleanup | Operational summaries without secrets or private payloads |

## Evidence Contract

Run the shared standard-library validator from the repository root:

```bash
python scripts/release_evidence.py validate-repository \
  --repository-root . \
  --expected-version 1.2.1 \
  --mode candidate \
  --revision <40-character-candidate-commit>
```

After the candidate ledger exists, validate and rewrite its canonical byte
form:

```bash
python scripts/release_evidence.py validate-evidence \
  --input docs/release/RELEASE_CANDIDATE_1_0_0.json \
  --output docs/release/RELEASE_CANDIDATE_1_0_0.json \
  --mode candidate \
  --revision <40-character-candidate-commit>
```

The validator requires:

- one synchronized SemVer across `VERSION`, engine package metadata,
  `backend/uv.lock`, `docs/VERSIONING.md`, and `docs/CHANGELOG.md`;
- exact wheel, source-distribution, backend-image, and frontend-image hashes;
- all thirteen fixed evaluation cases passing with no private case data;
- an explicit GPT-5.6 and research-used live fact;
- exactly four deliverables by four formats; and
- six `PASS` inspection dimensions for every artifact.

Unknown fields fail closed. Email-shaped strings, URLs, absolute paths, and
unsafe evidence fields are rejected even inside an otherwise allowed object.

## Private Working Boundary

Raw live work belongs only in ignored local paths:

- `.release-private/`
- `docs/release/private/`
- `docs/release/raw/`
- `docs/release/*.private.json`
- `docs/release/*.private.md`

Those locations may contain authenticated state or artifact content and must
use owner-only permissions. They are removed after the public-safe ledger is
derived. Project `.env` files remain the only supported location for ordinary
local secrets and are already ignored.

## Known External Exception

GitHub Actions billing currently rejects jobs before a runner starts. Every
locally executable workflow equivalent remains required and is recorded in
the session notes. Remote CodeQL has no exact local replacement and remains an
open low-severity external finding; this directory does not describe it as
passing.

## Final Human Release Handoff

All tracked judge assets and local release checks are complete. The human
operator then:

1. reviews the exact local commit and confirms the tree is clean;
2. rerun release/evidence tests and the repository version validator;
3. rebuild and inspect the wheel and source distribution;
4. rebuild and inspect both production images;
5. run production health and replacement smoke checks;
6. grants both required reviewers private repository access;
7. creates annotated tag `v1.2.1` on that exact commit;
8. pushes the commit and tag and verifies the remote refs;
9. publishes the verified demo video; and
10. completes and submits the Education entry on Devpost.

Exact platform instructions are in
[`docs/submission/HUMAN_PUBLISHING_HANDOFF.md`](../submission/HUMAN_PUBLISHING_HANDOFF.md).
No tracked edit is allowed after tagging without selecting a new version.
