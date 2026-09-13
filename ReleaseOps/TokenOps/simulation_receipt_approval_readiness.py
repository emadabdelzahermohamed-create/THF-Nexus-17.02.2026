#!/usr/bin/env python3
"""Fail-closed approval-readiness envelope bound to a TokenOps simulation review receipt.

This module is control-plane evidence only. It never creates transaction/instruction bytes,
never accepts or stores signatures or key material, and never signs/submits/broadcasts.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
RECEIPT_SCHEMA = "thf-tokenops-simulation-review-receipt/v1"
SCHEMA = "thf-tokenops-simulation-receipt-bound-approval-readiness/v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signatures", "signed_transaction", "raw_transaction",
    "serialized_transaction", "transaction_bytes", "instruction_bytes",
    "raw_logs", "logs", "account_data", "accounts_data", "rpc_response",
    "approver_private_key", "signer_private_key",
}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def _scan(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive/transaction field at {path}.{key}")
            _scan(item, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            _scan(item, f"{path}[{idx}]")


def _verify_receipt(receipt: Dict[str, Any]) -> str:
    _scan(receipt)
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise ValueError("unexpected simulation review receipt schema")
    if receipt.get("network") != CANONICAL_NETWORK or receipt.get("mint") != CANONICAL_MINT:
        raise ValueError("simulation review receipt target mismatch")
    digest = receipt.get("simulation_review_receipt_sha256")
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError("invalid simulation review receipt SHA-256")
    body = dict(receipt)
    body.pop("simulation_review_receipt_sha256", None)
    if canonical_sha256(body) != digest:
        raise ValueError("simulation review receipt SHA-256 mismatch")

    execution = receipt.get("execution", {})
    for key in (
        "transaction_instructions_created", "transaction_bytes_created", "transaction_created",
        "transaction_signed", "transaction_submitted", "broadcast_allowed", "execution_authorized",
        "financial_effect", "private_key_used",
    ):
        if execution.get(key) is not False:
            raise ValueError(f"unsafe simulation receipt execution flag: {key}")
    if execution.get("external_multisig_required") is not True:
        raise ValueError("external multisig requirement missing")
    if execution.get("user_controlled_approval_required") is not True:
        raise ValueError("user-controlled approval requirement missing")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation flag missing")
    return digest


def build_approval_readiness(
    simulation_receipt: Dict[str, Any],
    policy: Dict[str, Any],
    treasury_policy: Dict[str, Any],
) -> Dict[str, Any]:
    """Build deterministic approval-readiness evidence without collecting approvals/signatures."""
    for value in (policy, treasury_policy):
        _scan(value)
    receipt_sha = _verify_receipt(simulation_receipt)

    for label, value in (("policy", policy), ("treasury policy", treasury_policy)):
        if value.get("network") != CANONICAL_NETWORK or value.get("mint") != CANONICAL_MINT:
            raise ValueError(f"{label} target mismatch")

    if treasury_policy.get("control_model") != "external_multisig_required":
        raise ValueError("unexpected treasury control model")
    hard = treasury_policy.get("hard_guards", {})
    for key in (
        "seed_phrase_forbidden", "private_key_forbidden", "persistent_hot_wallet_forbidden",
        "broadcast_from_ci_forbidden", "authority_change_forbidden", "minting_forbidden",
        "third_party_balance_burn_forbidden", "wave_mawja_untouched",
    ):
        if hard.get(key) is not True:
            raise ValueError(f"required treasury hard guard missing: {key}")

    economics = policy.get("economics", {})
    if economics.get("active_user_revenue_share") != 0.35:
        raise ValueError("active-user distribution policy drift")
    if economics.get("approved_supply_floor_target_ui") != "8000000000":
        raise ValueError("approved 8B supply floor drift")

    operation = simulation_receipt.get("operation")
    approval_class = treasury_policy.get("approval_classes", {}).get(operation)
    if not isinstance(approval_class, dict) or approval_class.get("execution") != "external_multisig":
        raise ValueError("missing operation multisig class")
    threshold = int(approval_class.get("minimum_approvals", 0))
    if threshold <= 0:
        raise ValueError("invalid multisig approval threshold")

    blockers = set(str(x) for x in simulation_receipt.get("blockers", []))
    if simulation_receipt.get("simulation_review_passed") is not True:
        blockers.add("simulation_review_not_passed")
    if simulation_receipt.get("simulation_attempted") is not True:
        blockers.add("simulation_not_attempted")

    distribution = policy.get("distribution_controls", {})
    signer = policy.get("signer_policy", {})
    if distribution.get("anti_whale_cap_required") is not True:
        blockers.add("anti_whale_guard_not_required_by_policy")
    if distribution.get("per_user_cap") is None:
        blockers.add("per_user_cap_not_approved")
    if distribution.get("epoch_budget_cap") is None:
        blockers.add("epoch_budget_cap_not_approved")
    if signer.get("production_policy_status") != "approved":
        blockers.add("production_signer_policy_not_approved")

    ready = not blockers
    result = {
        "schema": SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "operation": operation,
        "amount_raw": int(simulation_receipt.get("amount_raw", 0)),
        "simulation_review_receipt_sha256": receipt_sha,
        "simulation_plan_sha256": simulation_receipt.get("simulation_plan_sha256"),
        "review_manifest_sha256": simulation_receipt.get("review_manifest_sha256"),
        "policy_sha256": canonical_sha256(policy),
        "treasury_policy_sha256": canonical_sha256(treasury_policy),
        "required_external_multisig_approvals": threshold,
        "approval_readiness": ready,
        "blockers": sorted(blockers),
        "approval_collection": {
            "approver_identities_collected": False,
            "approvals_collected": 0,
            "signatures_collected": 0,
            "signature_material_allowed": False,
            "external_multisig_required": True,
            "user_controlled_approval_required": True,
        },
        "exact_remaining_signer_action": (
            f"user_controlled_approval_then_collect_{threshold}_external_multisig_approvals_offline_before_any_signing"
            if ready else "none_until_fail_closed_blockers_are_resolved"
        ),
        "execution": {
            "transaction_instructions_created": False,
            "transaction_bytes_created": False,
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "execution_authorized": False,
            "financial_effect": False,
            "private_key_used": False,
            "external_multisig_required": True,
            "user_controlled_approval_required": True,
            "wave_mawja_untouched": True,
        },
    }
    result["approval_readiness_sha256"] = canonical_sha256(result)
    return result
