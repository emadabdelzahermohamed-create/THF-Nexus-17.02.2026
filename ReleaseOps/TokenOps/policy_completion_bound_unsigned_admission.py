#!/usr/bin/env python3
"""Bind authoritative policy-completion evidence into unsigned simulation admission.

This module is review-only. It never signs, submits, broadcasts, transfers,
burns, changes authorities, settles rewards/vesting, or mutates Solana state.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

from anti_whale_reward_policy_completion_gate import evaluate_policy_completion
from unsigned_simulation_admission_gate import evaluate_unsigned_simulation_admission

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


def evaluate_policy_completion_bound_admission(
    completion: Dict[str, Any],
    authoritative_policy: Dict[str, Any],
    treasury_policy: Dict[str, Any],
    provenance: Dict[str, Any],
    plan: Dict[str, Any],
    snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    for value in (completion, authoritative_policy, treasury_policy, provenance, plan, snapshot):
        _scan(value)

    for document, label in ((completion, "completion"), (snapshot, "snapshot"), (plan, "plan")):
        if document.get("network") != CANONICAL_NETWORK or document.get("mint") != CANONICAL_MINT:
            raise ValueError(f"{label} target mismatch")

    completion_result = evaluate_policy_completion(completion, authoritative_policy, treasury_policy)
    completion_sha = plan.get("policy_completion_evidence_sha256")
    if not isinstance(completion_sha, str) or not HEX64.fullmatch(completion_sha):
        raise ValueError("invalid policy-completion evidence SHA-256")
    if completion_sha != completion_result.get("completion_sha256"):
        raise ValueError("policy-completion evidence SHA-256 mismatch")

    # Bind the admission snapshot to the exact repository policy blobs used by
    # the completion evidence. This prevents a valid completion receipt from
    # being replayed against a different policy snapshot.
    for completion_field, snapshot_field in (
        ("authoritative_policy_blob_sha", "authoritative_policy_blob_sha"),
        ("treasury_policy_blob_sha", "treasury_policy_blob_sha"),
    ):
        value = completion.get(completion_field)
        if not isinstance(value, str) or not HEX40.fullmatch(value):
            raise ValueError(f"invalid completion Git blob binding: {completion_field}")
        if snapshot.get(snapshot_field) != value:
            raise ValueError(f"snapshot/completion blob mismatch: {snapshot_field}")

    base = evaluate_unsigned_simulation_admission(provenance, plan, snapshot)
    blockers = list(base.get("blockers", []))
    if completion_result.get("authoritatively_completed") is not True:
        blockers.append("policy_completion_not_authoritatively_completed")
        blockers.extend(f"policy_completion:{item}" for item in completion_result.get("blockers", []))

    eligible = bool(base.get("simulation_review_eligible")) and completion_result.get("authoritatively_completed") is True
    result = {
        "gate": "THF_TOKENOPS_POLICY_COMPLETION_BOUND_UNSIGNED_ADMISSION_V1",
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "intent": base.get("intent"),
        "policy_completion_evidence_sha256": completion_sha,
        "base_admission_sha256": base.get("admission_sha256"),
        "authoritative_policy_sha256": completion_result.get("authoritative_policy_sha256"),
        "treasury_policy_sha256": completion_result.get("treasury_policy_sha256"),
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
    result["bound_admission_sha256"] = canonical_sha256(result)
    return result
