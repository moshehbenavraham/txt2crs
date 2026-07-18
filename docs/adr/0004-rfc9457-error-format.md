# 4. RFC 9457 Error Format

**Status:** Accepted
**Date:** 2026-01-26

## Context

The backend previously used FastAPI's default `HTTPException` which produces inconsistent error responses:

```json
{"detail": "Not found"}
```

This creates problems for AI agents and clients:

1. **No semantic error codes** - clients must parse text to understand error types
2. **No standard format** - error structure varies by endpoint
3. **No trace correlation** - errors cannot be correlated with request logs
4. **Frontend guesswork** - clients must infer error handling from HTTP status alone

For AI-optimized codebases, errors must be machine-readable with semantic codes enabling programmatic error handling.

## Decision

Implement RFC 9457 Problem Details format for all API errors with semantic error codes.

### 1. Response Format

All errors return this structure with `Content-Type: application/problem+json`:

```json
{
  "type": "https://api.example.com/problems/USER_2001",
  "title": "User Not Found",
  "status": 404,
  "detail": "User with ID 'abc-123' not found",
  "code": "USER_2001",
  "trace_id": "trace-id-here",
  "errors": null
}
```

### 2. Semantic Error Codes

Error codes follow a numbered namespace pattern:

| Range | Domain | Examples |
|-------|--------|----------|
| 1xxx | Authentication | AUTH_1001 (invalid credentials), AUTH_1002 (token expired) |
| 2xxx | User | USER_2001 (not found), USER_2002 (already exists) |
| 3xxx | Item | ITEM_3001 (not found), ITEM_3002 (already exists) |
| 4xxx | Validation | VALIDATION_4001 (validation error), VALIDATION_4002 (invalid input) |
| 5xxx | Rate Limiting | RATE_5001 (rate limit exceeded) |
| 9xxx | Server | SERVER_9001 (internal error), SERVER_9002 (service unavailable) |

### 3. Exception Classes

Base `AppException` plus convenience classes:

- `AppException` - Generic exception with error code
- `AuthenticationError` - Auth failures (401)
- `AuthorizationError` - Permission failures (403)
- `NotFoundError` - Resource not found (404)
- `ConflictError` - Duplicate/conflict (409)
- `ValidationError` - Input validation (422)
- `RateLimitError` - Rate limiting (429)
- `InternalError` - Server errors (500)

### 4. Error Status Mapping

Each error code maps to a specific HTTP status code via `ERROR_STATUS_MAP` in constants.py.

### Implementation

```python
# Usage
from app.core.exceptions import AppException, NotFoundError
from app.core.constants import ErrorCode

# Generic exception
raise AppException(
    code=ErrorCode.USER_NOT_FOUND,
    detail="User with this email does not exist"
)

# Convenience exception
raise NotFoundError(resource="User", identifier="abc-123")
```

Files:
- `backend/app/core/constants.py` - Error codes, status mapping, messages
- `backend/app/core/exceptions.py` - Exception classes and ProblemDetail model
- `backend/app/core/exception_handlers.py` - FastAPI exception handlers

## Consequences

### Enables

- **Programmatic error handling** - clients switch on `code` field
- **AI agent self-correction** - agents understand errors semantically
- **Consistent frontend handling** - single error parsing logic
- **Error correlation** - trace_id links errors to request logs
- **Validation details** - structured field-level error messages
- **Documentation** - error codes are self-documenting

### Trade-offs

- Requires defining error codes for each error scenario
- Slightly larger response payload (~100-200 bytes)
- Developers must use AppException instead of HTTPException

### Prevents

- Ad-hoc error formats that break client parsing
- Text-based error detection (`if "not found" in error`)
- Uncorrelated errors in distributed tracing
- Inconsistent HTTP status code selection

## References

- [RFC 9457 - Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)
- [IETF Problem Details](https://datatracker.ietf.org/doc/html/rfc9457)
