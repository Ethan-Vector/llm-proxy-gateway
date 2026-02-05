from __future__ import annotations

import hashlib
import time
from typing import Any, Dict

from .base import BaseProvider

def _stable_hash(text: str) -> int:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(h[:8], 16)

class MockProvider(BaseProvider):
    name = "mock"

    async def chat_completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model = payload.get("model", "mock:demo")
        messages = payload.get("messages", [])
        prompt = " ".join([m.get("content","") for m in messages if isinstance(m.get("content"), str)])
        seed = _stable_hash(prompt + model)
        content = f"[mock] model={model} seed={seed} :: {self._respond(prompt)}"
        now = int(time.time())
        return {
            "id": f"chatcmpl-mock-{seed}",
            "object": "chat.completion",
            "created": now,
            "model": model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": max(1, len(prompt)//4), "completion_tokens": max(1, len(content)//4), "total_tokens": max(2, (len(prompt)+len(content))//4)},
        }

    async def completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model = payload.get("model", "mock:demo")
        prompt = payload.get("prompt", "")
        seed = _stable_hash(str(prompt) + model)
        text = f"[mock] model={model} seed={seed} :: {self._respond(str(prompt))}"
        now = int(time.time())
        return {
            "id": f"cmpl-mock-{seed}",
            "object": "text_completion",
            "created": now,
            "model": model,
            "choices": [{"index": 0, "text": text, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": max(1, len(str(prompt))//4), "completion_tokens": max(1, len(text)//4), "total_tokens": max(2, (len(str(prompt))+len(text))//4)},
        }

    async def embeddings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        model = payload.get("model", "mock:embed")
        inp = payload.get("input", "")
        if isinstance(inp, list):
            texts = [str(x) for x in inp]
        else:
            texts = [str(inp)]
        data = []
        for i, t in enumerate(texts):
            seed = _stable_hash(t + model)
            # Tiny deterministic vector
            vec = [((seed >> (k % 24)) & 0xFF) / 255.0 for k in range(16)]
            data.append({"object": "embedding", "index": i, "embedding": vec})
        return {"object": "list", "model": model, "data": data, "usage": {"prompt_tokens": sum(max(1, len(t)//4) for t in texts), "total_tokens": sum(max(1, len(t)//4) for t in texts)}}

    def _respond(self, prompt: str) -> str:
        p = prompt.strip()
        if not p:
            return "Hello. Give me a prompt and I will respond deterministically."
        # Simple heuristics for demo
        if "bullet" in p.lower():
            return "- point 1\n- point 2\n- point 3"
        if len(p) > 200:
            return "I received a long prompt. Consider enabling caching and stricter size limits."
        return f"I received: {p[:120]}"
