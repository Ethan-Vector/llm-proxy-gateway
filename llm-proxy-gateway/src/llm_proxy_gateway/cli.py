from __future__ import annotations

import argparse

import uvicorn

from .app import create_app
from .config import load_config

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-proxy", description="Run llm-proxy-gateway")
    p.add_argument("--config", required=True, help="Path to YAML config")
    p.add_argument("--host", default=None, help="Override host")
    p.add_argument("--port", type=int, default=None, help="Override port")
    return p

def main() -> None:
    args = build_parser().parse_args()
    loaded = load_config(args.config)
    cfg = loaded.cfg

    host = args.host or cfg.server.host
    port = args.port or cfg.server.port

    app = create_app(loaded)
    uvicorn.run(app, host=host, port=port, log_level=cfg.server.log_level.lower())
