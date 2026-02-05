from __future__ import annotations

import secrets
from typing import Callable

from fastapi import Request, Response

HEADER = "X-Request-Id"

async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    rid = request.headers.get(HEADER) or secrets.token_hex(12)
    request.state.request_id = rid
    response: Response = await call_next(request)
    response.headers[HEADER] = rid
    return response
