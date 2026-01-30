from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from .config import BudgetConfig, LoadedConfig
from .errors import PolicyDenied


@dataclass
class BudgetDecision:
    budget: BudgetConfig
    effective_max_tokens: int
    effective_max_cost_usd: float


class InMemoryRateLimiter:
    """
    Token bucket semplificato per demo/single instance.
    Chiave: (tenant_id, route). Finestra 60s.
    """

    def __init__(self, rpm: int):
        self.rpm = max(1, rpm)
        self._window_start = int(time.time())
        self._counts: dict[tuple[str, str], int] = {}

    def allow(self, tenant_id: str, route: str) -> bool:
        now = int(time.time())
        if now - self._window_start >= 60:
            self._window_start = now
            self._counts = {}
        k = (tenant_id, route)
        self._counts[k] = self._counts.get(k, 0) + 1
        return self._counts[k] <= self.rpm


def resolve_budget(cfg: LoadedConfig, tenant_id: str, route: str) -> BudgetDecision:
    budgets = cfg.config.budgets
    base = budgets.default
    t = budgets.tenants.get(tenant_id)
    r = budgets.routes.get(route)

    # Merge strategy: route overrides tenant overrides default
    effective = BudgetConfig(
        max_tokens=base.max_tokens,
        max_cost_usd=base.max_cost_usd,
    )
    if t:
        effective.max_tokens = t.max_tokens
        effective.max_cost_usd = t.max_cost_usd
    if r:
        effective.max_tokens = r.max_tokens
        effective.max_cost_usd = r.max_cost_usd

    return BudgetDecision(
        budget=effective,
        effective_max_tokens=effective.max_tokens,
        effective_max_cost_usd=effective.max_cost_usd,
    )


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Euristica: NON è billing. Serve per guardrail.
    Prezzi fittizi/placeholder -> sostituisci con lookup reale se vuoi.
    """
    # rough buckets
    if "gpt-4" in model:
        in_rate = 0.00015
        out_rate = 0.00060
    elif "claude" in model:
        in_rate = 0.00020
        out_rate = 0.00100
    else:
        in_rate = 0.00005
        out_rate = 0.00010

    return prompt_tokens * in_rate + completion_tokens * out_rate


def enforce_policy(
    cfg: LoadedConfig,
    tenant_id: str,
    route: str,
    rate_limiter: Optional[InMemoryRateLimiter],
    requested_max_tokens: Optional[int],
) -> BudgetDecision:
    if cfg.config.rate_limit.enabled and rate_limiter is not None:
        if not rate_limiter.allow(tenant_id, route):
            raise PolicyDenied("rate_limit_exceeded")

    bd = resolve_budget(cfg, tenant_id, route)

    if requested_max_tokens is not None and requested_max_tokens > bd.effective_max_tokens:
        raise PolicyDenied(f"max_tokens_exceeds_budget: {requested_max_tokens} > {bd.effective_max_tokens}")

    return bd
