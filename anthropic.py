from __future__ import annotations

import httpx

from .base import ProviderClient, ProviderResult
from ..errors import ProviderError


class AnthropicClient(ProviderClient):
    def __init__(self, provider_name: str, model: str, timeout_s: int, api_key: str, base_url: str):
        super().__init__(provider_name, model, timeout_s)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def chat(self, messages: list[dict[str, str]], temperature: float, max_tokens: int) -> ProviderResult:
        """
        Mapping minimale verso Anthropic Messages API:
        - prende system separatamente, il resto come messages user/assistant.
        """
        url = f"{self.base_url}/messages"
        system_parts = [m["content"] for m in messages if m.get("role") == "system"]
        system = "\n".join(system_parts) if system_parts else None
        msg_list = [{"role": m["role"], "content": m["content"]} for m in messages if m.get("role") != "system"]

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": msg_list,
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                r = await client.post(url, json=payload, headers=headers)
                if r.status_code >= 400:
                    raise ProviderError(self.provider_name, f"HTTP {r.status_code}: {r.text[:400]}")
                data = r.json()
        except httpx.HTTPError as e:
            raise ProviderError(self.provider_name, f"httpx_error: {str(e)}")

        # Anthropic response: content is list of blocks
        blocks = data.get("content") or []
        text_parts = []
        for b in blocks:
            if b.get("type") == "text":
                text_parts.append(b.get("text", ""))
        content = "".join(text_parts)

        # Usage fields differ; normalize best-effort
        usage = data.get("usage") or {}
        prompt_tokens = int(usage.get("input_tokens") or 0)
        completion_tokens = int(usage.get("output_tokens") or 0)
        usage_norm = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }
        return ProviderResult(content=content, usage=usage_norm)
