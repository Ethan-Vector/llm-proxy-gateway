from __future__ import annotations

import logging
import time
from typing import Callable

from fastapi import Request, Response

log = logging.getLogger("llm-proxy.access")

async def access_log_middleware(request: Request, call_next: Callable) -> Response:
    start = time.perf_counter()
    response: Response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000.0

    record = log.info  # type: ignore
    extra = {
        "request_id": getattr(request.state, "request_id", None),
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "latency_ms": round(latency_ms, 2),
        "client": request.client.host if request.client else None,
    }
    log.info("request", extra=extra)
    return response
