#!/usr/bin/env python3
"""Fail-closed binding of accounting policy/source seal into unsigned admission.

Review/control-plane evidence only. This module never constructs, signs, submits,
broadcasts, transfers, burns, settles, migrates treasury balances, changes
authorities, or executes DAO decisions.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
GATE_SCHEMA = "thf-tokenops-accounting-policy-seal-bound-admission/v1"
EXPECTED_BASE_GATE = "THF_TOKENOPS_POLICY_COMPLETION_BOUND_UNSIGNED_ADMISSION_V1"
EXPECTED_SEAL_SCHEMA = "thf-tokenops-accounting-policy-source-seal/v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
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


def _hex64(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def _hex40(value: Any, label: str) -> str:
    if not isinstance(value, str) or not HEX40.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def _verify_safe_execution_flags(document: Dict[str, Any], label: str) -> None:
    execution = document.get("execution", document)
    for key in (
        "transaction_created", "transaction_signed", "transaction_submitted",
        "broadcast_allowed", "financial_effect", "settlement_executed",
        "burn_executed", "treasury_migrated", "dao_decision_executed",
        "private_key_used",
    ):
        if key in execution and execution.get(key) is not False:
            raise ValueError(f"unsafe {label} execution flag: {key}")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError(f"{label} WAVE isolation flag is not preserved")


def evaluate_accounting_policy_seal_bound_admission(
    base_admission: Dict[str, Any],
    accounting_seal: Dict[str, Any],
    review_request: Dict[str, Any],
) -> Dict[str, Any]:
    """Bind one unsigned admission to one immutable accounting policy seal.

    The result is evidence-only and can never authorize execution. A seal that
    is not independently review-eligible propagates its blockers and keeps the
    resulting review fail-closed.
    """
    for value in (base_admission, accounting_seal, review_request):
        _scan(value)

    for document, label in (
        (base_admission, "base admission"),
        (accounting_seal, "accounting seal"),
        (review_request, "review request"),
    ):
        if document.get("network") != CANONICAL_NETWORK or document.get("mint") != CANONICAL_MINT:
            raise ValueError(f"{label} target mismatch")

    if base_admission.get("gate") != EXPECTED_BASE_GATE:
        raise ValueError("unexpected base admission gate")
    base_sha = _hex64(base_admission.get("bound_admission_sha256"), "base admission SHA-256")
    base_body = dict(base_admission)
    base_body.pop("bound_admission_sha256", None)
    if canonical_sha256(base_body) != base_sha:
        raise ValueError("base admission SHA-256 mismatch")
    _verify_safe_execution_flags(base_admission, "base admission")

    if accounting_seal.get("schema") != EXPECTED_SEAL_SCHEMA:
        raise ValueError("unexpected accounting seal schema")
    seal_sha = _hex64(accounting_seal.get("accounting_policy_seal_sha256"), "accounting policy seal SHA-256")
    seal_body = dict(accounting_seal)
    seal_body.pop("accounting_policy_seal_sha256", None)
    if canonical_sha256(seal_body) != seal_sha:
        raise ValueError("accounting policy seal SHA-256 mismatch")
    _verify_safe_execution_flags(accounting_seal, "accounting seal")

    requested_seal_sha = _hex64(review_request.get("accounting_policy_seal_sha256"), "requested accounting policy seal SHA-256")
    if requested_seal_sha != seal_sha:
        raise ValueError("review request is detached from accounting policy seal")
    requested_base_sha = _hex64(review_request.get("base_bound_admission_sha256"), "requested base admission SHA-256")
    if requested_base_sha != base_sha:
        raise ValueError("review request is detached from base admission")

    source = accounting_seal.get("policy_source", {})
    request_source = review_request.get("policy_source", {})
    for key in (
        "policy_file_sha256", "treasury_policy_file_sha256", "lineage_source_sha256",
    ):
        expected = _hex64(source.get(key), f"seal {key}")
        actual = _hex64(request_source.get(key), f"request {key}")
        if actual != expected:
            raise ValueError(f"policy/source replay mismatch: {key}")
    for key in ("policy_git_blob_sha", "treasury_policy_git_blob_sha", "source_commit_sha"):
        expected = _hex40(source.get(key), f"seal {key}")
        actual = _hex40(request_source.get(key), f"request {key}")
        if actual != expected:
            raise ValueError(f"policy/source replay mismatch: {key}")

    blockers = set(str(x) for x in base_admission.get("blockers", []))
    blockers |= set(str(x) for x in accounting_seal.get("blockers", []))
    if accounting_seal.get("seal_review_eligible") is not True:
        blockers.add("accounting_policy_seal_not_review_eligible")
    if base_admission.get("simulation_review_eligible") is not True:
        blockers.add("base_unsigned_admission_not_review_eligible")

    review_eligible = (
        accounting_seal.get("seal_review_eligible") is True
        and base_admission.get("simulation_review_eligible") is True
        and len(blockers) == 0
    )

    result = {
        "schema": GATE_SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "review_request_id": str(review_request.get("review_request_id", "")),
        "accounting_policy_seal_sha256": seal_sha,
        "base_bound_admission_sha256": base_sha,
        "lineage_checkpoint_sha256": accounting_seal.get("lineage_checkpoint_sha256"),
        "policy_source": dict(source),
        "simulation_review_eligible": review_eligible,
        "blockers": sorted(blockers),
        "execution": {
            "simulation_execution_permitted": False,
            "execution_authorized": False,
            "transaction_created": False,
            "transaction_signed": False,
            "transaction_submitted": False,
            "broadcast_allowed": False,
            "financial_effect": False,
            "settlement_executed": False,
            "burn_executed": False,
            "treasury_migrated": False,
            "dao_decision_executed": False,
            "private_key_used": False,
            "external_multisig_required": True,
            "user_controlled_approval_required": True,
            "wave_mawja_untouched": True,
        },
    }
    result["seal_bound_admission_sha256"] = canonical_sha256(result)
    return result
