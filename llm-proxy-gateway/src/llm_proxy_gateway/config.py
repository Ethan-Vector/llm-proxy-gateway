from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class EnvSettings(BaseSettings):
    llm_proxy_api_keys: str = Field(default="", alias="LLM_PROXY_API_KEYS")

    class Config:
        extra = "ignore"

class ServerCfg(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    request_body_max_bytes: int = 1_048_576
    log_level: str = "INFO"

class AuthCfg(BaseModel):
    enabled: bool = True
    api_keys: List[str] = Field(default_factory=list)

class RateLimitPerKeyCfg(BaseModel):
    refill_per_sec: float = 2.0
    capacity: int = 10

class RateLimitCfg(BaseModel):
    enabled: bool = True
    per_key: RateLimitPerKeyCfg = RateLimitPerKeyCfg()

class ProviderCfg(BaseModel):
    kind: str
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None

class RoutingCfg(BaseModel):
    default_provider: str = "mock"
    allowed_models: List[str] = Field(default_factory=list)
    providers: Dict[str, ProviderCfg] = Field(default_factory=dict)

class CacheCfg(BaseModel):
    enabled: bool = False
    ttl_seconds: int = 60
    max_items: int = 1024

class PoliciesCfg(BaseModel):
    enabled: bool = True
    max_prompt_chars: int = 50_000

class AppCfg(BaseModel):
    server: ServerCfg = ServerCfg()
    auth: AuthCfg = AuthCfg()
    rate_limit: RateLimitCfg = RateLimitCfg()
    routing: RoutingCfg = RoutingCfg()
    cache: CacheCfg = CacheCfg()
    policies: PoliciesCfg = PoliciesCfg()

@dataclass(frozen=True)
class LoadedConfig:
    cfg: AppCfg
    env: EnvSettings

def load_config(path: str) -> LoadedConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw: Dict[str, Any] = yaml.safe_load(f) or {}
    cfg = AppCfg.model_validate(raw)
    env = EnvSettings()
    # Merge API keys from env if config empty
    if cfg.auth.enabled and not cfg.auth.api_keys:
        keys = [k.strip() for k in env.llm_proxy_api_keys.split(",") if k.strip()]
        cfg.auth.api_keys = keys
    return LoadedConfig(cfg=cfg, env=env)
