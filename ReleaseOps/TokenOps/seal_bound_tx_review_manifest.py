#!/usr/bin/env python3
"""Deterministic, fail-closed transaction *review* manifest bound to TokenOps accounting admission.

This module is control-plane/accounting evidence only. It never constructs Solana
instructions or transaction bytes, never signs, submits, broadcasts, transfers,
burns, settles vesting/rewards, migrates treasury balances, or executes DAO decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
SCHEMA = "thf-tokenops-seal-bound-unsigned-tx-review-manifest/v1"
ADMISSION_SCHEMA = "thf-tokenops-accounting-policy-seal-bound-admission/v1"
ALLOWED = {"reward_epoch", "vesting_settlement", "burn", "treasury_transfer"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
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


def _hex(value: Any, label: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def _verify_admission(admission: Dict[str, Any]) -> str:
    _scan(admission)
    if admission.get("schema") != ADMISSION_SCHEMA:
        raise ValueError("unexpected admission schema")
    if admission.get("network") != CANONICAL_NETWORK or admission.get("mint") != CANONICAL_MINT:
        raise ValueError("admission target mismatch")
    digest = _hex(admission.get("seal_bound_admission_sha256"), "seal-bound admission SHA-256", HEX64)
    body = dict(admission)
    body.pop("seal_bound_admission_sha256", None)
    if canonical_sha256(body) != digest:
        raise ValueError("seal-bound admission SHA-256 mismatch")
    execution = admission.get("execution", {})
    for key in (
        "simulation_execution_permitted", "execution_authorized", "transaction_created",
        "transaction_signed", "transaction_submitted", "broadcast_allowed", "financial_effect",
        "settlement_executed", "burn_executed", "treasury_migrated", "dao_decision_executed",
        "private_key_used",
    ):
        if execution.get(key) is not False:
            raise ValueError(f"unsafe admission execution flag: {key}")
    if execution.get("external_multisig_required") is not True or execution.get("user_controlled_approval_required") is not True:
        raise ValueError("admission does not preserve external approval controls")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation flag is not preserved")
    return digest


def build_review_manifest(admission: Dict[str, Any], request: Dict[str, Any], treasury_policy: Dict[str, Any]) -> Dict[str, Any]:
    """Build deterministic evidence for human/multisig review without creating a transaction."""
    for value in (request, treasury_policy):
        _scan(value)
    admission_sha = _verify_admission(admission)

    if request.get("network") != CANONICAL_NETWORK or request.get("mint") != CANONICAL_MINT:
        raise ValueError("request target mismatch")
    if treasury_policy.get("network") != CANONICAL_NETWORK or treasury_policy.get("mint") != CANONICAL_MINT:
        raise ValueError("treasury policy target mismatch")
    if treasury_policy.get("control_model") != "external_multisig_required":
        raise ValueError("unexpected treasury control model")

    operation = str(request.get("operation", ""))
    if operation not in ALLOWED:
        raise ValueError("unsupported operation")
    approval_class = treasury_policy.get("approval_classes", {}).get(operation)
    if not isinstance(approval_class, dict) or approval_class.get("execution") != "external_multisig":
        raise ValueError("missing external multisig approval class")
    required_approvals = int(approval_class.get("minimum_approvals", 0))
    if required_approvals <= 0:
        raise ValueError("invalid approval threshold")
    if int(request.get("required_approvals", -1)) != required_approvals:
        raise ValueError("approval threshold mismatch")

    request_admission_sha = _hex(request.get("seal_bound_admission_sha256"), "requested admission SHA-256", HEX64)
    if request_admission_sha != admission_sha:
        raise ValueError("request is detached from seal-bound admission")

    source = admission.get("policy_source", {})
    request_source = request.get("policy_source", {})
    for key in ("policy_file_sha256", "treasury_policy_file_sha256", "lineage_source_sha256"):
        expected = _hex(source.get(key), f"admission {key}", HEX64)
        actual = _hex(request_source.get(key), f"request {key}", HEX64)
        if actual != expected:
            raise ValueError(f"policy/source replay mismatch: {key}")
    for key in ("policy_git_blob_sha", "treasury_policy_git_blob_sha", "source_commit_sha"):
        expected = _hex(source.get(key), f"admission {key}", HEX40)
        actual = _hex(request_source.get(key), f"request {key}", HEX40)
        if actual != expected:
            raise ValueError(f"policy/source replay mismatch: {key}")

    amount_raw = int(request.get("amount_raw", 0))
    if amount_raw <= 0:
        raise ValueError("amount_raw must be positive")
    if operation == "burn":
        current_supply_raw = int(request.get("current_supply_raw", 0))
        floor_raw = int(request.get("supply_floor_raw", 0))
        if floor_raw != 800000000000000000:
            raise ValueError("burn supply floor must match approved 8B target")
        if current_supply_raw - amount_raw < floor_raw:
            raise ValueError("burn would cross approved 8B supply floor")
        if request.get("source_control") != "treasury_verified":
            raise ValueError("burn source is not verified treasury")

    admission_blockers = sorted(set(str(x) for x in admission.get("blockers", [])))
    review_ready = admission.get("simulation_review_eligible") is True and not admission_blockers
    blockers = list(admission_blockers)
    if not review_ready and "seal_bound_admission_not_review_eligible" not in blockers:
        blockers.append("seal_bound_admission_not_review_eligible")
    blockers = sorted(set(blockers))

    if review_ready:
        exact_signer_action = (
            f"After separate user-controlled approval, obtain at least {required_approvals} external multisig approvals "
            "and independently reproduce/simulate the intended transaction outside CI; this manifest is not signable."
        )
    else:
        exact_signer_action = "none_until_fail_closed_blockers_are_resolved"

    result = {
        "schema": SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "request_id": str(request.get("request_id", "")),
        "operation": operation,
        "amount_raw": amount_raw,
        "intent": request.get("intent", {}),
        "seal_bound_admission_sha256": admission_sha,
        "accounting_policy_seal_sha256": admission.get("accounting_policy_seal_sha256"),
        "base_bound_admission_sha256": admission.get("base_bound_admission_sha256"),
        "lineage_checkpoint_sha256": admission.get("lineage_checkpoint_sha256"),
        "policy_source": dict(source),
        "required_external_multisig_approvals": required_approvals,
        "review_ready": review_ready,
        "blockers": blockers,
        "exact_remaining_signer_action": exact_signer_action,
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
    result["review_manifest_sha256"] = canonical_sha256(result)
    return result
