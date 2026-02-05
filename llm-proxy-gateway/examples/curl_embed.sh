#!/usr/bin/env bash
set -euo pipefail

curl -s http://localhost:8080/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dev-key" \
  -d '{
    "model":"mock:embed",
    "input":["hello","world"]
  }' | jq .
