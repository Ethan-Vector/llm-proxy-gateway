from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Callable

from fastapi import Request, Response


@dataclass
class RequestContext:
    request_id: str
    tenant_id: str
    route: str


def get_ctx(request: Request) -> RequestContext:
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    tenant_id = request.headers.get("x-tenant-id") or "anonymous"
    route = request.headers.get("x-route") or "default"
    return RequestContext(request_id=rid, tenant_id=tenant_id, route=route)


async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    ctx = get_ctx(request)
    request.state.ctx = ctx
    start = time.perf_counter()
    resp: Response = await call_next(request)
    dur_ms = int((time.perf_counter() - start) * 1000)
    resp.headers["x-request-id"] = ctx.request_id
    resp.headers["x-latency-ms"] = str(dur_ms)
    return resp
