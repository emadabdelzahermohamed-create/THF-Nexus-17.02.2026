#!/usr/bin/env python3
"""Fail-closed, hash-only review receipt for TokenOps simulation outcomes.

This module consumes an already-built simulation plan and an optional *sanitized*
simulation summary. It never accepts transaction/instruction bytes, signatures, keys,
or raw RPC logs; it never calls RPC, signs, submits, broadcasts, or changes token state.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Optional

CANONICAL_MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
CANONICAL_NETWORK = "solana-mainnet-beta"
PLAN_SCHEMA = "thf-tokenops-review-manifest-bound-simulation-plan/v1"
SCHEMA = "thf-tokenops-simulation-review-receipt/v1"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signatures", "signed_transaction", "raw_transaction",
    "serialized_transaction", "transaction_bytes", "instruction_bytes",
    "raw_logs", "logs", "account_data", "accounts_data", "rpc_response",
}
ALLOWED_COMMITMENTS = {"processed", "confirmed", "finalized"}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(payload).hexdigest()


def _scan(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden sensitive/raw simulation field at {path}.{key}")
            _scan(item, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            _scan(item, f"{path}[{idx}]")


def _verify_plan(plan: Dict[str, Any]) -> str:
    _scan(plan)
    if plan.get("schema") != PLAN_SCHEMA:
        raise ValueError("unexpected simulation plan schema")
    if plan.get("network") != CANONICAL_NETWORK or plan.get("mint") != CANONICAL_MINT:
        raise ValueError("simulation plan target mismatch")
    digest = plan.get("simulation_plan_sha256")
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise ValueError("invalid simulation plan SHA-256")
    body = dict(plan)
    body.pop("simulation_plan_sha256", None)
    if canonical_sha256(body) != digest:
        raise ValueError("simulation plan SHA-256 mismatch")

    intent = plan.get("simulation_intent", {})
    for key in ("construct_solana_instructions", "construct_transaction_bytes", "rpc_simulation_submitted"):
        if intent.get(key) is not False:
            raise ValueError(f"unsafe simulation plan intent: {key}")
    execution = plan.get("execution", {})
    for key in (
        "transaction_instructions_created", "transaction_bytes_created", "transaction_created",
        "transaction_signed", "transaction_submitted", "broadcast_allowed", "execution_authorized",
        "financial_effect", "private_key_used",
    ):
        if execution.get(key) is not False:
            raise ValueError(f"unsafe simulation plan execution flag: {key}")
    if execution.get("external_multisig_required") is not True:
        raise ValueError("external multisig requirement missing")
    if execution.get("user_controlled_approval_required") is not True:
        raise ValueError("user-controlled approval requirement missing")
    if execution.get("wave_mawja_untouched") is not True:
        raise ValueError("WAVE isolation flag missing")
    return digest


def _verify_summary(summary: Dict[str, Any]) -> None:
    _scan(summary)
    allowed = {
        "source", "slot", "commitment", "ok", "err_code", "units_consumed",
        "logs_sha256", "accounts_data_sha256", "return_data_sha256",
    }
    unknown = set(summary) - allowed
    if unknown:
        raise ValueError(f"unexpected sanitized simulation fields: {sorted(unknown)}")
    if summary.get("source") != "sanitized_external_simulation_summary":
        raise ValueError("unexpected simulation summary source")
    if not isinstance(summary.get("slot"), int) or summary["slot"] <= 0:
        raise ValueError("invalid simulation slot")
    if summary.get("commitment") not in ALLOWED_COMMITMENTS:
        raise ValueError("invalid simulation commitment")
    if not isinstance(summary.get("ok"), bool):
        raise ValueError("simulation ok must be boolean")
    err_code = summary.get("err_code")
    if err_code is not None and (not isinstance(err_code, str) or not err_code.strip()):
        raise ValueError("invalid simulation err_code")
    units = summary.get("units_consumed")
    if units is not None and (not isinstance(units, int) or units < 0):
        raise ValueError("invalid units_consumed")
    for key in ("logs_sha256", "accounts_data_sha256", "return_data_sha256"):
        value = summary.get(key)
        if value is not None and (not isinstance(value, str) or not HEX64.fullmatch(value)):
            raise ValueError(f"invalid {key}")
    if summary["ok"] and err_code is not None:
        raise ValueError("successful simulation cannot carry err_code")
    if not summary["ok"] and err_code is None:
        raise ValueError("failed simulation requires err_code")


def build_simulation_review_receipt(
    simulation_plan: Dict[str, Any],
    sanitized_summary: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Bind a safe simulation plan to a sanitized outcome or a fail-closed not-run receipt."""
    plan_sha = _verify_plan(simulation_plan)
    blockers = sorted(set(str(x) for x in simulation_plan.get("blockers", [])))
    eligible = simulation_plan.get("simulation_eligible") is True and not blockers

    if not eligible:
        if sanitized_summary is not None:
            raise ValueError("simulation summary forbidden while plan is fail-closed/ineligible")
        attempted = False
        passed = False
        outcome = "not_run_fail_closed"
        summary_sha = None
        slot = None
        commitment = None
        err_code = None
        units = None
    else:
        if sanitized_summary is None:
            raise ValueError("eligible simulation plan requires sanitized simulation summary")
        _verify_summary(sanitized_summary)
        attempted = True
        passed = sanitized_summary["ok"] is True
        outcome = "simulation_passed_review_only" if passed else "simulation_failed_review_only"
        summary_sha = canonical_sha256(sanitized_summary)
        slot = sanitized_summary["slot"]
        commitment = sanitized_summary["commitment"]
        err_code = sanitized_summary.get("err_code")
        units = sanitized_summary.get("units_consumed")

    result = {
        "schema": SCHEMA,
        "network": CANONICAL_NETWORK,
        "mint": CANONICAL_MINT,
        "operation": simulation_plan.get("operation"),
        "amount_raw": int(simulation_plan.get("amount_raw", 0)),
        "simulation_plan_sha256": plan_sha,
        "review_manifest_sha256": simulation_plan.get("review_manifest_sha256"),
        "policy_sha256": simulation_plan.get("policy_sha256"),
        "treasury_policy_sha256": simulation_plan.get("treasury_policy_sha256"),
        "simulation_eligible": eligible,
        "simulation_attempted": attempted,
        "simulation_review_passed": passed,
        "outcome": outcome,
        "blockers": blockers,
        "sanitized_summary_sha256": summary_sha,
        "simulation_observation": {
            "slot": slot,
            "commitment": commitment,
            "err_code": err_code,
            "units_consumed": units,
            "raw_logs_stored": False,
            "raw_account_data_stored": False,
            "raw_rpc_response_stored": False,
        },
        "exact_remaining_signer_action": (
            "user_controlled_approval_and_external_multisig_review_required_before_any_signing"
            if passed else "none_until_fail_closed_blockers_are_resolved"
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
    result["simulation_review_receipt_sha256"] = canonical_sha256(result)
    return result
