# Implementation Notes

**Session ID**: `phase05-session02-submission-assets-and-devpost`
**Started**: 2026-07-20 15:41
**Last Updated**: 2026-07-20 18:11

## Progress

| Metric | Value |
|--------|-------|
| Tasks completed | 16 / 16 |
| Blockers | 0 |

## Completed Evidence

### Release Prerequisites

- Prior Phase 05 Session 01 validation passed.
- Historical paid proof remains tied to
  `a80700863e99cdd34bed757873d969236cdf36fa`.
- Repository is Private; anonymous API and HTML access return 404.
- Git, GitHub CLI, Docker, uv, Node, npm, and ffmpeg are available.

### Product Story And Screenshots

- Root README now explains the learner outcome, reproducible sample, local
  Docker path, architecture, exact model policy, tests, privacy, and licenses.
- Six deterministic synthetic screenshots cover landing, intake, progress,
  results, inert course preview, and separate answer-key behavior.
- Each screenshot has recorded dimensions, SHA-256, and privacy review in
  `PUBLIC_EVIDENCE_INDEX.md`.

### Demo Video

- Candidate:
  `.release-private/video/txt2crs-demo-1.0.0.mp4`
- Duration: 142.600 seconds.
- Video: H.264 High, 1920x1080, 30 fps.
- Audio: AAC LC mono; -16.6 dB mean, -1.5 dB maximum.
- SHA-256:
  `cc78d540f41eb6bbb634540fbf70df0d98c9975a308a8ae984135fb492d5542f`.
- Ten sampled frames confirmed correct scene order, legibility, and no account
  controls or private job references.
- Video, narration, render scripts, and intermediates remain ignored.

### Devpost And Feedback

- Complete Education-category project story is in
  `docs/submission/DEVPOST_SUBMISSION.md`.
- Primary Codex feedback Session ID:
  `019f7990-e049-7242-9d36-dc1eb4462d69`.
- Submitter type and country remain account-only.

### Human Publishing Decision

All external publication and submission actions are human-only. The agent
prepares local assets and instructions; the human owns GitHub reviewer access,
branch/tag publication, YouTube upload, Devpost entry, and platform receipts.

An overengineered submission validator and its tests were removed. They added
no product or submission value and duplicated existing release checks. The
active session now measures the quality of the app, media, story, release
evidence, and handoff.

### Documentation Reconciliation

- Submission, release, event-requirement, system-plan, README, and changelog
  language now consistently treats external publishing as human-only.
- The repository no longer promises tracked public URLs or a post-tag receipt.
- The established release checks remain the only technical release framework.

### Asset Safety Verification

- The private video hash remains
  `cc78d540f41eb6bbb634540fbf70df0d98c9975a308a8ae984135fb492d5542f`;
  ffprobe reports 142.600 seconds, H.264 1920x1080 at 30 fps, and AAC audio.
- All six screenshot hashes and dimensions match the evidence index.
- Submission Markdown links resolve, text is ASCII/LF, and `git diff --check`
  passes.
- Scoped gitleaks scans found no secret in the submission or session package.
- No submission-specific validator or test file remains.

### Task T013 - Run Established Product And Release Gates

**Started**: 2026-07-20 17:55
**Completed**: 2026-07-20 17:59
**Duration**: 4 minutes

**Files Changed**:
- `README.md` - Restored the explicit credential-free fast-gate distinction
  caught by the complete backend regression suite.

**Verification**:
- `./scripts/validate-changes.sh --json`: PASS - 9/9 lint, format, type, focused
  backend, 489-test engine, and frontend gates pass.
- Release evidence and workflow tests: PASS - 27/27; candidate identity and
  canonical historical evidence also pass.
- Full backend suite: PASS - 517/517 after the README repair.
- Frontend: PASS - 132/132 unit tests and 2,215-module production build.
- Deterministic browser journeys: PASS - complete and failed scenarios each
  pass 16 tests with one intentional opposite-scenario skip.
- UI product/craft checks: PASS - browser coverage retains mobile, contrast,
  keyboard, progress, result, preview, answer-key, and recovery behavior.

### Task T014 - Verify The Complete Prebuild Judge Package

**Started**: 2026-07-20 17:59
**Completed**: 2026-07-20 18:02
**Duration**: 3 minutes

**Files Changed**:
- `README.md` - Corrected the engine license description to its actual scoped
  MIT-0 and Hermes-derived MIT terms.
- `docs/ongoing-projects/OPENAI_BUILD_WEEK_REQUIREMENTS.md` - Replaced one
  inherited smart-quote pair with ASCII punctuation.

**Verification**:
- 17 changed/new text deliverables: PASS - ASCII, LF, and relative links.
- `git diff --check`: PASS.
- Scoped Gitleaks scans: PASS - README, docs, and session files have no leak.
- Removed-scope scan: PASS - no submission validator, receipt, or false AGPL
  reference remains.
- Media identity: PASS - six screenshot hashes/dimensions and ignored video
  hash/streams match their reviewed records.

### Task T015 - Rebuild Distributions, Images, And Runtime

**Started**: 2026-07-20 18:02
**Completed**: 2026-07-20 18:05
**Duration**: 3 minutes

**Files Changed**:
- No tracked files; outputs remain in ignored local build storage and Docker.

**Verification**:
- Two independent distribution builds: PASS - byte-identical wheel
  `447e85e...98071` and sdist `976b023...01c4`, version `1.0.0`, scoped
  license, package README, and manifest present.
- Production images: PASS - backend `9b503211...80b4e` is non-root, one
  process, package `1.0.0`, healthy, and contains all email templates;
  frontend `176e1fda...143d9` contains the built app and healthcheck.
- `verify-production-baseline.sh`: PASS - import, UID 1001, owner-private
  state, and replacement-container reopen.
- Isolated root Compose: PASS - PostgreSQL, backend, and frontend healthy;
  application IDs changed on replacement while the database ID, private
  volume, mode-0600 marker, and marker bytes persisted.
- Cleanup: PASS - isolated containers, network, and volumes removed.

### Task T016 - Review And Commit The Final Local Package

**Started**: 2026-07-20 18:05
**Completed**: 2026-07-20 18:11
**Duration**: 6 minutes

**Files Changed**:
- `docs/submission/CODEX_FEEDBACK.md` - Avoided implying that the intended
  final judge-asset commit or tag already exists remotely.
- `docs/submission/HUMAN_PUBLISHING_HANDOFF.md` - Directed the human to review
  the final local release commit before any tag or push.
- `docs/submission/RELEASE_RECONCILIATION.md` - Kept local commit preparation
  separate from human-only external release actions.
- `docs/submission/PUBLIC_EVIDENCE_INDEX.md` - Described the synthetic
  test-account display in the answer-key frame exactly.

**Verification**:
- Six original-resolution screenshot reviews: PASS - the journey is legible,
  coherent, synthetic, and free of private values.
- Ten-frame video contact sheet: PASS - correct scene order, product-first
  story, correct `gpt-5.6-sol` runtime card, and no private value.
- Video identity: PASS - 142.600 seconds, H.264 1920x1080 at 30 fps, AAC, and
  SHA-256 `cc78d54...5542f`.
- Devpost, storyboard, evidence, and handoff review: PASS - claims agree with
  reproduced release evidence and reserve every external action for a human.
- Screenshot hashes/dimensions, ASCII/LF, relative links, removed-scope scan,
  and `git diff --check`: PASS.
- Scoped Gitleaks scans: PASS - README, submission assets, and session records
  contain no detected secret.
- Browser tooling note: the Browser plugin was unavailable, so repository-local
  Playwright supplied the deterministic browser evidence and each final image
  was separately inspected at original resolution.
- Local release commit and clean-tree verification: PASS - the complete
  tracked package is committed locally; no branch, tag, or external platform
  was changed.

## Next Command

`creview`
