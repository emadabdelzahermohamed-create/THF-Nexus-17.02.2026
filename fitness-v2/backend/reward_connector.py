"""Partner reward connector for Fitness V2.

Fitness owns verified-activity evidence only. Partner games own identities,
inventory, currency and progression. This module never writes partner data.
Raw camera frames and Health Connect records are deliberately absent from the
claim schema.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import base64
import hashlib
import hmac
import json
import time
from typing import Mapping


class RewardClaimError(ValueError):
    pass


@dataclass(frozen=True)
class RewardEligibilityClaim:
    issuer: str
    partner_id: str
    campaign_id: str
    fitness_user_id: str
    external_user_id: str
    reward_id: str
    quantity: int
    evidence_score: int
    session_hash: str
    nonce: str
    issued_at: int
    expires_at: int
    claim_id: str

    def payload(self) -> dict:
        return asdict(self)


class RewardClaimSigner:
    """HMAC implementation for local/dev deployments; key stays server-side.

    Production can replace this interface with KMS asymmetric signing without
    changing the partner claim contract.
    """

    def __init__(self, key: bytes, issuer: str = "topherofit-fitness"):
        if len(key) < 32:
            raise RewardClaimError("signing key must be at least 256 bits")
        self.key = key
        self.issuer = issuer

    @staticmethod
    def _canonical(payload: Mapping) -> bytes:
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()

    def issue(self, *, partner_id: str, campaign_id: str, fitness_user_id: str,
              external_user_id: str, reward_id: str, quantity: int,
              evidence_score: int, session_hash: str, nonce: str,
              ttl_seconds: int = 300, now: int | None = None) -> dict:
        now = int(time.time() if now is None else now)
        if quantity < 1 or not 0 <= evidence_score <= 100:
            raise RewardClaimError("invalid quantity/evidence score")
        if ttl_seconds < 1 or ttl_seconds > 900:
            raise RewardClaimError("ttl outside allowed range")
        if not all((partner_id, campaign_id, fitness_user_id, external_user_id,
                    reward_id, session_hash, nonce)):
            raise RewardClaimError("missing required binding")
        seed = f"{partner_id}:{campaign_id}:{fitness_user_id}:{external_user_id}:{reward_id}:{nonce}"
        claim_id = hashlib.sha256(seed.encode()).hexdigest()
        claim = RewardEligibilityClaim(
            self.issuer, partner_id, campaign_id, fitness_user_id,
            external_user_id, reward_id, quantity, evidence_score,
            session_hash, nonce, now, now + ttl_seconds, claim_id,
        )
        payload = claim.payload()
        signature = hmac.new(self.key, self._canonical(payload), hashlib.sha256).digest()
        return {"claim": payload, "signature": base64.urlsafe_b64encode(signature).decode().rstrip("=")}

    def verify(self, envelope: Mapping, *, expected_partner: str,
               now: int | None = None) -> RewardEligibilityClaim:
        payload = envelope.get("claim")
        signature = envelope.get("signature", "")
        if not isinstance(payload, dict):
            raise RewardClaimError("missing claim")
        expected = hmac.new(self.key, self._canonical(payload), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        if not hmac.compare_digest(expected, supplied):
            raise RewardClaimError("invalid signature")
        claim = RewardEligibilityClaim(**payload)
        current = int(time.time() if now is None else now)
        if claim.partner_id != expected_partner:
            raise RewardClaimError("partner binding mismatch")
        if current > claim.expires_at or claim.expires_at <= claim.issued_at:
            raise RewardClaimError("claim expired/invalid")
        return claim


def assert_reward_eligible(*, verified: bool, manual: bool, revoked: bool,
                           evidence_score: int, minimum_score: int) -> None:
    """Fail closed: manual/unverified/revoked activity never earns game rewards."""
    if manual or not verified or revoked or evidence_score < minimum_score:
        raise RewardClaimError("activity is not reward eligible")
