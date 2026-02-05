# Operating Instructions

This repo is meant to be copied into your GitHub and used as a starting point.

## Minimum production checklist

1. Put the gateway behind TLS (reverse proxy or load balancer).
2. Issue per-client API keys and rotate them.
3. Turn on:
   - strict model allowlist
   - request size limit
   - rate limits per key
4. Log to a centralized sink.
5. Add provider-specific retries and circuit breaking if your upstreams are flaky.
6. Add an audit trail for prompts/responses if compliance requires it (mind PII).

## Common extension points

- Add a provider: `src/llm_proxy_gateway/providers/`
- Add a policy: `src/llm_proxy_gateway/policies/`
- Add richer OpenAI schema support: `src/llm_proxy_gateway/schemas/openai.py`

## Troubleshooting

- 401: missing/invalid `Authorization: Bearer <key>`
- 429: rate limit exceeded for that key
- 400: body too large, invalid schema, or disallowed model
- 500: provider error (check upstream config)
