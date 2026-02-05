from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from llm_proxy_gateway.app import create_app
from llm_proxy_gateway.config import load_config

def _write_cfg(tmp: Path, extra_yaml: str = "") -> Path:
    cfg = f"""server:
  host: 127.0.0.1
  port: 9999
auth:
  enabled: true
  api_keys: ["k1"]
rate_limit:
  enabled: true
  per_key:
    refill_per_sec: 0.0
    capacity: 2
routing:
  default_provider: mock
  allowed_models: ["mock:demo", "mock:embed"]
  providers:
    mock:
      kind: mock
cache:
  enabled: false
policies:
  enabled: true
  max_prompt_chars: 10000
{extra_yaml}
"""
    p = tmp / "config.yaml"
    p.write_text(cfg, encoding="utf-8")
    return p

def test_auth_required():
    with tempfile.TemporaryDirectory() as d:
        cfg_path = _write_cfg(Path(d))
        loaded = load_config(str(cfg_path))
        app = create_app(loaded)
        c = TestClient(app)
        r = c.post("/v1/chat/completions", json={"model":"mock:demo","messages":[{"role":"user","content":"hi"}]})
        assert r.status_code == 401

def test_rate_limit_enforced():
    with tempfile.TemporaryDirectory() as d:
        cfg_path = _write_cfg(Path(d))
        loaded = load_config(str(cfg_path))
        app = create_app(loaded)
        c = TestClient(app)
        headers = {"Authorization":"Bearer k1"}
        # capacity 2, refill 0 => third request must fail
        for _ in range(2):
            r = c.post("/v1/chat/completions", headers=headers, json={"model":"mock:demo","messages":[{"role":"user","content":"hi"}]})
            assert r.status_code == 200
        r3 = c.post("/v1/chat/completions", headers=headers, json={"model":"mock:demo","messages":[{"role":"user","content":"hi"}]})
        assert r3.status_code == 429
