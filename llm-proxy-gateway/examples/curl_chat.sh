#!/usr/bin/env bash
set -euo pipefail

curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-key" \
  -d '{
    "model":"mock:demo",
    "messages":[{"role":"user","content":"Give me 3 bullet points about caching in LLM gateways."}],
    "temperature":0.2
  }' | jq .
