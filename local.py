from __future__ import annotations

import httpx

from .base import ProviderClient, ProviderResult
from ..errors import ProviderError


class LocalClient(ProviderClient):
    """
    Local stub provider:
    - assumes a simple endpoint POST {base_url}/chat that returns {"content": "...", "usage": {...}}
    """

    def __init__(self, provider_name: str, model: str, timeout_s: int, base_url: str):
        super().__init__(provider_name, model, timeout_s)
        self.base_url = base_url.rstrip("/")

    async def chat(self, messages: list[dict[str, str]], temperature: float, max_tokens: int) -> ProviderResult:
        url = f"{self.base_url}/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                r = await client.post(url, json=payload)
                if r.status_code >= 400:
                    raise ProviderError(self.provider_name, f"HTTP {r.status_code}: {r.text[:400]}")
                data = r.json()
        except httpx.HTTPError as e:
            raise ProviderError(self.provider_name, f"httpx_error: {str(e)}")

        content = data.get("content") or "(local mock) no content"
        usage = data.get("usage") or {}
        usage_norm = {
            "prompt_tokens": int(usage.get("prompt_tokens") or 0),
            "completion_tokens": int(usage.get("completion_tokens") or 0),
            "total_tokens": int(usage.get("total_tokens") or 0),
        }
        return ProviderResult(content=content, usage=usage_norm)
