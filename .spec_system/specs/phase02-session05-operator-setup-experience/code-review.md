# Code Review and Repair Report

**Session ID**: `phase02-session05-operator-setup-experience`
**Package**: frontend
**Reviewed**: 2026-07-19
**Base Commit**: `3b1986b7a9aa977d9649371625354171c1866590`
**Implementation Commit**: `fdeb074`
**Scope**: Complete base-to-implementation diff plus review repairs
**Result**: RESOLVED

## Review Surface

The exact base-to-head surface was reviewed across:

- `/setup` route authorization, metadata, Suspense, and recovery.
- Current-user query reuse and the superuser-only sidebar entry.
- Parallel readiness/authentication queries and conditional polling.
- Device start mutation, query-cache updates, terminal transitions, and
  readiness invalidation.
- Finite status presentation, safe messages, warnings/actions, and CLI
  recovery.
- Heading/landmark structure, live announcements, keyboard access, external
  links, reduced motion, responsive layout, and long bounded values.
- Generated route ownership, protected API/UI files, dependencies, and build
  output.
- Focused unit/browser tests, complete frontend tests, rendered screenshots,
  and Apex artifacts.

The review emphasized authorization before system reads, bounded traffic,
terminal polling, StrictMode behavior, challenge cleanup, backend-message
legibility, 320px behavior, duplicate API list values, secret isolation, and
generated/protected file ownership.

**Inventory commands**: `git status`, `git log --oneline "$BASE"..HEAD`,
`git diff "$BASE"`, `git ls-files --others --exclude-standard`, production
added-line sink scan, dependency/schema inventory, and rendered browser
inspection.

## Findings by Severity

### Critical

No findings.

### High

No findings.

### Medium

- `frontend/src/components/SystemSetup/SystemSetupWorkspace.tsx` - Mounting
  with an already-authenticated cache invalidated the readiness query that had
  just resolved in parallel. React StrictMode ran the effect twice, producing
  three readiness requests for one page load. | Fix: Track the previous auth
  state and invalidate only on a real non-authenticated to authenticated
  transition. Initial authenticated load now performs exactly one readiness
  request, while a completed device ceremony still refreshes readiness. |
  Status: FIXED
- `frontend/src/components/SystemSetup/AuthenticationPanel.tsx` - The shared
  Alert title's one-line clamp truncated the API's safe authentication message
  without a focus, tooltip, or expansion path. | Fix: Override the clamp at
  the feature boundary and allow safe text to wrap/break. A rendered
  regression checks the computed line-clamp state. | Status: FIXED
- `frontend/src/components/SystemSetup/AuthenticationPanel.tsx` - The API
  permits a 64-character validated user code, but the mono challenge line had
  no break opportunity and overflowed its own surface by 806 pixels at 320px.
  | Fix: Allow character-level wrapping for the bounded code. A 320px browser
  case verifies both element and document overflow remain zero. | Status:
  FIXED

### Low

- `frontend/src/components/SystemSetup/SystemSetupWorkspace.tsx` - Copy
  feedback remained in the live region after polling reached authenticated,
  causing the terminal announcement to include stale `Code copied` guidance.
  | Fix: Clear challenge-specific copy feedback whenever auth leaves waiting
  state. The ceremony regression now verifies the terminal announcement. |
  Status: FIXED
- `ReadinessOverview.tsx` and `RecoveryPanel.tsx` - The public schemas bound
  input modes, warnings, and actions but do not require unique values. Using
  value-only React keys could therefore emit duplicate-key console errors. |
  Fix: Include stable list position in keys. A repeated-value browser case
  verifies no duplicate-key error. | Status: FIXED

## Assumptions and Deliberate Non-Fixes

- Backend schemas remain the authority for the OpenAI HTTPS challenge URL,
  bounded code, safe message, and coarse readiness text.
- The UI does not add challenge expiry because the generated API exposes no
  expiry field.
- Authentication logout/account switching and learner course screens remain
  later-session scope.
- Polling remains one second because the session/API contract specifies that
  finite cadence; background polling remains disabled.
- Recovery warnings/actions intentionally preserve API order and repeated
  values instead of silently changing server meaning.
- The exact GPT-5.6/Tavily live proof remains release-gated by real
  credentials.

## Behavior Changes

- A current superuser can open `/setup`; a normal user redirects before any
  system endpoint mounts.
- Readiness and auth status start together; already-authenticated page mounts
  do not perform a redundant readiness refresh.
- Starting auth writes the safe response to the existing query cache.
- Waiting auth polls once per second, stops at terminal state, removes the
  challenge, clears temporary copy feedback, and refreshes readiness once.
- Bounded long codes and repeated safe API values render at 320px without
  overflow or React key warnings.
- Authentication messages remain fully readable rather than one-line
  truncated.

## Security And Compliance Review

| Area | Result | Evidence |
|------|--------|----------|
| Authentication/authorization | PASS | Route guard reuses the current-user cache and redirects non-superusers before the feature component or system queries mount |
| Input/output validation | PASS | Auth/readiness values come from generated finite contracts; production renders an explicit reviewed allowlist |
| Injection | PASS | React text escaping is preserved; no HTML injection, eval, dynamic execution, shell, SQL, or browser URL-fetch surface was added |
| Secrets | PASS | No token, credential, account identity, raw provider payload, exception, or local path is rendered, persisted, or logged |
| External navigation | PASS | Only the backend-validated challenge URL is used; the link opens with `target="_blank"` and `rel="noreferrer"` |
| Resource safety | PASS | Waiting-only foreground polling, terminal stop, unmount cleanup, cache reuse, and transition-only readiness invalidation are tested |
| Error handling | PASS | Query errors stay in a recoverable route boundary; mutation errors use the centrally translated safe RFC 9457 detail |
| Dependencies | PASS | No package manifest, lock, primitive, or generated API client has a final diff |
| Database | N/A | No schema, query, migration, or persisted engine shape changed |
| GDPR | PASS | No new personal-data field or durable browser storage was introduced; the short-lived challenge stays in superuser memory/cache only |

## Evidence Ledger

| Check | Command or Inspection | Result | Evidence |
|-------|-----------------------|--------|----------|
| Tests-first review regressions | Focused setup Playwright cases | PASS | Initial-auth request count, full safe message, terminal announcement, 64-character code, 320px layout, and duplicate keys protected |
| Focused unit tests | `npm run test:unit` | PASS | 33 passed |
| Focused setup browser suite | Playwright `tests/setup.spec.ts` | PASS | 7 passed including auth setup |
| Frontend static/build | Biome, TypeScript, Vite | PASS | 138 files; no type error; 2,204 modules built |
| Added-line security scan | Production setup diff and external-link inspection | PASS | No sensitive sink/secret marker; safe link attributes present |
| Dependency/schema inventory | Base-to-head manifest, lock, UI primitive, client, model, and migration inspection | PASS | No dependency, database, client, or primitive change |
| Patch integrity | `git diff --check "$BASE"` | PASS | No whitespace defect |

## Summary

1. Reviewed the complete base-to-implementation frontend surface.
2. Found 0 critical, 0 high, 3 medium, and 2 low issues.
3. Repaired all five findings with browser regressions.
4. Focused tests, lint, typecheck, build, security scans, and patch checks
   pass.
5. No unresolved code, security, privacy, accessibility, or workflow finding
   remains.

Next command: `validate`
