# Validation Report

**Session ID**: `phase05-session02-submission-assets-and-devpost`
**Package**: null (cross-cutting documentation and media)
**Validated**: 2026-07-20
**Base Commit**: `a47a61804e7eda353020957d8b344b67e737da42`
**Result**: PASS

## Validation Summary

| Check | Status | Notes |
|-------|--------|-------|
| Code Review | PASS | `code-review.md` is `RESOLVED`; all 3 medium and 2 low findings were repaired. |
| Tasks Complete | PASS | 16/16 tasks are checked. |
| Deliverables | PASS | All 10 specified deliverables exist and are non-empty; the screenshot directory contains six PNG images. |
| ASCII And LF | PASS | Changed text and session reports are ASCII with LF endings; repository whitespace checks pass. |
| Product Tests | PASS | Backend 517, engine 489, frontend 132, and both deterministic browser scenarios pass. |
| Database And Schema | N/A | No model, migration, engine persistence, or stored-data shape changed. |
| Success Criteria | PASS | Product story, six screenshots, narrated demo, Devpost copy, release evidence, and human handoff are complete. |
| Conventions | PASS | The work stays documentation/media-only and does not duplicate runtime or release logic. |
| Security And GDPR | PASS | No secret or private public value was found; GDPR is N/A because no personal-data behavior changed. |
| Behavioral Quality | N/A | No application behavior or source code changed. |
| UI Product Surface | PASS | No UI source changed; the final judge media shows the working learner journey without diagnostics or private values. |

**Overall**: PASS

## Evidence Ledger

| Check | Command Or Inspection | Result | Evidence |
|-------|-----------------------|--------|----------|
| Project state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Phase 5 Session 02 is current, cross-cutting, with 17 completed predecessors. |
| Code review | `code-review.md` plus complete base-to-HEAD inspection | PASS | Result is `RESOLVED`; 0 critical, 0 high, 3 medium, and 2 low findings are fixed. |
| Task completion | `tasks.md` checklist inspection | PASS | 16/16 task IDs are `[x]`; no task remains incomplete. |
| Deliverables | Explicit existence and non-empty checks | PASS | README, eight submission documents, six screenshots, and the ignored private MP4 candidate exist. |
| Repository gate | `./scripts/validate-changes.sh --json` | PASS | All 9 backend, engine, and frontend lint, format, type, and test steps pass. |
| Backend suite | Fresh migrated PostgreSQL 18 plus `uv run pytest tests/ -q` with isolated writable engine state | PASS | 517 passed in 16.81 seconds. |
| Engine suite | `uv run --package txt2crs pytest` | PASS | 489 passed; only the two explicit live-provider gates are skipped. |
| Frontend unit suite | `npm run test:unit` | PASS | 20 files and 132 tests pass. |
| Frontend production build | `npm run build` | PASS | TypeScript and Vite pass; 2,215 modules transform successfully. |
| Browser acceptance | Complete and failed deterministic Playwright scenarios | PASS | Each scenario passes 16 tests with one intentional opposite-scenario skip. |
| Answer-key recapture | Focused deterministic Playwright learner journey | PASS | Setup, learner journey, and cleanup pass 3/3; temporary capture hooks were removed. |
| Release contracts | Release evidence and workflow tests | PASS | 27/27 pass; candidate identity and canonical historical evidence validate. |
| Distributions | Two independent exact-source builds and byte comparison | PASS | Wheel `447e85e...98071` and sdist `976b023...01c4` are byte-identical across builds. |
| Production images | Build, inspect, health, and replacement checks | PASS | Backend `9b503211...80b4e` and frontend `176e1fda...143d9` pass; durable PostgreSQL and private engine state survive isolated replacement. |
| Screenshot identity | `sha256sum` and `file` over six PNG files | PASS | All hashes and dimensions match `PUBLIC_EVIDENCE_INDEX.md`. |
| Screenshot privacy | Original-resolution review and OCR pattern scan | PASS | No credential, email, account menu, private job reference, path, prompt, payload, or hidden reasoning appears. |
| Video identity | `ffprobe` and `sha256sum` | PASS | 142.600 seconds, H.264 1920x1080 at 30 fps, AAC, 5,863,350 bytes, expected hash. |
| Video craft review | Ten-frame contact sheet plus narration/storyboard comparison | PASS | Scene order, legibility, runtime model, Tavily research, learner value, and answer separation are clear. |
| Secret scan | `gitleaks git --log-opts=-2 --redact --no-banner` plus scoped scans | PASS | Both session commits and the judge package contain no detected leak. |
| Removed scope | File absence and content scan | PASS | No submission contract module/test exists; no agent publishing, receipt, public-repository, or completed-submission claim remains. |
| Human-only boundary | Handoff and cross-document comparison | PASS | Only the human may grant access, push branch/tag, upload video, edit/submit Devpost, or retain receipts. |

## Invocation Correction

The first full backend validation command sourced `.env` and accidentally
inherited Docker-only `/var/lib/txt2crs` paths while running on the host. It
produced one failure and 94 setup errors from host filesystem permission
denials after 422 tests had passed. No product assertion failed.

The exact suite was rerun against the same disposable migrated PostgreSQL 18
database with a private writable temporary engine state root. The corrected
run passed all 517 tests. The failed invocation is retained here so the
evidence does not hide or misclassify it.

## Deliverables

| Deliverable | Status |
|-------------|--------|
| `README.md` | PASS |
| `docs/submission/README_submission.md` | PASS |
| `docs/submission/screenshots/` (six PNG files) | PASS |
| `docs/submission/PUBLIC_EVIDENCE_INDEX.md` | PASS |
| `docs/submission/CODEX_FEEDBACK.md` | PASS |
| `docs/submission/VIDEO_STORYBOARD.md` | PASS |
| `.release-private/video/txt2crs-demo-1.0.0.mp4` | PASS |
| `docs/submission/DEVPOST_SUBMISSION.md` | PASS |
| `docs/submission/RELEASE_RECONCILIATION.md` | PASS |
| `docs/submission/HUMAN_PUBLISHING_HANDOFF.md` | PASS |

## Success Criteria

- [x] The README and submission copy communicate the real learner outcome.
- [x] Six reviewed synthetic screenshots show the complete learner journey.
- [x] The narrated 1080p demo is 142.600 seconds and ready for human upload.
- [x] The Education Devpost story and Codex Session ID are ready to paste.
- [x] Existing product and release checks pass on the final local package.
- [x] The human handoff contains the exact GitHub, YouTube, Devpost, deadline,
      and final-verification steps without assigning external actions to the
      agent.

## Scope-Specific Checks

Database/schema alignment is N/A because no persisted shape changed.
Behavioral Quality Checklist review is N/A because no application source
changed. Product-surface review remains PASS because the six screenshots and
video were visually inspected and the existing deterministic browser
journeys passed.

## Validation Result

### PASS

The judge package is substantive and product-focused: a working application,
reproducible proof, polished media, complete submission copy, and a short
human publishing handoff. There is no submission-specific contract framework.

No branch, tag, repository access, video platform, or Devpost state was
changed.

## Next Step

Next command: `updateprd`
