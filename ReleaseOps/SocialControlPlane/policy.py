from __future__ import annotations
from dataclasses import dataclass
import re
from .models import PostIntent

RETURN_PATTERNS = [
    r"guaranteed?\s+(profit|return)", r"risk[- ]?free\s+(profit|return)",
    r"مضمون(?:ة)?\s+(?:الربح|الأرباح|العائد)", r"ارباح\s+مضمونة",
    r"سيرتفع\s+حتما", r"to the moon", r"100x", r"1000x",
]
URGENCY_PATTERNS = [r"buy\s+now", r"last\s+chance", r"اشتر(?:ي|وا)?\s+الآن", r"فرصتك\s+الأخيرة"]
TOKEN_CLAIM_TERMS = {
    "supply", "burn", "mint", "revenue share", "tokenomics", "treasury",
    "المعروض", "الحرق", "السك", "الخزانة", "الإيراد", "التوكنوميكس",
}

@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reasons: tuple[str, ...]
    requires_evidence: bool


def evaluate(intent: PostIntent) -> PolicyDecision:
    text = intent.text.lower()
    reasons: list[str] = []
    for p in RETURN_PATTERNS:
        if re.search(p, text, flags=re.I):
            reasons.append("prohibited_return_or_price_promise")
            break
    for p in URGENCY_PATTERNS:
        if re.search(p, text, flags=re.I):
            reasons.append("prohibited_financial_urgency")
            break
    requires_evidence = any(term in text for term in TOKEN_CLAIM_TERMS)
    if requires_evidence and not intent.source_evidence:
        reasons.append("token_claim_requires_source_evidence")
    if not intent.text.strip() and not intent.media_url:
        reasons.append("empty_post")
    return PolicyDecision(not reasons, tuple(reasons), requires_evidence)
