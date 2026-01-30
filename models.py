from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    # passthrough metadata (not forwarded unless you choose)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    provider: str
    request_id: str
    content: str
    usage: dict[str, int] = Field(default_factory=dict)
    fallback_used: bool = False
