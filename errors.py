from __future__ import annotations


class GatewayError(Exception):
    pass


class PolicyDenied(GatewayError):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class ProviderError(GatewayError):
    def __init__(self, provider: str, message: str):
        super().__init__(f"{provider}: {message}")
        self.provider = provider
        self.message = message
