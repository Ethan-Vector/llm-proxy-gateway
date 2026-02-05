from __future__ import annotations

from typing import Callable, Iterable, Optional

from fastapi import Request, Response

from ..errors import http_error

def _extract_bearer(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return None

async def auth_middleware(enabled: bool, api_keys: Iterable[str], request: Request, call_next: Callable) -> Response:
    if not enabled:
        request.state.api_key = "anonymous"
        return await call_next(request)

    key = _extract_bearer(request.headers.get("authorization"))
    if not key or key not in set(api_keys):
        raise http_error(401, "unauthorized")
    request.state.api_key = key
    return await call_next(request)
