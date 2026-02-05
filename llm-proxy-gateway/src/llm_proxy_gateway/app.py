from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .cache import TTLCache
from .config import LoadedConfig
from .errors import http_error
from .logging import setup_logging
from .middleware.access_log import access_log_middleware
from .middleware.auth import auth_middleware
from .middleware.body_limit import body_limit_middleware
from .middleware.rate_limit import TokenBucketLimiter, rate_limit_middleware
from .middleware.request_id import request_id_middleware
from .policies.basic import enforce_model_allowlist, enforce_prompt_size, extract_prompt_from_chat
from .routing import ProviderRegistry, build_registry, provider_from_model
from .schemas.openai import ChatCompletionsRequest, CompletionsRequest, EmbeddingsRequest

log = logging.getLogger("llm-proxy")

def _cache_key(path: str, payload: Dict[str, Any]) -> str:
    raw = json.dumps({"path": path, "payload": payload}, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def create_app(loaded: LoadedConfig) -> FastAPI:
    cfg = loaded.cfg
    setup_logging(cfg.server.log_level)

    app = FastAPI(title="llm-proxy-gateway", version="0.1.0")

    registry: ProviderRegistry = build_registry(cfg.routing.providers)
    limiter = TokenBucketLimiter(
        refill_per_sec=cfg.rate_limit.per_key.refill_per_sec,
        capacity=cfg.rate_limit.per_key.capacity,
    )
    cache: Optional[TTLCache] = None
    if cfg.cache.enabled:
        cache = TTLCache(ttl_seconds=cfg.cache.ttl_seconds, max_items=cfg.cache.max_items)

    @app.middleware("http")
    async def _request_id(request: Request, call_next):
        return await request_id_middleware(request, call_next)

    @app.middleware("http")
    async def _body_limit(request: Request, call_next):
        return await body_limit_middleware(cfg.server.request_body_max_bytes, request, call_next)

    @app.middleware("http")
    async def _auth(request: Request, call_next):
        return await auth_middleware(cfg.auth.enabled, cfg.auth.api_keys, request, call_next)

    @app.middleware("http")
    async def _rate_limit(request: Request, call_next):
        return await rate_limit_middleware(cfg.rate_limit.enabled, limiter, request, call_next)

    @app.middleware("http")
    async def _access_log(request: Request, call_next):
        return await access_log_middleware(request, call_next)

    @app.get("/healthz")
    async def healthz():
        return {"ok": True}

    @app.post("/v1/chat/completions")
    async def chat_completions(req: ChatCompletionsRequest, request: Request):
        model = req.model
        enforce_model_allowlist(model, cfg.routing.allowed_models)

        if cfg.policies.enabled:
            prompt = extract_prompt_from_chat([m.model_dump() for m in req.messages])
            enforce_prompt_size(prompt, cfg.policies.max_prompt_chars)

        provider_name, upstream_model = provider_from_model(model)
        provider = registry.get(provider_name or cfg.routing.default_provider)

        payload = req.model_dump()
        # Preserve original model string in the response (OpenAI-compatible), but pass upstream model to provider if desired.
        # Here we keep it simple: send the full model string; you can map it in providers if you need.
        path = "/v1/chat/completions"

        if cache:
            key = _cache_key(path, payload)
            hit = cache.get(key)
            if hit is not None:
                return JSONResponse(hit)

        out = await provider.chat_completions(payload)

        if cache:
            cache.set(key, out)
        return JSONResponse(out)

    @app.post("/v1/completions")
    async def completions(req: CompletionsRequest, request: Request):
        model = req.model
        enforce_model_allowlist(model, cfg.routing.allowed_models)

        if cfg.policies.enabled:
            # prompt can be list or str
            if isinstance(req.prompt, list):
                prompt = "\n".join([str(x) for x in req.prompt])
            else:
                prompt = str(req.prompt)
            enforce_prompt_size(prompt, cfg.policies.max_prompt_chars)

        provider_name, _upstream = provider_from_model(model)
        provider = registry.get(provider_name or cfg.routing.default_provider)

        payload = req.model_dump()
        path = "/v1/completions"

        if cache:
            key = _cache_key(path, payload)
            hit = cache.get(key)
            if hit is not None:
                return JSONResponse(hit)

        out = await provider.completions(payload)

        if cache:
            cache.set(key, out)
        return JSONResponse(out)

    @app.post("/v1/embeddings")
    async def embeddings(req: EmbeddingsRequest, request: Request):
        model = req.model
        enforce_model_allowlist(model, cfg.routing.allowed_models)

        provider_name, _upstream = provider_from_model(model)
        provider = registry.get(provider_name or cfg.routing.default_provider)

        payload = req.model_dump()
        path = "/v1/embeddings"

        if cache:
            key = _cache_key(path, payload)
            hit = cache.get(key)
            if hit is not None:
                return JSONResponse(hit)

        out = await provider.embeddings(payload)

        if cache:
            cache.set(key, out)
        return JSONResponse(out)

    return app
