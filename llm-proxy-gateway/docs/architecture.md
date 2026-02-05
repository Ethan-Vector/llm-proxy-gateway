# Architecture

## Data plane
Client -> FastAPI gateway -> Provider -> Upstream model

### Responsibilities
- Validate request schema (minimal OpenAI compatibility)
- Enforce policy:
  - auth
  - rate limit
  - body size
  - model allowlist
  - prompt size
- Route:
  - `model` prefix selects provider (`openai:*`, `mock:*`, ...)
- Observability:
  - request id
  - structured logs
- Optional:
  - response cache (TTL)

## Control plane (future)
If you want a more serious gateway:
- dynamic config reload
- per-tenant routing + quotas
- circuit breaking and retries
- metrics export (Prometheus)
