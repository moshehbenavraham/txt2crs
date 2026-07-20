# txt2crs Submission Evidence

This directory contains the prepared txt2crs OpenAI Build Week Education
submission assets. External publication and submission remain human-only.

The repository-root [README](../../README.md) is the judge starting point.
This directory contains submission evidence, while the existing
[release evidence](../release/README_release.md), [architecture](../ARCHITECTURE.md),
[configuration](../CONFIGURATION.md), and
[deployment policy](../deployment-policy.md) remain the technical sources of
truth.

## Evidence Index

| Evidence | Purpose |
|----------|---------|
| [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) | Prepared local asset review |
| [`PUBLIC_EVIDENCE_INDEX.md`](PUBLIC_EVIDENCE_INDEX.md) | Curated screenshots and bounded release proof |
| [`CODEX_FEEDBACK.md`](CODEX_FEEDBACK.md) | Primary Codex feedback Session ID and development summary |
| [`VIDEO_STORYBOARD.md`](VIDEO_STORYBOARD.md) | Verified demo video, narration, and upload metadata |
| [`DEVPOST_SUBMISSION.md`](DEVPOST_SUBMISSION.md) | Complete Education-category project story |
| [`RELEASE_RECONCILIATION.md`](RELEASE_RECONCILIATION.md) | Historical live proof versus intended tag identity |
| [`HUMAN_PUBLISHING_HANDOFF.md`](HUMAN_PUBLISHING_HANDOFF.md) | Exact human GitHub, YouTube, and Devpost steps |
| [`screenshots/`](screenshots/) | Synthetic, reviewed product frames |

## Public Safety Boundary

Tracked submission evidence may include:

- synthetic product input and deterministic public result shapes;
- bounded build, test, model-family, research, timing, and artifact counts;
- the private repository URL and intended release identity;
- one bounded Codex feedback Session ID required by the event; and
- the human publishing instructions required to finish the entry.

Tracked submission evidence must not include:

- credentials, cookies, browser storage, authentication state, or provider
  tokens;
- learner identities, email addresses, source bodies, prompts, provider
  payloads, hidden reasoning, or account-only form answers;
- local filesystem paths, private artifact URLs, unrestricted downloads, or
  raw generated publication bodies; or
- invented legal, regulatory, retention, provider-deletion, security-contact,
  CODEOWNERS, or hosted-deployment claims.

Raw screen recordings, authenticated browser profiles, private artifacts,
editing intermediates, and platform receipts remain outside Git. The verified
video candidate stays in the ignored private release workspace until the human
operator uploads it.

## Release Identity

The paid synthetic `gpt-5.6-sol` plus Tavily proof remains tied to historical
source revision `a80700863e99cdd34bed757873d969236cdf36fa`. Later repairs and
these tracked judge assets form a different final commit. The human operator
tags the reviewed final commit as `v1.0.1`; the historical provider run is
never relabeled as if it executed from the later commit.

No tracked edit may follow the final tag without selecting a new SemVer
release.

## Verification

Use the existing product, release, distribution, image, and smoke checks in
[`docs/release/README_release.md`](../release/README_release.md). Then follow
[`HUMAN_PUBLISHING_HANDOFF.md`](HUMAN_PUBLISHING_HANDOFF.md) for the external
actions that only the human operator may perform.
