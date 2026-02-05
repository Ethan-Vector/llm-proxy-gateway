# llm-proxy-gateway

A small, production-minded **LLM proxy gateway** that exposes an **OpenAI-compatible API** and routes requests to one of multiple upstream providers (or a local/mock provider).

This repo is designed to be:
- **boring to operate**: explicit config, sane defaults, clear logs
- **safe-by-default**: API key auth, rate limiting, request size limits, optional allowlists
- **testable**: unit tests + smoke tests + a tiny eval harness
- **vendor-neutral**: providers are pluggable; routing is config-driven

> Works out of the box using the built-in **MockProvider** (no keys required).

---

## What you get

- OpenAI-compatible endpoints:
  - `POST /v1/chat/completions`
  - `POST /v1/completions`
  - `POST /v1/embeddings` (minimal)
- Routing:
  - by **model prefix** (e.g., `openai:gpt-4.1`, `anthropic:claude-3-5`, `mock:demo`)
  - or by **default provider**
- Guardrails:
  - API key auth (header `Authorization: Bearer <key>`)
  - rate limiting (token bucket, per API key)
  - request body size limit
  - allowlist for models
  - optional response caching (TTL)
- Observability:
  - structured JSON logs
  - request id
  - `GET /healthz`
- Tooling:
  - Dockerfile + compose
  - GitHub Actions CI (ruff + pytest)
  - `examples/` curl commands

---

## Quickstart (MockProvider)

### 1) Create venv and install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) Configure
Copy the sample config:
```bash
cp configs/config.example.yaml configs/config.yaml
cp .env.example .env
```

### 3) Run
```bash
llm-proxy --config configs/config.yaml
```

### 4) Call it
```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-key" \
  -d '{
    "model": "mock:demo",
    "messages": [{"role":"user","content":"Write 3 bullet points about SRE for LLM apps."}],
    "temperature": 0.2
  }' | jq .
```

---

## Config overview

See:
- `configs/config.example.yaml`
- `docs/config.md`

---

## Development

### Run tests
```bash
pytest -q
```

### Lint
```bash
ruff check .
ruff format .
```

---

## Security notes

- The gateway is not a full WAF. It is a **policy-aware proxy** with basic controls.
- See `docs/security.md` for recommended deployment patterns.

---

## License

MIT (see `LICENSE`).
