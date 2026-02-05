from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict

from fastapi import Request, Response

from ..errors import http_error

@dataclass
class Bucket:
    tokens: float
    last_ts: float

class TokenBucketLimiter:
    def __init__(self, refill_per_sec: float, capacity: int):
        self.refill_per_sec = float(refill_per_sec)
        self.capacity = int(capacity)
        self._buckets: Dict[str, Bucket] = {}

    def allow(self, key: str, cost: float = 1.0) -> bool:
        now = time.monotonic()
        b = self._buckets.get(key)
        if b is None:
            b = Bucket(tokens=float(self.capacity), last_ts=now)
            self._buckets[key] = b

        elapsed = max(0.0, now - b.last_ts)
        b.tokens = min(float(self.capacity), b.tokens + elapsed * self.refill_per_sec)
        b.last_ts = now

        if b.tokens >= cost:
            b.tokens -= cost
            return True
        return False

async def rate_limit_middleware(enabled: bool, limiter: TokenBucketLimiter, request: Request, call_next: Callable) -> Response:
    if not enabled:
        return await call_next(request)

    api_key = getattr(request.state, "api_key", "anonymous")
    if not limiter.allow(api_key, cost=1.0):
        raise http_error(429, "rate limit exceeded")
    return await call_next(request)
