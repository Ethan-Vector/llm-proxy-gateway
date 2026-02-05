from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseProvider(ABC):
    name: str

    @abstractmethod
    async def chat_completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def embeddings(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError
