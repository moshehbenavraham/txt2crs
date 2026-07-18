# 3. Structured JSON Logging

**Status:** Accepted
**Date:** 2026-01-26

## Context

The backend previously used Python's basic logging with unstructured text output. This created several problems:

1. **AI agents cannot parse logs programmatically** - text logs require regex parsing prone to errors
2. **No request correlation** - impossible to trace requests across async operations
3. **Inconsistent format** - logs varied in structure, making filtering difficult
4. **Poor integration** - text logs don't integrate well with log aggregation platforms (ELK, Datadog)

For AI-optimized codebases, logs must be machine-readable while maintaining human readability during development.

## Decision

Implement structured JSON logging with the following features:

### 1. JSON Output Format (Production)

Single-line JSON objects with standardized fields:
- `timestamp`: ISO 8601 format with UTC timezone
- `level`: Log level (INFO, WARNING, ERROR, etc.)
- `logger`: Logger name (module path)
- `message`: Event name following naming convention
- `trace_id`: Request correlation ID
- `location`: File, line, function for debugging
- `extra`: Additional context fields

### 2. Human-Readable Format (Development)

Local development uses a text format:
```
TIMESTAMP | LEVEL | [TRACE_ID] | LOGGER | MESSAGE | EXTRA
```

### 3. Event Naming Convention

All log events follow the pattern: `{domain}.{action}_{state}`

- **Domains**: user, item, auth, database, request, health, external, agent
- **States**: _started, _completed, _failed, _validated, _rejected, _retrying

Examples:
- `user.registration_completed`
- `auth.login_failed`
- `request.http_received`

### 4. Trace ID Correlation

Every request receives a unique trace ID, propagated via:
- Context variable (`trace_id_var`) for async operations
- `X-Trace-ID` response header for client correlation
- Included in all log entries for the request lifecycle

### Implementation

```python
# Usage
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.info("user.registration_completed", extra={"user_id": str(user.id)})
```

Files:
- `backend/app/core/logging.py` - Formatters and setup
- `backend/app/core/middleware.py` - Request middleware for trace ID

## Consequences

### Enables

- AI agents can parse and analyze logs programmatically
- Request tracing across async operations and distributed systems
- Easy integration with ELK, Datadog, and other log platforms
- Consistent log format across all services
- Faster debugging with trace ID correlation
- Structured queries on log attributes

### Trade-offs

- Slightly increased log volume due to JSON overhead (~20-30%)
- Requires JSON-aware log viewer for production logs
- Event naming convention requires developer discipline

### Prevents

- Ad-hoc log formats that break parsing
- Uncorrelated request logs in async contexts
- Inconsistent logging patterns across modules
