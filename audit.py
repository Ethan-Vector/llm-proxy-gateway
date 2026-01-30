from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AuditEvent:
    ts_ms: int
    request_id: str
    tenant_id: str
    route: str
    config_version: str

    provider: str
    model: str
    attempt: int
    fallback_used: bool

    status: str  # ok | error | denied
    latency_ms: int

    request_redacted: dict[str, Any]
    response_redacted: dict[str, Any]
    error: Optional[str] = None


class AuditSink:
    """
    Default: stdout JSON lines.
    In prod: sostituisci con Kafka / OTEL logs / SIEM pipeline.
    """

    def emit(self, ev: AuditEvent) -> None:
        print(json.dumps(ev.__dict__, ensure_ascii=False))

    @staticmethod
    def now_ms() -> int:
        return int(time.time() * 1000)
