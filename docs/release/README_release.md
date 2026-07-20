# txt2crs Release Evidence

This directory indexes the bounded, public-safe evidence for the `1.0.0`
hackathon release. It does not contain raw learner input, artifact bodies,
credentials, provider payloads, prompts, account identifiers, local paths, or
unrestricted private links.

## Current State

Phase 05 Session 01 produced and validated the `1.0.0` candidate from exact
source revision `a80700863e99cdd34bed757873d969236cdf36fa`. Its real synthetic
GPT-5.6 plus Tavily job completed with exactly sixteen verified artifacts;
every inspection row passes and the canonical public ledger passes the strict
evidence validator.

The final annotated `v1.0.0` tag is intentionally deferred until Session 02
completes all tracked judge assets and repeats the immutable checks below. A
tracked change after the tag requires a new SemVer release.

## Evidence Index

| Evidence | Purpose | Public-safety boundary |
|----------|---------|------------------------|
| [`DETERMINISTIC_SAMPLE_1_0_0.md`](DETERMINISTIC_SAMPLE_1_0_0.md) | Reproducible credential-free input and expected public result shape | Synthetic input and aggregate output facts only |
| [`ARTIFACT_INSPECTION_1_0_0.md`](ARTIFACT_INSPECTION_1_0_0.md) | One review row for every deliverable/format pair | Judgments, sizes, and hashes; never artifact bodies |
| [`RELEASE_CANDIDATE_1_0_0.json`](RELEASE_CANDIDATE_1_0_0.json) | Canonical revision, version, build, evaluation, live, and artifact ledger | Strictly allowlisted hashes, counts, durations, and judgments only |
| [Session implementation notes](../../.spec_system/specs/phase05-session01-release-hardening-and-live-proof/implementation-notes.md) | Exact local commands, counts, known exceptions, and cleanup | Operational summaries without secrets or private payloads |

## Evidence Contract

Run the shared standard-library validator from the repository root:

```bash
python scripts/release_evidence.py validate-repository \
  --repository-root . \
  --expected-version 1.0.0 \
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

## Final Tag Handoff

Session 02 must complete all tracked judge assets before tagging. On the exact
final commit it must:

1. confirm the tree is clean and every public link is final;
2. rerun release/evidence tests and the repository version validator;
3. rebuild and inspect the wheel and source distribution;
4. rebuild and inspect both production images;
5. run production health and replacement smoke checks;
6. reconcile the final commit in the judge README, video, and Devpost fields;
7. create annotated tag `v1.0.0` on that commit; and
8. push the commit and tag, then verify the remote tag resolves to the same
   object.

No tracked edit is allowed after step 7 without selecting a new version.
