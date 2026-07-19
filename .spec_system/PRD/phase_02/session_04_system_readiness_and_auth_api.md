# Session 04: System Readiness and Auth API

**Session ID**: `phase02-session04-system-readiness-and-auth-api`
**Package**: backend
**Status**: Not Started
**Estimated Tasks**: ~12-25
**Estimated Duration**: 2-4 hours

---

## Objective

Expose strict authenticated system readiness and superuser-only device
authentication endpoints backed by the application lifecycle, cache, and
public engine contracts.

---

## Scope

### In Scope (MVP)

- Strict public readiness and device-auth response schemas.
- Authenticated `GET /api/v1/system/readiness`.
- Superuser-only `POST /api/v1/system/auth/start`.
- Superuser-only `GET /api/v1/system/auth/status`.
- Rate limits, authorization behavior, safe error translation, and OpenAPI
  client regeneration.

### Out of Scope

- Learner job and artifact endpoints.
- Account creation or external identity-provider changes.
- Frontend setup route.
- Direct credential, token, or provider-detail responses.

---

## Prerequisites

- [x] Session 03 provides cached readiness and safe error translation.
- [x] Session 01 exposes the package-owned authenticator lifecycle.

---

## Deliverables

1. Route and authorization tests written before handlers.
2. Strict system readiness and browser-safe device-auth schemas.
3. System API routes using application-owned services.
4. Regenerated and formatted OpenAPI document and frontend client.
5. API documentation for operator recovery and response safety.

---

## Success Criteria

- [ ] Authenticated users can read only the coarse readiness projection.
- [ ] Non-superusers cannot start or inspect the device ceremony.
- [ ] Device state exposes only bounded user-code, the validated OpenAI
  verification URL, and safe status/recovery fields. The pinned SDK exposes no
  expiry, so the API does not fabricate one.
- [ ] Concurrent job ownership returns cached state or a safe busy response
  without starting another runtime.
- [ ] Failures use `AppException`, registered `ErrorCode` values, RFC 9457,
  and trace IDs.
- [ ] Backend tests, OpenAPI generation, type checks, and lint pass.
