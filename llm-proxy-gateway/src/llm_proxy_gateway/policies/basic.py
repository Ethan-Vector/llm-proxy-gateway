from __future__ import annotations

from typing import Iterable, Optional

from ..errors import http_error

def enforce_model_allowlist(model: str, allowed: Iterable[str]) -> None:
    allowed_list = list(allowed)
    if allowed_list and model not in allowed_list:
        raise http_error(400, f"model '{model}' is not allowed")

def enforce_prompt_size(text: str, max_chars: int) -> None:
    if max_chars > 0 and len(text) > max_chars:
        raise http_error(400, f"prompt too large ({len(text)} chars > {max_chars})")

def extract_prompt_from_chat(messages: list[dict]) -> str:
    # Rough: concatenate content
    parts = []
    for m in messages:
        c = m.get("content")
        if isinstance(c, str):
            parts.append(c)
    return "\n".join(parts)
