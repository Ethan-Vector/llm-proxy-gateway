# Evals

This is a tiny harness to keep the gateway honest.

- It runs a few requests against a local gateway instance.
- It checks basic invariants (status codes, schema keys).
- It measures latency roughly.

Run:
```bash
python -m llm_proxy_gateway.evals.harness --base-url http://localhost:8080 --api-key dev-key
```
