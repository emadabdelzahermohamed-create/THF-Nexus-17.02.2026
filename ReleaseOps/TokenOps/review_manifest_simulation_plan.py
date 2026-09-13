#!/usr/bin/env python3
"""Deterministic fail-closed simulation *plan* bound to a TokenOps review manifest.

Control-plane evidence only. This module never creates Solana instructions or transaction
bytes, never signs/submits/broadcasts, and never performs financial/token actions.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
SCHEMA = "thf-tokenops-review-manifest-bound-simulation-plan/v1"
REVIEW_SCHEMA = "thf-tokenops-seal-bound-unsigned-tx-review-manifest/v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
    "transaction_bytes", "instruction_bytes",
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


def _verify_review_manifest(manifest: Dict[str, Any]) -> str:
    _scan(manifest)
    if manifest.get("schema") != REVIEW_SCHEMA:
        raise ValueError("unexpected review manifest schema")
    if manifest.get("network") != CANONICAL_NETWORK or manifest.get("mint") != CANONICAL_MINT:
        raise ValueError("review manifest target mismatch")
    digest = manifest.get("review_manifest_sha256")
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError("invalid review manifest SHA-256")
    body = dict(manifest)
    body.pop("review_manifest_sha256", None)
    if canonical_sha256(body) != digest:
        raise ValueError("review manifest SHA-256 mismatch")
    execution = manifest.get("execution", {})
    for key in (
        "transaction_instructions_created", "transaction_bytes_created", "transaction_created",
        "transaction_signed", "transaction_submitted", "broadcast_allowed", "execution_authorized",
        "financial_effect", "private_key_used",
    ):
        if execution.get(key) is not False:
            raise ValueError(f"unsafe review manifest flag: {key}")
    if execution.get("external_multisig_required") is not True:
        raise ValueError("external multisig requirement missing")
    if execution.get("user_controlled_approval_required") is not True:
        raise ValueError("user-controlled approval requirement missing")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation flag missing")
    return digest


def build_simulation_plan(
    review_manifest: Dict[str, Any], policy: Dict[str, Any], treasury_policy: Dict[str, Any]
) -> Dict[str, Any]:
    """Build non-executable simulation intent evidence; fail closed on incomplete policy."""
    for value in (policy, treasury_policy):
        _scan(value)
    manifest_sha = _verify_review_manifest(review_manifest)

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

    operation = review_manifest.get("operation")
    approval = treasury_policy.get("approval_classes", {}).get(operation)
    if not isinstance(approval, dict) or approval.get("execution") != "external_multisig":
        raise ValueError("missing operation multisig class")
    if int(approval.get("minimum_approvals", 0)) != int(review_manifest.get("required_external_multisig_approvals", -1)):
        raise ValueError("review manifest approval threshold drift")

    blockers = set(str(x) for x in review_manifest.get("blockers", []))
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
    if review_manifest.get("review_ready") is not True:
        blockers.add("review_manifest_not_ready")

    simulation_eligible = not blockers
    exact_action = (
        "user_controlled_approval_then_external_multisig_simulation_review"
        if simulation_eligible else "none_until_fail_closed_blockers_are_resolved"
    )

    result = {
        "schema": SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "operation": operation,
        "amount_raw": int(review_manifest.get("amount_raw", 0)),
        "review_manifest_sha256": manifest_sha,
        "seal_bound_admission_sha256": review_manifest.get("seal_bound_admission_sha256"),
        "accounting_policy_seal_sha256": review_manifest.get("accounting_policy_seal_sha256"),
        "lineage_checkpoint_sha256": review_manifest.get("lineage_checkpoint_sha256"),
        "required_external_multisig_approvals": int(review_manifest.get("required_external_multisig_approvals", 0)),
        "policy_sha256": canonical_sha256(policy),
        "treasury_policy_sha256": canonical_sha256(treasury_policy),
        "simulation_eligible": simulation_eligible,
        "blockers": sorted(blockers),
        "exact_remaining_signer_action": exact_action,
        "simulation_intent": {
            "mode": "non_executable_review_only",
            "construct_solana_instructions": False,
            "construct_transaction_bytes": False,
            "rpc_simulation_submitted": False,
        },
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
    result["simulation_plan_sha256"] = canonical_sha256(result)
    return result
