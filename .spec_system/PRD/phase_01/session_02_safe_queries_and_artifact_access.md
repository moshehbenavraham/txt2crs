# Session 02: Safe Queries and Artifact Access

**Session ID**: `phase01-session02-safe-queries-and-artifact-access`
**Package**: backend/packages/txt2crs
**Status**: Not Started
**Estimated Tasks**: ~16-22
**Estimated Duration**: 2-4 hours

---

## Objective

Expose bounded owner-safe job and artifact query contracts without revealing
private engine state, checkpoint payloads, or filesystem paths.

---

## Scope

### In Scope (MVP)

- An allowlisted public job projection from the job and latest checkpoint.
- Bounded progress, safe failure, source summary, conflict, and artifact
  availability fields.
- Owner-scoped artifact manifest reads that do not load artifact bodies.
- Stable artifact identifiers and allowlisted artifact metadata.
- Context-managed single-artifact streaming from one validated descriptor.
- Confinement, symlink, byte-limit, content hash, and metadata verification.
- Indistinguishable missing and wrong-owner behavior.

### Out of Scope

- HTTP response headers, range requests, or FastAPI streaming responses.
- Browser preview behavior and frontend result cards.
- Request submission and provider runtime composition.

---

## Prerequisites

- [ ] Session 01 request persistence and recovery contracts are validated.
- [ ] Existing artifact-store integrity and bundle-read tests remain green.

---

## Deliverables

1. Public job snapshot and safe source/artifact availability models.
2. Manifest metadata and stable artifact identifier contracts.
3. Owner-scoped context-managed artifact stream implementation.
4. Privacy, ownership, symlink, mutation, corruption, and size-limit tests.

---

## Success Criteria

- [ ] Public snapshots cannot serialize source text, evidence excerpts,
  prompts, provider identifiers, token data, paths, or checkpoint JSON.
- [ ] Manifest reads return metadata without loading complete artifact bodies.
- [ ] Artifact reads validate and hash one confined descriptor before yielding
  bounded chunks from that same descriptor.
- [ ] Missing and wrong-owner requests produce the same safe package error.
- [ ] Existing full-bundle restore behavior remains compatible and tested.
