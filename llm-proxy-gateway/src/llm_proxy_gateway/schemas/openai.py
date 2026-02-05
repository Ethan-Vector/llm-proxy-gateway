from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant", "tool"]

class ChatMessage(BaseModel):
    role: Role
    content: Union[str, List[Dict[str, Any]]] = ""

class ChatCompletionsRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class CompletionsRequest(BaseModel):
    model: str
    prompt: Union[str, List[str]]
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

class EmbeddingsRequest(BaseModel):
    model: str
    input: Union[str, List[str]]
