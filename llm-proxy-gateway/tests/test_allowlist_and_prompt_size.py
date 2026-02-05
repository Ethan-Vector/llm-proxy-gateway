from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from llm_proxy_gateway.app import create_app
from llm_proxy_gateway.config import load_config

def _cfg(tmp: Path) -> Path:
    y = """auth:
  enabled: true
  api_keys: ["k1"]
rate_limit:
  enabled: false
routing:
  default_provider: mock
  allowed_models: ["mock:demo"]
  providers:
    mock:
      kind: mock
policies:
  enabled: true
  max_prompt_chars: 10
"""
    p = tmp / "c.yaml"
    p.write_text(y, encoding="utf-8")
    return p

def test_allowlist_blocks_other_models():
    with tempfile.TemporaryDirectory() as d:
        loaded = load_config(str(_cfg(Path(d))))
        app = create_app(loaded)
        c = TestClient(app)
        headers = {"Authorization":"Bearer k1"}
        r = c.post("/v1/chat/completions", headers=headers, json={"model":"mock:other","messages":[{"role":"user","content":"hi"}]})
        assert r.status_code == 400

def test_prompt_size_limit():
    with tempfile.TemporaryDirectory() as d:
        loaded = load_config(str(_cfg(Path(d))))
        app = create_app(loaded)
        c = TestClient(app)
        headers = {"Authorization":"Bearer k1"}
        r = c.post("/v1/chat/completions", headers=headers, json={"model":"mock:demo","messages":[{"role":"user","content":"12345678901"}]})
        assert r.status_code == 400
