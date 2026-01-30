from __future__ import annotations

import os
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .audit import AuditEvent, AuditSink
from .config import EnvSettings, load_config
from .errors import PolicyDenied, ProviderError
from .middleware import request_id_middleware
from .models import ChatCompletionRequest, ChatCompletionResponse
from .policy import InMemoryRateLimiter, enforce_policy, estimate_cost_usd
from .redaction import Redactor
from .providers.openai import OpenAIClient
from .providers.anthropic import AnthropicClient
from .providers.local import LocalClient


def build_provider(provider_name: str, pcfg: Any, env: EnvSettings):
    kind = pcfg.kind.lower()
    if kind == "openai":
        if not env.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY missing")
        return OpenAIClient(
            provider_name=provider_name,
            model=pcfg.model,
            timeout_s=pcfg.timeout_s,
            api_key=env.openai_api_key,
            base_url=env.openai_base_url,
        )
    if kind == "anthropic":
        if not env.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY missing")
        return AnthropicClient(
            provider_name=provider_name,
            model=pcfg.model,
            timeout_s=pcfg.timeout_s,
            api_key=env.anthropic_api_key,
            base_url=env.anthropic_base_url,
        )
    if kind == "local":
        return LocalClient(
            provider_name=provider_name,
            model=pcfg.model,
            timeout_s=pcfg.timeout_s,
            base_url=env.local_provider_base_url,
        )
    raise RuntimeError(f"Unknown provider kind: {pcfg.kind}")


env = EnvSettings()
loaded = load_config(env.config_path)
redactor = Redactor.from_config(loaded.config.redaction)
audit_sink = AuditSink()
rate_limiter = (
    InMemoryRateLimiter(loaded.config.rate_limit.requests_per_minute)
    if loaded.config.rate_limit.enabled
    else None
)

app = FastAPI(title="ethan-llm-proxy-gateway", version="0.1.0")
app.middleware("http")(request_id_middleware)


@app.get("/healthz")
async def healthz():
    return {
        "ok": True,
        "config_version": loaded.version_hash,
        "gateway": loaded.config.gateway,
    }


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(req: ChatCompletionRequest, request: Request):
    ctx = request.state.ctx
    tenant_id = ctx.tenant_id
    route = ctx.route

    # policy gate
    bd = enforce_policy(
        cfg=loaded,
        tenant_id=tenant_id,
        route=route,
        rate_limiter=rate_limiter,
        requested_max_tokens=req.max_tokens,
    )

    route_cfg = loaded.config.routes.get(route)
    if not route_cfg:
        return JSONResponse(status_code=400, content={"error": f"unknown route: {route}"})

    provider_chain: list[str] = list(route_cfg.get("providers") or [])
    if not provider_chain:
        return JSONResponse(status_code=400, content={"error": f"route has no providers: {route}"})

    # effective max_tokens: request override else budget max_tokens
    max_tokens = req.max_tokens if req.max_tokens is not None else bd.effective_max_tokens

    # messages as dict list for provider clients
    messages = [m.model_dump() for m in req.messages]

    # audit-safe versions
    req_redacted = {
        "messages": redactor.apply_messages(messages),
        "temperature": req.temperature,
        "max_tokens": max_tokens,
        "metadata": req.metadata,
    }

    request_id = ctx.request_id

    last_err: str | None = None

    for attempt, pname in enumerate(provider_chain, start=1):
        pcfg = loaded.config.providers.get(pname)
        if not pcfg:
            last_err = f"provider_not_configured: {pname}"
            continue

        provider = build_provider(pname, pcfg, env)
        try:
            res = await provider.chat(messages=messages, temperature=req.temperature, max_tokens=max_tokens)

            # budget: cost estimate
            prompt_t = int(res.usage.get("prompt_tokens") or 0)
            completion_t = int(res.usage.get("completion_tokens") or 0)
            est_cost = estimate_cost_usd(provider.model, prompt_t, completion_t)
            if est_cost > bd.effective_max_cost_usd:
                raise PolicyDenied(
                    f"estimated_cost_exceeds_budget: {est_cost:.4f} > {bd.effective_max_cost_usd:.4f}"
                )

            resp = ChatCompletionResponse(
                id=str(uuid.uuid4()),
                model=provider.model,
                provider=provider.provider_name,
                request_id=request_id,
                content=res.content,
                usage=res.usage,
                fallback_used=(attempt > 1),
            )

            # audit emit
            audit_sink.emit(
                AuditEvent(
                    ts_ms=audit_sink.now_ms(),
                    request_id=request_id,
                    tenant_id=tenant_id,
                    route=route,
                    config_version=loaded.version_hash,
                    provider=provider.provider_name,
                    model=provider.model,
                    attempt=attempt,
                    fallback_used=(attempt > 1),
                    status="ok",
                    latency_ms=int(request.headers.get("x-latency-ms") or 0),
                    request_redacted=req_redacted,
                    response_redacted={"content": redactor.apply(res.content), "usage": res.usage},
                    error=None,
                )
            )
            return resp

        except PolicyDenied as e:
            # hard stop (non ha senso fallbackare se budget/policy ha negato)
            audit_sink.emit(
                AuditEvent(
                    ts_ms=audit_sink.now_ms(),
                    request_id=request_id,
                    tenant_id=tenant_id,
                    route=route,
                    config_version=loaded.version_hash,
                    provider=provider.provider_name,
                    model=provider.model,
                    attempt=attempt,
                    fallback_used=(attempt > 1),
                    status="denied",
                    latency_ms=int(request.headers.get("x-latency-ms") or 0),
                    request_redacted=req_redacted,
                    response_redacted={},
                    error=e.reason,
                )
            )
            return JSONResponse(status_code=429, content={"error": e.reason})

        except ProviderError as e:
            last_err = e.message
            audit_sink.emit(
                AuditEvent(
                    ts_ms=audit_sink.now_ms(),
                    request_id=request_id,
                    tenant_id=tenant_id,
                    route=route,
                    config_version=loaded.version_hash,
                    provider=e.provider,
                    model=pcfg.model,
                    attempt=attempt,
                    fallback_used=(attempt > 1),
                    status="error",
                    latency_ms=int(request.headers.get("x-latency-ms") or 0),
                    request_redacted=req_redacted,
                    response_redacted={},
                    error=str(e),
                )
            )
            continue

    return JSONResponse(
        status_code=502,
        content={"error": "all_providers_failed", "last_error": last_err, "request_id": request_id},
    )


def main():
    import uvicorn

    uvicorn.run(
        "llm_proxy_gateway.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8080")),
        reload=False,
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
    )


if __name__ == "__main__":
    main()
