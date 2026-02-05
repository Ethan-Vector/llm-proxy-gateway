from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx

from .base import BaseProvider
from ..errors import http_error

class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, base_url: str, api_key_env: str):
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env

    def _api_key(self) -> str:
        key = os.getenv(self.api_key_env, "")
        if not key:
            raise http_error(500, f"missing upstream api key in env {self.api_key_env}")
        return key

    async def chat_completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("/chat/completions", payload)

    async def completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("/completions", payload)

    async def embeddings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("/embeddings", payload)

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self._api_key()}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(self.base_url + path, headers=headers, json=payload)
            if r.status_code >= 400:
                raise http_error(502, f"upstream error ({r.status_code}): {r.text[:200]}")
            return r.json()
