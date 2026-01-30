from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ProviderResult:
    content: str
    usage: dict[str, int]


class ProviderClient(ABC):
    def __init__(self, provider_name: str, model: str, timeout_s: int):
        self.provider_name = provider_name
        self.model = model
        self.timeout_s = timeout_s

    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], temperature: float, max_tokens: int) -> ProviderResult:
        raise NotImplementedError
