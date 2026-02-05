# Security

This gateway provides *basic* controls. Recommended deployment posture:

1. Deploy behind TLS termination (LB / reverse proxy).
2. Do not expose upstream keys to clients.
3. Enforce model allowlists.
4. Set request size limits.
5. Configure rate limits based on abuse model.
6. Log safely:
   - avoid secrets
   - consider hashing prompts if you don't need plaintext
7. Add network egress controls if you run in a regulated environment.

## Threat model (minimal)
- API key leakage -> rotate keys, short TTL, per-tenant keys
- Prompt injection -> cannot fully prevent; restrict tools/egress for agents
- Abuse / DoS -> rate limits + WAF + autoscaling + queueing for heavy workloads
