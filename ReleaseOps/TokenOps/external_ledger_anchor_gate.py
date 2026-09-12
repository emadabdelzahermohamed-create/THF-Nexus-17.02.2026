#!/usr/bin/env python3
"""Fail-closed external immutable-anchor gate for THF TokenOps review ledger.

This module prepares an anchor request and verifies an externally produced receipt.
It never creates, serializes, simulates, signs, submits, broadcasts, transfers,
burns, or changes Solana state. Production receipts must come from an independent
immutable store reached with short-lived identity (preferred: GCP WIF).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
from datetime import datetime, timezone
from typing import Any, Dict

import audit_export

NETWORK = "solana-mainnet-beta"
MINT = "HjCHpu3tLRGCkJtZyUjzCKHv47usxWcMcqwhkaeBpjiv"
SUPPORTED_PROVIDERS = {"gcp-object-lock"}
FORBIDDEN_FIELDS = {
    "seed", "seed_phrase", "mnemonic", "private_key", "secret_key", "keypair",
    "signature", "signed_transaction", "raw_transaction", "serialized_transaction",
}


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


def _hex64(value: Any, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a 64-char hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be hex") from exc
    return value.lower()


def _iso8601(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} missing")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"{field} must be timezone-aware")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def prepare_anchor_request(ledger_path: str, source_head_sha: str) -> Dict[str, Any]:
    _reject({"source_head_sha": source_head_sha})
    if not isinstance(source_head_sha, str) or len(source_head_sha) != 40:
        raise ValueError("source_head_sha must be a full Git commit SHA")
    try:
        int(source_head_sha, 16)
    except ValueError as exc:
        raise ValueError("source_head_sha must be hex") from exc
    p = pathlib.Path(ledger_path)
    if not p.exists():
        raise ValueError("ledger does not exist")
    state = audit_export.verify(ledger_path)
    if state["entries"] < 1 or state["head_hash"] == "GENESIS":
        raise ValueError("non-empty verified ledger required")
    ledger_bytes_sha256 = hashlib.sha256(p.read_bytes()).hexdigest()
    out = {
        "version": 1,
        "record_type": "tokenops_external_ledger_anchor_request",
        "network": NETWORK,
        "mint": MINT,
        "source_head_sha": source_head_sha.lower(),
        "ledger_entries": state["entries"],
        "ledger_head_sha256": _hex64(state["head_hash"], "ledger_head_sha256"),
        "ledger_bytes_sha256": ledger_bytes_sha256,
        "required_provider": "gcp-object-lock",
        "required_identity_mode": "workload-identity-federation-or-equivalent-short-lived",
        "persistent_service_account_key_allowed": False,
        "simulation_review_eligible": False,
        "execution_authorized": False,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "wave_mawja_touched": False,
    }
    out["anchor_request_sha256"] = _sha(out)
    return out


def verify_anchor_receipt(request: Dict[str, Any], receipt: Dict[str, Any]) -> Dict[str, Any]:
    _reject({"request": request, "receipt": receipt})
    supplied_request = request.get("anchor_request_sha256")
    request_core = dict(request); request_core.pop("anchor_request_sha256", None)
    if not isinstance(supplied_request, str) or _sha(request_core) != supplied_request:
        raise ValueError("anchor request digest mismatch")
    if request.get("network") != NETWORK or request.get("mint") != MINT:
        raise ValueError("canonical network/mint mismatch")
    provider = receipt.get("provider")
    if provider not in SUPPORTED_PROVIDERS or provider != request.get("required_provider"):
        raise ValueError("unsupported or mismatched immutable anchor provider")
    if receipt.get("immutable_retention") is not True or receipt.get("externally_verified") is not True:
        raise ValueError("external immutable verification required")
    if receipt.get("identity_mode") != request.get("required_identity_mode"):
        raise ValueError("short-lived identity mode mismatch")
    if receipt.get("persistent_service_account_key_used") is not False:
        raise ValueError("persistent service-account keys are forbidden")
    for field in ("anchor_request_sha256", "ledger_head_sha256", "ledger_bytes_sha256", "source_head_sha"):
        if receipt.get(field) != request.get(field):
            raise ValueError(f"anchor receipt {field} mismatch")
    object_id = receipt.get("object_id")
    if not isinstance(object_id, str) or not object_id.strip() or "placeholder" in object_id.lower():
        raise ValueError("real immutable object_id required")
    anchored_at = _iso8601(receipt.get("anchored_at_utc"), "anchored_at_utc")
    supplied_receipt = receipt.get("receipt_sha256")
    receipt_core = dict(receipt); receipt_core.pop("receipt_sha256", None)
    if not isinstance(supplied_receipt, str) or _sha(receipt_core) != supplied_receipt:
        raise ValueError("anchor receipt digest mismatch")
    out = {
        "version": 1,
        "record_type": "tokenops_external_ledger_anchor_verified",
        "network": NETWORK,
        "mint": MINT,
        "source_head_sha": request["source_head_sha"],
        "ledger_head_sha256": request["ledger_head_sha256"],
        "anchor_request_sha256": supplied_request,
        "anchor_receipt_sha256": supplied_receipt,
        "provider": provider,
        "object_id": object_id,
        "anchored_at_utc": anchored_at,
        "external_immutable_anchor_verified": True,
        "simulation_review_eligible": True,
        "simulation_execution_permitted": False,
        "execution_authorized": False,
        "external_signer_required_for_execution": True,
        "user_controlled_approval_required_for_execution": True,
        "transaction_created": False,
        "transaction_signed": False,
        "transaction_submitted": False,
        "broadcast_allowed": False,
        "financial_effect": False,
        "private_key_used": False,
        "wave_mawja_touched": False,
    }
    out["external_anchor_gate_sha256"] = _sha(out)
    return out
