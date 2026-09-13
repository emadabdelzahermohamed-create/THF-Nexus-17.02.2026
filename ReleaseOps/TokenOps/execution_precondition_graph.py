#!/usr/bin/env python3
"""THF TokenOps execution-precondition graph.

Pure planning/evidence compiler. It never creates transaction/instruction bytes,
collects approvals/signatures, signs, submits, broadcasts, or mutates on-chain state.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Mapping, Optional

NETWORK = "solana-mainnet-beta"
MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
DECIMALS = 8
SUPPLY_FLOOR_UI = 8_000_000_000
SHARE_BPS = 3500
SCHEMA = "thf-tokenops-execution-precondition-graph/v1"

FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signatures", "signed_transaction", "serialized_transaction",
    "raw_transaction", "transaction_bytes", "instruction_bytes", "raw_instruction",
    "service_account_key", "access_token", "refresh_token",
}
FINAL_DELIVERY_VALUES = {"claim", "push", "hybrid"}
INTENT_CLASSES = ("reward_epoch", "vesting_settlement", "burn", "treasury_transfer")


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _scan(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELDS:
                raise ValueError(f"forbidden sensitive/execution field at {path}.{key}")
            _scan(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan(item, f"{path}[{index}]")


def _hash_ok(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _evidence_ok(evidence: Mapping[str, Any], key: str) -> bool:
    item = evidence.get(key)
    return isinstance(item, Mapping) and item.get("status") == "verified" and _hash_ok(item.get("sha256"))


def _base_invariant_blockers(policy: Mapping[str, Any], audit: Mapping[str, Any]) -> List[str]:
    blockers: List[str] = []
    verified = policy.get("verified", {})
    if policy.get("network") != NETWORK or audit.get("network") != NETWORK:
        blockers.append("network_drift")
    if policy.get("mint") != MINT or audit.get("mint") != MINT:
        blockers.append("mint_drift")
    expected_program = verified.get("token_program", TOKEN_PROGRAM)
    if audit.get("program_id") != expected_program or expected_program != TOKEN_PROGRAM:
        blockers.append("token_program_drift")
    if audit.get("decimals") != DECIMALS or verified.get("decimals") != DECIMALS:
        blockers.append("decimals_drift")
    if audit.get("mint_authority") is not None:
        blockers.append("mint_authority_reappeared")
    if audit.get("freeze_authority") is not None:
        blockers.append("freeze_authority_reappeared")
    try:
        supply_raw = int(audit.get("supply_raw"))
    except Exception:
        blockers.append("invalid_supply")
    else:
        if supply_raw < SUPPLY_FLOOR_UI * (10 ** DECIMALS):
            blockers.append("supply_below_approved_8b_floor")
    economics = policy.get("economics", {})
    if economics.get("active_user_revenue_share") != 0.35:
        blockers.append("approved_35_percent_share_drift")
    if economics.get("approved_supply_floor_target_ui") != "8000000000":
        blockers.append("approved_8b_target_drift")
    if economics.get("burn_source_policy") != "treasury_controlled_balances_only":
        blockers.append("burn_source_policy_drift")
    if economics.get("minting_assumption") != "disabled_immutable":
        blockers.append("minting_assumption_drift")
    return sorted(set(blockers))


def _policy_blockers(policy: Mapping[str, Any], intent: str) -> List[str]:
    d = policy.get("distribution_controls", {})
    signer = policy.get("signer_policy", {})
    blockers: List[str] = []
    if signer.get("production_policy_status") != "approved":
        blockers.append("production_signer_policy_not_approved")
    if intent == "reward_epoch":
        if d.get("per_user_cap") is None:
            blockers.append("per_user_cap_not_approved")
        if d.get("epoch_budget_cap") is None:
            blockers.append("epoch_budget_cap_not_approved")
        if d.get("claim_or_push_model") not in FINAL_DELIVERY_VALUES:
            blockers.append("reward_delivery_model_not_approved")
        if d.get("anti_sybil_required") is not True:
            blockers.append("anti_sybil_requirement_missing")
        if d.get("activity_evidence_required") is not True:
            blockers.append("activity_evidence_requirement_missing")
        if d.get("anti_whale_cap_required") is not True:
            blockers.append("anti_whale_requirement_missing")
    return blockers


def _required_evidence(intent: str) -> List[str]:
    common = ["mainnet_audit", "policy_snapshot", "treasury_policy_snapshot", "simulation_receipt"]
    return {
        "reward_epoch": common + ["activity_eligibility", "anti_sybil_review", "distribution_reserve", "allocation_accounting", "governance_authority"],
        "vesting_settlement": common + ["vesting_terms", "vesting_liability", "vesting_reserve", "governance_authority"],
        "burn": common + ["treasury_ownership", "treasury_balance", "burn_reserve", "governance_authority"],
        "treasury_transfer": common + ["treasury_ownership", "treasury_balance", "destination_review", "governance_authority"],
    }[intent]


def compile_precondition_graph(policy: Dict[str, Any], treasury_policy: Dict[str, Any], audit: Dict[str, Any], evidence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compile deterministic, fail-closed intent readiness from public/hash-only inputs."""
    evidence = evidence or {}
    for obj in (policy, treasury_policy, audit, evidence):
        _scan(obj)
    if treasury_policy.get("network") != NETWORK or treasury_policy.get("mint") != MINT:
        raise ValueError("treasury policy target mismatch")
    if treasury_policy.get("control_model") != "external_multisig_required":
        raise ValueError("external multisig control model is required")

    hard = treasury_policy.get("hard_guards", {})
    mandatory_hard_guards = (
        "seed_phrase_forbidden", "private_key_forbidden", "persistent_hot_wallet_forbidden",
        "broadcast_from_ci_forbidden", "authority_change_forbidden", "minting_forbidden",
        "third_party_balance_burn_forbidden", "wave_mawja_untouched",
    )
    missing_hard_guards = [name for name in mandatory_hard_guards if hard.get(name) is not True]
    global_blockers = _base_invariant_blockers(policy, audit)
    if missing_hard_guards:
        global_blockers += [f"hard_guard_not_asserted:{name}" for name in missing_hard_guards]

    classes = treasury_policy.get("approval_classes", {})
    intents: Dict[str, Any] = {}
    for intent in INTENT_CLASSES:
        threshold = classes.get(intent, {}).get("minimum_approvals")
        blockers = list(global_blockers) + _policy_blockers(policy, intent)
        if not isinstance(threshold, int) or threshold <= 0:
            blockers.append("approval_threshold_missing")
        if classes.get(intent, {}).get("execution") != "external_multisig":
            blockers.append("external_multisig_not_required")
        required = _required_evidence(intent)
        missing = [name for name in required if not _evidence_ok(evidence, name)]
        blockers += [f"missing_verified_evidence:{name}" for name in missing]
        if intent == "burn":
            if classes.get("burn", {}).get("supply_floor_ui") != "8000000000":
                blockers.append("burn_class_8b_floor_drift")
            burn_reserve = evidence.get("burn_reserve", {})
            if burn_reserve.get("status") == "verified":
                try:
                    amount_int = int(burn_reserve.get("amount_raw"))
                    supply_raw = int(audit.get("supply_raw"))
                except Exception:
                    blockers.append("burn_reserve_amount_invalid")
                else:
                    max_headroom = max(0, supply_raw - SUPPLY_FLOOR_UI * (10 ** DECIMALS))
                    if amount_int < 0 or amount_int > max_headroom:
                        blockers.append("burn_reserve_exceeds_8b_floor_headroom")
        blockers = sorted(set(blockers))
        intents[intent] = {
            "minimum_external_multisig_approvals": threshold,
            "required_evidence": required,
            "verified_evidence": sorted(name for name in required if _evidence_ok(evidence, name)),
            "blockers": blockers,
            "unsigned_review_ready": not blockers,
            "external_signer_handoff_ready": False,
            "execution_authorized": False,
            "broadcast_allowed": False,
            "financial_effect": False,
        }

    supply_raw = int(audit.get("supply_raw", 0)) if str(audit.get("supply_raw", "")).isdigit() else None
    theoretical_burn_headroom_raw = max(0, supply_raw - SUPPLY_FLOOR_UI * (10 ** DECIMALS)) if supply_raw is not None else None
    result = {
        "schema": SCHEMA, "network": NETWORK, "mint": MINT,
        "policy_sha256": sha256(policy), "treasury_policy_sha256": sha256(treasury_policy),
        "audit_sha256": sha256(audit), "evidence_index_sha256": sha256(evidence),
        "approved_economics": {"active_user_revenue_share_bps": SHARE_BPS, "supply_floor_target_ui": str(SUPPLY_FLOOR_UI), "theoretical_burn_headroom_raw": theoretical_burn_headroom_raw},
        "global_blockers": sorted(set(global_blockers)), "intents": intents,
        "exact_remaining_signer_action": "none_until_fail_closed_blockers_are_resolved" if any(v["blockers"] for v in intents.values()) else "user_controlled_approval_and_external_multisig_handoff_still_required",
        "safety": {"accepts_private_key_material": False, "creates_transaction_bytes": False, "creates_instruction_bytes": False, "collects_signatures": False, "signs": False, "submits": False, "broadcasts": False, "mutates_authorities": False, "financial_effect": False, "wave_mawja_untouched": True},
    }
    result["precondition_graph_sha256"] = sha256(result)
    return result
