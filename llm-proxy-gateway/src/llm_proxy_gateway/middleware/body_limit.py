from __future__ import annotations

from typing import Callable

from fastapi import Request, Response

from ..errors import http_error

async def body_limit_middleware(max_bytes: int, request: Request, call_next: Callable) -> Response:
    cl = request.headers.get("content-length")
    if cl is not None:
        try:
            if int(cl) > max_bytes:
                raise http_error(413, f"request body too large (>{max_bytes} bytes)")
        except ValueError:
            pass
    # For safety: read body once and store for downstream if needed
    body = await request.body()
    if len(body) > max_bytes:
        raise http_error(413, f"request body too large (>{max_bytes} bytes)")
    request.state.raw_body = body
    return await call_next(request)
