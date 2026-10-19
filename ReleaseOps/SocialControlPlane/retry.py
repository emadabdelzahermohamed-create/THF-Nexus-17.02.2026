from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RetryDecision:
    retry: bool
    delay_seconds: int
    reason: str

def classify(status: int, attempt: int, retry_after: int | None = None) -> RetryDecision:
    if attempt < 1: raise ValueError('attempt must be >= 1')
    if status == 429:
        return RetryDecision(True, retry_after or min(3600, 30 * (2 ** (attempt - 1))), 'rate_limited')
    if status in {408, 425, 500, 502, 503, 504}:
        return RetryDecision(True, min(900, 5 * (2 ** (attempt - 1))), 'transient')
    return RetryDecision(False, 0, 'permanent')
