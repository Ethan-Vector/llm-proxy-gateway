from __future__ import annotations

import argparse
import time
from typing import Any, Dict

import httpx

def _post(client: httpx.Client, url: str, api_key: str, payload: Dict[str, Any]) -> httpx.Response:
    return client.post(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=30.0,
    )

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:8080")
    p.add_argument("--api-key", default="dev-key")
    args = p.parse_args()

    base = args.base_url.rstrip("/")
    with httpx.Client() as client:
        t0 = time.perf_counter()
        r = _post(
            client,
            base + "/v1/chat/completions",
            args.api_key,
            {"model": "mock:demo", "messages": [{"role": "user", "content": "Say hello"}], "temperature": 0.0},
        )
        dt = (time.perf_counter() - t0) * 1000.0
        r.raise_for_status()
        j = r.json()
        assert "choices" in j and j["choices"], "missing choices"
        assert "message" in j["choices"][0], "missing message"
        print(f"chat_completions ok in {dt:.2f}ms")

        t1 = time.perf_counter()
        r2 = _post(
            client,
            base + "/v1/embeddings",
            args.api_key,
            {"model": "mock:embed", "input": ["a", "b"]},
        )
        dt2 = (time.perf_counter() - t1) * 1000.0
        r2.raise_for_status()
        j2 = r2.json()
        assert "data" in j2 and len(j2["data"]) == 2
        print(f"embeddings ok in {dt2:.2f}ms")

if __name__ == "__main__":
    main()
