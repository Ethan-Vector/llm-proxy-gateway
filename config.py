from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 8080
    log_level: str = "INFO"
    config_path: str = "configs/gateway.yaml"

    # provider env
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"

    anthropic_api_key: Optional[str] = None
    anthropic_base_url: str = "https://api.anthropic.com/v1"

    local_provider_base_url: str = "http://localhost:9999"

    class Config:
        env_file = ".env"
        extra = "ignore"


class RedactionPattern(BaseModel):
    name: str
    regex: str
    replacement: str


class RedactionConfig(BaseModel):
    enabled: bool = True
    patterns: list[RedactionPattern] = Field(default_factory=list)


class RateLimitConfig(BaseModel):
    enabled: bool = True
    requests_per_minute: int = 60


class BudgetConfig(BaseModel):
    max_tokens: int = 1200
    max_cost_usd: float = 0.50


class Budgets(BaseModel):
    default: BudgetConfig = BudgetConfig()
    tenants: dict[str, BudgetConfig] = Field(default_factory=dict)
    routes: dict[str, BudgetConfig] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    kind: str  # openai | anthropic | local
    model: str
    timeout_s: int = 30


class AppConfig(BaseModel):
    gateway: dict[str, Any] = Field(default_factory=dict)
    redaction: RedactionConfig = RedactionConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    budgets: Budgets = Budgets()
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)
    routes: dict[str, dict[str, Any]] = Field(default_factory=dict)


@dataclass(frozen=True)
class LoadedConfig:
    config: AppConfig
    raw: dict[str, Any]
    version_hash: str


def load_config(path: str) -> LoadedConfig:
    p = Path(path)
    raw_bytes = p.read_bytes()
    raw: dict[str, Any] = yaml.safe_load(raw_bytes) or {}
    version_hash = hashlib.sha256(raw_bytes).hexdigest()[:12]
    config = AppConfig.model_validate(raw)
    return LoadedConfig(config=config, raw=raw, version_hash=version_hash)
