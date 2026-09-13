#!/usr/bin/env python3
"""Fail-closed THF anti-whale/reward policy completion gate.

This module validates policy-completion provenance only. It never signs,
submits, broadcasts, transfers, burns, or mutates Solana state.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction"
}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def _scan(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive/signature field at {path}.{key}")
            _scan(item, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            _scan(item, f"{path}[{idx}]")


def _positive_integer_string(value: Any, label: str) -> int:
    if not isinstance(value, str) or not value.isdigit() or int(value) <= 0:
        raise ValueError(f"{label} must be a positive integer string")
    return int(value)


def evaluate_policy_completion(
    completion: Dict[str, Any],
    authoritative_policy: Dict[str, Any],
    treasury_policy: Dict[str, Any],
) -> Dict[str, Any]:
    _scan(completion)
    _scan(authoritative_policy)
    _scan(treasury_policy)

    for document, label in (
        (completion, "completion"),
        (authoritative_policy, "authoritative policy"),
        (treasury_policy, "treasury policy"),
    ):
        if document.get("network") != CANONICAL_NETWORK or document.get("mint") != CANONICAL_MINT:
            raise ValueError(f"{label} target mismatch")

    policy_sha = completion.get("authoritative_policy_sha256")
    treasury_sha = completion.get("treasury_policy_sha256")
    if not isinstance(policy_sha, str) or not HEX64.fullmatch(policy_sha):
        raise ValueError("invalid authoritative policy SHA-256")
    if not isinstance(treasury_sha, str) or not HEX64.fullmatch(treasury_sha):
        raise ValueError("invalid treasury policy SHA-256")
    if policy_sha != canonical_sha256(authoritative_policy):
        raise ValueError("authoritative policy SHA-256 mismatch")
    if treasury_sha != canonical_sha256(treasury_policy):
        raise ValueError("treasury policy SHA-256 mismatch")

    for field in ("authoritative_policy_blob_sha", "treasury_policy_blob_sha", "source_head_prior_verified"):
        value = completion.get(field)
        if not isinstance(value, str) or not HEX40.fullmatch(value):
            raise ValueError(f"invalid Git provenance field: {field}")

    economics = authoritative_policy.get("economics", {})
    controls = authoritative_policy.get("distribution_controls", {})
    hard_guards = treasury_policy.get("hard_guards", {})
    if economics.get("active_user_revenue_share") != 0.35:
        raise ValueError("authoritative active-user revenue share must remain exactly 35%")
    if str(economics.get("approved_supply_floor_target_ui")) != "8000000000":
        raise ValueError("authoritative 8B supply floor mismatch")
    if controls.get("anti_whale_cap_required") is not True:
        raise ValueError("authoritative anti-whale requirement missing")
    if controls.get("activity_evidence_required") is not True or controls.get("anti_sybil_required") is not True:
        raise ValueError("authoritative eligibility controls weakened")
    if hard_guards.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation not asserted")
    if hard_guards.get("private_key_forbidden") is not True or hard_guards.get("seed_phrase_forbidden") is not True:
        raise ValueError("key-material guard weakened")

    if completion.get("active_user_revenue_share") != 0.35:
        raise ValueError("completion must preserve exact 35% active-user share")
    safety = completion.get("safety", {})
    if safety.get("wave_mawja_untouched") is not True:
        raise ValueError("completion does not assert WAVE isolation")
    if any(bool(safety.get(k)) for k in (
        "simulation_review_eligible", "execution_authorized", "transaction_signing",
        "transaction_broadcast", "private_key_material_allowed"
    )):
        raise ValueError("unsafe completion state")

    anti_whale = completion.get("anti_whale", {})
    reward_epoch = completion.get("reward_epoch", {})
    governance = completion.get("governance_provenance", {})
    blockers = []

    per_user = anti_whale.get("per_user_cap_ui")
    epoch_cap = anti_whale.get("epoch_budget_cap_ui")
    policy_per_user = controls.get("per_user_cap")
    policy_epoch_cap = controls.get("epoch_budget_cap")

    if per_user is None or epoch_cap is None:
        blockers.append("anti_whale_caps_not_authoritatively_configured")
    else:
        per_user_int = _positive_integer_string(per_user, "per_user_cap_ui")
        epoch_cap_int = _positive_integer_string(epoch_cap, "epoch_budget_cap_ui")
        if per_user_int > epoch_cap_int:
            raise ValueError("per-user cap cannot exceed reward epoch budget cap")
        if reward_epoch.get("epoch_budget_cap_ui") != epoch_cap:
            raise ValueError("reward epoch budget must bind the same epoch cap")
        if str(policy_per_user) != per_user or str(policy_epoch_cap) != epoch_cap:
            blockers.append("authoritative_repo_policy_caps_incomplete_or_mismatched")

    required_governance = ("decision_id", "approval_record_sha256", "governance_policy_sha256", "approved_at")
    if governance.get("status") != "approved" or any(not governance.get(k) for k in required_governance):
        blockers.append("governance_provenance_incomplete")
    else:
        if not HEX64.fullmatch(str(governance["approval_record_sha256"])):
            raise ValueError("invalid governance approval-record SHA-256")
        if not HEX64.fullmatch(str(governance["governance_policy_sha256"])):
            raise ValueError("invalid governance-policy SHA-256")

    if completion.get("production_caps_configured") is not True:
        blockers.append("production_caps_not_approved")

    completed = not blockers
    if completed and completion.get("status") != "authoritatively_completed":
        raise ValueError("completed policy must declare authoritatively_completed")
    if not completed and completion.get("status") == "authoritatively_completed":
        raise ValueError("incomplete policy cannot declare authoritatively_completed")

    result = {
        "gate": "THF_TOKENOPS_ANTI_WHALE_REWARD_POLICY_COMPLETION_V1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "authoritative_policy_sha256": policy_sha,
        "treasury_policy_sha256": treasury_sha,
        "authoritatively_completed": completed,
        "blockers": sorted(set(blockers)),
        "active_user_revenue_share": 0.35,
        "simulation_review_eligible": False,
        "execution_authorized": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_untouched": True,
    }
    result["completion_sha256"] = canonical_sha256(result)
    return result
