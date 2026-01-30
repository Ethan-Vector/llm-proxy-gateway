#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=./src
export CONFIG_PATH="${CONFIG_PATH:-configs/gateway.yaml}"

uvicorn llm_proxy_gateway.main:app --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8080}" --reload
