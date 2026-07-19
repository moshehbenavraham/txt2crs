# Session 03: Cached Readiness and Observability

**Session ID**: `phase02-session03-cached-readiness-and-observability`
**Package**: backend
**Status**: Complete
**Tasks**: 25
**Estimated Duration**: 2-4 hours

---

## Objective

Build a bounded, side-effect-free readiness cache and safe observability layer
that combines engine, worker, storage, authentication, research, input, and
admission state without leaking request or provider data.

---

## Scope

### In Scope (MVP)

- Safe readiness response and internal cache models.
- Startup and bounded maintenance refresh orchestration.
- Shared runtime ownership lock for readiness, authentication, and execution.
- Coarse checks for authentication, GPT-5.6, research, storage, worker,
  enabled inputs, and admission capacity.
- Sanitized request logging, structured events, and package exception
  translation helpers.

### Out of Scope

- HTTP system routes.
- Browser device-code ceremony.
- Learner job routes or artifact delivery.
- Hosted telemetry or retention automation.

---

## Prerequisites

- [x] Session 01 exposes one application-owned facade.
- [x] Session 02 exposes a bounded safe worker snapshot.

---

## Deliverables

1. Tests proving browser reads cause no provider, MCP, or destructive storage
   work.
2. Cached readiness coordinator with explicit freshness and safe warnings.
3. Runtime ownership lock and refresh scheduling.
4. Sanitized request middleware and structured log helpers.
5. Safe engine-to-shell exception translation using project error codes.

---

## Success Criteria

- [x] Readiness is `accepting_jobs=true` only when every required check and
  admission condition passes.
- [x] Unconfigured systems report safe recovery actions without credentials,
  paths, provider payloads, or exception context.
- [x] Browser reads return the last snapshot and never start a provider
  resource or storage probe.
- [x] A running job prevents competing readiness or login ownership.
- [x] Logs omit raw paths, query strings, client IPs, learner data, and
  provider internals.
- [x] Focused backend tests and static checks pass.
