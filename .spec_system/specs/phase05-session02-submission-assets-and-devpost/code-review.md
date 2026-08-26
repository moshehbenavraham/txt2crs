# Code Review and Repair Report

**Session ID**: `phase05-session02-submission-assets-and-devpost`
**Package**: Cross-cutting
**Reviewed**: 2026-07-20
**Base Commit**: `a47a61804e7eda353020957d8b344b67e737da42`
**Scope**: All changes since the base commit, including the mid-session commit
and review repairs
**Result**: RESOLVED

## Review Surface

**Files reviewed**:

- `.spec_system/state.json` - tracked modification in the session commit.
- `.spec_system/PRD/phase_05/session_02_submission_assets_and_devpost.md` -
  review repair to the source session definition.
- `.spec_system/specs/phase05-session02-submission-assets-and-devpost/spec.md` -
  new session specification plus review repair.
- `.spec_system/specs/phase05-session02-submission-assets-and-devpost/tasks.md` -
  new completed task checklist.
- `.spec_system/specs/phase05-session02-submission-assets-and-devpost/implementation-notes.md` -
  new implementation evidence plus review reconciliation.
- `README.md` - rewritten judge-facing product and local-run guide.
- `docs/CHANGELOG.md` - submission-package release entry.
- `docs/ongoing-projects/INPUT_TO_COURSE_SYSTEM_PLAN.md` - human-publishing
  boundary reconciliation.
- `docs/archive/build-week/OPENAI_BUILD_WEEK_REQUIREMENTS.md` - prepared-local
  versus human-external checklist.
- `docs/release/DETERMINISTIC_SAMPLE_1_0_0.md` - corrected browser command.
- `docs/release/README_release.md` - human release handoff.
- `docs/archive/build-week/CODEX_FEEDBACK.md` - new bounded Session ID record.
- `docs/archive/build-week/DEVPOST_SUBMISSION.md` - new Education project story.
- `docs/archive/build-week/HUMAN_PUBLISHING_HANDOFF.md` - new external-action handoff.
- `docs/archive/build-week/PUBLIC_EVIDENCE_INDEX.md` - new image identity and safety
  ledger plus review repair.
- `docs/archive/build-week/README_build_week.md` - new submission evidence index.
- `docs/archive/build-week/RELEASE_RECONCILIATION.md` - new release identity boundary.
- `docs/archive/build-week/SUBMISSION_CHECKLIST.md` - new prepared-asset checklist.
- `docs/archive/build-week/VIDEO_STORYBOARD.md` - new video record and upload metadata.
- `docs/archive/build-week/screenshots/01-landing.png` - new reviewed PNG.
- `docs/archive/build-week/screenshots/02-create.png` - new reviewed PNG.
- `docs/archive/build-week/screenshots/03-progress.png` - new reviewed PNG.
- `docs/archive/build-week/screenshots/04-results.png` - new reviewed PNG.
- `docs/archive/build-week/screenshots/05-course-preview.png` - new reviewed PNG.
- `docs/archive/build-week/screenshots/06-answer-key.png` - new PNG regenerated during
  review.

The six binary PNG files were reviewed at original resolution. Their exact
dimensions and SHA-256 values are recorded in
`docs/archive/build-week/PUBLIC_EVIDENCE_INDEX.md`; byte-level source inspection is not
meaningful for rendered evidence. The ignored MP4 was reviewed through
`ffprobe`, SHA-256, and a ten-frame contact sheet and is not part of Git.
`code-review.md` was created by this command and self-reviewed with the final
diff.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git diff --cached "$BASE"`, and
`git ls-files --others --exclude-standard`.

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `README.md:117` - The committed quick start told Docker users to run the
  host authentication helper before starting Compose and incorrectly said its
  credentials populated Docker's private mounted state. The script fixes its
  state at `.txt2crs-system/`, while Compose mounts a distinct named volume at
  `/var/lib/txt2crs`. | Fix: Start Compose first, authenticate the Docker
  runtime from `/setup`, and label `auth-codex.sh` as host-only recovery. |
  Status: FIXED
- `docs/archive/build-week/screenshots/06-answer-key.png` - The committed public frame
  retained a truncated synthetic test email/account control, contrary to the
  session's public-safety rule. | Fix: Regenerated a focused 1440x900 frame
  from the deterministic browser journey with the account footer and opaque
  job reference hidden, then updated its hash and dimensions. | Status: FIXED
- `.spec_system/PRD/phase_05/session_02_submission_assets_and_devpost.md:12` -
  The source session definition still required agent-operated publication,
  tag/push operations, a Devpost receipt, and a redundant submission
  validator after the active session had moved to human-only publishing. |
  Fix: Rewrote the source objective, scope, deliverables, and success criteria
  around real judge assets, established release gates, and an exact human
  handoff. | Status: FIXED

### Low

- `.spec_system/specs/phase05-session02-submission-assets-and-devpost/spec.md:7`
  - The session omitted its base commit, which would make `creview` fall back
  to `HEAD` and skip the actual session diff. | Fix: Recorded exact parent
  commit `a47a61804e7eda353020957d8b344b67e737da42`. | Status: FIXED
- `docs/CHANGELOG.md:25` - The session commit claimed removal of a validator
  that was never part of a committed release. | Fix: Removed the misleading
  changelog entry; the changelog now records only shipped judge assets and
  handoff material. | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- The short authentication helper remains valuable for host-only engine
  development. `scripts/auth-codex.sh`, its contract test, and
  `docker-compose.yml` prove that its host state and Docker's named volume are
  intentionally separate, so the review corrected documentation instead of
  changing either runtime.
- External GitHub, YouTube, and Devpost actions remain human-only. No
  repository visibility, invitation, branch, tag, upload, or submission state
  was changed.
- The Behavioral Quality Checklist is N/A because this session changes
  documentation and media only. Existing runtime behavior was re-exercised;
  no application source or generated client changed.

## Behavior Changes

- Docker quick-start users are now directed to the working in-application
  device-login flow; the host helper is no longer presented as populating the
  Docker credential volume.
- The sixth judge screenshot is now a focused answer-key view with no account
  display or private job reference.
- The source session job now enforces the requested human-only publishing
  boundary.

No application runtime behavior changed.

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence / Blocker |
|-------|-----------------------|--------|--------------------|
| Deterministic state | `bash .spec_system/scripts/analyze-project.sh --json` | PASS | Current session and 17 completed predecessors resolved. |
| Review inventory | `git status`; `git log --oneline "$BASE"..HEAD`; `git diff "$BASE"`; `git diff --cached "$BASE"`; `git ls-files --others --exclude-standard` | PASS | One mid-session commit and the complete 25-file repair surface inventoried. |
| Focused docs/container contracts | `POSTGRES_SERVER=127.0.0.1 POSTGRES_PORT=55432 uv run pytest tests/scripts/test_system_auth_script_contract.py tests/scripts/test_container_contract.py -q` | PASS | 20/20 tests pass against disposable migrated PostgreSQL 18. |
| Deterministic answer-key journey | `TXT2CRS_BROWSER_SCENARIO=complete POSTGRES_SERVER=127.0.0.1 POSTGRES_PORT=55432 npx playwright test --config=playwright.jobs.config.ts --project=chromium --grep "submits one prompt and survives direct progress refresh"` | PASS | Setup, complete learner journey, screenshot capture, and owner cleanup: 3/3 pass. Temporary capture hooks removed. |
| Repository gate | `POSTGRES_SERVER=127.0.0.1 POSTGRES_PORT=55432 ./scripts/validate-changes.sh --json` | PASS | 9/9 backend, engine, and frontend lint, format, type, and test gates pass. |
| Screenshot visual review | Original-resolution inspection of all six PNG files, including regenerated `06-answer-key.png` | PASS | Clear learner journey; no credential, email, account menu, private job ID, path, prompt, payload, or diagnostic. |
| Screenshot identity | `sha256sum docs/archive/build-week/screenshots/*.png`; `file docs/archive/build-week/screenshots/*.png` | PASS | Six hashes and dimensions match the evidence index; final frame is 1440x900. |
| Screenshot OCR safety | `tesseract "$screenshot" stdout \| rg 'browser-.*@|@example\\.com|job-[a-f0-9]{12}|private job reference'` for all six PNG files | PASS | No private-value pattern found. |
| Video identity | `ffprobe ... .release-private/video/txt2crs-demo-1.0.0.mp4`; `sha256sum .release-private/video/txt2crs-demo-1.0.0.mp4` | PASS | 142.600 seconds, H.264 1920x1080 at 30 fps, AAC, hash `cc78d54...5542f`. |
| Security/privacy | Security Compliance Checklist plus scoped `gitleaks dir --redact` scans | PASS | No secret or unsupported personal-data/compliance claim; no dependency or runtime change. |
| ASCII/LF/links | Changed-text `file`, CR scan, and relative Markdown target existence check | PASS | 19 changed text files are ASCII/LF and all relative targets resolve. |
| Linter | `./scripts/validate-changes.sh --json` | PASS | Backend, engine, and frontend lint pass. |
| Formatter | `./scripts/validate-changes.sh --json`; `git diff --check "$BASE"` | PASS | Backend format and repository whitespace checks pass; no app source changed. |
| Type checker | `./scripts/validate-changes.sh --json` | PASS | Backend mypy, engine mypy, and frontend TypeScript pass. |
| Final diff re-read | `git diff "$BASE"` plus untracked-file inventory and original-resolution binary inspection | PASS | All findings resolved; no debug/capture hook or unrelated source change remains. |

The first focused pytest attempt used a stale long-running PostgreSQL volume
whose stored password no longer matched `.env`; collection failed in the
autouse database fixture. The exact tests were rerun against a fresh migrated
PostgreSQL 18 container and passed 20/20, so no test failure remains.

## Summary

1. Reviewed all 25 files changed since base commit `a47a618`, plus this report.
2. Resolved 0 critical, 0 high, 3 medium, and 2 low findings.
3. Made no deliberate unfixed exception and changed no application runtime.
4. The focused contracts, deterministic browser journey, 9-step repository
   gate, visual/privacy review, secret scans, ASCII/LF/link checks, lint,
   format, and type checks all pass.

## Next Command

`validate`
