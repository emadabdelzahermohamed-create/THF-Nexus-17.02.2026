#!/usr/bin/env python3
"""Bind a verified freshness gate into TokenOps audit and approval records.

The resulting records are review evidence only. This module never authorizes or
executes a financial action and never creates, serializes, signs, submits, broadcasts,
or simulates a Solana transaction.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

import approval_ledger
import audit_export
import evidence_freshness_gate

FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


def _canonical_sha256(value: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _reject_secrets(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in FORBIDDEN_FIELDS:
                raise ValueError(f"forbidden secret/signature field: {key}")
            _reject_secrets(item)
    elif isinstance(value, list):
        for item in value:
            _reject_secrets(item)


def build_approval_record(manifest: Dict[str, Any], policy: Dict[str, Any],
                          freshness_gate: Dict[str, Any]) -> Dict[str, Any]:
    _reject_secrets({"manifest": manifest, "policy": policy, "freshness_gate": freshness_gate})
    verified = evidence_freshness_gate.verify(freshness_gate)
    if freshness_gate.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("freshness gate manifest mismatch")
    base = approval_ledger.build(manifest, policy)
    if base.get("execution_authorized") is not False:
        raise ValueError("approval ledger must not authorize execution")
    if base.get("external_multisig_required") is not True:
        raise ValueError("external multisig boundary missing")
    if base.get("transaction_signed") is not False or base.get("transaction_submitted") is not False:
        raise ValueError("unsafe approval ledger transaction flags")
    base.pop("ledger_entry_sha256", None)
    base.update({
        "record_type": "fresh_simulation_review_approval",
        "evidence_freshness_gate_sha256": verified["evidence_freshness_gate_sha256"],
        "evidence_fresh": True,
        "simulation_review_eligible": True,
        "simulation_execution_permitted": False,
        "user_controlled_approval_required_for_execution": True,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_touched": False,
    })
    base["ledger_entry_sha256"] = _canonical_sha256(base)
    return base


def append_audit_record(manifest: Dict[str, Any], freshness_gate: Dict[str, Any],
                        ledger_path: str, created_at: int | None = None) -> Dict[str, Any]:
    _reject_secrets({"manifest": manifest, "freshness_gate": freshness_gate})
    verified = evidence_freshness_gate.verify(freshness_gate)
    if freshness_gate.get("manifest_sha256") != manifest.get("manifest_sha256"):
        raise ValueError("freshness gate manifest mismatch")
    event = {
        "version": 1,
        "event_type": "tokenops_fresh_simulation_review",
        "network": freshness_gate.get("network"),
        "mint": freshness_gate.get("mint"),
        "manifest_sha256": manifest.get("manifest_sha256"),
        "evidence_freshness_gate_sha256": verified["evidence_freshness_gate_sha256"],
        "evidence_fresh": True,
        "simulation_review_eligible": True,
        "simulation_execution_permitted": False,
        "transaction_created": False,
        "transaction_serialized": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "external_signer_required_for_execution": True,
        "user_controlled_approval_required_for_execution": True,
        "private_key_used": False,
        "wave_mawja_touched": False,
    }
    return audit_export.append_entry(event, ledger_path, created_at=created_at)
