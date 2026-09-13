#!/usr/bin/env python3
"""Fail-closed admission gate for THF unsigned simulation plans.

This module never signs, submits, broadcasts, or mutates Solana state. It only
checks whether an offline unsigned planning manifest is eligible for simulation
review under an exact provenance digest and policy snapshot.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
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


def evaluate_unsigned_simulation_admission(
    provenance: Dict[str, Any],
    plan: Dict[str, Any],
    snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    _scan(provenance)
    _scan(plan)
    _scan(snapshot)

    if snapshot.get("network") != CANONICAL_NETWORK or snapshot.get("mint") != CANONICAL_MINT:
        raise ValueError("non-canonical network or mint")
    if plan.get("network") != CANONICAL_NETWORK or plan.get("mint") != CANONICAL_MINT:
        raise ValueError("plan target mismatch")

    provenance_sha = plan.get("unified_review_provenance_sha256")
    if not isinstance(provenance_sha, str) or not HEX64.fullmatch(provenance_sha):
        raise ValueError("invalid unified review provenance digest")
    if provenance_sha != canonical_sha256(provenance):
        raise ValueError("unified review provenance digest mismatch")

    snapshot_sha = plan.get("policy_snapshot_sha256")
    if not isinstance(snapshot_sha, str) or not HEX64.fullmatch(snapshot_sha):
        raise ValueError("invalid policy snapshot digest")
    if snapshot_sha != canonical_sha256(snapshot):
        raise ValueError("policy snapshot digest mismatch")

    safety = snapshot.get("safety", {})
    if any(bool(safety.get(k)) for k in (
        "production_signer_policy_approved", "simulation_execution_permitted",
        "execution_authorized", "transaction_signing", "transaction_broadcast"
    )):
        raise ValueError("unsafe policy snapshot")
    if safety.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation not asserted")

    economics = snapshot.get("economics", {})
    if economics.get("active_user_revenue_share") != 0.35:
        raise ValueError("active-user revenue share must remain exactly 35%")
    if str(economics.get("approved_supply_floor_target_ui")) != "8000000000":
        raise ValueError("approved supply floor mismatch")

    controls = snapshot.get("distribution_controls", {})
    blockers = []
    if controls.get("anti_whale_cap_required") is not True:
        raise ValueError("anti-whale requirement removed")
    if controls.get("per_user_cap") is None or controls.get("epoch_budget_cap") is None:
        blockers.append("anti_whale_caps_not_authoritatively_configured")
    if controls.get("production_caps_configured") is not True:
        blockers.append("production_caps_not_approved")

    if plan.get("unsigned") is not True:
        raise ValueError("plan must be explicitly unsigned")
    if any(bool(plan.get(k)) for k in ("sign", "submit", "broadcast", "financial_effect")):
        raise ValueError("execution capability requested")

    intent = plan.get("intent")
    if intent not in {"reward_epoch", "vesting_settlement", "burn_plan", "treasury_transfer_plan"}:
        raise ValueError("unsupported planning intent")

    if intent == "reward_epoch" and plan.get("active_user_revenue_share") != 0.35:
        raise ValueError("reward plan must bind exact 35% share")

    if intent == "burn_plan":
        current_supply = int(str(plan.get("current_supply_ui")))
        planned_burn = int(str(plan.get("planned_burn_ui")))
        floor = int(str(economics["approved_supply_floor_target_ui"]))
        if planned_burn < 0 or current_supply - planned_burn < floor:
            raise ValueError("burn plan would violate approved 8B supply floor")
        if plan.get("burn_source_policy") != "treasury_controlled_balances_only":
            raise ValueError("burn source policy mismatch")

    eligible = not blockers
    result = {
        "gate": "THF_TOKENOPS_UNSIGNED_SIMULATION_ADMISSION_V1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": intent,
        "unified_review_provenance_sha256": provenance_sha,
        "policy_snapshot_sha256": snapshot_sha,
        "simulation_review_eligible": eligible,
        "blockers": sorted(set(blockers)),
        "simulation_execution_permitted": False,
        "execution_authorized": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_untouched": True,
    }
    result["admission_sha256"] = canonical_sha256(result)
    return result
