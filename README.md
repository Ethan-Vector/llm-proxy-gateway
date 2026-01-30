# ethan-llm-proxy-gateway

Un LLM gateway “da produzione”: tratta le chiamate al modello come dipendenze volatili.
Include:
- Routing per route/tenant (modello primario + fallback)
- Budget (max tokens / costo stimato) e rate limiting (semplice, per chiavi)
- Redaction PII per audit/logging
- Audit event envelope (tracciabilità, versioning config, provider, outcome)
- Provider-agnostico (OpenAI, Anthropic, Local stub)

## Quickstart

### 1) Setup
```bash
cp .env.example .env
cp configs/gateway.example.yaml configs/gateway.yaml
```

Edita `.env` con le API key (se usi provider cloud).

### 2) Run (dev)
```bash
make dev
# oppure
./scripts/run_dev.sh
```

Server: http://localhost:8080

### 3) Chiamata esempio
Endpoint gateway (stile OpenAI-ish semplificato):
- `POST /v1/chat/completions`

Esempio:
```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -H 'x-tenant-id: acme' \
  -H 'x-route: support_copilot' \
  -d '{
    "messages":[
      {"role":"system","content":"You are a helpful assistant."},
      {"role":"user","content":"Reset password per l’utente mario.rossi@example.com"}
    ],
    "temperature":0.2
  }' | jq
```

## Config: routing e fallback

File: `configs/gateway.yaml`

- `routes.<route_name>.providers`: lista ordinata; il primo è primario, gli altri sono fallback.
- `budgets`: limiti per route/tenant (max_tokens e max_cost_usd stimato).
- `redaction`: regole PII da applicare SOLO a log/audit (non al prompt inviato al provider, salvo tu lo voglia).

## Audit events

Ogni richiesta produce un evento JSON (stdout di default), con:
- request_id, tenant_id, route
- provider scelto, fallback usato o meno
- latenza end-to-end
- prompt/response redatti (safe logging)
- config_version (hash del file YAML)

## Comandi utili
```bash
make test
make lint
make fmt
make docker-build
make docker-run
```

## Note operative (scelte deliberate)
- Redaction di default solo per audit/log, per non cambiare l’input al modello.
- Costo stimato: euristica, utile come “guardrail” ma non contabilità.
- Rate limit: semplice in-memory (OK per demo e single instance). In prod: Redis.

## License
MIT
