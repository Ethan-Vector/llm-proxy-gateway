from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self, ttl_seconds: int, max_items: int):
        self.ttl_seconds = int(ttl_seconds)
        self.max_items = int(max_items)
        self._data: Dict[str, CacheEntry] = {}

    def _evict_if_needed(self) -> None:
        if len(self._data) <= self.max_items:
            return
        # naive eviction: remove oldest expiry
        oldest_key = min(self._data.items(), key=lambda kv: kv[1].expires_at)[0]
        self._data.pop(oldest_key, None)

    def get(self, key: str) -> Optional[Any]:
        e = self._data.get(key)
        if not e:
            return None
        if time.time() > e.expires_at:
            self._data.pop(key, None)
            return None
        return e.value

    def set(self, key: str, value: Any) -> None:
        expires_at = time.time() + self.ttl_seconds
        self._data[key] = CacheEntry(value=value, expires_at=expires_at)
        self._evict_if_needed()
