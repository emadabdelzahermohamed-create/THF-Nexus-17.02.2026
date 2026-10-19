from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Route:
    provider: str
    estimated_marginal_cost_usd: float
    sustainable: bool
    reason: str


def choose(routes: list[Route]) -> Route:
    viable = [r for r in routes if r.sustainable]
    if not viable:
        raise ValueError("no sustainable route")
    return sorted(viable, key=lambda r: (r.estimated_marginal_cost_usd, r.provider))[0]
