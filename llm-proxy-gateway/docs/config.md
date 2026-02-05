# Configuration

Main file: `configs/config.yaml`

Key areas:

- `server`: host/port, request body size limit
- `auth`: enable + API keys
- `rate_limit`: token bucket per key
- `routing`:
  - `default_provider`
  - `allowed_models` (recommended)
  - `providers`: provider definitions (kind + base_url + key env)
- `cache`: TTL response cache
- `policies`: prompt size limits, etc.

See `configs/config.example.yaml` for a complete annotated sample.
