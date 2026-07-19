# Phase Transition Infrastructure Report

**Date:** 2026-07-19
**Result:** PASS
**Selected bundle:** Backup
**Platform:** Repository-root Docker Compose
**Scope:** Local-only PostgreSQL and private txt2crs engine state

## Scope Decision

Repository-root Docker Compose remains the complete deployment scope under
ADR-0008. The Phase 00 Health bundle is already configured and was revalidated
through the Phase 01 audit and pipeline gates. The next incomplete
infrastructure requirement was recoverability: the inherited
`scripts/backup-db.sh` captured only PostgreSQL and omitted the engine's
durable SQLite jobs, rendered artifacts, and Codex credential store.

No hosted backup provider was selected. Local encrypted-copy location,
off-host replication, and backup cadence remain operator responsibilities
because the project has no hosted environment or remote storage boundary.

## Implemented Backup Contract

1. `scripts/backup-local-state.sh` briefly quiesces the backend writer and
   creates one timestamped bundle.
2. PostgreSQL is stored as a validated custom-format dump.
3. The concrete Compose-prefixed volume mounted at `/var/lib/txt2crs` is
   discovered from the backend container and archived in full.
4. `scripts/local_state_archive.py` accepts only directories and regular
   files; symbolic links, traversal paths, duplicate paths, and special files
   fail before restore can clear current state.
5. `SHA256SUMS` covers both stores and the manifest. Bundle directories use
   mode `0700`; files use mode `0600`.
6. `scripts/restore-local-state.sh` requires
   `TXT2CRS_RESTORE_CONFIRM=replace-local-state`, validates checksums and both
   archive formats before destructive work, replaces both stores, and returns
   a previously running backend to health.
7. The default `backups/` directory is excluded from Git because bundles can
   contain learner data, generated content, and Codex credentials.

## Tests-First Record

Six contract tests were added before implementation. The initial focused run
failed all six because the scripts, helper, and Git exclusion did not exist.
After implementation, the suite passed.

The first live backup then exposed a host-ownership defect: the root
maintenance container produced a correctly private `0600` archive that the
invoking host user could not checksum. A failing ownership regression was
added before the fix. The script now transfers archive ownership back to the
invoking host UID/GID while retaining mode `0600`.

## Evidence Ledger

| Bundle | Component | Validation target / command | Result | Fixes applied |
|--------|-----------|-----------------------------|--------|---------------|
| Backup | Safe archive helper | `uv run pytest --confcutdir=tests/scripts tests/scripts/test_local_backup_contract.py -q` | PASS: 6 | Added regular-file-only archive and validate-before-clear restore |
| Backup | Shell syntax and repository baseline | `bash -n scripts/backup-local-state.sh scripts/restore-local-state.sh`; `./scripts/validate-changes.sh backend` | PASS | Added both scripts and baseline coverage |
| Backup | Complete backup | Isolated `txt2crs-infra-backup` Compose project with PostgreSQL and engine-volume markers | PASS | Host UID/GID handoff fixed after first live attempt |
| Restore | Destructive replacement | Mutated both stores, added a stale engine file, restored the bundle | PASS: database and volume returned to original markers; stale file removed |
| Integrity | Bundle hashes and permissions | `sha256sum --check SHA256SUMS`; `stat`; `find -perm` | PASS: all 3 hashes; directory `0700`; all 4 files `0600` |
| Health | Restored backend | Internal `/api/v1/utils/health/` after restore | PASS: healthy with PostgreSQL ready |
| Quality | Repository hooks | `uv run --directory backend pre-commit run --all-files` | PASS: all hooks |
| Cleanup | Isolated resources | Project-labelled container/volume checks after `docker compose down --volumes` | PASS: no proof containers, volumes, temporary bundles, or network remained |

## Operator Recovery Model

The recovery point is the most recent manually retained complete bundle.
Restore is a full local replacement, not a selective row or artifact recovery.
Checksums detect accidental corruption but do not authenticate a bundle;
operators must keep bundles in encrypted, access-controlled storage and review
their source before restore.

`scripts/backup-db.sh` remains available only as a legacy PostgreSQL-only
utility. It is explicitly documented as insufficient for application recovery.

## Remaining Infrastructure Work

None is skipped for the approved local-only deployment target. Automated
off-host replication, hosted disaster recovery, WAF, domains, TLS, managed
secrets, and remote rollout are not silently deferred requirements; they
require an explicit future hosting decision and new ADR.

## Handoff

`infra -> carryforward` is the required Phase Transition handoff. `documents`
follows `carryforward`; the next implementation session is not planned until
`phasebuild` creates the next phase.

**Next command:** `carryforward`
