# Security Policy

This project is a template. Before production use, review:

- TLS termination (must be enabled)
- API key storage (use secrets manager)
- Logging (avoid leaking secrets / PII)
- Rate limiting defaults (set realistically)
- Allowlist models (recommended)
- Deploy behind a reverse proxy / WAF if exposed to the internet

Report security issues privately (do not open public issues with exploit details).
