from __future__ import annotations

import os
from typing import Any, Dict

import httpx

from .base import BaseProvider
from ..errors import http_error

class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, base_url: str, api_key_env: str):
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env

    def _api_key(self) -> str:
        key = os.getenv(self.api_key_env, "")
        if not key:
            raise http_error(500, f"missing upstream api key in env {self.api_key_env}")
        return key

    async def chat_completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # NOTE: This is a compatibility bridge. Anthropic's native API is different.
        # Here we intentionally provide a simple error to avoid giving a false sense
        # of full compatibility without explicit mapping.
        raise http_error(501, "anthropic provider stub: implement mapping for your use-case")

    async def completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise http_error(501, "anthropic provider stub: implement mapping for your use-case")

    async def embeddings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise http_error(501, "anthropic provider stub: implement mapping for your use-case")
