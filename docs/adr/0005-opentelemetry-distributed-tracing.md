# 5. OpenTelemetry Distributed Tracing

**Status:** Accepted
**Date:** 2026-01-27

## Context

While ADR-0003 established structured JSON logging with trace ID correlation, it only provides visibility within the backend service. In production environments with multiple services, databases, and external APIs, understanding request flow requires distributed tracing.

Current observability gaps:
1. **No span-level timing** - Logs show request duration but not breakdown by operation
2. **No service topology** - Cannot visualize how requests flow between services
3. **Limited database visibility** - SQL queries are not traced
4. **No outbound HTTP tracing** - External API calls are not correlated to requests
5. **Vendor lock-in** - Sentry provides error tracking but not full APM capabilities

OpenTelemetry is the CNCF standard for observability with:
- Vendor-neutral instrumentation
- Auto-instrumentation for common frameworks
- Support for traces, metrics, and logs
- Wide ecosystem of backends (Jaeger, Tempo, Datadog, etc.)

## Decision

Implement OpenTelemetry distributed tracing as an opt-in feature with:

### 1. Configuration (Environment Variables)

```bash
OTEL_ENABLED=true                    # Enable/disable tracing
OTLP_ENDPOINT=http://localhost:4317  # OTLP collector endpoint
OTEL_SERVICE_NAME=my-service         # Service name (defaults to PROJECT_NAME)
OTEL_TRACES_SAMPLER_ARG=1.0          # Sampling rate (1.0 = all, 0.1 = 10%)
```

### 2. Auto-Instrumentation

Automatically instrument:
- **FastAPI** - HTTP requests, middleware, exception handling
- **SQLAlchemy** - Database queries with timing and parameters
- **HTTPX** - Outbound HTTP calls to external APIs

### 3. Integration with Existing Trace ID

When OpenTelemetry is enabled:
- OTEL generates W3C Trace Context compliant trace IDs
- Middleware bridges OTEL trace IDs into `trace_id_var` for log correlation
- Incoming `X-Trace-ID` headers are respected for trace propagation

When disabled:
- Fallback to existing UUID-based trace IDs
- No additional overhead or dependencies loaded

### 4. Opt-In Design

OpenTelemetry is disabled by default (`OTEL_ENABLED=false`) because:
- Production environments may not have OTLP collectors
- Adds latency for span creation and export (~1-5ms per request)
- Dependencies increase container size (~15MB)

### Implementation

```python
# In main.py
from app.core.telemetry import setup_telemetry, instrument_app

setup_telemetry()  # Before app creation
app = FastAPI(...)
instrument_app(app)  # After app creation
```

Files:
- `backend/app/core/telemetry.py` - Tracer setup and instrumentation
- `backend/app/core/config.py` - OTEL configuration settings
- `backend/app/core/middleware.py` - Bridge to existing trace ID system

### Local Development with Jaeger

```yaml
# Add to docker-compose.override.yml
services:
  jaeger:
    image: jaegertracing/jaeger:2.19.0
    ports:
      - "16686:16686"  # Jaeger UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
    environment:
      - COLLECTOR_OTLP_GRPC_HOST_PORT=0.0.0.0:4317
      - COLLECTOR_OTLP_HTTP_HOST_PORT=0.0.0.0:4318
```

Access Jaeger UI at http://localhost:16686

## Consequences

### Enables

- **Distributed tracing** across all services using W3C Trace Context
- **Database query analysis** with timing and parameter visibility
- **External API monitoring** with outbound request correlation
- **Service topology visualization** in Jaeger/Tempo/Grafana
- **Span-level performance analysis** for optimization
- **Vendor-neutral observability** - switch backends without code changes
- **AI agent debugging** - agents can trace request flows to diagnose issues

### Trade-offs

- **Increased latency** - ~1-5ms per request for span processing
- **Additional dependencies** - 15MB+ for opentelemetry packages
- **Infrastructure requirement** - needs OTLP collector in production
- **Learning curve** - team needs to understand distributed tracing concepts
- **Sampling decisions** - high-traffic services must balance coverage vs. cost

### Prevents

- Vendor lock-in to proprietary APM solutions
- Blind spots in service-to-service communication
- Undiagnosed database performance issues
- External API failures without context

## Alternatives Considered

### 1. Sentry Performance (Current)
- Already integrated for error tracking
- Limited distributed tracing support
- Proprietary, though has good SDK
- **Rejected**: Not a full APM solution, limited tracing

### 2. AWS X-Ray
- Good for AWS-native applications
- Tight integration with AWS services
- **Rejected**: Vendor lock-in, limited ecosystem

### 3. Datadog APM
- Comprehensive APM solution
- Good auto-instrumentation
- **Rejected**: Expensive, proprietary agent required

### 4. Custom Tracing
- Full control over implementation
- No external dependencies
- **Rejected**: Reinventing the wheel, no ecosystem benefits

## References

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [ADR-0003: Structured JSON Logging](./0003-structured-json-logging.md)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
- [OpenTelemetry Python](https://opentelemetry-python.readthedocs.io/)
