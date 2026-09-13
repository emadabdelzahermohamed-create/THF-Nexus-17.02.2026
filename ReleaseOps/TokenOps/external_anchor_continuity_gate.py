#!/usr/bin/env python3
"""Bind an externally verified immutable ledger anchor to the live TokenOps ledger.

Review-only fail-closed control. This module never creates, serializes, simulates,
signs, submits, broadcasts, transfers, burns, or changes Solana state.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any, Dict

import audit_export
import external_ledger_anchor_gate

NETWORK = external_ledger_anchor_gate.NETWORK
MINT = external_ledger_anchor_gate.MINT
FORBIDDEN_FIELDS = external_ledger_anchor_gate.FORBIDDEN_FIELDS


def _sha(value: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _reject(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower().replace("-", "_") in FORBIDDEN_FIELDS:
                raise ValueError(f"forbidden secret/signature field: {key}")
            _reject(item)
    elif isinstance(value, list):
        for item in value:
            _reject(item)


def verify_continuity(
    anchor_request: Dict[str, Any],
    anchor_receipt: Dict[str, Any],
    ledger_path: str,
    expected_source_head_sha: str,
) -> Dict[str, Any]:
    """Verify external receipt and prove the local ledger still equals its anchored state."""
    _reject({
        "anchor_request": anchor_request,
        "anchor_receipt": anchor_receipt,
        "expected_source_head_sha": expected_source_head_sha,
    })
    if not isinstance(expected_source_head_sha, str) or len(expected_source_head_sha) != 40:
        raise ValueError("expected_source_head_sha must be a full Git commit SHA")
    try:
        int(expected_source_head_sha, 16)
    except ValueError as exc:
        raise ValueError("expected_source_head_sha must be hex") from exc

    verified_anchor = external_ledger_anchor_gate.verify_anchor_receipt(anchor_request, anchor_receipt)
    if verified_anchor.get("network") != NETWORK or verified_anchor.get("mint") != MINT:
        raise ValueError("canonical network/mint mismatch")
    if verified_anchor.get("source_head_sha") != expected_source_head_sha.lower():
        raise ValueError("external anchor source head mismatch")

    p = pathlib.Path(ledger_path)
    if not p.exists():
        raise ValueError("ledger does not exist")
    ledger_state = audit_export.verify(ledger_path)
    if ledger_state.get("entries", 0) < 1 or ledger_state.get("head_hash") == "GENESIS":
        raise ValueError("non-empty verified ledger required")
    if ledger_state.get("head_hash") != verified_anchor.get("ledger_head_sha256"):
        raise ValueError("ledger head differs from immutable external anchor")
    ledger_bytes_sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
    if ledger_bytes_sha256 != anchor_request.get("ledger_bytes_sha256"):
        raise ValueError("ledger bytes differ from immutable external anchor")

    out = {
        "version": 1,
        "record_type": "tokenops_external_anchor_continuity_verified",
        "network": NETWORK,
        "mint": MINT,
        "source_head_sha": expected_source_head_sha.lower(),
        "ledger_entries": ledger_state["entries"],
        "anchored_prior_ledger_head_sha256": verified_anchor["ledger_head_sha256"],
        "anchored_ledger_bytes_sha256": ledger_bytes_sha256,
        "anchor_request_sha256": verified_anchor["anchor_request_sha256"],
        "anchor_receipt_sha256": verified_anchor["anchor_receipt_sha256"],
        "external_anchor_gate_sha256": verified_anchor["external_anchor_gate_sha256"],
        "provider": verified_anchor["provider"],
        "object_id": verified_anchor["object_id"],
        "anchored_at_utc": verified_anchor["anchored_at_utc"],
        "external_immutable_anchor_verified": True,
        "ledger_continuity_verified": True,
        "replay_guard_prior_head_eligible": True,
        "simulation_review_eligible": True,
        "simulation_execution_permitted": False,
        "execution_authorized": False,
        "external_signer_required_for_execution": True,
        "user_controlled_approval_required_for_execution": True,
        "transaction_created": False,
        "transaction_serialized": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_touched": False,
    }
    out["external_anchor_continuity_sha256"] = _sha(out)
    return out


def verify_record(record: Dict[str, Any]) -> Dict[str, Any]:
    _reject(record)
    supplied = record.get("external_anchor_continuity_sha256")
    core = dict(record)
    core.pop("external_anchor_continuity_sha256", None)
    if not isinstance(supplied, str) or _sha(core) != supplied:
        raise ValueError("external anchor continuity digest mismatch")
    if record.get("network") != NETWORK or record.get("mint") != MINT:
        raise ValueError("canonical network/mint mismatch")
    required_true = (
        "external_immutable_anchor_verified",
        "ledger_continuity_verified",
        "replay_guard_prior_head_eligible",
        "simulation_review_eligible",
        "external_signer_required_for_execution",
        "user_controlled_approval_required_for_execution",
    )
    if any(record.get(field) is not True for field in required_true):
        raise ValueError("required review-only continuity invariant missing")
    required_false = (
        "simulation_execution_permitted",
        "execution_authorized",
        "transaction_created",
        "transaction_serialized",
        "transaction_signed",
        "transaction_submitted",
        "broadcast_allowed",
        "financial_effect",
        "private_key_used",
        "wave_mawja_touched",
    )
    if any(record.get(field) is not False for field in required_false):
        raise ValueError("execution safety invariant violated")
    return {"verified": True, "external_anchor_continuity_sha256": supplied}
