from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .config import ProviderCfg
from .errors import http_error
from .providers.base import BaseProvider
from .providers.mock import MockProvider
from .providers.openai import OpenAIProvider
from .providers.anthropic import AnthropicProvider

@dataclass
class ProviderRegistry:
    providers: Dict[str, BaseProvider]

    def get(self, name: str) -> BaseProvider:
        p = self.providers.get(name)
        if not p:
            raise http_error(400, f"unknown provider '{name}'")
        return p

def build_registry(provider_cfgs: Dict[str, ProviderCfg]) -> ProviderRegistry:
    built: Dict[str, BaseProvider] = {}
    for name, cfg in provider_cfgs.items():
        kind = cfg.kind.lower()
        if kind == "mock":
            built[name] = MockProvider()
        elif kind == "openai":
            if not cfg.base_url or not cfg.api_key_env:
                raise ValueError("openai provider requires base_url and api_key_env")
            built[name] = OpenAIProvider(base_url=cfg.base_url, api_key_env=cfg.api_key_env)
        elif kind == "anthropic":
            if not cfg.base_url or not cfg.api_key_env:
                raise ValueError("anthropic provider requires base_url and api_key_env")
            built[name] = AnthropicProvider(base_url=cfg.base_url, api_key_env=cfg.api_key_env)
        else:
            raise ValueError(f"unknown provider kind '{cfg.kind}' for provider '{name}'")
    return ProviderRegistry(providers=built)

def provider_from_model(model: str) -> Tuple[Optional[str], str]:
    # model format: "<provider>:<upstream_model>"
    if ":" not in model:
        return None, model
    prefix, rest = model.split(":", 1)
    return prefix, rest
