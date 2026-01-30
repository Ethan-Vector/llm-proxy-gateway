from __future__ import annotations

import re
from dataclasses import dataclass

from .config import RedactionConfig


@dataclass(frozen=True)
class Redactor:
    enabled: bool
    compiled: list[tuple[str, re.Pattern[str], str]]

    @classmethod
    def from_config(cls, cfg: RedactionConfig) -> "Redactor":
        compiled: list[tuple[str, re.Pattern[str], str]] = []
        for p in cfg.patterns:
            compiled.append((p.name, re.compile(p.regex), p.replacement))
        return cls(enabled=cfg.enabled, compiled=compiled)

    def apply(self, text: str) -> str:
        if not self.enabled or not text:
            return text
        out = text
        for _, rx, repl in self.compiled:
            out = rx.sub(repl, out)
        return out

    def apply_messages(self, messages: list[dict]) -> list[dict]:
        # expects list of {role, content}
        return [{"role": m.get("role"), "content": self.apply(m.get("content", ""))} for m in messages]
